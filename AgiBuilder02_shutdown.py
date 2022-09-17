import os
import glob
import Metashape

FolderList = glob.glob("ReconOuput\\*")
#i = 0
for folder in FolderList:
    print("[LOG] Begin Process: " + folder)

    SavePath = os.path.join(folder, "AgiSoftOut")
    ProjectPach = os.path.join(SavePath, "Auto_Project.psz")
    MeshExportPath = os.path.join(SavePath, "mesh.obj")
    if not os.path.exists(ProjectPach):
        print("[ERROR] Folder: " + folder +" ProjectFile not found, Use Photo Align to Generate projectfile")
        continue
    print("[LOG] " + folder + "Begin Mesh Reconstruction")
    doc = Metashape.app.document
    doc.open(ProjectPach)
    chunk = doc.chunk
    #chunk.buildDepthMaps(downscale=4, filter_mode=Metashape.AggressiveFiltering)
    chunk.buildDepthMaps(downscale=2, filter_mode=Metashape.MildFiltering)
    #chunk.buildDepthMaps(downscale=1, filter_mode=Metashape.MildFiltering)
    #chunk.buildDenseCloud()
    doc.save(path = ProjectPach, chunks = [doc.chunk])

    chunk.buildDenseCloud(point_confidence = True)
    doc.save(path = ProjectPach, chunks = [doc.chunk])
    ##chunk.buildModel(surface_type=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation)
    chunk.buildModel(face_count = Metashape.FaceCount.CustomFaceCount, face_count_custom = 6000000, interpolation = Metashape.EnabledInterpolation)
    doc.save(path = ProjectPach, chunks = [doc.chunk])
    
    print("[LOG] " + folder + "Begin Texture Reconstruction")
    chunk.buildUV(mapping_mode=Metashape.GenericMapping)
    chunk.buildTexture(blending_mode=Metashape.MosaicBlending, texture_size=16384)
    #chunk.buildTexture(blending_mode=Metashape.AverageBlending, texture_size=8192)

    chunk.exportModel(MeshExportPath)

    doc.save(path = ProjectPach, chunks = [doc.chunk])

    doc.clear()

    print("[LOG] " + folder + "Reconstruction Finished")

    """
    i += 1
    if i >= 2:
        break
        """
os.system("shutdown /s /t 1")