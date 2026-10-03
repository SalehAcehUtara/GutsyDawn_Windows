import os
import sys
import threading
import requests
import wx
import sys
from include.core.app_paths import get_sounds_dir

class DownloadDialog(wx.Dialog):
    def __init__(self, parent, title, missing_files, repo_url, tts_manager):
        super().__init__(parent, title=title, size=(500, 400))
        self.missing_files = missing_files
        self.repo_url = repo_url
        self.tts = tts_manager
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.lbl_status = wx.StaticText(panel, label="Memulai pengunduhan...")
        vbox.Add(self.lbl_status, 0, wx.ALL | wx.EXPAND, 10)
        
        self.list_box = wx.ListBox(panel, style=wx.LB_SINGLE)
        vbox.Add(self.list_box, 1, wx.ALL | wx.EXPAND, 10)
        
        self.btn_close = wx.Button(panel, id=wx.ID_CLOSE, label="Tutup")
        self.btn_close.Disable()
        self.btn_close.Bind(wx.EVT_BUTTON, self.on_close)
        vbox.Add(self.btn_close, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        panel.SetSizer(vbox)
        self.Centre()
        self.list_box.SetFocus()
        
        # Mulai thread
        threading.Thread(target=self._download_task, daemon=True).start()
        
    def _download_task(self):
        total = len(self.missing_files)
        sukses = 0
        gagal = 0
        last_announced = 0
        
        for i, (filepath, local_path) in enumerate(self.missing_files):
            filename = os.path.basename(filepath)
            url = f"{self.repo_url}/{filepath.replace('\\', '/')}"
            try:
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    with open(local_path, 'wb') as out:
                        out.write(r.content)
                    sukses += 1
                    wx.CallAfter(self.list_box.Append, f"[SUKSES] {filename}")
                else:
                    gagal += 1
                    wx.CallAfter(self.list_box.Append, f"[GAGAL] {filename} (HTTP {r.status_code})")
            except Exception as e:
                gagal += 1
                wx.CallAfter(self.list_box.Append, f"[GAGAL] {filename} ({str(e)})")
                
            wx.CallAfter(self.list_box.SetSelection, self.list_box.GetCount() - 1)
            
            persen = int(((i + 1) / total) * 100)
            wx.CallAfter(self.lbl_status.SetLabel, f"Mengunduh... {persen}% ({i+1}/{total})")
            
            if persen - last_announced >= 20 or persen == 100:
                if persen != last_announced:
                    wx.CallAfter(self.tts.speak, f"{persen} persen")
                    last_announced = persen
                    
        wx.CallAfter(self.lbl_status.SetLabel, f"Selesai! Berhasil: {sukses}, Gagal: {gagal}")
        wx.CallAfter(self.tts.speak, "Pengunduhan paket suara telah selesai.")
        wx.CallAfter(self.btn_close.Enable)
        wx.CallAfter(self.btn_close.SetFocus)
        
    def on_close(self, event):
        self.Destroy()

class SoundUpdater:
    def __init__(self, app_manager):
        self.manager = app_manager
        self.repo_url = "https://huggingface.co/datasets/salehganteng/gutsy_dawn-voicepack/resolve/main"

    def check_update(self, auto=False, callback=None):
        try:
            if getattr(sys, 'frozen', False):
                list_path = os.path.join(sys._MEIPASS, 'include', 'updater', 'sound_list.txt')
            else:
                list_path = os.path.join(sys._MEIPASS if getattr(sys, 'frozen', False) else os.getcwd(), 'include', 'updater', 'sound_list.txt')
                
            if not os.path.exists(list_path):
                if not auto: wx.MessageBox(f"Error: File daftar suara tidak ditemukan!\nPath: {list_path}", "Error Update", wx.OK | wx.ICON_ERROR)
                if callback: wx.CallAfter(callback)
                return

            try:
                with open(list_path, 'r', encoding='utf-16') as f:
                    files = [line.strip() for line in f if line.strip()]
            except UnicodeError:
                try:
                    with open(list_path, 'r', encoding='utf-8-sig') as f:
                        files = [line.strip() for line in f if line.strip()]
                except UnicodeError:
                    with open(list_path, 'r', encoding='ansi') as f:
                        files = [line.strip() for line in f if line.strip()]

            missing_files = []
            for filepath in files:
                filename = os.path.basename(filepath)
                local_path = os.path.join(get_sounds_dir(), filename)
                if not os.path.exists(local_path):
                    missing_files.append((filepath, local_path))

            if not missing_files:
                if not auto: wx.MessageBox("Data suara kamu sudah lengkap! Tidak ada yang perlu diunduh.", "Update Suara", wx.OK | wx.ICON_INFORMATION)
                if callback: wx.CallAfter(callback)
                return

            dlg = wx.MessageDialog(None, f"Paket suara baru tersedia.\nTerdapat {len(missing_files)} file suara yang belum ada di komputermu.\n\nApakah kamu mau melanjutkan untuk unduh?", "Konfirmasi Update", wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            
            if result == wx.ID_YES:
                dl_dlg = DownloadDialog(self.manager.frame, "Proses Update Suara", missing_files, self.repo_url, self.manager.tts)
                dl_dlg.ShowModal()
                dl_dlg.Destroy()
                if callback: wx.CallAfter(callback)
            else:
                if callback: wx.CallAfter(callback)
        except Exception as e:
            if not auto: wx.MessageBox(f"Terjadi kesalahan saat update:\n{str(e)}", "Error", wx.OK | wx.ICON_ERROR)
            if callback: wx.CallAfter(callback)

