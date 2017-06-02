#-*- coding:utf-8 -*-
import os
import PIL
from PIL import Image
import simplejson
import traceback
import requests
import random
import sys
import json
import time
from time import sleep
import datetime
from datetime import date, datetime
from Models import Video
import hashlib
import json
## 数据库相关
from middleware import DATA_PROVIDER

from moviepy.editor import VideoFileClip, AudioFileClip
import threading
from threading import Timer
reload(sys)
sys.setdefaultencoding('utf8')




def start_thread_loop():
    t = Timer(20, start_thread_loop)
    t.start()
    test_session_per_thread(DATA_PROVIDER.caption_loop_queue_session)


def test_session_per_thread(session):
    update_videos = []
    videos = DATA_PROVIDER.get_video_by_hash_name(session, "ad0234829205b9033196ba818f7a872b")
    print videos
    for vi in videos:
        print vi
        if vi.caption is None or vi.caption == "":
            continue
        caption = json.loads(vi.caption)


        tags = caption['tags']
        print tags
        is_chinese = 0
        if caption.has_key('is_chinese') and caption['is_chinese'] == "false":
            is_chinese = 1
        print is_chinese

        xunfei_id = ""
        if caption.has_key('xunfei_id') and caption['xunfei_id'] != "":
            xunfei_id = caption['xunfei_id']

        vi.tag = tags
        vi.status = random.randint(1, 9)
        print vi.status
        vi.is_chinese = is_chinese
        vi.xunfei_id = xunfei_id
        update_videos.append(vi)
    result = DATA_PROVIDER.add_or_update_videos(session, update_videos)
    print result

def test_local_session():
    sessions = [DATA_PROVIDER.main_queue_session, DATA_PROVIDER.upload_queue_session, DATA_PROVIDER.main_queue_session,
                DATA_PROVIDER.caption_queue_session]
    update_videos = []
    index = random.randint(0, 3)
    # videos = DATA_PROVIDER.all_videos(currentsession=sessions[index])
    videos = DATA_PROVIDER.get_video_by_hash_name(DATA_PROVIDER.main_queue_session, "ad0234829205b9033196ba818f7a872b")
    print videos
    for vi in videos:

        if vi.caption is None or vi.caption == "":
            continue
        caption = json.loads(vi.caption)

        tags = caption['tags']
        print tags
        is_chinese = 0
        if caption.has_key('is_chinese') and caption['is_chinese'] == "false":
            is_chinese = 1
        print is_chinese

        xunfei_id = ""
        if caption.has_key('xunfei_id') and caption['xunfei_id'] != "":
            xunfei_id = caption['xunfei_id']

        vi.tag = tags
        vi.status = 5
        vi.is_chinese = is_chinese
        vi.xunfei_id = xunfei_id
        update_videos.append(vi)
    index = random.randint(0, 3)
    result = DATA_PROVIDER.add_or_update_videos(sessions[index], update_videos)
    print result

start_thread_loop()


while(True):
    t = random.randint(13, 32)
    sleep(t)
    test_session_per_thread(DATA_PROVIDER.main_queue_session)