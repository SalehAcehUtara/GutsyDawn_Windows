import requests
import json
import logging

class APIClient:
    def __init__(self, manager):
        self.manager = manager
        self.base_url = "https://gd-project.nyamancenter1804.workers.dev"
        self.session = requests.Session()
        
    
    def verify_token(self):
        self.manager.tts.speak("Sedang memverifikasi token ke server...")
        try:
            payload = {"token": self.manager.player.token}
            headers = {"Content-Type": "application/json"}
            
            try:
                response = self.session.post(f"{self.base_url}/api/verify", json=payload, headers=headers, timeout=10)
            except requests.exceptions.ConnectionError:
                # Retry sekali jika koneksi keep-alive diputus server (WinError 10054)
                response = self.session.post(f"{self.base_url}/api/verify", json=payload, headers=headers, timeout=10)
                
            data = response.json() if response.status_code in [200, 401, 403, 404, 500] else {}
            if data.get("status") == "requires_otp":
                import wx
                wx.CallAfter(self.manager.akun_ui.show_otp_dialog, email)
            elif response.status_code == 200:
                if data.get("error"):
                    self.manager.tts.speak(data["error"])
                    self.manager.menus.show_main_menu()
                else:
                    self.manager.player.username = data.get("playername", data.get("data", {}).get("playername", self.manager.player.username))
                    self.manager.player.role = data.get("role", data.get("data", {}).get("role", self.manager.player.role))
                    if hasattr(self.manager, 'chat'):
                        self.manager.chat.sambungkan()
                        self.manager.chat.update_role(self.manager.player.role)
                    if data.get("ambient_sound") and hasattr(self.manager, 'ambience'):
                        self.manager.ambience.play(data["ambient_sound"])
                    self.manager.state = 'IN_GAME'
                    import wx
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
                        logging.error("TT START ERROR: " + traceback.format_exc())
            else:
                self.manager.tts.speak(f"Gagal memverifikasi akun (Error {response.status_code}).")
                self.manager.menus.show_main_menu()
        except Exception as e:
            import logging, traceback
            logging.error("VERIFY TOKEN ERROR: " + traceback.format_exc())
            self.manager.tts.speak("Gagal menghubungi server.")
            self.manager.menus.show_main_menu()
            
    def send_chat(self, chat_type, message):
        try:
            payload = {
                "token": self.manager.player.token,
                "message": message,
                "type": chat_type,
                "map_name": self.manager.player.current_map
            }
            headers = {"Content-Type": "application/json"}
            import requests
            requests.post(f"{self.base_url}/api/chat", json=payload, headers=headers, timeout=5)
        except:
            pass

    def logout(self):
        try:
            payload = {"token": self.manager.player.token}
            headers = {"Content-Type": "application/json"}
            self.session.post(f"{self.base_url}/api/logout", json=payload, headers=headers, timeout=5)
        except:
            pass

    def send_action(self, action_name):
        self.manager.tts.speak("Memproses...")
        try:
            payload = {
                "token": self.manager.player.token,
                "action": action_name
            }
            headers = {"Content-Type": "application/json"}
            
            try:
                response = self.session.post(f"{self.base_url}/api/aksi", json=payload, headers=headers, timeout=10)
            except requests.exceptions.ConnectionError:
                response = self.session.post(f"{self.base_url}/api/aksi", json=payload, headers=headers, timeout=10)
                
            if response.status_code == 200:
                data = response.json()
                self._handle_server_response(data)
            elif response.status_code == 401:
                self.manager.player.username = ""
                self.manager.player.token = ""
                self.manager.player.save_profile()
                self.manager.tts.speak("Sesi kadaluarsa atau akun telah dihapus. Silakan login kembali.")
                self.manager.menus.show_main_menu()
            else:
                self.manager.tts.speak(f"Error server: {response.status_code}")
        except Exception as e:
            logging.error(f"API Error: {e}")
            self.manager.tts.speak("Gagal menghubungi server.")

    def _handle_server_response(self, data):
        # Selalu update current_map jika disediakan server (agar tombol C / polling sinkron)
        if data.get("current_map"):
            self.manager.player.current_map = data["current_map"]
            if hasattr(self.manager, 'chat'):
                self.manager.chat.update_peta(data["current_map"])
                
        if data.get("ambient_sound"):
            if hasattr(self.manager, 'ambience'):
                self.manager.ambience.play(data["ambient_sound"])
            
        if "error" in data:
            self.manager.tts.speak(data["error"])
            return

        if data.get("fileToSave") and data["fileToSave"].get("filename"):
            file_data = data["fileToSave"]
            try:
                with open(file_data["filename"], "w", encoding="utf-8") as f:
                    f.write(file_data["content"])
                if file_data.get("caption"):
                    self.manager.tts.speak(file_data["caption"])
                else:
                    self.manager.tts.speak(f"File {file_data['filename']} berhasil disimpan.")
            except Exception as e:
                pass

        if data.get("alertText"):
            if data["alertText"] == "TRIGGER_MAP_MAKER":
                self.manager.tts.speak("Memasuki pembuat map.")
            else:
                self.manager.tts.speak(data["alertText"])

        if data.get("success"):
            if data.get("requestInput"):
                self.manager.menus.show_input_dialog(data.get("text", "Masukan Server:"))
            elif data.get("buttons") and len(data["buttons"]) > 0:
                self.manager.menus.show_server_menu(data["text"], data["buttons"])
            else:
                # Tidak ada input dan tidak ada tombol -> Akhir dari dialog menu server
                self.manager.state = 'IN_GAME'
                if data.get("text"):
                    self.manager.tts.speak(data["text"])
                elif not data.get("alertText"):
                    self.manager.tts.speak("Server mengembalikan respon kosong tanpa tombol.")













