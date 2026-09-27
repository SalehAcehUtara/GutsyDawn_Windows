# Panduan Kompilasi Gutsy Dawn (Python Client)

## Prasyarat (Yang Harus Di-install)
Untuk menjalankan kode sumber (gd.py) atau melakukan kompilasi sendiri, kamu harus menginstal library Python berikut:
\\\ash
pip install pygame wxPython accessible_output2 requests
\\\
*(Catatan: Module pytalk untuk TeamTalk tidak perlu diinstal via pip karena sudah disematkan (bundled) secara lokal di folder site-packages virtual environment kamu, dan sudah ikut dipaketkan saat kompilasi).*

## Cara Kompilasi Menjadi 1 File .exe (Sangat Rapi)
Aku mengompilasi game ini menggunakan **PyInstaller**. Karena game ini punya struktur folder khusus dan dependensi eksternal, perintah kompilasinya cukup panjang.

Masuk ke folder Windows, lalu jalankan perintah ini di CMD/Terminal:
\\\ash
pyinstaller --name GutsyDawn --noconsole --onefile -p include --add-data "include/updater/sound_list.txt;include/updater" --add-data "D:\File\Bot\TeamTalk Bot\teamtalk-telegram-sender\.venv\Lib\site-packages\pytalk;pytalk" gd.py
\\\

### Penjelasan Perintah:
1. **--name GutsyDawn**: Nama file .exe yang dihasilkan.
2. **--noconsole**: Menyembunyikan layar hitam CMD saat game dijalankan.
3. **--onefile**: Membungkus semua Python, dependensi, dan script menjadi **1 file .exe saja** tanpa folder _internal yang berantakan.
4. **-p include**: Memberitahu PyInstaller agar memasukkan modul-modul lokal kita yang ada di folder include/.
5. **--add-data "..."**: Membawa file teks updater (sound_list.txt) dan package pytalk secara paksa ke dalam memori .exe karena PyInstaller tidak bisa menemukannya secara otomatis.

Setelah selesai, file GutsyDawn.exe akan muncul di dalam folder Windows/dist/. 
Kamu tinggal memindahkannya bersebelahan dengan folder dll milikmu agar gamenya bisa memuat pustaka suara dan TeamTalk dengan sempurna.
