# -*- coding:utf-8 -*-
# Import the video2gif package
import global_config

if not global_config.config['is_local']:
    import video2gif
'''
Compile the score function
On the GPU, the network will be using cuDNN layer implementations available in the Lasagne master

If the device is CPU, it will use the CPU version that requires my Lasagne fork with added 3D convolution and pooling.
You can get it from https://github.com/gyglim/Lasagne

'''
import Queue
import threading
from threading import Timer

if not global_config.config['is_local']:
    score_function = video2gif.get_prediction_function()

from IPython.display import Image, display
import os
from moviepy.editor import VideoFileClip, AudioFileClip
import sys
import json
import time
from time import sleep
from datetime import date, datetime
from middleware import DATA_PROVIDER
from Models import Video
basedir = os.path.abspath(os.path.dirname(__file__))
config = {}
config['UPLOAD_FOLDER'] = basedir + '/unprocessedvideos/'
config['PROCESSED_FOLDER'] = basedir + '/processedvideos/'
config['THUMBNAIL_FOLDER'] = basedir + '/unprocessedvideos/thumbnail/'
config['GIF_FOLDER'] = basedir + '/static/gifs/'
config['ORIGINAL_GIF_FOLDER'] = basedir + '/static/original_gifs/'
config['BOTTLENECK'] = basedir + '/bottleneck/'
config['ZIPED_GIF_FOLDER'] = basedir + '/zipedgifs/'

config['XUNFEI_JAR'] = basedir + '/Lfasr.jar'
config['XUNFEI_APPID'] = '591c2c4d'
config['XUNFEI_KEY'] = 'c238e91e995ae7b31d313caba8ce28a5'

# 排队处理中
# 排队处理中（字幕）
# 处理中
# 生成字幕中
# 生成字幕成功
# 处理中（字幕）

# status
# tags
# caption  标记类型
# file_name
# xunfei_id

# videos = {'择天记_时间.mp4': {'status': "处理中"}, '择天记_时间2.mp4': {'status': "排队处理中"}, '择天记_字幕.mp4': {'status': "生成字幕中"}, '择天记_字幕2.mp4': {'status': "排队处理中（字幕）"}, '择天记_字幕3.mp4': {'status': "处理中（字幕）"}}
videos = {}
noCaptionQueue = Queue.Queue(maxsize=50)
captionQueue = Queue.Queue(maxsize=50)
uploadAudioQueue = Queue.Queue(maxsize=50)
getAudioQueue = Queue.Queue(maxsize=50)
topCount = 100
clipDuration = 2


## nocaption video 队列
def start_nocaption_video_queue():
    thread = threading.Thread(target=did_start_nocaption_video_queue)
    thread.daemon = True
    thread.start()


def did_start_nocaption_video_queue():
    for video in get_no_caption_video():
        process_video_to_generate_gifs(video)


def get_no_caption_video():
    item = noCaptionQueue.get()
    while item:
        yield item
        noCaptionQueue.task_done()
        item = noCaptionQueue.get()


def is_overlapping(x1, x2, y1, y2):
    return max(x1, y1) < min(x2, y2)


def process_video_to_generate_gifs(video):
    print "process_video_to_generate_gifs"
    ## 检查状态
    sleep(0.1)
    videos = DATA_PROVIDER.get_video_by_hash_name(DATA_PROVIDER.no_caption_queue_session, video.hash_name)
    if len(videos) == 0:
        print "dataError: process_video_to_generate_gifs 数据丢失"
        return
    print "检查状态"
    print "准备更新状态 3"
    vi = videos[0]
    if vi.status != 2:
        print "dataError: process_video_to_generate_gifs 数据状态不是'排队等待处理中'"
        print vi.status
        return
    print "更新状态 3"
    ## 更新video状态
    vi.status = 3
    vi.update_time = datetime.now()
    sleep(0.01)
    DATA_PROVIDER.update_video(DATA_PROVIDER.no_caption_queue_session, vi)

    ## 开始处理
    print "开始处理"
    process_start = time.time()
    video_path = os.path.join(config['UPLOAD_FOLDER'], vi.hash_name + "." + vi.extension)
    processed_path = os.path.join(config['PROCESSED_FOLDER'], vi.hash_name + "." + vi.extension)
    gif_path = os.path.join(config['GIF_FOLDER'], vi.hash_name)
    ogiginal_gif_path = os.path.join(config['ORIGINAL_GIF_FOLDER'], vi.hash_name)
    zip_path = os.path.join(config['ZIPED_GIF_FOLDER'], vi.hash_name + '.zip')
    print video_path
    print processed_path
    print gif_path
    print ogiginal_gif_path
    print zip_path

    video = VideoFileClip(video_path)
    segmentsArray = []
    duration = vi.segment_duration
    if duration <= 0:
        duration = clipDuration
    for videoStart in range(0, duration, 1):
        particalSegments = [(start, int(start + video.fps * duration)) for start in
                            range(int(videoStart * video.fps), int(video.duration * video.fps),
                                  int(video.fps * duration))]
        print "particalSegments count:"
        print len(particalSegments)
        segmentsArray.append(particalSegments)

    print "segments array count:"
    print len(segmentsArray)

    if global_config.config['is_local']:
        print "本地假装开始对 %s 进行评分" % vi.name
        sleep(60)
        print "本地假装对 %s 进行评分结束" % vi.name
        vi.status = 33
        vi.update_time = datetime.now()
        DATA_PROVIDER.update_video(DATA_PROVIDER.no_caption_queue_session, vi)
        return

    # Score the segments
    scores = {}
    

    for particalSegments in segmentsArray:
        particalScores = video2gif.get_scores(score_function, particalSegments, video, vi.name, stride=8)
        scores.update(particalScores)
        print "score count:"
        print len(scores)

    if not os.path.exists(gif_path):
        os.mkdir(gif_path)

    if not os.path.exists(ogiginal_gif_path):
        os.mkdir(ogiginal_gif_path)

    # Generate GIFs from the top scoring segments
    generate_start_time = time.time()
    nr = 0
    totalCount = len(scores)
    top_k = min(topCount, totalCount)
    occupiedTime = []
    height = vi.thumb_height
    for segment in sorted(scores, key=lambda x: -scores.get(x))[0:totalCount]:
        if nr >= top_k:
            break

        overlaping = 0

        for seg in occupiedTime:
            if is_overlapping(seg[0], seg[1], segment[0], segment[1]):
                overlaping = 1
                print "skip overlapping"
                break
        if overlaping == 0:
            occupiedTime.append(segment)
            clip = video.subclip(segment[0] / float(video.fps), segment[1] / float(video.fps))
            original_clip = video.subclip(segment[0] / float(video.fps), segment[1] / float(video.fps))
            out_gif = "%s/%.2d.gif" % (gif_path.decode('utf-8'), nr)
            origianl_gif = "%s/%.2d.mp4" % (ogiginal_gif_path.decode('utf-8'), nr)
            ## resize
            if height > 0:
                clip = clip.resize(height=height)
            else:
                clip = clip.resize(width=320)
            clip.write_gif(out_gif, fps=10, program="ImageMagick", opt="optimizeplus")
            original_clip.write_videofile(origianl_gif, fps=10, audio=False)
            nr += 1
    print("生成图片用时: %.2fs" % (time.time() - generate_start_time))

    # 压缩原尺寸图片
    cmd = "zip -rj " + zip_path + " " + ogiginal_gif_path
    print cmd
    os.system(cmd)

    # 转移视频
    cmd1 = 'mv ' + video_path + " " + processed_path
    print cmd1
    os.system(cmd1)

    #把状态更新成已处理
    vi.status = 1
    vi.update_time = datetime.now()
    sleep(0.01)
    DATA_PROVIDER.update_video(DATA_PROVIDER.no_caption_queue_session, vi)

    print("处理无字幕视频用时: %.2fs" % (time.time() - process_start))


## 初始化提取 audio 队列
def start_get_audio_queue():
    print "初始化提取音频队列"
    thread = threading.Thread(target=did_start_get_audio_queue)
    thread.daemon = True
    thread.start()


def did_start_get_audio_queue():
    print 'did_start_get_audio_queue'
    for video in get_video_to_audio_path():
        print "did_start_get_audio_queue"
        sleep(0.1)
        ## 检查状态
        videos = DATA_PROVIDER.get_video_by_hash_name(DATA_PROVIDER.audio_queue_session,video.hash_name)
        if len(videos) == 0:
            print "dataError: did_start_get_audio_queue 数据丢失"
            return

        vi = videos[0]
        if vi.status != 2:
            print "dataError: did_start_get_audio_queue 数据状态不是'排队等待处理中'"
            print vi.status
            return

        ## 更新video状态
        vi.status = 4 ## 提取音频中
        vi.update_time = datetime.now()
        sleep(0.01)
        DATA_PROVIDER.update_video(DATA_PROVIDER.audio_queue_session, vi)

        ## 开始处理
        start = time.time()

        # 先检查audio_path是否有文件了
        # 如果有检查audio的时长跟video的时长是否一样，不一样的话删除audio，重新提取audio
        video_path = os.path.join(config['UPLOAD_FOLDER'], vi.hash_name + "." + vi.extension)
        audio_path = os.path.join(config['BOTTLENECK'], vi.hash_name + "." + "mp3")
        print video_path
        print audio_path

        has_audio = False
        if os.path.isfile(audio_path):
            has_audio = True
        # audio = AudioFileClip(audio_path)
        # video = VideoFileClip(video_path)
        # if audio.duration == video.duration:
        # 	has_audio = True
        # 	print "音视频一般长"
        # else:
        # 	print "音视频不一样长"
        # 	os.remove(audio_path)

        if not has_audio:
            try:
                video = VideoFileClip(video_path)
                clip = video.subclip(0)
                clip.audio.write_audiofile(audio_path, bitrate="128k")
            except:
                print "%s提取音频失败" % vi.hash_name
                if os.path.isfile(audio_path):
                    os.remove(audio_path)
                # 重新加入提取音频队列
                vi.status = 2
                vi.update_time = datetime.now()
                sleep(0.01)
                DATA_PROVIDER.update_video(DATA_PROVIDER.audio_queue_session, vi)

                getAudioQueue.put(vi)
                continue
        print("提取音频用时: %.2fs" % (time.time() - start))
        ## 更新video状态
        vi.status = 5  ## 提取音频成功
        vi.update_time = datetime.now()
        sleep(0.01)
        DATA_PROVIDER.update_video(DATA_PROVIDER.audio_queue_session, vi)
        uploadAudioQueue.put(vi)


def get_video_to_audio_path():
    item = getAudioQueue.get()
    while item:
        yield item
        getAudioQueue.task_done()
        item = getAudioQueue.get()


## 初始化上传音频到讯飞的队列
def start_upload_audio_queue():
    thread = threading.Thread(target=did_start_upload_audio_queue)
    thread.daemon = True
    thread.start()


def did_start_upload_audio_queue():
    for video in get_audio_path():

        ## 检查状态
        sleep(0.1)
        videos = DATA_PROVIDER.get_video_by_hash_name(DATA_PROVIDER.upload_queue_session, video.hash_name)
        if len(videos) == 0:
            print "dataError: did_start_upload_audio_queue 数据丢失"
            return

        vi = videos[0]
        ## 更新video状态
        vi.status = 6  ## 上传音频中
        vi.update_time = datetime.now()
        sleep(0.01)
        DATA_PROVIDER.update_video(DATA_PROVIDER.upload_queue_session, vi)

        ## 开始处理
        start = time.time()
        xunfei_id = vi.xunfei_id
        if xunfei_id is not None and xunfei_id != "":
            print("已上传过音频,讯飞id: %s" % xunfei_id)
            ## 更新video状态
            vi.status = 7  ## 上传音频成功
            vi.update_time = datetime.now()
            sleep(0.01)
            DATA_PROVIDER.update_video(DATA_PROVIDER.upload_queue_session, vi)
            continue

        audio_path = os.path.join(config['BOTTLENECK'], vi.hash_name + "." + "mp3")
        print audio_path
        cmd = "java -jar %s 0 %s %s %s" % (
        config['XUNFEI_JAR'], config['XUNFEI_APPID'], config['XUNFEI_KEY'], audio_path)
        print cmd
        try:
            result = json.loads(os.popen(cmd).read())
        except:
            # 上传失败,重新加入上传音频队列
            print "上传失败"
            ## 更新video状态
            vi.status = 5  ## 提取音频成功
            vi.update_time = datetime.now()
            sleep(0.01)
            DATA_PROVIDER.update_video(DATA_PROVIDER.upload_queue_session, vi)

            uploadAudioQueue.put(vi)
            continue

        print result
        if result['ok'] == 0:
            ## 更新video状态
            vi.status = 7  ## 上传音频成功
            xunfei_id = result['data']
            vi.xunfei_id = xunfei_id
            vi.update_time = datetime.now()
            vi.xunfei_upload_time = datetime.now()
            sleep(0.01)
            DATA_PROVIDER.update_video(DATA_PROVIDER.upload_queue_session, vi)
        else:
            # 上传失败,重新加入上传音频队列
            print "上传失败"
            ## 更新video状态
            vi.status = 5  ## 提取音频成功
            vi.update_time = datetime.now()
            sleep(0.01)
            DATA_PROVIDER.update_video(DATA_PROVIDER.upload_queue_session, vi)
            uploadAudioQueue.put(vi)
            continue

        print("上传音频用时: %.2fs" % (time.time() - start))


def get_audio_path():
    item = uploadAudioQueue.get()
    while item:
        yield item
        uploadAudioQueue.task_done()
        item = uploadAudioQueue.get()


## 周期性遍历videos，去讯飞获取字幕，同时将获取成功的video添加进字幕video队列
def start_get_caption_loop():
    t = Timer(20, start_get_caption_loop)
    t.start()
    get_caption_from_xunfei()


def get_caption_from_xunfei():
    print 'get_caption_from_xunfei'
    sleep(0.1)
    videos = DATA_PROVIDER.get_all_fetching_caption_videos(DATA_PROVIDER.caption_loop_queue_session)
    for vi in videos:
        ## d
        time_gap = datetime.now() - vi.xunfei_upload_time

        if time_gap.days > 0 or time_gap.seconds > 480:
            print "%s 开始获取字幕, xunfei_id: %s" % (vi.name, vi.xunfei_id)
        else:
            print "尚未到讯飞要求的时间"

        ## 更新video状态
        vi.status = 8  ## 获取字幕中
        vi.update_time = datetime.now()
        sleep(0.01)
        DATA_PROVIDER.update_video(DATA_PROVIDER.caption_loop_queue_session, vi)

        xunfei_id = vi.xunfei_id
        cmd = "java -jar %s 1 %s %s %s" % (
        config['XUNFEI_JAR'], config['XUNFEI_APPID'], config['XUNFEI_KEY'], xunfei_id)
        print cmd
        try:
            result = json.loads(os.popen(cmd).read())
        except:
            continue

        if result['ok'] != 0:
            print result
            ## 更新video状态
            vi.status = 7  ## 上传音频成功
            vi.update_time = datetime.now()
            sleep(0.01)
            DATA_PROVIDER.update_video(DATA_PROVIDER.caption_loop_queue_session, vi)
            continue

        print "%s 获取字幕成功, xunfei_id: %s" % (vi.name, xunfei_id)
        ## 更新video状态
        vi.status = 9  ## 获取字幕成功
        vi.caption= result['data']
        vi.update_time = datetime.now()
        sleep(0.1)
        DATA_PROVIDER.update_video(DATA_PROVIDER.caption_loop_queue_session, vi)

        # 加入字幕视屏队列
        captionQueue.put(vi)


## 初始化有字幕 video 队列
def start_caption_video_queue():
    thread = threading.Thread(target=did_start_caption_video_queue)
    thread.daemon = True
    thread.start()


def did_start_caption_video_queue():
    for video in get_caption_video_path():
        process_caption_video_to_generate_gifs(video)


def get_caption_video_path():
    item = captionQueue.get()
    while item:
        yield item
        captionQueue.task_done()
        item = captionQueue.get()


def process_caption_video_to_generate_gifs(video):
    ## 检查状态
    print("process_caption_video_to_generate_gifs")
    sleep(0.1)
    videos = DATA_PROVIDER.get_video_by_hash_name(DATA_PROVIDER.caption_queue_session, video.hash_name)
    if len(videos) == 0:
        print "dataError: process_caption_video_to_generate_gifs 数据丢失"
        return

    vi = videos[0]
    if vi.status != 9:
        print "dataError: process_caption_video_to_generate_gifs 数据状态不是'获取字幕成功'"
        print vi.status
        return

    ## 更新video状态
    vi.status = 3
    vi.update_time = datetime.now()
    sleep(0.01)
    DATA_PROVIDER.update_video(DATA_PROVIDER.caption_queue_session, vi)

    ## 开始处理
    start = time.time()

    video_path = os.path.join(config['UPLOAD_FOLDER'], vi.hash_name + "." + vi.extension)
    processed_path = os.path.join(config['PROCESSED_FOLDER'], vi.hash_name + "." + vi.extension)
    gif_path = os.path.join(config['GIF_FOLDER'], vi.hash_name)
    ogiginal_gif_path = os.path.join(config['ORIGINAL_GIF_FOLDER'], vi.hash_name)
    zip_path = os.path.join(config['ZIPED_GIF_FOLDER'], vi.hash_name + '.zip')
    print video_path
    print processed_path
    print gif_path
    print ogiginal_gif_path
    print zip_path


    video = VideoFileClip(video_path)
    info = {}

    captions = json.loads(vi.caption)
    info['caption'] = captions
    segments = []
    fps = video.fps
    for ca in captions:
        bg = int(ca['bg'])
        ed = int(ca['ed'])
        start_frame = int(float(bg) / float(1000) * fps)
        end_frame = int(float(ed) / float(1000) * fps)

        duration = float(ed - bg) / 1000.0
        if duration > 5:
            print "大于5秒"
            continue
        if end_frame - 16 > start_frame:
            segments.append((start_frame, end_frame, ca['onebest']))
        else:
            print "不足16帧"

    if global_config.config['is_local']:
        print "本地假装开始对 %s 进行评分" % vi.name
        sleep(60)
        print "本地假装对 %s 进行评分结束" % vi.name
        vi.status = 33
        vi.update_time = datetime.now()
        DATA_PROVIDER.update_video(DATA_PROVIDER.no_caption_queue_session, vi)
        return

    scores = video2gif.get_scores(score_function, segments, video, vi.name, stride=8)
    count = len(scores)
    print "segment count:"
    print count

    if not os.path.exists(gif_path):
        os.mkdir(gif_path)
    if not os.path.exists(ogiginal_gif_path):
        os.mkdir(ogiginal_gif_path)

    return
    # Generate GIFs from the top scoring segments
    nr = 0
    top_k = min(topCount, count)
    result = []
    height = vi.thumb_height
    print height
    for segment in sorted(scores, key=lambda x: -scores.get(x))[0:count]:
        if nr >= top_k:
            break
        print segment[0] / float(fps)
        print segment[1] / float(fps)
        original_clip = video.subclip(segment[0] / float(fps), segment[1] / float(fps))
        clip = video.subclip(segment[0] / float(fps), segment[1] / float(fps))
        out_gif = "%s/%.2d.gif" % (gif_path.decode('utf-8'), nr)
        original_gif = "%s/%.2d.mp4" % (ogiginal_gif_path.decode('utf-8'), nr)
        gif_name = "%.2d.gif" % nr
        ## resize
        if height > 0:
            clip = clip.resize(height=height)
        else:
            clip = clip.resize(width=320)
        clip.write_gif(out_gif, fps=10, program="ImageMagick", opt="optimizeplus")
        original_clip.write_videofile(original_gif, fps=10, audio=False)
        result.append({"gif": gif_name, 'caption': segment[2]})
        nr += 1

    info['gif_caption'] = result
    print "处理带字幕的视频完成完成"

    # 压缩原尺寸图片
    cmd = "zip -rj " + zip_path + " " + ogiginal_gif_path
    print cmd
    os.system(cmd)

    print '准备转移视频'
    # 转移视频
    cmd1 = 'mv ' + video_path + " " + processed_path
    print cmd1
    os.system(cmd1)

    ## 更新video状态
    vi.status = 1
    vi.update_time = datetime.now()
    vi.caption = json.dumps(info)
    sleep(0.01)
    DATA_PROVIDER.update_video(DATA_PROVIDER.caption_queue_session, vi)
    print("处理字幕视频用时: %.2fs" % (time.time() - start))


## helpers
def is_mp4(file):
    fileName, fileExtension = os.path.splitext(file.lower())
    print fileName
    print fileExtension
    print "is mp4"
    if fileExtension == '.mp4':
        print "did is mp4"
        return True
    return False


def zhuanyi(original):
    chars = ['&', '<', '>', '|', '?', '*', '~', '#', ';', '$', '!']
    for char in chars:
        original = original.replace(char, '\\' + char)
    return original


## 接口
def get_file_status_info(fileName):
    op = "处理"
    status = "尚未处理"
    if videos.has_key(fileName):
        info = videos[fileName]
        if info.has_key('status'):
            status = info['status']
        if status == "生成字幕中" or status == "生成字幕成功" or status == "排队处理中（字幕）" or status == "处理中" or status == "处理中（字幕）":
            op = ""
        elif status == "排队处理中":
            op = ""  ##TODO

    return status, op


def start_all_queues():
    print "初始化队列"
    start_nocaption_video_queue()
    start_get_audio_queue()
    start_upload_audio_queue()
    start_get_caption_loop()
    start_caption_video_queue()
    print "初始化队列完成"


def add_video_to_process(fileName, height, tags, caption, isChinese, duration):
    sleep(0.01)
    videos = DATA_PROVIDER.get_video_by_hash_name(DATA_PROVIDER.main_queue_session, fileName)
    print "video count:"
    print len(videos)
    if len(videos) == 0:
        return {'result': 1001, "error_message": "该视频丢失"}

    video = videos[0]
    print "添加的video"
    print video.hash_name
    ## 检查video状态
    if video.status != 0:
        return {'result': 1002, "error_message": "视频已经在处理了", "video": video.mini_serialize()}

    video.tag = tags
    video.status = 2
    video.thumb_height = height
    video.segment_duration = duration
    is_chinese = 0
    if isChinese == "false":
        is_chinese = 1
    video.is_chinese = is_chinese

    split_type = 1
    if caption == "true":
        split_type = 0

    video.split_type = split_type
    video.update_time = datetime.now()
    sleep(0.01)
    DATA_PROVIDER.update_video(DATA_PROVIDER.main_queue_session, video)

    if split_type == 0:
        getAudioQueue.put(video)
    else:
        noCaptionQueue.put(video)

    print "添加的video"
    print video.hash_name
    return {'result': 0, "video": video.mini_serialize()}




