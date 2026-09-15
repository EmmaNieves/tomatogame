import os
import pygame
import settings


class AudioManager:
    """
    Maneja musica y efectos. Si el mixer falla o falta
    un archivo, el juego sigue funcionando sin sonido.
    Coloca tus archivos en assets/audio/music y assets/audio/sfx.
    """

    def __init__(self):
        self.enabled = True
        self.current_music = None
        try:
            pygame.mixer.init()
        except pygame.error:
            self.enabled = False

    def play_music(self, filename, loop=-1, volume=0.5, force=False):
        if not self.enabled:
            return
        if not force and self.current_music == filename and pygame.mixer.music.get_busy():
            return
        path = os.path.join(settings.AUDIO_DIR, "music", filename)
        if os.path.isfile(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loop)
                self.current_music = filename
            except pygame.error:
                pass

    def play_sfx(self, filename, assets, volume=0.7):
        if not self.enabled:
            return
        path = os.path.join(settings.AUDIO_DIR, "sfx", filename)
        sound = assets.load_sound(path)
        if sound:
            sound.set_volume(volume)
            sound.play()
