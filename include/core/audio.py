import pygame
import os
from .app_paths import get_sounds_dir

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.sound_dir = get_sounds_dir()
        self.bgm_keys = ["gd_logo.ogg", "menumus8.ogg", "birds20.ogg"] # File yg dianggap sebagai BGM
        self.bgm_volume = 0.5
        self.sfx_volume = 1.0
        
    def _load(self, filename):
        if filename not in self.sounds:
            filepath = os.path.join(self.sound_dir, filename)
            if os.path.exists(filepath):
                self.sounds[filename] = pygame.mixer.Sound(filepath)
            else:
                return False
        return True
        
    def play(self, filename, volume=None):
        if self._load(filename):
            if volume is None:
                vol = self.bgm_volume if filename in self.bgm_keys else self.sfx_volume
            else:
                vol = volume
            self.sounds[filename].set_volume(vol)
            self.sounds[filename].play()
            
    def play_loop(self, filename, volume=None):
        if self._load(filename):
            if volume is None:
                vol = self.bgm_volume if filename in self.bgm_keys else self.sfx_volume
            else:
                vol = volume
            self.sounds[filename].set_volume(vol)
            self.sounds[filename].play(loops=-1)
            
    def set_volume(self, filename, volume):
        if filename in self.sounds:
            self.sounds[filename].set_volume(volume)
            
    def update_bgm_volume(self, new_volume):
        self.bgm_volume = new_volume
        for bgm in self.bgm_keys:
            if bgm in self.sounds:
                self.sounds[bgm].set_volume(new_volume)
                
    def update_sfx_volume(self, new_volume):
        self.sfx_volume = new_volume
        for name, sound in self.sounds.items():
            if name not in self.bgm_keys and not name.startswith("amb_"):
                sound.set_volume(new_volume)
            
    def stop_all(self):
        for sound in self.sounds.values():
            sound.stop()

    def stop(self, filename):
        if filename in self.sounds:
            self.sounds[filename].stop()


