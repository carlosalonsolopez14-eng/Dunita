"""
DUNE DOMINION - Motor Principal del Juego
State Machine: Main_Menu → Loading_Screen → Gameplay_Loop
"""
import pygame
import sys
import os

from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    GameState, load_settings, save_settings, SAVES_DIR
)
from src.utils.asset_manager import assets
from src.systems.audio_manager import audio


class Engine:
    """
    Motor principal del juego.
    Gestiona el ciclo de vida, la máquina de estados y el bucle principal.
    """

    def __init__(self):
        # Inicializar pygame
        pygame.init()

        # Cargar configuración
        self.settings = load_settings()
        os.makedirs(SAVES_DIR, exist_ok=True)

        # Configurar pantalla
        self._setup_display()

        # Reloj
        self.clock = pygame.time.Clock()
        self.running = False
        self.dt = 0.0  # delta time en segundos

        # Máquina de estados
        self.current_state = None
        self.states = {}
        self._pending_state = None
        self._pending_kwargs = {}

        # Cargar assets
        assets.load_all()

        # Datos del juego
        from src.config import load_game_data
        self.game_data = load_game_data()

        # Datos de partida (se inicializan al empezar)
        self.save_data = None

    def _setup_display(self):
        """Configura la ventana de juego"""
        flags = 0
        if self.settings.get('fullscreen', False):
            flags |= pygame.FULLSCREEN
        if self.settings.get('vsync', False):
            flags |= pygame.SCALED

        w, h = self.settings.get('resolution', [SCREEN_WIDTH, SCREEN_HEIGHT])

        try:
            self.screen = pygame.display.set_mode((w, h), flags)
        except Exception:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.set_caption(TITLE)

        # Icono
        try:
            icon = pygame.Surface((32, 32))
            icon.fill((210, 170, 100))
            pygame.draw.circle(icon, (255, 200, 0), (16, 16), 12)
            pygame.display.set_icon(icon)
        except Exception:
            pass

    def apply_display_settings(self):
        """
        Aplica en caliente los cambios de resolución, pantalla completa y vsync
        guardados en self.settings. Actualiza self.screen y la referencia en el
        estado actual para que los cambios sean visibles de inmediato.
        """
        flags = 0
        if self.settings.get('fullscreen', False):
            flags |= pygame.FULLSCREEN
        if self.settings.get('vsync', False):
            flags |= pygame.SCALED

        w, h = self.settings.get('resolution', [SCREEN_WIDTH, SCREEN_HEIGHT])

        try:
            self.screen = pygame.display.set_mode((w, h), flags)
        except Exception:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Actualizar la referencia de pantalla en el estado actual
        if self.current_state is not None:
            self.current_state.screen = self.screen

    def apply_audio_settings(self):
        """
        Aplica en caliente los cambios de volumen guardados en self.settings.
        """
        audio.set_master_vol(self.settings.get('master_vol', 0.8))
        audio.set_bgm_vol(self.settings.get('bgm_vol', 0.6))
        audio.set_sfx_vol(self.settings.get('sfx_vol', 0.7))

    def reload_fonts(self):
        """
        Recarga las fuentes aplicando el font_scale guardado en self.settings.
        """
        assets.reload_fonts(self.settings.get('font_scale', 1.0))

    def register_state(self, name: str, state_class):
        """Registra una clase de estado"""
        self.states[name] = state_class

    def change_state(self, state_name: str, **kwargs):
        """Programa un cambio de estado"""
        self._pending_state = state_name
        self._pending_kwargs = kwargs

    def _do_state_change(self):
        """Ejecuta el cambio de estado pendiente"""
        if self._pending_state is None:
            return

        state_name = self._pending_state
        kwargs = self._pending_kwargs
        self._pending_state = None
        self._pending_kwargs = {}

        if state_name not in self.states:
            print(f"Error: State '{state_name}' not registered")
            return

        # Salir del estado actual
        if self.current_state:
            self.current_state.on_exit()

        # Crear e inicializar nuevo estado
        self.current_state = self.states[state_name](self)
        self.current_state.on_enter(**kwargs)

    def run(self):
        """Bucle principal del juego"""
        self.running = True

        # Iniciar con menú principal
        self.change_state(GameState.MAIN_MENU)
        self._do_state_change()

        while self.running:
            # Delta time
            self.dt = self.clock.tick(FPS) / 1000.0
            self.dt = min(self.dt, 0.05)  # Cap a 50ms para evitar saltos

            # Procesar eventos
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F4 and (pygame.key.get_mods() & pygame.KMOD_ALT):
                        self.quit()
                        return

            # Actualizar estado actual
            if self.current_state:
                self.current_state.handle_events(events)
                self.current_state.update(self.dt)
                self.current_state.draw(self.screen)

            # Cambio de estado pendiente
            if self._pending_state:
                self._do_state_change()

            pygame.display.flip()

        pygame.quit()

    def quit(self):
        """Cierra el juego"""
        save_settings(self.settings)
        self.running = False

    def new_game(self):
        """Inicializa datos de nueva partida"""
        from src.config import STARTING_GOLD
        self.save_data = {
            'gold': STARTING_GOLD,
            'day': 1,
            'creatures': [],      # Lista de criaturas compradas
            'buildings': [],      # Lista de edificios colocados
            'inventory': [],      # Array de pociones (max 4)
            'player_pos': [0, 0], # Posición del jugador en tiles
        }

    def load_game(self):
        """Carga partida guardada"""
        import json
        from src.config import SAVE_FILE
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, 'r') as f:
                    self.save_data = json.load(f)
                return True
        except Exception as e:
            print(f"Load error: {e}")
        return False

    def save_game(self):
        """Guarda la partida actual"""
        import json
        from src.config import SAVE_FILE
        if self.save_data:
            try:
                os.makedirs(SAVES_DIR, exist_ok=True)
                with open(SAVE_FILE, 'w') as f:
                    json.dump(self.save_data, f, indent=2)
            except Exception as e:
                print(f"Save error: {e}")


class BaseState:
    """Clase base para todos los estados del juego"""

    def __init__(self, engine: Engine):
        self.engine = engine
        self.screen = engine.screen
        self.settings = engine.settings

    def on_enter(self, **kwargs):
        """Llamado al entrar al estado"""
        pass

    def on_exit(self):
        """Llamado al salir del estado"""
        pass

    def handle_events(self, events):
        """Procesa eventos de pygame"""
        pass

    def update(self, dt: float):
        """Actualiza lógica del estado"""
        pass

    def draw(self, screen: pygame.Surface):
        """Dibuja el estado"""
        pass
