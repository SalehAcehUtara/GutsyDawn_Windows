import wx

class ChatActionDialog(wx.Dialog):
    def __init__(self, parent, target_name):
        super().__init__(parent, title=f"Aksi untuk {target_name}", size=(300, 200))
        self.target_name = target_name
        self.panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(self.panel, label=f"Pilih aksi untuk pemain {target_name}:")
        vbox.Add(lbl, flag=wx.ALL, border=10)
        self.list_actions = wx.ListBox(self.panel, choices=["Balas (Reply)", "Pesan Pribadi (Private Message)"])
        vbox.Add(self.list_actions, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(self.panel, wx.ID_OK, "Pilih")
        btn_cancel = wx.Button(self.panel, wx.ID_CANCEL, "Batal")
        btn_box.Add(btn_ok, flag=wx.RIGHT, border=5)
        btn_box.Add(btn_cancel)
        vbox.Add(btn_box, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)
        self.panel.SetSizer(vbox)
        self.list_actions.SetSelection(0)
        self.list_actions.SetFocus()
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)

    def on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

class ChatHistoryDialog(wx.Dialog):
    def __init__(self, parent, chat_history_list, app_manager):
        super().__init__(parent, title="Riwayat Chat", size=(600, 450))
        self.app_manager = app_manager
        self.chat_history_list = chat_history_list
        
        self.panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.categories = [
            ("Semua", ["all"]),
            ("Global", ["global"]),
            ("Lokal", ["local", "lokal"]),
            ("Notif Server", ["server", "system_notif", "system"]),
            ("Koneksi", ["koneksi"])
        ]
        
        is_dev = (self.app_manager.player.role.lower() == 'developer')
        if is_dev:
            self.categories.extend([
                ("Pesan Staf", ["developer"]),
                ("Notifikasi Staf", ["staff_notif"]),
                ("Admin Tell", ["admin_tell"])
            ])
            
        cat_names = [c[0] for c in self.categories]
        
        lbl_filter = wx.StaticText(self.panel, label="Filter Kategori:")
        self.cb_filter = wx.ComboBox(self.panel, choices=cat_names, style=wx.CB_READONLY)
        self.cb_filter.SetSelection(0)
        
        vbox.Add(lbl_filter, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(self.cb_filter, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
        
        lbl_list = wx.StaticText(self.panel, label="Daftar Pesan:")
        self.list_chat = wx.ListBox(self.panel)
        
        vbox.Add(lbl_list, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(self.list_chat, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_close = wx.Button(self.panel, wx.ID_CANCEL, label="Tutup")
        btn_box.Add(btn_close, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(btn_box, flag=wx.ALIGN_CENTER)
        
        self.panel.SetSizer(vbox)
        
        self.cb_filter.Bind(wx.EVT_COMBOBOX, self.on_filter_change)
        self.list_chat.Bind(wx.EVT_LISTBOX_DCLICK, self.on_action)
        self.list_chat.Bind(wx.EVT_KEY_DOWN, self.on_key)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        self.update_list()
        
        wx.CallAfter(self.cb_filter.SetFocus)
        
    def on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()
        
    def on_filter_change(self, event):
        self.update_list()
        event.Skip()
        
    def update_list(self):
        sel_idx = self.cb_filter.GetSelection()
        filters = self.categories[sel_idx][1]
        
        filtered = []
        for msg in self.chat_history_list:
            ctype = ""
            if "]" in msg:
                ctype = msg.split("]")[0].replace("[", "").lower().strip()
                
            if "all" in filters:
                filtered.append(msg)
            else:
                if ctype in filters:
                    filtered.append(msg)
                elif "koneksi" in filters and ("telah keluar" in msg.lower() or "bergabung" in msg.lower()):
                    filtered.append(msg)
                    
        if not filtered:
            filtered = ["(Kosong)"]
            
        self.list_chat.Clear()
        self.list_chat.AppendItems(filtered)
        if filtered != ["(Kosong)"]:
            self.list_chat.SetSelection(self.list_chat.GetCount() - 1)
            
    def on_key(self, event):
        code = event.GetKeyCode()
        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.on_action(event)
        elif code == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()
            
    def on_action(self, event):
        sel = self.list_chat.GetSelection()
        if sel == wx.NOT_FOUND:
            return
            
        text = self.list_chat.GetString(sel)
        if text == "(Kosong)":
            return
            
        if "]" in text and ":" in text:
            try:
                parts = text.split("]", 1)[1].strip()
                pname = parts.split(":", 1)[0].strip()
                
                if pname.lower() == "sistem":
                    self.app_manager.tts.speak("Tidak bisa membalas pesan sistem.")
                    return
                    
                dlg = ChatActionDialog(self, pname)
                if dlg.ShowModal() == wx.ID_OK:
                    action_idx = dlg.list_actions.GetSelection()
                    if action_idx == 0:
                        self.EndModal(wx.ID_OK)
                        self.app_manager.menus.show_chat_dialog(initial_text=f"@{pname} ")
                    elif action_idx == 1:
                        self.app_manager.tts.speak("Fitur Private Message (PM) sedang dalam pengembangan.")
                dlg.Destroy()
            except:
                pass
                
    def on_close(self, event):
        self.app_manager.tts.speak("Riwayat chat ditutup.")
        self.EndModal(wx.ID_CANCEL)

