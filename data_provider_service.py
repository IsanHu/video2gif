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

        db_engineb = create_engine(engine, isolation_level="READ UNCOMMITTED")
        db_sessionb = sessionmaker(bind=db_engineb)

        db_enginec = create_engine(engine, isolation_level="READ UNCOMMITTED")
        db_sessionc = sessionmaker(bind=db_enginec)

        db_engined = create_engine(engine, isolation_level="READ UNCOMMITTED")
        db_sessiond = sessionmaker(bind=db_engined)

        db_enginee = create_engine(engine, isolation_level="READ UNCOMMITTED")
        db_sessione = sessionmaker(bind=db_enginee)

        db_enginef = create_engine(engine, isolation_level="READ UNCOMMITTED")
        db_sessionf = sessionmaker(bind=db_enginef)


        self.main_queue_session = db_session()

        self.no_caption_queue_session = db_sessionb()
        self.audio_queue_session = db_sessionc()
        self.upload_queue_session = db_sessiond()
        self.caption_loop_queue_session = db_sessione()
        self.caption_queue_session = db_sessionf()



        print 'init DataProviderService'

    def init_database(self):
        """
        Initializes the database tables and relationships
        :return: None
        """
        init_database(self.engine)

    def all_videos(self,currentsession, serialize=False):
        # videos = self.session.query(Video.name, Video.video_info, Video.status, Video.upload_time, Video.hash_name,Video.processed_time).filter(Video.status != -1).order_by(Video.upload_time)
        videos = currentsession.query(Video).filter(Video.status != -1).order_by(Video.upload_time)
        if serialize:
            return [vi.mini_serialize() for vi in videos]
        else:
            return videos

    def get_video_by_hash_name(self,currentsession, hash_name, serialize=False):

        videos = currentsession.query(Video).filter(Video.hash_name == hash_name).all()
        if serialize:
            return [vi.serialize() for vi in videos]
        else:
            return videos

    def get_video_by_name(self,currentsession, name, serialize=False):

        videos = currentsession.query(Video).filter(Video.name.like('%' + name + '%')).limit(1)

        if serialize:
            return [vi.serialize() for vi in videos]
        else:
            return videos

    def get_all_fetching_caption_videos(self,currentsession, serialize=False):
        videos = currentsession.query(Video).filter(Video.status == 7).all()
        if serialize:
            return [vi.serialize() for vi in videos]
        else:
            return videos




    def add_or_update_videos(self,currentsession, videos):
        for vi in videos:
            currentsession.add(vi)
        result = currentsession.commit()
        return result

    def unprocessed_videos(self,currentsession, serialize=False):
        videos = currentsession.query(Video).filter(Video.status != -1).order_by(Video.upload_time)
        if serialize:
            return [vi.serialize() for vi in videos]
        else:
            return videos

    def add_unprocessed_videos(self,currentsession, videos):
        for vi in videos:
            currentsession.add(vi)
        result = currentsession.commit()
        return result

