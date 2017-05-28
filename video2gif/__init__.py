#-*- coding:utf-8 -*-
'''
This module contains functions to create the Video2GIF network and load the weights
as well as some helper functions, e.g. for generating the final GIF files.
For more information on the method, see

 Michael Gygli, Yale Song, Liangliang Cao
    "Video2GIF: Automatic Generation of Animated GIFs from Video," IEEE CVPR 2016
'''

__author__ = 'Michael Gygli'
import ConfigParser
import Queue
import collections
import numpy as np
import os
import threading
import time
from time import sleep
import model
import ctypes
import sys
try:
    import lasagne
    import theano
except (ImportError,AssertionError) as e:
    print(e.message)


reload(sys)

# Load the configuration
config=ConfigParser.SafeConfigParser()
print('Loaded config file from %s' % config.read('%s/config.ini' % os.path.dirname(__file__))[0])

# Load the mean snipplet (for mean subtraction)
snipplet_mean = np.load(config.get('paths','snipplet_mean'))

def get_prediction_function(feature_layer = None):
    '''
    Get prediction function (C3D and Video2GIF combined)
    @param feature_layer: a layer name (see model.py). If provided, pred_fn returns (score, and the activations at feature_layer)
    @return: theano function that scores sniplets
    '''
    print('Load weights and compile model...')

    # Build model
    net= model.build_model(batch_size=2)

    # Set the weights (takes some time)
    model.set_weights(net['score'],config.get('paths','c3d_weight_file'),config.get('paths','video2gif_weight_file'))
    layer='score'
    prediction = lasagne.layers.get_output(net[layer], deterministic=True)
    if feature_layer:
        features = lasagne.layers.get_output(net[feature_layer], deterministic=True)
        pred_fn = theano.function([net['input'].input_var], [prediction, features], allow_input_downcast = True)
    else:
        pred_fn = theano.function([net['input'].input_var], prediction, allow_input_downcast = True)


    return pred_fn

def get_scores(predict, segments, video, stride=8, with_features=False):
    '''
    Predict scores for segments using threaded loading
    (see https://github.com/Lasagne/Lasagne/issues/12#issuecomment-59494251)

    NOTE: Segments shorter than 16 frames (C3D input) don't get a prediction

    @param predict: prediction function
    @param segments: list of segment tuples
    @param video: moviepy VideoFileClip
    @param stride: stride of the extraction (8=50% overlap, 16=no overlap)
    @return: dictionary key: segment -> value: score
    '''

    queue = Queue.Queue(maxsize=50)
    sentinel = object()  # guaranteed unique reference

    def produce_input_data():
        '''
        Function to generate sniplets that serve as input to the network
        @return:
        '''
        frames=[]
        seg_nr=0
        for frame_idx, f in enumerate(video.iter_frames()):
            if frame_idx > segments[seg_nr][1]:
                seg_nr+=1
                if seg_nr==len(segments):
                    print "it's impossible"
                    break

                snip = model.get_snips(frames,snipplet_mean,0,True)
                queue.put((segments[seg_nr],snip))
                print "添加数据:"
                print seg_nr
                frames=[]

            frames.append(f)

        queue.put(sentinel)

    def get_input_data():
        '''
        Iterator reading snipplets from the queue
        @return: (segment,snip)
        '''
        # run as consumer (read items from queue, in current thread)
        item = queue.get()
        while item is not sentinel:
            yield item
            queue.task_done()
            item = queue.get()


    # start producer (in a background thread)
    thread = threading.Thread(target=produce_input_data)
    thread.daemon = True

    segment2score=collections.OrderedDict()

    extractStart=time.time()
    thread.start()
    print('Score segments...')
    print("Total %d segments" % len(segments))
    index = 0
    for segment,snip in get_input_data():
        # only add a segment, once we certainly get a prediction
        index = index + 1
        if segment not in segment2score:
            segment2score[segment]=[]

        scores=predict(snip)
        segment2score[segment].append(scores.mean(axis=0))
        if index % 10 == 0:
            print("first %d " % index)

    print("first count: %d " % index)

    index = 0
    for segment in segment2score.keys():
        index = index + 1
        print "segment scores count:"
        print len(segment2score[segment])
        segment2score[segment]=np.array(segment2score[segment]).mean(axis=0)
        print("second %d " % index)

    print("second count: %d " % index)

    print("Extracting scores for %d segments took %.3fs" % (len(segments),time.time()-extractStart))
    return segment2score

def is_overlapping(x1,x2,y1,y2):
    return max(x1,y1) < min(x2,y2)

def generate_gifs(out_dir, segment2scores, video, video_id, top_k=6):
    '''
    @param out_dir: directory where the GIFs are written to
    @param segment2scores: a dict with segments (start frame, end frame) as keys and the segment score as value
    @param video: a VideoFileClip object
    @param video_id: the identifier of the video (used for naming the GIFs)
    @return:
    '''
    segment2scores = segment2scores.copy()

    nr=0
    totalCount = len(segment2scores)
    top_k=min(top_k, totalCount)
    occupiedTime = []

    for segment in sorted(segment2scores, key=lambda x: -segment2scores.get(x))[0:totalCount]:
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
            clip = video.subclip(segment[0]/float(video.fps), segment[1]/float(video.fps))
            out_gif = "%s/%s_%.2d.gif" % (out_dir.decode('utf-8'),video_id.decode('utf-8'),nr)
            ## resize
            clip=clip.resize(width=500)
            clip.write_gif(out_gif,fps=10)
            nr += 1
