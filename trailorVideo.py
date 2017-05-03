#-*- coding:utf-8 -*-
from IPython.display import Image, display
import os
from moviepy.editor import VideoFileClip
import sys

videoPath = './择天记02.mp4'

video = VideoFileClip(videoPath)
print video.fps


video_name=os.path.splitext(os.path.split(videoPath)[1])[0].decode('utf-8')
print video_name
print videoPath
video = VideoFileClip(videoPath)