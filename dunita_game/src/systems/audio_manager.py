"""
Audio Manager - Gestión de música y efectos de sonido
Reproduce pistas en loop continuo dependiendo del estado del juego
"""
import pygame
import os
import math
from src.config import (
    MUSIC_DIR, DEFAULT_MASTER_VOL, DEFAULT_BGM_VOL, DEFAULT_SFX_VOL,
    GameState
)


class AudioManager:
    """
    Gestor de audio con soporte para:
    - BGM (Background Music) por estado del juego
    - SFX (Sound Effects)
    - Sliders independientes: Master, BGM, SFX
    - Generación procedural de música chiptune si no hay archivos
    """

    # Mapeo de estado → nombre de archivo de música
    _STATE_MUSIC_FILES = {
        GameState.MAIN_MENU:     ['Musica_menu.mp3', 'menu.ogg', 'menu.mp3', 'menu.wav'],
        GameState.LOADING:       ['Musica_partida.mp3', 'loading.ogg', 'loading.mp3', 'loading.wav'],
        GameState.GAMEPLAY:      ['Iron_Beneath_the_Sands.mp3', 'game.ogg', 'game.mp3', 'game.wav'],
        GameState.CREDITS:       ['Musica_creditos.mp3', 'credits.ogg', 'credits.mp3', 'credits.wav'],
        GameState.SETTINGS:      ['Musica_menu.mp3', 'menu.ogg', 'menu.mp3', 'menu.wav'],
        GameState.ACCESSIBILITY: ['Musica_menu.mp3', 'menu.ogg', 'menu.mp3', 'menu.wav'],
    }

    def __init__(self):
        self._master_vol = DEFAULT_MASTER_VOL
        self._bgm_vol = DEFAULT_BGM_VOL
        self._sfx_vol = DEFAULT_SFX_VOL
        self._current_track = None
        self._current_state = None
        self._sounds = {}
        self._initialized = False
        self._bgm_tracks = {}
        self._use_generated = False

        # Intentar inicializar mixer
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._initialized = True
            self._load_or_generate_music()
        except Exception as e:
            print(f"Audio init warning: {e}")

    def _generate_beep_sound(self, frequency: float, duration_ms: int,
                              volume: float = 0.3, wave_type: str = 'square') -> pygame.mixer.Sound:
        """Genera un sonido sintético tipo chiptune"""
        import array
        sample_rate = 44100
        num_samples = int(sample_rate * duration_ms / 1000)

        buf = array.array('h', [0] * num_samples)

        for i in range(num_samples):
            t = i / sample_rate
            if wave_type == 'square':
                val = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
            elif wave_type == 'triangle':
                val = 2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.5))) - 1
            else:  # sine
                val = math.sin(2 * math.pi * frequency * t)

            buf[i] = int(val * 32767 * volume)

        sound = pygame.mixer.Sound(buffer=buf)
        return sound

    def _load_or_generate_music(self):
        """Carga archivos de música reales o genera música procedural chiptune como fallback"""
        loaded_any = False
        for state, filenames in self._STATE_MUSIC_FILES.items():
            for filename in filenames:
                path = os.path.join(MUSIC_DIR, filename)
                if os.path.exists(path):
                    self._bgm_tracks[state] = path
                    loaded_any = True
                    break

        if not loaded_any:
            # Generar música procedural chiptune como fallback
            self._use_generated = True
            self._generate_chiptune_tracks()

    def _generate_chiptune_tracks(self):
        """Genera pistas chiptune procedurales para cada estado"""
        if not self._initialized:
            return

        try:
            import array
            import math

            sample_rate = 44100

            def make_note(freq, dur_ms, vol=0.2, wave='square'):
                n = int(sample_rate * dur_ms / 1000)
                buf = array.array('h', [0] * n)
                for i in range(n):
                    t = i / sample_rate
                    # Envelope: attack/decay
                    env = min(1.0, i / (n * 0.1)) * max(0.0, 1.0 - i / (n * 0.9))
                    if wave == 'square':
                        v = 1 if math.sin(2 * math.pi * freq * t) > 0 else -1
                    elif wave == 'triangle':
                        v = 2 * abs(2 * (t * freq - math.floor(t * freq + 0.5))) - 1
                    else:
                        v = math.sin(2 * math.pi * freq * t)
                    buf[i] = int(v * env * 32767 * vol)
                return buf

            # Melodía menú: escala pentatónica desierto
            menu_notes = [220, 261, 293, 349, 392, 440, 392, 349, 293, 261]
            menu_buf = array.array('h', [])
            for freq in menu_notes:
                menu_buf.extend(make_note(freq, 300, 0.15, 'triangle'))
                menu_buf.extend(make_note(0, 50))  # silencio

            # Melodía gameplay: más dinámica
            game_notes = [330, 392, 440, 523, 440, 392, 330, 294, 330, 392]
            game_buf = array.array('h', [])
            for freq in game_notes:
                game_buf.extend(make_note(freq, 200, 0.12, 'square'))
                game_buf.extend(make_note(0, 30))

            # Loading: notas ascendentes
            load_notes = [220, 247, 277, 294, 330, 370, 415, 440]
            load_buf = array.array('h', [])
            for freq in load_notes:
                load_buf.extend(make_note(freq, 400, 0.1, 'triangle'))

            # Créditos: melodía suave
            credits_notes = [261, 293, 329, 349, 392, 349, 329, 293]
            credits_buf = array.array('h', [])
            for freq in credits_notes:
                credits_buf.extend(make_note(freq, 350, 0.12, 'triangle'))
                credits_buf.extend(make_note(0, 60))

            self._bgm_buffers = {
                GameState.MAIN_MENU:     menu_buf,
                GameState.GAMEPLAY:      game_buf,
                GameState.LOADING:       load_buf,
                GameState.CREDITS:       credits_buf,
                GameState.SETTINGS:      menu_buf,
                GameState.ACCESSIBILITY: menu_buf,
            }

        except Exception as e:
            print(f"Chiptune generation warning: {e}")

    def play_bgm(self, state: str):
        """Reproduce BGM para el estado dado. Si ya suena la misma pista, no la reinicia."""
        if not self._initialized:
            return

        # Determinar qué pista corresponde a este estado
        new_track = self._bgm_tracks.get(state)

        # Si usamos archivos reales: no reiniciar si ya suena la misma pista
        if not self._use_generated:
            if new_track is not None and new_track == self._current_track:
                return  # Ya suena la pista correcta
        else:
            # Música generada: comparar por estado
            if state == self._current_state:
                return

        self._current_state = state
        self._current_track = new_track

        try:
            if self._use_generated:
                # Música generada: usar canal dedicado
                pygame.mixer.stop()
                if hasattr(self, '_bgm_buffers') and state in self._bgm_buffers:
                    sound = pygame.mixer.Sound(buffer=self._bgm_buffers[state])
                    sound.set_volume(self._master_vol * self._bgm_vol)
                    channel = pygame.mixer.Channel(0)
                    channel.play(sound, loops=-1)
            else:
                # Música de archivo
                if new_track is not None:
                    pygame.mixer.music.load(new_track)
                    pygame.mixer.music.set_volume(self._master_vol * self._bgm_vol)
                    pygame.mixer.music.play(-1)  # loop infinito
                else:
                    # No hay pista para este estado: detener música
                    pygame.mixer.music.stop()
        except Exception as e:
            print(f"BGM play warning: {e}")

    def stop_bgm(self):
        """Detiene la música de fondo"""
        if not self._initialized:
            return
        try:
            if self._use_generated:
                pygame.mixer.Channel(0).stop()
            else:
                pygame.mixer.music.stop()
            self._current_state = None
            self._current_track = None
        except Exception:
            pass

    def play_sfx(self, sfx_name: str):
        """Reproduce un efecto de sonido"""
        if not self._initialized:
            return
        try:
            if sfx_name in self._sounds:
                self._sounds[sfx_name].set_volume(self._master_vol * self._sfx_vol)
                self._sounds[sfx_name].play()
            else:
                # Generar SFX básico
                self._play_generated_sfx(sfx_name)
        except Exception:
            pass

    def _play_generated_sfx(self, sfx_name: str):
        """Genera y reproduce SFX básico"""
        import array
        import math

        sfx_params = {
            'click':    (440, 50,  0.1, 'square'),
            'hover':    (330, 30,  0.05, 'triangle'),
            'buy':      (523, 100, 0.15, 'triangle'),
            'error':    (110, 150, 0.2, 'square'),
            'success':  (660, 200, 0.15, 'triangle'),
            'turn':     (220, 300, 0.1, 'square'),
            'place':    (392, 150, 0.12, 'triangle'),
        }

        params = sfx_params.get(sfx_name, (440, 50, 0.1, 'square'))
        freq, dur, vol, wave = params

        sample_rate = 44100
        n = int(sample_rate * dur / 1000)
        buf = array.array('h', [0] * n)

        for i in range(n):
            t = i / sample_rate
            env = max(0.0, 1.0 - i / n)
            if wave == 'square':
                v = 1 if math.sin(2 * math.pi * freq * t) > 0 else -1
            else:
                v = 2 * abs(2 * (t * freq - math.floor(t * freq + 0.5))) - 1
            buf[i] = int(v * env * 32767 * vol)

        try:
            sound = pygame.mixer.Sound(buffer=buf)
            sound.set_volume(self._master_vol * self._sfx_vol)
            sound.play()
        except Exception:
            pass

    def set_master_vol(self, vol: float):
        """Ajusta volumen master (0.0 - 1.0)"""
        self._master_vol = max(0.0, min(1.0, vol))
        self._update_volumes()

    def set_bgm_vol(self, vol: float):
        """Ajusta volumen BGM (0.0 - 1.0)"""
        self._bgm_vol = max(0.0, min(1.0, vol))
        self._update_volumes()

    def set_sfx_vol(self, vol: float):
        """Ajusta volumen SFX (0.0 - 1.0)"""
        self._sfx_vol = max(0.0, min(1.0, vol))

    def _update_volumes(self):
        """Actualiza volúmenes en tiempo real"""
        if not self._initialized:
            return
        try:
            if not self._use_generated:
                pygame.mixer.music.set_volume(self._master_vol * self._bgm_vol)
            else:
                # Actualizar canal generado si está activo
                ch = pygame.mixer.Channel(0)
                if ch.get_busy():
                    # No se puede cambiar el volumen del canal directamente en pygame
                    # sin recargar el sonido; se aplica en la próxima reproducción
                    pass
        except Exception:
            pass

    @property
    def master_vol(self): return self._master_vol
    @property
    def bgm_vol(self): return self._bgm_vol
    @property
    def sfx_vol(self): return self._sfx_vol


# Instancia global
audio = AudioManager()
