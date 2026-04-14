"""
DUNE DOMINION - Estado: Main Menu
Menú principal con música, botones y submódulos de Configuración, Accesibilidad y Créditos
"""
import pygame
import math
import os

from src.engine import BaseState
from src.config import (
    GameState, Colors, SCREEN_WIDTH, SCREEN_HEIGHT,
    save_settings
)
from src.ui.widgets import Button, Panel, Slider, Label, Toggle
from src.utils.asset_manager import assets
from src.systems.audio_manager import audio


# ─── FONDO ANIMADO ────────────────────────────────────────────────────────────

class DuneBackground:
    """Fondo animado de dunas con partículas de arena"""

    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.time = 0.0
        self.particles = []
        self._init_particles()
        self._surface = pygame.Surface((width, height))

    def _init_particles(self):
        import random
        for _ in range(80):
            self.particles.append({
                'x': random.randint(0, self.w),
                'y': random.randint(0, self.h),
                'speed': random.uniform(20, 60),
                'size': random.randint(1, 3),
                'alpha': random.randint(80, 180),
            })

    def update(self, dt):
        self.time += dt
        import random
        for p in self.particles:
            p['x'] += p['speed'] * dt
            if p['x'] > self.w:
                p['x'] = -p['size']
                p['y'] = random.randint(0, self.h)

    def draw(self, surface):
        # Gradiente de fondo
        self._surface.fill(Colors.UI_BG)

        # Dunas (curvas sinusoidales)
        dune_colors = [
            (80, 50, 20),
            (100, 65, 25),
            (120, 80, 35),
            (140, 95, 45),
        ]

        for i, color in enumerate(dune_colors):
            offset = i * 60 + 200
            phase = self.time * 0.3 + i * 0.8
            points = [(0, self.h)]
            for x in range(0, self.w + 10, 10):
                y = offset + math.sin(x * 0.008 + phase) * 30 + math.sin(x * 0.02 + phase * 1.3) * 15
                points.append((x, int(y)))
            points.append((self.w, self.h))
            pygame.draw.polygon(self._surface, color, points)

        surface.blit(self._surface, (0, 0))

        # Partículas de arena
        for p in self.particles:
            alpha_surf = pygame.Surface((p['size'], p['size']), pygame.SRCALPHA)
            alpha_surf.fill((*Colors.SAND_LIGHT, p['alpha']))
            surface.blit(alpha_surf, (int(p['x']), int(p['y'])))


# ─── ESTADO MAIN MENU ─────────────────────────────────────────────────────────

class MainMenuState(BaseState):

    def on_enter(self, **kwargs):
        self.background = DuneBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.sub_state = 'main'  # main, settings, accessibility, credits
        self.title_time = 0.0

        # Iniciar música de menú
        audio.play_bgm(GameState.MAIN_MENU)

        self._build_main_menu()
        self._build_settings_panel()
        self._build_accessibility_panel()
        self._build_credits_panel()

    def _build_main_menu(self):
        """Construye botones del menú principal"""
        cx = SCREEN_WIDTH // 2
        btn_w, btn_h = 220, 48
        start_y = SCREEN_HEIGHT // 2 - 20
        spacing = 60

        self.main_buttons = [
            Button(cx - btn_w//2, start_y + 0*spacing, btn_w, btn_h,
                   "NUEVA PARTIDA", self._on_new_game),
            Button(cx - btn_w//2, start_y + 1*spacing, btn_w, btn_h,
                   "CARGAR PARTIDA", self._on_load_game),
            Button(cx - btn_w//2, start_y + 2*spacing, btn_w, btn_h,
                   "CONFIGURACION", self._on_settings),
            Button(cx - btn_w//2, start_y + 3*spacing, btn_w, btn_h,
                   "ACCESIBILIDAD", self._on_accessibility),
            Button(cx - btn_w//2, start_y + 4*spacing, btn_w, btn_h,
                   "CREDITOS", self._on_credits),
        ]

    def _build_settings_panel(self):
        """Construye panel de configuración"""
        pw, ph = 600, 500
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2

        self.settings_panel = Panel(px, py, pw, ph, "CONFIGURACION")

        # Resoluciones disponibles
        self.resolutions = [
            (1280, 720), (1366, 768), (1600, 900), (1920, 1080)
        ]
        self.res_idx = 0
        for i, (w, h) in enumerate(self.resolutions):
            if [w, h] == self.settings.get('resolution', [1280, 720]):
                self.res_idx = i

        lx = px + 30

        # Sliders de audio
        self.slider_master = Slider(
            lx, py + 60, pw - 60, 30,
            label="Master",
            value=self.settings.get('master_vol', 0.8),
            callback=self._on_master_vol
        )
        self.slider_bgm = Slider(
            lx, py + 120, pw - 60, 30,
            label="BGM",
            value=self.settings.get('bgm_vol', 0.6),
            callback=self._on_bgm_vol
        )
        self.slider_sfx = Slider(
            lx, py + 180, pw - 60, 30,
            label="SFX",
            value=self.settings.get('sfx_vol', 0.7),
            callback=self._on_sfx_vol
        )

        # Toggles
        self.toggle_fullscreen = Toggle(
            lx, py + 250, 200, 30,
            label="Pantalla Completa",
            value=self.settings.get('fullscreen', False),
            callback=lambda v: self.settings.update({'fullscreen': v})
        )
        self.toggle_vsync = Toggle(
            lx, py + 290, 200, 30,
            label="V-Sync",
            value=self.settings.get('vsync', False),
            callback=lambda v: self.settings.update({'vsync': v})
        )

        # Botones resolución
        self.btn_res_prev = Button(
            lx, py + 340, 40, 32, "<",
            callback=self._prev_resolution, font_size='medium'
        )
        self.btn_res_next = Button(
            lx + 200, py + 340, 40, 32, ">",
            callback=self._next_resolution, font_size='medium'
        )

        # Botón cerrar
        self.btn_settings_close = Button(
            px + pw//2 - 80, py + ph - 60, 160, 40,
            "APLICAR Y CERRAR",
            callback=self._close_settings,
            font_size='small'
        )

        self.settings_widgets = [
            self.slider_master, self.slider_bgm, self.slider_sfx,
            self.toggle_fullscreen, self.toggle_vsync,
            self.btn_res_prev, self.btn_res_next,
            self.btn_settings_close
        ]

    def _build_accessibility_panel(self):
        """Construye panel de accesibilidad"""
        pw, ph = 600, 480
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2

        self.acc_panel = Panel(px, py, pw, ph, "ACCESIBILIDAD")
        lx = px + 30

        # Modos daltonismo
        self.colorblind_modes = ['none', 'protanopia', 'deuteranopia', 'tritanopia']
        self.colorblind_labels = ['Normal', 'Protanopia', 'Deuteranopia', 'Tritanopia']
        self.colorblind_idx = 0
        current = self.settings.get('colorblind_mode', 'none')
        if current in self.colorblind_modes:
            self.colorblind_idx = self.colorblind_modes.index(current)

        self.btn_cb_prev = Button(lx, py + 70, 40, 32, "<",
                                   callback=self._prev_colorblind)
        self.btn_cb_next = Button(lx + 200, py + 70, 40, 32, ">",
                                   callback=self._next_colorblind)

        # Escala de fuente
        self.slider_font_scale = Slider(
            lx, py + 140, pw - 60, 30,
            min_val=0.8, max_val=1.5,
            label="Escala de Texto",
            value=self.settings.get('font_scale', 1.0),
            callback=lambda v: self.settings.update({'font_scale': v})
        )

        # Modo fotosensibilidad
        self.toggle_photosensitivity = Toggle(
            lx, py + 210, 300, 30,
            label="Modo Fotosensibilidad (sin destellos)",
            value=self.settings.get('photosensitivity', False),
            callback=lambda v: self.settings.update({'photosensitivity': v})
        )

        # Velocidad de texto
        self.slider_text_speed = Slider(
            lx, py + 270, pw - 60, 30,
            min_val=0.5, max_val=2.0,
            label="Velocidad de Texto",
            value=self.settings.get('text_speed', 1.0),
            callback=lambda v: self.settings.update({'text_speed': v})
        )

        self.btn_acc_close = Button(
            px + pw//2 - 80, py + ph - 60, 160, 40,
            "GUARDAR Y CERRAR",
            callback=self._close_accessibility,
            font_size='small'
        )

        self.acc_widgets = [
            self.btn_cb_prev, self.btn_cb_next,
            self.slider_font_scale, self.toggle_photosensitivity,
            self.slider_text_speed, self.btn_acc_close
        ]

    def _build_credits_panel(self):
        """Construye panel de créditos"""
        pw, ph = 500, 400
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2

        self.credits_panel = Panel(px, py, pw, ph, "CREDITOS")

        self.credits_lines = [
            ("DUNE DOMINION", 'large', Colors.GOLD),
            ("", 'small', Colors.UI_TEXT),
            ("Basado en el universo de DUNE", 'small', Colors.UI_TEXT),
            ("por Frank Herbert", 'small', Colors.UI_TEXT_DIM),
            ("", 'small', Colors.UI_TEXT),
            ("Datos extraidos de:", 'small', Colors.UI_HIGHLIGHT),
            ("dunepixart-tj6e9gfb.manus.space", 'tiny', Colors.BLUE_SPICE),
            ("dunecatalog-mltpe2ng.manus.space", 'tiny', Colors.BLUE_SPICE),
            ("github.com/carlosalonsolopez14-eng/Dunita", 'tiny', Colors.BLUE_SPICE),
            ("", 'small', Colors.UI_TEXT),
            ("Desarrollado con Python + Pygame", 'small', Colors.UI_TEXT_DIM),
            ("2026 - DUNE DOMINION v1.0", 'small', Colors.UI_TEXT_DIM),
        ]

        self.btn_credits_close = Button(
            px + pw//2 - 60, py + ph - 60, 120, 40,
            "CERRAR",
            callback=self._close_credits,
            font_size='small'
        )

    # ─── CALLBACKS ────────────────────────────────────────────────────────────

    def _on_new_game(self):
        self.engine.new_game()
        # Pasar is_new para que GameplayState sepa que debe mostrar el lore
        self.engine.change_state(GameState.LOADING, mode='new', is_new=True)

    def _on_load_game(self):
        if self.engine.load_game():
            self.engine.change_state(GameState.LOADING, mode='load')
        else:
            # Sin guardado: mostrar mensaje
            self._show_no_save_message()

    def _show_no_save_message(self):
        self._no_save_timer = 2.0

    def _on_settings(self):
        self.sub_state = 'settings'

    def _on_accessibility(self):
        self.sub_state = 'accessibility'

    def _on_credits(self):
        self.sub_state = 'credits'
        # Cambiar música a la de créditos
        audio.play_bgm(GameState.CREDITS)

    def _on_master_vol(self, v):
        self.settings['master_vol'] = v
        audio.set_master_vol(v)

    def _on_bgm_vol(self, v):
        self.settings['bgm_vol'] = v
        audio.set_bgm_vol(v)

    def _on_sfx_vol(self, v):
        self.settings['sfx_vol'] = v
        audio.set_sfx_vol(v)

    def _prev_resolution(self):
        self.res_idx = (self.res_idx - 1) % len(self.resolutions)
        w, h = self.resolutions[self.res_idx]
        self.settings['resolution'] = [w, h]

    def _next_resolution(self):
        self.res_idx = (self.res_idx + 1) % len(self.resolutions)
        w, h = self.resolutions[self.res_idx]
        self.settings['resolution'] = [w, h]

    def _prev_colorblind(self):
        self.colorblind_idx = (self.colorblind_idx - 1) % len(self.colorblind_modes)
        self.settings['colorblind_mode'] = self.colorblind_modes[self.colorblind_idx]

    def _next_colorblind(self):
        self.colorblind_idx = (self.colorblind_idx + 1) % len(self.colorblind_modes)
        self.settings['colorblind_mode'] = self.colorblind_modes[self.colorblind_idx]

    def _close_settings(self):
        """Guarda la configuración y aplica los cambios de pantalla y audio en caliente."""
        save_settings(self.settings)
        # Aplicar cambios de pantalla (resolución, fullscreen, vsync)
        self.engine.apply_display_settings()
        # Aplicar cambios de audio (volúmenes)
        self.engine.apply_audio_settings()
        self.sub_state = 'main'

    def _close_accessibility(self):
        """Guarda la configuración de accesibilidad y aplica los cambios en caliente."""
        # Actualizar modo daltonismo en settings
        self.settings['colorblind_mode'] = self.colorblind_modes[self.colorblind_idx]
        save_settings(self.settings)
        # Aplicar escala de fuente en caliente
        self.engine.reload_fonts()
        self.sub_state = 'main'

    def _close_credits(self):
        """Cierra el panel de créditos y vuelve a la música del menú."""
        self.sub_state = 'main'
        # Restaurar música del menú al salir de créditos
        audio.play_bgm(GameState.MAIN_MENU)

    # ─── HANDLE EVENTS ────────────────────────────────────────────────────────

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.sub_state == 'credits':
                    # Al salir de créditos con ESC, restaurar música del menú
                    self._close_credits()
                elif self.sub_state != 'main':
                    self.sub_state = 'main'

            if self.sub_state == 'main':
                for btn in self.main_buttons:
                    btn.handle_event(event)

            elif self.sub_state == 'settings':
                for w in self.settings_widgets:
                    w.handle_event(event)

            elif self.sub_state == 'accessibility':
                for w in self.acc_widgets:
                    w.handle_event(event)

            elif self.sub_state == 'credits':
                self.btn_credits_close.handle_event(event)

    # ─── UPDATE ───────────────────────────────────────────────────────────────

    def update(self, dt):
        self.title_time += dt
        self.background.update(dt)

        if hasattr(self, '_no_save_timer'):
            self._no_save_timer -= dt
            if self._no_save_timer <= 0:
                del self._no_save_timer

    # ─── DRAW ─────────────────────────────────────────────────────────────────

    def draw(self, screen):
        # Fondo
        self.background.draw(screen)

        if self.sub_state == 'main':
            self._draw_main(screen)
        elif self.sub_state == 'settings':
            self._draw_main(screen)
            self._draw_settings(screen)
        elif self.sub_state == 'accessibility':
            self._draw_main(screen)
            self._draw_accessibility(screen)
        elif self.sub_state == 'credits':
            self._draw_main(screen)
            self._draw_credits(screen)

        # Aplicar filtro de daltonismo si está activo
        colorblind_mode = self.settings.get('colorblind_mode', 'none')
        if colorblind_mode != 'none':
            filtered = assets.apply_colorblind_filter(screen, colorblind_mode)
            screen.blit(filtered, (0, 0))

    def _draw_main(self, screen):
        # Título con efecto de brillo pulsante
        pulse = 0.5 + 0.5 * math.sin(self.title_time * 2.0)
        if not self.settings.get('photosensitivity', False):
            title_color = (
                int(200 + 55 * pulse),
                int(160 + 40 * pulse),
                int(50 + 50 * pulse)
            )
        else:
            title_color = Colors.GOLD

        font_title = assets.get_font('huge')
        title_surf = font_title.render("DUNE DOMINION", True, title_color)
        title_rect = title_surf.get_rect(centerx=SCREEN_WIDTH//2, top=60)
        screen.blit(title_surf, title_rect)

        # Subtítulo
        font_sub = assets.get_font('medium')
        sub_surf = font_sub.render("El Dominio del Desierto", True, Colors.SAND)
        sub_rect = sub_surf.get_rect(centerx=SCREEN_WIDTH//2, top=130)
        screen.blit(sub_surf, sub_rect)

        # Línea decorativa
        pygame.draw.line(screen, Colors.GOLD_DARK,
                         (SCREEN_WIDTH//2 - 200, 165),
                         (SCREEN_WIDTH//2 + 200, 165), 2)

        # Botones
        for btn in self.main_buttons:
            btn.draw(screen)

        # Mensaje sin guardado
        if hasattr(self, '_no_save_timer'):
            font = assets.get_font('small')
            msg = font.render("No hay partida guardada", True, Colors.UI_ERROR)
            screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT - 80))

        # Versión
        font_tiny = assets.get_font('tiny')
        ver = font_tiny.render("v1.0 | DUNE DOMINION", True, Colors.UI_TEXT_DIM)
        screen.blit(ver, (10, SCREEN_HEIGHT - 20))

    def _draw_settings(self, screen):
        # Overlay oscuro
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        self.settings_panel.draw(screen)

        # Sección audio
        font = assets.get_font('small')
        screen.blit(font.render("-- AUDIO --", True, Colors.UI_HIGHLIGHT),
                    (self.settings_panel.rect.left + 30,
                     self.settings_panel.rect.top + 42))

        self.slider_master.draw(screen)
        self.slider_bgm.draw(screen)
        self.slider_sfx.draw(screen)

        # Sección gráficos
        screen.blit(font.render("-- GRAFICOS --", True, Colors.UI_HIGHLIGHT),
                    (self.settings_panel.rect.left + 30,
                     self.settings_panel.rect.top + 232))

        self.toggle_fullscreen.draw(screen)
        self.toggle_vsync.draw(screen)

        # Resolución
        screen.blit(font.render("Resolucion:", True, Colors.UI_TEXT),
                    (self.settings_panel.rect.left + 30,
                     self.settings_panel.rect.top + 322))

        w, h = self.resolutions[self.res_idx]
        res_text = font.render(f"{w} x {h}", True, Colors.GOLD)
        screen.blit(res_text, (self.settings_panel.rect.left + 90,
                               self.settings_panel.rect.top + 348))

        self.btn_res_prev.draw(screen)
        self.btn_res_next.draw(screen)
        self.btn_settings_close.draw(screen)

        # Keybinding info
        tiny = assets.get_font('tiny')
        kb_text = tiny.render("Controles: WASD=Mover | E=Interactuar | I/Tab=Inventario | Espacio=Turno | Esc=Pausa",
                              True, Colors.UI_TEXT_DIM)
        screen.blit(kb_text, (self.settings_panel.rect.left + 10,
                               self.settings_panel.rect.bottom - 80))

    def _draw_accessibility(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        self.acc_panel.draw(screen)

        font = assets.get_font('small')
        px = self.acc_panel.rect.left
        py = self.acc_panel.rect.top

        # Daltonismo
        screen.blit(font.render("Filtro Daltonismo:", True, Colors.UI_HIGHLIGHT),
                    (px + 30, py + 45))

        cb_label = self.colorblind_labels[self.colorblind_idx]
        cb_surf = font.render(cb_label, True, Colors.GOLD)
        screen.blit(cb_surf, (px + 80, py + 75))

        self.btn_cb_prev.draw(screen)
        self.btn_cb_next.draw(screen)

        self.slider_font_scale.draw(screen)
        self.toggle_photosensitivity.draw(screen)
        self.slider_text_speed.draw(screen)
        self.btn_acc_close.draw(screen)

    def _draw_credits(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        self.credits_panel.draw(screen)

        px = self.credits_panel.rect.left
        py = self.credits_panel.rect.top + 40

        for i, (text, size, color) in enumerate(self.credits_lines):
            if not text:
                py += 8
                continue
            font = assets.get_font(size)
            surf = font.render(text, True, color)
            rect = surf.get_rect(centerx=self.credits_panel.rect.centerx, top=py)
            screen.blit(surf, rect)
            py += surf.get_height() + 4

        self.btn_credits_close.draw(screen)
