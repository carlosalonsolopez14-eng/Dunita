# -*- mode: python ; coding: utf-8 -*-
"""
DUNE DOMINION - PyInstaller Spec File
Genera ejecutable standalone con todos los assets incluidos
"""
import os

block_cipher = None

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(SPEC))

# Assets a incluir
datas = [
    # Sprites de criaturas
    (os.path.join(BASE_DIR, 'assets/sprites/creatures_8bit'), 'assets/sprites/creatures_8bit'),
    # Sprites de edificios
    (os.path.join(BASE_DIR, 'assets/sprites/buildings_8bit'), 'assets/sprites/buildings_8bit'),
    # Tiles
    (os.path.join(BASE_DIR, 'assets/sprites/tiles'), 'assets/sprites/tiles'),
    # UI
    (os.path.join(BASE_DIR, 'assets/sprites/ui'), 'assets/sprites/ui'),
    # Datos del juego
    (os.path.join(BASE_DIR, 'data/game_data.json'), 'data'),
]

# Añadir música si existe
music_dir = os.path.join(BASE_DIR, 'assets/music')
if os.path.exists(music_dir) and os.listdir(music_dir):
    datas.append((music_dir, 'assets/music'))

a = Analysis(
    [os.path.join(BASE_DIR, 'main.py')],
    pathex=[BASE_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'pygame',
        'pygame.mixer',
        'pygame.font',
        'pygame.image',
        'pygame.transform',
        'src',
        'src.config',
        'src.engine',
        'src.states.main_menu',
        'src.states.loading_screen',
        'src.states.gameplay',
        'src.systems.audio_manager',
        'src.systems.economy_manager',
        'src.systems.world',
        'src.ui.widgets',
        'src.ui.ui_manager',
        'src.utils.asset_manager',
        'json',
        'math',
        'random',
        'os',
        'sys',
        'array',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy', 'PIL'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DuneDominion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Sin consola en Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DuneDominion',
)
