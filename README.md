## Landsat-Time-Series-Analysis-for-Multi-Temporal-Land-Cover-Classification

The Time series analysis for the landsat images was implemented using the random forest machine learning algorithm.
The algorithm classified the image into 4 classes:

1. Vegetation
2. Urban
3. Bare Soil
4. Water

To do the classification different phases were implemented.
1. The first phase includes the claculation of NDVI (Normalized Difference Vegetation Index) and the MNDWI(Modified Normalized Difference      Water Index).
2. The second phase involves the stacking of all these .tiff files into a single .tiff file.
   The stacking generally involves the use of bands from 2 to 7 , annual NDVI files and the MNDWI file of the selected day.
3. Using this Stacked image we predict the classes using our random forest algorithm and classify the images into the above mentioned 4        classes.
