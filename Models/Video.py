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
    thumb_height = Column(Integer, nullable=False, default=0)
    segment_duration = Column(Integer, nullable=False, default=0)
    is_chinese = Column(Integer, nullable=False, default=0)
    xunfei_id = Column(String(45), nullable=True)
    xunfei_upload_time = Column(Date, nullable=True)
    process_info = Column(String(1024), nullable=False, default='')


    @classmethod
    def get_new_instance(cls, vi):
        new_vi = Video(id=vi.id,
                   name=vi.name,
                   hash_name=vi.hash_name,
                   extension=vi.extension,
                   status=vi.status,
                   update_time=vi.update_time,
                   upload_time=vi.upload_time,
                   processed_time=vi.processed_time,
                   split_type=vi.split_type,
                   caption=vi.caption,
                   video_info=vi.video_info,
                   tag=vi.tag,
                   thumb_height=vi.thumb_height,
                   segment_duration=vi.segment_duration,
                   is_chinese=vi.is_chinese,
                   xunfei_id=vi.xunfei_id,
                   xunfei_upload_time=vi.xunfei_upload_time,
                   process_info=vi.process_info,

                   )
        return new_vi

    @classmethod
    def sync_old_video(cls, old_vi, vi):
        old_vi.id = vi.id,
        old_vi.name = vi.name,
        old_vi.hash_name = vi.hash_name,
        old_vi.extension = vi.extension,
        old_vi.status = vi.status,
        old_vi.update_time = vi.update_time,
        old_vi.upload_time = vi.upload_time,
        old_vi.processed_time = vi.processed_time,
        old_vi.split_type = vi.split_type,
        old_vi.caption = vi.caption,
        old_vi.video_info = vi.video_info,
        old_vi.tag = vi.tag,
        old_vi.thumb_height = vi.thumb_height,
        old_vi.segment_duration = vi.segment_duration,
        old_vi.is_chinese = vi.is_chinese,
        old_vi.xunfei_id = vi.xunfei_id,
        old_vi.xunfei_upload_time = vi.xunfei_upload_time
        old_vi.process_info = vi.process_info,

        return old_vi


    @classmethod
    def get_video_from_dic(cls, viDic):
        new_vi = Video(id=viDic["id"],
                   name=viDic["name"],
                   hash_name=viDic["hash_name"],
                   extension=viDic["extension"],
                   status=viDic["status"],
                   update_time=viDic["update_time"],
                   upload_time=viDic["upload_time"],
                   processed_time=viDic["processed_time"],
                   split_type=viDic["split_type"],
                   caption=viDic["caption"],
                   video_info=viDic["video_info"],
                   tag=viDic["tag"],
                   thumb_height=viDic["thumb_height"],
                   segment_duration=viDic["segment_duration"],
                   is_chinese=viDic["is_chinese"],
                   xunfei_id=viDic["xunfei_id"],
                   xunfei_upload_time=viDic["xunfei_upload_time"],
                   process_info=viDic["process_info"],
                   )
        return new_vi


    def serialize(self):
        tag_str = self.tag
        if tag_str != "":
            tag_str = json.loads(tag_str)

        caption_str = self.caption
        if caption_str != "":
            caption_str = json.loads(caption_str)

        process_info_str = self.process_info
        if process_info_str != "":
            process_info_str = json.loads(process_info_str)

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
            "video_info": json.loads(self.video_info),
            "thumb_height":self.thumb_height,
            "segment_duration": self.segment_duration,
            "is_chinese": self.is_chinese,
            "xunfei_id": self.xunfei_id,
            "xunfei_upload_time": self.xunfei_upload_time,
            "process_info":process_info_str
        }


    def mini_serialize(self):
        process_info_str = self.process_info
        if process_info_str != "":
            process_info_str = json.loads(process_info_str)

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
                "gif_info": self.gif_info(),
                "thumb_height": self.thumb_height,
                "segment_duration": self.segment_duration,
                "is_chinese": self.is_chinese,
                "xunfei_id": self.xunfei_id,
                "process_info":process_info_str
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
            "video_info": json.loads(self.video_info),
            "thumb_height": self.thumb_height,
            "segment_duration": self.segment_duration,
            "is_chinese": self.is_chinese,
            "xunfei_id": self.xunfei_id,
            "process_info":process_info_str
        }

    def status_info(self):
        video_status = {-1: "已删除", 0: "尚未处理", 1: "已处理", 2: "排队等待处理中", 3: "处理中", 4: "提取音频中", 5:"提取音频成功", 6:"上传音频中", 7:"上传音频成功",8:"获取字幕中", 9:"获取字幕成功", 33:"假装处理完了"}
        return video_status[self.status]

    def ziped_gif_info(self):
        ziped_gif_info = {}
        ziped_gif_file_name = self.hash_name + ".zip"
        ziped_gif_path = os.path.join(config['ZIPED_GIF_FOLDER'], ziped_gif_file_name)
        ziped_gif_size = round(float(os.path.getsize(ziped_gif_path)) / 1024.0 / 1024.0, 2)

        ziped_gif_info['download_url'] = "zipedgif/%s" % ziped_gif_file_name
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


