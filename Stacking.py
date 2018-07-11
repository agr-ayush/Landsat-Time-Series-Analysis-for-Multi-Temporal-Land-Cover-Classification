
# coding: utf-8

# In[1]:


import gdal
import numpy as np


outvrt = '/vsimem/stacked.vrt' #/vsimem is special in-memory virtual "directory"
outtif = r'path for storing the stacked image'
tifs = [
        ##Paths for all the images to be stacked.
       ] 

outds = gdal.BuildVRT(outvrt, tifs, separate=True)
outds = gdal.Translate(outtif, outds)

outds=None



