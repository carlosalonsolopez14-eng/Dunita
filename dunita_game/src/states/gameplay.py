"""
DUNE DOMINION - Estado: Gameplay
Loop principal con mapa infinito, ciclo día/noche, enemigos y visitantes
"""
import pygame
import math
import random
import os

from src.engine import BaseState
from src.config import (
    GameState, Colors, SCREEN_WIDTH, SCREEN_HEIGHT,
    TILE_SIZE, DAY_DURATION_SEC, NIGHT_DURATION_SEC, ENEMY_SPAWN_RATE
)
from src.utils.asset_manager import assets
from src.systems.audio_manager import audio
from src.systems.economy_manager import EconomyManager
from src.systems.world import WorldMap, PlayerController, Camera
from src.systems.entities import Enemy, Visitor, Mercenary, Projectile
from src.ui.ui_manager import HUD, ShopUI, TurnPanel, BuildModeUI, Notification


class GameplayState(BaseState):
    
    def on_enter(self, **kwargs):
        # Iniciar música de gameplay
        audio.play_bgm(GameState.GAMEPLAY)
        
        # Inicializar economía
        self.economy = EconomyManager(self.engine.save_data)
        self.economy.add_callback(self._on_economy_event)
        
        # Generar mapa infinito
        seed = self.engine.save_data.get('seed', None)
        self.world = WorldMap(seed=seed)
        if seed is None:
            self.engine.save_data['seed'] = self.world.seed
        
        # Restaurar edificios colocados
        for building in self.economy.buildings:
            tx = building.get('tile_x')
            ty = building.get('tile_y')
            if tx is not None and ty is not None:
                self.world.place_building(tx, ty, building)
        
        # Jugador
        px = self.engine.save_data.get('player_pos', [0, 0])
        self.player = PlayerController(px[0], px[1], self.world)
        
        # Cámara
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera.x = self.player.px - SCREEN_WIDTH // 2
        self.camera.y = self.player.py - SCREEN_HEIGHT // 2
        
        # UI
        self.hud = HUD(self.economy, self.player)
        self.shop = ShopUI(self.economy, self.engine.game_data)
        self.turn_panel = TurnPanel(self.economy)
        self.build_mode = BuildModeUI(self.world, self.economy)
        
        # Notificaciones
        self.notifications = []
        
        # Estado de pausa
        self.paused = False
        self._init_pause_menu()
        
        # Ciclo día/noche
        self.time_elapsed = self.engine.save_data.get('time_elapsed', 0.0)
        self.is_night = False
        self.night_alpha = 0
        
        # Entidades
        self.enemies = []
        self.visitors = []
        self.mercenaries = []
        self.projectiles = []
        self.spawn_timer = 0
        self.visitor_spawn_timer = 0
        
        # Lore inicial si es partida nueva
        if kwargs.get('is_new', False):
            self._show_initial_lore()

    def _init_pause_menu(self):
        from src.ui.widgets import Panel, Button, Slider, Label
        pw, ph = 400, 450
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2
        self.pause_panel = Panel(px, py, pw, ph, "MENU DE PAUSA")
        
        y = py + 60
        self.pause_widgets = []
        
        # Sliders de sonido
        self.pause_widgets.append(Label(px + 40, y, "CONFIGURACION DE SONIDO", font_size='small', color=Colors.GOLD))
        y += 40
        
        def set_master(v): 
            self.engine.settings['master_vol'] = v
            self.engine.apply_audio_settings()
        self.pause_widgets.append(Slider(px + 40, y, 320, 20, value=self.engine.settings.get('master_vol', 0.8), label="Maestro", callback=set_master))
        y += 50
        
        def set_bgm(v):
            self.engine.settings['bgm_vol'] = v
            self.engine.apply_audio_settings()
        self.pause_widgets.append(Slider(px + 40, y, 320, 20, value=self.engine.settings.get('bgm_vol', 0.6), label="Musica", callback=set_bgm))
        y += 50
        
        def set_sfx(v):
            self.engine.settings['sfx_vol'] = v
            self.engine.apply_audio_settings()
        self.pause_widgets.append(Slider(px + 40, y, 320, 20, value=self.engine.settings.get('sfx_vol', 0.7), label="Efectos", callback=set_sfx))
        y += 70
        
        # Botones
        self.pause_widgets.append(Button(px + 100, y, 200, 40, "CONTINUAR", callback=self._toggle_pause))
        y += 50
        self.pause_widgets.append(Button(px + 100, y, 200, 40, "MENU PRINCIPAL", callback=lambda: self.engine.change_state(GameState.MAIN_MENU), color_normal=Colors.RED))

    def _toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            audio.play_sfx('click')
        else:
            from src.config import save_settings
            save_settings(self.engine.settings)

    def _show_initial_lore(self):
        lore = [
            "Año 10191. La Casa Atreides toma el control de Arrakis.",
            "El Duque Leto busca alianzas con los Fremen.",
            "Pero las sombras de la Casa Harkonnen acechan...",
            "Tu misión: Establecer un enclave y asegurar la Especia.",
            "La supervivencia es el primer paso hacia el poder."
        ]
        for i, line in enumerate(lore):
            self._add_notification(line, Colors.GOLD)
            
        # Dar recursos iniciales y edificio básico
        self.economy.gold += 15000
        self._add_notification("+15000 Solaris de la Casa Atreides", Colors.GREEN)
        
        # Colocar edificio inicial automáticamente si no hay ninguno
        if not self.economy.buildings:
            basic_building_data = next((b for b in self.engine.game_data['buildings'] if b['id'] == 'caseta_basica'), None)
            if basic_building_data:
                success, msg, instance = self.economy.buy_building(basic_building_data)
                if success:
                    # Forzar colocación en el centro (0,0)
                    self.world.place_building(0, 0, instance)
                    self.economy.place_building(instance['instance_id'], 0, 0)
                    self._add_notification("Puesto de avanzada establecido.", Colors.UI_SUCCESS)
                    
                    # Asegurar que el jugador no aparezca dentro de una roca
                    from src.config import TILE_SIZE
                    tx, ty = 5, 5 # Empezar un poco desplazado del edificio
                    while not self.world.is_walkable(tx, ty):
                        tx += 1
                    self.player.px = tx * TILE_SIZE
                    self.player.py = ty * TILE_SIZE

    def _on_economy_event(self, message):
        self._add_notification(message, Colors.UI_TEXT)

    def _add_notification(self, text, color):
        self.notifications.append(Notification(text, color))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.build_mode.active:
                        self.build_mode.deactivate()
                    else:
                        self._toggle_pause()
                if not self.paused:
                    if event.key == pygame.K_TAB:
                        self.shop.visible = not self.shop.visible
                    if event.key == pygame.K_b:
                        if not self.build_mode.active:
                            basic_building = next((b for b in self.economy.buildings if not b.get('tile_x')), None)
                            if basic_building:
                                self.build_mode.activate(basic_building)
                            else:
                                self._add_notification("No tienes edificios para colocar.", Colors.UI_ERROR)
                        else:
                            self.build_mode.deactivate()
                    
                    if event.key == pygame.K_e:
                        self.shop.visible = not self.shop.visible
                        if self.shop.visible:
                            self._add_notification("Accediendo al Mercado de Especia...", Colors.GOLD)
            
            if not self.paused:
                if self.hud.handle_event(event): return
                if self.shop.handle_event(event): return
                
                if self.build_mode.active:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.build_mode.try_place():
                            self._add_notification("Edificio colocado con éxito.", Colors.UI_SUCCESS)
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not self.shop.visible and not self.build_mode.active:
                        self._handle_shoot(event.pos)
            else:
                for w in self.pause_widgets:
                    w.handle_event(event)

    def _handle_shoot(self, mouse_pos):
        if not self.player.equipped_weapon:
            self._add_notification("No tienes un arma equipada.", Colors.RED)
            return
            
        weapon = self.player.equipped_weapon
        world_mx = mouse_pos[0] + self.camera.x
        world_my = mouse_pos[1] + self.camera.y
        
        self.projectiles.append(Projectile(
            self.player.px, self.player.py, 
            world_mx, world_my, 
            weapon.get('daño', 10),
            speed=600 if weapon.get('id') == 'lasgun' else 400,
            sprite_key='ui_projectile'
        ))
        
        audio.play_sfx('click')
        self.player.anim_timer = 0

    def update(self, dt):
        if self.paused:
            for w in self.pause_widgets: w.update(dt)
            return
            
        if self.shop.pending_building_placement:
            self.build_mode.activate(self.shop.pending_building_placement)
            self.shop.pending_building_placement = None
            self._add_notification("Modo Construccion: Elige donde situar el edificio", Colors.GOLD)
            
        if self.economy.pending_mercenary_spawn:
            tipo = self.economy.pending_mercenary_spawn
            self.economy.pending_mercenary_spawn = None
            is_elite = (tipo == 'MERCENARIO')
            mx = self.player.px + random.randint(-50, 50)
            my = self.player.py + random.randint(-50, 50)
            self.mercenaries.append(Mercenary(mx, my, is_elite))
            self._add_notification(f"{tipo} contratado y listo para el combate.", Colors.UI_SUCCESS)
            
        self.time_elapsed += dt
        cycle_time = self.time_elapsed % (DAY_DURATION_SEC + NIGHT_DURATION_SEC)
        
        was_night = self.is_night
        self.is_night = cycle_time > DAY_DURATION_SEC
        
        if self.is_night:
            self.night_alpha = min(150, self.night_alpha + dt * 50)
            if not was_night:
                self._add_notification("Cae la noche... Los peligros acechan.", Colors.RED)
                self.visitors = []
            
            self.spawn_timer += dt
            if self.spawn_timer >= ENEMY_SPAWN_RATE:
                self.spawn_timer = 0
                self._spawn_enemy()
        else:
            self.night_alpha = max(0, self.night_alpha - dt * 50)
            if was_night:
                self._add_notification("Amanece en Arrakis.", Colors.GOLD)
                self.enemies = []
                self.economy.advance_turn('day')
            
            self.visitor_spawn_timer += dt
            if self.visitor_spawn_timer >= 10.0:
                self.visitor_spawn_timer = 0
                self._spawn_visitors()

        if not self.shop.visible and not self.build_mode.active:
            keys = pygame.key.get_pressed()
            dx, dy = self.player.handle_input(keys, self.engine.settings)
            
            if dx != 0 or dy != 0:
                if dx != 0 and dy != 0:
                    dist = math.sqrt(dx*dx + dy*dy)
                    dx /= dist
                    dy /= dist
                
                new_px = self.player.px + dx * self.player.speed * dt
                new_py = self.player.py + dy * self.player.speed * dt
                
                tx = int(new_px // TILE_SIZE)
                ty = int(new_py // TILE_SIZE)
                
                if self.world.is_walkable(tx, ty) and (tx, ty) not in self.world.buildings_on_map:
                    self.player.px = new_px
                    self.player.py = new_py
            
            self.player.update(dt)
        else:
            self.player.is_moving = False
            self.player.update(dt)

        self.camera.follow(self.player, dt)
        
        for e in self.enemies: e.update(dt, self.player, self.world)
        for v in self.visitors: v.update(dt, self.player, self.world)
        for m in self.mercenaries: m.update(dt, self.player, self.world, self.enemies)
        for p in self.projectiles: p.update(dt, self.enemies)
        
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.enemies = [e for e in self.enemies if e.alive]
        self.mercenaries = [m for m in self.mercenaries if m.alive]
        
        for n in self.notifications: n.update(dt)
        self.notifications = [n for n in self.notifications if not n.done]
        self.shop.update(dt)
        
        if self.build_mode.active:
            self.build_mode.update_ghost(pygame.mouse.get_pos(), self.camera.x, self.camera.y)

    def _spawn_enemy(self):
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(200, 400)
        ex = self.player.px + math.cos(angle) * dist
        ey = self.player.py + math.sin(angle) * dist
        
        tx, ty = int(ex // TILE_SIZE), int(ey // TILE_SIZE)
        if self.world.is_walkable(tx, ty):
            day_mult = 1.0 + (self.economy.day / 10.0)
            self.enemies.append(Enemy(ex, ey, day_mult))

    def _spawn_visitors(self):
        num_buildings = len(self.economy.buildings)
        num_creatures = len(self.economy.creatures)
        target_visitors = min(15, (num_buildings * 2) + (num_creatures // 2))
        
        if len(self.visitors) < target_visitors:
            if self.economy.buildings:
                b = random.choice(self.economy.buildings)
                if b.get('tile_x') is not None:
                    vx = b['tile_x'] * TILE_SIZE + random.randint(-50, 50)
                    vy = b['tile_y'] * TILE_SIZE + random.randint(-50, 50)
                    self.visitors.append(Visitor(vx, vy))

    def draw(self, screen):
        self.world.draw(screen, int(self.camera.x), int(self.camera.y), SCREEN_WIDTH, SCREEN_HEIGHT)
        
        for v in self.visitors: v.draw(screen, self.camera.x, self.camera.y)
        for m in self.mercenaries: m.draw(screen, self.camera.x, self.camera.y)
        for e in self.enemies: e.draw(screen, self.camera.x, self.camera.y)
        for p in self.projectiles: p.draw(screen, self.camera.x, self.camera.y)
        self.player.draw(screen, self.camera.x, self.camera.y)
        
        if self.night_alpha > 0:
            night_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            night_surf.fill((10, 10, 30, self.night_alpha))
            screen.blit(night_surf, (0, 0))
            
        self.hud.draw(screen)
        self.shop.draw(screen)
        
        if self.build_mode.active:
            self.build_mode.draw(screen, self.camera.x, self.camera.y)
        
        self._draw_controls_help(screen)
        
        for i, n in enumerate(self.notifications):
            n.draw(screen, 20, 100 + i * 30)
            
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            self.pause_panel.draw(screen)
            for w in self.pause_widgets: w.draw(screen)

    def _draw_controls_help(self, screen):
        font = assets.get_font('tiny')
        help_text = "WASD: Mover | TAB: Tienda | B: Construir | E: Interactuar | Click Izq: Atacar | ESC: Pausa"
        text_surf = font.render(help_text, True, Colors.WHITE)
        
        bg_rect = pygame.Rect(0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 30)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 150))
        screen.blit(bg_surf, bg_rect)
        
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15))
        screen.blit(text_surf, text_rect)
            
        self._draw_time_hud(screen)

    def _draw_time_hud(self, screen):
        font = assets.get_font('small')
        cycle_name = "NOCHE" if self.is_night else "DÍA"
        color = Colors.RED if self.is_night else Colors.GOLD
        time_text = f"CICLO: {cycle_name}"
        surf = font.render(time_text, True, color)
        screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, 10))
