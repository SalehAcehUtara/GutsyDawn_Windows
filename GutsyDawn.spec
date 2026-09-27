# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['gd.py'],
    pathex=['include'],
    binaries=[],
    datas=[('include/updater/sound_list.txt', 'include/updater')],
    hiddenimports=['pytalk', 'requests', 'pygame', 'accessible_output2', 'wx'],
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
    [],
    exclude_binaries=True,
    name='GutsyDawn',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory='lib',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GutsyDawn',
)