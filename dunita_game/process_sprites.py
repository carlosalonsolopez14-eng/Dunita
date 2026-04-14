#!/usr/bin/env python3.11
"""
Pixel Art 8-bit Downscaler
Convierte sprites de alta resolución a estética pixel art 8-bit con paleta limitada
"""
from PIL import Image, ImageFilter
import os
import numpy as np

# Paleta de colores desierto/Arrakis (8-bit estilo)
DUNE_PALETTE = [
    (0, 0, 0),        # Negro
    (20, 12, 28),     # Negro oscuro
    (68, 36, 52),     # Marrón oscuro
    (48, 52, 109),    # Azul oscuro
    (78, 74, 78),     # Gris oscuro
    (133, 76, 48),    # Marrón arena
    (52, 101, 36),    # Verde oscuro
    (208, 70, 72),    # Rojo
    (117, 113, 97),   # Gris arena
    (89, 125, 206),   # Azul cielo
    (210, 125, 44),   # Naranja arena
    (133, 149, 161),  # Gris claro
    (109, 170, 44),   # Verde
    (210, 170, 153),  # Beige
    (109, 194, 202),  # Cyan
    (218, 212, 94),   # Amarillo arena
    (222, 136, 56),   # Naranja
    (228, 166, 114),  # Arena claro
    (240, 208, 148),  # Arena muy claro
    (255, 255, 255),  # Blanco
    (255, 200, 100),  # Dorado
    (180, 100, 40),   # Marrón medio
    (100, 60, 20),    # Marrón tierra
    (255, 120, 0),    # Naranja vivo
    (200, 180, 120),  # Beige arena
    (60, 40, 20),     # Marrón muy oscuro
    (140, 100, 60),   # Marrón claro
    (255, 240, 180),  # Crema
    (80, 60, 40),     # Marrón medio oscuro
    (160, 120, 80),   # Marrón claro arena
    (220, 200, 160),  # Arena pálido
    (40, 30, 20),     # Casi negro marrón
]

def find_closest_color(pixel, palette):
    """Encuentra el color más cercano en la paleta"""
    r, g, b = pixel[:3]
    min_dist = float('inf')
    closest = palette[0]
    for color in palette:
        cr, cg, cb = color
        dist = (r - cr)**2 + (g - cg)**2 + (b - cb)**2
        if dist < min_dist:
            min_dist = dist
            closest = color
    return closest

def pixelate_image(img, target_size=(64, 64), palette=None):
    """
    Convierte imagen a pixel art 8-bit:
    1. Redimensiona a tamaño pequeño (pixelación)
    2. Aplica paleta de colores limitada
    3. Escala de vuelta al tamaño objetivo
    """
    # Convertir a RGBA para manejar transparencia
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Paso 1: Downscale agresivo para crear efecto pixel
    pixel_size = (16, 16)  # Resolución interna 8-bit
    small = img.resize(pixel_size, Image.NEAREST)
    
    # Paso 2: Aplicar paleta de colores limitada
    if palette:
        pixels = small.load()
        w, h = small.size
        for y in range(h):
            for x in range(w):
                pixel = pixels[x, y]
                if pixel[3] > 128:  # Si no es transparente
                    new_color = find_closest_color(pixel, palette)
                    pixels[x, y] = (*new_color, pixel[3])
                else:
                    pixels[x, y] = (0, 0, 0, 0)  # Transparente
    
    # Paso 3: Upscale con NEAREST para mantener bordes duros
    result = small.resize(target_size, Image.NEAREST)
    return result

def process_creature_sprites(input_dir, output_dir, size=(64, 64)):
    """Procesa todos los sprites de criaturas"""
    os.makedirs(output_dir, exist_ok=True)
    processed = []
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.png'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            try:
                img = Image.open(input_path)
                pixel_img = pixelate_image(img, target_size=size, palette=DUNE_PALETTE)
                pixel_img.save(output_path)
                print(f"  Processed: {filename} -> {size}")
                processed.append(filename)
            except Exception as e:
                print(f"  Error {filename}: {e}")
    
    return processed

def process_building_sprites(input_dir, output_dir, size=(96, 96)):
    """Procesa sprites de edificios a mayor tamaño"""
    os.makedirs(output_dir, exist_ok=True)
    processed = []
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.png'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            try:
                img = Image.open(input_path)
                # Para edificios usamos resolución interna mayor (24x24)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                small = img.resize((24, 24), Image.LANCZOS)
                # Aplicar paleta
                pixels = small.load()
                w, h = small.size
                for y in range(h):
                    for x in range(w):
                        pixel = pixels[x, y]
                        if pixel[3] > 128:
                            new_color = find_closest_color(pixel, DUNE_PALETTE)
                            pixels[x, y] = (*new_color, 255)
                        else:
                            pixels[x, y] = (0, 0, 0, 0)
                
                result = small.resize(size, Image.NEAREST)
                result.save(output_path)
                print(f"  Processed building: {filename} -> {size}")
                processed.append(filename)
            except Exception as e:
                print(f"  Error {filename}: {e}")
    
    return processed

def create_player_sprite(output_dir):
    """Crea sprite del jugador (avatar mini pixel art)"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Crear sprite del jugador 16x16 -> 32x32
    size = 16
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    pixels = img.load()
    
    # Diseño simple de personaje tipo Fremen
    # Cabeza
    head_color = (210, 170, 153)  # Beige piel
    robe_color = (68, 36, 52)     # Marrón oscuro (ropa Fremen)
    eye_color = (89, 125, 206)    # Azul (ojos azules en glow por especia)
    
    # Cabeza (fila 1-3, col 5-10)
    for y in range(1, 4):
        for x in range(5, 11):
            pixels[x, y] = (*head_color, 255)
    
    # Ojos
    pixels[6, 2] = (*eye_color, 255)
    pixels[9, 2] = (*eye_color, 255)
    
    # Cuerpo/Ropa (fila 4-10)
    for y in range(4, 11):
        for x in range(4, 12):
            pixels[x, y] = (*robe_color, 255)
    
    # Brazos
    for y in range(5, 9):
        pixels[3, y] = (*robe_color, 255)
        pixels[12, y] = (*robe_color, 255)
    
    # Piernas
    for y in range(11, 15):
        pixels[5, y] = (*robe_color, 255)
        pixels[6, y] = (*robe_color, 255)
        pixels[9, y] = (*robe_color, 255)
        pixels[10, y] = (*robe_color, 255)
    
    # Escalar a 32x32
    result = img.resize((32, 32), Image.NEAREST)
    result.save(os.path.join(output_dir, 'player.png'))
    print("  Created: player.png (32x32)")

def create_caseta_sprite(output_dir):
    """Crea sprite de la caseta básica inicial"""
    os.makedirs(output_dir, exist_ok=True)
    
    size = 24
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    pixels = img.load()
    
    wall_color = (133, 76, 48)    # Marrón arena
    roof_color = (100, 60, 20)    # Marrón oscuro
    door_color = (68, 36, 52)     # Marrón muy oscuro
    window_color = (89, 125, 206) # Azul ventana
    
    # Paredes (fila 8-20)
    for y in range(8, 21):
        for x in range(2, 22):
            pixels[x, y] = (*wall_color, 255)
    
    # Techo (triángulo)
    for y in range(2, 9):
        margin = y - 2
        for x in range(margin, size - margin):
            pixels[x, y] = (*roof_color, 255)
    
    # Puerta
    for y in range(14, 21):
        for x in range(9, 15):
            pixels[x, y] = (*door_color, 255)
    
    # Ventanas
    for y in range(10, 14):
        for x in range(3, 7):
            pixels[x, y] = (*window_color, 255)
        for x in range(17, 21):
            pixels[x, y] = (*window_color, 255)
    
    # Escalar a 96x96
    result = img.resize((96, 96), Image.NEAREST)
    result.save(os.path.join(output_dir, 'caseta_basica.png'))
    print("  Created: caseta_basica.png (96x96)")

def create_tileset(output_dir):
    """Crea tileset básico para el mapa (arena, roca, oasis)"""
    os.makedirs(output_dir, exist_ok=True)
    
    tile_size = 32
    
    # Tile de arena
    sand = Image.new('RGBA', (tile_size, tile_size), (210, 170, 100, 255))
    pixels = sand.load()
    import random
    random.seed(42)
    for y in range(tile_size):
        for x in range(tile_size):
            # Variación de color para textura
            var = random.randint(-15, 15)
            r = max(0, min(255, 210 + var))
            g = max(0, min(255, 170 + var))
            b = max(0, min(255, 100 + var//2))
            pixels[x, y] = (r, g, b, 255)
    sand.save(os.path.join(output_dir, 'tile_sand.png'))
    
    # Tile de roca
    rock = Image.new('RGBA', (tile_size, tile_size), (117, 113, 97, 255))
    pixels = rock.load()
    for y in range(tile_size):
        for x in range(tile_size):
            var = random.randint(-20, 20)
            r = max(0, min(255, 117 + var))
            g = max(0, min(255, 113 + var))
            b = max(0, min(255, 97 + var))
            pixels[x, y] = (r, g, b, 255)
    rock.save(os.path.join(output_dir, 'tile_rock.png'))
    
    # Tile de oasis (agua)
    oasis = Image.new('RGBA', (tile_size, tile_size), (48, 100, 160, 255))
    pixels = oasis.load()
    for y in range(tile_size):
        for x in range(tile_size):
            var = random.randint(-10, 10)
            r = max(0, min(255, 48 + var))
            g = max(0, min(255, 100 + var))
            b = max(0, min(255, 160 + var))
            pixels[x, y] = (r, g, b, 255)
    oasis.save(os.path.join(output_dir, 'tile_oasis.png'))
    
    # Tile de piso interior
    floor = Image.new('RGBA', (tile_size, tile_size), (80, 60, 40, 255))
    pixels = floor.load()
    for y in range(tile_size):
        for x in range(tile_size):
            var = random.randint(-10, 10)
            r = max(0, min(255, 80 + var))
            g = max(0, min(255, 60 + var))
            b = max(0, min(255, 40 + var))
            pixels[x, y] = (r, g, b, 255)
    floor.save(os.path.join(output_dir, 'tile_floor.png'))
    
    print("  Created tileset: sand, rock, oasis, floor")

def create_ui_elements(output_dir):
    """Crea elementos básicos de UI pixel art"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Botón normal
    btn_w, btn_h = 160, 40
    btn = Image.new('RGBA', (btn_w, btn_h), (68, 36, 52, 255))
    pixels = btn.load()
    # Borde
    for x in range(btn_w):
        pixels[x, 0] = (210, 170, 100, 255)
        pixels[x, btn_h-1] = (210, 170, 100, 255)
    for y in range(btn_h):
        pixels[0, y] = (210, 170, 100, 255)
        pixels[btn_w-1, y] = (210, 170, 100, 255)
    btn.save(os.path.join(output_dir, 'btn_normal.png'))
    
    # Botón hover
    btn_hover = Image.new('RGBA', (btn_w, btn_h), (100, 60, 80, 255))
    pixels = btn_hover.load()
    for x in range(btn_w):
        pixels[x, 0] = (255, 200, 100, 255)
        pixels[x, btn_h-1] = (255, 200, 100, 255)
    for y in range(btn_h):
        pixels[0, y] = (255, 200, 100, 255)
        pixels[btn_w-1, y] = (255, 200, 100, 255)
    btn_hover.save(os.path.join(output_dir, 'btn_hover.png'))
    
    # Icono de moneda (especia)
    coin = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    pixels = coin.load()
    gold = (255, 200, 0)
    for y in range(3, 13):
        for x in range(3, 13):
            if (x-7.5)**2 + (y-7.5)**2 <= 25:
                pixels[x, y] = (*gold, 255)
    coin.save(os.path.join(output_dir, 'icon_coin.png'))
    
    # Panel de inventario (slot)
    slot = Image.new('RGBA', (48, 48), (40, 30, 20, 200))
    pixels = slot.load()
    border = (133, 76, 48)
    for x in range(48):
        pixels[x, 0] = (*border, 255)
        pixels[x, 47] = (*border, 255)
    for y in range(48):
        pixels[0, y] = (*border, 255)
        pixels[47, y] = (*border, 255)
    slot.save(os.path.join(output_dir, 'inv_slot.png'))
    
    print("  Created UI elements: buttons, coin, inventory slot")

if __name__ == '__main__':
    BASE = '/home/ubuntu/dunita_game'
    
    print("=== PIXEL ART PROCESSOR ===\n")
    
    print("1. Processing creature sprites...")
    process_creature_sprites(
        f'{BASE}/assets/sprites/creatures',
        f'{BASE}/assets/sprites/creatures_8bit',
        size=(64, 64)
    )
    
    print("\n2. Processing building sprites...")
    process_building_sprites(
        f'{BASE}/assets/sprites/buildings',
        f'{BASE}/assets/sprites/buildings_8bit',
        size=(96, 96)
    )
    
    print("\n3. Creating player sprite...")
    create_player_sprite(f'{BASE}/assets/sprites/ui')
    
    print("\n4. Creating caseta básica sprite...")
    create_caseta_sprite(f'{BASE}/assets/sprites/buildings_8bit')
    
    print("\n5. Creating tileset...")
    create_tileset(f'{BASE}/assets/sprites/tiles')
    
    print("\n6. Creating UI elements...")
    create_ui_elements(f'{BASE}/assets/sprites/ui')
    
    print("\n=== DONE ===")
