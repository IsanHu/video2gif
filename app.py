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
import requests

from lib.upload_file import uploadfile, processedfile, zipedgiffile
import sys
import processVideos
import hardwareInfo
import json
import time
reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = basedir + '/unprocessedvideos/'
app.config['PROCESSED_FOLDER'] = basedir + '/processedvideos/'
app.config['THUMBNAIL_FOLDER'] = basedir + '/unprocessedvideos/thumbnail/'
app.config['GIF_FOLDER'] = basedir + '/static/gifs/'
app.config['ORIGINAL_GIF_FOLDER'] = basedir + '/static/original_gifs/'
app.config['BOTTLENECK'] = basedir + '/bottleneck/'
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

@app.route("/hInfo", methods=['GET'])
def hInfo():
    # //获取硬件信息
    free_disk = "磁盘可用空间：%.2fG" % hardwareInfo.free_disk("/home/3isan333")
    # gpu_info = hardwareInfo.gpu_info()
    hinfo = {"free_disk": free_disk}
    return simplejson.dumps(hinfo)

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files['file']

        if files:
            filename = files.filename.encode('utf-8')
            filename = gen_file_name(filename)
            print filename
            mime_type = files.content_type
            print "文件类型"
            print mime_type

            if not allowed_file(files.filename):
                result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="请上传MP4文件")

            else:
                # save file to disk
                uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                files.save(uploaded_file_path)
                print "saved path:"
                print uploaded_file_path
                
                # get file size after saving
                size = os.path.getsize(uploaded_file_path)

                # return json for js call back
                result = uploadfile(name=filename, type=mime_type, size=size)
            
            return simplejson.dumps({"files": [result.get_file()]})

    if request.method == 'GET':
        # get all file in ./data directory
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'],f)) and f not in IGNORED_FILES ]
        
        file_display = []

        for f in sorted(files):
            size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f))
            file_saved = uploadfile(name=f, size=size)
            file_info = file_saved.get_file()
            file_info['processed'] = False
            file_display.append(file_info)

        processed_files = [f for f in os.listdir(app.config['PROCESSED_FOLDER']) if os.path.isfile(os.path.join(app.config['PROCESSED_FOLDER'],f)) and f not in IGNORED_FILES ]
        for f in sorted(processed_files):
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

@app.route("/gifs/<string:filename>", methods=['GET'])
def gifs(filename):
    gifs_dir = app.config['GIF_FOLDER'] + filename
    gifs = []
    path = "/static/gifs/%s" % filename + "/"
    original_gif_path = "/static/original_gifs/%s" % filename + "/"
    info_path = os.path.join(app.config['BOTTLENECK'], filename + '.txt')
    info = {}
    try:
        with open(info_path, 'r') as f:
            info = json.loads(f.read())
    except:
        return render_template('upload_gif.html', gifs="", result=0)
    index = 0
    tags = json.loads(info['tags'])
    if info.has_key('gif_caption'):
        gif_caption = info['gif_caption']
        if os.path.isdir(gifs_dir):
            # 获取字幕分词
            captions = []
            for ca in gif_caption:
                captions.append(ca['caption'])

            apiUrl = "http://120.27.214.63:8080/open-api/word/segments"
            headers = {'Content-Type': 'application/json;charset:UTF-8'}
            print '分词访问前'
            response = requests.post(url=apiUrl, data=json.dumps(captions), headers=headers)
            print '分词请求发送'
            result = json.loads(response.content)
            if result['error_code'] == 0:
                segments_array = result['data']


            for f in sorted(os.listdir(gifs_dir)):
                if f.rsplit(".", 1)[1].lower() == "gif":
                    size = round(float(os.path.getsize(os.path.join(basedir + path, f))) / 1024.0, 2)
                    full_size = round(float(os.path.getsize(os.path.join(basedir + original_gif_path, f))) / 1024.0 / 1024.0, 2)
                    if index < len(segments_array):
                        gifs.append({'url': path + f, 'name':f, 'size':size, 'full_size':full_size, 'original_gif_url':original_gif_path + f, 'tags':tags, 'caption': gif_caption[index]['caption'], 'segments': segments_array[index]})
                    else:
                        gifs.append({'url': path + f, 'name':f, 'size':size, 'full_size':full_size, 'original_gif_url':original_gif_path + f, 'tags': tags, 'caption': gif_caption[index]['caption'],
                                     'segments': ''})
                    index += 1
    else:
        if os.path.isdir(gifs_dir):
            for f in os.listdir(gifs_dir):
                if f.rsplit(".", 1)[1].lower() == "gif":
                    size = round(float(os.path.getsize(os.path.join(basedir + path, f))) / 1024.0, 2)
                    full_size = round(float(os.path.getsize(os.path.join(basedir + original_gif_path, f))) / 1024.0 / 1024.0, 2)
                    gifs.append({'url': path + f, 'name':f, 'size':size, 'full_size':full_size, 'original_gif_url':original_gif_path + f, 'tags': tags, 'caption': '', 'segments': ''})
    gifs_str = json.dumps(gifs)
    return render_template('upload_gif.html', gifs=gifs_str, result=1)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', tab='upload')

@app.route('/alldata', methods=['GET', 'POST'])
def alldata():
    time.sleep(0.01)
    return render_template('alldata.html', tab='process')

@app.route('/getalldata', methods=['GET', 'POST'])
def getalldata():
    time.sleep(0.01)
    processed_files, unprocessed_files = did_get_all_data()
    return simplejson.dumps({"processed_files": processed_files, 'unprocessed_files':unprocessed_files})

def did_get_all_data():
    # get all file in ./data directory
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if
             os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f)) and f not in IGNORED_FILES]
    file_display = []
    unprocessed_files = []
    for f in sorted(files):
        size = round(float(os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f))) / 1024.0 / 1024.0, 2)
        file_saved = uploadfile(name=f, size=size)
        file_info = file_saved.get_file()
        file_name = os.path.splitext(os.path.split(f)[1])[0]
        status, op = processVideos.get_file_status_info(file_name)
        file_info['status'] = status
        if op != "":
            file_info['op'] = op
        unprocessed_files.append(file_info)

    processed_files = []
    processed = [f for f in os.listdir(app.config['PROCESSED_FOLDER']) if
                 os.path.isfile(os.path.join(app.config['PROCESSED_FOLDER'], f)) and f not in IGNORED_FILES]
    for f in sorted(processed):
        size = round(float(os.path.getsize(os.path.join(app.config['PROCESSED_FOLDER'], f))) / 1024.0 / 1024.0, 2)
        file_saved = processedfile(name=f, size=size)
        file_info = file_saved.get_file()

        file_name = os.path.splitext(os.path.split(f)[1])[0]
        ziped_gif_file_name = file_name + ".zip"
        ziped_gif_path = os.path.join(app.config['ZIPED_GIF_FOLDER'], ziped_gif_file_name)

        if os.path.isfile(ziped_gif_path):
            ziped_gif_size = round(float(os.path.getsize(ziped_gif_path)) / 1024.0 / 1024.0, 2)
            ziped_gif_saved = zipedgiffile(name=ziped_gif_file_name, size=ziped_gif_size)
            file_info['ziped_gif_info'] = ziped_gif_saved.get_file()

        # gif图片目录
        gifs_dir = app.config['GIF_FOLDER'] + file_name
        gif_count = 0
        if os.path.isdir(gifs_dir):
            file_info['gifs_dir'] = "gifs/%s" % file_name
            for f in os.listdir(gifs_dir):
                if f.rsplit(".", 1)[1].lower() == "gif":
                    gif_count += 1
        file_info['gif_count'] = gif_count

        processed_files.append(file_info)
    return processed_files, unprocessed_files

@app.route("/addVideoToProcess", methods=['POST'])
def addVideoToProcess():
    params = request.form
    videoName = params['videoName'].encode('utf-8')
    height = int(params['height'])
    tags = params['tags']
    captionChecked = params['captionChecked']
    processVideos.add_video_to_process(videoName, height, tags, captionChecked)
    processed_files, unprocessed_files = did_get_all_data()
    return simplejson.dumps({"processed_files": processed_files, 'unprocessed_files': unprocessed_files})


processVideos.start_all_queues()

if __name__ == '__main__':
    app.run(host='0.0.0.0')