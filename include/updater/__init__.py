from .client_updater import ClientUpdater
from .sound_updater import SoundUpdater

class UpdaterManager:
    def __init__(self, app_manager):
        self.client = ClientUpdater(app_manager)
        self.sound = SoundUpdater(app_manager)
