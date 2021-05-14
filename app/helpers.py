from app import app
from werkzeug.utils import secure_filename
import os
import datetime
import subprocess


def create_saving_directory(type_courrier):
    today = datetime.datetime.now().date()
    directory = type_courrier + "/Courriers_{}".format(today.strftime('%d-%m-%Y'))
    if not os.path.exists(app.config['UPLOAD_PATH'] + '/' + directory):
        os.mkdir(app.config['UPLOAD_PATH'] + '/' + directory)
    return directory


def handle_uploaded_files(file, directory=''):
    filename = secure_filename(file.filename)
    thumbnail = None
    if filename != '':
        # fichier_ext = os.path.splitext(fichier_nom)[1]
        file.save(os.path.join(app.config['UPLOAD_PATH'], directory, filename))
        thumbnail = generate_thumbnail(filename, directory)
    return filename, thumbnail


def generate_thumbnail(file, directory):
    file_path = os.path.join(app.config['UPLOAD_PATH'], directory, file + '[0]')
    thumbnail_name = os.path.splitext(file)[0] + '.jpeg'
    thumbnail_path = os.path.join(app.config['UPLOAD_PATH'], directory, thumbnail_name)
    params = ['convert', file_path, thumbnail_path]
    subprocess.check_call(params)
    return thumbnail_name
