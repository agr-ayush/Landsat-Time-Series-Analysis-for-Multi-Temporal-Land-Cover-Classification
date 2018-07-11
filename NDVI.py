
# coding: utf-8

# In[ ]:


from osgeo import gdal, gdal_array

    file1 = gdal.Open(str(path of green band))
    file2 = gdal.Open(str(path of NIR band))


    file1 = file1.ReadAsArray()
    file2 = file2.ReadAsArray()

    a, b = file1.shape
    a,b


# In[56]:


import numpy as np

final_arr = np.zeros((a, b))
# print(final_arr)
# print(final_arr)
for i in range(a):
    for j in range(b):
        final_arr[i][j] = (file2[i][j] - file1[i][j])*100/(file1[i][j] + file2[i][j])#-100 to +100




# In[58]:


inRaster = str(path of green band)
inDS=gdal.Open(inRaster,1)
geoTransform = inDS.GetGeoTransform()
band=inDS.GetRasterBand(1)
datatype=band.DataType
proj = inDS.GetProjection()


# In[59]:


outRaster = str('path to store the NDVI file')
driver=inDS.GetDriver()
outDS = driver.Create(outRaster, b,a, 1,datatype)
geoTransform = inDS.GetGeoTransform()


# In[60]:


outDS.SetGeoTransform(geoTransform)
proj = inDS.GetProjection()
outDS.SetProjection(proj)
outBand = outDS.GetRasterBand(1)
outBand.WriteArray(final_arr,0,0)
outDS=None

