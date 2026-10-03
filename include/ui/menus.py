import wx

class InputDialog(wx.Dialog):
    def __init__(self, parent, title, prompt):
        super().__init__(parent, title=title, size=(300, 150))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        lbl_prompt = wx.StaticText(panel, label=prompt)
        self.txt_input = wx.TextCtrl(panel)
        vbox.Add(lbl_prompt, 0, wx.ALL, 5)
        vbox.Add(self.txt_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, id=wx.ID_OK, label="OK")
        btn_cancel = wx.Button(panel, id=wx.ID_CANCEL, label="Batal")
        
        btn_ok.SetDefault()
        
        btn_box.Add(btn_ok, 0, wx.ALL, 5)
        btn_box.Add(btn_cancel, 0, wx.ALL, 5)
        
        vbox.Add(btn_box, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        
        panel.SetSizer(vbox)
        self.Centre()


class ChatDialog(wx.Dialog):
    def __init__(self, parent, role):
        super().__init__(parent, title="Kirim Pesan", size=(350, 250))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        lbl_msg = wx.StaticText(panel, label="Ketik pesanmu di sini:")
        self.txt_msg = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.txt_msg.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        vbox.Add(lbl_msg, 0, wx.ALL, 5)
        vbox.Add(self.txt_msg, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        lbl_target = wx.StaticText(panel, label="Kirim ke:")
        
        choices = ["Global (Seluruh Server)", "Lokal (Hanya satu map)"]
        if role == "developer":
            choices.append("Staf (Admin/Moderator)")
            choices.append("Broadcast (Developer)")
            
        self.cb_target = wx.ComboBox(panel, choices=choices, style=wx.CB_READONLY)
        self.cb_target.SetSelection(0)
        vbox.Add(lbl_target, 0, wx.ALL, 5)
        vbox.Add(self.cb_target, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, id=wx.ID_OK, label="Kirim")
        btn_cancel = wx.Button(panel, id=wx.ID_CANCEL, label="Batal")
        btn_ok.SetDefault()
        btn_box.Add(btn_ok, 0, wx.ALL, 5)
        btn_box.Add(btn_cancel, 0, wx.ALL, 5)
        vbox.Add(btn_box, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        
        panel.SetSizer(vbox)
        self.Centre()
        self.txt_msg.SetFocus()

    def on_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN and not event.ShiftDown():
            self.EndModal(wx.ID_OK)
        else:
            event.Skip()

class QuickMenuDialog(wx.Dialog):
    def __init__(self, parent, initial_selection=0):
        super().__init__(parent, title="GD Menu", size=(300, 220))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        lbl = wx.StaticText(panel, label="Gunakan panah atas bawah untuk memilih, lalu tekan Enter.")
        vbox.Add(lbl, 0, wx.ALL, 5)
        
        # Daftar command yang dikirim ke server
        self.menu_data = [
            ("Menu Hari Ini", "/start"),
            ("Cek status player", "/status"),
            ("Masuk ke menu cepat", "/menu_cepat"),
            ("Berbelanja di Toko NPC", "/toko"),
            ("Membersihkan kuncian Input", "/clear"),
            ("Ajak temanmu untuk bergabung", "/undang"),
            ("Baca panduan game", "/help"),
            ("Buat pintasan bermain dengan mudah dan cepat", "/shortcut"),
            ("Menghubungi tim staf", "/hubungi"),
            ("Melihat pembaruan atau changelog bot", "/changelog"),
            ("Tutup Menu", "tutup")
        ]
        
        choices = [item[0] for item in self.menu_data]
        self.listbox = wx.ListBox(panel, choices=choices)
        if 0 <= initial_selection < len(choices):
            self.listbox.SetSelection(initial_selection)
        else:
            self.listbox.SetSelection(0)
        vbox.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 5)
        
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, id=wx.ID_OK, label="Pilih")
        btn_cancel = wx.Button(panel, id=wx.ID_CANCEL, label="Batal")
        btn_ok.SetDefault()
        btn_box.Add(btn_ok, 0, wx.RIGHT, 5)
        btn_box.Add(btn_cancel, 0, wx.LEFT, 5)
        vbox.Add(btn_box, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        panel.SetSizer(vbox)
        self.Centre()
        
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.listbox.Bind(wx.EVT_LISTBOX_DCLICK, lambda evt: self.EndModal(wx.ID_OK))
        self.listbox.SetFocus()

    def on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

class MenuManager:
    def __init__(self, manager):
        self.manager = manager
        self.menu_items = []
        self.menu_callbacks = []
        self.selection = 0
        self.menu_title = ""
        
    def show_main_menu(self):
        self.manager.state = 'STATE_MENU'
        import wx
        wx.CallAfter(self.manager.panel.Show)
        wx.CallAfter(self.manager.motd_list.SetFocus)
        wx.CallAfter(self.manager.frame.Layout)
        wx.CallAfter(self.manager.build_menu_bar)
        
    def show_server_menu(self, text, buttons):
        self.manager.state = 'MENU_SERVER'
        self.manager.audio.play("Menu_Pannel_Server.ogg")
        self.menu_title = text
        self.menu_items = []
        self.menu_callbacks = []
        
        # Jadikan teks utama sebagai "item menu maya" di urutan teratas (index 0)
        if text:
            self.menu_items.append(text)
            self.menu_callbacks.append("TEXT_ONLY")
        
        for row in buttons:
            for btn in row:
                self.menu_items.append(btn.get("text", "Tombol"))
                self.menu_callbacks.append(btn.get("callback_data", ""))
        
        
        
        
        self.selection = 0
        # Bacakan langsung teks pertama (yang merupakan isi utama pesan)
        self.manager.tts.speak(self.menu_items[self.selection])

    def show_input_dialog(self, prompt_text, action_override=None):
        dlg = InputDialog(self.manager.frame, "Masukan Server", prompt_text)
        if dlg.ShowModal() == wx.ID_OK:
            action = dlg.txt_input.GetValue().strip()
            if action:
                self.manager.tts.speak("Mengirim...")
                if action_override == "staf":
                    self.manager.api.send_chat("developer", action)
                else:
                    self.manager.api.send_action(action)
            else:
                self.manager.api.send_action("batal")
        else:
            self.manager.api.send_action("batal")
        dlg.Destroy()
        self.manager.frame.SetFocus()









    def show_chat_dialog(self, initial_text="", initial_target=0):
        dlg = ChatDialog(self.manager.frame, self.manager.player.role)
        if initial_text:
            dlg.txt_msg.SetValue(initial_text)
            dlg.txt_msg.SetInsertionPointEnd()
        dlg.cb_target.SetSelection(initial_target)
        if dlg.ShowModal() == wx.ID_OK:
            msg = dlg.txt_msg.GetValue().strip()
            target = dlg.cb_target.GetSelection()
            self.manager.frame.SetFocus()
            
            if msg:
                self.manager.tts.speak("Mengirim pesan...")
                
                if self.manager.player.role == "developer":
                    target_map = ["global", "lokal", "developer", "broadcast"]
                else:
                    target_map = ["global", "lokal"]
                    
                if target >= len(target_map):
                    target = 0
                    
                target_type = target_map[target]
                
                def _send_chat():
                    if target_type == "global":
                        format_pesan = f"{self.manager.player.username}: {msg}"
                        self.manager.chat.kirim_global(format_pesan)
                    elif target_type == "lokal":
                        format_pesan = f"{self.manager.player.username}: {msg}"
                        self.manager.chat.kirim_lokal(format_pesan)
                    elif target_type == "broadcast":
                        format_pesan = f"PENGUMUMAN SERVER: {msg}"
                        self.manager.chat.kirim_broadcast(format_pesan)
                    elif target_type == "developer":
                        format_pesan = f"STAF [{self.manager.player.username}]: {msg}"
                        self.manager.chat.kirim_staf(format_pesan)
                
                import threading
                threading.Thread(target=_send_chat, daemon=True).start()
                
        else:
            self.manager.frame.SetFocus()
        dlg.Destroy()

    def show_quick_menu(self):
        initial_sel = getattr(self, 'last_quick_menu_sel', 0)
        dlg = QuickMenuDialog(self.manager.frame, initial_selection=initial_sel)
        res = dlg.ShowModal()
        sel = dlg.listbox.GetSelection()
        if sel != wx.NOT_FOUND:
            self.last_quick_menu_sel = sel
        self.manager.frame.SetFocus()
        
        if res == wx.ID_OK:
            command_label, command_action = dlg.menu_data[sel]
            if command_action != "tutup":
                self.manager.tts.speak(f"Membuka {command_label}...")
                self.manager.api.send_action(command_action)
        dlg.Destroy()

    def handle_input(self, keycode):
        # Menu navigation (List menus)
        if keycode == wx.WXK_UP:
            if self.selection > 0:
                self.manager.audio.play("menu_move.ogg")
                self.selection -= 1
                self.manager.tts.speak(self.menu_items[self.selection])
        elif keycode == wx.WXK_DOWN:
            if self.selection < len(self.menu_items) - 1:
                self.manager.audio.play("menu_move.ogg")
                self.selection += 1
                self.manager.tts.speak(self.menu_items[self.selection])
        elif keycode == wx.WXK_RETURN:
            callback = self.menu_callbacks[self.selection]
            if callback == "TEXT_ONLY":
                return # Teks informasi, bukan tombol sungguhan
            
            self.manager.audio.play("menu_select.ogg")
            if self.manager.state == 'MENU_MAIN':
                if callback == "login_token":
                    self.manager.api.verify_token()
                elif callback == "login_new":
                    # Panggil fungsi asinkron agar tidak memblokir event EVT_KEY_DOWN
                    wx.CallAfter(self.manager.akun_ui.show_login_form)
                elif callback == "register":
                    wx.CallAfter(self.manager.akun_ui.show_register_form)
                elif callback == "forgot_password":
                    wx.CallAfter(self.manager.akun_ui.show_forgot_password_form)
                elif callback == "exit":
                    self.manager.frame.Close()
            elif self.manager.state == 'MENU_SERVER':
                # Gunakan CallAfter jika api call memicu dialog lain
                wx.CallAfter(self.manager.api.send_action, callback)
        elif keycode == wx.WXK_BACK:
            # Auto-klik tombol kembali/batal/tutup jika ada
            for i, text in enumerate(self.menu_items):
                t_lower = text.lower()
                if "batal" in t_lower or "tutup" in t_lower or "kembali" in t_lower or "selesai" in t_lower:
                    callback = self.menu_callbacks[i]
                    self.manager.audio.play("menu_select.ogg")
                    if self.manager.state == 'MENU_MAIN':
                        pass # Menu utama tidak bisa diback
                    elif self.manager.state == 'MENU_SERVER':
                        wx.CallAfter(self.manager.api.send_action, callback)
                    return
            
            # Jika tidak ada tombol batal yang jelas, tutup paksa
            if self.manager.state == 'MENU_SERVER':
                self.manager.audio.play("menu_select.ogg")
                self.manager.state = 'IN_GAME'
                self.manager.tts.speak("Menu ditutup paksa.")
                wx.CallAfter(self.manager.api.send_action, "batal")















