"""
DUNE DOMINION - Configuración Global
Constantes, rutas y configuración del juego
"""
import os
import json

# ─── RUTAS ───────────────────────────────────────────────────────────────────
# Soporte para PyInstaller: usar _MEIPASS si está disponible
import sys
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Ejecutando desde PyInstaller bundle
    BASE_DIR = sys._MEIPASS
    SAVES_DIR_BASE = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SAVES_DIR_BASE = BASE_DIR
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DATA_DIR = os.path.join(BASE_DIR, 'data')
SPRITES_DIR = os.path.join(ASSETS_DIR, 'sprites')
MUSIC_DIR = os.path.join(ASSETS_DIR, 'music')
SAVES_DIR = os.path.join(SAVES_DIR_BASE, 'saves')

CREATURES_DIR = os.path.join(SPRITES_DIR, 'creatures_8bit')
BUILDINGS_DIR = os.path.join(SPRITES_DIR, 'buildings_8bit')
TILES_DIR = os.path.join(SPRITES_DIR, 'tiles')
UI_DIR = os.path.join(SPRITES_DIR, 'ui')

# ─── PANTALLA ─────────────────────────────────────────────────────────────────
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "DUNE DOMINION"
WINDOW_ICON = None

# ─── TILE ─────────────────────────────────────────────────────────────────────
TILE_SIZE = 32
MAP_WIDTH = 40   # tiles
MAP_HEIGHT = 30  # tiles

# ─── PALETA DE COLORES DUNE ───────────────────────────────────────────────────
class Colors:
    BLACK       = (0, 0, 0)
    WHITE       = (255, 255, 255)
    SAND        = (210, 170, 100)
    SAND_DARK   = (133, 76, 48)
    SAND_LIGHT  = (240, 208, 148)
    GOLD        = (255, 200, 0)
    GOLD_DARK   = (180, 130, 0)
    BROWN       = (100, 60, 20)
    BROWN_DARK  = (68, 36, 52)
    BROWN_MED   = (133, 76, 48)
    BLUE_SPICE  = (89, 125, 206)   # Azul ojos especia
    BLUE_DARK   = (48, 52, 109)
    RED         = (208, 70, 72)
    GREEN       = (109, 170, 44)
    GRAY        = (117, 113, 97)
    GRAY_DARK   = (78, 74, 78)
    GRAY_LIGHT  = (133, 149, 161)
    ORANGE      = (222, 136, 56)
    TRANSPARENT = (0, 0, 0, 0)
    
    # UI específicos
    UI_BG           = (20, 12, 28)
    UI_PANEL        = (40, 28, 20)
    UI_PANEL_BORDER = (133, 76, 48)
    UI_TEXT         = (240, 208, 148)
    UI_TEXT_DIM     = (133, 149, 161)
    UI_HIGHLIGHT    = (255, 200, 0)
    UI_ERROR        = (208, 70, 72)
    UI_SUCCESS      = (109, 170, 44)
    UI_BTN_NORMAL   = (68, 36, 52)
    UI_BTN_HOVER    = (100, 60, 80)
    UI_BTN_PRESSED  = (40, 20, 35)
    
    # Rareza
    RARITY_COMUN      = (133, 149, 161)
    RARITY_RARO       = (89, 125, 206)
    RARITY_EPICO      = (180, 100, 200)
    RARITY_LEGENDARIO = (255, 200, 0)

# ─── FUENTES ──────────────────────────────────────────────────────────────────
FONT_SIZES = {
    'tiny':   10,
    'small':  14,
    'medium': 18,
    'large':  24,
    'title':  36,
    'huge':   52,
}

# ─── ESTADOS DEL JUEGO ────────────────────────────────────────────────────────
class GameState:
    MAIN_MENU    = "main_menu"
    LOADING      = "loading"
    GAMEPLAY     = "gameplay"
    SETTINGS     = "settings"
    CREDITS      = "credits"
    ACCESSIBILITY = "accessibility"

# ─── ECONOMÍA ─────────────────────────────────────────────────────────────────
STARTING_GOLD = 25000
TURN_TYPES = ['day', 'week']

# ─── INVENTARIO ───────────────────────────────────────────────────────────────
INVENTORY_SIZE = 8  # Aumentado para armas

# ─── CICLO DÍA/NOCHE ──────────────────────────────────────────────────────────
DAY_DURATION_SEC = 300  # 5 minutos
NIGHT_DURATION_SEC = 120 # 2 minutos de noche intensa
TIME_SCALE = 1.0        # Multiplicador de tiempo para debug

# ─── ENEMIGOS ─────────────────────────────────────────────────────────────────
ENEMY_BASE_HP = 50
ENEMY_BASE_DAMAGE = 10
ENEMY_SPEED = 80
ENEMY_SPAWN_RATE = 5.0  # Segundos entre spawns nocturnos

# ─── LOADING SCREEN ───────────────────────────────────────────────────────────
LOADING_DURATION_MS = 7000  # 7 segundos exactos

# ─── AUDIO ────────────────────────────────────────────────────────────────────
DEFAULT_MASTER_VOL = 0.8
DEFAULT_BGM_VOL    = 0.6
DEFAULT_SFX_VOL    = 0.7

# ─── CONTROLES POR DEFECTO ────────────────────────────────────────────────────
DEFAULT_KEYS = {
    'move_up':    'w',
    'move_down':  's',
    'move_left':  'a',
    'move_right': 'd',
    'interact':   'e',
    'inventory':  'i',
    'shop':       'tab',
    'advance_turn': 'space',
    'pause':      'escape',
}

# ─── CONFIGURACIÓN GUARDADA ───────────────────────────────────────────────────
SETTINGS_FILE = os.path.join(SAVES_DIR, 'settings.json')
SAVE_FILE     = os.path.join(SAVES_DIR, 'savegame.json')

def load_settings():
    """Carga configuración guardada o retorna defaults"""
    defaults = {
        'resolution': [SCREEN_WIDTH, SCREEN_HEIGHT],
        'fullscreen': False,
        'vsync': False,
        'master_vol': DEFAULT_MASTER_VOL,
        'bgm_vol': DEFAULT_BGM_VOL,
        'sfx_vol': DEFAULT_SFX_VOL,
        'keys': DEFAULT_KEYS.copy(),
        'colorblind_mode': 'none',  # none, protanopia, deuteranopia, tritanopia
        'font_scale': 1.0,
        'photosensitivity': False,
        'text_speed': 1.0,
    }
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                saved = json.load(f)
                defaults.update(saved)
    except Exception:
        pass
    return defaults

def save_settings(settings):
    """Guarda configuración"""
    os.makedirs(SAVES_DIR, exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def load_game_data():
    """Carga datos del juego (criaturas, edificios, ítems)"""
    path = os.path.join(DATA_DIR, 'game_data.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
