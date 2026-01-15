import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.music_file = "musics/theme.mp3" 
        self.sfx_file = "musics/effect.mp3"
        
        self.music_enabled = False
        self.sfx_enabled = False

    def play_bg_music(self):
        if os.path.exists(self.music_file):
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play(-1)
            if not self.music_enabled:
                pygame.mixer.music.pause()
    

    def stop_music(self):
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
        if self.sfx_enabled and os.path.exists(self.sfx_file):
            sound = pygame.mixer.Sound(self.sfx_file)
            sound.play()

    def toggle_sfx(self, state):
        self.sfx_enabled = state