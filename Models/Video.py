#-*- coding:utf-8 -*-
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Date
from Model import Model


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
        return {
            "id": self.id,
            "name": self.name,
            "hash_name": self.hash_name,
            "extension": self.extension,
            "status": self.status,
            "upload_time": self.upload_time,
            "update_time": self.update_time,
            "split_type": self.split_type,
            "processed_time": self.processed_time,
            "tag": self.tag,
            "caption": self.caption,
            "video_info": self.video_info
        }