import os

def save_audio(file_path, file_content):
    with open(file_path, 'wb') as new_file:
        new_file.write(file_content)

def delete_audio(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
