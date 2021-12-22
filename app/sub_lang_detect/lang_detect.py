import logging
from langdetect import detect
import webvtt

from app import constants

class Sub_detect:
    
    def __init__(self, file_path):
        self.sub_file = file_path

    def temp_extract_convert(self,track):
        ffmpeg_cmd = [
            constants.FFMPEG_BINARY,
            "-i", self.sub_file,
            "-map", f"0:{track['index']}",
            "-c:s", "webvtt",
            "-y", 'temp.vtt'
            ]

    def lang_detect(self):
        logging.info("Detecting language")
        subtitle = ""
        for caption in webvtt.read(r"{str}".format(str = self.sub_file)):
            subtitle += f"{caption.text} "
    
        return detect(subtitle)


#print(Sub_detect("app\\sub_lang_detect\\und_4.vtt").lang_detect())