# ANAK (UI/TTS Bridge)
# Bertugas menyampaikan pesan ke pemain (membacakan pakai NVDA) secara aman tanpa tabrakan.
import queue

class AnakPenyampai:
    def __init__(self):
        # Antrian pesan masuk agar dibacakan berurutan dan tidak putus-putus
        self.antrian_pesan = queue.Queue()
        
    def sampaikan_ke_pemain(self, teks, saluran="LOKAL"):
        self.antrian_pesan.put((teks, saluran))
