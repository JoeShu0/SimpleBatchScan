import os
import glob
import Metashape

FolderList = glob.glob("ReconOuput\\*")
#i = 0
for folder in FolderList:
    #
    print("[LOG] Begin Process: " + folder)

    SavePath = os.path.join(folder, "AgiSoftOut")
    ProjectPach = os.path.join(SavePath, "Auto_Project.psz")

    RCSavePath = os.path.join(folder, "RCOutput")
    RCProjectPach = os.path.join(RCSavePath, "project.rcproj")

    if os.path.exists(ProjectPach):
        print("[LOG] " + folder + "ProjectFile Exist:" + ProjectPach)
        continue

    if os.path.exists(RCProjectPach):
        print("[LOG] " + folder + "RC ProjectFile Exist:" + RCProjectPach)
        continue

    print("[LOG] " + folder + "Begin Photo Align")
    doc = Metashape.app.document
    chunk = doc.addChunk()
    PhotoListPNG = glob.glob(os.path.join(folder, "*.png"))
    PhotoListJPG = glob.glob(os.path.join(folder, "*.JPG"))
    if(not PhotoListPNG) and (not PhotoListJPG):
        print("[ERROR] No JPG or png in Folder: " + folder)
        continue
    if(PhotoListPNG):
        chunk.addPhotos(PhotoListPNG)
    if(PhotoListJPG):
        chunk.addPhotos(PhotoListJPG)
    chunk.matchPhotos(downscale=0, generic_preselection=True, reference_preselection=True, reference_preselection_mode = Metashape.ReferencePreselectionMode.ReferencePreselectionSource)
    chunk.alignCameras(min_image=2, adaptive_fitting=True)
    os.makedirs(SavePath, exist_ok = True)
    doc.save(path = ProjectPach, chunks = [doc.chunk])
    doc.clear()
    print("[LOG] " + folder + "Photo Align Finished")
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