from glob import glob
import logging
import os

from app.transcode import Content_transcode
from app.pakager import Packcontent

logging.basicConfig(level=logging.DEBUG)

#This function will load the files to be transcoded
def load_files_to_process():
    files = glob("works/*.mkv")
    logging.info(f'Files to be processed{files}')
    return files

def create_dir_if_not_exists(file_name):
    if os.path.exists(f'output/{file_name}') == False:
        os.mkdir(f'output/{file_name}')
    return file_name

def clean_dir(file_out_path):
    dir_to_check = file_out_path
    files_to_delete = glob(f"{dir_to_check}/*.mp4")
    logging.info("Deleting mp4 files")
    
    for file in files_to_delete:
        os.remove(file)
    

def main():
    
    for file in load_files_to_process():
        
        origin_file_path = file
        file_name = os.path.basename(file)[0:-4]
        file_out_path = f'output/{create_dir_if_not_exists(file_name)}'
        job = Content_transcode(origin_file_path,file_name,file_out_path).transcode()
        pack_content = Packcontent().pack_file(job,file_out_path)
        if pack_content:
            clean_dir(file_out_path)



if __name__ == "__main__":
    main()

