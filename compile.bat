@echo off
echo Mengkompilasi Gutsy Dawn...

rem Hapus build lama agar bersih
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller --clean --name GutsyDawn --noconsole --onedir --contents-directory lib -p include --add-data "include/updater/sound_list.txt;include/updater" --hidden-import pytalk gd.py

echo.
echo ========================================================
echo KOMPILASI SELESAI
echo ========================================================
set /p DEST_PATH="Paste path disini untuk memindahkan hasil kompilasi (misal: C:\Portable\Games\GutsyDawn): "

if not "%DEST_PATH%"=="" (
    if exist "%DEST_PATH%" (
        echo Menghapus lib lama di %DEST_PATH%\lib ...
        if exist "%DEST_PATH%\lib" rmdir /s /q "%DEST_PATH%\lib"
        if exist "%DEST_PATH%\GutsyDawn.exe" del /f /q "%DEST_PATH%\GutsyDawn.exe"
        
        echo Memindahkan file baru ke %DEST_PATH% ...
        xcopy /Y /E /I "dist\GutsyDawn" "%DEST_PATH%"
        if exist "whatsnew.txt" copy /Y "whatsnew.txt" "%DEST_PATH%\"
        echo Berhasil dipindahkan!
    ) else (
        echo Path tujuan tidak ditemukan.
    )
) else (
    echo Path kosong, tidak memindahkan.
)

echo Selesai!
pause