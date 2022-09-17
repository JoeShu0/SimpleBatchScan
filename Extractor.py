import os
import glob

ffmpeg =  ".\\ffmpeg-master-latest-win64-lgpl\\bin\\ffmpeg.exe"

VideoList = glob.glob(".\\InputFolder\\*.mp4")
OutputPath = "ReconOuput"
#print(VideoList)
for video in VideoList:
    ExtractFolderName = video.rsplit("\\")[-1].rsplit(".")[0]
    ExtractFolder = os.path.join(OutputPath, ExtractFolderName)
    os.makedirs(ExtractFolder, exist_ok = True)
    ExtractPath = os.path.join(ExtractFolder, "ffmpeg_%0d.png")
    CMD = ffmpeg
    CMD += " -i " + video
    #CMD += " -filter:v fps=2 -vsync 0 " 
    CMD += " -r 5 -q:v 1 "
    CMD += ExtractPath
    print(CMD)
    os.system(CMD)



# .\ffmpeg-master-latest-win64-lgpl\bin\ffmpeg.exe -i .\InputFolder\PRO_VID_20220618_065446_00_015.mp4  -filter:v fps=2 .\InputFolder\PRO_VID_20220618_065446_00_015\ffmpeg_%0d.bmp
#D:\"Program Files"\Agisoft\"Metashape Pro"\python\python.exe Extractor.py