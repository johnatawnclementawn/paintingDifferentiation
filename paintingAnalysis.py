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

# Read files:
# Data location:
dataGDB = "\\Week05DataOnPaintings.gdb"
# Array of pictures to process:
pics = [path+dataGDB+"\\a",path+dataGDB+"\\b",path+dataGDB+"\\c",path+dataGDB+"\\d",path+dataGDB+"\\e"]

zsNeigh = 5
# NbrRectangle({width}, {height}, {units})
neighborhood = NbrRectangle(zsNeigh, zsNeigh, "CELL")

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


######################################################################################################### 
# Count the number of tallhills / low valleys  
def tallHills_lowValleys(inPainting, neighborhood, oneValPainting):
    # Get name of current picture that is being evaluated
    name = os.path.basename(inPainting)
        
    # Calculate focal stats mean x3 
    smooth = arcpy.sa.FocalStatistics(inPainting, neighborhood, "MEAN")
    smoother = arcpy.sa.FocalStatistics(smooth, neighborhood, "MEAN")
    smoothest = arcpy.sa.FocalStatistics(smoother, neighborhood, "MEAN")
    print(name + " smoothed")
    
    # Identify regions of great change by subtracting Mean x3 from original raster
    deviations = RasterCalculator([inPainting, smoothest], ["x", "y"], "x-y")
    print(name + " deviations created")
    
    # Reclassify to identify tall hills (high positives) and low valleys (low negatives)
    # Hard-coded values should be changed in the future
    # RemapRange args are ([startValue,endValue,newValue],...)
    # Using breaks defined by 5 quantile symbology 
    tallHills = Reclassify(deviations, "Value", "-3.497446 -0.431105 NODATA;-0.431105 -0.102569 NODATA;-0.102569 0.143834 NODATA;0.143834 0.444992 NODATA;0.444992 3.483955 1")
    lowValleys = Reclassify(deviations, "Value", "-3.497446 -0.431105 1;-0.431105 -0.102569 NODATA;-0.102569 0.143834 NODATA;0.143834 0.444992 NODATA;0.444992 3.483955 NODATA")
    print(name + " tall hills and low valleys identified")
    
    # Create zones for each individual hill / valley
    indvTallHills = RegionGroup(tallHills, "FOUR", "WITHIN", "ADD_LINK")
    indvLowValleys = RegionGroup(lowValleys, "FOUR", "WITHIN", "ADD_LINK")  
        
    # Count the number of tall hills / low valleys in the painting
    numTallHills = arcpy.sa.ZonalStatistics(oneValPainting, "Value", indvTallHills, "MAXIMUM")
    numLowValleys = arcpy.sa.ZonalStatistics(oneValPainting, "Value", indvLowValleys, "MAXIMUM")
    print(name + " tall hills and low valleys counted")
    
    # Save intermediates for viewing 
    oneValPainting.save(outFolder + "\\" + name + r"_oneValue")  
    smooth.save(outFolder + "\\" + name + r"_smooth")
    smoother.save(outFolder + "\\" + name + r"_smoother")
    smoothest.save(outFolder + "\\" + name + r"_smoothest")
    deviations.save(outFolder + "\\" + name + r"_deviations")
    tallHills.save(outFolder + "\\" + name + r"_tallHills")
    lowValleys.save(outFolder + "\\" + name + r"_lowValleys")
    indvTallHills.save(outFolder + "\\" + name + r"_indvTallHills")
    indvLowValleys.save(outFolder + "\\" + name + r"_indvLowValleys")
    numTallHills.save(outFolder + "\\" + name + r"_numTallHills")
    numLowValleys.save(outFolder + "\\" + name + r"_numLowValleys")
    print(name + " outputs saved to disk")
    
    # Return objects for later use
    return numTallHills, numLowValleys

#########################################################################################################
# Identify percentage of "rough" areas - essentially how many interactions between non-similar zones
def pctRough(inPainting, neighborhood, areaOVP):
    # Get name of current picture that is being evaluated
    name = os.path.basename(inPainting)
    
    # Calculate the standard deviation (roughness)
    roughness = arcpy.sa.FocalStatistics(inPainting, neighborhood, "STD")
    roughness.save(outFolder + "\\" + name + r"_roughness")
    
    # Select only really rough zones
    
    
    # Find total area of rough zone
    
    # Calculate area of rough zones as a percentage of total area
    
#########################################################################################################
# Iterate through images to process
for pic in pics:
    # Create single value painting raster
    oneValPainting = Reclassify(pic, "Value", "0.100000 10 1")
    # Calculate area of each individual painting
    areaOVP = ZonalGeometry(oneValPainting, "Value", "AREA")
    
    #tallHills_lowValleys(pic, neighborhood, oneValPainting)
    pctRough(pic, neighborhood, areaOVP)
print("Outputs saved! Have a look!") 
    
    