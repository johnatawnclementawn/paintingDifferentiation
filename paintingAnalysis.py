# Johnathan Clementi
# October 2021
# Raster GIS for Urban & Environmental Modeling - UPenn
# Automating Painting Differentiation

import os, sys
import arcpy
 
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'in_memory'

# Set Working Directory
os.chdir(r'D:\Users\Johnathan\Google Drive\Grad School\PennDesign_MUSA\RasterGIS_UrbanAndEnvironmentalModeling\Week5\wk5Homework')
path = os.getcwd()

# Read file:
pic1 = path + "\\Week05DataOnPaintings.gdb\\a"


# Check if output directory exists. Create a directory if one does not exist
outFolder = path + "\\output.gdb"
if os.path.exists(outFolder):
    if os.path.isdir(outFolder):
        print('The proper output folder exists, moving on')
    else:
        arcpy.management.CreateFileGDB(path, "output.gdb")
        print('Created the output directory')
else: 
    arcpy.management.CreateFileGDB(path, "output.gdb")
    print('Created the output directory')
 
# 
# def tallHills(inPainting):
#     
    