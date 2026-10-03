from .ketua import KetuaMQTT
from .wakil import WakilLogika
from .anak import AnakPenyampai

class ChatManager:
    def __init__(self, app):
        self.app = app
        self.anak = AnakPenyampai()
        self.wakil = WakilLogika(self.anak)
        self.ketua = KetuaMQTT(self.wakil)
        
    def sambungkan(self):
        self.wakil.role = getattr(self.app.player, 'role', 'player')
        self.wakil.peta_sekarang = getattr(self.app.player, 'current_map', 'hutan')
        self.ketua.sambungkan()
        
    def putuskan(self):
        self.ketua.putuskan()

    def update_role(self, role):
        if self.wakil.role != role:
            self.wakil.role = role
            self.ketua.langganan_ulang()
        
    def kirim_global(self, teks):
        self.ketua.kirim_pesan(self.wakil.dapatkan_topik_global(), teks)
        
    def kirim_lokal(self, teks):
        self.ketua.kirim_pesan(self.wakil.dapatkan_topik_lokal(), teks)
        
    def kirim_team(self, teks):
        if self.wakil.team_id != "0":
            self.ketua.kirim_pesan(self.wakil.dapatkan_topik_team(), teks)
            
    def kirim_broadcast(self, teks):
        self.ketua.kirim_pesan(self.wakil.dapatkan_topik_broadcast(), teks)
        
    def kirim_staf(self, teks):
        self.ketua.kirim_pesan(self.wakil.dapatkan_topik_staf(), teks)
            
    def update_peta(self, nama_peta):
        nama_peta_normal = str(nama_peta).strip().lower()
        if self.wakil.peta_sekarang != nama_peta_normal:
            if self.ketua.is_connected:
                try:
                    self.ketua.client.unsubscribe(self.wakil.dapatkan_topik_lokal())
                except:
                    pass
                
            self.wakil.peta_sekarang = nama_peta_normal
            
            if self.ketua.is_connected:
                try:
                    self.ketua.client.subscribe(self.wakil.dapatkan_topik_lokal())
                except:
                    pass
                
    def proses_antrean(self):
        # Membaca semua pesan masuk dan memainkan suara + TTS
        while not self.anak.antrian_pesan.empty():
            pesan, saluran = self.anak.antrian_pesan.get()
            
            # Catat ke history chat pemain
            if hasattr(self.app, 'game') and hasattr(self.app.game, 'chat_history'):
                self.app.game.chat_history.append(f"[{saluran}] {pesan}")
            
            # Putar efek suara yang berbeda sesuai saluran
            if saluran == "GLOBAL":
                self.app.audio.play("pesan_global.ogg")
            elif saluran == "LOKAL":
                self.app.audio.play("pesan_lokal.ogg")
            elif saluran == "TEAM":
                self.app.audio.play("pesan_lokal.ogg")
            elif saluran == "BROADCAST":
                self.app.audio.play("notif_developer.ogg")
            elif saluran == "STAF":
                self.app.audio.play("staf_msg.ogg")
                
            # Bacakan pesannya
            self.app.tts.speak(pesan)
