import wx

class OTPDialog(wx.Dialog):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(320, 160))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        lbl_otp = wx.StaticText(panel, label="Masukkan 6 angka OTP dari email Anda:")
        self.txt_otp = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        vbox.Add(lbl_otp, 0, wx.ALL, 5)
        vbox.Add(self.txt_otp, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, id=wx.ID_OK, label="Verifikasi")
        btn_cancel = wx.Button(panel, id=wx.ID_CANCEL, label="Batal")
        btn_ok.SetDefault()
        btn_box.Add(btn_ok, 0, wx.ALL, 5)
        btn_box.Add(btn_cancel, 0, wx.ALL, 5)
        vbox.Add(btn_box, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        
        panel.SetSizer(vbox)
        self.Centre()
        
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.txt_otp.Bind(wx.EVT_TEXT_ENTER, lambda evt: self.EndModal(wx.ID_OK))
        self.txt_otp.SetFocus()

    def on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

class RegisterDialog(wx.Dialog):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(400, 450))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Nama
        lbl_nama = wx.StaticText(panel, label="Nama Karakter/Pemain:")
        self.txt_nama = wx.TextCtrl(panel)
        vbox.Add(lbl_nama, 0, wx.ALL, 5)
        vbox.Add(self.txt_nama, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        # Gender
        lbl_gender = wx.StaticText(panel, label="Jenis Kelamin:")
        self.cb_gender = wx.ComboBox(panel, choices=["Laki-laki", "Perempuan"], style=wx.CB_READONLY)
        self.cb_gender.SetSelection(0)
        vbox.Add(lbl_gender, 0, wx.ALL, 5)
        vbox.Add(self.cb_gender, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        # Email
        lbl_email = wx.StaticText(panel, label="Alamat Email (Harus Asli/Aktif):")
        self.txt_email = wx.TextCtrl(panel)
        vbox.Add(lbl_email, 0, wx.ALL, 5)
        vbox.Add(self.txt_email, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        # Password
        lbl_pass = wx.StaticText(panel, label="Password:")
        self.txt_pass = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        vbox.Add(lbl_pass, 0, wx.ALL, 5)
        vbox.Add(self.txt_pass, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        # Reason
        lbl_reason = wx.StaticText(panel, label="Alasan Bermain Gutsy Dawn (Minimal 50 Karakter):")
        self.txt_reason = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        vbox.Add(lbl_reason, 0, wx.ALL, 5)
        vbox.Add(self.txt_reason, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        # Buttons
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, id=wx.ID_OK, label="Daftar")
        btn_cancel = wx.Button(panel, id=wx.ID_CANCEL, label="Batal")
        
        btn_ok.SetDefault()
        
        btn_box.Add(btn_ok, 0, wx.ALL, 5)
        btn_box.Add(btn_cancel, 0, wx.ALL, 5)
        
        vbox.Add(btn_box, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        
        panel.SetSizer(vbox)
        self.Centre()

class LoginDialog(wx.Dialog):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(300, 200))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Email
        lbl_email = wx.StaticText(panel, label="Alamat Email:")
        self.txt_email = wx.TextCtrl(panel)
        vbox.Add(lbl_email, 0, wx.ALL, 5)
        vbox.Add(self.txt_email, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        # Password
        lbl_pass = wx.StaticText(panel, label="Password:")
        self.txt_pass = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        vbox.Add(lbl_pass, 0, wx.ALL, 5)
        vbox.Add(self.txt_pass, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        # Buttons
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, id=wx.ID_OK, label="Masuk")
        btn_forgot = wx.Button(panel, id=wx.ID_HELP, label="Lupa Password")
        btn_cancel = wx.Button(panel, id=wx.ID_CANCEL, label="Batal")
        
        btn_ok.SetDefault()
        
        btn_box.Add(btn_ok, 0, wx.ALL, 5)
        btn_box.Add(btn_forgot, 0, wx.ALL, 5)
        btn_box.Add(btn_cancel, 0, wx.ALL, 5)
        
        vbox.Add(btn_box, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        
        btn_forgot.Bind(wx.EVT_BUTTON, self.on_forgot)
        
        panel.SetSizer(vbox)
        self.Centre()

    def on_forgot(self, event):
        self.EndModal(wx.ID_HELP)

class ForgotPasswordDialog(wx.Dialog):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(300, 150))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        lbl_email = wx.StaticText(panel, label="Masukkan Email akun Anda:")
        self.txt_email = wx.TextCtrl(panel)
        vbox.Add(lbl_email, 0, wx.ALL, 5)
        vbox.Add(self.txt_email, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        btn_ok = wx.Button(panel, id=wx.ID_OK, label="Kirim OTP")
        btn_ok.SetDefault()
        vbox.Add(btn_ok, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        panel.SetSizer(vbox)
        self.Centre()

class ResetPasswordDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(ResetPasswordDialog, self).__init__(parent, title=title, size=(300, 250))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.lbl_otp = wx.StaticText(self, label="Masukkan 6 angka OTP dari email Anda:")
        sizer.Add(self.lbl_otp, 0, wx.ALL | wx.EXPAND, 5)
        self.txt_otp = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.txt_otp, 0, wx.ALL | wx.EXPAND, 5)
        
        self.lbl_pass = wx.StaticText(self, label="Password Baru:")
        sizer.Add(self.lbl_pass, 0, wx.ALL | wx.EXPAND, 5)
        self.txt_pass = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        sizer.Add(self.txt_pass, 0, wx.ALL | wx.EXPAND, 5)
        
        self.btn_reset = wx.Button(self, label="Ubah Password")
        sizer.Add(self.btn_reset, 0, wx.ALL | wx.CENTER, 5)
        
        self.btn_reset.Bind(wx.EVT_BUTTON, self.on_reset)
        self.txt_otp.Bind(wx.EVT_TEXT_ENTER, self.on_reset)
        self.txt_pass.Bind(wx.EVT_TEXT_ENTER, self.on_reset)
        
        self.SetSizer(sizer)
        
        self.txt_otp.SetFocus()

    def on_reset(self, event):
        if not self.txt_otp.GetValue().strip() or not self.txt_pass.GetValue().strip():
            wx.MessageBox("OTP dan Password Baru wajib diisi!", "Error", wx.OK | wx.ICON_ERROR)
            return
        self.EndModal(wx.ID_OK)
        
class AkunUIManager:
    def __init__(self, manager):
        self.manager = manager

    def show_otp_dialog(self, email):
        self.manager.tts.speak("Email terkirim! Silakan buka inbox email Anda dan masukkan 6 angka kode verifikasi.")
        dlg = OTPDialog(self.manager.frame, "Verifikasi OTP")
        if dlg.ShowModal() == wx.ID_OK:
            otp_code = dlg.txt_otp.GetValue().strip()
            self.manager.akun_api.verify_otp(email, otp_code)
        else:
            self.manager.tts.speak("Verifikasi dibatalkan.")
            self.manager.frame.SetFocus()
            self.manager.menus.show_main_menu()
        dlg.Destroy()

    def show_register_form(self):
        dlg = RegisterDialog(self.manager.frame, "Pendaftaran Akun Gutsy Dawn")
        if dlg.ShowModal() == wx.ID_OK:
            nama = dlg.txt_nama.GetValue().strip()
            gender = dlg.cb_gender.GetStringSelection()
            email = dlg.txt_email.GetValue().strip()
            password = dlg.txt_pass.GetValue().strip()
            reason = dlg.txt_reason.GetValue().strip()
            
            if not nama or not email or not password or not reason:
                self.manager.tts.speak("Mohon isi semua kolom yang diperlukan!")
                self.manager.frame.SetFocus()
                self.manager.menus.show_main_menu()
            else:
                self.manager.akun_api.register(nama, gender, email, password, reason)
        else:
            self.manager.frame.SetFocus()
            self.manager.menus.show_main_menu()
        dlg.Destroy()

    def show_login_form(self):
        dlg = LoginDialog(self.manager.frame, "Login Gutsy Dawn")
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            email = dlg.txt_email.GetValue().strip()
            password = dlg.txt_pass.GetValue().strip()
            self.manager.akun_api.login(email, password)
        elif res == wx.ID_HELP:
            wx.CallAfter(self.show_forgot_password_form)
        else:
            self.manager.frame.SetFocus()
            self.manager.menus.show_main_menu()
        dlg.Destroy()
        
    def show_forgot_password_form(self):
        dlg = ForgotPasswordDialog(self.manager.frame, "Lupa Password")
        if dlg.ShowModal() == wx.ID_OK:
            email = dlg.txt_email.GetValue().strip()
            self.manager.akun_api.forgot_password(email)
        else:
            self.manager.frame.SetFocus()
            self.manager.menus.show_main_menu()
        dlg.Destroy()

    def show_reset_password_dialog(self, email):
        dlg = ResetPasswordDialog(self.manager.frame, "Reset Password")
        if dlg.ShowModal() == wx.ID_OK:
            otp = dlg.txt_otp.GetValue().strip()
            new_pass = dlg.txt_pass.GetValue().strip()
            self.manager.akun_api.reset_password(email, otp, new_pass)
        else:
            self.manager.frame.SetFocus()
            self.manager.menus.show_main_menu()
        dlg.Destroy()
