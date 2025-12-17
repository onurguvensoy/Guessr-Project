import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        # Dosya isimlerini buraya yaz (assets klasöründe olduklarını varsayıyorum)
        self.music_file = "musics/theme.mp3" 
        self.sfx_file = "musics/effect.mp3"
        
        self.music_enabled = True
        self.sfx_enabled = True

    def play_bg_music(self):
        """Müziği sonsuz döngüde başlatır."""
        if os.path.exists(self.music_file):
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play(-1) # -1 sonsuz döngü demektir
            if not self.music_enabled:
                pygame.mixer.music.pause()
    

    def stop_music(self): # Bu metodun varlığından emin olalım
        pygame.mixer.music.stop()

        
    def toggle_music(self, state):
        self.music_enabled = state
        if state:
            pygame.mixer.music.unpause()
            if not pygame.mixer.music.get_busy():
                self.play_bg_music()
        else:
            pygame.mixer.music.pause()

    def play_click_sfx(self):
        """Buton sesi."""
        if self.sfx_enabled and os.path.exists(self.sfx_file):
            sound = pygame.mixer.Sound(self.sfx_file)
            sound.play()

    def toggle_sfx(self, state):
        self.sfx_enabled = state