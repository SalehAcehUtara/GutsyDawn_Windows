import wx
import os
import sys
import threading
import requests
import zipfile
import shutil
import subprocess

class ClientUpdateDialog(wx.Dialog):
    def __init__(self, parent, remote_ver, zip_url, tts_manager):
        super().__init__(parent, title="Proses Update Klien", size=(400, 200))
        self.zip_url = zip_url
        self.tts = tts_manager
        self.remote_ver = remote_ver
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.lbl_status = wx.StaticText(self, label="Mengunduh update... Mohon tunggu.")
        vbox.Add(self.lbl_status, 0, wx.ALL | wx.EXPAND, 15)
        
        self.SetSizer(vbox)
        self.Centre()
        
                # Sembunyikan window utama agar cuma updater yang kelihatan
        # JANGAN PAKE parent.Hide() KARENA BIKIN DIALOG ANAK JUGA IKUT HILANG/FREEZE!
        # if parent:
        #     parent.Hide()
            
        # Matikan semua suara/musik game agar seolah-olah game sudah tutup
        try:
            import pygame
            pygame.mixer.music.stop()
            pygame.mixer.stop()
        except:
            pass
            
        wx.CallAfter(self.tts.speak, "Memulai unduhan, ukuran sekitar 50 sampai 100 megabyte. Mohon ditunggu.")
        threading.Thread(target=self._download_and_apply, daemon=True).start()
        
    def _download_and_apply(self):
        try:
                        # 1. Download zip dari Github Releases
            zip_path = "update_download.zip"
            # Pakai URL rilis resmi Github biar dapet Content-Length (ukuran file)
            real_zip_url = f"https://github.com/SalehAcehUtara/GutsyDawn_Windows/releases/download/v{self.remote_ver}/GutsyDawn.zip"
            
            r = requests.get(real_zip_url, stream=True, timeout=30)
            if r.status_code == 200 or r.status_code == 302:
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                last_announced_percent = 0
                last_label_percent = -1
                
                with open(zip_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0:
                                percent = int((downloaded / total_size) * 100)
                                # Update label di layar hanya jika persen berubah biar ngga bikin UI freeze
                                if percent > last_label_percent:
                                    last_label_percent = percent
                                    wx.CallAfter(self.lbl_status.SetLabel, f"Mengunduh... {percent}%")
                                
                                # Ngomong setiap kelipatan 10% (10, 20, 30, dst)
                                if percent > last_announced_percent and percent % 10 == 0:
                                    last_announced_percent = percent
                                    wx.CallAfter(self.tts.speak, f"{percent} persen")
                            else:
                                # Fallback kalau ternyata Content-Length tetep ga ada
                                mb = downloaded // (1024 * 1024)
                                wx.CallAfter(self.lbl_status.SetLabel, f"Mengunduh... {mb} MB")
            else:
                raise Exception(f"HTTP Error {r.status_code}")
                
            wx.CallAfter(self.lbl_status.SetLabel, "Mengekstrak file...")
            wx.CallAfter(self.tts.speak, "Mengekstrak file update.")
            
            # 2. Ekstrak zip ke folder sementara pake Python
            extract_folder = "update_extracted_temp"
            if os.path.exists(extract_folder):
                shutil.rmtree(extract_folder)
            os.makedirs(extract_folder)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)
                
            # Karena dari github biasanya ada folder utama (misal GutsyDawn-main)
            # Kita cari folder terdalam yang isinya GutsyDawn.exe
            source_folder = extract_folder
            for root, dirs, files in os.walk(extract_folder):
                if "GutsyDawn.exe" in files:
                    source_folder = root
                    break
            
            wx.CallAfter(self.lbl_status.SetLabel, "Menerapkan update... Game akan direstart otomatis.")
            wx.CallAfter(self.tts.speak, "Update siap. Game akan direstart otomatis.")
            
            # 3. Buat file .bat (Si Penutup Sementara)
            bat_path = "pasang_update.bat"
            pid = os.getpid()
            bat_content = f"""@echo off
setlocal EnableDelayedExpansion
title Memasang Update Gutsy Dawn...
echo Menunggu game ditutup...
set /a WAIT_SECONDS=0
:WAIT
tasklist /FI "PID eq {pid}" 2>NUL | find "{pid}" >NUL
if not errorlevel 1 (
    set /a WAIT_SECONDS+=1
    if !WAIT_SECONDS! GEQ 10 (
        taskkill /F /PID {pid} >NUL 2>&1
    )
    ping 127.0.0.1 -n 2 >NUL
    goto WAIT
)
ping 127.0.0.1 -n 3 >NUL
echo Menimpa file lama...
xcopy /Y /E /H /C /I "{source_folder}\\*" "."
echo Bersih-bersih...
rmdir /s /q "{extract_folder}"
del /f /q "{zip_path}"
echo Menyalakan game kembali...
start "" "GutsyDawn.exe"
del "%~f0"
"""
            with open(bat_path, "w") as f:
                f.write(bat_content)
            
            # 4. Jalankan .bat secara gaib (tanpa console popup yang merusak konsentrasi NVDA)
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            subprocess.Popen(bat_path, shell=True, creationflags=flags)
            
            wx.CallAfter(self.EndModal, wx.ID_OK)
            wx.CallAfter(self.GetParent().Close) # Mematikan game
            
        except Exception as e:
            wx.CallAfter(self.lbl_status.SetLabel, f"Gagal update: {str(e)}")
            wx.CallAfter(self.tts.speak, "Gagal mengunduh update.")
            # Hapus file temp kalau gagal
            if os.path.exists("update_download.zip"):
                os.remove("update_download.zip")

class ClientUpdater:
    

    def __init__(self, app_manager):
        self.manager = app_manager
        # Cek versi langsung ke server Cloudflare
        self.version_url = "https://api.github.com/repos/SalehAcehUtara/GutsyDawn_Windows/releases/latest"
        self.zip_url = "https://github.com/SalehAcehUtara/GutsyDawn_Windows/archive/refs/heads/main.zip"
            
    def get_local_version(self):
        try:
            import os, sys
            if getattr(sys, 'frozen', False):
                base_dir = sys._MEIPASS
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            with open(os.path.join(base_dir, 'include', 'updater', 'version.txt'), 'r', encoding='utf-8') as f:
                return f.read().strip()
        except:
            return "1.0.0"

    def check_update(self, auto=False, callback=None):
        local_ver = self.get_local_version()
        
        # Biar game nggak nge-freeze saat ngecek, kita pakai thread
        def _check():
            try:
                # Tambahin timeout biar gak kelamaan kalau internet lemot
                res = requests.get(self.version_url, timeout=7)
                if res.status_code == 200:
                    data = res.json()
                    remote_ver = data.get("tag_name", "").replace("v", "").strip()
                    changelog = data.get("body", "").strip()
                    if remote_ver and remote_ver != local_ver:
                        # Cek apakah remote lebih baru dari local
                        try:
                            rv_parts = [int(x) for x in remote_ver.split('.')]
                            lv_parts = [int(x) for x in local_ver.split('.')]
                            is_newer = rv_parts > lv_parts
                        except:
                            is_newer = remote_ver != local_ver
                            
                        if is_newer:
                            # Ada update!
                            wx.CallAfter(self._prompt_update, remote_ver, changelog, callback)
                        else:
                            if not auto:
                                wx.CallAfter(self._show_info, f"Kamu sudah menggunakan versi klien terbaru!\nVersi: {local_ver}")
                            if callback:
                                wx.CallAfter(callback)
                    else:
                        # Jika versi sama persis
                        if not auto:
                            wx.CallAfter(self._show_info, f"Kamu sudah menggunakan versi klien terbaru!\nVersi: {local_ver}")
                        if callback:
                            wx.CallAfter(callback)
                else:
                    if not auto:
                        wx.CallAfter(self._show_info, "Gagal terhubung ke server update.")
                    if callback:
                        wx.CallAfter(callback)
            except Exception as e:
                if not auto:
                    wx.CallAfter(self._show_info, f"Terjadi kesalahan koneksi:\n{str(e)}")
                if callback:
                    wx.CallAfter(callback)
                
        threading.Thread(target=_check, daemon=True).start()
        
    def _prompt_update(self, remote_ver, changelog, callback=None):
        dlg = wx.Dialog(self.manager.frame, title="Update Gutsy Dawn", size=(500, 400))
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        lbl = wx.StaticText(dlg, label=f"Versi terbaru Gutsy Dawn ({remote_ver}) telah tersedia!")
        vbox.Add(lbl, 0, wx.ALL, 10)
        
        if changelog:
            lbl_cl = wx.StaticText(dlg, label="Apa yang baru:")
            vbox.Add(lbl_cl, 0, wx.LEFT | wx.RIGHT, 10)
            txt_cl = wx.TextCtrl(dlg, style=wx.TE_MULTILINE | wx.TE_READONLY, value=changelog)
            vbox.Add(txt_cl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
            
        lbl_q = wx.StaticText(dlg, label="Apakah kamu mau mengunduh dan memasangnya sekarang?")
        vbox.Add(lbl_q, 0, wx.ALL, 10)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        btn_yes = wx.Button(dlg, wx.ID_YES, "Ya (Download)")
        btn_no = wx.Button(dlg, wx.ID_NO, "Tidak")
        hbox.Add(btn_yes, 0, wx.ALL, 5)
        hbox.Add(btn_no, 0, wx.ALL, 5)
        vbox.Add(hbox, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        dlg.SetSizer(vbox)
        dlg.Centre()
        
        btn_yes.Bind(wx.EVT_BUTTON, lambda e: dlg.EndModal(wx.ID_YES))
        btn_no.Bind(wx.EVT_BUTTON, lambda e: dlg.EndModal(wx.ID_NO))
        
        # Focus on text if changelog exists, else yes button
        wx.CallAfter(btn_yes.SetFocus)
        
        result = dlg.ShowModal()
        dlg.Destroy()
        
        if result == wx.ID_YES:
            dl_dlg = ClientUpdateDialog(self.manager.frame, remote_ver, self.zip_url, self.manager.tts)
            dl_dlg.ShowModal()
            
    def _show_info(self, pesan):
        wx.MessageBox(pesan, "Update Klien", wx.OK | wx.ICON_INFORMATION)




