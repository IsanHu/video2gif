# -*- coding:utf-8 -*-
# !flask/bin/python

# Author: Ngo Duy Khanh
# Email: ngokhanhit@gmail.com
# Git repository: https://github.com/ngoduykhanh/flask-file-uploader
# This work based on jQuery-File-Upload which can be found at https://github.com/blueimp/jQuery-File-Upload/
import global_config
import os
import PIL
from PIL import Image
import simplejson
import traceback

from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_bootstrap import Bootstrap
from werkzeug import secure_filename
import requests

import sys
from sys import argv
import process
import hardwareInfo
import json
import time
from time import sleep
import hashlib
from moviepy.editor import VideoFileClip
from flask import jsonify
from datetime import datetime
## 数据库相关

from data_service import DATA_PROVIDER

import process

from Models import Video
from datetime import datetime

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


def gen_file_name(fName):
    """
    If file was exist already, rename it and return a new name
    """
    name = fName
    videos = DATA_PROVIDER.all_videos()
    for vi in videos:
        if vi.name == fName:
            name = name + "_1"
            break
    print "上传的文件的名称: %s" % name
    return name



@app.route("/hInfo", methods=['GET'])
def hInfo():
    # //获取硬件信息
    free_disk = "磁盘可用空间：%.2fG" % hardwareInfo.free_disk("/root")
    # gpu_info = hardwareInfo.gpu_info()
    hinfo = {"free_disk": free_disk}
    return simplejson.dumps(hinfo)



@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', tab='upload')

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files['file']
        upload_info_dic= {}
        if files:
            filename = files.filename.encode('utf-8')
            upload_info_dic['name'] = filename
            mime_type = files.content_type
            upload_info_dic['type'] = mime_type
            upload_info_dic['upload_time'] = str(datetime.now())
            upload_info_dic['message'] = ""
            if not allowed_file(filename):
                upload_info_dic['error'] = "请上传MP4文件"
                upload_info_dic['size'] = ""
            else:
                # save file to disk
                fName = filename.rsplit('.', 1)[0]
                extension = filename.rsplit('.', 1)[1]
                fName = gen_file_name(fName)
                hash_name = md5_name(fName)

                uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], hash_name + "." + extension)
                try:
                    files.save(uploaded_file_path)
                    video_clip = VideoFileClip(uploaded_file_path)
                    duration = sec_2_time(video_clip.duration)
                    dimention = "%d*%d" % (video_clip.size[0], video_clip.size[1])
                    size = round(float(os.path.getsize(uploaded_file_path)) / 1024.0 / 1024.0, 2)
                    size_str = "%.2f M" % size
                    fps = video_clip.fps
                    info = {'duration': duration, 'dimention': dimention, 'size': size_str, 'fps':fps}
                    info_str = json.dumps(info)
                    upload_info_dic['size'] = size_str
                    upload_info_dic['message'] = "上传成功"
                except (Exception) as e:
                    upload_info_dic['size'] = ""
                    upload_info_dic['error'] = e.message
                    print "%s上传文件完成后,处理失败" % filename
                    print e.message
                    return simplejson.dumps({"files": [upload_info_dic]})

                print "saved path:"
                print uploaded_file_path

                video = Video(name=fName,
                              hash_name=hash_name,
                              extension="mp4",
                              status=0,
                              update_time=datetime.now(),
                              upload_time=datetime.now(),
                              video_info=info_str)
                ## 保存成功后, 在数据库中添加记录
                DATA_PROVIDER.add_unprocessed_videos([video])

                # return json for js call back
        return simplejson.dumps({"files": [upload_info_dic]})

    if request.method == 'GET':
        return simplejson.dumps({"files": []})

    return redirect(url_for('index'))

@app.route('/alldata', methods=['GET', 'POST'])
def alldata():
    videos, page_indexs, current_page = DATA_PROVIDER.videos_at_page(1, serialize=True)
    return render_template('alldata.html', videos=json.dumps(videos), page_indexs=page_indexs, current_page = current_page, tab='process')

@app.route("/videos", methods=['POST'])
def get_videos_at_page():
    params = request.form
    key = params['key'].encode('utf-8')
    page = int(params['page'])
    videos, page_indexs, current_page = DATA_PROVIDER.videos_at_page(page, key=key, serialize=True)
    return simplejson.dumps({"videos":videos, "page_indexs":page_indexs, "current_page": current_page})


## 查看视频生成的gif
@app.route("/gifs/<string:filename>", methods=['GET'])
def gifs(filename):
    sleep(0.01)
    videos = DATA_PROVIDER.get_video_by_hash_name(filename)
    if len(videos) == 0:
        return {'result': 1001, "error_message": "该视频丢失"}
    vi = videos[0]

    gifs_dir = app.config['GIF_FOLDER'] + filename
    gifs = []
    path = "/static/gifs/%s" % filename + "/"
    original_gif_path = "/static/original_gifs/%s" % filename + "/"

    tags = json.loads(vi.tag)
    generare_caption = (vi.split_type == 0 and vi.is_chinese == 0)
    if generare_caption:
        print "include caption"
        info = json.loads(vi.caption)
        gif_caption = info['gif_caption']
        if os.path.isdir(gifs_dir):
            # 获取字幕分词
            captions = []
            for ca in gif_caption:
                captions.append(ca['caption'])

            segments_array = []
            try:
                apiUrl = "http://120.27.214.63:8080/open-api/word/segments"
                headers = {'Content-Type': 'application/json;charset:UTF-8'}
                print '分词访问前'
                response = requests.post(url=apiUrl, data=json.dumps(captions), headers=headers)
                print '分词请求发送'
                result = json.loads(response.content)
                if result['error_code'] == 0:
                    segments_array = result['data']
            except:
                print '分词失败'

            index = 0
            for f in sorted(os.listdir(gifs_dir)):
                if f.rsplit(".", 1)[1].lower() == "gif":
                    fName = f.rsplit(".", 1)[0] + ".mp4"
                    size = round(float(os.path.getsize(os.path.join(basedir + path, f))) / 1024.0, 2)
                    full_size = 0
                    original_mp4_path = os.path.join(basedir + original_gif_path, fName)
                    if os.path.isfile(original_mp4_path):
                        full_size = round(float(os.path.getsize(original_mp4_path)) / 1024.0 / 1024.0, 2)
                    if index < len(segments_array):
                        gifs.append(
                            {'url': path + f, 'name': fName, 'index': index, 'size': size, 'full_size': full_size,
                             'original_gif_url': original_gif_path + fName, 'tags': tags,
                             'caption': gif_caption[index]['caption'], 'segments': segments_array[index]})
                    else:
                        gifs.append(
                            {'url': path + f, 'name': fName, 'index': index, 'size': size, 'full_size': full_size,
                             'original_gif_url': original_gif_path + fName, 'tags': tags,
                             'caption': gif_caption[index]['caption'],
                             'segments': ''})
                    index += 1
    else:
        if os.path.isdir(gifs_dir):
            index = 0
            for f in sorted(os.listdir(gifs_dir)):
                if f.rsplit(".", 1)[1].lower() == "gif":
                    fName = f.rsplit(".", 1)[0] + ".mp4"
                    size = round(float(os.path.getsize(os.path.join(basedir + path, f))) / 1024.0, 2)
                    full_size = 0
                    original_mp4_path = os.path.join(basedir + original_gif_path, fName)
                    if os.path.isfile(original_mp4_path):
                        full_size = round(float(os.path.getsize(original_mp4_path)) / 1024.0 / 1024.0, 2)
                    gifs.append({'url': path + f, 'name': fName, 'index': index, 'size': size, 'full_size': full_size,
                                 'original_gif_url': original_gif_path + fName, 'tags': tags, 'caption': '',
                                 'segments': ''})
                    index = index + 1
    gifs_str = json.dumps(gifs)
    return render_template('upload_gif.html', gifs=gifs_str, result=1)


## 删除


## 下载zip
@app.route("/zipedgif/<string:filename>", methods=['GET'])
def get_ziped_gif_file(filename):
    return send_from_directory(os.path.join(app.config['ZIPED_GIF_FOLDER']), filename=filename)




@app.route("/addVideoToProcess", methods=['POST'])
def addVideoToProcess():
    params = request.form
    videoName = params['videoName'].encode('utf-8')
    height = int(params['height'])
    tags = params['tags']
    captionChecked = params['captionChecked']
    isChinese = params['isChinese']
    duration = int(params['duration'])
    result = process.add_video_to_process(videoName, height, tags, captionChecked, isChinese, duration)
    return simplejson.dumps(result)


## helper
def md5_name(name):
    m = hashlib.md5()
    m.update(name)
    return m.hexdigest()


def sec_2_time(sec):
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return ("%02d:%02d:%02d" % (h, m, s))


print "app.py 脚本"
process.start_all_queues()

if __name__ == '__main__':
    global_config.config['port'] = argv[1]
    app.run(host='0.0.0.0', port=global_config.config['port'])
