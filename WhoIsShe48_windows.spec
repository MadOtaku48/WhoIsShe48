# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect data
datas = [
    ('Groups_clean', 'Groups'),
    ('fonts', 'fonts'),
    ('.insightface', '.insightface'),
]

# Add insightface data
datas += collect_data_files('insightface')

a = Analysis(
    ['WhoIsShe48.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'sklearn.metrics.pairwise',
        'insightface',
        'insightface.app',
        'insightface.model_zoo',
        'onnx',
        'onnxruntime',
        'PIL._tkinter_finder',
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=['runtime_hook_insightface_windows.py'],
    excludes=[
        'pandas',
        'seaborn',
        'plotly',
        'bokeh',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'torch',
        'tensorflow',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WhoIsShe48',
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
    icon='WhoIsShe48.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WhoIsShe48'
)
