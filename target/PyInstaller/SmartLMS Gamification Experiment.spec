# -*- mode: python -*-

block_cipher = None


a = Analysis(['C:\\Users\\Dinar\\Desktop\\GamifyHSE\\src\\main\\python\\main.py'],
             pathex=['C:\\Users\\Dinar\\Desktop\\GamifyHSE\\target\\PyInstaller'],
             binaries=[],
             datas=[],
             hiddenimports=['PySide2.QtXml'],
             hookspath=['c:\\users\\dinar\\appdata\\local\\programs\\python\\python36\\lib\\site-packages\\fbs\\freeze\\hooks'],
             runtime_hooks=['C:\\Users\\Dinar\\Desktop\\GamifyHSE\\target\\PyInstaller\\fbs_pyinstaller_hook.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='SmartLMS Gamification Experiment',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False , version='C:\\Users\\Dinar\\Desktop\\GamifyHSE\\target\\PyInstaller\\version_info.py', icon='C:\\Users\\Dinar\\Desktop\\GamifyHSE\\src\\main\\icons\\Icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='SmartLMS Gamification Experiment')
