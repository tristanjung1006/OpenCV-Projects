# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['sub.py'],
    pathex=[],
    binaries=[],
    datas=[('venv\\Lib\\site-packages\\jamo\\data\\U+11xx.json', 'jamo\\data'), ('venv\\Lib\\site-packages\\jamo\\data\\U+31xx.json', 'jamo\\data')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='sub',
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
