# Johnathan Clementi
# October 2021
# Raster GIS for Urban & Environmental Modeling - UPenn
# Automating Painting Differentiation

import os, sys
import arcpy
from arcpy.sa import *
from arcpy.ia.raster_functions import RasterCalculator
from arcpy.sa.Functions import Reclassify, RegionGroup
# from arcpy.sa.Functions import Reclassify
# from arcpy.sa.ComplexArguments import RemapRange
 
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'in_memory'
# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

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
 
 
def tallHills_lowValleys(inPainting, zsNeigh):
    # NbrRectangle({width}, {height}, {units})
    neighborhood = NbrRectangle(zsNeigh, zsNeigh, "CELL")
    
    # Calculate focal stats mean x3 
    smooth = arcpy.sa.FocalStatistics(inPainting, neighborhood, "MEAN")
    smoother = arcpy.sa.FocalStatistics(smooth, neighborhood, "MEAN")
    smoothest = arcpy.sa.FocalStatistics(smoother, neighborhood, "MEAN")
    print("Smoooooth")
    
    # Identify regions of great change by subtracting Mean x3 from original raster
    deviations = RasterCalculator([inPainting, smoothest], ["x", "y"], "x-y", "FirstOf", "FirstOf")
    print("Deviations created")
    
    # Reclassify to identify tall hills (high positives) and low valleys (low negatives)
    # Hard-coded values should be changed in the future
    # RemapRange args are ([startValue,endValue,newValue],...)
    # Using breaks defined by 5 quantile symbology 
    tallHills = Reclassify(deviations, "Value", "-3.497446 -0.431105 NODATA;-0.431105 -0.102569 NODATA;-0.102569 0.143834 NODATA;0.143834 0.444992 NODATA;0.444992 3.483955 1")
    lowValleys = Reclassify(deviations, "Value", "-3.497446 -0.431105 1;-0.431105 -0.102569 NODATA;-0.102569 0.143834 NODATA;0.143834 0.444992 NODATA;0.444992 3.483955 NODATA")
    
    print("Identifying your tall hills and low valleys")
    
    # Create zones for each individual hill / valley
    indvTallHills = RegionGroup(tallHills, "FOUR", "WITHIN", "ADD_LINK")
    indvLowValleys = RegionGroup(lowValleys, "FOUR", "WITHIN", "ADD_LINK")
    print("Seperate them!")
    
    # Create single value painting raster
    #painting1 = Reclassify(inPainting, "Value", RemapRange[0.1,10,1])
    
    # Save outputs for viewing
    smooth.save(outFolder + "\\smooth")
    smoother.save(outFolder + "\\smoother")
    smoothest.save(outFolder + "\\smoothest")
    deviations.save(outFolder + "\\deviations")
    tallHills.save(outFolder + "\\tallHills")
    lowValleys.save(outFolder + "\\lowValleys")
    indvTallHills.save(outFolder + "\\indvTallHills")
    indvLowValleys.save(outFolder + "\\indvLowValleys")
    print("Outputs saved! Have a look!")
    
tallHills_lowValleys(pic1, 5)
    
    
    
    
    
    
    