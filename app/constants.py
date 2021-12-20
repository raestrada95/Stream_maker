import os
import sys 

BINARIES_FOLDER = 'binaries'


if sys.platform == "win32":
    FFMPEG_BINARY = os.path.join(BINARIES_FOLDER, 'ffmpeg.exe')
    FFPROBE_BINARY = os.path.join(BINARIES_FOLDER, 'ffprobe.exe')
    PACKAGER_BINARY = os.path.join(BINARIES_FOLDER, 'packager-win-x64.exe')
else:
    FFMPEG_BINARY = 'ffmpeg'
    FFPROBE_BINARY = 'ffprobe'
    PACKAGER_BINARY = os.path.join(BINARIES_FOLDER, 'packager-linux-x64')


