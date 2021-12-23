import subprocess
from iso639 import languages
import logging

import app.constants

class Packcontent:

    def __init__(self):
        self.languages = languages

    def hls_dash(self,dic):
            commands_list= []
            counter = 0
            for track in dic.values():
            
                if track['codec_type'] == 'audio':
                    a_config = [f"in={track['output_file_path']},stream={track['codec_type']},output={track['output_dir']}/{track['codec_type']}-{counter}-{track['language']}-{track['channels']}/init.mp4,playlist_name={track['codec_type']}-{counter}-{track['language']}-{track['channels']}/main.m3u8,hls_group_id={track['codec_type']}_{track['codec_name']},hls_name={track['language'].upper()}_CH_{track['channels']}"]

                    counter += 1
                    commands_list.extend(a_config)

                if track['codec_type'] == 'video':
                    v_config = [f"in={track['output_file_path']},stream={track['codec_type']},output={track['output_dir']}/{track['codec_name']}_{track['resolution']}/init.mp4,playlist_name={track['codec_name']}_{track['resolution']}/main.m3u8,iframe_playlist_name={track['codec_name']}_{track['resolution']}/iframe.m3u8"]

                    counter += 1
                    commands_list.extend(v_config)

                if track['codec_type'] == 'subtitle':
                    s_config = {f"in={track['output_file_path']},stream=text,output={track['output_dir']}/text/{track['lang']}_{track['index']}.vtt,language={languages.get(part2b=track['lang']).part1},playlist_name=text/{track['lang']}_{track['index']}.m3u8,hls_group_id=text,hls_name={track['lang']}"}
                    
                    commands_list.extend(s_config)
                    counter += 1

            return commands_list

    def make_shaka_commands(self,x,file_out_path):
        command = [
            app.constants.PACKAGER_BINARY,
            "--hls_master_playlist_output", f"{file_out_path}/index.m3u8",
            "--mpd_output", f"{file_out_path}/h264.mpd",
            "--segment_duration", "6"
            ]

        command.extend(self.hls_dash(x))

        return command

    def pack_file(self,x,file_out_path):

        shaka_cmd = self.make_shaka_commands(x,file_out_path)
        logging.info("Packaging streams HLS/DASH")
        process = subprocess.Popen(shaka_cmd, stderr=subprocess.PIPE ,stdout = subprocess.PIPE )
        output = process.communicate()
        return True

