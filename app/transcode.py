import logging
import subprocess
import json
import time
import webvtt
import os

import app.constants
from app.sub_lang_detect.lang_detect import Sub_detect


class Content_transcode: 
    def __init__(self,file_path,filename,output_dir):
        self.file_path = file_path
        self.file_name = filename
        self.output_dir = output_dir
        self.webvtt = webvtt
    
    def list_tracks(self):
        ffprobe_cmd =  app.constants.FFPROBE_BINARY +" -hide_banner -show_streams -print_format json "+ self.file_path
        process = subprocess.Popen(ffprobe_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
        output = json.loads(process.communicate()[0])

        tracks_dic = {}
        for stream in output["streams"]:   
            if(stream['codec_type'] == 'audio'):
                index = stream['index']
                codec = stream['codec_name']
                channels = stream['channels']
                lang = stream['tags']['language']
                codec_type = stream['codec_type']
                temp_dic = {"index":index, "codec_type":codec_type, "codec_name":codec, "channels":channels, "language":lang}
                tracks_dic[index] = temp_dic

            if(stream['codec_type'] == 'video') and stream['index'] == 0:
                index = stream['index']
                codec = stream['codec_name']
                codec_type = stream['codec_type']
                temp_dic = {"index":index, "codec_type":codec_type, "codec_name":codec}
                tracks_dic[index] = temp_dic

            if (stream['codec_type'] == 'subtitle'):
                index = stream['index']
                codec = stream['codec_name']
                if 'language' in stream['tags']:
                    lang = stream['tags']['language']
                else:
                    lang = "und"
                    #lang = Sub_detect(self.file_path).lang_detect(stream)
                codec_type = stream['codec_type']
                disposition = stream['disposition']['forced']
                temp_dic = {"index":index, "codec_type":codec_type, "codec_name":codec, "language":lang, "forced":disposition}
                tracks_dic[index] = temp_dic
                
        return tracks_dic

    def transcode(self):
        job_done = {}

        aac_configs = {
            "aac": "-c:a aac -ar 48000 -b:a 192k  -ac 2 -y",
            "ac3": "-c:a ac3 -y"}
        
        h264_configs = {
            "360p": "-vf scale=-640:360:force_original_aspect_ratio=decrease,crop -vcodec libx264 -preset slow -profile:v main -level:v 3.1 -x264-params scenecut=0:open_gop=0:min-keyint=144:keyint=144 -minrate 600k -maxrate 600k -bufsize 600k -b:v 600k -y",
            "480p": "-vf scale=842:480:force_original_aspect_ratio=decrease,crop -vcodec libx264 -preset slow -profile:v main -level:v 3.2 -x264-params scenecut=0:open_gop=0:min-keyint=144:keyint=144 -minrate 1000k -maxrate 1000k -bufsize 1000k -b:v 1000k  -y",
            "720p": "-vf scale=1280:720:force_original_aspect_ratio=decrease,crop -vcodec libx264 -preset slow -profile:v high -level:v 4.1 -x264-params scenecut=0:open_gop=0:min-keyint=144:keyint=144 -maxrate 2000k -bufsize 2000k -b:v 2000k -y",
            "1080p": "-vf scale=1920:1080:force_original_aspect_ratio=decrease,crop -vcodec libx264 -preset slow -profile:v high -level:v 4.1 -x264-params scenecut=0:open_gop=0:min-keyint=144:keyint=144 -maxrate 5000k -bufsize 5000k -b:v 5000k -y"}
        
        
        for track in self.list_tracks().values():
            if track['codec_type'] == 'audio':
                for codec, audio_conf in aac_configs.items():
                    start_time = time.time()
                    ffmpeg_cmd = f"{app.constants.FFMPEG_BINARY} -i {self.file_path} -map 0:{track['index']} {audio_conf} {self.output_dir}/{track['language']}_{track['index']}_{codec}.mp4"
                    logging.info(f"Transcoding the audio track index # {track['index']} of {self.file_name} to {track['language']}_{track['index']}_{codec}.mp4")
                    process = subprocess.Popen(ffmpeg_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                    output = process.communicate()
                    logging.info(f"This transcode took {round(time.time()-start_time)}s")

                    if codec == 'aac':
                        chs = 2
                    else:
                        chs = track['channels']

                    temp_dic = {"codec_type":track['codec_type'], "codec_name":codec, "channels":chs, "language":track['language'], "output_file_path": f"{self.output_dir}/{track['language']}_{track['index']}_{codec}.mp4", 'output_dir':self.output_dir, "index":{track['index']}}
                    job_done[f"{track['index']}_{codec}"] = temp_dic
            
            if track['codec_type'] == 'video':
                for resolution, video_conf in h264_configs.items():
                    start_time = time.time()
                    ffmpeg_cmd = f"{app.constants.FFMPEG_BINARY} -i {self.file_path} -map 0:{track['index']} {video_conf} {self.output_dir}/{resolution}.mp4"
                    logging.info(f'Transcoding the video track of {self.file_name} to {resolution}.mp4')
                    process = subprocess.Popen(ffmpeg_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                    output = process.communicate()
                    
                    logging.info(f"This transcode took {round(time.time()-start_time)/60}m")
                    temp_dic = {"codec_type":track['codec_type'], "codec_name":track['codec_name'], "output_file_path": f"{self.output_dir}/{resolution}.mp4", "resolution": resolution, 'output_dir':self.output_dir}
                    job_done[f"{track['index']}_{resolution}"] = temp_dic

            if track['codec_type'] == 'subtitle':
                output_name = f"{self.output_dir}/{track['language']}_{track['index']}"
                if track['forced'] == 1:
                    output_name = f"{self.output_dir}/{track['language']}_forced_{track['index']}"

                ffmpeg_cmd = [
                    app.constants.FFMPEG_BINARY,
                    "-i", self.file_path,
                    "-map", f"0:{track['index']}",
                    "-c:s", "copy",
                    "-y", output_name+".srt"
                ]
                
                logging.info(f"Transcoding the subtitle track of {self.file_name} to {output_name}.vtt")
                
                #Task.execute(self,ffmpeg_cmd)
                process = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE ,stdout = subprocess.PIPE )
                output = process.communicate()
                
                #### Transcode srt to vtt
                webvtt = self.webvtt.from_srt(output_name+".srt").save()
                
                ### Remove srt files
                os.remove(output_name+".srt")
                
                temp_dic = {"codec_type":track['codec_type'], "codec_name":track['codec_name'], "output_file_path": output_name+".vtt",'output_dir':self.output_dir, "forced":track['forced'], "lang": track['language'], "index": track['index'] }
                job_done[f"{track['index']}"] = temp_dic

        return job_done
