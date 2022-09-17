import os
import sys
import glob
import rawpy
import matplotlib.pyplot as plt
import numpy as np
import cv2
import imageio
from random import randint

RawInputFolder = "InputFolder"
#".\\InputFolder\\*.ARW"

OutputPath = "ReconOuput\\Temp"



from multiprocessing import Process, Pool
import os, time
import multiprocessing
cpus = multiprocessing.cpu_count()


class PoolProgress:
  def __init__(self,pool,update_interval=10):
    self.pool            = pool
    self.update_interval = update_interval
  def track(self, job):
    task = self.pool._cache[job._job]
    while task._number_left>0:
      print("Tasks remaining = {0}".format(task._number_left*task._chunksize), end = "\r")
      time.sleep(self.update_interval)

def track_job(job, update_interval=3):
    while job._number_left > 0:
        print("Tasks remaining = {0}".format(
        job._number_left * job._chunksize), end = "\r")
        time.sleep(update_interval)

def main_map(i):
    result = i * i
    time.sleep(1)
    print(result)
    return result

def RawProcess(RawPath):
    time.sleep(randint(0, 5))

    RawName = RawPath.rsplit("\\")[-1].rsplit(".")[0]
    ProcessedPath = os.path.join(OutputPath, RawName+".jpg")

    raw = rawpy.imread(RawPath)
    #imaged3 = raw.postprocess(use_camera_wb=True, output_color=rawpy.ColorSpace.sRGB, output_bps=8,exp_shift=0.125)
    imaged2 = raw.postprocess(use_camera_wb=True, output_color=rawpy.ColorSpace.sRGB, output_bps=8,exp_shift=0.25)
    #imaged1 = raw.postprocess(use_camera_wb=True, output_color=rawpy.ColorSpace.sRGB, output_bps=8,exp_shift=0.5)
    image0 = raw.postprocess(use_camera_wb=True, output_color=rawpy.ColorSpace.sRGB,  output_bps=8,exp_shift=1)
    #imageb1 = raw.postprocess(use_camera_wb=True, output_color=rawpy.ColorSpace.sRGB, output_bps=8,exp_shift=2)
    imageb2 = raw.postprocess(use_camera_wb=True, output_color=rawpy.ColorSpace.sRGB, output_bps=8,exp_shift=4)
    #imageb3 = raw.postprocess(use_camera_wb=True, output_color=rawpy.ColorSpace.sRGB, output_bps=8,exp_shift=8)

    img_list = [imaged2,image0,imageb2]

    merge_mertens = cv2.createMergeMertens(1.0,10.0,5.0)
    res_mertens = merge_mertens.process(img_list)

    imageio.imsave(ProcessedPath, np.uint8(np.clip(res_mertens*255,0,255)), quality=100)
    
    #print(RawPath + " 处理结束")
    

if __name__ == '__main__':
    start = time.time()
    RawList = glob.glob(os.path.join(RawInputFolder, "*.ARW"))
    #print(RawList)
    os.makedirs(OutputPath, exist_ok = True)

    pool = Pool(16)#进程数
    #PProgress = PoolProgress(pool)
    pool_outputs = pool.map_async(RawProcess, RawList)

    print("Raw处理开始")
    #PProgress.track(pool_outputs)
    track_job(pool_outputs)

    # close 保证不会有新的任务加入到pool中
    pool.close()
    # join 使得主进程会在所有子进程结束之后再结束
    pool.join()

    

    print("Raw处理结束")
    end = time.time()

    ProcessTime = end - start
    TimePerTask = ProcessTime/len(RawList)
    print('总处理时间： %.2f 秒.' % (ProcessTime))
    print('平均每张处理时间： %.2f 秒.' % (TimePerTask))

    """
    inputs = [0, 1, 2, 3]
    pool = Pool(4)

    # Map async 非阻塞式线程池
    pool_outputs = pool.map_async(main_map, inputs)
    print(" pool.map main block")

    # close 保证不会有新的任务加入到pool中
    pool.close()
    # join 使得主进程会在所有子进程结束之后再结束
    pool.join()

    print(" pool.map main block finished")
    """