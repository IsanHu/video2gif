#-*- coding:utf-8 -*-
from flask import jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import url_for

from data_provider_service import DataProviderService

import global_config

db_engine = global_config.config['db_engine']


DATA_PROVIDER = DataProviderService(db_engine)


def video_by_name(name):
    video = DATA_PROVIDER.get_video_by_name(name)
    if video:
        return jsonify({'video': video})
    else:
        abort(404)

def add_unprocessed_videos(videos):
    result = DATA_PROVIDER.add_unprocessed_videos(videos)
    return result

def all_videos():
    return DATA_PROVIDER.all_videos()

