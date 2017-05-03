#-*- coding:utf-8 -*-
import gc
from flask import Flask, request, jsonify, render_template
from werkzeug import secure_filename
from routes import init_route
# import cv2
import numpy as np
from PIL import Image, ImageSequence
import os
import sys
from hash_utils import Hash
from image_hash_utils import ImageAhash
import imagehash
import requests
from StringIO import StringIO
import datetime

reload(sys)
print sys.getdefaultencoding()
sys.setdefaultencoding('utf8')


app = Flask(__name__)
init_route(app)


@app.route('/upload', methods=['POST'])
def upload():
    images = []
    basedir = os.path.abspath(os.path.dirname(__file__))
    updir = os.path.join(basedir, 'static/upload/')
    files = request.files
    # print files
    index = 0
    for f in files:
        file = files[f]
        filename = secure_filename(file.filename)
        print file
        file.save(os.path.join(updir, filename))
        print "file path:"
        print os.path.join(updir, filename)
        file_size = os.path.getsize(os.path.join(updir, filename))

    return render_template('result.html', results='上传成功')

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', debug=True)
    # app.run(host='0.0.0.0', port=5555)

