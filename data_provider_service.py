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


import datetime
import sys
from time import sleep

from Models import Video
from Models import init_database


db_engine = create_engine('mysql+pymysql://root:@localhost:3306/video2gif?charset=utf8', isolation_level="READ UNCOMMITTED")
session_factory = sessionmaker(bind=db_engine)
Scope_Session = scoped_session(session_factory)

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

        db_sessionb = sessionmaker(bind=db_engine)

        db_sessionc = sessionmaker(bind=db_engine)

        db_sessiond = sessionmaker(bind=db_engine)

        db_sessione = sessionmaker(bind=db_engine)

        db_sessionf = sessionmaker(bind=db_engine)


        self.main_queue_session = db_session()

        self.no_caption_queue_session = db_sessionb()
        self.audio_queue_session = db_sessionc()
        self.upload_queue_session = db_sessiond()
        self.caption_loop_queue_session = db_sessione()
        self.caption_queue_session = db_sessionf()


        print self.main_queue_session, self.no_caption_queue_session, self.audio_queue_session, self.upload_queue_session, self.caption_loop_queue_session, self.caption_queue_session



        print 'init DataProviderService'

    def init_database(self):
        """
        Initializes the database tables and relationships
        :return: None
        """
        init_database(self.engine)

    def all_videos(self,currentsession, serialize=False):
        # sleep(0.1)
        # print currentsession
        # temp_session = Scope_Session()
        # print temp_session
        # videos = self.session.query(Video.name, Video.video_info, Video.status, Video.upload_time, Video.hash_name,Video.processed_time).filter(Video.status != -1).order_by(Video.upload_time)
        videos = currentsession.query(Video).filter(Video.status != -1).order_by(Video.upload_time)
        # Scope_Session.remove()
        if serialize:
            return [vi.mini_serialize() for vi in videos]
        else:
            return videos

    def get_video_by_hash_name(self,currentsession, hash_name, serialize=False):
        # sleep(0.2)
        print currentsession

        # temp_session = Scope_Session()
        # print temp_session
        videos = currentsession.query(Video).filter(Video.hash_name == hash_name).all()
        # Scope_Session.remove()
        if serialize:
            return [vi.serialize() for vi in videos]
        else:
            return videos

    def get_video_by_name(self,currentsession, name, serialize=False):
        # sleep(0.1)
        videos = currentsession.query(Video).filter(Video.name.like('%' + name + '%')).limit(1)

        if serialize:
            return [vi.serialize() for vi in videos]
        else:
            return videos

    def get_all_fetching_caption_videos(self,currentsession, serialize=False):
        # sleep(0.1)
        print currentsession
        # temp_session = Scope_Session()
        # print temp_session

        videos = currentsession.query(Video).filter(Video.status == 7).all()
        currentsession.commit()
        # Scope_Session.remove()
        if serialize:
            return [vi.serialize() for vi in videos]
        else:
            return videos




    def add_or_update_videos(self,currentsession, videos):
        # sleep(0.1)
        print currentsession
        # temp_session = Scope_Session()
        # print temp_session
        for vi in videos:
            currentsession.add(vi)

        currentsession.commit()

    def update_video(self,currentsession, video):  ## trick: 先查出来,再更新
        # sleep(0.1)
        print currentsession
        videos = currentsession.query(Video).filter(Video.id == video.id).all()
        if len(videos) > 0:
            vi = videos[0]
            new_vi = Video.sync_old_video(old_vi=vi, vi=video)
            currentsession.add(new_vi)
            currentsession.commit()

        print "update_video 借宿"


    def unprocessed_videos(self,currentsession, serialize=False):
        # sleep(0.1)
        videos = currentsession.query(Video).filter(Video.status != -1).order_by(Video.upload_time)
        if serialize:
            return [vi.serialize() for vi in videos]
        else:
            return videos

    def add_unprocessed_videos(self,currentsession, videos):
        # sleep(0.1)
        for vi in videos:
            currentsession.add(vi)
        result = currentsession.commit()
        return result







    ## temp
    # def update_video_with(self, video_dic):

