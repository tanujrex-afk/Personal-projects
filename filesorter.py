import os
import shutil
current_dir=os.getcwd()
print(f"Cleaning up the file folder:{current_dir}")
for filename in os.listdir(current_dir):
    if os.path.isdir(filename) or filename=="filesorter.py":
        continue
    file_ext=os.path.splitext(filename)[1].lower()
    if file_ext in['.jpg','.jpeg','.png','.gif','.heic','.avif']:
        target_folder="Images"
    elif file_ext in ['.pdf','.docx','.doc','.txt']:
        target_folder="Documents"
    elif file_ext in ['.mp3','.mp4','.wav','.aiff','.flac','.wma','.ogg','.dts','.mkv','.m4v']:
        target_folder="Audio"
    elif file_ext in['.zip','.zipx','.rar','.7z']:
        target_folder="Archives"
    else:
        target_folder="Others"
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    shutil.move(filename,os.path.join(target_folder,filename))
    print(f"Moved:{filename}->{target_folder}/")
print("Folder cleanup complete")
        