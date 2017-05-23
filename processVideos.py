#-*- coding:utf-8 -*-
# Import the video2gif package
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
score_function = video2gif.get_prediction_function()

from IPython.display import Image, display
import os
from moviepy.editor import VideoFileClip, AudioFileClip
import sys
import json
import time


print "这里走了吗"

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
config['XUNFEI_APPID'] = '591eae07'
config['XUNFEI_KEY'] = '08d5287ec77c65b58f9eb18b168cad4d'

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
print "这里走了吗111"
videos = {}
noCaptionQueue = Queue.Queue(maxsize=50)
captionQueue = Queue.Queue(maxsize=50)
uploadAudioQueue = Queue.Queue(maxsize=50)
getAudioQueue = Queue.Queue(maxsize=50)
topCount = 100
clipDuration = 2
print "这里走了吗222"


## nocaption video 队列
def start_nocaption_video_queue():
	thread = threading.Thread(target=did_start_nocaption_video_queue)
	thread.daemon = True
	thread.start()

def did_start_nocaption_video_queue():
	for file_name, video_path, gif_path, info_file_path, processed_path in get_no_caption_video_path():
		process_video_to_generate_gifs(file_name, video_path, gif_path, info_file_path, processed_path)

def get_no_caption_video_path():
    item = noCaptionQueue.get()
    while item:
        yield item
        noCaptionQueue.task_done()
        item = noCaptionQueue.get()

def is_overlapping(x1,x2,y1,y2):
    return max(x1,y1) < min(x2,y2)

def process_video_to_generate_gifs(file_name, video_path, gif_path, info_file_path, processed_path):
	if not videos.has_key(file_name):
		return
	process_start = time.time()
	info = videos[file_name]
	info['status'] = '处理中'
	video = VideoFileClip(video_path)
	segmentsArray = []
	for videoStart in range(0, clipDuration, 1):
		print "videoStart:"
		print videoStart
		particalSegments = [(start, int(start+video.fps*clipDuration)) for start in range(int(videoStart*video.fps),int(video.duration*video.fps),int(video.fps*clipDuration))]
		print "particalSegments count:"
		print len(particalSegments)
		segmentsArray.append(particalSegments)

	print "segments count:"
	print len(segmentsArray)

	# Score the segments
	scores = {}
	for particalSegments in segmentsArray:
		particalScores = video2gif.get_scores(score_function, particalSegments, video, stride=8)
		scores.update(particalScores)
		print "score count:"
		print len(scores)

	OUT_DIR=gif_path
	if not os.path.exists(OUT_DIR):
	    os.mkdir(OUT_DIR)
	ogiginal_gif_path = os.path.join(config['ORIGINAL_GIF_FOLDER'], file_name)
	print 'original path:'
	print ogiginal_gif_path
	if not os.path.exists(ogiginal_gif_path):
	    os.mkdir(ogiginal_gif_path)

	# Generate GIFs from the top scoring segments

	nr=0
	totalCount = len(scores)
	top_k=min(topCount, totalCount)
	occupiedTime = []
	height = videos[file_name]['height']
	print height
	for segment in sorted(scores, key=lambda x: -scores.get(x))[0:totalCount]:
		if nr >= top_k:
			break


		overlaping = 0

		for seg in occupiedTime:
			if is_overlapping(seg[0], seg[1], segment[0], segment[1]):
				overlaping = 1
				print "skip overlapping"
				break
		print 'overlapping'
		print overlaping
		if overlaping == 0:
			occupiedTime.append(segment)
			clip = video.subclip(segment[0] / float(video.fps), segment[1] / float(video.fps))
			original_clip = video.subclip(segment[0] / float(video.fps), segment[1] / float(video.fps))
			out_gif = "%s/%s_%.2d.gif" % (OUT_DIR.decode('utf-8'),file_name.decode('utf-8'),nr)
			origianl_gif = "%s/%s_%.2d.gif" % (ogiginal_gif_path.decode('utf-8'), file_name.decode('utf-8'), nr)
			## resize
			if height > 0:
				clip = clip.resize(height=height)
			else:
				clip = clip.resize(width=320)
			clip.write_gif(out_gif,fps=10)
			original_clip.write_gif(origianl_gif, fps=10)
			nr += 1

	# 压缩原尺寸图片
	zip_path = os.path.join(config['ZIPED_GIF_FOLDER'], file_name)
	cmd = "zip -rj " + zip_path + " " +  ogiginal_gif_path
	print cmd
	os.system(cmd)

	# 转移视频
	cmd1 = 'mv ' + video_path + " " + processed_path
	print cmd1
	os.system(cmd1)

	del videos[file_name]
	print("处理无字幕视频用时: %.2fs" % (time.time() - process_start))


## 初始化提取 audio 队列
def start_get_audio_queue():
	print "初始化提取音频队列"
	thread = threading.Thread(target=did_start_get_audio_queue)
	thread.daemon = True
	thread.start()

def did_start_get_audio_queue():
	print 'did_start_get_audio_queue'
	for file_name, video_path, gif_path, audio_path, caption_path, processed_path in get_video_to_audio_path():
		# 先检查audio_path是否有文件了
		# 如果有检查audio的时长跟video的时长是否一样，不一样的话删除audio，重新提取audio
		start = time.time()
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
				print "%s提取音频失败" % file_name
				if os.path.isfile(audio_path):
					os.remove(audio_path)
				# 重新加入提取音频队列
				getAudioQueue.put((file_name, video_path, gif_path, audio_path, caption_path, processed_path))
				continue
		print("提取音频用时: %.2fs" % (time.time() - start))
		uploadAudioQueue.put((file_name, video_path, audio_path))


def get_video_to_audio_path():
	print 'get_video_to_audio_path'
	item = getAudioQueue.get()
	while item:
		print "获取到了item"
		yield item
		getAudioQueue.task_done()
		item = getAudioQueue.get()



## 初始化上传音频到讯飞的队列
def start_upload_audio_queue():
	thread = threading.Thread(target=did_start_upload_audio_queue)
	thread.daemon = True
	thread.start()

def did_start_upload_audio_queue():
	for file_name, video_path, audio_path in get_audio_path():
		start = time.time()
		cmd = "java -jar %s 0 %s %s %s" % (config['XUNFEI_JAR'], config['XUNFEI_APPID'], config['XUNFEI_KEY'], audio_path)
		try:
			result = json.loads(os.popen(cmd).read())
		except:
			# 上传失败,重新加入上传音频队列
			uploadAudioQueue.put((file_name, video_path, audio_path))
			continue

		print result
		if result['ok'] == 0:
			xunfei_id = result['data']
			info = videos[file_name]
			info['xunfei_id'] = xunfei_id
		else:
			# 上传失败,重新加入上传音频队列
			uploadAudioQueue.put((file_name, video_path, audio_path))
			continue

		# 临时
		# xunfei_id = 'd2931698fdf8413f8b496de400025295'
		# info = videos[file_name]
		# info['xunfei_id'] = xunfei_id

		info['status'] = "生成字幕中"

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
	for key in videos:
		vi = videos[key]
		if vi.has_key('xunfei_id') and vi['status'] != "生成字幕成功":
			print key
			xunfei_id = vi['xunfei_id']
			cmd = "java -jar %s 1 %s %s %s" % (config['XUNFEI_JAR'], config['XUNFEI_APPID'], config['XUNFEI_KEY'], xunfei_id)
			print cmd
			try:
				result = json.loads(os.popen(cmd).read())
			except:
				continue

			if result['ok'] != 0:
				print result
				continue

			print "%s 获取字幕成功" % xunfei_id
			vi['status'] = "生成字幕成功"
			content = {}
			content['file_name'] = vi['file_name']
			content['tags'] = vi['tags']
			content['xunfei_id'] = xunfei_id
			caption_string = result['data']
			content['caption'] = json.loads(caption_string)

			caption_file_name = vi['file_name'] + '.txt'
			caption_file_path = os.path.join(config['BOTTLENECK'], caption_file_name)

			try:
				with open(caption_file_path, 'w') as f:
					f.write(json.dumps(content))
			except:
				print "%s 写文件失败" % xunfei_id

			# 加入字幕视屏队列
			video_path = os.path.join(config['UPLOAD_FOLDER'], key + ".mp4")
			gif_path = os.path.join(config['GIF_FOLDER'], vi['file_name'])
			print gif_path
			processed_path = os.path.join(config['PROCESSED_FOLDER'], vi['file_name'] + '.mp4')
			audio_name = vi['file_name'] + ".mp3"
			audio_path = os.path.join(config['BOTTLENECK'], audio_name)
			caption_path = caption_file_path
			captionQueue.put((vi['file_name'], video_path, gif_path, audio_path, caption_path, processed_path))



## 初始化有字幕 video 队列
def start_caption_video_queue():
	thread = threading.Thread(target=did_start_caption_video_queue)
	thread.daemon = True
	thread.start()

def did_start_caption_video_queue():
	for file_name, video_path, gif_path, audio_path, caption_path, processed_path in get_caption_video_path():
		process_caption_video_to_generate_gifs(file_name, video_path, gif_path, audio_path, caption_path,processed_path)


def get_caption_video_path():
	item = captionQueue.get()
	while item:
		yield item
		captionQueue.task_done()
		item = captionQueue.get()

def process_caption_video_to_generate_gifs(file_name, video_path, gif_path, audio_path, caption_path, processed_path):
	if not videos.has_key(file_name):
		return
	start = time.time()

	video = VideoFileClip(video_path)
	info = {}
	try:
		with open(caption_path, 'r') as f:
			info = json.loads(f.read())
	except:
		print "%s 读字幕文件失败" % file_name
		captionQueue.put((file_name, video_path, gif_path, audio_path, caption_path, processed_path))
		return

	captions = info['caption']
	segments = []
	fps = video.fps
	durations = []
	for ca in captions:
		bg = int(ca['bg'])
		ed = int(ca['ed'])
		start_frame = int(float(bg) / float(1000) * fps)
		end_frame = int(float(ed) / float(1000) * fps)

		duration = float(ed - bg) / 1000.0
		durations.append(duration)

		if duration > 5:
			print "大于5秒"
			continue
		if end_frame - 16 > start_frame:
			segments.append((start_frame, end_frame, ca['onebest']))
		else:
			print "不足16帧"

	scores = video2gif.get_scores(score_function, segments, video, stride=8)
	count = len(scores)
	print "segment count:"
	print count

	if not os.path.exists(gif_path):
		os.mkdir(gif_path)
	ogiginal_gif_path = os.path.join(config['ORIGINAL_GIF_FOLDER'], file_name)
	print 'original path:'
	print ogiginal_gif_path
	if not os.path.exists(ogiginal_gif_path):
		os.mkdir(ogiginal_gif_path)

	# Generate GIFs from the top scoring segments
	nr = 0
	top_k = min(topCount, count)
	result = []
	height = videos[file_name]['height']
	print height
	for segment in sorted(scores, key=lambda x: -scores.get(x))[0:count]:
		if nr >= top_k:
			break
		original_clip = video.subclip(segment[0] / float(fps), segment[1] / float(fps))
		clip = video.subclip(segment[0] / float(fps), segment[1] / float(fps))
		out_gif = "%s/%s_%.2d.gif" % (gif_path.decode('utf-8'), file_name.decode('utf-8'), nr)
		original_gif = "%s/%s_%.2d.gif" % (ogiginal_gif_path.decode('utf-8'), file_name.decode('utf-8'), nr)
		gif_name = "%s_%.2d.gif" % (file_name, nr)
		## resize
		if height > 0:
			clip = clip.resize(height=height)
		else:
			clip = clip.resize(width=320)
		clip.write_gif(out_gif, fps=10)
		original_clip.write_gif(original_gif, fps=10)
		result.append({"gif": gif_name, 'caption': segment[2]})
		nr += 1

	info['gif_caption'] = result
	print "处理带字幕的视频完成完成"
	try:
		with open(caption_path, 'w') as f:
			print '打开info,写入result'
			f.write(json.dumps(info))
	except:
		print "%s 依据字幕生成gif后,记录gif对应字幕失败" % file_name

	# 压缩原尺寸图片
	zip_path = os.path.join(config['ZIPED_GIF_FOLDER'], file_name)
	cmd = "zip -rj " + zip_path + " " + ogiginal_gif_path
	print cmd
	os.system(cmd)

	print '准备转移视频'
	# 转移视频
	cmd1 = 'mv ' + video_path + " " + processed_path
	print cmd1
	os.system(cmd1)

	del videos[file_name]
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
			op = "" ##TODO
			
	return status, op

def start_all_queues():
	print "初始化队列"
	start_nocaption_video_queue()
	start_get_audio_queue()
	start_upload_audio_queue()
	start_get_caption_loop()
	start_caption_video_queue()
	print "初始化队列完成"

def add_video_to_process(fileName, height, tags, caption):
	info = {}
	info['height'] = height
	info['tags'] = tags
	info['caption'] = caption
	file_name=os.path.splitext(os.path.split(fileName)[1])[0]
	info['file_name'] = file_name
	video_path = os.path.join(config['UPLOAD_FOLDER'], fileName)
	
	gif_path = os.path.join(config['GIF_FOLDER'], file_name)
	processed_path = os.path.join(config['PROCESSED_FOLDER'], fileName)
	if caption == "true":
		info['status'] = "排队处理中（字幕）"
		audio_name = file_name + ".mp3"
		audio_path = os.path.join(config['BOTTLENECK'], audio_name)
		caption_name = file_name + ".txt"
		caption_path = os.path.join(config['BOTTLENECK'], caption_name)
		getAudioQueue.put((file_name, video_path, gif_path, audio_path, caption_path, processed_path))
		print "添加item到音频队列"
	else:
		info['status'] = "排队处理中"
		content = {}
		content['file_name'] = file_name
		content['tags'] = tags

		info_file_name = file_name + '.txt'
		info_file_path = os.path.join(config['BOTTLENECK'], info_file_name)
		try:
			with open(info_file_path, 'w') as f:
				f.write(json.dumps(content))
		except:
			print "%s 写info失败" % file_name
			return
		noCaptionQueue.put((file_name, video_path, gif_path, info_file_path, processed_path))

	videos[file_name] = info
	print "添加的video"
	print file_name


	
