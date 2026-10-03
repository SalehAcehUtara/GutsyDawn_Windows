import os
import wx

class HelpDialog(wx.Dialog):
    def __init__(self, parent, help_text):
        super().__init__(parent, title="Bantuan Gutsy Dawn", size=(520, 400))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        lbl = wx.StaticText(panel, label="Gunakan tombol panah untuk membaca teks bantuan:")
        vbox.Add(lbl, 0, wx.ALL, 8)
        
        self.txt = wx.TextCtrl(panel, value=help_text, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        vbox.Add(self.txt, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        
        self.btn_close = wx.Button(panel, wx.ID_CANCEL, label="Tutup Bantuan")
        vbox.Add(self.btn_close, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        panel.SetSizer(vbox)
        self.Centre()
        
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.btn_close.Bind(wx.EVT_BUTTON, self.on_close)
        
        self.txt.SetFocus()

    def on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    def on_close(self, event):
        self.EndModal(wx.ID_CANCEL)


class HelpManager:
    def __init__(self, app_manager):
        self.app = app_manager
        self.help_file_path = os.path.join(os.path.dirname(__file__), "help.txt")

    def load_help_text(self):
        if os.path.exists(self.help_file_path):
            try:
                with open(self.help_file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"Gagal membaca file bantuan: {e}"
        # Fallback coba cek bantuan.txt jika help.txt tidak ditemukan
        alt_path = os.path.join(os.path.dirname(__file__), "bantuan.txt")
        if os.path.exists(alt_path):
            try:
                with open(alt_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return "File bantuan tidak ditemukan."

    def copy_to_clipboard(self, text):
        try:
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(text))
                wx.TheClipboard.Close()
                return True
        except Exception:
            pass
        return False

    def show_help(self):
        text = self.load_help_text()
        self.copy_to_clipboard(text)
        
        speech_msg = (
            "Pesan bantuan telah disalin di clipboard. "
            "Tekan Alt+M untuk membuka menu. "
            "Alt+P untuk perjalanan. "
            "C untuk tahu di mana lokasi saat ini."
        )
        self.app.tts.speak(speech_msg)
        
        dlg = HelpDialog(self.app.frame, text)
        dlg.ShowModal()
        dlg.Destroy()
        if hasattr(self.app, 'frame') and self.app.frame:
            self.app.frame.SetFocus()
