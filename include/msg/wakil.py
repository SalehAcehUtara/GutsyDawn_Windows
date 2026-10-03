# WAKIL (Filter & Logic)
# Mengatur nama saluran rahasia dan menyortir pesan yang masuk untuk diserahkan ke Anak.

class WakilLogika:
    def __init__(self, anak):
        self.anak = anak
        self.prefix_rahasia = "GutsyDawn_1804/Chat"
        
        # Saluran saat ini
        self.peta_sekarang = "hutan"
        self.team_id = "0"
        self.role = "player" # Akan diubah oleh ChatManager
        
    def dapatkan_daftar_saluran(self):
        peta_normal = str(self.peta_sekarang).strip().lower()
        saluran = [
            f"{self.prefix_rahasia}/Global",
            f"{self.prefix_rahasia}/Lokal/{peta_normal}",
            f"{self.prefix_rahasia}/Team/{self.team_id}",
            f"{self.prefix_rahasia}/Broadcast"
        ]
        if self.role == "developer":
            saluran.append(f"{self.prefix_rahasia}/Staf")
        return saluran
        
    def proses_pesan_masuk(self, topik, teks):
        # Cek dari saluran mana
        if "/Broadcast" in topik:
            self.anak.sampaikan_ke_pemain(f"{teks}", "BROADCAST")
        elif "/Staf" in topik:
            self.anak.sampaikan_ke_pemain(f"{teks}", "STAF")
        elif "/Global" in topik:
            self.anak.sampaikan_ke_pemain(f"{teks}", "GLOBAL")
        elif "/Lokal/" in topik:
            self.anak.sampaikan_ke_pemain(f"{teks}", "LOKAL")
        elif "/Team/" in topik:
            self.anak.sampaikan_ke_pemain(f"{teks}", "TEAM")
            
    def dapatkan_topik_global(self):
        return f"{self.prefix_rahasia}/Global"
        
    def dapatkan_topik_lokal(self):
        peta_normal = str(self.peta_sekarang).strip().lower()
        return f"{self.prefix_rahasia}/Lokal/{peta_normal}"
        
    def dapatkan_topik_team(self):
        return f"{self.prefix_rahasia}/Team/{self.team_id}"

    def dapatkan_topik_broadcast(self):
        return f"{self.prefix_rahasia}/Broadcast"
        
    def dapatkan_topik_staf(self):
        return f"{self.prefix_rahasia}/Staf"
