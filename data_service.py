#-*- coding:utf-8 -*-
# coding=utf8
from flask import jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import url_for

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
from sqlalchemy import func
import time
import datetime
import sys
import math
import global_config

from Models import Video
from Models import init_database

db_engine = create_engine(global_config.config['db_engine'], isolation_level="READ UNCOMMITTED")
session_factory = sessionmaker(bind=db_engine)
Scope_Session = scoped_session(session_factory)

per_page = 10

class DataService:
    def __init__(self, engine):
        """
        :param engine: The engine route and login details
        :return: a new instance of DAL class
        :type engine: string
        """
        if not engine:
            raise ValueError('The values specified in engine parameter has to be supported by SQLAlchemy')
        print 'init DataService'

    def init_database(self):
        """
        Initializes the database tables and relationships
        :return: None
        """
        init_database(self.engine)

    def videos_at_page(self, page=1, key="", serialize=False):
        try:
            offset = (page - 1) * per_page
            temp_session = Scope_Session()
            # count = temp_session.query(func.count(Video.status != -1))
            count = temp_session.query(Video).filter(Video.status != -1, Video.name.like('%' + key + '%')).count()
            page_count = int(math.ceil(count / float(per_page)))
            print page_count
            if page_count == 0:
                page_count = 1

            page_indexs = [(i + 1) for i in range(page_count)]
            current_page = page

            videos = temp_session.query(Video).filter(Video.status != -1, Video.name.like('%' + key + '%')).order_by(Video.upload_time.desc()).offset(offset).limit(per_page)
            clean_videos = [Video.get_new_instance(vi) for vi in videos]
            Scope_Session.remove()
            if serialize:
                return [vi.mini_serialize() for vi in clean_videos], page_indexs, current_page
            else:
                return clean_videos, page_indexs, current_page
        except (Exception) as e:
            print "抓到exception"
            print "all_videos 操作失败"
            print e.message
            return [], [], 1


    def all_videos(self, serialize=False):
        try:
            temp_session = Scope_Session()
            start = time.time()
            videos = temp_session.query(Video).filter(Video.status != -1).order_by(Video.upload_time.desc()).offset(40).limit(10)
            print videos
            print("查询所有video用时: %.2fs" % (time.time() - start))

            new_start = time.time()
            count = temp_session.query(Video).filter(Video.status != -1).count()
            print count
            print("查询总共有多少video用时: %.2fs" % (time.time() - new_start))

            new_start = time.time()
            count = temp_session.query(func.count(Video.status != -1))
            print count
            print("新方式查询总共有多少video用时: %.2fs" % (time.time() - new_start))

            clean_videos = [Video.get_new_instance(vi) for vi in videos]
            Scope_Session.remove()
            if serialize:
                return [vi.mini_serialize() for vi in clean_videos]
            else:
                return clean_videos
        except (Exception) as e:
            print "抓到exception"
            print "all_videos 操作失败"
            print e.message
            return []

    def get_video_by_hash_name(self, hash_name, serialize=False):
        try:
            temp_session = Scope_Session()
            videos = temp_session.query(Video).filter(Video.hash_name == hash_name).all()
            clean_videos = [Video.get_new_instance(vi) for vi in videos]
            Scope_Session.remove()
            if serialize:
                return [vi.serialize() for vi in clean_videos]
            else:
                return clean_videos
        except (Exception) as e:
            print "抓到exception"
            print e.message
            print "get_video_by_hash_name 操作失败"


    def get_video_by_name(self, name, serialize=False):
        try:
            temp_session = Scope_Session()
            videos = temp_session.query(Video).filter(Video.name.like('%' + name + '%')).limit(1)
            clean_videos = [Video.get_new_instance(vi) for vi in videos]
            Scope_Session.remove()
            if serialize:
                return [vi.serialize() for vi in clean_videos]
            else:
                return clean_videos
        except (Exception) as e:
            print "抓到exception"
            print e.message
            print "get_video_by_name 操作失败"


    def get_all_fetching_caption_videos(self, serialize=False):
        try:
            temp_session = Scope_Session()
            videos = temp_session.query(Video).filter(Video.status == 7).all()
            clean_videos = [Video.get_new_instance(vi) for vi in videos]
            Scope_Session.remove()
            if serialize:
                return [vi.serialize() for vi in clean_videos]
            else:
                return clean_videos
        except (Exception) as e:
            print "抓到exception"
            print "get_all_fetching_caption_videos 操作失败"
            print e.message


    def update_video(self, video):  ## trick: 先查出来,再更新
        try:
            temp_session = Scope_Session()
            videos = temp_session.query(Video).filter(Video.id == video.id).all()
            if len(videos) > 0:
                vi = videos[0]
                vi = Video.sync_old_video(old_vi=vi, vi=video)
                temp_session.add(vi)
                temp_session.commit()
            Scope_Session.remove()
        except (Exception) as e:
            print "抓到exception"
            print "update_video 操作失败"
            print e.message


    def add_unprocessed_videos(self, videos):
        temp_session = Scope_Session()
        for vi in videos:
            temp_session.add(vi)
        temp_session.commit()
        Scope_Session.remove()



DATA_PROVIDER = DataService(global_config.config['db_engine'])