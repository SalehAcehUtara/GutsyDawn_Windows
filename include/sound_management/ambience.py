import os
import pygame
try:
    from core.app_paths import get_sounds_dir
except ImportError:
    from include.core.app_paths import get_sounds_dir

class AmbienceManager:
    def __init__(self, app_manager):
        self.app = app_manager
        self.current_ambient = None
        self.sound_dir = get_sounds_dir()
        self.sounds = {}
        self.channel = None
        self._init_channel()

    def _init_channel(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            # Channel 1 khusus ambient sound berulang (looping)
            self.channel = pygame.mixer.Channel(1)
        except Exception as e:
            logging.error(f"Gagal init channel ambient: {e}")
            self.channel = None

    def _load(self, filename):
        if filename not in self.sounds:
            filepath = os.path.join(self.sound_dir, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[filename] = pygame.mixer.Sound(filepath)
                except Exception as e:
                    logging.error(f"Gagal memuat sound ambient {filename}: {e}")
                    return False
            else:
                return False
        return True

    def play(self, filename):
        if not filename:
            return
            
        if filename == self.current_ambient and self.channel and self.channel.get_busy():
            return
            
        self.current_ambient = filename
        vol = getattr(self.app.player, 'ambient_volume', 1.0)
        
        if self._load(filename):
            try:
                snd = self.sounds[filename]
                snd.set_volume(vol)
                if not self.channel:
                    self._init_channel()
                if self.channel:
                    self.channel.stop()
                    self.channel.set_volume(vol)
                    self.channel.play(snd, loops=-1)
                else:
                    snd.play(loops=-1)
            except Exception as e:
                logging.error(f"Error memutar ambient {filename}: {e}")

    def set_volume(self, volume):
        if self.channel:
            try:
                self.channel.set_volume(volume)
            except:
                pass
        if self.current_ambient and self.current_ambient in self.sounds:
            try:
                self.sounds[self.current_ambient].set_volume(volume)
            except:
                pass

    def stop(self):
        if self.channel:
            try:
                self.channel.stop()
            except:
                pass
        self.current_ambient = None
