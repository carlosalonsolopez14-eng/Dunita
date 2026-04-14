"""
DUNE DOMINION - Estado: Loading Screen
Carga asíncrona simulada de exactamente 7000ms con arte 8-bit y tooltips de lore
"""
import pygame
import math
import random

from src.engine import BaseState
from src.config import (
    GameState, Colors, SCREEN_WIDTH, SCREEN_HEIGHT,
    LOADING_DURATION_MS
)
from src.utils.asset_manager import assets
from src.systems.audio_manager import audio


class LoadingScreenState(BaseState):
    
    def on_enter(self, mode='new', **kwargs):
        self.mode = mode  # 'new' o 'load'
        self.kwargs = kwargs # Guardar para pasar al siguiente estado
        
        # Timer exacto de 7000ms
        self.total_ms = LOADING_DURATION_MS
        self.elapsed_ms = 0.0
        self.done = False
        
        # Música de loading
        audio.play_bgm(GameState.LOADING)
        
        # Datos del juego para tips
        game_data = self.engine.game_data
        self.lore_tips = game_data.get('lore_tips', [
            "Cargando el desierto de Arrakis...",
            "La especia debe fluir...",
            "Los Fremen conocen los secretos del desierto...",
        ])
        
        # Sprites de criaturas para mostrar
        self.creature_sprites = []
        creatures = game_data.get('creatures', [])
        for c in creatures[:6]:  # Mostrar hasta 6 criaturas
            sprite_key = f"creature_{c['id']}"
            self.creature_sprites.append({
                'sprite': sprite_key,
                'nombre': c['nombre'],
                'descripcion': c.get('descripcion', ''),
            })
        
        # Estado de animación
        self.current_tip_idx = 0
        self.tip_timer = 0.0
        self.tip_duration = 1.8  # segundos por tip
        self.current_creature_idx = 0
        self.creature_timer = 0.0
        self.creature_duration = 2.0
        
        # Animación de puntos
        self.dot_timer = 0.0
        self.dot_count = 0
        
        # Partículas de arena
        self.particles = []
        for _ in range(40):
            self.particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'vx': random.uniform(30, 80),
                'vy': random.uniform(-5, 5),
                'size': random.randint(1, 3),
                'alpha': random.randint(60, 150),
            })
        
        # Barra de progreso falsa con aceleración no lineal
        self._progress_curve = self._generate_progress_curve()
        self._curve_idx = 0
        
        # Superficie de fondo
        self._bg = self._create_background()
    
    def _generate_progress_curve(self):
        """Genera curva de progreso no lineal para barra falsa"""
        steps = 100
        curve = []
        for i in range(steps + 1):
            t = i / steps
            # Curva con pausas y aceleraciones (más realista)
            if t < 0.3:
                p = t / 0.3 * 0.4  # Rápido al inicio
            elif t < 0.6:
                p = 0.4 + (t - 0.3) / 0.3 * 0.2  # Lento en el medio
            elif t < 0.85:
                p = 0.6 + (t - 0.6) / 0.25 * 0.3  # Medio
            else:
                p = 0.9 + (t - 0.85) / 0.15 * 0.1  # Lento al final
            curve.append(min(1.0, p))
        return curve
    
    def _create_background(self):
        """Crea superficie de fondo estilo terminal Arrakis"""
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg.fill(Colors.UI_BG)
        
        # Patrón de grid sutil
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(bg, (30, 20, 10), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(bg, (30, 20, 10), (0, y), (SCREEN_WIDTH, y), 1)
        
        return bg
    
    def on_exit(self):
        pass
    
    def handle_events(self, events):
        # No permitir skip durante loading (bloqueo de transición)
        pass
    
    def update(self, dt):
        if self.done:
            return
        
        # Avanzar timer (en milisegundos)
        self.elapsed_ms += dt * 1000.0
        
        # Actualizar barra de progreso
        progress_ratio = min(1.0, self.elapsed_ms / self.total_ms)
        self._curve_idx = int(progress_ratio * (len(self._progress_curve) - 1))
        
        # Rotar tips de lore
        self.tip_timer += dt
        if self.tip_timer >= self.tip_duration:
            self.tip_timer = 0.0
            self.current_tip_idx = (self.current_tip_idx + 1) % len(self.lore_tips)
        
        # Rotar criaturas
        self.creature_timer += dt
        if self.creature_timer >= self.creature_duration:
            self.creature_timer = 0.0
            if self.creature_sprites:
                self.current_creature_idx = (self.current_creature_idx + 1) % len(self.creature_sprites)
        
        # Animación de puntos
        self.dot_timer += dt
        if self.dot_timer >= 0.4:
            self.dot_timer = 0.0
            self.dot_count = (self.dot_count + 1) % 4
        
        # Partículas
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            if p['x'] > SCREEN_WIDTH:
                p['x'] = -p['size']
                p['y'] = random.randint(0, SCREEN_HEIGHT)
        
        # Verificar si terminó exactamente a los 7000ms
        if self.elapsed_ms >= self.total_ms and not self.done:
            self.done = True
            self._transition()
    
    def _transition(self):
        """Transición al gameplay"""
        self.engine.change_state(GameState.GAMEPLAY, **self.kwargs)
    
    def draw(self, screen):
        # Fondo
        screen.blit(self._bg, (0, 0))
        
        # Partículas
        for p in self.particles:
            alpha_surf = pygame.Surface((p['size'], p['size']), pygame.SRCALPHA)
            alpha_surf.fill((*Colors.SAND_LIGHT, p['alpha']))
            screen.blit(alpha_surf, (int(p['x']), int(p['y'])))
        
        # Sprite de criatura actual
        self._draw_creature(screen)
        
        # Panel de información
        self._draw_info_panel(screen)
        
        # Barra de progreso
        self._draw_progress(screen)
        
        # Texto de carga
        self._draw_loading_text(screen)
    
    def _draw_creature(self, screen):
        """Dibuja sprite de criatura con animación"""
        if not self.creature_sprites:
            return
        
        creature = self.creature_sprites[self.current_creature_idx]
        sprite = assets.get_sprite(creature['sprite'])
        
        # Escalar sprite para display
        display_size = 200
        scaled = pygame.transform.scale(sprite, (display_size, display_size))
        
        # Animación de flotación
        float_y = math.sin(pygame.time.get_ticks() * 0.002) * 8
        
        x = SCREEN_WIDTH // 2 - display_size // 2
        y = int(SCREEN_HEIGHT // 2 - display_size // 2 - 60 + float_y)
        
        # Sombra
        shadow = pygame.Surface((display_size, 20), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 60))
        screen.blit(shadow, (x, y + display_size - 5))
        
        screen.blit(scaled, (x, y))
        
        # Nombre de la criatura
        font = assets.get_font('medium')
        name_surf = font.render(creature['nombre'], True, Colors.GOLD)
        name_rect = name_surf.get_rect(centerx=SCREEN_WIDTH//2, top=y + display_size + 10)
        screen.blit(name_surf, name_rect)
    
    def _draw_info_panel(self, screen):
        """Dibuja panel con tip de lore"""
        panel_w = 700
        panel_h = 80
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = SCREEN_HEIGHT - 180
        
        # Fondo del panel
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((*Colors.UI_PANEL, 200))
        pygame.draw.rect(panel_surf, Colors.GOLD_DARK, (0, 0, panel_w, panel_h), 2)
        screen.blit(panel_surf, (panel_x, panel_y))
        
        # Icono de consejo
        font_small = assets.get_font('small')
        tip_label = font_small.render("[ LORE ]", True, Colors.GOLD)
        screen.blit(tip_label, (panel_x + 10, panel_y + 8))
        
        # Texto del tip con fade
        tip_alpha = 255
        fade_time = 0.3
        if self.tip_timer < fade_time:
            tip_alpha = int(255 * self.tip_timer / fade_time)
        elif self.tip_timer > self.tip_duration - fade_time:
            tip_alpha = int(255 * (self.tip_duration - self.tip_timer) / fade_time)
        
        tip_text = self.lore_tips[self.current_tip_idx]
        font_tip = assets.get_font('small')
        
        # Wrap de texto
        words = tip_text.split()
        lines = []
        current_line = []
        max_width = panel_w - 20
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surf = font_tip.render(test_line, True, Colors.UI_TEXT)
            if test_surf.get_width() > max_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines[:2]):
            line_surf = font_tip.render(line, True, Colors.UI_TEXT)
            line_surf.set_alpha(tip_alpha)
            screen.blit(line_surf, (panel_x + 10, panel_y + 30 + i * 20))
    
    def _draw_progress(self, screen):
        """Dibuja barra de progreso falsa"""
        bar_w = 600
        bar_h = 20
        bar_x = (SCREEN_WIDTH - bar_w) // 2
        bar_y = SCREEN_HEIGHT - 90
        
        # Fondo
        pygame.draw.rect(screen, Colors.GRAY_DARK, (bar_x, bar_y, bar_w, bar_h))
        
        # Progreso
        progress = self._progress_curve[self._curve_idx]
        fill_w = int(bar_w * progress)
        
        if fill_w > 0:
            # Gradiente de color en la barra
            for i in range(fill_w):
                ratio = i / bar_w
                r = int(Colors.BROWN_MED[0] + (Colors.GOLD[0] - Colors.BROWN_MED[0]) * ratio)
                g = int(Colors.BROWN_MED[1] + (Colors.GOLD[1] - Colors.BROWN_MED[1]) * ratio)
                b = int(Colors.BROWN_MED[2] + (Colors.GOLD[2] - Colors.BROWN_MED[2]) * ratio)
                pygame.draw.line(screen, (r, g, b),
                                 (bar_x + i, bar_y),
                                 (bar_x + i, bar_y + bar_h - 1))
        
        # Borde
        pygame.draw.rect(screen, Colors.GOLD_DARK, (bar_x, bar_y, bar_w, bar_h), 2)
        
        # Porcentaje
        font = assets.get_font('small')
        pct_text = f"{int(progress * 100)}%"
        pct_surf = font.render(pct_text, True, Colors.UI_TEXT)
        screen.blit(pct_surf, (bar_x + bar_w + 10, bar_y + 2))
        
        # Tiempo transcurrido (debug/info)
        time_text = f"{min(self.elapsed_ms/1000, 7.0):.1f}s / 7.0s"
        time_surf = assets.get_font('tiny').render(time_text, True, Colors.UI_TEXT_DIM)
        screen.blit(time_surf, (bar_x, bar_y + bar_h + 5))
    
    def _draw_loading_text(self, screen):
        """Dibuja texto de carga animado"""
        dots = '.' * self.dot_count
        loading_text = f"CARGANDO{dots}"
        
        font = assets.get_font('large')
        text_surf = font.render(loading_text, True, Colors.SAND)
        text_rect = text_surf.get_rect(centerx=SCREEN_WIDTH//2, top=30)
        screen.blit(text_surf, text_rect)
        
        # Subtítulo
        mode_text = "NUEVA PARTIDA" if self.mode == 'new' else "CARGANDO PARTIDA"
        font_sub = assets.get_font('small')
        sub_surf = font_sub.render(mode_text, True, Colors.UI_TEXT_DIM)
        sub_rect = sub_surf.get_rect(centerx=SCREEN_WIDTH//2, top=80)
        screen.blit(sub_surf, sub_rect)
