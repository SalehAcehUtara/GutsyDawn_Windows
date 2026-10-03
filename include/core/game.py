import wx
import os
import threading
import time
import requests
import json
import logging
from .app_paths import get_save_path, get_sounds_dir

class GameLogic:
    def __init__(self, manager):
        self.manager = manager
        
        self.last_chat_id = 0
        self.first_chat_fetch = True
        self.polling_active = False
        self.stop_polling = False
        
        self.chat_history = []
        
        # Thread polling akan dibuat di start()
        
    def start(self):
        self.stop_polling = False
        self.first_chat_fetch = True
        self.poll_generation = getattr(self, "poll_generation", 0) + 1
        gen = self.poll_generation
        
        if hasattr(self.manager, 'chat'):
            self.manager.chat.sambungkan()
            self.manager.chat.update_role(getattr(self.manager.player, 'role', 'player'))
        
        def _wrapper():
            self._poll_loop(gen)
        threading.Thread(target=_wrapper, daemon=True).start()
        
    def stop(self):
        self.stop_polling = True
        if hasattr(self.manager, 'ambience'):
            self.manager.ambience.stop()
        if hasattr(self.manager, 'chat'):
            self.manager.chat.putuskan()

    def handle_input(self, keycode, modifiers):
        p = self.manager.player
        
        alt_pressed = (modifiers & wx.MOD_ALT) != 0
        ctrl_pressed = (modifiers & wx.MOD_CONTROL) != 0
        
        if alt_pressed and keycode == ord('S'):
            self.manager.api.send_action("srv_menu")
        elif alt_pressed and keycode == ord('M'):
            wx.CallAfter(self.manager.menus.show_quick_menu)
        elif alt_pressed and keycode == ord('H'):
            if self.chat_history:
                from ui.chat_management import ChatHistoryDialog
                def show_history():
                    dlg = ChatHistoryDialog(self.manager.frame, self.chat_history, self.manager)
                    dlg.ShowModal()
                    dlg.Destroy()
                    self.manager.frame.SetFocus()
                wx.CallAfter(show_history)
            else:
                self.manager.tts.speak("Belum ada histori chat.")
        elif alt_pressed and keycode == ord('P'):
            self.manager.tts.speak("Membuka Peta Perjalanan...")
            self.manager.api.send_action("/perjalanan")
        elif keycode == ord('C'):
            self.manager.tts.speak(f"Lokasi saat ini: {p.current_map}")
            
        elif keycode == ord('\\'):
            wx.CallAfter(self.manager.menus.show_chat_dialog)
            
        elif keycode == wx.WXK_F1:
            wx.CallAfter(self.manager.help.show_help)
            
        elif keycode == wx.WXK_F7:
            def _confirm_staff():
                dlg = wx.MessageDialog(self.manager.frame,
                    "Apakah kau yakin mau menghubungi staf??\nMohon tidak mengirimkan pesan sembarangan, jika anda salah tekan,, silahkan batalkan.",
                    "Hubungi Staf",
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
                )
                if dlg.ShowModal() == wx.ID_YES:
                    dlg.Destroy()
                    self.manager.menus.show_input_dialog("Ketik pesan untuk Staf:", action_override="staf")
                else:
                    dlg.Destroy()
                self.manager.frame.SetFocus()
            wx.CallAfter(_confirm_staff)
            
        # Tombol panah sekarang tidak melakukan pergerakan koordinat 3D lagi saat sedang In Game
        elif keycode in (wx.WXK_UP, wx.WXK_DOWN, wx.WXK_LEFT, wx.WXK_RIGHT):
            pass
        
    def _poll_loop(self, gen):
        import time
        import requests
        import wx
        ping_counter = 0
        while not self.stop_polling and self.poll_generation == gen:
            if self.manager.player.token:
                # 1. Chat Polling
                try:
                    url = f"{self.manager.api.base_url}/api/chat?last_id={self.last_chat_id}&map={self.manager.player.current_map}"
                    res = requests.get(url, timeout=5)
                    if res.status_code == 200:
                        data = res.json()
                        if data:
                            self.last_chat_id = int(data[-1].get('id', self.last_chat_id))
                            if not self.first_chat_fetch:
                                wx.CallAfter(self._process_chat, data)
                        self.first_chat_fetch = False
                except Exception as e:
                    pass
                
                # 2. Ping Polling
                ping_counter += 2
                if ping_counter >= 10:
                    try:
                        ping_url = f"{self.manager.api.base_url}/api/ping"
                        payload = {"token": self.manager.player.token}
                        requests.post(ping_url, json=payload, timeout=5)
                    except:
                        pass
                    ping_counter = 0
                    
            time.sleep(2)
            
    def _process_chat(self, data):
        for msg in data:
            msg_id = int(msg.get("id", 0))
            # Pengecekan last_chat_id sekarang dipindahkan ke dalam loop thread aman
            if True:
                
                ctype = msg.get("chat_type", "global")
                pname = msg.get("playername", "Sistem")
                content = msg.get("message", "")
                
                self.chat_history.append(f"[{ctype}] {pname}: {content}")
                
                if ctype == "restart_trigger":
                    self.manager.tts.speak("Server sedang direstart. Menutup klien.")
                    wx.CallLater(2000, self.manager.frame.Close)
                    return
                elif ctype == "system":
                    if "bergabung" in content:
                        self.manager.audio.play("masuk_server.ogg")
                    else:
                        self.manager.audio.play("keluar_server.ogg")
                    self.manager.tts.speak(f"{pname} {content}")
                elif ctype == "developer":
                    if "Pemain baru" in content:
                        self.manager.audio.play("permintaan_aqun.ogg")
                    else:
                        self.manager.audio.play("staf_msg.ogg")
                    self.manager.tts.speak(f"[Developer] {pname}: {content}")
                elif ctype == "broadcast":
                    self.manager.audio.play("notif_developer.ogg")
                    self.manager.tts.speak(f"Broadcast dari {pname}: {content}")
                elif ctype == "lokal":
                    self.manager.audio.play("pesan_lokal.ogg")
                    self.manager.tts.speak(f"[Lokal] {pname}: {content}")
                else:
                    self.manager.audio.play("pesan_global.ogg")
                    self.manager.tts.speak(f"{pname}: {content}")












