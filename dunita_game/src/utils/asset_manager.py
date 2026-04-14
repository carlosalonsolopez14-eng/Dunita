"""
Asset Manager - Gestión centralizada de recursos gráficos y de audio
"""
import pygame
import os
import sys
from src.config import (
    CREATURES_DIR, BUILDINGS_DIR, TILES_DIR, UI_DIR,
    FONT_SIZES, Colors
)


class AssetManager:
    """Gestor centralizado de assets del juego"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._sprites = {}
        self._fonts = {}
        self._sounds = {}
        self._font_scale = 1.0
        self._initialized = True

    def load_all(self):
        """Carga todos los assets del juego"""
        self._load_fonts(self._font_scale)
        self._load_creature_sprites()
        self._load_building_sprites()
        self._load_tile_sprites()
        self._load_ui_sprites()

    def _load_fonts(self, scale: float = 1.0):
        """Carga fuentes pixel art con escala aplicada"""
        font_candidates = [
            'freemono', 'courier', 'couriernew', 'monospace',
            'dejavusansmono', 'liberationmono'
        ]

        for size_name, base_size in FONT_SIZES.items():
            scaled_size = max(8, int(base_size * scale))
            loaded = False
            for font_name in font_candidates:
                try:
                    font = pygame.font.SysFont(font_name, scaled_size, bold=True)
                    self._fonts[size_name] = font
                    loaded = True
                    break
                except Exception:
                    continue
            if not loaded:
                self._fonts[size_name] = pygame.font.Font(None, scaled_size)

    def reload_fonts(self, scale: float = 1.0):
        """Recarga todas las fuentes con la nueva escala"""
        self._font_scale = scale
        self._load_fonts(scale)

    def _load_creature_sprites(self):
        """Carga sprites de criaturas"""
        if not os.path.exists(CREATURES_DIR):
            return
        for filename in os.listdir(CREATURES_DIR):
            if filename.endswith('.png'):
                key = f"creature_{filename[:-4]}"
                path = os.path.join(CREATURES_DIR, filename)
                try:
                    surf = pygame.image.load(path).convert_alpha()
                    self._sprites[key] = surf
                except Exception as e:
                    print(f"Warning: Could not load {path}: {e}")

    def _load_building_sprites(self):
        """Carga sprites de edificios"""
        if not os.path.exists(BUILDINGS_DIR):
            return
        for filename in os.listdir(BUILDINGS_DIR):
            if filename.endswith('.png'):
                key = f"building_{filename[:-4]}"
                path = os.path.join(BUILDINGS_DIR, filename)
                try:
                    surf = pygame.image.load(path).convert_alpha()
                    self._sprites[key] = surf
                except Exception as e:
                    print(f"Warning: Could not load {path}: {e}")

    def _load_tile_sprites(self):
        """Carga tiles del mapa"""
        if not os.path.exists(TILES_DIR):
            return
        for filename in os.listdir(TILES_DIR):
            if filename.endswith('.png'):
                key = f"tile_{filename[:-4].replace('tile_', '')}"
                path = os.path.join(TILES_DIR, filename)
                try:
                    surf = pygame.image.load(path).convert()
                    self._sprites[key] = surf
                except Exception as e:
                    print(f"Warning: Could not load {path}: {e}")

    def _load_ui_sprites(self):
        """Carga elementos de UI"""
        if not os.path.exists(UI_DIR):
            return
        for filename in os.listdir(UI_DIR):
            if filename.endswith('.png'):
                key = f"ui_{filename[:-4]}"
                path = os.path.join(UI_DIR, filename)
                try:
                    surf = pygame.image.load(path).convert_alpha()
                    self._sprites[key] = surf
                except Exception as e:
                    print(f"Warning: Could not load {path}: {e}")

    def get_sprite(self, key: str) -> pygame.Surface:
        """Obtiene un sprite por clave, retorna placeholder si no existe"""
        if key in self._sprites:
            return self._sprites[key]
        # Crear sprite placeholder
        surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        surf.fill((255, 0, 255, 180))  # Magenta = asset faltante
        return surf

    def get_font(self, size: str = 'medium') -> pygame.font.Font:
        """Obtiene fuente por tamaño"""
        if size in self._fonts:
            return self._fonts[size]
        return pygame.font.Font(None, max(8, int(FONT_SIZES.get(size, 18) * self._font_scale)))

    def get_scaled_sprite(self, key: str, width: int, height: int) -> pygame.Surface:
        """Obtiene sprite escalado"""
        sprite = self.get_sprite(key)
        return pygame.transform.scale(sprite, (width, height))

    def create_text_surface(self, text: str, size: str = 'medium',
                            color=None, bold: bool = False) -> pygame.Surface:
        """Crea superficie con texto renderizado"""
        if color is None:
            color = Colors.UI_TEXT
        font = self.get_font(size)
        return font.render(str(text), True, color)

    def apply_colorblind_filter(self, surface: pygame.Surface, mode: str) -> pygame.Surface:
        """
        Aplica filtro de daltonismo a una superficie pygame.
        Utiliza transformación píxel a píxel con las matrices estándar de simulación.
        """
        if mode == 'none':
            return surface

        # Matrices de transformación para daltonismo (filas: R, G, B)
        matrices = {
            'protanopia': [
                [0.567, 0.433, 0.000],
                [0.558, 0.442, 0.000],
                [0.000, 0.242, 0.758],
            ],
            'deuteranopia': [
                [0.625, 0.375, 0.000],
                [0.700, 0.300, 0.000],
                [0.000, 0.300, 0.700],
            ],
            'tritanopia': [
                [0.950, 0.050, 0.000],
                [0.000, 0.433, 0.567],
                [0.000, 0.475, 0.525],
            ],
        }

        if mode not in matrices:
            return surface

        try:
            import numpy as np

            m = matrices[mode]
            # Convertir surface a array numpy (H, W, 4) con canal alpha
            arr = pygame.surfarray.array3d(surface)  # (W, H, 3) RGB
            arr = arr.astype(np.float32) / 255.0

            r = arr[:, :, 0]
            g = arr[:, :, 1]
            b = arr[:, :, 2]

            new_r = np.clip(m[0][0] * r + m[0][1] * g + m[0][2] * b, 0, 1)
            new_g = np.clip(m[1][0] * r + m[1][1] * g + m[1][2] * b, 0, 1)
            new_b = np.clip(m[2][0] * r + m[2][1] * g + m[2][2] * b, 0, 1)

            out = np.stack([new_r, new_g, new_b], axis=2)
            out = (out * 255).astype(np.uint8)

            result = surface.copy()
            pygame.surfarray.blit_array(result, out)
            return result

        except ImportError:
            # Fallback sin numpy: devolver copia sin transformar
            return surface.copy()
        except Exception:
            return surface.copy()


# Instancia global
assets = AssetManager()
