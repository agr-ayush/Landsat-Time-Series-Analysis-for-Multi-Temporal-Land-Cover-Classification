
# coding: utf-8

# In[1]:


import gdal
import numpy as np


outvrt = '/vsimem/stacked.vrt' #/vsimem is special in-memory virtual "directory"
outtif = r'E:\Internships\ISRO\Dataset3\Training\\train_input_b.tif'
tifs = [
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band1.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band2.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band3.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band4.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band5.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band6.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band7.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band8.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band9.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band10.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band11.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band12.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band13.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band14.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band15.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band16.tif',
        r'E:\Internships\ISRO\Dataset3\Training\train_input_band17.tif'
       ] 

outds = gdal.BuildVRT(outvrt, tifs, separate=True)
outds = gdal.Translate(outtif, outds)

outds=None


# In[3]:


a = gdal.Open(r'E:\Internships\ISRO\Dataset1\Testing\\test_input_b.tif')

b = a.ReadAsArray()

print(b.shape)

