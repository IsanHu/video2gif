#-*- coding:utf-8 -*-
import os
import PIL
from PIL import Image
import simplejson
import traceback
import requests

import sys
import json
import time
import datetime
from datetime import date, datetime
from Models import Video
import hashlib
## 数据库相关
from middleware import DATA_PROVIDER

reload(sys)
sys.setdefaultencoding('utf8')
basedir = os.path.abspath(os.path.dirname(__file__))
config = {}
config['UPLOAD_FOLDER'] = basedir + '/unprocessedvideos/'
config['PROCESSED_FOLDER'] = basedir + '/processedvideos/'
config['GIF_FOLDER'] = basedir + '/static/gifs/'
config['ORIGINAL_GIF_FOLDER'] = basedir + '/static/original_gifs/'
config['BOTTLENECK'] = basedir + '/bottleneck/'
config['ZIPED_GIF_FOLDER'] = basedir + '/zipedgifs/'


IGNORED_FILES = set(['.gitignore', '.DS_Store'])

def md5_name(name):
    m = hashlib.md5()
    m.update(name)
    return m.hexdigest()

def zhuanyi(original):
	chars = ['&','<','>','|','?','*','~','#',';','$','!']
	for char in chars:
		original = original.replace(char, '\\' + char)
	return original

def process_unprocessed():
    files = [f for f in os.listdir(config['UPLOAD_FOLDER']) if
                 os.path.isfile(os.path.join(config['UPLOAD_FOLDER'], f)) and f not in IGNORED_FILES]
    sql = ""
    videos = []
    for f in files:
        if f.rsplit(".", 1)[1].lower() == "mp4":
            print f
            fName = f.rsplit(".", 1)[0]
            print fName
            hash_name = md5_name(fName)
            original = config['UPLOAD_FOLDER'] + f
            hashed = config['UPLOAD_FOLDER'] + hash_name + '.mp4'
            cmd = 'mv ' + zhuanyi(original)  + ' ' + zhuanyi(hashed)
            print cmd
            os.system(cmd)

            video = Video(name=fName,
                          hash_name=hash_name,
                          extension="mp4",
                          status=0,
                          update_time=datetime.now(),
                          upload_time=datetime.now())
            videos.append(video)
            # sql += 'insert into video (name, hash_name, extension, status, update_time, upload_time) values ("%s", "%s", "mp4", 0, current_timestamp, current_timestamp);' % (fName, hash_name)

    # print sql
    result = DATA_PROVIDER.add_unprocessed_videos(videos)
    print result

process_unprocessed()








def process_processed():
    videos = []
    files = [f for f in os.listdir(config['PROCESSED_FOLDER']) if
                 os.path.isfile(os.path.join(config['PROCESSED_FOLDER'], f)) and f not in IGNORED_FILES]
    for f in files:
        if f.rsplit(".", 1)[1].lower() == "mp4":
            print f
            fName = f.rsplit(".", 1)[0]
            print fName
            hash_name = md5_name(fName)
            original = config['PROCESSED_FOLDER'] + f
            hashed = config['PROCESSED_FOLDER'] + hash_name + '.mp4'
            cmd = 'mv ' + zhuanyi(original)  + ' ' + zhuanyi(hashed)
            print cmd
            os.system(cmd)

            ## 读取caption (不需要修改caption文件名,因为用不到了)
            caption_path = os.path.join(config['BOTTLENECK'], fName + ".txt")
            print caption_path
            caption = ""
            try:
                with open(caption_path, 'r') as f:
                    caption = f.read()
            except:
                print "%s 读字幕文件失败" % fName
                return


            ## 更改zip名
            ziped_gif_file_name = fName + ".zip"
            new_ziped_gif_file_name = hash_name + ".zip"
            ziped_gif_path = os.path.join(config['ZIPED_GIF_FOLDER'], ziped_gif_file_name)
            new_ziped_gif_path = os.path.join(config['ZIPED_GIF_FOLDER'], new_ziped_gif_file_name)
            cmd = 'mv ' + zhuanyi(ziped_gif_path) + ' ' + zhuanyi(new_ziped_gif_path)
            print cmd
            os.system(cmd)


            ## 更改gif名称
            gifs_dir = config['GIF_FOLDER'] + fName
            new_gifs_dir = config['GIF_FOLDER'] + hash_name
            index = 0
            for f in sorted(os.listdir(gifs_dir)):
                if f.rsplit(".", 1)[1].lower() == "gif":
                    new_name = "%.2d.gif" % index
                    cmd = "mv " + zhuanyi(gifs_dir + '/' + f) + " " + zhuanyi(gifs_dir + '/' + new_name)
                    print cmd
                    os.system(cmd)
                    index += 1

            cmd_gif = 'mv ' + gifs_dir + " " + new_gifs_dir
            print cmd_gif
            os.system(cmd_gif)


            ## 更改original_gif名称
            ori_gifs_dir = config['ORIGINAL_GIF_FOLDER'] + fName
            new_ori_gifs_dir = config['ORIGINAL_GIF_FOLDER'] + hash_name
            index = 0
            for f in sorted(os.listdir(ori_gifs_dir)):
                if f.rsplit(".", 1)[1].lower() == "mp4":
                    new_name = "%.2d.mp4" % index
                    cmd = "mv " + zhuanyi(ori_gifs_dir + '/' + f) + " " + zhuanyi(ori_gifs_dir + '/' + new_name)
                    print cmd
                    os.system(cmd)
                    index += 1

            cmd_gif = 'mv ' + ori_gifs_dir + " " + new_ori_gifs_dir
            print cmd_gif
            os.system(cmd_gif)

            video = Video(name=fName,
                          hash_name=hash_name,
                          extension="mp4",
                          status=1,
                          update_time=datetime.now(),
                          upload_time=datetime.now(),
                          processed_time=datetime.now(),
                          split_type=0,
                          caption = caption
                          )
            videos.append(video)
    result = DATA_PROVIDER.add_unprocessed_videos(videos)
    print result

process_processed()