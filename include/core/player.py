import os
import json
from .app_paths import get_app_data_dir

class PlayerData:
    def __init__(self):
        self.username = ""
        self.token = ""
        self.role = "player"
        self.current_map = "Dunia Luar"
        self.bgm_volume = 0.5
        self.ambient_volume = 1.0
        self.sfx_volume = 1.0
        self.voice_volume = 1.0
        self.saved_accounts = []
        
        self.profile_path = os.path.join(get_app_data_dir(), "profile.json")
        self.load_profile()
        
    def load_profile(self):
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.username = data.get("username", "")
                    self.token = data.get("token", "")
                    self.bgm_volume = data.get("bgm_volume", 0.5)
                    self.ambient_volume = data.get("ambient_volume", 1.0)
                    self.sfx_volume = data.get("sfx_volume", 1.0)
                    self.voice_volume = data.get("voice_volume", 1.0)
                    self.saved_accounts = data.get("saved_accounts", [])
                    if self.username and self.token:
                        self.add_saved_account(self.username, self.token)
            except:
                pass
                
    def add_saved_account(self, username, token):
        if not hasattr(self, 'saved_accounts'):
            self.saved_accounts = []
        self.saved_accounts = [acc for acc in self.saved_accounts if acc['username'] != username]
        self.saved_accounts.insert(0, {'username': username, 'token': token})
        
    def save_profile(self):
        try:
            if self.username and self.token:
                self.add_saved_account(self.username, self.token)
            data = {
                "username": self.username,
                "token": self.token,
                "bgm_volume": self.bgm_volume,
                "ambient_volume": self.ambient_volume,
                "sfx_volume": self.sfx_volume,
                "voice_volume": self.voice_volume,
                "saved_accounts": getattr(self, 'saved_accounts', [])
            }
            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except:
            pass

    def clear_saved_accounts(self):
        self.saved_accounts = []
        self.save_profile()
