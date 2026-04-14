"""
World System - Gestión de generación procedural del mapa infinito y controlador del jugador
"""
import pygame
import random
import math
from src.config import (
    TILE_SIZE, Colors, SCREEN_WIDTH, SCREEN_HEIGHT
)
from src.utils.asset_manager import assets


# ─── TIPOS DE TILE ────────────────────────────────────────────────────────────

class TileType:
    SAND   = 0
    ROCK   = 1
    OASIS  = 2
    FLOOR  = 3  # Interior de edificios


TILE_WALKABLE = {
    TileType.SAND:  True,
    TileType.ROCK:  False,
    TileType.OASIS: False,
    TileType.FLOOR: True,
}

TILE_COLORS = {
    TileType.SAND:  (210, 170, 100),
    TileType.ROCK:  (117, 113, 97),
    TileType.OASIS: (48, 100, 160),
    TileType.FLOOR: (80, 60, 40),
}

TILE_SPRITE_KEYS = {
    TileType.SAND:  'tile_sand',
    TileType.ROCK:  'tile_rock',
    TileType.OASIS: 'tile_oasis',
    TileType.FLOOR: 'tile_floor',
}


# ─── GENERADOR DE MAPA INFINITO ───────────────────────────────────────────────

class WorldMap:
    """
    Mapa 2D generado proceduralmente de forma infinita mediante chunks.
    """
    
    CHUNK_SIZE = 16  # Tamaño de cada chunk en tiles
    
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(0, 99999)
        self.chunks = {}  # {(cx, cy): [[tile_type, ...], ...]}
        self.buildings_on_map = {}  # {(tx, ty): building_instance}
        self._tile_cache = {}
        
    def _get_chunk_coords(self, tx: int, ty: int) -> tuple:
        return int(tx // self.CHUNK_SIZE), int(ty // self.CHUNK_SIZE)
    
    def _generate_chunk(self, cx: int, cy: int):
        """Genera un chunk de mapa usando ruido determinista basado en la semilla (mapa más abierto)"""
        chunk_tiles = [[TileType.SAND] * self.CHUNK_SIZE for _ in range(self.CHUNK_SIZE)]
        
        for y in range(self.CHUNK_SIZE):
            for x in range(self.CHUNK_SIZE):
                tx, ty = cx * self.CHUNK_SIZE + x, cy * self.CHUNK_SIZE + y
                
                # Ruido determinista simple
                n = self._noise(tx, ty)
                
                # Reducir drásticamente la probabilidad de rocas y oasis para evitar el efecto laberinto
                if n < 0.02:
                    chunk_tiles[y][x] = TileType.OASIS
                elif n > 0.96:
                    chunk_tiles[y][x] = TileType.ROCK
                else:
                    chunk_tiles[y][x] = TileType.SAND
                    
        self.chunks[(cx, cy)] = chunk_tiles

    def _noise(self, x: int, y: int) -> float:
        """Función de ruido determinista básica"""
        # Combinar x, y y seed para obtener un valor pseudo-aleatorio entre 0 y 1
        val = math.sin(x * 12.9898 + y * 78.233 + self.seed) * 43758.5453
        return val - math.floor(val)

    def get_tile(self, tx: int, ty: int) -> int:
        tx, ty = int(tx), int(ty)
        cx, cy = self._get_chunk_coords(tx, ty)
        if (cx, cy) not in self.chunks:
            self._generate_chunk(cx, cy)
        
        lx, ly = tx % self.CHUNK_SIZE, ty % self.CHUNK_SIZE
        return self.chunks[(cx, cy)][ly][lx]

    def is_walkable(self, tx: int, ty: int) -> bool:
        tx, ty = int(tx), int(ty)
        # Los edificios ya no bloquean el paso por defecto para evitar que el jugador se quede encerrado
        tile = self.get_tile(tx, ty)
        return TILE_WALKABLE.get(tile, False)

    def place_building(self, tx: int, ty: int, building_instance: dict, size: int = 3) -> bool:
        """Coloca un edificio en el mapa (ocupa size x size tiles)"""
        tx, ty = int(tx), int(ty)
        # Verificar área
        for dy in range(size):
            for dx in range(size):
                nx, ny = tx + dx, ty + dy
                if self.get_tile(nx, ny) == TileType.ROCK or (nx, ny) in self.buildings_on_map:
                    return False
        
        # Colocar
        for dy in range(size):
            for dx in range(size):
                self.buildings_on_map[(tx + dx, ty + dy)] = building_instance
        
        # Guardar la posición de origen para el dibujo
        building_instance['tile_x'] = tx
        building_instance['tile_y'] = ty
        building_instance['size'] = size
        return True

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int, screen_w: int, screen_h: int):
        """Dibuja los tiles visibles y los edificios"""
        start_tx = int(camera_x // TILE_SIZE)
        start_ty = int(camera_y // TILE_SIZE)
        end_tx = int((camera_x + screen_w) // TILE_SIZE + 1)
        end_ty = int((camera_y + screen_h) // TILE_SIZE + 1)
        
        # Dibujar Tiles
        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                tile = self.get_tile(tx, ty)
                sx = tx * TILE_SIZE - camera_x
                sy = ty * TILE_SIZE - camera_y
                
                # Dibujar sprite si existe, si no color plano
                sprite_key = TILE_SPRITE_KEYS.get(tile)
                sprite = assets.get_sprite(sprite_key)
                if sprite:
                    surface.blit(sprite, (sx, sy))
                else:
                    pygame.draw.rect(surface, TILE_COLORS[tile], (sx, sy, TILE_SIZE, TILE_SIZE))

        # Dibujar Edificios (solo una vez por edificio, usando su posición de origen)
        drawn_buildings = set()
        for ty in range(start_ty - 5, end_ty + 5):
            for tx in range(start_tx - 5, end_tx + 5):
                if (tx, ty) in self.buildings_on_map:
                    b = self.buildings_on_map[(tx, ty)]
                    b_id = id(b)
                    if b_id not in drawn_buildings:
                        self._draw_building(surface, b, camera_x, camera_y)
                        drawn_buildings.add(b_id)

    def _draw_building(self, surface, b, camera_x, camera_y):
        tx, ty = b['tile_x'], b['tile_y']
        
        # Escalar tamaño según capacidad (si existe en los stats)
        # Capacidad base es 5 (tamaño 3), cada 20 de capacidad extra aumenta 1 tile de tamaño
        capacidad = b.get('stats', {}).get('capacidad', 5)
        size = 3 + (capacidad - 5) // 20
        size = max(2, min(size, 6)) # Limitar entre 2 y 6 tiles
        
        sx = tx * TILE_SIZE - camera_x
        sy = ty * TILE_SIZE - camera_y
        
        # Obtener sprite del edificio
        sprite_name = b.get('sprite', 'caseta_basica.png')
        if sprite_name.endswith('.png'):
            sprite_name = sprite_name[:-4]
        sprite_key = f"building_{sprite_name}"
        
        sprite = assets.get_sprite(sprite_key)
        
        if sprite and sprite_key in assets._sprites: # Verificar que no sea el placeholder
            # Escalar sprite al tamaño del edificio (size * TILE_SIZE)
            target_size = int(size * TILE_SIZE)
            if sprite.get_width() != target_size:
                sprite = pygame.transform.scale(sprite, (target_size, target_size))
            
            # Dibujar sombra simple debajo
            shadow = pygame.Surface((target_size, target_size // 3), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 80), (0, 0, target_size, target_size // 3))
            surface.blit(shadow, (sx, sy + target_size - target_size // 4))
            
            surface.blit(sprite, (sx, sy))
        else:
            # Fallback visual si no hay sprite
            rect_size = size * TILE_SIZE
            pygame.draw.rect(surface, (100, 100, 100), (sx, sy, rect_size, rect_size))
            pygame.draw.rect(surface, (200, 200, 200), (sx, sy, rect_size, rect_size), 2)


# ─── CONTROLADOR DEL JUGADOR ──────────────────────────────────────────────────

class PlayerController:
    def __init__(self, x: float, y: float, world=None):
        self.px = x
        self.py = y
        self.world = world
        self.speed = 200
        self.hp = 100
        self.max_hp = 100
        self.equipped_weapon = None
        
        # Animación
        self.sprite_key = 'ui_player'
        self.frame = 0
        self.anim_timer = 0
        self.facing_right = True
        self.is_moving = False

    def handle_input(self, keys, settings):
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        
        self.is_moving = (dx != 0 or dy != 0)
        if dx > 0: self.facing_right = True
        elif dx < 0: self.facing_right = False
        
        return dx, dy

    def update(self, dt):
        if self.is_moving:
            self.anim_timer += dt
            if self.anim_timer > 0.15:
                self.frame = (self.frame + 1) % 4
                self.anim_timer = 0
        else:
            self.frame = 0
            self.anim_timer = 0

    def get_screen_pos(self, camera_x: int, camera_y: int):
        """Devuelve la posición del jugador en coordenadas de pantalla"""
        return int(self.px - camera_x), int(self.py - camera_y)

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        sx, sy = self.get_screen_pos(camera_x, camera_y)
        
        # Sombra
        shadow = pygame.Surface((24, 8), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 100))
        surface.blit(shadow, (sx - 12, sy + 12))
        
        # Cuerpo del jugador
        sprite = assets.get_sprite(self.sprite_key)
        if sprite:
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            
            # Efecto de bobbing al caminar
            bob = 0
            angle = 0
            if self.is_moving:
                bob = int(math.sin(pygame.time.get_ticks() * 0.01) * 3)
                angle = math.sin(pygame.time.get_ticks() * 0.01) * 5
                if angle != 0:
                    sprite = pygame.transform.rotate(sprite, angle)
            
            surface.blit(sprite, (sx - 16, sy - 16 + bob))
            
            # Dibujar arma equipada
            if self.equipped_weapon:
                w_sprite = assets.get_sprite(self.equipped_weapon.get('sprite', 'weapon_knife'))
                if w_sprite:
                    if not self.facing_right:
                        w_sprite = pygame.transform.flip(w_sprite, True, False)
                        surface.blit(w_sprite, (sx - 25, sy - 5 + bob))
                    else:
                        surface.blit(w_sprite, (sx + 5, sy - 5 + bob))
        else:
            pygame.draw.circle(surface, Colors.PLAYER, (sx, sy), 15)


# ─── CÁMARA ───────────────────────────────────────────────────────────────────

class Camera:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def follow(self, target, dt):
        target_x = target.px - SCREEN_WIDTH // 2
        target_y = target.py - SCREEN_HEIGHT // 2
        
        # Suavizado
        self.x += (target_x - self.x) * 5 * dt
        self.y += (target_y - self.y) * 5 * dt
