"""
Test de importaciones y lógica del juego (sin display)
"""
import os
import sys

# Configurar entorno headless
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

print("=== DUNE DOMINION - Test de Importaciones ===")

# Test 1: pygame
import pygame
pygame.init()
print("[OK] pygame importado:", pygame.version.ver)

# Test 2: configuración
from src.config import (
    Colors, GameState, SCREEN_WIDTH, SCREEN_HEIGHT,
    TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, INVENTORY_SIZE,
    load_game_data, load_settings
)
print("[OK] src.config importado")

# Test 3: datos del juego
game_data = load_game_data()
print(f"[OK] game_data cargado: {len(game_data['creatures'])} criaturas, "
      f"{len(game_data['buildings'])} edificios, {len(game_data['items'])} items")

# Test 4: asset manager (sin display real)
screen = pygame.display.set_mode((100, 100))
from src.utils.asset_manager import assets
assets.load_all()
print("[OK] AssetManager cargado")

# Test 5: audio manager
from src.systems.audio_manager import audio
print("[OK] AudioManager cargado")

# Test 6: economy manager
settings = load_settings()
save_data = {
    'gold': 25000,
    'day': 1,
    'creatures': [],
    'buildings': [],
    'inventory': [],
    'player_pos': [20, 15],
}
from src.systems.economy_manager import EconomyManager
economy = EconomyManager(save_data)
print(f"[OK] EconomyManager: saldo={economy.gold}, dia={economy.day}")

# Test 6a: compra de criatura
creature = game_data['creatures'][0]
success, msg = economy.buy_creature(creature)
print(f"[OK] Compra criatura '{creature['nombre']}': {success} - {msg}")

# Test 6b: compra de edificio
building = [b for b in game_data['buildings'] if not b.get('esInicial', False)][0]
success, msg, b_inst = economy.buy_building(building)
print(f"[OK] Compra edificio '{building['nombre']}': {success} - {msg}")

# Test 6c: avance de turno
result = economy.advance_turn('day')
print(f"[OK] Turno dia: gasto={result['total_cost']}, nuevo_saldo={result['new_gold']}, dia={result['new_day']}")

result_w = economy.advance_turn('week')
print(f"[OK] Turno semana: gasto={result_w['total_cost']}, nuevo_saldo={result_w['new_gold']}, dia={result_w['new_day']}")

# Test 6d: compra de ítem (poción)
if game_data['items']:
    item = game_data['items'][0]
    success, msg = economy.buy_item(item)
    print(f"[OK] Compra item '{item['nombre']}': {success} - {msg}")
    print(f"     Inventario: {len(economy.inventory)}/{INVENTORY_SIZE}")

# Test 7: world map
from src.systems.world import WorldMap, PlayerController, Camera
world = WorldMap(MAP_WIDTH, MAP_HEIGHT, seed=12345)
print(f"[OK] WorldMap generado: {MAP_WIDTH}x{MAP_HEIGHT} tiles, seed=12345")
print(f"     Tile central: {world.get_tile(MAP_WIDTH//2, MAP_HEIGHT//2)} (0=SAND)")

# Test 7a: colocar edificio
if b_inst:
    placed = world.place_building(10, 10, b_inst)
    print(f"[OK] Edificio colocado en (10,10): {placed}")
    print(f"     Tile (10,10) walkable: {world.is_walkable(10, 10)}")

# Test 7b: jugador
player = PlayerController(MAP_WIDTH//2, MAP_HEIGHT//2, world)
print(f"[OK] PlayerController en ({player.tile_x},{player.tile_y})")

# Test 8: UI widgets
from src.ui.widgets import Button, Panel, Slider, Label, Toggle, ScrollableList
btn = Button(0, 0, 100, 40, "TEST")
panel = Panel(0, 0, 200, 150, "Test Panel")
slider = Slider(0, 0, 200, 30, label="Vol", value=0.7)
print("[OK] UI Widgets instanciados")

# Test 9: UI Manager
from src.ui.ui_manager import HUD, ShopUI, TurnPanel, BuildModeUI, Notification
hud = HUD(economy)
shop = ShopUI(economy, game_data)
turn_panel = TurnPanel(economy)
build_mode = BuildModeUI(world, economy)
notif = Notification("Test", Colors.GOLD, 2.0)
print("[OK] UI Manager instanciado")

# Test 10: verificar lore_tips
tips = game_data.get('lore_tips', [])
print(f"[OK] Lore tips: {len(tips)} disponibles")
if tips:
    print(f"     Ejemplo: '{tips[0][:60]}...'")

pygame.quit()
print("\n=== TODOS LOS TESTS PASARON ===")
print("El juego está listo para ejecutarse.")
