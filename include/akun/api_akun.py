import wx
import requests
import uuid

class AkunAPIClient:
    def __init__(self, manager):
        self.manager = manager
        self.base_url = "https://gd-project.nyamancenter1804.workers.dev"
        self.session = requests.Session()

    def register(self, playername, gender, email, password, reason):
        self.manager.tts.speak("Sedang mengirim data pendaftaran...")
        try:
            laptop_id = str(uuid.getnode())
            payload = {
                "playername": playername,
                "gender": gender,
                "email": email,
                "password": password,
                "reason": reason,
                "laptop_id": laptop_id
            }
            headers = {"Content-Type": "application/json"}
            
            try:
                response = self.session.post(f"{self.base_url}/api/register", json=payload, headers=headers, timeout=10)
            except requests.exceptions.ConnectionError:
                response = self.session.post(f"{self.base_url}/api/register", json=payload, headers=headers, timeout=10)
                
            try:
                data = response.json()
            except ValueError:
                data = {}
            if data.get("status") == "requires_otp":
                wx.CallAfter(self.manager.akun_ui.show_otp_dialog, email)
            elif response.status_code == 200 or response.status_code == 201:
                self.manager.tts.speak(data.get("message", "Akun berhasil didaftarkan!"))
                self.manager.menus.show_main_menu()
            else:
                self.manager.tts.speak(data.get("error", "Gagal mendaftar akun."))
                self.manager.menus.show_main_menu()
        except Exception as e:
            self.manager.tts.speak("Terjadi kesalahan jaringan.")
            self.manager.menus.show_main_menu()

    def verify_otp(self, email, otp_code):
        self.manager.tts.speak("Sedang memverifikasi kode...")
        try:
            payload = {"email": email, "otp": otp_code}
            headers = {"Content-Type": "application/json"}
            
            try:
                response = self.session.post(f"{self.base_url}/api/verify_otp", json=payload, headers=headers, timeout=10)
            except requests.exceptions.ConnectionError:
                response = self.session.post(f"{self.base_url}/api/verify_otp", json=payload, headers=headers, timeout=10)
                
            data = response.json()
            if response.status_code == 200:
                self.manager.tts.speak(data.get("message", "Akun berhasil diverifikasi dan langsung aktif!"))
                self.manager.menus.show_main_menu()
            else:
                self.manager.tts.speak(data.get("error", "Kode OTP salah atau kedaluwarsa."))
                self.manager.akun_ui.show_otp_dialog(email)
        except Exception as e:
            self.manager.tts.speak("Terjadi kesalahan jaringan saat verifikasi OTP.")
            self.manager.menus.show_main_menu()

    def login(self, email, password):
        self.manager.tts.speak("Sedang memverifikasi akun ke server...")
        try:
            payload = {"email": email, "password": password}
            headers = {"Content-Type": "application/json"}
            
            try:
                response = self.session.post(f"{self.base_url}/api/login", json=payload, headers=headers, timeout=10)
            except requests.exceptions.ConnectionError:
                response = self.session.post(f"{self.base_url}/api/login", json=payload, headers=headers, timeout=10)
                
            try:
                data = response.json()
            except ValueError:
                data = {}
            if data.get("status") == "requires_otp":
                wx.CallAfter(self.manager.akun_ui.show_otp_dialog, email)
            elif response.status_code == 200:
                if data.get("error"):
                    self.manager.tts.speak(data["error"])
                    self.manager.menus.show_main_menu()
                else:
                    self.manager.player.username = data.get("data", {}).get("playername", "")
                    self.manager.player.token = data.get("data", {}).get("token", "")
                    self.manager.player.role = data.get("data", {}).get("role", "player")
                    self.manager.player.is_logged_in = True
                    self.manager.player.save_profile()
                    
                    if hasattr(self.manager, 'chat'):
                        self.manager.chat.sambungkan()
                        self.manager.chat.update_role(self.manager.player.role)
                    if data.get("ambient_sound") and hasattr(self.manager, 'ambience'):
                        self.manager.ambience.play(data["ambient_sound"])
                    
                    self.manager.tts.speak(f"Selamat datang kembali, {self.manager.player.username}!")
                    self.manager.state = 'IN_GAME'
                    
                    wx.CallAfter(self.manager.panel.Hide)
                    wx.CallAfter(self.manager.frame.Layout)
                    wx.CallAfter(self.manager.build_menu_bar)
                    wx.CallAfter(self.manager.frame.SetFocus)
                    
                    self.manager.audio.stop('menumus8.ogg')
                    try:
                        self.manager.game.start()
                    except Exception as e:
                        import logging, traceback
                        logging.error("GAME START ERROR: " + traceback.format_exc())
                        
                    try:
                        self.manager.tt.start(self.manager.player.username)
                    except Exception as e:
                        import logging, traceback
                        logging.error("TEAMTALK START ERROR: " + traceback.format_exc())
                        
                    self.manager.api.send_action("/start")
            else:
                self.manager.tts.speak(data.get("error", "Email atau password salah!"))
                self.manager.menus.show_main_menu()
        except Exception as e:
            self.manager.tts.speak("Terjadi kesalahan jaringan.")
            self.manager.menus.show_main_menu()
            
    def forgot_password(self, email):
        self.manager.tts.speak("Sedang meminta kode reset password...")
        try:
            payload = {"email": email}
            headers = {"Content-Type": "application/json"}
            
            try:
                response = self.session.post(f"{self.base_url}/api/forgot_password", json=payload, headers=headers, timeout=10)
            except requests.exceptions.ConnectionError:
                response = self.session.post(f"{self.base_url}/api/forgot_password", json=payload, headers=headers, timeout=10)
                
            data = response.json()
            if response.status_code == 200:
                self.manager.tts.speak(data.get("message", "Kode reset password telah dikirim ke email Anda."))
                wx.CallAfter(self.manager.akun_ui.show_reset_password_dialog, email)
            else:
                self.manager.tts.speak(data.get("error", "Email tidak ditemukan!"))
                self.manager.menus.show_main_menu()
        except Exception as e:
            self.manager.tts.speak("Terjadi kesalahan jaringan.")
            self.manager.menus.show_main_menu()
            
    def reset_password(self, email, otp, new_password):
        self.manager.tts.speak("Sedang mengubah password...")
        try:
            payload = {"email": email, "otp": otp, "new_password": new_password}
            headers = {"Content-Type": "application/json"}
            
            try:
                response = self.session.post(f"{self.base_url}/api/reset_password", json=payload, headers=headers, timeout=10)
            except requests.exceptions.ConnectionError:
                response = self.session.post(f"{self.base_url}/api/reset_password", json=payload, headers=headers, timeout=10)
                
            data = response.json()
            if response.status_code == 200:
                self.manager.tts.speak(data.get("message", "Password berhasil diubah! Silakan login dengan password baru."))
                wx.CallAfter(self.manager.akun_ui.show_login_form)
            else:
                self.manager.tts.speak(data.get("error", "Kode OTP salah atau kedaluwarsa."))
                wx.CallAfter(self.manager.akun_ui.show_reset_password_dialog, email)
        except Exception as e:
            self.manager.tts.speak("Terjadi kesalahan jaringan.")
            self.manager.menus.show_main_menu()
