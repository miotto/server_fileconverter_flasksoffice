import os
from config import config
from werkzeug.utils import secure_filename

def uploads_url(path):
    return path.replace(config['uploads_dir'], '/upload')


def save_to(folder, file):
    os.makedirs(folder, exist_ok=True)
    save_path = os.path.join(folder, secure_filename(file.filename))
    file.save(save_path)
    return save_path
