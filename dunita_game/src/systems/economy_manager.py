"""
Economy Manager - Sistema de economía y motor de turnos
Gestiona el saldo, compras, ventas y resolución de turnos
"""
from src.config import STARTING_GOLD, INVENTORY_SIZE


class EconomyManager:
    """
    Gestiona la economía del juego:
    - Saldo del jugador (Solaris / Especia)
    - Compra/venta de criaturas e ítems
    - Motor de turnos (día/semana)
    - Cálculo de gastos: criaturas * alimentación + mantenimiento estructuras
    """
    
    def __init__(self, save_data: dict):
        self.save_data = save_data
        self._callbacks = []
        self.pending_mercenary_spawn = None  # Callbacks para notificaciones
    
    @property
    def gold(self) -> int:
        return self.save_data.get('gold', STARTING_GOLD)
    
    @gold.setter
    def gold(self, value: int):
        self.save_data['gold'] = max(0, int(value))
    
    @property
    def day(self) -> int:
        return self.save_data.get('day', 1)
    
    @property
    def creatures(self) -> list:
        return self.save_data.get('creatures', [])
    
    @property
    def buildings(self) -> list:
        return self.save_data.get('buildings', [])
    
    @property
    def inventory(self) -> list:
        return self.save_data.get('inventory', [])
    
    def can_afford(self, cost: int) -> bool:
        return self.gold >= cost
    
    def buy_creature(self, creature_data: dict) -> tuple:
        """
        Intenta comprar una criatura.
        Returns: (success: bool, message: str)
        """
        cost = creature_data.get('costeCompra', 0)
        
        if not self.can_afford(cost):
            return False, f"Fondos insuficientes. Necesitas {cost} Solaris."
        
        self.gold -= cost
        
        # Añadir criatura a la lista
        creature_instance = {
            'id': creature_data['id'],
            'nombre': creature_data['nombre'],
            'sprite': creature_data.get('sprite', ''),
            'costeAlimentacionDiario': creature_data.get('costeAlimentacionDiario', 10),
            'costeAlimentacionSemanal': creature_data.get('costeAlimentacionSemanal', 70),
            'tags': creature_data.get('tags', []),
            'capacidadRequerida': creature_data.get('capacidadRequerida', 'pequeño'),
            'recinto_id': None,  # Sin asignar inicialmente
            'instance_id': self._generate_id(),
        }
        self.save_data['creatures'].append(creature_instance)
        
        self._notify(f"Criatura adquirida: {creature_data['nombre']}")
        return True, f"Has adquirido {creature_data['nombre']} por {cost} Solaris."
    
    def buy_building(self, building_data: dict) -> tuple:
        """
        Intenta comprar un edificio.
        Returns: (success: bool, message: str, building_instance: dict or None)
        """
        cost = building_data.get('coste', 0)
        
        if not self.can_afford(cost):
            return False, f"Fondos insuficientes. Necesitas {cost} Solaris.", None
        
        self.gold -= cost
        
        building_instance = {
            'id': building_data['id'],
            'nombre': building_data['nombre'],
            'sprite': building_data.get('sprite', ''),
            'coste': cost,
            'mantenimiento': building_data.get('stats', {}).get('mantenimiento', 10),
            'capacidadMaxima': building_data.get('capacidadMaxima', 5),
            'tagEspeciesPermitidas': building_data.get('tagEspeciesPermitidas', []),
            'criaturas_asignadas': [],
            'tile_x': None,
            'tile_y': None,
            'instance_id': self._generate_id(),
        }
        self.save_data['buildings'].append(building_instance)
        
        self._notify(f"Edificio adquirido: {building_data['nombre']}")
        return True, f"Has adquirido {building_data['nombre']} por {cost} Solaris.", building_instance
    
    def buy_item(self, item_data: dict) -> tuple:
        """
        Compra un ítem. Si es POCION o ARMA, va al inventario.
        Si es RECLUTA o MERCENARIO, se añade a la lista de entidades.
        Returns: (success: bool, message: str)
        """
        cost = item_data.get('coste', 0)
        tipo = item_data.get('tipo', '').upper()
        
        if not self.can_afford(cost):
            return False, f"Fondos insuficientes. Necesitas {cost} Solaris."
        
        if tipo in ['RECLUTA', 'MERCENARIO']:
            self.gold -= cost
            # Flag para que GameplayState spawnee la entidad
            self.pending_mercenary_spawn = tipo
            return True, f"{item_data['nombre']} contratado."

        if tipo in ['POCION', 'ARMA']:
            if len(self.inventory) >= INVENTORY_SIZE:
                return False, f"Inventario lleno ({len(self.inventory)}/{INVENTORY_SIZE})."
            
            self.gold -= cost
            item_instance = {
                'id': item_data['id'],
                'nombre': item_data['nombre'],
                'tipo': tipo,
                'descripcion': item_data.get('descripcion', ''),
                'instance_id': self._generate_id(),
            }
            
            # Añadir stats específicos
            if tipo == 'POCION':
                item_instance['efectos'] = item_data.get('efectos', [])
            elif tipo == 'ARMA':
                item_instance['daño'] = item_data.get('daño', 10)
                item_instance['rango'] = item_data.get('rango', 100)
                item_instance['cadencia'] = item_data.get('cadencia', 1.0)
                item_instance['sprite'] = item_data.get('sprite', 'weapon_knife')
                item_instance['equipado'] = False
                
            self.save_data['inventory'].append(item_instance)
            return True, f"{item_data['nombre']} añadido al inventario."
        else:
            self.gold -= cost
            return True, f"Ítem adquirido: {item_data['nombre']}"

    def equip_weapon(self, instance_id: str) -> tuple:
        """Equipa un arma del inventario y desequipa la anterior"""
        inventory = self.save_data.get('inventory', [])
        weapon_to_equip = None
        
        # Buscar el arma y desequipar otras
        for item in inventory:
            if item.get('tipo') == 'ARMA':
                if item.get('instance_id') == instance_id:
                    weapon_to_equip = item
                    item['equipado'] = True
                else:
                    item['equipado'] = False
        
        if weapon_to_equip:
            return True, f"Equipado: {weapon_to_equip['nombre']}", weapon_to_equip
        return False, "Arma no encontrada", None
    
    def use_item(self, instance_id: str) -> tuple:
        """Usa un ítem del inventario"""
        inventory = self.save_data.get('inventory', [])
        for i, item in enumerate(inventory):
            if item.get('instance_id') == instance_id:
                inventory.pop(i)
                return True, f"Usaste: {item['nombre']}"
        return False, "Ítem no encontrado"
    
    def assign_creature_to_building(self, creature_instance_id: str,
                                     building_instance_id: str) -> tuple:
        """
        Asigna una criatura a un recinto.
        Valida: capacidad máxima y tags de especies permitidas.
        """
        creature = self._find_creature(creature_instance_id)
        building = self._find_building(building_instance_id)
        
        if not creature or not building:
            return False, "Criatura o recinto no encontrado."
        
        # Validar capacidad
        assigned = building.get('criaturas_asignadas', [])
        if len(assigned) >= building.get('capacidadMaxima', 5):
            return False, f"El recinto está lleno ({len(assigned)}/{building['capacidadMaxima']})."
        
        # Validar tags de especie
        allowed_tags = building.get('tagEspeciesPermitidas', [])
        creature_tags = creature.get('tags', [])
        
        if allowed_tags:
            compatible = any(tag in allowed_tags for tag in creature_tags)
            if not compatible:
                return False, (f"Esta criatura ({', '.join(creature_tags)}) no es compatible "
                               f"con este recinto ({', '.join(allowed_tags)}).")
        
        # Asignar
        if creature_instance_id not in assigned:
            assigned.append(creature_instance_id)
            building['criaturas_asignadas'] = assigned
            creature['recinto_id'] = building_instance_id
        
        return True, f"{creature['nombre']} asignado a {building['nombre']}."
    
    def advance_turn(self, turn_type: str = 'day') -> dict:
        """
        Avanza un turno (día o semana).
        Calcula: (criaturas * coste_alimentación) + mantenimiento_estructuras
        Returns: dict con resumen de gastos
        """
        multiplier = 1 if turn_type == 'day' else 7
        
        # Calcular gastos de alimentación
        feed_cost = 0
        feed_breakdown = []
        for creature in self.creatures:
            daily_cost = creature.get('costeAlimentacionDiario', 10)
            total_cost = daily_cost * multiplier
            feed_cost += total_cost
            feed_breakdown.append({
                'nombre': creature['nombre'],
                'coste': total_cost,
            })
        
        # Calcular mantenimiento de estructuras
        maint_cost = 0
        maint_breakdown = []
        for building in self.buildings:
            daily_maint = building.get('mantenimiento', 10)
            total_maint = daily_maint * multiplier
            maint_cost += total_maint
            maint_breakdown.append({
                'nombre': building['nombre'],
                'coste': total_maint,
            })
        
        total_cost = feed_cost + maint_cost
        
        # Aplicar gastos
        previous_gold = self.gold
        self.gold -= total_cost
        
        # Avanzar día
        self.save_data['day'] = self.day + multiplier
        
        result = {
            'turn_type': turn_type,
            'days_advanced': multiplier,
            'new_day': self.day,
            'feed_cost': feed_cost,
            'maint_cost': maint_cost,
            'total_cost': total_cost,
            'previous_gold': previous_gold,
            'new_gold': self.gold,
            'feed_breakdown': feed_breakdown,
            'maint_breakdown': maint_breakdown,
            'bankrupt': self.gold <= 0,
        }
        
        self._notify(f"Turno avanzado: -{total_cost} Solaris")
        return result
    
    def place_building(self, instance_id: str, tile_x: int, tile_y: int) -> bool:
        """Coloca un edificio en el mapa en las coordenadas dadas"""
        building = self._find_building(instance_id)
        if building:
            building['tile_x'] = tile_x
            building['tile_y'] = tile_y
            return True
        return False
    
    def _find_creature(self, instance_id: str) -> dict:
        for c in self.creatures:
            if c.get('instance_id') == instance_id:
                return c
        return None
    
    def _find_building(self, instance_id: str) -> dict:
        for b in self.buildings:
            if b.get('instance_id') == instance_id:
                return b
        return None
    
    def _generate_id(self) -> str:
        import time
        import random
        return f"{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
    
    def add_callback(self, callback):
        self._callbacks.append(callback)
    
    def _notify(self, message: str):
        for cb in self._callbacks:
            try:
                cb(message)
            except Exception:
                pass
    
    def get_summary(self) -> dict:
        """Retorna resumen del estado económico"""
        return {
            'gold': self.gold,
            'day': self.day,
            'num_creatures': len(self.creatures),
            'num_buildings': len(self.buildings),
            'inventory_count': len(self.inventory),
            'inventory_max': INVENTORY_SIZE,
            'daily_upkeep': sum(c.get('costeAlimentacionDiario', 10) for c in self.creatures) +
                            sum(b.get('mantenimiento', 10) for b in self.buildings),
        }
