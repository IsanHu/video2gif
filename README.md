# MGC
## 下载仓库中缺少的大文件
```
wget https://data.vision.ee.ethz.ch/gyglim/C3D/c3d_model.pkl -P ./data -nc
```

## 依赖
- python 2.7， 依赖包：./requirements
- [theano](http://deeplearning.net/software/theano/install_ubuntu.html)(相当于tensorflow的一个计算框架，最好按照文档中推荐的方式安装) 
- [cuda](http://docs.nvidia.com/cuda/cuda-installation-guide-linux/#axzz4VZnqTJ2A)
- [cuDNN](https://developer.nvidia.com/cudnn)

## 数据库
```
CREATE TABLE `video` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` tinytext NOT NULL,
  `hash_name` tinytext NOT NULL,
  `extension` tinytext NOT NULL COMMENT '文件后缀，暂时默认mp4',
  `status` tinyint(3) NOT NULL DEFAULT '0' COMMENT 'video目前的状态',
  `update_time` datetime NOT NULL COMMENT 'video 状态更新的时间',
  `upload_time` datetime NOT NULL COMMENT 'video 上传的时间',
  `split_type` tinyint(2) DEFAULT NULL COMMENT '分割video的类型 0：讯飞字幕；1：按固定时间间隔',
  `processed_time` datetime DEFAULT NULL COMMENT 'video 处理成功的时间',
  `tag` text COMMENT '处理时，设置的tag',
  `caption` longtext COMMENT 'video带时间轴的字幕',
  `video_info` text,
  `thumb_height` int(5) NOT NULL DEFAULT '0' COMMENT '可选的截图高度',
  `segment_duration` int(5) NOT NULL DEFAULT '0' COMMENT '按时间截图的时长',
  `is_chinese` tinyint(1) NOT NULL DEFAULT '0' COMMENT '视频音频是否是中文， 0：是；1：不是',
  `xunfei_id` text,
  `xunfei_upload_time` datetime DEFAULT NULL COMMENT '音频上传成功时间',
  `process_info` text COMMENT '处理过程记录',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10630 DEFAULT CHARSET=utf8mb4;
```

## 运行
配置./global_config中的 config['db_engine']（数据库地址）及 config['port']（服务端口）   
python ./app.py