import subprocess
import os

import app.constants

class Packcontent:

    def hls_dash(self,dic):
            commands_dic = {}
            counter = 0
            for track in dic.values():
            
                if track['codec_type'] == 'audio':
                    a_config = (f"in={track['output_file_path']},stream={track['codec_type']},output={track['output_dir']}/{track['codec_type']}-{counter}-{track['language']}-{track['channels']}/init.mp4,playlist_name={track['codec_type']}-{counter}-{track['language']}-{track['channels']}/main.m3u8,hls_group_id={track['codec_type']}_{track['codec_name']},hls_name={track['language'].upper()}_CH_{track['channels']}")
                    commands_dic[counter] = a_config
                    counter += 1


                if track['codec_type'] == 'video':
                    v_config = (f"in={track['output_file_path']},stream={track['codec_type']},output={track['output_dir']}/{track['codec_name']}_{track['resolution']}/init.mp4,playlist_name={track['codec_name']}_{track['resolution']}/main.m3u8,iframe_playlist_name={track['codec_name']}_{track['resolution']}/iframe.m3u8")
                    commands_dic[counter] = v_config
                    counter += 1

                """ if track['codec_type'] == 'subtitle':
                    s_config = f"in={track['output_file_path']},stream=text,output=text/{track['index']}_{track['lang']}.vtt,playlist_name=text/{track['index']}_{track['lang']}.m3u8,hls_group_id=text,hls_name=ENGLISH'"
                    commands_dic[counter] = s_config
                    counter += 1 """

            return commands_dic

    def make_shaka_commands(self,x,file_out_path):
        command = f"{app.constants.PACKAGER_BINARY} "

        for x in self.hls_dash(x).values():
            command += str(f"{x} ")

        command += str(f"--hls_master_playlist_output {file_out_path}/index.m3u8 ")
        command += str(f" --mpd_output {file_out_path}/h264.mpd")
        command += str(f" --segment_duration 6 ")

        return command


    def pack_file(self,x,file_out_path):
        os.system(self.make_shaka_commands(x,file_out_path))

        return True


