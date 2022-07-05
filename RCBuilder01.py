import os
import glob

RCPath = 'D:\\"Program Files"\\"Capturing Reality"\RealityCapture\RealityCapture.exe'

#cmd = RCPath
#cmd += " -addFolder " + "D:\Projects\SimpleBatchScan\ReconOuput\BikeMark"
#os.system(cmd)

FolderList = glob.glob("ReconOuput\\*")
#i = 0
for folder in FolderList:
    #
    print("[LOG] Begin Process: " + folder)

    SavePath = os.path.join(folder, "RCOutput")
    ProjectPach = os.path.join(SavePath, "project.rcproj")
    if os.path.exists(ProjectPach):
        print("[LOG] " + folder + "ProjectFile Exist:" + ProjectPach)
        continue
    print("[LOG] " + folder + "Begin Photo Align")
    PhotoListPNG = glob.glob(os.path.join(folder, "*.png"))
    PhotoListJPG = glob.glob(os.path.join(folder, "*.JPG"))
    if(not PhotoListPNG) and (not PhotoListJPG):
        print("[ERROR] No JPG or png in Folder: " + folder)
        continue
    os.makedirs(SavePath, exist_ok = True)

    cmd = RCPath
    cmd += " -addFolder " + os.path.abspath(folder)
    cmd += " -align "
    cmd += " -setReconstructionRegionAuto "
    cmd += " -save " + os.path.abspath(ProjectPach)
    cmd += " -quit"
    os.system(cmd)

    print("[LOG] " + folder + "Photo Align Finished")
    """
    i += 1
    if i >= 2:
        break
        """