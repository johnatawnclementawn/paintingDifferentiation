# Johnathan Clementi
# October, 2021
# Raster GIS for Urban & Environmental Modeling - UPenn
# Automating Painting Differentiation

import os, sys
import arcpy
 
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'in_memory'

# Set Working Directory
os.chdir(r'D:\Users\Johnathan\Google Drive\Grad School\PennDesign_MUSA\RasterGIS_UrbanAndEnvironmentalModeling\Week5\wk5Homework')

