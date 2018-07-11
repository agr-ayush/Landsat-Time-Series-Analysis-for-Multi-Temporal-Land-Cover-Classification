#GUI to ease the process
# The input to be provided is the directory location where all the zips from landsat are present.
# coding: utf-8

# In[81]:


from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from osgeo import gdal, gdal_array
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from random import randint
from progressbar import Bar, ETA, FileTransferSpeed, Percentage, RotatingMarker, ProgressBar
import webbrowser
import os
import gzip
import tarfile
import time
import gdal
import numpy as np
import threading
import pickle
import datetime
import dateutil.parser


# In[82]:


list1 = ['RBV','TM','MSS','ETM+','OLI','TIRS']
directoryname = ''
train_directoryname = ''
train_output_filename = ''
filename = ''


# In[83]:


def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))


# In[84]:


def createmodel(train_input,train_output):
   # print("Creating Model.............................................")
    ds_input = gdal.Open(train_input)
    ds_output = gdal.Open(train_output)
    input_imgarr = ds_input.ReadAsArray()
    output_imgarr = ds_output.ReadAsArray()
    n_samples = (output_imgarr>0).sum()
    p = input_imgarr
    q = np.array(p[0][0])
    X = input_imgarr[:,output_imgarr>0]
    Y = output_imgarr[output_imgarr>0]
    X = X.T
    p = Y.T
    q = np.array(p)
    rf = RandomForestClassifier(n_estimators=5000,oob_score=True,n_jobs=-1)
    rf = rf.fit(X,Y)
    joblib.dump(rf, str(directoryname + '\LandCoverModel.pkl'))
    predict_files = [(x[2]) for x in os.walk(str(directoryname))]
    for i in predict_files[0]:
        if ((not (i.endswith("tar.gz"))) and i!= trainfile):
            loadmodel(str(directoryname + "\\" + i))
            


# In[85]:


def geoextent(train_path):
    print("Geo Extent.......................................")
    IMG1 = gdal.Open(str(train_path + "\\stacked_image.tif" ))
    IMG2 = gdal.Open(str(train_output_filename))
    gt1 = IMG1.GetGeoTransform()
    gt2 = IMG2.GetGeoTransform()
    #print(gt1)
    #print(gt2)
    r1 = [gt1[0], gt1[3],gt1[0] + (gt1[1] * IMG1.RasterXSize), gt1[3] + (gt1[5] * IMG1.RasterYSize)]
    r2 = [gt2[0], gt2[3],gt2[0] + (gt2[1] * IMG2.RasterXSize), gt2[3] + (gt2[5] * IMG2.RasterYSize)]
    intersection = [max(r1[0], r2[0]), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]
    #print(intersection)
    ds = gdal.Open(str(train_path + "\\stacked_image.tif" ))
    #print(ds)
    ds = gdal.Translate(str(train_path + "\\stacked_image1.tif" ),ds,projWin = intersection)
    #print(ds)
    ds = None
    randomsampling(train_path)


# In[86]:


def loadmodel(test_file):
    print("Loading Model........................................................")
    if v.get()==0:
        rf = joblib.load('DefaultModel.pkl') 
    else:
        rf = joblib.load(str(directoryname + '\LandCoverModel.pkl'))
    print("Predicting...........................................................")
    if v.get()==0:
        predict_arr = gdal.Open(str(test_file + "\\stacked_image.tif"))
    else:
        predict_arr = gdal.Open(str(test_file + "\\stacked_image1.tif"))
    img_predict = predict_arr.ReadAsArray()
    img_predict = img_predict.T
    B = []
    count=0
    for i in range(len(img_predict[1])):
        class_predict = rf.predict(img_predict[:,i,:])
        B.append(class_predict)
    B = np.array(B)
    a,b = B.shape
    if v.get()==0:
        inRaster=str(test_file+"\\stacked_image.tif")
    else:
        inRaster=str(test_file+"\\stacked_image1.tif")
    inDS=gdal.Open(inRaster,1)
    geoTransform = inDS.GetGeoTransform()
    band=inDS.GetRasterBand(1)
    datatype=band.DataType
    proj = inDS.GetProjection()
    outRaster = test_file + "\\test_out.tif"
    driver=inDS.GetDriver()
    outDS = driver.Create(outRaster , b , a , 1 , datatype)
    geoTransform = inDS.GetGeoTransform()
    outDS.SetGeoTransform(geoTransform)
    proj = inDS.GetProjection()
    outDS.SetProjection(proj)
    outBand = outDS.GetRasterBand(1)
    outBand.WriteArray(B,0,0)
    outDS=None
    if v.get()==0:
        print("Water Replacing...........................")
        waterreaplace(test_file)
    print("Finished")


# In[87]:


def down():
    url = 'https://earthexplorer.usgs.gov/'
    webbrowser.open_new(url)      


# In[88]:


def randomsampling(directorypath):
   # print("Random Sampling..................................................")
    inimage = gdal.Open(str(directorypath + "\\stacked_image1.tif"))
    outimage = gdal.Open(train_output_filename)
    in_imgarr = inimage.ReadAsArray()
    out_imgarr = outimage.ReadAsArray()
    x,y,z = in_imgarr.shape
    #print(x,y,z)
    a,b = out_imgarr.shape
    ##print(a,b)
    #print(ndvi_count)
    waterarr = [[0 for x in range(b)] for y in range(a)]
    soilarr = [[0 for x in range(b)] for y in range(a)]
    urbanarr = [[0 for x in range(b)] for y in range(a)]
    vegarr = [[0 for x in range(b)] for y in range(a)]
    new_array = [[[0 for a in range(z)] for b in range(y)] for c in range(x)]
    finalarr = [[0 for x in range(b)] for y in range(a)]
    new_array = np.array(new_array)
    new_array = in_imgarr
    p,q,r = new_array.shape
    count1=0
    count2=0
    count3=0
    count4=0
    for i in range(a):
        for j in range(b):       
            if(out_imgarr[i][j]==4):
                waterarr[i][j] = 4
                count1+=1
            elif(out_imgarr[i][j]==3):
                soilarr[i][j] = 3
                count2+=1
            elif(out_imgarr[i][j]==2):
                urbanarr[i][j] = 2
                count3+=1
            elif(out_imgarr[i][j]==1):
                vegarr[i][j] = 1
                count4+=1
    countmax = 500
    count1=0
    count2=0
    count3=0
    count4=0
    counttotal = 0
    countori = 0
    for i in range(a):
        for j in range(b):
            counttotal+=1
            s = randint(0, a-1)
            d = randint(0, b-1)
            if(waterarr[s][d]!=0 and count1<=0.5*countmax):
                finalarr[s][d] = 4
                count1+=1
                waterarr[s][d]=0
            elif(urbanarr[s][d]!=0 and count2<=countmax):
                finalarr[s][d] = 2
                count2+=1
                urbanarr[s][d]=0
            elif(vegarr[s][d]!=0 and count3<=countmax):
                finalarr[s][d] = 1
                count3+=1
                vegarr[s][d]=0
            elif(soilarr[s][d]!=0 and count4<=countmax):
                finalarr[s][d] = 3
                count4+=1
                soilarr[s][d]=0
            else:
                finalarr[s][d] = 0
                countori+=1
                for k in range(p):
                    new_array[k][s][d] = 0
    inDS=gdal.Open(train_output_filename, 1)
    geoTransform = inDS.GetGeoTransform()
    band=inDS.GetRasterBand(1)
    datatype=band.DataType
    proj = inDS.GetProjection()
    #####For input#######
    outRaster= directorypath + "\\train_input.tif" 
    driver=inDS.GetDriver()
    outDS = driver.Create(outRaster , z , y , x , datatype)
    geoTransform = inDS.GetGeoTransform()
    outDS.SetGeoTransform(geoTransform)
    proj = inDS.GetProjection()
    outDS.SetProjection(proj)
    for i in range(1,x):
        outBand = outDS.GetRasterBand(i)
        outBand.WriteArray(np.array(new_array[i-1,:,:]),0,0)
    outDS=None
    ####For Output#########
    outRaster1= directorypath + "\\train_output.tif" 
    driver=inDS.GetDriver()
    outDS = driver.Create(outRaster1 , b , a , 1 , datatype)
    geoTransform = inDS.GetGeoTransform()
    outDS.SetGeoTransform(geoTransform)
    proj = inDS.GetProjection()
    outDS.SetProjection(proj)
    outBand = outDS.GetRasterBand(1)
    outBand.WriteArray(np.array(finalarr),0,0)
    outDS=None
    createmodel(outRaster,outRaster1)


# In[89]:


def waterreplace(path):
    f1 = gdal.Open(str(path + "\\test_out.tif"))
    f2 = gdal.Open( path +'\\MNDWI.tif')
    arr1 = f1.ReadAsArray()
    arr2 = f2.ReadAsArray()
    a,b = arr2.shape
    arr3 = arr1[16,:,:]
    for i in range(a):
        for j in range(b):
            if(arr3[i][j]>0):
                arr2[i][j] = 4
    inRaster = str(path + "\\test_out.tif")
    inDS=gdal.Open(inRaster,1)
    geoTransform = inDS.GetGeoTransform()
    band=inDS.GetRasterBand(1)
    datatype=band.DataType
    proj = inDS.GetProjection()
    outRaster= str(path + "\\test_output.tif")
    driver=inDS.GetDriver()
    outDS = driver.Create(outRaster , b , a , 1 , datatype)
    geoTransform = inDS.GetGeoTransform()
    outDS.SetGeoTransform(geoTransform)
    proj = inDS.GetProjection()
    outDS.SetProjection(proj)
    outBand = outDS.GetRasterBand(1)
    outBand.WriteArray(arr2,0,0)
    outDS=None


# In[90]:


def openbrowser():
    global filename
    filename =  filedialog.askopenfilename(initialdir = "/",
                                              title = "Select file",
                                              filetypes = (("shape file","*.shp"),("shape file","*.shx"),("shape file","*.dbf")))
    #print(filename)
    
def openfile():
    global train_output_filename
    train_output_filename = filedialog.askopenfilename(initialdir = "/",
                                              title = "Select file",
                                              filetypes = (("tif file","*.tif"),("tiff file","*.tiff")))
    
def opendir():
    global directoryname
    directoryname = filedialog.askdirectory()
    #print(directoryname)


# In[91]:


def showchoice():
    if v.get()==1:
        sensor = Label(root,text="Select LANDSAT Sensor:")
        sensor.pack(anchor='w',padx= 10,pady= 5)
        Application(root)
        bands = Label(root,text="Select Bands:")
        bands.pack(anchor=W,padx= 10,pady= 5)
        checkBox1.pack(anchor=W,padx= 10,pady= 5)
        checkBox2.pack(anchor=W,padx= 10,pady= 5)
        checkBox3.pack(anchor=W,padx= 10,pady= 5)
        checkBox4.pack(anchor=W,padx= 10,pady= 5)
        checkBox5.pack(anchor=W,padx= 10,pady= 5)
        checkBox6.pack(anchor=W,padx= 10,pady= 5)
        checkBox7.pack(anchor=W,padx= 10,pady= 5)
        checkBox8.pack(anchor=W,padx= 10,pady= 5)
        checkBox9.pack(anchor=W,padx= 10,pady= 5)
        checkBox10.pack(anchor=W,padx= 10,pady= 5)
        checkBox11.pack(anchor=W,padx= 10,pady= 5)
        checkBox12.pack(anchor=W,padx= 10,pady= 5)
        area = Label(root,text="Select Area(Select Shape File):")
        area.pack(anchor=W,padx= 10,pady= 5)
        Button2 = Button(root,text="Browse",command=openbrowser).pack(anchor=W,padx= 10,pady= 5)
        folder = Label(root,text="Choose Folder(Select Zip File):")
        folder.pack(anchor=W,padx= 10,pady= 5)
        Button1 = Button(root,text="Browse",command=opendir).pack(anchor=W,padx= 10,pady= 5)
        l1 = Label(root,text="Train Input Date(yyyymmdd):").pack(anchor=W,padx= 10,pady= 5)
        b2.pack(anchor=W,padx= 10,pady= 5)
        l = Label(root,text="Select train output(tif file):").pack(anchor=W,padx= 10,pady= 5)
        b1 = Button(root,text ="Browse",command=openfile).pack(anchor=W,padx= 10,pady= 5)
        Button3 = Button(root,text="Run", command = preprocess).pack(anchor=E,padx= 10,pady= 5)
        Button4 = Button(root,text="Download Files",command = down).pack(anchor=E,padx= 10,pady= 5)
    else:
        folder = Label(root,text="Choose Folder(Select Zip File):")
        folder.pack(anchor=W,padx= 10,pady= 5)
        Button1 = Button(root,text="Browse",command=opendir).pack(anchor=W,padx= 10,pady= 5)
        Button3 = Button(root,text="Run", command = preprocess).pack(anchor=E,padx= 10,pady= 5)


# In[92]:


root = Tk()
root.title("ISRO_GUI")
band1 = StringVar()
band2 = StringVar()
band3 = StringVar()
band4 = StringVar()
band5 = StringVar()
band6 = StringVar()
band7 = StringVar()
pan = StringVar()
cirrus = StringVar()
band10 = StringVar()
band11 = StringVar()
pixelqa = StringVar()
checkBox1 = Checkbutton(root, variable=band1,state='disable', onvalue='BAND1', offvalue='', text="BAND1")
checkBox2 = Checkbutton(root, variable=band2,state='disable', onvalue='BAND2', offvalue='', text="BAND2")
checkBox3 = Checkbutton(root, variable=band3, state='disable',onvalue='BAND3', offvalue='', text="BAND3")
checkBox4 = Checkbutton(root, variable=band4,state='disable', onvalue='BAND4', offvalue='', text="BAND4")
checkBox5 = Checkbutton(root, variable=band5, state='disable',onvalue='BAND5', offvalue='', text="BAND5")
checkBox6 = Checkbutton(root, variable=band6, state='disable',onvalue='BAND6', offvalue='', text="BAND6")
checkBox7 = Checkbutton(root, variable=band7, state='disable',onvalue='BAND7', offvalue='', text="BAND7")
checkBox8 = Checkbutton(root, variable=pan, state='disable',onvalue='PAN', offvalue='', text="PAN")
checkBox9 = Checkbutton(root, variable=cirrus,state='disable', onvalue='CIRRUS', offvalue='', text="CIRRUS")
checkBox10 = Checkbutton(root, variable=band10, state='disable',onvalue='BAND10', offvalue='', text="BAND10")
checkBox11 = Checkbutton(root, variable=band11, state='disable',onvalue='BAND11', offvalue='', text="BAND11")
checkBox12 = Checkbutton(root, variable=pixelqa, state='disable',onvalue='PIXEL_QA', offvalue='', text="PIXEL_QA")
b2 = Entry(root)

v = IntVar()
r1 = Radiobutton(root,text="Default Settings",variable=v,value=0,command = showchoice)
r2 = Radiobutton(root,text="Custom Settings",variable=v,value=1,command = showchoice)

class Application:
    def __init__(self, parent):
        self.parent = parent
        self.combo()

    def combo(self):
        self.box_value = StringVar()
        self.box = Combobox(self.parent, textvariable=self.box_value, state='readonly', width=75)
        self.box.bind("<<ComboboxSelected>>", self.checklist)
        self.box['values'] = list1
        self.box.current(0)
        self.box.pack(anchor=E,padx= 10,pady= 10)
        
    def checklist(self,item):
        checkBox1.config(state='disable', offvalue=0)
        checkBox2.config(state='disable', offvalue=0)
        checkBox3.config(state='disable', offvalue=0)
        checkBox4.config(state='disable', offvalue=0)
        checkBox5.config(state='disable', offvalue=0)
        checkBox6.config(state='disable', offvalue=0)
        checkBox7.config(state='disable', offvalue=0)
        checkBox8.config(state='disable', offvalue=0)
        checkBox9.config(state='disable', offvalue=0)
        checkBox10.config(state='disable', offvalue=0)
        checkBox11.config(state='disable', offvalue=0)
        checkBox12.config(state='disable', offvalue=0)
        if self.box.get() == "RBV":
            checkBox4.config(state='enable')
            checkBox5.config(state='enable')
            checkBox6.config(state='enable')
            checkBox12.config(state='enable')
        elif self.box.get() == 'TM':
            checkBox1.config(state='enable')
            checkBox2.config(state='enable')
            checkBox3.config(state='enable')
            checkBox4.config(state='enable')
            checkBox5.config(state='enable')
            checkBox6.config(state='enable')
            checkBox7.config(state='enable')
            checkBox12.config(state='enable')
        elif self.box.get() == 'ETM+':
            checkBox1.config(state='enable')
            checkBox2.config(state='enable')
            checkBox3.config(state='enable')
            checkBox4.config(state='enable')
            checkBox5.config(state='enable')
            checkBox6.config(state='enable')
            checkBox7.config(state='enable')
            checkBox8.config(state='enable')
            checkBox12.config(state='enable')
        elif self.box.get() == 'MSS':
            checkBox1.config(state='enable')
            checkBox2.config(state='enable')
            checkBox3.config(state='enable')
            checkBox4.config(state='enable')
            checkBox12.config(state='enable')
        elif self.box.get() == 'OLI':
            checkBox1.config(state='enable')
            checkBox2.config(state='enable')
            checkBox3.config(state='enable')
            checkBox4.config(state='enable')
            checkBox5.config(state='enable')
            checkBox6.config(state='enable')
            checkBox7.config(state='enable')
            checkBox8.config(state='enable')
            checkBox9.config(state='enable')
            checkBox12.config(state='enable')
        elif self.box.get() == 'TIRS':
            checkBox10.config(state='enable')
            checkBox11.config(state='enable')
            checkBox12.config(state='enable')


# In[93]:


def BandStacking(path, selectedband, ndvi_path):
    outvrt = '/vsimem/stacked.vrt' #/vsimem is special in-memory virtual "directory"
    outtif = str(path + "\\stacked_image.tif")
    tifs = []
    for i in selectedband:
        tifs.append(str(path + "\\" + i))
    tifs.append(str(path + "\\MNDWI.tif"))
    ndvifiles = [x[2] for x in os.walk(ndvi_path)]
    for i in ndvifiles[0]:
        tifs.append(str(ndvi_path + "\\" + i))
    outds = gdal.BuildVRT(outvrt, tifs, separate=True)
    outds = gdal.Translate(outtif, outds)
    outds=None
    print("Band Stacking Done!")


# In[94]:


def NDVI(ndvi_input_band4, ndvi_input_band5, ndvi_path, c):  
    file1 = gdal.Open(str(ndvi_input_band4))
    file2 = gdal.Open(str(ndvi_input_band5))
    file1 = file1.ReadAsArray()
    file2 = file2.ReadAsArray()
    a, b = file1.shape
    final_arr = np.zeros((a, b))
    for i in range(a):
        for j in range(b):
            final_arr[i][j] = (file2[i][j] - file1[i][j])*100/(file1[i][j] + file2[i][j]) #-100 to +100
    inRaster = str(ndvi_input_band5)
    inDS=gdal.Open(inRaster,1)
    geoTransform = inDS.GetGeoTransform()
    band=inDS.GetRasterBand(1)
    datatype=band.DataType
    proj = inDS.GetProjection()
    outRaster = str(ndvi_path + "\\NDVI"+ str(c) + ".tif")
    driver=inDS.GetDriver()
    outDS = driver.Create(outRaster, b,a, 1,datatype)
    geoTransform = inDS.GetGeoTransform()
    outDS.SetGeoTransform(geoTransform)
    proj = inDS.GetProjection()
    outDS.SetProjection(proj)
    outBand = outDS.GetRasterBand(1)
    outBand.WriteArray(final_arr,0,0)
    outDS=None


# In[95]:


def MNDWI(mndwi_input_band3, mndwi_input_band6 ,path):
    file1 = gdal.Open(str(mndwi_input_band6))
    file2 = gdal.Open(str(mndwi_input_band3))
    file1 = file1.ReadAsArray()
    file2 = file2.ReadAsArray()
    a,b = file1.shape
    final_arr = np.zeros((a, b))
    for i in range(a):
        for j in range(b):
            final_arr[i][j] = (file2[i][j] - file1[i][j])*100/(file1[i][j] + file2[i][j]) #-100 to +100
        inRaster = str(mndwi_input_band6)
    inDS=gdal.Open(inRaster,1)
    geoTransform = inDS.GetGeoTransform()
    band=inDS.GetRasterBand(1)
    datatype=band.DataType
    proj = inDS.GetProjection()
    outRaster =  str(path + 'MNDWI.tif')
    driver=inDS.GetDriver()
    outDS = driver.Create(outRaster, b,a, 1,datatype)
    geoTransform = inDS.GetGeoTransform()
    outDS.SetGeoTransform(geoTransform)
    proj = inDS.GetProjection()
    outDS.SetProjection(proj)
    outBand = outDS.GetRasterBand(1)
    outBand.WriteArray(final_arr,0,0)
    outDS=None


# In[96]:


def preprocess():
    global selectedband 
    selectedband = []
    global directoryname
    ndvi_path = directoryname + "\\NDVI Files"
    os.mkdir(ndvi_path)
    datafile= [(x[2]) for x in os.walk(str(directoryname))]
    global trainfile
    trainfile = ""
    c = 1
    global ndvi_count 
    ndvi_count = 0
    for i in datafile[0]:
        #print(i)
        if (i.endswith("tar.gz")):
            ndvi_count += 1
            tar = tarfile.open(directoryname + "\\"+i)
            tar.extractall(path=directoryname + "\\" + i[:-7] + "\\")
            tar.close()
            tardir = directoryname + "\\" + i[:-7]
            print("Extracted in Current Directory")
            readfile = [x[2] for x in os.walk(str(directoryname + "\\" + i[:-7]+"\\"))]     
            if v.get()==1:
                for j in readfile[0]:
                    if band1.get().lower()!='' and band1.get().lower() in j:
                        selectedband.append(j)
                    if band2.get().lower()!='' and band2.get().lower() in j:
                        selectedband.append(j)
                    if band3.get().lower()!='' and band3.get().lower() in j:
                        selectedband.append(j)
                    if band4.get().lower()!='' and band4.get().lower() in j:
                            selectedband.append(j)
                    if band5.get().lower()!='' and band5.get().lower() in j:
                        selectedband.append(j)
                    if band6.get().lower()!='' and band6.get().lower() in j:
                        selectedband.append(j)
                    if band7.get().lower()!='' and band7.get().lower() in j:
                        selectedband.append(j)
                    if pan.get().lower()!='' and pan.get().lower() in j:
                        selectedband.append(j)
                    if cirrus.get().lower()!='' and cirrus.get().lower() in j:
                        selectedband.append(j)
                    if band10.get().lower()!='' and band10.get().lower() in j:
                        selectedband.append(j)
                    if band11.get().lower()!='' and band11.get().lower() in j:
                        selectedband.append(j)
                    if pixelqa.get().lower()!='' and pixelqa.get().lower() in j:
                        selectedband.append(j)
            else:
                for j in readfile[0]:
                    if((".tif" in j) and (("band2" in j) or ("band3" in j) or ("band4" in j) or ("band5" in j) or ("band6" in j)  or ("band7" in j))):
                        selectedband.append(j)
                #print(selectedband)
            ndvi_input_band4 = ""
            ndvi_input_band5 = ""
            mndwi_input_band3 = ""
            mndwi_input_band6 = ""
            for j in readfile[0]:
                if((".tif" in j) and ("band4" in j)):
                    ndvi_input_band4 = directoryname + "\\" + i[:-7] + "\\" + j
                if((".tif" in j) and ("band5" in j)):
                    ndvi_input_band5 = directoryname + "\\" + i[:-7] + "\\" + j
                if((".tif" in j) and ("band3" in j)):
                    mndwi_input_band3 = directoryname + "\\" + i[:-7] + "\\" + j
                if((".tif" in j) and ("band6" in j)):
                    mndwi_input_band6 = directoryname + "\\" + i[:-7] + "\\" + j
            print("NDVI.................................")
            NDVI(ndvi_input_band4, ndvi_input_band5, ndvi_path, c)
            print("MNDWI.................................")
            MNDWI(mndwi_input_band3, mndwi_input_band6, str(directoryname + "\\" + i[:-7] + "\\"))
            c += 1
    print("Band Stacking.............................................................")        
    for i in datafile[0]:
        print("Stacking")
        BandStacking(str(directoryname + "\\" + i[:-7] + "\\"),selectedband,ndvi_path)        
    if v.get()==1:
        date = b2.get()
        year = date[0:4]
        month = date[4:6]
        day = date[6:8]
        date = datetime.datetime(int(year),int(month),int(day))
        file_dates = []
        try:
            for i in datafile[0]:
                x = datetime.datetime(int(i[10:14]),int(i[14:16]),int(i[16:18]))
                file_dates.append(x)
        except:
            pass

        near =  nearest(file_dates,date)
        b = str(near)
        d = dateutil.parser.parse(b).date()
        d = str(d).replace("-","")
        for i in datafile[0]:
            if str(d) in i:
                trainfile = directoryname + "\\" + i[:-7]
                geoextent(trainfile)
    else:
        widgets = ["Completed: ", Percentage(), ' ', Bar(marker = RotatingMarker()),
          ' ', ETA(), ' ', FileTransferSpeed()]

        pbar = ProgressBar(widget  = widgets, maxval = 10000000).start()
        for i in pbar(datafile[0]):
             loadmodel(str(directoryname + "\\" + i[:-7] ))
                


# In[97]:


r1.pack(anchor=W,padx= 10,pady= 10)
r2.pack(anchor=W,padx= 10,pady= 10)
root.resizable(False, False)
root.mainloop()

