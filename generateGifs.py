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
import json
import time

reload(sys)
print sys.getdefaultencoding()
sys.setdefaultencoding('utf8')


videosDir = sys.argv[1]
topCount = int(sys.argv[2])
clipDuration = int(sys.argv[3])
outputDir = sys.argv[4]


def process_and_generate_gifs(video_path, video_name):
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

	# print "print scores:"
	# print scores
	# print "write scores to scores.log"
	# logfile = open("scores.log", "wb")
	# logfile.write(json.dumps(scores))
	# logfile.close


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
    process_and_generate_gifs(video_path, video_name)

print("total time took %.3fs" % (time.time()-scriptStart))
	

