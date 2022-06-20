import os
import glob
import Metashape

FolderList = glob.glob("ReconOuput\\*")
#i = 0
for folder in FolderList:
    print("[LOG] Begin Process: " + folder)

    SavePath = os.path.join(folder, "AgiSoftOut")
    ProjectPach = os.path.join(SavePath, "Auto_Project.psz")
    if not os.path.exists(ProjectPach):
        print("[ERROR] Folder: " + folder +" ProjectFile not found, Use Photo Align to Generate projectfile")
        continue
    print("[LOG] " + folder + "Begin Mesh Reconstruction")
    doc = Metashape.app.document
    doc.open(ProjectPach)
    chunk = doc.chunk
    #chunk.buildDepthMaps(downscale=4, filter_mode=Metashape.AggressiveFiltering)
    chunk.buildDepthMaps(downscale=2, filter_mode=Metashape.MildFiltering)
    #chunk.buildDenseCloud()
    chunk.buildDenseCloud(point_confidence = True)
    ##chunk.buildModel(surface_type=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation)
    chunk.buildModel(face_count = Metashape.FaceCount.CustomFaceCount, face_count_custom = 4000000)
    print("[LOG] " + folder + "Begin Texture Reconstruction")
    chunk.buildUV(mapping_mode=Metashape.GenericMapping)
    #chunk.buildTexture(blending_mode=Metashape.MosaicBlending, texture_size=8192)
    chunk.buildTexture(blending_mode=Metashape.AverageBlending, texture_size=8192)
    doc.save(path = ProjectPach, chunks = [doc.chunk])
    doc.clear()

    print("[LOG] " + folder + "Reconstruction Finished")

    """
    i += 1
    if i >= 2:
        break
        """
"""
doc = Metashape.app.document

chunk = doc.addChunk()
PhotoList = glob.glob("ReconOuput\\PRO_VID_20220618_065258_00_014\\*.png")
chunk.addPhotos(PhotoList)
chunk.matchPhotos(downscale=1, generic_preselection=True, reference_preselection=False)
chunk.alignCameras()
SavePath = os.path.join("ReconOuput\\PRO_VID_20220618_065258_00_014", "AgiSoftOut")
os.makedirs(SavePath, exist_ok = True)
ProjectPach = os.path.join(SavePath, "project.psz")
doc.save(path = ProjectPach, chunks = [doc.chunk])


doc.open(ProjectPach)
chunk.buildDepthMaps(downscale=4, filter_mode=Metashape.AggressiveFiltering)
chunk.buildDenseCloud()
chunk.buildModel(surface_type=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation)
chunk.buildUV(mapping_mode=Metashape.GenericMapping)
chunk.buildTexture(blending_mode=Metashape.MosaicBlending, texture_size=4096)
"""