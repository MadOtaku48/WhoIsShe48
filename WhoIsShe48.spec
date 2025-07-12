# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
import platform

block_cipher = None

# Collect data
datas = [
    ('Groups', 'Groups'),
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
        'sklearn',
        'sklearn.metrics.pairwise',
        'scipy',
        'scipy.spatial',
        'scipy.spatial.distance',
        'insightface',
        'insightface.app',
        'insightface.model_zoo',
        'onnx',
        'onnxruntime',
        'PIL._tkinter_finder',
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=['runtime_hook_insightface.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if platform.system() == 'Darwin':  # macOS
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='WhoIsShe48',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=True,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='WhoIsShe48.icns'
    )
    
    app = BUNDLE(
        exe,
        name='WhoIsShe48.app',
        icon='WhoIsShe48.icns',
        bundle_identifier='com.akb48.whoishe48',
        info_plist={
            'CFBundleName': 'WhoIsShe48',
            'CFBundleDisplayName': 'WhoIsShe48',
            'CFBundleIdentifier': 'com.akb48.whoishe48',
            'CFBundleVersion': '1.0.1',
            'CFBundleShortVersionString': '1.0.1',
            'LSMinimumSystemVersion': '10.13.0',
            'NSHighResolutionCapable': True,
        },
    )
else:  # Windows
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='WhoIsShe48',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='WhoIsShe48.ico'
    )