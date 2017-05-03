from IPython.display import Image, display
import os
from moviepy.editor import VideoFileClip
import sys
import Queue

def produce_data(video):
	segmentsArray = []
	queue = Queue.Queue(maxsize=500)
	sentinel = object()  # guaranteed unique reference
	for videoStart in range(0, 2, 1):
		print "videoStart:"
		print videoStart
		particalSegments = [(start, int(start+video.fps*2)) for start in range(int(videoStart*video.fps),int(video.duration*video.fps),int(video.fps*2))]
		seg_nr=0		
		frames=[]

	    for frame_idx, f in enumerate(video.iter_frames()):
	        if frame_idx > particalSegments[seg_nr][1]:
	            seg_nr+=1
	            if seg_nr==len(particalSegments):
	                break
	            frames=[]

	        frames.append(f)

	        if len(frames)==16: # Extract scores
	            start=time.time()
	            snip = model.get_snips(frames,snipplet_mean,0,True)
	            queue.put((particalSegments[seg_nr],snip))
	            print "put data to queue"
	            frames=frames[stride:] # shift by 'stride' frames
	    queue.put(sentinel)





videosDir = sys.argv[1]

list_dirs = os.walk(videosDir) 
for root, dirs, files in list_dirs:  
  for f in files: 
  	# Take the example video
    video_path = os.path.join(root, f)
    video_name=os.path.splitext(os.path.split(video_path)[1])[0].decode('utf-8')
    print video_path
    video = VideoFileClip(video_path)
    produce_data(video)
    





    
        