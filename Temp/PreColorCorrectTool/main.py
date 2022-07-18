import os, array
import shutil, glob
import multiprocessing
import sys, time
import tkinter as tk
import tkinter.filedialog
import threading

#CC
import colour
from PIL import Image
from colour_checker_detection import detect_colour_checkers_segmentation
import imageio, rawpy
import PythonMagick
from collections import OrderedDict
from OpenImageIO import ImageOutput, ImageInput
D65 = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['D65']
REFERENCE_COLOUR_CHECKER = colour.CCS_COLOURCHECKERS['ColorChecker24 - After November 2014']
REFERENCE_SWATCHES = colour.XYZ_to_RGB(
    colour.xyY_to_XYZ(list(REFERENCE_COLOUR_CHECKER.data.values())),
    REFERENCE_COLOUR_CHECKER.illuminant, D65,
    colour.RGB_COLOURSPACES['sRGB'].matrix_XYZ_to_RGB)
exiftoolPath = "exiftool.exe -m -overwrite_original_in_place -tagsFromFile"

#Global variables
ColorChecker = ""
PhotosDir = ""
OutPutDir = ""

#ProcessNum = 4
status = ""
bBusy = False
PhotoNum = 0

def getColorCorrectionSwatches(colorChecker,cacheFolder):
    # we use no brighten by default
    bNoAutoBrighten = True

    if not os.path.exists(colorChecker):
        return False, False, []

    #利用rawpy将raw文件转换成tiff文件格式方便校色
    colorCheckerTiff = convert2sRGBTiff(colorChecker, cacheFolder)
    #First blur the image to get rid of noise in colorchecker
    #对有色卡的照片进行模糊操作， 这样能去点部分噪点达到更好的检测
    print("blurring " + colorCheckerTiff)
    blurtiff = os.path.join(cacheFolder, os.path.splitext(os.path.basename(colorChecker))[0]+ "_blur" + '.tiff')
    img = PythonMagick.Image(colorCheckerTiff)
    img.blur(0,10)
    img.write(blurtiff)
    
    #Retrieve the color correction swatch values from the given image
    print(f"Detecting color checker in {blurtiff}")
    #将图片中的非线性R'G'B'值转换成线性的RGB值
    image = colour.cctf_decoding(colour.io.read_image(blurtiff))
    #检测图片中的色卡值
    swatches = detect_colour_checkers_segmentation(image)
    if len(swatches) < 1:
        return False, False, []
    #对每个检测到的色卡值进行校色，并返回结果最准确的那个。
    Vresult, swatch = VerifyColorSwatches(swatches)

    return Vresult, bNoAutoBrighten, swatch

 

def VerifyColorSwatches(swatches):
    deviation = []
    #标准色卡颜色值
    rgb_RCCL = colour.XYZ_to_RGB(colour.xyY_to_XYZ(list(REFERENCE_COLOUR_CHECKER.data.values())),
        D65, D65, colour.RGB_COLOURSPACES['sRGB'].matrix_XYZ_to_RGB)
    for swatch in swatches:
        swatch_cc = colour.colour_correction(swatch, swatch, REFERENCE_SWATCHES)
        CCL = swatch_cc
        totalsum = 0.0
        for i in range(len(rgb_RCCL)):
            #插值和
            totalsum += abs(rgb_RCCL[i][0]-CCL[i][0]) + abs(rgb_RCCL[i][1]-CCL[i][1]) + abs(rgb_RCCL[i][2]-CCL[i][2])
        deviation.append(totalsum)
    print("swatches deviations: "+str(deviation))
    min_d = 100.0
    min_i = -1
    for i in range(len(deviation)):
        if deviation[i] < min_d:
            min_d = deviation[i]
            min_i = i
    print("The lowest devi is: " + str(min_d))
    result = False
    #通常插值和在8.0一下都可以接受
    if min_d < 3.0:
        print("devi is good ! ")
        result = True
    elif min_d < 5.0:
        print("devi is near average ! ")
        result = True
    elif min_d < 8.0:
        print("devi is near BAD ! the COLORS will be off!!!!")
        result = True
    else:
        print("devi is BAD ! the Swatches are completely off!!!!")
        result = False
    return result, swatches[min_i]


def CCProcess(files, Vresult, swatch, colorCorrectFolder, CacheDir):
    #folder = folderpath.split("\\")[-1]
    #LocalCcCache = os.path.join(LocalCachPath, folder, "Cache")
    for file in files:
        #利用rawpy将raw文件转换成tiff文件格式方便校色
        tifffile = convert2sRGBTiff(file, CacheDir)
        print("ColorCorrecting: "+tifffile)
        #将图片中的非线性R'G'B'值转换成线性的RGB值
        image = colour.cctf_decoding(colour.io.read_image(os.path.join(CacheDir, tifffile)))
        #使用拍摄颜色值（swatch）进行校色
        cc_image = colour.colour_correction(image, swatch, REFERENCE_SWATCHES, 'Finlayson 2015')
        #这里将校色完成的图片存为32位图像
        tiff_CC_32 = os.path.join(CacheDir, os.path.splitext(os.path.basename(file))[0] + "_CC" +'.tiff')
        #将图片中的线性的RGB值值转换成非线性R'G'B'
        colour.io.write_image(colour.cctf_encoding(cc_image), tiff_CC_32)# write out 32bit image
        print("Save CC image to jpg: "+file)
        cctifffile = os.path.join(CacheDir, os.path.splitext(os.path.basename(file))[0] + '.tiff')
        #ccpngfile = os.path.join(folderpath,'ColorCorrected', os.path.splitext(os.path.basename(file))[0] + '.tiff')
        #转换为8位图片以节约空间
        img = PythonMagick.Image(tiff_CC_32)
        img.depth(8)
        img.write(cctifffile)

        #项目要求转换为JPG并缩放尺寸
        Final_ccJpgfile = os.path.join(colorCorrectFolder, os.path.splitext(os.path.basename(file))[0] + '.jpg')
        img = Image.open(cctifffile)
        """disable resize
        if max(img.size[0], img.size[1]) > DestFrameSize:
            ResizePercent = DestFrameSize/float(max(img.size[0], img.size[1]))
            img = img.resize((int(img.size[0]*ResizePercent), int(img.size[1]*ResizePercent)), 5)
        """
        img.save(Final_ccJpgfile, quality=100, subsampling=0)

        TransferMetaData(file, Final_ccJpgfile)

 

 

def convert2sRGBTiff(file, outfolder, bNo_Auto_Bright = True):
    """
    Convert ALL to tiff in sRGB space
    """
    tiffFile = ""
    extention = file.rsplit(".",1)[-1]
    tiffFile = os.path.join(outfolder, os.path.splitext(os.path.basename(file))[0] + '.tiff')
    #对于非raw格式，只做一个简单的转换
    if (extention == "jpg" or extention == "JPG" or
        extention == "png" or extention == "PNG" or
        extention == "tga" or extention == "TGA"):
        im = imageio.imread(file)
        imageio.imsave(tiffFile, im)
        return tiffFile
    #对raw格式，设置为不裁剪高光，不自动加亮，使用默认白平衡（校色会自带白平衡）， 使用sRGB gamma
    else:
        try:
            raw = rawpy.imread(file)
            rgb = raw.postprocess(highlight_mode=0, no_auto_bright=bNo_Auto_Bright, use_camera_wb=True, gamma=(2.4, 12.92))
            tiffFile = os.path.join(outfolder, os.path.splitext(os.path.basename(file))[0] + '.tiff')
            imageio.imsave(tiffFile, rgb)
            return tiffFile
        except:
            print("Unsupported Format!!")
            return False

def TransferMetaData(SourceFile, DistFile):
    command = exiftoolPath
    command += " "+ SourceFile
    command += " "+ DistFile
    os.system(command)


def CleanUP(CacheDir):
    if os.path.exists(CacheDir):
        shutil.rmtree(CacheDir) 

def MainCCProcess(ColorChecker, folderpath, OutPutDir, Threads):
    DisableButtons()
    Format = ColorChecker.rsplit(".",1)[-1]
    FileList = glob.glob(os.path.join(folderpath, '*.'+Format))

    if len(FileList) < 2:
        print("No file to CC!")
        return False

    #CCDir = os.path.join(folderpath, "ColorCorrected")
    #os.makedirs(CCDir, exist_ok=True)
    CCDir = OutPutDir
    CleanUP(CCDir)
    os.makedirs(CCDir, exist_ok=True)
    CacheDir = os.path.join(CCDir,"Cache")
    os.makedirs(CacheDir, exist_ok=True)
    global PhotoNum
    PhotoNum = len(FileList)
    print("Prepare ColorChecker")
    Vresult, bNoAutoBrighten, swatch = getColorCorrectionSwatches(ColorChecker, CacheDir)

    if Vresult:
        print("ColorCheckerDetected")
    else:
        print("ColorCheckerDetectionFailed, Abort")
        CleanUp(CCDir)
        return False

    print("***Start Mass ColorCorrcting***")
    Process = []
    FramePerProcess = int(len(FileList)/int(Threads))

    for i in range(Threads+1):
        LastFrame = min((i+1)*FramePerProcess, len(FileList))
        files = FileList[i*FramePerProcess:LastFrame]
        x = multiprocessing.Process(target=CCProcess, args=(files, Vresult, swatch, CCDir, CacheDir,))
        Process.append(x)
        x.start()
        time.sleep(5)

    for ps in Process:
        ps.join()

    EnableButtons()

 
def ColorCorrect():
    if ColorChecker == "" or PhotosDir == "" or OutPutDir == "":
        print("Invalid Settings!")
        return False
    BakeT = threading.Thread(target=MainCCProcess, args=(ColorChecker,PhotosDir,OutPutDir,int(ProcessNumBlock.get()),))
    BakeT.start()

    #MainCCProcess("F:\PhotoGrammetry\ColorCorrector\\123\ColorChecker.dng","F:\PhotoGrammetry\ColorCorrector\\123",4)

 

 

#UI stuff
def Choose_ColourChecker():
    global ColorChecker
    filename = tk.filedialog.askopenfilename()
    ColorCheckerBlock["text"] = filename
    ColorChecker = filename
    print(filename)

def Choose_PhotoDir():
    global PhotosDir
    filedir = tk.filedialog.askdirectory()
    PhotosDirBlock["text"] = filedir
    PhotosDir = filedir
    print(filedir)

def Choose_OutPutDir():
    global OutPutDir
    filedir = tk.filedialog.askdirectory()
    OutPutDirBlock["text"] = filedir
    OutPutDir = filedir
    print(filedir)
 

def DisableButtons():
    ChooseColorChecker["state"] = tk.DISABLED
    ChoosePhotosDir["state"] = tk.DISABLED
    ChooseOutputDir["state"] = tk.DISABLED
    StartButton["state"] = tk.DISABLED
    global bBusy
    bBusy = True

def EnableButtons():
    ChooseColorChecker["state"] = tk.NORMAL
    ChoosePhotosDir["state"] = tk.NORMAL
    ChooseOutputDir["state"] = tk.NORMAL
    StartButton["state"] = tk.NORMAL
    global bBusy, status
    bBusy = False
    status = "WaitingForCommand"

def GetProgress():
    global PhotoNum
    if PhotoNum == 0:
        return 0
    else:
        FileNum = len(glob.glob(os.path.join(OutPutDir, '*.jpg')))
        progress = int(float(FileNum)/float(PhotoNum)*100.0)
        return progress

if __name__ == "__main__":
   
    multiprocessing.freeze_support()
    Window = tk.Tk()
    Window.title("ColourCorrector")
    Window.geometry("800x150")
    #DecimateBakeButton = tk.Button(Window, text = "CC", width = 20, height = 1, command=ColorCorrect)
    #DecimateBakeButton.grid(row=0,column=0,sticky="W")
    """
    bDiffuse = tk.BooleanVar()
    bNormal = tk.BooleanVar()
    bAO = tk.BooleanVar()
    bVColortoTex = tk.BooleanVar()
    TriCount = tk.IntVar()
    """
    #UI Elements
    #l.grid(row=3)
   
    ColorCheckerL = tk.Label(Window, text = "ColourChecker(色卡路径)： ", width = 25, height = 1  )
    ColorCheckerL.grid(row=0, column=0)
    ColorCheckerBlock = tk.Label(Window, text = "None(未指定色卡)", width = 50, height = 1)
    ColorCheckerBlock.grid(row=0, column=1)
    ChooseColorChecker = tk.Button(Window, text = "...", width = 4, height = 1, command=Choose_ColourChecker)
    ChooseColorChecker.grid(row=0,column=2,sticky="E")

    PhotosDirL = tk.Label(Window, text = "Photos(待较色路径)： ", width = 25, height = 1  )
    PhotosDirL.grid(row=1, column=0)
    PhotosDirBlock = tk.Label(Window, text = "None(未指定路径)", width = 50, height = 1 )
    PhotosDirBlock.grid(row=1, column=1)
    ChoosePhotosDir = tk.Button(Window, text = "...", width = 4, height = 1,  command=Choose_PhotoDir)#
    ChoosePhotosDir.grid(row=1,column=2,sticky="E")
   
    OutPutDirL = tk.Label(Window, text = "OutPut(输出路径)： ", width = 25, height = 1)
    OutPutDirL.grid(row=2, column=0)
    OutPutDirBlock = tk.Label(Window, text = "None(未指定输出)", width = 50, height = 1)
    OutPutDirBlock.grid(row=2, column=1)
    ChooseOutputDir = tk.Button(Window, text = "...", width = 4, height = 1, command=Choose_OutPutDir)
    ChooseOutputDir.grid(row=2,column=2,sticky="E")

    ProcessNumL = tk.Label(Window, text = "ProcessNum(进程数)", width = 30, height = 1)
    ProcessNumL.grid(row=3,column=0,sticky="E")
    ProcessNumBlock = tk.Entry(Window, width = 15)
    ProcessNumBlock.insert(0, "3")
    ProcessNumBlock.grid(row=3,column=1,sticky="W")

    StartButton = tk.Button(Window, text = "Start ColorCorrection(开始较色)", width = 30, height = 1, command=ColorCorrect)
    StartButton.grid(row=3,column=2,sticky="W")
   
    l = tk.Label(Window, text = "ABC", width = 80, height = 1, font=("Arial"))
    l.place(x=5,y=125)

    def UpdateStatus():
        global status, bBusy
        percent = GetProgress()
        status = str(percent)+"%"
        """
        if bBusy:
            if status[-3:] == "...":
                status = status[:-3]
            else:
                status += "."
        """
        l["text"] = status
        l.after(500, UpdateStatus)
    l.after(500, UpdateStatus)

    Window.mainloop()