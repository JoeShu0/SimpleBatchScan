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
    MeshExportPath = os.path.join(SavePath, "mesh.obj")
    if not os.path.exists(ProjectPach):
        print("[ERROR] Folder: " + folder +" ProjectFile not found, Use Photo Align to Generate projectfile")
        continue
    print("[LOG] " + folder + "Begin Mesh And Tex Reconstruction")


    cmd = RCPath
    
    cmd += " -load " + os.path.abspath(ProjectPach)
    cmd += " -mvs " #" -calculateNormalModel "
    #cmd += " -mvsHigh"
    #cmd += " -modelSelectMarginalTriangles " # " -selectMarginalTriangles "
    #cmd += " -modelRemoveSelectedTriangles " # " -removeSelectedTriangles "

    cmd += " -renameModel " + "OriginalMesh" # " -renameSelectedModel "
    cmd += " -closeHoles "
    

    cmd += " -simplify " + str(5000000)
    cmd += " -renameModel " + "SimpleMesh"

    cmd += " -calculateTexture "
    cmd += " -exportModel " + "SimpleMesh " + os.path.abspath(MeshExportPath) + " " + os.path.abspath("exportParams.xml")

    cmd += " -save " + os.path.abspath(ProjectPach)
    cmd += " -quit"
    os.system(cmd)

    print("[LOG] " + folder + "Reconstruction Finished")

os.system("shutdown /s /t 1")