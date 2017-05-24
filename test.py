#-*- coding:utf-8 -*-
from IPython.display import Image, display
import os, json
from moviepy.editor import VideoFileClip, AudioFileClip, VideoClip
from threading import Timer
import threading
import requests
import StringIO
#
# print("哈哈")
import sys
reload(sys)
sys.setdefaultencoding('utf8')
basedir = os.path.abspath(os.path.dirname(__file__))
config = {}
config['UPLOAD_FOLDER'] = basedir + '/unprocessedvideos/'
config['GIF_FOLDER'] = basedir + '/static/gifs/'
config['BOTTLENECK'] = basedir + '/bottleneck/'
config['XUNFEI_JAR'] = basedir + '/LfasrDemo.jar'
config['XUNFEI_APPID'] = '5913fa87'
config['XUNFEI_KEY'] = '6c48f072a4ecf750538f2d073051a5b0'


video = VideoFileClip('./花儿与少年3-井柏然.mp4')
print video.fps
for videoStart in range(0, 5, 1):
	video.write_videofile
	clip = video.subclip(videoStart * 2, (videoStart + 1) * 2)
	out_clip = "out_%.2d.mp4" % videoStart
	out_gif = "out_%.2d.gif" % videoStart
	clip.write_videofile(out_clip, fps=10, audio=False)


	clip.resize(width=500)
	clip.write_gif(out_gif, fps=10, program="ImageMagick", opt="optimizeplus")


# url= 'http://120.27.214.63:8080/open-api/word/segments'
# cas = ["你狮子","哈哈无语了"]
#
# headers = {'Content-Type':'application/json;charset:UTF-8'}
# response = requests.post(url=url, data=json.dumps(cas), headers=headers)
# captions = ','.join(json.loads(response.content)['data'][1])
# print captions


def test():
	# cmd1 = 'java -jar LfasrDemo.jar 1 5913fa87 6c48f072a4ecf750538f2d073051a5b0 f00ba12c13744653bf33add66faf1ac6'
	# cmd = 'java -jar LfasrDemo.jar 0 5913fa87 6c48f072a4ecf750538f2d073051a5b0 /Users/isan/Dev/ML/video2gif/ztj.mp3'
	# print "ddd"
	# result = json.loads(os.popen(cmd1).read())
	# print len(result)
	# print result[1]
	# print "dddffff"



	# 择天记
	# videos = {'择天记_时间.mp4': {'status': "处理中"}, '择天记_时间2.mp4': {'status': "排队处理中"}, '择天记_字幕.mp4': {'status': "生成字幕中", 'file_name':'择天记_字幕', 'xunfei_id': 'f00ba12c13744653bf33add66faf1ac6', "tags":['dd', 'dddd']}, '择天记_字幕2.mp4': {'status': "排队处理中（字幕）"}, '择天记_字幕3.mp4': {'status': "处理中（字幕）"}}
	# for key in videos:
	# 	print key
	# 	vi = videos[key]
	# 	if vi.has_key('xunfei_id'):
	# 		xunfei_id = vi['xunfei_id']
	# 		cmd = "java -jar %s 1 %s %s %s" % (config['XUNFEI_JAR'], config['XUNFEI_APPID'], config['XUNFEI_KEY'], xunfei_id)
	# 		print cmd
	# 		try:
	# 			result = json.loads(os.popen(cmd).read())
	# 		except:
	# 			continue
	# 		print "%s 获取字幕成功" % vi['xunfei_id']
	# 		content = {}
	# 		content['file_name'] = vi['file_name']
	# 		content['tags'] = vi['tags']
	# 		content['xunfei_id'] = vi['xunfei_id']
	# 		content['caption'] = result

	# 		caption_file_name = vi['file_name'] + '.txt'
	# 		caption_file_path = os.path.join(config['BOTTLENECK'], caption_file_name)

	# 		try:
	# 			with open(caption_file_path, 'w') as f:
	# 				f.write(json.dumps(content))
	# 		except:
	# 			print "%s 写文件失败" % vi['xunfei_id']

	# 处理info文件
	file_name = '择天记.txt'
	info_path = os.path.join(config['BOTTLENECK'], file_name)
	video_path = os.path.join(config['UPLOAD_FOLDER'], '择天记.mp4')
	gif_path = os.path.join(config['GIF_FOLDER'], '择天记')

	video = VideoFileClip(video_path)
	info = {}
	try:
		with open(info_path, 'r') as f:
			info = json.loads(f.read())
	except:
		print "%s 读字幕文件失败" % file_name
		return

	captions = info['caption']
	segments = []
	fps = video.fps
	for ca in captions:
		start_frame = int(float(ca['bg']) / float(1000) * fps)
		end_frame = int(float(ca['ed']) / float(1000) * fps)
		segments.append((start_frame, end_frame, ca['onebest']))

	count = len(segments)
	print "segment count:"
	print count

	if not os.path.exists(gif_path):
		os.mkdir(gif_path)

	# Generate GIFs from the top scoring segments
	nr = 0
	top_k = min(20, count)
	result = []
	for segment in segments[100:150]:
		if nr >= top_k:
			break

		clip = video.subclip(segment[0] / float(fps), segment[1] / float(fps))
		out_gif = "%s/%s_%.2d.gif" % (gif_path.decode('utf-8'), file_name.decode('utf-8'), nr)
		gif_name = "%s_%.2d.gif" % (file_name, nr)
		## resize
		clip = clip.resize(width=500)
		clip.write_gif(out_gif, fps=10)
		result.append({"gif": gif_name, 'caption': segment[2]})
		nr += 1

	info['gif_caption'] = result

	try:
		with open(info_path, 'w') as f:
			f.write(json.dumps(info))
	except:
		print "%s 依据字幕生成gif后,记录gif对应字幕失败" % file_name


def ga():
	audio = AudioFileClip('./huanglesong_05_caption.mp3')
	video = VideoFileClip('./huanlesong_05.mp4')
	print audio.duration
	print video.duration

def start_get_caption_loop():
	t = Timer(2, start_get_caption_loop)
	t.start()
	get_caption_from_xunfei()

def get_caption_from_xunfei():
	print 'get_caption_from_xunfei'

