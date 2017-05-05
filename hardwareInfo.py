#-*- coding:utf-8 -*-
import os
from collections import namedtuple
import psutil

_ntuple_diskusage = namedtuple('usage', 'total used free')

def disk_usage(path):
    """Return disk usage statistics about the given path.

    Returned valus is a named tuple with attributes 'total', 'used' and
    'free', which are the amount of total, used and free space, in bytes.
    """
    st = os.statvfs(path)
    free = float(st.f_bavail * st.f_frsize) / 1024.0 / 1024.0 / 1024.0
    # total = float(st.f_blocks * st.f_frsize) / 1024.0 / 1024.0 / 1024.0
    # used = float((st.f_blocks - st.f_bfree) * st.f_frsize) / 1024.0 / 1024.0 / 1024.0
    return free


# gpu
def gpu_info():
	cmd = "nvidia-smi"
	info = os.popen(cmd)
	return info.read()


def cpu_usage():
	total_cpu=psutil.cpu_times().user+psutil.cpu_times().idle
	user_cpu=psutil.cpu_times().user
	cpu_syl=user_cpu/total_cpu*100
	 
	# mem = psutil.virtual_memory()   #使用psutil.virtual_memory方法获取内存完整信息
	# mem_total=mem.total
	# mem_used=mem.used
	# mem_syl=mem_used/float(mem_total)*100
	 
	# dis_syl= psutil.disk_usage('/').used/float (psutil.disk_usage('/').total)*100
	print cpu_syl
