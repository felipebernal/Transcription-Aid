# -*- mode: python -*-

block_cipher = None

added_files = [
         ('C:/Anaconda3/Lib/site-packages/docx/templates/default.docx', 'docx/templates/' ),
         ('ffmpeg/presets/*','ffmpeg/presets/'),
         ('ffmpeg/licenses/*','ffmpeg/licenses/'),
         ]

added_binaries=[('ffmpeg/bin/ffmpeg.exe', 'ffmpeg/bin/' ),
                #('ffmpeg/bin/ffplay.exe', 'ffmpeg/bin/' ),
                #('ffmpeg/bin/ffprobe.exe', 'ffmpeg/bin/' )
                ]
a = Analysis(['LoadTrnascribeTranscriptionCorrect.py'],
             pathex=['C:\\Users\\felipe bernal arango\\Desktop\\FinalversionProgram'],
             binaries=added_binaries,
             datas=added_files,
             hiddenimports=['six','packaging','packaging.version','packaging.specifiers','packaging.requirements','packaging.utils','packaging.markers'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Transcription-Aid',
          debug=False,
          strip=False,
          upx=True,
          console=True , icon='crow.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Transcription-Aid')
