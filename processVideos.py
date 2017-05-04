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

score_function = video2gif.get_prediction_function()

from IPython.display import Image, display
import os
from moviepy.editor import VideoFileClip
import sys
import json
import time

basedir = os.path.abspath(os.path.dirname(__file__))
config = {}
config['SECRET_KEY'] = 'hard to guess string'
config['UPLOAD_FOLDER'] = basedir + '/unprocessedvideos/'
config['PROCESSED_FOLDER'] = basedir + '/processedvideos/'
config['THUMBNAIL_FOLDER'] = basedir + '/unprocessedvideos/thumbnail/'
config['GIF_FOLDER'] = basedir + '/gifs/'
config['ZIPED_GIF_FOLDER'] = basedir + '/zipedgifs/'

queue = Queue.Queue(maxsize=50)
topCount = 10
clipDuration = 2

def get_video_path():
    item = queue.get()
    while item:
        yield item
        queue.task_done()
        item = queue.get()

def is_mp4(file):
    fileName, fileExtension = os.path.splitext(file.lower())
    print fileName
    print fileExtension
    print "is mp4"
    if fileExtension == '.mp4':
    	print "did is mp4"
        return True
    return False

def add_video_to_queue(video_path, gif_path, zip_path, processed_path):
	queue.put((video_path, gif_path, zip_path, processed_path))

def did_process_video_queue():
	# 遍历unprocessed目录
	list_dirs = os.walk(config['UPLOAD_FOLDER']) 
	for root, dirs, files in list_dirs:  
		for f in files:
			print f
			if is_mp4(f):
				video_path = os.path.join(config['UPLOAD_FOLDER'], f)
				file_name=os.path.splitext(os.path.split(f)[1])[0]
				ziped_gif_file_name = file_name + ".zip"
				ziped_gif_path = os.path.join(config['ZIPED_GIF_FOLDER'], ziped_gif_file_name)
				gif_path = os.path.join(config['GIF_FOLDER'], file_name)
				processed_path = os.path.join(config['PROCESSED_FOLDER'], f)
				print 'add video to queue'
				add_video_to_queue(video_path, gif_path, ziped_gif_path, processed_path)


	for video_path, gif_path, zip_path, processed_path in get_video_path():
		print '从队列中读取数据'
		print video_path
		print gif_path
		print zip_path
		video_name=os.path.splitext(os.path.split(video_path)[1])[0]
		process_and_generate_gifs(video_path, video_name, gif_path, zip_path, processed_path)

def process_video_queue():
	thread = threading.Thread(target=did_process_video_queue)
	thread.daemon = True
	thread.start()


def process_and_generate_gifs(video_path, video_name, gif_path, zip_path, processed_path):
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

	# Generate GIFs from the top scoring segments
	gifCount = len(scores)
	print "gifs count:"
	print gifCount
	video2gif.generate_gifs(OUT_DIR,scores, video, video_name,top_k=topCount)

	# 压缩图片
	cmd = "zip -rj " + zip_path + " " +  gif_path
	print cmd
	os.system(cmd)

	# 转移视频
	cmd1 = 'mv ' + video_path + " " + processed_path
	print cmd1
	os.system(cmd1)


	
