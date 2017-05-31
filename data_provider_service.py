#-*- coding:utf-8 -*-
# coding=utf8
from flask import jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import url_for

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


import datetime
import sys

from Models import Video
from Models import init_database


class DataProviderService:
    def __init__(self, engine):
        """
        :param engine: The engine route and login details
        :return: a new instance of DAL class
        :type engine: string
        """
        if not engine:
            raise ValueError('The values specified in engine parameter has to be supported by SQLAlchemy')
        self.engine = engine
        db_engine = create_engine(engine, isolation_level="READ UNCOMMITTED")
        db_session = sessionmaker(bind=db_engine)
        self.session = db_session()
        print 'init DataProviderService'

    def init_database(self):
        """
        Initializes the database tables and relationships
        :return: None
        """
        init_database(self.engine)

    def all_videos(self, serialize=False):
        # videos = self.session.query(Video.name, Video.video_info, Video.status, Video.upload_time, Video.hash_name,Video.processed_time).filter(Video.status != -1).order_by(Video.upload_time)
        videos = self.session.query(Video).filter(Video.status != -1).order_by(Video.upload_time)
        if serialize:
            return [vi.mini_serialize() for vi in videos]
        else:
            return videos

    def unprocessed_videos(self, serialize=False):
        videos = self.session.query(Video).filter(Video.status != -1).order_by(Video.upload_time)
        if serialize:
            return [vi.serialize() for vi in videos]
        else:
            return videos


    def get_video_by_name(self, name, serialize=False):

        videos = self.session.query(Video).filter(Video.name.like('%' + name + '%')).limit(1)

        if serialize:
            return [vi.serialize() for vi in videos]
        else:
            return videos


    def excute_temp_sql(self, sql):
        result = self.session.execute(sql)
        return result

    def add_unprocessed_videos(self, videos):
        for vi in videos:
            self.session.add(vi)
        result = self.session.commit()
        return result

