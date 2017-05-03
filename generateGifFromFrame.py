#-*- coding:utf-8 -*-
# Import the video2gif package
import video2gif
'''
Compile the score function
On the GPU, the network will be using cuDNN layer implementations available in the Lasagne master

If the device is CPU, it will use the CPU version that requires my Lasagne fork with added 3D convolution and pooling.
You can get it from https://github.com/gyglim/Lasagne

'''

score_function = video2gif.get_prediction_function()

from IPython.display import Image, display
import os
from moviepy.editor import VideoFileClip
import sys

import time

videosDir = sys.argv[1]
topCount = int(sys.argv[2])
clipDuration = int(sys.argv[3])
outputDir = sys.argv[4]


def process_and_generate_gifs_with_frame(video_path, video_name):

	video = VideoFileClip(video_path)

	## 0.5s to clipDuration
	fps = video.fps
	minFrames = max(int(0.5*fps), 30)
	maxFrames = max(int(clipDuration*fps), minFrames)
	print("minFrames: %d" % minFrames)
	print("maxFrames: %d" % maxFrames)
	
	segmentsArray = []
	for frameCount in range(minFrames, maxFrames + 1, 1):
		print("frameCount: %d" % frameCount)
		for frameStart in range(0, frameCount, 1):
			particalSegments = [(start, start+frameCount) for start in range(frameStart,int(video.duration*fps),frameCount)]
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


		'''
	Now we generate GIFs for some segments and show them
	'''
	# We need a directory to store the GIFs
	OUT_DIR=outputDir
	if not os.path.exists(OUT_DIR):
	    os.mkdir(OUT_DIR)

	# Generate GIFs from the top scoring segments
	gifCount = len(scores)
	print "gifs count:"
	print gifCount
	video2gif.generate_gifs(OUT_DIR,scores, video, video_name,top_k=topCount)

scriptStart=time.time()


list_dirs = os.walk(videosDir) 
for root, dirs, files in list_dirs:  
  for f in files: 
  	# Take the example video
    video_path = os.path.join(root, f)
    video_name=os.path.splitext(os.path.split(video_path)[1])[0]
    print video_path
    process_and_generate_gifs_with_frame(video_path, video_name)


print("total time took %.3fs" % time.time()-scriptStart)
	

