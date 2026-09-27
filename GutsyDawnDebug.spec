# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gd.py'],
    pathex=['include'],
    binaries=[],
    datas=[('include/updater/sound_list.txt', 'include/updater'), ('D:/File/Bot/TeamTalk Bot/teamtalk-telegram-sender/.venv/Lib/site-packages/pytalk', 'pytalk')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GutsyDawnDebug',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
