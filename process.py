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
from data_service import DATA_PROVIDER
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


videos = {}
processQueue = Queue.Queue(maxsize=50)
uploadAudioQueue = Queue.Queue(maxsize=50)
getAudioQueue = Queue.Queue(maxsize=50)
topCount = 200
clipDuration = 2


def start_process_queue():
    thread = threading.Thread(target=did_start_process_queue)
    thread.daemon = True
    thread.start()


def did_start_process_queue():
    for video in get_video_to_process():
        processVideo(video)


def get_video_to_process():
    item = processQueue.get()
    while item:
        yield item
        processQueue.task_done()
        item = processQueue.get()


def processVideo(video):
    print "要处理的视频类型:"
    print video.split_type
    if video.split_type == 1:
        process_video_to_generate_gifs(video)
    else:
        process_caption_video_to_generate_gifs(video)


def is_overlapping(x1, x2, y1, y2):
    return max(x1, y1) < min(x2, y2)


def process_video_to_generate_gifs(video):
    print "process_video_to_generate_gifs"

    ## 检查状态
    sleep(0.1)
    videos = DATA_PROVIDER.get_video_by_hash_name(video.hash_name)
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
    DATA_PROVIDER.update_video(vi)

    ## 开始处理
    print "开始处理"
    print vi.name
    try:
        process_start = time.time()
        process_info = {}
        process_info['port'] = global_config.config['port']

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
            sleep(30)
            print "本地假装对 %s 进行评分结束" % vi.name
            vi.status = 33
            vi.update_time = datetime.now()
            DATA_PROVIDER.update_video(vi)
            return
    except (Exception) as e:
        print "处理失败"
        print "分割视频失败"
        print vi.name
        print e.message
        vi.status = 11  ##处理失败
        vi.update_time = datetime.now()
        process_info['error_message'] = "分割视频失败: %s" % e.message
        vi.process_info = json.dumps(process_info)
        sleep(0.01)
        DATA_PROVIDER.update_video(vi)
        return

    try:
        # Score the segments
        scores = {}
        for particalSegments in segmentsArray:
            particalScores = video2gif.get_scores(score_function, particalSegments, video, vi.name, stride=8)
            scores.update(particalScores)
            print "score count:"
            print len(scores)
    except (Exception) as e:
        print "处理失败"
        print "评分失败"
        print e.message
        vi.status = 11  ##处理失败
        vi.update_time = datetime.now()
        process_info['error_message'] = "评分失败: %s" % e.message
        vi.process_info = json.dumps(process_info)
        sleep(0.01)
        DATA_PROVIDER.update_video(vi)
        return

    try:
        process_info['segment_count'] = len(scores)
        process_info['score_time'] = int(time.time() - process_start)

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
                out_gif = "%s/%.3d.gif" % (gif_path.decode('utf-8'), nr)
                origianl_gif = "%s/%.3d.mp4" % (ogiginal_gif_path.decode('utf-8'), nr)
                ## resize
                if height > 0:
                    clip = clip.resize(height=height)
                else:
                    clip = clip.resize(width=320)
                clip.write_gif(out_gif, fps=10, program="ImageMagick", opt="optimizeplus")
                original_clip.write_videofile(origianl_gif, fps=10, audio=False)
                nr += 1
        print("生成图片用时: %.2fs" % (time.time() - generate_start_time))
        process_info['generate_time'] = int(time.time() - generate_start_time)

        # 压缩原尺寸图片
        cmd = "zip -rj " + zip_path + " " + ogiginal_gif_path
        print cmd
        os.system(cmd)

        # 转移视频
        cmd1 = 'mv ' + video_path + " " + processed_path
        print cmd1
        os.system(cmd1)
    except (Exception) as e:
        print "处理失败"
        print "生成图片失败"
        print vi.name
        print e.message
        vi.status = 11 ##处理失败
        vi.update_time = datetime.now()
        process_info['error_message'] = "生成图片失败: %s" % e.message
        vi.process_info = json.dumps(process_info)
        sleep(0.01)
        DATA_PROVIDER.update_video(vi)
        return

    # 把状态更新成已处理
    vi.status = 1
    vi.update_time = datetime.now()
    process_info['total_time'] = int(time.time() - process_start)
    vi.process_info = json.dumps(process_info)
    sleep(0.01)
    DATA_PROVIDER.update_video(vi)

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

        process_info = {}
        process_info['port'] = global_config.config['port']
        sleep(0.1)
        ## 检查状态
        videos = DATA_PROVIDER.get_video_by_hash_name(video.hash_name)
        if len(videos) == 0:
            print "dataError: did_start_get_audio_queue 数据丢失"
            continue

        vi = videos[0]
        if vi.status != 2:
            print "dataError: did_start_get_audio_queue 数据状态不是'排队等待处理中'"
            print vi.status
            continue

        if vi.xunfei_id is not None and vi.xunfei_id != "":
            print "%s 之前已经上传过音频了" % vi.name
            vi.status = 7  ## 上传音频成功
            vi.update_time = datetime.now()
            vi.process_info = json.dumps(process_info)
            sleep(0.01)
            DATA_PROVIDER.update_video(vi)
            continue


        ## 更新video状态
        vi.status = 4  ## 提取音频中
        vi.update_time = datetime.now()
        sleep(0.01)
        DATA_PROVIDER.update_video(vi)

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
            except (Exception) as e:
                print "%s提取音频失败" % vi.name
                print e.message
                vi.status = 11  ##处理失败
                vi.update_time = datetime.now()
                process_info['error_message'] = "提取音频失败: %s" % e.message
                vi.process_info = json.dumps(process_info)
                sleep(0.01)
                DATA_PROVIDER.update_video(vi)

                if os.path.isfile(audio_path):
                    os.remove(audio_path)

                continue
        print("提取音频用时: %.2fs" % (time.time() - start))
        process_info['extract_audio_time'] = int(time.time() - start)
        ## 更新video状态
        vi.status = 5  ## 提取音频成功
        vi.update_time = datetime.now()
        vi.process_info = json.dumps(process_info)
        sleep(0.01)
        DATA_PROVIDER.update_video(vi)
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
        videos = DATA_PROVIDER.get_video_by_hash_name(video.hash_name)
        if len(videos) == 0:
            print "dataError: did_start_upload_audio_queue 数据丢失"
            continue

        vi = videos[0]
        ## 更新video状态
        vi.status = 6  ## 上传音频中
        vi.update_time = datetime.now()
        sleep(0.01)
        DATA_PROVIDER.update_video(vi)

        ## 开始处理
        start = time.time()
        process_info = json.loads(vi.process_info)
        xunfei_id = vi.xunfei_id
        if xunfei_id is not None and xunfei_id != "":
            print("已上传过音频,讯飞id: %s" % xunfei_id)
            ## 更新video状态
            vi.status = 7  ## 上传音频成功
            vi.update_time = datetime.now()
            sleep(0.01)
            DATA_PROVIDER.update_video(vi)
            continue

        audio_path = os.path.join(config['BOTTLENECK'], vi.hash_name + "." + "mp3")
        print audio_path
        cmd = "java -jar %s 0 %s %s %s" % (
            config['XUNFEI_JAR'], config['XUNFEI_APPID'], config['XUNFEI_KEY'], audio_path)
        print cmd
        try:
            result = json.loads(os.popen(cmd).read())
            print result
        except (Exception) as e:
            # 上传失败,重新加入上传音频队列
            print "上传失败"
            print vi.name
            print e.message
            ## 更新video状态
            vi.status = 5  ## 提取音频成功
            vi.update_time = datetime.now()
            sleep(0.01)
            DATA_PROVIDER.update_video(vi)

            uploadAudioQueue.put(vi)
            continue

        print result
        if result['ok'] == 0:
            ## 更新video状态
            vi.status = 7  ## 上传音频成功
            xunfei_id = result['data']
            vi.xunfei_id = xunfei_id
            vi.update_time = datetime.now()
            process_info['upload_audio_time'] = int(time.time() - start)
            vi.process_info = json.dumps(process_info)
            vi.xunfei_upload_time = datetime.now()
            sleep(0.01)
            DATA_PROVIDER.update_video(vi)
        else:
            # 上传失败,重新加入上传音频队列
            print "上传失败"
            ## 更新video状态
            vi.status = 5  ## 提取音频成功
            vi.update_time = datetime.now()
            sleep(0.01)
            DATA_PROVIDER.update_video(vi)
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
    videos = DATA_PROVIDER.get_all_fetching_caption_videos()
    for vi in videos:

        ##检查是否是本实例处理的视频
        process_info = json.loads(vi.process_info)
        if process_info['port'] != global_config.config['port']:
            print "%s 不是本实例处理的视频" % vi.name
            continue

        time_gap = datetime.now() - vi.xunfei_upload_time
        if time_gap.days > 0 or time_gap.seconds > 480:  ##TODO根据视频duration决定等待时间
            print "%s 开始获取字幕, xunfei_id: %s" % (vi.name, vi.xunfei_id)
        else:
            print "尚未到讯飞要求的时间"
            continue

        ## 更新video状态
        vi.status = 8  ## 获取字幕中
        vi.update_time = datetime.now()
        sleep(0.01)
        DATA_PROVIDER.update_video(vi)

        xunfei_id = vi.xunfei_id
        cmd = "java -jar %s 1 %s %s %s" % (
            config['XUNFEI_JAR'], config['XUNFEI_APPID'], config['XUNFEI_KEY'], xunfei_id)
        print cmd
        try:
            result = json.loads(os.popen(cmd).read())
        except (Exception) as e:
            print "获取字幕失败"
            print vi.name
            print e.message
            vi.status = 7  ## 上传音频成功
            vi.update_time = datetime.now()
            sleep(0.01)
            DATA_PROVIDER.update_video(vi)
            continue

        if result['ok'] != 0:
            {u'failed': u'Task failed, please contact us.', u'err_no': 26201, u'ok': -1}
            if result['err_no'] != 0:
                print "转写失败"
                print result
                vi.status = 11  ##处理失败
                vi.xunfei_id = ""
                vi.update_time = datetime.now()
                process_info['error_message'] = "讯飞转写失败: %d %s" % (result['err_no'], result['failed'])
                vi.process_info = json.dumps(process_info)
                sleep(0.01)
                DATA_PROVIDER.update_video(vi)
                ##删除音频
                audio_path = os.path.join(config['BOTTLENECK'], vi.hash_name + "." + "mp3")
                if os.path.isfile(audio_path):
                    os.remove(audio_path)
                continue
            else:
                print result
                ## 更新video状态
                vi.status = 7  ## 上传音频成功
                vi.update_time = datetime.now()
                sleep(0.01)
                DATA_PROVIDER.update_video(vi)
                continue

        print "%s 获取字幕成功, xunfei_id: %s" % (vi.name, xunfei_id)
        ## 更新video状态
        vi.status = 9  ## 获取字幕成功
        vi.caption = result['data']
        vi.update_time = datetime.now()
        sleep(0.1)
        DATA_PROVIDER.update_video(vi)

        # 加入字幕视屏队列
        processQueue.put(vi)


def process_caption_video_to_generate_gifs(video):
    # if video.split_type == 1: ## 因为thero在多线程下有问题
    #     process_video_to_generate_gifs(video)
    #     return
    ## 检查状态
    print("process_caption_video_to_generate_gifs")
    sleep(0.1)
    videos = DATA_PROVIDER.get_video_by_hash_name(video.hash_name)
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
    DATA_PROVIDER.update_video(vi)

    ## 开始处理
    print "开始处理"
    try:
        start = time.time()
        process_info = json.loads(vi.process_info)

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
            sleep(30)
            print "本地假装对 %s 进行评分结束" % vi.name
            vi.status = 33
            vi.update_time = datetime.now()
            DATA_PROVIDER.update_video(vi)
            return

    except (Exception) as e:
        print "处理失败"
        print "分割视频失败"
        print vi.name
        print e.message
        vi.status = 11  ##处理失败
        vi.update_time = datetime.now()
        process_info['error_message'] = "分割视频失败: %s" % e.message
        vi.process_info = json.dumps(process_info)
        sleep(0.01)
        DATA_PROVIDER.update_video(vi)
        return

    try:
        scores = video2gif.get_scores(score_function, segments, video, vi.name, stride=8)
        count = len(scores)
        print "segment count:"
        print count
        process_info['segment_count'] = len(scores)
        process_info['score_time'] = int(time.time() - start)

    except (Exception) as e:
        print "处理失败"
        print "评分失败"
        print e.message
        vi.status = 11  ##处理失败
        vi.update_time = datetime.now()
        process_info['error_message'] = "评分失败: %s" % e.message
        vi.process_info = json.dumps(process_info)
        sleep(0.01)
        DATA_PROVIDER.update_video(vi)
        return

    try:

        if not os.path.exists(gif_path):
            os.mkdir(gif_path)
        if not os.path.exists(ogiginal_gif_path):
            os.mkdir(ogiginal_gif_path)

        # Generate GIFs from the top scoring segments

        generate_start_time = time.time()
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
            out_gif = "%s/%.3d.gif" % (gif_path.decode('utf-8'), nr)
            original_gif = "%s/%.3d.mp4" % (ogiginal_gif_path.decode('utf-8'), nr)
            gif_name = "%.3d.gif" % nr
            ## resize
            if height > 0:
                clip = clip.resize(height=height)
            else:
                clip = clip.resize(width=320)
            clip.write_gif(out_gif, fps=10, program="ImageMagick", opt="optimizeplus")
            original_clip.write_videofile(original_gif, fps=10, audio=False)
            result.append({"gif": gif_name, 'caption': segment[2]})
            nr += 1

        process_info['generate_time'] = int(time.time() - generate_start_time)

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

    except (Exception) as e:
        print "处理失败"
        print "生成图片失败"
        print vi.name
        print e.message
        vi.status = 11 ##处理失败
        vi.update_time = datetime.now()
        process_info['error_message'] = "生成图片失败: %s" % e.message
        vi.process_info = json.dumps(process_info)
        sleep(0.01)
        DATA_PROVIDER.update_video(vi)
        return

    process_info['total_time'] = int(time.time() - start)
    ## 更新video状态
    vi.status = 1
    vi.update_time = datetime.now()
    vi.caption = json.dumps(info)
    vi.process_info = json.dumps(process_info)
    sleep(0.01)
    DATA_PROVIDER.update_video(vi)
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
    start_get_audio_queue()
    start_upload_audio_queue()
    start_get_caption_loop()
    start_process_queue()
    print "初始化队列完成"


def add_video_to_process(fileName, height, tags, caption, isChinese, duration):
    split_type = 1
    if caption == "true":
        split_type = 0

    sleep(0.01)
    videos = DATA_PROVIDER.get_video_by_hash_name(fileName)
    print "video count:"
    print len(videos)
    if len(videos) == 0:
        return {'result': 1001, "error_message": "该视频丢失"}

    video = videos[0]
    print "添加的video"
    print video.name
    ## 检查video状态
    if video.status == 12:
        return {'result': 1002, "error_message": "视频正在删除中", "video": video.mini_serialize()}

    if video.status != 0 and  video.status != 11 :
        return {'result': 1002, "error_message": "视频已经在处理了", "video": video.mini_serialize()}

    ## 按时间截图的情况下,检测segment的帧数是否能够达到16
    if split_type == 1:
        info_dic = json.loads(video.video_info)
        fps = info_dic['fps']
        frames = fps * duration
        if frames < 16:
            return {'result': 1009, "error_message": "该视频帧率为: %.2f, 设置的图片截取时长为: %d秒, 总帧数不足16" % (fps, duration)}


    video.tag = tags
    video.status = 2
    video.thumb_height = height
    video.segment_duration = duration
    is_chinese = 0
    if isChinese == "false":
        is_chinese = 1
    video.is_chinese = is_chinese

    video.split_type = split_type
    video.update_time = datetime.now()
    sleep(0.01)
    DATA_PROVIDER.update_video(video)

    if split_type == 0:
        getAudioQueue.put(video)
    else:
        processQueue.put(video)  ##由于thero在多线程下有问题

    print "添加的video"
    print video.name
    return {'result': 0, "video": video.mini_serialize()}

def delete_video(fileName):
    sleep(0.01)
    videos = DATA_PROVIDER.get_video_by_hash_name(fileName)
    if len(videos) == 0:
        return {'result': 1001, "error_message": "该视频丢失"}

    video = videos[0]
    print "将要删除的video:"
    print video.name
    ## 检查video状态
    if video.status != 0 and video.status != 11 and video.status != 13 and video.status != 1:
        return {'result': 1002, "error_message": "视频正在处理中, 不能删除", "video": video.mini_serialize()}

    if video.status == 12:
        return {'result': 1002, "error_message": "该视频正在删除中", "video": video.mini_serialize()}

    ## 将视频状态更新成删除中
    video.status = 12
    video.update_time = datetime.now()
    sleep(0.01)
    DATA_PROVIDER.update_video(video)

    ##开始删除
    video_path = os.path.join(config['UPLOAD_FOLDER'], video.hash_name + "." + video.extension)
    processed_path = os.path.join(config['PROCESSED_FOLDER'], video.hash_name + "." + video.extension)
    gif_path = os.path.join(config['GIF_FOLDER'], video.hash_name)
    ogiginal_gif_path = os.path.join(config['ORIGINAL_GIF_FOLDER'], video.hash_name)
    zip_path = os.path.join(config['ZIPED_GIF_FOLDER'], video.hash_name + '.zip')
    audio_path = os.path.join(config['BOTTLENECK'], video.hash_name + "." + "mp3")

    try:
        if os.path.isfile(audio_path):
            print "删除%s" % audio_path
            os.remove(audio_path)

        if os.path.isfile(zip_path):
            print "删除%s" % zip_path
            os.remove(zip_path)

        if os.path.isdir(gif_path):
            print "删除%s" % gif_path
            cmd = "rm -rf " + gif_path
            print cmd
            os.system(cmd)

        if os.path.isdir(ogiginal_gif_path):
            print "删除%s" % ogiginal_gif_path
            cmd = "rm -rf " + ogiginal_gif_path
            print cmd
            os.system(cmd)

        if os.path.isfile(processed_path):
            print "删除%s" % processed_path
            os.remove(processed_path)

        if os.path.isfile(video_path):
            print "删除%s" % video_path
            os.remove(video_path)

    except (Exception) as e:
        print "%s删除失败: %s" % (video.name, e.message)
        video.status = 13
        video.update_time = datetime.now()
        sleep(0.01)
        DATA_PROVIDER.update_video(video)
        return {'result': 1002, "error_message": "视频删除失败", "video": video.mini_serialize()}

    print "%s删除成功" % video.name
    video.status = -1
    video.update_time = datetime.now()
    sleep(0.01)
    DATA_PROVIDER.update_video(video)
    return {'result': 0, "video": video.mini_serialize()}





