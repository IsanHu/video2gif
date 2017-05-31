#-*- coding:utf-8 -*-
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Date
from Model import Model
import json
import os

config = {}
basedir = os.path.abspath(os.path.dirname(__file__)) + "/.."
config['UPLOAD_FOLDER'] = basedir + '/unprocessedvideos/'
config['PROCESSED_FOLDER'] = basedir + '/processedvideos/'
config['THUMBNAIL_FOLDER'] = basedir + '/unprocessedvideos/thumbnail/'
config['GIF_FOLDER'] = basedir + '/static/gifs/'
config['ORIGINAL_GIF_FOLDER'] = basedir + '/static/original_gifs/'
config['BOTTLENECK'] = basedir + '/bottleneck/'
config['ZIPED_GIF_FOLDER'] = basedir + '/zipedgifs/'

class Video(Model):
    __tablename__ = 'video'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False, default='')
    hash_name = Column(String(45), nullable=False, default='')
    extension = Column(String(6), nullable=False, default='')
    status = Column(Integer, nullable=False)
    upload_time = Column(Date, nullable=False)
    update_time = Column(Date, nullable=False)
    split_type = Column(Integer, nullable=True)
    processed_time = Column(Date, nullable=True)
    tag = Column(String(512), nullable=False, default='')
    caption = Column(String(512*1024), nullable=False, default='')
    video_info = Column(String(512), nullable=False, default='')



    def serialize(self):
        tag_str = self.tag
        if tag_str != "":
            json.loads(tag_str)
        caption_str = self.caption
        if caption_str != "":
            json.loads(caption_str)
        return {
            "id": self.id,
            "name": self.name,
            "hash_name": self.hash_name,
            "extension": self.extension,
            "status": self.status,
            "status_info": self.status_info(),
            "upload_time": str(self.upload_time),
            "update_time": str(self.update_time),
            "split_type": self.split_type,
            "processed_time": str(self.processed_time),
            "tag": tag_str,
            "caption": caption_str,
            "video_info": json.loads(self.video_info)
        }


    def mini_serialize(self):
        if self.status == 1:

            return {
                "id": self.id,
                "name": self.name,
                "hash_name": self.hash_name,
                "extension": self.extension,
                "status": self.status,
                "status_info": self.status_info(),
                "upload_time": str(self.upload_time),
                "update_time": str(self.update_time),
                "split_type": self.split_type,
                "processed_time": str(self.processed_time),
                "video_info": json.loads(self.video_info),
                "ziped_gif_info": self.ziped_gif_info(),
                "gif_info": self.gif_info()
            }
        return {
            "id": self.id,
            "name": self.name,
            "hash_name": self.hash_name,
            "extension": self.extension,
            "status": self.status,
            "status_info":self.status_info(),
            "upload_time": str(self.upload_time),
            "update_time": str(self.update_time),
            "split_type": self.split_type,
            "processed_time": str(self.processed_time),
            "video_info": json.loads(self.video_info)
        }

    def status_info(self):
        video_status = {-1: "已删除", 0: "尚未处理", 1: "已处理", 2: "排队处理中", 3: "处理中"}
        return video_status[self.status]

    def ziped_gif_info(self):
        ziped_gif_info = {}
        ziped_gif_file_name = self.hash_name + ".zip"
        ziped_gif_path = os.path.join(config['ZIPED_GIF_FOLDER'], ziped_gif_file_name)
        ziped_gif_size = round(float(os.path.getsize(ziped_gif_path)) / 1024.0 / 1024.0, 2)

        ziped_gif_info['download_url'] = "zipedgif/%s" % self.name
        ziped_gif_info['size'] = "%.2fM" % ziped_gif_size
        print ziped_gif_info
        return ziped_gif_info

    def gif_info(self):
        gif_info = {}
        gifs_dir = config['GIF_FOLDER'] + self.hash_name
        gif_count = 0
        if os.path.isdir(gifs_dir):
            gif_info['gifs_dir'] = "gifs/%s" % self.hash_name
            for f in os.listdir(gifs_dir):
                if f.rsplit(".", 1)[1].lower() == "gif":
                    gif_count += 1
        gif_info['gif_count'] = gif_count
        print gif_info
        return gif_info


