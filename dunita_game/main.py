"""
DUNE DOMINION - Punto de Entrada Principal
Videojuego 2D de gestión de criaturas en el universo de Dune
"""
import sys
import os

# Asegurar que el directorio del juego está en el path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Configurar variable de entorno para display headless si es necesario (solo para entornos sin GUI)
# En Windows, Pygame debería detectar el driver automáticamente.
# if 'DISPLAY' not in os.environ and sys.platform != 'win32' and sys.platform != 'darwin':
#     os.environ.setdefault('SDL_VIDEODRIVER', 'x11')
#     os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import pygame

from src.engine import Engine
from src.config import GameState


def main():
    """Función principal del juego"""
    # Crear motor
    engine = Engine()
    
    # Registrar estados
    from src.states.main_menu import MainMenuState
    from src.states.loading_screen import LoadingScreenState
    from src.states.gameplay import GameplayState
    
    engine.register_state(GameState.MAIN_MENU, MainMenuState)
    engine.register_state(GameState.LOADING, LoadingScreenState)
    engine.register_state(GameState.GAMEPLAY, GameplayState)
    
    # Ejecutar
    engine.run()


if __name__ == '__main__':
    main()
