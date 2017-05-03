#-*- coding:utf-8 -*-
from IPython.display import Image, display
import os
from moviepy.editor import VideoFileClip
import sys


videosDir = sys.argv[1]
verify_dir = './gifs/verify'
if not os.path.exists(verify_dir):
        os.mkdir(verify_dir)

list_dirs = os.walk(videosDir) 
for root, dirs, files in list_dirs:  
  for f in files: 
  	# Take the example video
    video_path = os.path.join(root, f)
    video_name=os.path.splitext(os.path.split(video_path)[1])[0].decode('utf-8')
    print video_path
    video = VideoFileClip(video_path)
    print "fps:"
    print video.fps

    clip = video.subclip('0:00:14.88', '0:00:17.28')
    out_gif = "%s/%s_%.2d.gif" % (verify_dir, video_name, 1)
    clip = clip.resize(height=240)
    clip.write_gif(out_gif, fps=5)