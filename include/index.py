import wx
import pygame
from core.audio import AudioManager
from core.tts import TTSManager
from core.api import APIClient
from voicechat.teamtalk import TeamTalkManager
from ui.menus import MenuManager
from core.game import GameLogic
from core.player import PlayerData
from updater import UpdaterManager
from msg import ChatManager

class AppManager:
    def __init__(self):
        self.tts = TTSManager()
        self.audio = AudioManager()
        self.player = PlayerData()
        self.chat = ChatManager(self)
        
        from sound_management.ambience import AmbienceManager
        self.ambience = AmbienceManager(self)
        
        self.updater = UpdaterManager(self)
        self.tt = TeamTalkManager(self)
        self.api = APIClient(self)
        self.menus = MenuManager(self)
        
        from include.akun.api_akun import AkunAPIClient
        from include.akun.ui_akun import AkunUIManager
        self.akun_api = AkunAPIClient(self)
        self.akun_ui = AkunUIManager(self)
        
        from help.manage import HelpManager
        self.help = HelpManager(self)
        
        self.audio.bgm_volume = self.player.bgm_volume
        self.audio.sfx_volume = getattr(self.player, 'sfx_volume', 1.0)
        
        self.game = GameLogic(self)
        
        self.frame = wx.Frame(None, title='Gutsy Dawn', size=(400, 300))
        
        self.panel = wx.Panel(self.frame)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.motd_list = wx.ListBox(self.panel)
        vbox.Add(self.motd_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        self.panel.SetSizer(vbox)
        
        # Sembunyikan UI saat intro sedang berlangsung atau saat In Game
        self.panel.Hide()
        
        self.frame.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        self.frame.Bind(wx.EVT_CLOSE, self.on_close)
        
        self.state = 'STATE_INTRO'
        self.build_menu_bar()
        self.intro_timer = wx.Timer(self.frame)
        self.frame.Bind(wx.EVT_TIMER, self.on_intro_tick, self.intro_timer)
        
        self.chat_timer = wx.Timer(self.frame)
        self.frame.Bind(wx.EVT_TIMER, lambda evt: self.chat.proses_antrean(), self.chat_timer)
        self.chat_timer.Start(200) # Cek chat setiap 200ms


    def check_auto_updates(self):
        def on_sound_checked():
            self.start_intro()
            
        def on_client_checked():
            self.updater.sound.check_update(auto=True, callback=on_sound_checked)
            
        import sys
        if getattr(sys, 'frozen', False):
            self.updater.client.check_update(auto=True, callback=on_client_checked)
        else:
            on_client_checked()

    def start(self):

        # Ambil versi klien untuk dibacakan        import os, sys
        version = "1.0.0"
        try:
            version = self.updater.client.get_local_version()
        except:
            pass
            
        self.tts.speak(f"Gutsy Dawn versi {version}. Membuka game mohon tunggu.")
        self._cached_motd_lines = []
        self.frame.Show()
        self.check_auto_updates()
        
    def start_intro(self):
        import threading
        def fetch():
            import requests
            try:
                res = requests.get("https://gd-project.nyamancenter1804.workers.dev/api/motd", timeout=5)
                if res.status_code == 200:
                    text = res.json().get("motd", "Selamat datang di Gutsy Dawn!")
                else:
                    text = "Gagal memuat pesan server."
            except Exception as e:
                text = f"Koneksi ke server terputus. ({str(e)})"
            import wx
            def update_list():
                lines = text.split('\n')
                lines.append("")
                lines.append("Tekan tombol Alt untuk membuka menu utama.")
                self._cached_motd_lines = lines
                
                # Mainkan intro setelah MOTD selesai dimuat
                self.audio.play("gd_logo.ogg", volume=self.player.bgm_volume)
                self.intro_timer.Start(100)
                
            wx.CallAfter(update_list)
        threading.Thread(target=fetch, daemon=True).start()

    def on_intro_tick(self, event):
        if self.state != 'STATE_INTRO':
            self.intro_timer.Stop()
            return
            
        if not pygame.mixer.get_busy():
            self.skip_intro()
            
    def skip_intro(self):
        if self.state == 'STATE_INTRO':
            self.intro_timer.Stop()
            self.audio.stop("gd_logo.ogg")
            self.audio.play_loop("menumus8.ogg", volume=self.player.bgm_volume)
            self.state = 'STATE_MENU'
            self.panel.Show()
            if hasattr(self, '_cached_motd_lines') and self._cached_motd_lines:
                self.motd_list.SetItems(self._cached_motd_lines)
            self.motd_list.SetFocus()
            self.frame.Layout()

    def build_menu_bar(self):
        self.menubar = wx.MenuBar()
        
        if self.state != 'IN_GAME':
            # Menu Gutsy Dawn (Akun & Koneksi)
            self.menu_gd = wx.Menu()
            
            self.menu_koneksi = wx.Menu()
            self.mi_koneksi = self.menu_gd.AppendSubMenu(self.menu_koneksi, "Koneksi\tF2")
            
            saved_accs = getattr(self.player, 'saved_accounts', [])
            if not saved_accs and self.player.username and self.player.token:
                saved_accs = [{"username": self.player.username, "token": self.player.token}]
                
            if saved_accs:
                for acc in saved_accs:
                    mi_masuk = self.menu_koneksi.Append(wx.ID_ANY, f"Masuk sebagai {acc['username']}")
                    self.frame.Bind(wx.EVT_MENU, lambda evt, u=acc['username'], t=acc['token']: self.do_token_login(u, t), mi_masuk)
                
                mi_lain = self.menu_koneksi.Append(wx.ID_ANY, "Login ke Akun Lain")
                self.frame.Bind(wx.EVT_MENU, lambda evt: self.akun_ui.show_login_form(), mi_lain)
                
                mi_hapus = self.menu_koneksi.Append(wx.ID_ANY, "Hapus Akun Tersimpan")
                self.frame.Bind(wx.EVT_MENU, lambda evt: self.clear_accounts(), mi_hapus)
            else:
                mi_lain = self.menu_koneksi.Append(wx.ID_ANY, "Login Akun")
                self.frame.Bind(wx.EVT_MENU, lambda evt: self.akun_ui.show_login_form(), mi_lain)
                
            mi_buat = self.menu_gd.Append(wx.ID_ANY, "Buat Akun Baru")
            self.frame.Bind(wx.EVT_MENU, lambda evt: self.akun_ui.show_register_form(), mi_buat)
            
            # Sub-Menu Update
            self.menu_update = wx.Menu()
            self.mi_update = self.menu_gd.AppendSubMenu(self.menu_update, "Pembaruan (Update)")
            
            mi_up_klien = self.menu_update.Append(wx.ID_ANY, "Cek Update Klien")
            self.frame.Bind(wx.EVT_MENU, lambda evt: self.updater.client.check_update(), mi_up_klien)
            
            mi_up_sound = self.menu_update.Append(wx.ID_ANY, "Cek Update Paket Suara")
            self.frame.Bind(wx.EVT_MENU, lambda evt: self.updater.sound.check_update(), mi_up_sound)
            
            self.menu_gd.AppendSeparator()
            mi_vol = self.menu_gd.Append(wx.ID_ANY, "Volume Manager\tAlt+Shift+V")
            self.frame.Bind(wx.EVT_MENU, self.on_open_volume_manager, mi_vol)
            
            mi_help = self.menu_gd.Append(wx.ID_ANY, "Bantuan Game\tF1")
            self.frame.Bind(wx.EVT_MENU, lambda evt: self.help.show_help(), mi_help)
            
            self.menu_gd.AppendSeparator()
            mi_exit = self.menu_gd.Append(wx.ID_EXIT, "Keluar")
            self.frame.Bind(wx.EVT_MENU, self.on_exit, mi_exit)
            
            self.menubar.Append(self.menu_gd, "&Gutsy Dawn")
        else:
            # Menu Voice Chat
            self.menu_vc = wx.Menu()
            self.mi_mic = self.menu_vc.Append(wx.ID_ANY, "Mic: Mati")
            self.frame.Bind(wx.EVT_MENU, self.on_mic_toggle, self.mi_mic)
            
            self.menu_device = wx.Menu()
            self.mi_device_sub = self.menu_vc.AppendSubMenu(self.menu_device, "Device Input")
            
            self.menu_vc.AppendSeparator()
            mi_vol = self.menu_vc.Append(wx.ID_ANY, "Volume Manager\tAlt+Shift+V")
            self.frame.Bind(wx.EVT_MENU, self.on_open_volume_manager, mi_vol)
            
            mi_help = self.menu_vc.Append(wx.ID_ANY, "Bantuan Game\tF1")
            self.frame.Bind(wx.EVT_MENU, lambda evt: self.help.show_help(), mi_help)
            
            self.menubar.Append(self.menu_vc, "&Voice Chat")
            
        self.frame.SetMenuBar(self.menubar)

    def on_mic_toggle(self, event):
        self.tt.toggle_mic()
        if self.tt.mic_active:
            self.mi_mic.SetItemLabel("Mic: Aktif")
        else:
            self.mi_mic.SetItemLabel("Mic: Mati")
            
    def update_audio_devices(self, devices):
        if not hasattr(self, 'menu_device') or not self.menu_device:
            return
        for item in self.menu_device.GetMenuItems():
            self.menu_device.Delete(item)
            
        for d in devices:
            if 'Input' in str(d) or 'Capture' in str(d) or 'Microphone' in str(d):
                mi = self.menu_device.Append(wx.ID_ANY, d.name)
                # Harus dipaksa binding dev_id dengan default parameter agar scope tidak bocor
                self.frame.Bind(wx.EVT_MENU, lambda evt, dev_id=d.id: self.on_device_select(dev_id), mi)

    def on_device_select(self, dev_id):
        if self.tt.tt_instance:
            try:
                self.tt.tt_instance.set_input_device(dev_id)
                self.tts.speak("Input audio diganti.")
            except Exception as e:
                import logging
                logging.error(f"Gagal ganti device: {e}")

    def on_exit(self, event):
        self.frame.Close()

    def on_open_volume_manager(self, event=None):
        from sound_management.volume_manager import VolumeManagerDialog
        self.tts.speak("Volume Manager dibuka")
        dlg = VolumeManagerDialog(self.frame, self)
        dlg.ShowModal()
        dlg.Destroy()

    def on_key_down(self, event):
        keycode = event.GetKeyCode()
        modifiers = event.GetModifiers()
        
        # Tambahan untuk deteksi tombol live debugger (intip)
        mod_str = ""
        if modifiers & wx.MOD_CONTROL: mod_str += "Ctrl+"
        if modifiers & wx.MOD_ALT: mod_str += "Alt+"
        if modifiers & wx.MOD_SHIFT: mod_str += "Shift+"
        
        key_map = {
            wx.WXK_UP: "Up", wx.WXK_DOWN: "Down", wx.WXK_LEFT: "Left", wx.WXK_RIGHT: "Right",
            wx.WXK_RETURN: "Enter", wx.WXK_ESCAPE: "Escape", wx.WXK_SPACE: "Space",
            wx.WXK_BACK: "Backspace", wx.WXK_TAB: "Tab",
            wx.WXK_F1: "F1", wx.WXK_F2: "F2", wx.WXK_F3: "F3", wx.WXK_F4: "F4",
            wx.WXK_F5: "F5", wx.WXK_F6: "F6", wx.WXK_F7: "F7", wx.WXK_F8: "F8",
            wx.WXK_F9: "F9", wx.WXK_F10: "F10", wx.WXK_F11: "F11", wx.WXK_F12: "F12"
        }
        name = key_map.get(keycode)
        if not name:
            if 32 <= keycode <= 126:
                name = chr(keycode).upper()
            else:
                name = f"Code({keycode})"
        print(f"[DEBUG] Menekan tombol: {mod_str}{name}", flush=True)
        
        if modifiers == (wx.MOD_ALT | wx.MOD_SHIFT) and keycode in (ord('V'), ord('v')):
            self.on_open_volume_manager()
            return
            
        if keycode == wx.WXK_F1:
            wx.CallAfter(self.help.show_help)
            return
            
        if keycode == wx.WXK_F2 and self.state != 'IN_GAME':
            popup = wx.Menu()
            saved_accs = getattr(self.player, 'saved_accounts', [])
            if not saved_accs and self.player.username and self.player.token:
                saved_accs = [{"username": self.player.username, "token": self.player.token}]
            if saved_accs:
                for acc in saved_accs:
                    mi = popup.Append(wx.ID_ANY, f"Masuk sebagai {acc['username']}")
                    self.frame.Bind(wx.EVT_MENU, lambda evt, u=acc['username'], t=acc['token']: self.do_token_login(u, t), mi)
                mi_lain = popup.Append(wx.ID_ANY, "Login ke Akun Lain")
                self.frame.Bind(wx.EVT_MENU, lambda evt: self.akun_ui.show_login_form(), mi_lain)
                mi_hapus = popup.Append(wx.ID_ANY, "Hapus Akun Tersimpan")
                self.frame.Bind(wx.EVT_MENU, lambda evt: self.clear_accounts(), mi_hapus)
            else:
                mi_lain = popup.Append(wx.ID_ANY, "Login Akun")
                self.frame.Bind(wx.EVT_MENU, lambda evt: self.akun_ui.show_login_form(), mi_lain)
            self.frame.PopupMenu(popup)
            popup.Destroy()
            return
            
        if self.state == 'STATE_INTRO' and keycode == wx.WXK_SPACE:
            self.skip_intro()
            return
        
        if self.state == 'STATE_INTRO':
            if keycode in (wx.WXK_SPACE, wx.WXK_RETURN, wx.WXK_ESCAPE):
                self.skip_intro()
            return
            
        if keycode == wx.WXK_ESCAPE:
            if self.state == 'IN_GAME':
                dlg = wx.MessageDialog(self.frame, "Apakah kamu yakin ingin keluar ke Menu Utama?", "Konfirmasi Keluar", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == wx.ID_YES:
                    self.api.logout()
                    self.game.stop()
                    self.tt.stop()
                    self.audio.stop_all()
                    self.state = 'STATE_MENU'
                    self.audio.play_loop("menumus8.ogg", volume=self.player.bgm_volume)
                    self.panel.Show()
                    self.motd_list.SetFocus()
                    self.frame.Layout()
                    self.build_menu_bar()
            else:
                dlg = wx.MessageDialog(self.frame, "Apakah kamu yakin ingin menutup Gutsy Dawn?", "Keluar Game", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == wx.ID_YES:
                    self.tts.speak("Keluar dari game.")
                    self.frame.Close()
            return
            
        if self.state.startswith('MENU_'):
            ctrl_pressed = (modifiers & wx.MOD_CONTROL) != 0
            if ctrl_pressed and keycode == ord('W'):
                self.state = 'IN_GAME'
                self.tts.speak("Menu ditutup paksa.")
                self.api.send_action("batal")
                return
            self.menus.handle_input(keycode)
        elif self.state == 'IN_GAME':
            self.game.handle_input(keycode, modifiers)
            
        event.Skip()
        
    def on_close(self, event):
        self.player.save_profile()
        if hasattr(self, 'game'):
            self.game.stop()
        if hasattr(self, 'tt'):
            self.tt.stop()
        if hasattr(self, 'ambience'):
            self.ambience.stop()
        if hasattr(self, 'audio'):
            self.audio.stop_all()
        if hasattr(self, 'chat'):
            self.chat.putuskan()
        event.Skip()

































    def clear_accounts(self):
        if not hasattr(self.player, 'saved_accounts') or not self.player.saved_accounts:
            self.tts.speak("Tidak ada akun tersimpan.")
            return
            
        choices = [acc['username'] for acc in self.player.saved_accounts]
        choices.append("Hapus Semua Akun (Bersihkan Daftar)")
        
        dlg = wx.SingleChoiceDialog(self.frame, "Pilih akun yang ingin dihapus dari daftar tersimpan:", "Hapus Akun Tersimpan", choices)
        if dlg.ShowModal() == wx.ID_OK:
            sel_idx = dlg.GetSelection()
            if sel_idx == len(choices) - 1:
                self.player.saved_accounts = []
                self.player.username = ""
                self.player.token = ""
                self.player.save_profile()
                self.tts.speak("Semua daftar akun tersimpan telah dibersihkan.")
            else:
                acc_name = choices[sel_idx]
                if self.player.username == acc_name:
                    self.player.username = ""
                    self.player.token = ""
                self.player.saved_accounts = [acc for acc in self.player.saved_accounts if acc['username'] != acc_name]
                self.player.save_profile()
                self.tts.speak(f"Akun {acc_name} berhasil dihapus dari daftar tersimpan.")
            self.build_menu_bar()
        dlg.Destroy()
        
    def do_token_login(self, username, token):
        self.player.username = username
        self.player.token = token
        self.chat.sambungkan()
        self.api.verify_token()
