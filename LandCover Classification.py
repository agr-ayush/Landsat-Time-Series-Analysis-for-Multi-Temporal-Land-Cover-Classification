
# coding: utf-8

# In[1]:


import gdal
import numpy as np
import matplotlib.pyplot as plt
import pickle


# In[2]:


ds_input = gdal.Open(r"E:\Internships\ISRO\Dataset3\Training\train_input_b.tif")
ds_output = gdal.Open(r"E:\Internships\ISRO\Dataset3\Training\train_output_b.tif")

input_imgarr = ds_input.ReadAsArray()
output_imgarr = ds_output.ReadAsArray()



# In[3]:


input_imgarr.shape


# In[4]:


output_imgarr.shape


# In[5]:


n_samples = (output_imgarr>0).sum()
n_samples


# In[6]:


labels = np.unique(output_imgarr[output_imgarr > 0])
print('The training data include {n} classes: {classes}'.format(n=labels.size, 
                                                                classes=labels))


# In[7]:


p = input_imgarr
q = np.array(p[0][0])
q.shape


# In[8]:


X = input_imgarr[:,output_imgarr>0]
Y = output_imgarr[output_imgarr>0]
X = X.T
print(X.shape)
print(Y.shape)


# In[9]:


p = Y.T
q = np.array(p)


# In[10]:


from sklearn.ensemble import RandomForestClassifier


# In[11]:


rf = RandomForestClassifier(n_estimators=5000,oob_score=True,n_jobs=-1)


# In[12]:


rf = rf.fit(X,Y)


# In[13]:


print('Our OOB prediction of accuracy is: {oob}%'.format(oob=rf.oob_score_ * 100))


# In[15]:


######Save Model###########
from sklearn.externals import joblib
joblib.dump(rf, 'E:\Internships\ISRO\Dataset3\LandCoverModel.pkl') 


# In[ ]:


########Load Model###############
rf = joblib.load('E:\Internships\ISRO\Dataset3\LandCoverModel.pkl') 


# In[14]:


predict_arr = gdal.Open(r"E:\Internships\ISRO\Dataset3\Testing\test_input_b.tif")


# In[15]:


img_predict = predict_arr.ReadAsArray()
img_predict = img_predict.T
img_predict.shape


# In[16]:


B = []
count=0
for i in range(len(img_predict[1])):
    count+=1
    print(count)
    class_predict = rf.predict(img_predict[:,i,:])
    B.append(class_predict)


# In[17]:


plt.imshow(B)


# In[18]:


B = np.array(B)
a,b = B.shape
a,b


# In[19]:


inRaster=r'E:\Internships\ISRO\Dataset3\Training\train_output_b.tif'
inDS=gdal.Open(inRaster,1)
print(inDS)
geoTransform = inDS.GetGeoTransform()
band=inDS.GetRasterBand(1)
datatype=band.DataType
proj = inDS.GetProjection()


# In[20]:


outRaster=r'E:\\Internships\\ISRO\\Dataset3\\Testing\\test_output_b.tif'
driver=inDS.GetDriver()
outDS = driver.Create(outRaster , b , a , 1 , datatype)
geoTransform = inDS.GetGeoTransform()
print(geoTransform)


# In[21]:


outDS.SetGeoTransform(geoTransform)
proj = inDS.GetProjection()
outDS.SetProjection(proj)
outBand = outDS.GetRasterBand(1)
outBand.WriteArray(B,0,0)
outDS=None

