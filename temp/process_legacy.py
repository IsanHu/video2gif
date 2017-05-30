import os
import PIL
from PIL import Image
import simplejson
import traceback
import requests

import sys
import json
import time

import hashlib
## 数据库相关
from middleware import video_by_name

reload(sys)
sys.setdefaultencoding('utf8')
basedir = os.path.abspath(os.path.dirname(__file__)) + '/..'
config = {}
config['UPLOAD_FOLDER'] = basedir + '/unprocessedvideos/'
config['PROCESSED_FOLDER'] = basedir + '/processedvideos/'
config['GIF_FOLDER'] = basedir + '/static/gifs/'
config['ORIGINAL_GIF_FOLDER'] = basedir + '/static/original_gifs/'
config['BOTTLENECK'] = basedir + '/bottleneck/'
config['ZIPED_GIF_FOLDER'] = basedir + '/zipedgifs/'


IGNORED_FILES = set(['.gitignore', '.DS_Store'])

def hash_name(name):
    m = hashlib.md5()
    m.update(name)
    return m.hexdigest()

def zhuanyi(original):
	chars = ['&','<','>','|','?','*','~','#',';','$','!']
	for char in chars:
		original = original.replace(char, '\\' + char)
	return original


files = [f for f in os.listdir(config['UPLOAD_FOLDER']) if
             os.path.isfile(os.path.join(config['UPLOAD_FOLDER'], f)) and f not in IGNORED_FILES]
for f in files:
    if f.rsplit(".", 1)[1].lower() == "mp4":
        fName = f.rsplit(".", 1)[0]
        hash_name = hash_name(fName)
        original = config['UPLOAD_FOLDER'] + f
        hashed = config['UPLOAD_FOLDER'] + hash_name + '.mp4'
        cmd = 'mv ' + zhuanyi(original)  + ' ' + hashed
        print cmd










    # size = round(float(os.path.getsize(os.path.join(config['UPLOAD_FOLDER'], f))) / 1024.0 / 1024.0, 2)
    # file_saved = uploadfile(name=f, size=size)
    # file_info = file_saved.get_file()
    # file_name = os.path.splitext(os.path.split(f)[1])[0]
    # status, op = processVideos.get_file_status_info(file_name)
    # file_info['status'] = status
    # if op != "":
    #     file_info['op'] = op
    # unprocessed_files.append(file_info)


    # processed_files = []
    # processed = [f for f in os.listdir(config['PROCESSED_FOLDER']) if
    #              os.path.isfile(os.path.join(config['PROCESSED_FOLDER'], f)) and f not in IGNORED_FILES]
    # processed.sort(processedSort)
    # for f in processed:
    #     size = round(float(os.path.getsize(os.path.join(config['PROCESSED_FOLDER'], f))) / 1024.0 / 1024.0, 2)
    #     file_saved = processedfile(name=f, size=size)
    #     file_info = file_saved.get_file()
    #
    #     file_name = os.path.splitext(os.path.split(f)[1])[0]
    #     ziped_gif_file_name = file_name + ".zip"
    #     ziped_gif_path = os.path.join(config['ZIPED_GIF_FOLDER'], ziped_gif_file_name)
    #
    #     if os.path.isfile(ziped_gif_path):
    #         ziped_gif_size = round(float(os.path.getsize(ziped_gif_path)) / 1024.0 / 1024.0, 2)
    #         ziped_gif_saved = zipedgiffile(name=ziped_gif_file_name, size=ziped_gif_size)
    #         file_info['ziped_gif_info'] = ziped_gif_saved.get_file()
    #
    #     # gif图片目录
    #     gifs_dir = config['GIF_FOLDER'] + file_name
    #     gif_count = 0
    #     if os.path.isdir(gifs_dir):
    #         file_info['gifs_dir'] = "gifs/%s" % file_name
    #         for f in os.listdir(gifs_dir):
    #             if f.rsplit(".", 1)[1].lower() == "gif":
    #                 gif_count += 1
    #     file_info['gif_count'] = gif_count
    #
    #     processed_files.append(file_info)
    # return processed_files, unprocessed_files