#-*- coding:utf-8 -*-
#!flask/bin/python

# Author: Ngo Duy Khanh
# Email: ngokhanhit@gmail.com
# Git repository: https://github.com/ngoduykhanh/flask-file-uploader
# This work based on jQuery-File-Upload which can be found at https://github.com/blueimp/jQuery-File-Upload/

import os
import PIL
from PIL import Image
import simplejson
import traceback

from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_bootstrap import Bootstrap
from werkzeug import secure_filename

from lib.upload_file import uploadfile, processedfile, zipedgiffile
import sys

reload(sys)
print sys.getdefaultencoding()
sys.setdefaultencoding('utf8')


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['UPLOAD_FOLDER'] = basedir + '/unprocessed videos/'
app.config['PROCESSED_FOLDER'] = basedir + '/processed videos/'
app.config['THUMBNAIL_FOLDER'] = basedir + '/unprocessed videos/thumbnail/'
app.config['GIF_FOLDER'] = basedir + '/gifs/'
app.config['ZIPED_GIF_FOLDER'] = basedir + '/zipedgifs/'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['mp4', 'zip'])
IGNORED_FILES = set(['.gitignore', '.DS_Store'])

bootstrap = Bootstrap(app)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def gen_file_name(filename):
    """
    If file was exist already, rename it and return a new name
    """

    i = 1
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        name, extension = os.path.splitext(filename)
        filename = '%s_%s%s' % (name, str(i), extension)
        i += 1

    return filename


def create_thumbnail(image):
    try:
        base_width = 80
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image))
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
        img.save(os.path.join(app.config['THUMBNAIL_FOLDER'], image))

        return True

    except:
        print traceback.format_exc()
        return False


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files['file']

        if files:
            filename = secure_filename(files.filename)
            filename = gen_file_name(filename)
            mime_type = files.content_type
            print "文件类型"
            print mime_type

            if not allowed_file(files.filename):
                result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")

            else:
                # save file to disk
                uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                files.save(uploaded_file_path)

                # create thumbnail after saving
                if mime_type.startswith('image'):
                    create_thumbnail(filename)
                
                # get file size after saving
                size = os.path.getsize(uploaded_file_path)

                # return json for js call back
                result = uploadfile(name=filename, type=mime_type, size=size)
            
            return simplejson.dumps({"files": [result.get_file()]})

    if request.method == 'GET':
        # get all file in ./data directory
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'],f)) and f not in IGNORED_FILES ]
        
        file_display = []

        for f in files:
            size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f))
            file_saved = uploadfile(name=f, size=size)
            file_info = file_saved.get_file()
            file_info['processed'] = False
            file_display.append(file_info)

        processed_files = [f for f in os.listdir(app.config['PROCESSED_FOLDER']) if os.path.isfile(os.path.join(app.config['PROCESSED_FOLDER'],f)) and f not in IGNORED_FILES ]
        for f in processed_files:
            size = os.path.getsize(os.path.join(app.config['PROCESSED_FOLDER'], f))
            file_saved = processedfile(name=f, size=size)
            file_info = file_saved.get_file()
            file_info['processed'] = True

            file_name=os.path.splitext(os.path.split(f)[1])[0]
            ziped_gif_file_name = file_name + ".zip"
            ziped_gif_path = os.path.join(app.config['ZIPED_GIF_FOLDER'], ziped_gif_file_name)
            print ziped_gif_path
            if os.path.isfile(ziped_gif_path):
                ziped_gif_size = os.path.getsize(ziped_gif_path)
                ziped_gif_saved = zipedgiffile(name=ziped_gif_file_name, size=ziped_gif_size)
                file_info['ziped_gif_info'] = ziped_gif_saved.get_file()

            file_display.append(file_info)

        return simplejson.dumps({"files": file_display})

    return redirect(url_for('index'))


@app.route("/deleteunprocessed/<string:filename>", methods=['DELETE'])
def deleteunprocessed(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return simplejson.dumps({filename: 'True'})
        except:
            return simplejson.dumps({filename: 'False'})

@app.route("/deleteprocessed/<string:filename>", methods=['DELETE'])
def deleteprocessed(filename):
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return simplejson.dumps({filename: 'True'})
        except:
            return simplejson.dumps({filename: 'False'})

@app.route("/deletezipedgif/<string:filename>", methods=['DELETE'])
def deletezipedgif(filename):
    file_path = os.path.join(app.config['ZIPED_GIF_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return simplejson.dumps({filename: 'True'})
        except:
            return simplejson.dumps({filename: 'False'})


# serve static files
@app.route("/thumbnail/<string:filename>", methods=['GET'])
def get_thumbnail(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename=filename)


@app.route("/processed/<string:filename>", methods=['GET'])
def get_processed_file(filename):
    return send_from_directory(os.path.join(app.config['PROCESSED_FOLDER']), filename=filename)

@app.route("/unprocessed/<string:filename>", methods=['GET'])
def get_unprocessed_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename=filename)

@app.route("/zipedgif/<string:filename>", methods=['GET'])
def get_ziped_gif_file(filename):
    return send_from_directory(os.path.join(app.config['ZIPED_GIF_FOLDER']), filename=filename)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0 ', debug=True)
