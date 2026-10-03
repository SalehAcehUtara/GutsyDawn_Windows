import os
import sys
import threading
from accessible_output2 import outputs

class TTSManager:
    def __init__(self):
        self.speaker = outputs.auto.Auto()
        from .app_paths import get_base_dir; self.spool_path = os.path.join(get_base_dir(), "spool.log")
        
    def _speak_thread(self, text, interrupt):
        # 1. Output ke pembaca layar (NVDA/JAWS)
        try:
            self.speaker.output(text, interrupt)
        except:
            pass
            
        # 2. Tulis ke spool.log
        try:
            with open(self.spool_path, "a", encoding="utf-8") as f:
                f.write(text + "\n")
        except:
            pass
            
    def speak(self, text, interrupt=True):
        # Lempar semua beban (NVDA RPC & Disk I/O) ke background thread
        # agar wxPython UI Thread tidak pernah Not Responding meski di-spam
        threading.Thread(target=self._speak_thread, args=(text, interrupt), daemon=True).start()
