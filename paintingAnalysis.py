# Johnathan Clementi
# October 2021
# Raster GIS for Urban & Environmental Modeling - UPenn
# Automating Painting Differentiation

import os, sys
import numpy
import arcpy
from arcpy.sa import *
from arcpy.ia.raster_functions import RasterCalculator
from arcpy.management import ReclassifyField

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
intermediates = path + "\\intermediates.gdb"
if os.path.exists(intermediates):
    if os.path.isdir(intermediates):
        print('The proper intermediates folder exists, moving on')
    else:
        arcpy.management.CreateFileGDB(path, "intermediates.gdb")
        print('Created the intermediates directory')
else: 
    arcpy.management.CreateFileGDB(path, "intermediates.gdb")
    print('Created the intermediates directory')

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
# Quantiles reclassification function courtesy of 
# https://gis.stackexchange.com/questions/309808/classifying-quantiles-in-raster-dataset-with-arcpy
def reclassify_by_quantiles(raster, quantiles):
    desc = arcpy.Describe(raster)

    # Get the quantile break points
    percentiles = list()
    for i in range(1, quantiles):
        percentiles.append(i * (100.0/quantiles))

    # Ensure that the raster is a raster object, in order to identify the minimum and
    #   maximum values
    if type(raster) != arcpy.Raster:
        raster = arcpy.Raster(raster)

    value_minimum = raster.minimum
    value_maximum = raster.maximum

    # Identify a value that does not occur in the raster
    null_value = value_minimum - 1

    # If the raster is not an integer type, then there is no need to futz with NaNs
    if desc.pixelType.startswith('F'):
        arr = arcpy.RasterToNumPyArray(raster, nodata_to_value=numpy.NaN)
    # Since integer arrays can't contain NaNs, you must do wackiness
    else:
        # Convert to an array, setting NoData cells to the unique value
        arr = arcpy.RasterToNumPyArray(raster, nodata_to_value=null_value)
        # Convert the array of integers to an array of floats
        arr = arr.astype('float')
        # Replace the placeholder null value with NaNs
        arr[arr==null_value] = numpy.NaN

    # Compile the quantile breaks
    breakpoints = list(numpy.nanpercentile(arr, percentiles))
    breakpoints.insert(0, value_minimum)
    breakpoints.append(value_maximum)

    # You no longer need the array...though you could do the remaining calculations
    #   on the array instead of one the raster
    del(arr)

    # Map the ranges to class numbers
    remap_table = list()
    for index, breakpt in enumerate(breakpoints[:-1]):
        remap_table.append([breakpt, breakpoints[index+1], index+1])
    remap = RemapRange(remap_table)

    result = Reclassify(raster, 'Value', remap)
    return result



######################################################################################################### 
# Count the number of tallhills / low valleys  
def tallHills_lowValleys(inPainting, name, neighborhood, oneValPainting):
        
    # Calculate focal stats mean x3 
    smooth = FocalStatistics(inPainting, neighborhood, "MEAN")
    smoother = FocalStatistics(smooth, neighborhood, "MEAN")
    smoothest = FocalStatistics(smoother, neighborhood, "MEAN")
    print(name + " smoothed")
    
    # Identify regions of great change by subtracting Mean x3 from original raster
    deviations = RasterCalculator([inPainting, smoothest], ["x", "y"], "x-y")
    print(name + " deviations created")
    
    # Reclassify to identify tall hills (high positives) and low valleys (low negatives)
    # Hard-coded values should be changed in the future
    # RemapRange args are ([startValue,endValue,newValue],...)
    # Using breaks defined by 5 quantile symbology 
    deviationsQuantiles = reclassify_by_quantiles(deviations, 5)
    tallHills = Reclassify(deviationsQuantiles, "VALUE", "1 NODATA;2 NODATA;3 NODATA;4 NODATA;5 1", "DATA")
    lowValleys = Reclassify(deviationsQuantiles, "VALUE", "1 1;2 NODATA;3 NODATA;4 NODATA;5 NODATA", "DATA")
    print(name + " tall hills and low valleys identified")
    
    # Create zones for each individual hill / valley
    indvTallHills = RegionGroup(tallHills, "FOUR", "WITHIN", "ADD_LINK")
    indvLowValleys = RegionGroup(lowValleys, "FOUR", "WITHIN", "ADD_LINK")  
        
    # Count the number of tall hills / low valleys in the painting
    numTallHills = ZonalStatistics(oneValPainting, "Value", indvTallHills, "MAXIMUM")
    numLowValleys = ZonalStatistics(oneValPainting, "Value", indvLowValleys, "MAXIMUM")
    print(name + " tall hills and low valleys counted")
    
    # Save intermediates for viewing 
    oneValPainting.save(intermediates + "\\" + name + r"_oneValue")  
    smooth.save(intermediates + "\\" + name + r"_smooth")
    smoother.save(intermediates + "\\" + name + r"_smoother")
    smoothest.save(intermediates + "\\" + name + r"_smoothest")
    deviations.save(intermediates + "\\" + name + r"_deviations")
    tallHills.save(intermediates + "\\" + name + r"_tallHills")
    lowValleys.save(intermediates + "\\" + name + r"_lowValleys")
    indvTallHills.save(intermediates + "\\" + name + r"_indvTallHills")
    indvLowValleys.save(intermediates + "\\" + name + r"_indvLowValleys")
    numTallHills.save(intermediates + "\\" + name + r"_numTallHills")
    numLowValleys.save(intermediates + "\\" + name + r"_numLowValleys")
    print(name + " th/lv outputs saved to disk")
    
    # Return objects for later use
    return [numTallHills, numLowValleys]



#########################################################################################################
# Identify percentage of "rough" areas - essentially how many interactions between non-similar zones
def pctRough(inPainting, name, neighborhood, oneValPainting, areaOVP):
    
    # Calculate the standard deviation (rough)
    rough = FocalStatistics(inPainting, neighborhood, "STD")
    rough.save(intermediates + "\\" + name + r"_rough")
    
    # Reclass upper quantile
    roughQuantiles = reclassify_by_quantiles(rough, 5)
    veryRough = Reclassify(roughQuantiles, "VALUE", "1 NODATA;2 NODATA;3 NODATA;4 NODATA;5 1", "DATA")
    veryRough.save(intermediates + "\\" + name + r"_veryRough")    
    
    # Find total area of rough zone
    vRoughArea = ZonalGeometry(veryRough, "VALUE", "AREA")
    vRoughArea.save(intermediates + "\\" + name + r"_vRoughArea")
    
    # Calculate area of rough zones as a percentage of total area
    maxRoughArea = ZonalStatistics(oneValPainting, "VALUE", vRoughArea, "MAXIMUM")
    pctRoughArea = RasterCalculator([maxRoughArea, areaOVP], ["x", "y"], "(x/y)*1000")
    areaOVP.save(intermediates + "\\" + name + r"_areaOVP")
    pctRoughArea.save(intermediates + "\\" + name + r"_pctRoughArea")
    print(name + " pct rough area calculated")

    return pctRoughArea



#########################################################################################################
# Identify average slope 
def avgSlopeF(inPainting, name, oneValPainting):
    
    # Slope is the 
    slope = Slope(inPainting, "PERCENT_RISE", 1, "PLANAR", "METER")
    slope.save(intermediates + "\\" + name + r"_slope")
    
    avgSlope = ZonalStatistics(oneValPainting, "VALUE", slope, "MEAN")
    avgSlope.save(intermediates + "\\" + name + r"_avgSlope")
    print(name + " calculated slope")
    
    return avgSlope



#########################################################################################################
# Identify average aspect - direction of downhill slope
def avgAspectF(inPainting, name, oneValPainting):
    
    # Slope is the 
    aspect = Aspect(inPainting, "PLANAR", "METER", "GEODESIC_AZIMUTHS")
    aspect.save(intermediates + "\\" + name + r"_aspect")
    
    avgAspect = ZonalStatistics(oneValPainting, "VALUE", aspect, "MEAN")
    avgAspect.save(intermediates + "\\" + name + r"_avgAspect")
    print(name + " calculated aspect")
    
    return avgAspect



#########################################################################################################
# Final Score Calculation 
def scoreCalculator(name, numTallHills, numLowValleys, pctRoughArea, avgSlope, avgAspect):
    finalScore = RasterCalculator([numTallHills, numLowValleys, pctRoughArea, avgSlope, avgAspect], ["x", "y", "z", "a", "b"], "x+y+z+a+b")
    finalScore.save(outFolder + "\\" + name + r"_finalScore")
    
    tHlV_RoughScore = RasterCalculator([numTallHills, numLowValleys, pctRoughArea], ["x", "y", "z"], "x+y+z")
    tHlV_RoughScore.save(outFolder + "\\" + name + r"_tHlV_RoughScore")
    
    slopeAspectScore = RasterCalculator([avgSlope, avgAspect], ["a", "b"], "a+b")
    slopeAspectScore.save(outFolder + "\\" + name + r"_slopeAspectScore")
    print(name + " final score calculated")
    
    return finalScore
 


#########################################################################################################
# Use main function to pass return values between functions
def main():
    numTallHills, numLowValleys = tallHills_lowValleys(pic, name, neighborhood, oneValPainting)
    pctRoughArea = pctRough(pic, name, neighborhood, oneValPainting, areaOVP)
    avgSlope = avgSlopeF(pic, name, oneValPainting)
    avgAspect = avgAspectF(pic, name, oneValPainting)
    scoreCalculator(name, numTallHills, numLowValleys, pctRoughArea, avgSlope, avgAspect)


    
#########################################################################################################
# Iterate through images to process
for pic in pics:
    # Get name of current picture that is being evaluated
    name = os.path.basename(pic)
        
    # Create single value painting raster
    oneValPainting = Reclassify(pic, "Value", "0.100000 10 1")
    
    # Calculate area of each individual painting
    areaOVP = ZonalGeometry(oneValPainting, "Value", "AREA")
    
    main()
    
    
        
print("Outputs saved! Have a look!") 
    
    