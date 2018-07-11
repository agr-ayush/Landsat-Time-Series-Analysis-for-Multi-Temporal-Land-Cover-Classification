
# coding: utf-8

# In[57]:


def MNDWI(mndwi_input_band4, mndwi_input_band5, path):
    file1 = gdal.Open(str(mndwi_input_band4))
    file2 = gdal.Open(str(mndwi_input_band5))
    file1 = file1.ReadAsArray()
    file2 = file1.ReadAsArray()
    a,b = file1.shape


# In[58]:


final_arr = np.zeros((a, b))
for i in range(a):
    for j in range(b):
        final_arr[i][j] = (file2[i][j] - file1[i][j])*100/(file1[i][j] + file2[i][j]) #-100 to +100




# In[61]:


inRaster = str(mndwi_input_band4)
inDS=gdal.Open(inRaster,1)
geoTransform = inDS.GetGeoTransform()
band=inDS.GetRasterBand(1)
datatype=band.DataType
print (datatype)
proj = inDS.GetProjection()


# In[62]:


outRaster =  r'E:\Internships\ISRO\Cities\delhi\Delhi 2017\LC081460402017120201T1-SC20171224010342\MNDWI.tif'
driver=inDS.GetDriver()
outDS = driver.Create(outRaster, b,a, 1,datatype)
geoTransform = inDS.GetGeoTransform()


# In[63]:


outDS.SetGeoTransform(geoTransform)
proj = inDS.GetProjection()
outDS.SetProjection(proj)
outBand = outDS.GetRasterBand(1)
outBand.WriteArray(final_arr,0,0)
outDS=None

