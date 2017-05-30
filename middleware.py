#-*- coding:utf-8 -*-
from flask import jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import url_for

from data_provider_service import DataProviderService

db_engine = 'mysql+pymysql://isan:smart_isan@localhost:3306/video2gif?charset=utf8'


DATA_PROVIDER = DataProviderService(db_engine)


def video_by_name(name):
    video = DATA_PROVIDER.get_video_by_name(name, serialize=True)
    if video:
        return jsonify({'video': video})
    else:
        abort(404)
