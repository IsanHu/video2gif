#!/usr/bin/python
# coding=utf-8

import paramiko
import os

def sftp_upload(host,port,username,password,local,remote):
    sf = paramiko.Transport((host,port))
    sf.connect(username = username,password = password)
    sftp = paramiko.SFTPClient.from_transport(sf)
    try:
        if os.path.isdir(local):#判断本地参数是目录还是文件
            for f in os.listdir(local):#遍历本地目录
                sftp.put(os.path.join(local+f),os.path.join(remote+f), callback=)#上传目录中的文件
        else:
            sftp.put(local,remote)#上传文件
    except Exception,e:
        print('upload exception:',e)
    sf.close()

def sftp_download(host,port,username,password,local,remote):
    sf = paramiko.Transport((host,port))
    sf.connect(username = username,password = password)
    sftp = paramiko.SFTPClient.from_transport(sf)
    try:
        if os.path.isdir(local):#判断本地参数是目录还是文件
            for f in sftp.listdir(remote):#遍历远程目录
                 sftp.get(os.path.join(remote+f),os.path.join(local+f))#下载目录中文件
        else:
            sftp.get(remote,local)#下载文件
    except Exception,e:
        print('download exception:',e)
    sf.close()

host = 'localhost'#主机
port = 22 #端口
username = 'isan' #用户名
password = 'smart_isan' #密码
local = '/Users/isan/sftptest/local/'#本地文件或目录
remote = '/Users/isan/sftptest/remote/'
sftp_upload(host,port,username,password,local,remote)#上传

#sftp_download(host,port,username,password,local,remote)#下载

    
    