# 2D shape analysis
#
#Written by Matthew J. Gastinger
#
#Aug 2020 - Imaris 9.6.0

# <CustomTools>
#     <Menu>
#         <Submenu name="Surfaces Functions">
#             <Item name="2D Shape Analysis5 beta" icon="Python3">
#                 <Command>Python3XT::XT_MJG_Shape_Analysis5_beta(%i)</Command>
#             </Item>
#         </Submenu>
#     </Menu>
#     <SurpassTab>
#         <SurpassComponent name="bpSurfaces">
#             <Item name="2D Shape Analysis5 beta" icon="Python3">
#                 <Command>Python3XT::XT_MJG_Shape_Analysis5_beta(%i)</Command>
#             </Item>
#         </SurpassComponent>
#     </SurpassTab>
# </CustomTools>
#
#Description:
#This XTension will calculate a variety of 2D statistics.  If isosurface is 2D,
#the calculations are done on mask of the surface on the slice.  If the isosurface
#if 3D, the closest slice to the center of homegeneous mass of the surface is used

#
#Ring mask generated using   ndimage.filters.generic_filter(vSliceData, np.std, size=2)

#
#All statistics are based on a masked surface at the midline of the 3D surface,
#or in a 2D slice.
#Definite of New Statistics:
# 1.Perimeter midline
#     1)Border Perimeter midline (convexhull)
#           Measurement of the length of the perimeter of the calculated 2D convexhull
#
#     2)Border Perimeter midline - Contour vertices
            #Measurement of the contour vertices and walking distances between vertices (better)
# 2.2D cross-sectional area (at midline)
#     1) 2DArea -- Quantification of voxels inside the mask multiplied by size of one pixel
#     2) 2DArea convexhull -- of the Convexhull created from the border pixels
# 3.Chord Max length
#     -Maximum distance edge to edge
#        (takes all points, and does a pairwise distance measure along the perimeter
#           find the largest distance)
# 4. Compactness
#       -A measure of roundness or circularity (area to perimeter ratio) which includes local irregularities
#           defined as the ratio of the area of an object to the area of a circle with the actual perimeter
# 5. Circularity
#       -A measure of roundness or circularity (area to perimeter ratio) which excludes local irregularities
#           can be obtained as the ratio of the area of an object to the area of a circle with the same convex perimeter
# 6. Convexity
#       -Relative amount that an object differs from a convex object.
#       -A measure of convexity can be obtained by # forming the ratio of the
#        -perimeter of an object’s convex hull to the perimeter of the object
# 6. Solidity
#        Solidity is the ratio of contour area to its convex hull area.
# 7.Diameter of Equivalent Circle (Compactness)
#     -Diameter of circle based on the actual perimeter=circle circumference
#      -Defined as the ratio of the area of an object to the area of a circle with
#           the same perimeter.
# 8.FeretDiameter Max
#     -BoundingBoxOO Length C - for the surfaces
# 9.Feret Diameter Max90
#     -BoundingBoxOO Length B - surfaces
#     -the Feret diameter measured at an angle of 90 degrees to that of the
#       maximum Feret diameter.
# 10. Intensity of the border ring at midline (measured without physically making ring)
#     -IntensityMean
#     -IntensityMedian
#     -IntensityMax
# 10a. Expanded border for intensity statistics only.  Will NOT affect any other stat.

#NOTE: If Imaris Ring surfaces are not made:
#            FeretDiameterMax = BoundingBoxOOLengthC (for original surface)
#            FeretDiameterMax90 = BoundingBoxOOLengthB (for original surface)

import time
import numpy as np
from scipy.spatial import ConvexHull#, convex_hull_plot_2d
from scipy.spatial.distance import euclidean
from scipy.spatial.distance import cdist
import scipy.ndimage as ndimage
# import matplotlib.pyplot as plt
from operator import itemgetter
import operator
#import matplotlib.pyplot as plt
import cv2
from statistics import mean
from statistics import median
# from sklearn.neighbors import NearestNeighbors
# # import networkx as nx
# from skimage.measure import perimeter
# from shapely.geometry import LineString
from itertools import chain


# GUI imports
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import ImarisLib

#aImarisId=0
def XT_MJG_Shape_Analysis5_beta(aImarisId):
    # Create an ImarisLib object
    vImarisLib = ImarisLib.ImarisLib()
    # Get an imaris object with id aImarisId
    vImarisApplication = vImarisLib.GetApplication(aImarisId)
    # Get the factory
    vFactory = vImarisApplication.GetFactory()
    # Get the currently loaded dataset
    vImage = vImarisApplication.GetDataSet()
    # Get the Surpass scene
    vSurpassScene = vImarisApplication.GetSurpassScene()

    ############################################################################
    ############################################################################

    #Dialog window
    ############################################################################
    window = tk.Tk()
    window.title('2D Shape Analysis')
    #window.geometry('75x100')
    window.attributes("-topmost", True)

    ##################################################################
    #Set input in center on screen
    # Gets the requested values of the height and widht.
    windowWidth = window.winfo_reqwidth()
    windowHeight = window.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(window.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(window.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    window.geometry("+{}+{}".format(positionRight, positionDown))
    ##################################################################
    def ShapeAnalysis_Options():
        global vOptionMakeRings, vOptionMeasureIntensity,vOptionExpandBorderIntensity
        global zDilateRing
        vOptionMakeRings=var1.get()
        vOptionMeasureIntensity=var2.get()
        vOptionExpandBorderIntensity=var3.get()
        zDilateRing=0
        if vOptionExpandBorderIntensity==1:
            zDilateRing=4
        window.destroy()

    var1 = tk.IntVar(value=0)
    var2 = tk.IntVar(value=0)
    var3 = tk.IntVar(value=0)

    tk.Label(window, font="bold", text='Extra Features').grid(row=0,column=0)
    tk.Checkbutton(window, text='Create midline Perimeter Surface (Longer Processing Time)',
                    variable=var1, onvalue=1, offvalue=0).grid(row=1, column=0, padx=40,sticky=W)
    tk.Checkbutton(window, text='Calculate Border Intensity at midline',
                    variable=var2, onvalue=1, offvalue=0).grid(row=2, column=0, padx=40,sticky=W)
    tk.Checkbutton(window, text='Expand Border',
                    variable=var3, onvalue=1, offvalue=0).grid(row=3, column=0, padx=85,sticky=W)

    btn = Button(window, text="Calculare Statistics", bg='blue', fg='white', command=ShapeAnalysis_Options)
    btn.grid(column=0, row=4, sticky=W, padx=100)

    # tk.Label(window, font="bold", text='Statistics Calculated:\n').grid(row=5,column=0,sticky=E)
    # tk.Label(window, text='Perimeter midline, 2DArea cross section (midline)\n'
    #                      'Compactness, Circularity, Convexity\n'
    #                      'Diameter Equivalent Circle\n'
    #                      'Feret Diameter, Chord Max Length\n'
    #                      'Intensity border ring').grid(row=6,column=0,sticky=E)


    window.mainloop()

    ############################################################################
    ############################################################################
    #testing surface masking
    vDataMin = [vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ()]
    vDataMax = [vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ()]
    vDataSize = [vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ()]
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    aXvoxelSpacing= (vDataMax[0]-vDataMin[0])/vDataSize[0]
    aYvoxelSpacing= (vDataMax[1]-vDataMin[1])/vDataSize[1]
    aZvoxelSpacing = round((vDataMax[2]-vDataMin[2])/vDataSize[2],3)
    vSmoothingFactor=aXvoxelSpacing*2

    #get all surfaces
    vSurfaces = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
    vNumberOfSurfaces = vSurfaces.GetNumberOfSurfaces()
    if vOptionMakeRings==1:
        vPerimeterRings = vImarisApplication.GetFactory().CreateSurfaces()
        vPerimeterRingsWorking = vImarisApplication.GetFactory().CreateSurfaces()

    #Define slice# and Z position
    vZSlicePosition=[vDataMin[2]]
    for vSliceIndex in range (vDataSize[2]):
        vZSlicePosition.append(vZSlicePosition[vSliceIndex]+aZvoxelSpacing)

    #add additional channel
    if vOptionMeasureIntensity==1:
        vImage.SetSizeC(vSizeC + 1)
        TotalNumberofChannels=vSizeC+1
        vLastChannel=TotalNumberofChannels-1

    #make Imaris invisible for faster running
    # if vNumberOfSurfaces>100:
    #     vImarisApplication.SetVisible(~vImarisApplication.GetVisible)

    #Generate postions from center of mass
    vPositionFinal=[]
    for SurfaceIndex  in range (vNumberOfSurfaces):
        vPositionFinal.extend(vSurfaces.GetCenterOfMass(SurfaceIndex))

    #############################
    #############################
    vNewStatConvexhullPerimeter=[]
    vNewStatPerimeterBinaryPixels=[]
    vNewStatPerimeterContourVertices=[]
    vNewStat_2D_Perimeter_Contours=[]
    vAllTimeIndices=[]
    vNewStatMaxChordLength=[]
    vNewStatDiameterEquivCircle=[]
    vNewStat_2D_Area_CrossSectionalPixels=[]
    vNewStat_2D_Area_CrossSectionalConvexhull=[]
    vNewStat_2D_Area_Contours=[]
    vNewStatCircularity=[]
    vNewStatCompactness=[]
    vNewStatConvexity=[]
    vNewStatSolidity=[]
    ########################
    ########################

    # Create the master object
    master = tk.Tk()
    # Create a progressbar widget
    progress_bar = ttk.Progressbar(master, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    # And a label for it
    label_1 = tk.Label(master, text="2D shape - Progress Bar")
    # Use the grid manager
    label_1.grid(row=0, column=0,pady=10)
    progress_bar.grid(row=0, column=1)
    master.geometry('250x50')
    master.attributes("-topmost", True)


    #################################################################
    #Set input in center on screen
    # Gets the requested values of the height and widht.
    windowWidth = master.winfo_reqwidth()
    windowHeight = master.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(master.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(master.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    master.geometry("+{}+{}".format(positionRight, positionDown))
    ##################################################################

    # Necessary, as the master object needs to draw the progressbar widget
    # Otherwise, it will not be visible on the screen
    master.update()
    progress_bar['value'] = 0
    master.update()
    zRingIntensityMean=[]
    zRingIntensityMedian=[]
    zRingIntensityMax=[]
    qIsBadSurface=False
    qIsPerimeterFail=False
    wNewStatCount=0
    wNewCountPerimeterFail=0
    #cycle thru random color mask indices
    for vSurfaceIndex in range (vNumberOfSurfaces):
        vPositionXYZworking = vSurfaces.GetCenterOfMass(vSurfaceIndex)
        vAllTimeIndices.append(vSurfaces.GetTimeIndex(vSurfaceIndex))
    #Find slice closest to the center of mass
        if vDataSize[2]!=1:
            vSliceIndexZ=(list(map(abs, [i-vPositionXYZworking[0][2] for i in vZSlicePosition])))
            vSurfaceIndexMiddle=vSliceIndexZ.index(min(vSliceIndexZ))
        else:
            vSurfaceIndexMiddle=0

        zMaskSingleSurface = vSurfaces.GetSingleMask(vSurfaceIndex,
                                                 vDataMin[0],
                                                 vDataMin[1],
                                                 vDataMin[2],
                                                 vDataMax[0],
                                                 vDataMax[1],
                                                 vDataMax[2],
                                                 vDataSize[0],
                                                 vDataSize[1],
                                                 vDataSize[2])

        #Generate slice to find center of Surfacemask
        if vSurfaceIndexMiddle!=0:
            vSlice = zMaskSingleSurface.GetDataSliceShorts(vSurfaceIndexMiddle-1, 0, 0)
        else:
            vSlice = zMaskSingleSurface.GetDataSliceShorts(vSurfaceIndexMiddle, 0, 0)

        zMaskTest=int(np.amax(vSlice))
        if zMaskTest==0:
            qIsBadSurface=True
            if vOptionMeasureIntensity==1:
                zRingIntensityMean.append(999994)
                zRingIntensityMax.append(999994)
                zRingIntensityMedian.append(999994)
        #pad stat result for "bad surface masking"
            vNewStatConvexhullPerimeter.append(999994)
            vNewStatPerimeterContourVertices.append(999994)
            vNewStat_2D_Area_CrossSectionalPixels.append(999994)
            vNewStatDiameterEquivCircle.append(999994)
            vNewStat_2D_Area_CrossSectionalConvexhull.append(999994)
            vNewStat_2D_Area_Contours.append(999994)
            vNewStatCircularity.append(999994)
            vNewStatCompactness.append(999994)
            vNewStatConvexity.append(999994)
            vNewStatSolidity.append(999994)

            continue

        vSliceNumpy=np.array(vSlice)
        vSliceNumpyNew=ndimage.binary_fill_holes(vSliceNumpy).astype(float)
        vSliceNumpyNew=ndimage.grey_erosion(vSliceNumpyNew, size=(2,1))

        if vOptionMeasureIntensity==1 or vOptionMakeRings==1:
        ## find the non-zero min-max coords of canny

            pts = np.argwhere(vSliceNumpy>0)
            y1,x1 = pts.min(axis=0)
            y2,x2 = pts.max(axis=0)

            #test if mask share edge of slice border
            y1CropAdj=0
            y2CropAdj=0
            x1CropAdj=0
            x2CropAdj=0

            if y1==0:
                y1CropAdj=2+zDilateRing
            if y2==0:
                y2CropAdj=2+zDilateRing
            if x1==0:
                x1CropAdj=2+zDilateRing
            if x2==0:
                x2CropAdj=2+zDilateRing

            ## crop the region
            vSlicecropped = vSliceNumpy[y1-2+y1CropAdj-zDilateRing:y2+2-y2CropAdj+zDilateRing,
                                        x1-2+x1CropAdj-zDilateRing:x2+2-x2CropAdj+zDilateRing]
            vSlicecropped=ndimage.binary_fill_holes(vSlicecropped).astype(float)
            vSlicecropped=ndimage.grey_erosion(vSlicecropped, size=(2,1))

            start = time.time()
            #Run Variance filter thru scipy to find edges of the binary
            if vOptionExpandBorderIntensity==1:
                vVarianceFilterResult=ndimage.filters.generic_filter(vSlicecropped, np.std, size=4)
            else:
                vVarianceFilterResult=ndimage.filters.generic_filter(vSlicecropped, np.std, size=2)

            # imshow(vSlicecroppedfilled)
            # imshow(vSlicecropped)
            # imshow(vSlice)
            # imshow(vSliceNumpy)
            # imshow(vVarianceFilterResult)
            # imshow(vSlicecroppedDenoised)

        ############################################################################
            #need to set the ring back into the original frame
            zNumColRight=(vSliceNumpy.shape[1]-x2-2-zDilateRing) # 12 col on right
            zNumColLeft=x1-2-zDilateRing    #110 col left
            zNumRowBottom=(vSliceNumpy.shape[0]-y2-2-zDilateRing) #30 row bottom
            zNumRowTop=y1-2-zDilateRing   #46 row top
            #add columns to right - test if on border
            if zNumColRight>0:
                vVarianceFilterResult = np.column_stack( [ vVarianceFilterResult , [[0]*zNumColRight]*vVarianceFilterResult.shape[0] ] )
            #add columns to left - test if on border
            if zNumColLeft>0:
                vVarianceFilterResult = np.column_stack( [ [[0]*zNumColLeft]*vVarianceFilterResult.shape[0], vVarianceFilterResult ] )
            #add rows to bottom - test if on border
            if zNumRowBottom>0:
                vVarianceFilterResult = np.row_stack( [ vVarianceFilterResult , [[0]*vSliceNumpy.shape[1]]*zNumRowBottom ] )
            #add rows to top - test if on border
            if zNumRowTop >0:
                vVarianceFilterResult = np.row_stack( [ [[0]*vSliceNumpy.shape[1]]*zNumRowTop, vVarianceFilterResult ] )

    ############################################################################
    #Get intensity in all channels for new Statistic
        if vOptionMeasureIntensity==1:
            for cIndex in range (vSizeC):
                if vSurfaceIndexMiddle!=0:
                    vSlice = vImage.GetDataSliceFloats(vSurfaceIndexMiddle-1,cIndex,vAllTimeIndices[vSurfaceIndex])
                else:
                    vSlice = vImage.GetDataSliceFloats(vSurfaceIndexMiddle,cIndex,vAllTimeIndices[vSurfaceIndex])
        #Compare vSlice and ring slice - find all values insvSlice that are in ring
                zRingIntensityMean.append(mean(np.array(vSlice)[vVarianceFilterResult > 0]))
                zRingIntensityMax.append(max(np.array(vSlice)[vVarianceFilterResult > 0]))
                zRingIntensityMedian.append(median(np.array(vSlice)[vVarianceFilterResult > 0]))

    ############################################################################
    #Set Donut FinalMask (donut) to new channel
        if vOptionMakeRings==1:
            vVarianceFilterResult[vVarianceFilterResult > 0] = 10#if pixel >0 set to 0 numpy solution
            vFinalMaskToList = vVarianceFilterResult.tolist()
            if vSurfaceIndexMiddle!=0:
                vImage.SetDataSliceFloats(vFinalMaskToList,vSurfaceIndexMiddle-1,vSizeC,vAllTimeIndices[vSurfaceIndex])
            else:
                vImage.SetDataSliceFloats(vFinalMaskToList,vSurfaceIndexMiddle,vSizeC,vAllTimeIndices[vSurfaceIndex])

    #############################################
        vSliceNumpyNew = vSliceNumpyNew.astype('float')
    ###############################################
    #Calculate contour perimeter and convexhull
        ret,zThresh = cv2.threshold(vSliceNumpyNew.astype(float),0,255,0)
        zThreshBinary=zThresh.astype(np.uint8)
        zContours,zHierarchy = cv2.findContours(zThreshBinary, 1, 2)
    # # create hull array for convex hull vertices
        hull = []
        # calculate points for each contour
        for i in range(0,len(zContours)):
            vertices = zContours[i]
        hull=cv2.convexHull(vertices)
    #Calculate ChordLength
        for i in range (len(vertices)):
            vertices[i]
    ##Find MaxChord Length
        if len(vertices)>2:
            #Calculate Max chord length from contour vertices
            wContourVertices = list(chain.from_iterable(vertices.tolist()))
            vDistanceArray=cdist(wContourVertices,wContourVertices)
            vNewStatMaxChordLength.append(np.max(vDistanceArray)*aXvoxelSpacing)
    ###############################################
        #Calculated 2D Cross section area from contour vertices
            vNewStat_2D_Area_Contours.append(cv2.contourArea(vertices)*aXvoxelSpacing*aYvoxelSpacing)
        #Find 2D area of convex hull
            vNewStat_2D_Area_CrossSectionalConvexhull.append(cv2.contourArea(hull)*aXvoxelSpacing*aYvoxelSpacing)
    ##############################################
        #Calcualte Perimeters
        #Contour perimeter
            vNewStatPerimeterContourVertices.append(cv2.arcLength(vertices,True)*aXvoxelSpacing)
        #Convexhull perimeter
            vNewStatConvexhullPerimeter.append(cv2.arcLength(hull,True)*aXvoxelSpacing)
        #Find diameter from equivalent circle
            vNewStatDiameterEquivCircle.append(vNewStatPerimeterContourVertices[vSurfaceIndex]/3.1415926)
        #Compactness (alternative)
        #Objects which have an elliptical shape, or a boundary that is irregular rather than smooth, will decrease the measure.
            vNewStatCompactness.append(4*3.1415926*vNewStat_2D_Area_Contours[vSurfaceIndex]/(vNewStatPerimeterContourVertices[vSurfaceIndex]**2))
        #Convexity is the relative amount that an object differs from a convex object
            vNewStatConvexity.append(vNewStatConvexhullPerimeter[vSurfaceIndex]/vNewStatPerimeterContourVertices[vSurfaceIndex])
        #Circularity= 4*pi*Area/(P*P) Excludes local irregularities
            vNewStatCircularity.append(4*3.1415926*vNewStat_2D_Area_Contours[vSurfaceIndex]/(vNewStatConvexhullPerimeter[vSurfaceIndex]**2))
        # #Solidity -- Solidity is the ratio of contour area to its convex hull area.
            vNewStatSolidity.append(vNewStat_2D_Area_Contours[vSurfaceIndex]/vNewStat_2D_Area_CrossSectionalConvexhull[vSurfaceIndex])

        else:
            qIsPerimeterFail=True
            vNewStatMaxChordLength.append(9999944)
            vNewStat_2D_Area_Contours.append(9999944)
            vNewStat_2D_Area_CrossSectionalConvexhull.append(9999944)
            vNewStatPerimeterContourVertices.append(9999944)
            vNewStatConvexhullPerimeter.append(9999944)
            vNewStatDiameterEquivCircle.append(9999944)
            vNewStatCompactness.append(9999944)
            vNewStatConvexity.append(9999944)
            vNewStatCircularity.append(9999944)
            vNewStatSolidity.append(9999944)
            wNewCountPerimeterFail=wNewCountPerimeterFail+1
    #############################################
        #Quantify cross-sectional area by voxel count
        vNewStat_2D_Area_CrossSectionalPixels.append(np.count_nonzero(vSliceNumpyNew)*aXvoxelSpacing*aYvoxelSpacing)
    ###############################################################################
    #Set Donut result to new channel - If the option is checked
        if vOptionMakeRings==1:
            ip = vImarisApplication.GetImageProcessing()
        #Make single Surface from Donut channel using ROI. no smoothing
            vLowerThreshold=10
            vPerimeterRingsWorking = ip.DetectSurfacesWithUpperThreshold(vImage,
                                                                    [[0,
                                                                      0,
                                                                      vSurfaceIndexMiddle-1,
                                                                      vAllTimeIndices[vSurfaceIndex],
                                                                      vDataSize[0],
                                                                      vDataSize[1],
                                                                      vSurfaceIndexMiddle-1,
                                                                      vAllTimeIndices[vSurfaceIndex]]],
                                                                      vLastChannel, 0, 0, True,False,
                                                                      vLowerThreshold-0.5,True, False,
                                                                      vLowerThreshold,'')
            if vPerimeterRingsWorking.GetNumberOfSurfaces()==1:
                vNewPerimeterRingsIndex=[0]
                vPerimeterRingsWorking.CopySurfacesToSurfaces(vNewPerimeterRingsIndex, vPerimeterRings)

        progress_bar['value'] = int((vSurfaceIndex+1)/vNumberOfSurfaces*100)
        master.update()
    master.destroy()
    master.mainloop()

    #Create a new folder object for new ring surfaces - if option is checked
    if vOptionMakeRings==1:
        result = vFactory.CreateDataContainer()
        result.SetName('2D Shape Analysis -- ' + vSurfaces.GetName())
        vPerimeterRings.SetName('2D Perimeter Rings -- ' + vSurfaces.GetName())
        result.AddChild(vPerimeterRings, -1)
        vImarisApplication.GetSurpassScene().AddChild(result, -1)

    ####################################################
    vAllvSurfacesStatistics = vSurfaces.GetStatistics()
    vAllvSurfacesIds = vAllvSurfacesStatistics.mIds
    vAllvSurfaceIdsSorted=sorted((e,i) for i,e in enumerate(vAllvSurfacesIds))
    vAllvSurfacesStatNames = vAllvSurfacesStatistics.mNames
    vAllvSurfacesStatValues = vAllvSurfacesStatistics.mValues
    vNewStatFeretDiameterMaxIndex=[i for i,val in enumerate(vAllvSurfacesStatNames)
                                   if val==('BoundingBoxOO Length C')]
    vNewStatFeretDiameterMax90Index=[i for i,val in enumerate(vAllvSurfacesStatNames)
                                   if val==('BoundingBoxOO Length B')]
    if len(vNewStatFeretDiameterMaxIndex)>1:
        vNewStatFeretDiameterMax=list(itemgetter(*vNewStatFeretDiameterMaxIndex)(vAllvSurfacesStatValues))
        vNewStatFeretDiameterMax90=list(itemgetter(*vNewStatFeretDiameterMax90Index)(vAllvSurfacesStatValues))
    else:
        vNewStatFeretDiameterMax=[x[1] for x in enumerate(vAllvSurfacesStatValues)
                          if x[0] in vNewStatFeretDiameterMaxIndex]
        vNewStatFeretDiameterMax90=[x[1] for x in enumerate(vAllvSurfacesStatValues)
                          if x[0] in vNewStatFeretDiameterMax90Index]

    ####################################################
    #Remove the working channels
    if vOptionMeasureIntensity==1:
        vImarisApplication.GetDataSet().SetSizeC(vSizeC)

    ####################################################
    ####################################################
    #Generate Surface stat
        #number of new stat values
    vNumberOfNewStats=len(vNewStatConvexhullPerimeter)

    ####################################################
    vSurfaceStatvIds=list(range(vNumberOfNewStats))
    vSurfaceIDs=vSurfaces.GetIds()

    if qIsBadSurface==True:
        #Find index of marked stat values "999994"
        vBadSurfaceIdIndex=[i for i,val in enumerate(vNewStatConvexhullPerimeter)
                                    if val==999994]
        #remove bad surfaceIds and stats
        for ele in sorted(vBadSurfaceIdIndex, reverse = True):
            del vSurfaceStatvIds[ele]
            del vSurfaceIDs[ele]
            if vOptionMeasureIntensity==1:
                del zRingIntensityMean[ele]
                del zRingIntensityMax[ele]
                del zRingIntensityMedian[ele]
            del vNewStatConvexhullPerimeter[ele]
            del vNewStatPerimeterContourVertices[ele]
            del vNewStat_2D_Area_CrossSectionalPixels[ele]
            del vNewStatDiameterEquivCircle[ele]
            del vNewStat_2D_Area_CrossSectionalConvexhull[ele]
            del vNewStat_2D_Area_Contours[ele]
            del vNewStatCircularity[ele]
            del vNewStatCompactness[ele]
            del vNewStatConvexity[ele]
            del vNewStatFeretDiameterMax90[ele]
            del vNewStatFeretDiameterMax[ele]
        vNumberOfNewStats=len(vNewStatConvexhullPerimeter)

    if qIsPerimeterFail==True:
        vSurfaceIDsPerimeterFail=vSurfaceIDs
        vSurfaceIDsPerimeterFailRing=vSurfaceStatvIds
        #Find index of marked stat values "999994"
        vBadSurfaceIdPerimeterFailIndex=[i for i,val in enumerate(vNewStatPerimeterContourVertices)
                                    if val==9999944]
        for ele in sorted(vBadSurfaceIdPerimeterFailIndex, reverse = True):
            del vNewStatPerimeterContourVertices[ele]
            del vNewStatDiameterEquivCircle[ele]
            del vNewStatCompactness[ele]
            del vNewStatConvexity[ele]
            del vNewStatMaxChordLength[ele]
            del vNewStat_2D_Area_Contours[ele]
            del vNewStat_2D_Area_CrossSectionalConvexhull[ele]
            del vNewStatConvexhullPerimeter[ele]
            del vNewStatCircularity[ele]

            del vSurfaceIDsPerimeterFail[ele]
            del vSurfaceIDsPerimeterFailRing[ele]
        vNumberOfNewStatsPerimeterFail=len(vNewStatPerimeterContourVertices)

    ####################################################
    vSurfaceStatUnits=['um']*vNumberOfNewStats
    #Create Tuple list for each surface in time
    vSurfaceStatFactors=(['Surface']*vNumberOfNewStats,
                          [str(e) for e in [i+1 for i in vAllTimeIndices]])
    vSurfaceStatFactorName=['Category','Time']
    ####################################################
    if vOptionMakeRings==1:

        vSurfaceStatNames=[' Feret Diameter Max']*vNumberOfNewStats
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatFeretDiameterMax,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Ferret Diameter Max90']*vNumberOfNewStats
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatFeretDiameterMax90,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Area2D (from #pixels']*vNumberOfNewStats
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStat_2D_Area_CrossSectionalPixels,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)

    ####################################################
        if  qIsPerimeterFail==True:
            vSurfaceStatvIds=vSurfaceIDsPerimeterFailRing
            vNumberOfNewStats=vNumberOfNewStatsPerimeterFail
            vSurfaceStatFactors=(['Surface']*vNumberOfNewStatsPerimeterFail,
                              [str(e) for e in [i+1 for i in vAllTimeIndices]])
            vSurfaceStatUnits=['um']*vNumberOfNewStatsPerimeterFail
    ####################################################
    ####################################################
        vSurfaceStatNames=[' Border Perimeter midline - Contour vertices']*vNumberOfNewStats
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatPerimeterContourVertices,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Diameter of Equvialent Circle']*vNumberOfNewStats
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatDiameterEquivCircle,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Compactness']*vNumberOfNewStats
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatCompactness,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
        ####################################################
        vSurfaceStatNames=[' Convexity']*vNumberOfNewStats
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatConvexity,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Circularity']*vNumberOfNewStats
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatCircularity,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Solidity']*vNumberOfNewStats
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatSolidity,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceStatvIds)

    ####################################################
        vSurfaceStatNames=[' Border Perimeter midline (convexhull)']*vNumberOfNewStats
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatConvexhullPerimeter,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Chord Max length']*vNumberOfNewStats
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatMaxChordLength,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Area2D (contour)']*vNumberOfNewStats
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStat_2D_Area_Contours,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
        ####################################################
        vSurfaceStatNames=[' Area2D (Convexhull)']*vNumberOfNewStats
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStat_2D_Area_CrossSectionalConvexhull,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)

    ####################################################
    ####################################################
    ####################################################
    ####################################################
    vSurfaceStatUnits=['um']*vNumberOfNewStats
    #Create Tuple list for each surface in time
    vSurfaceStatFactors=(['Surface']*vNumberOfNewStats,
                          [str(e) for e in [i+1 for i in vAllTimeIndices]])
    ###############################################
    ####################################################
    vSurfaceStatNames=[' Area 2D #Pixels']*vNumberOfNewStats
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStat_2D_Area_CrossSectionalPixels,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Feret Diameter Max']*vNumberOfNewStats
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatFeretDiameterMax,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Ferret Diameter Max90']*vNumberOfNewStats
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatFeretDiameterMax90,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceIDs)
    #######################################################
    #Intensity of the ring
    if vOptionMeasureIntensity==1:
        zCompleteRingIntensityMean = [[] for _ in range(vSizeC)]
        for index, item in enumerate(zRingIntensityMean):
            zCompleteRingIntensityMean[index % vSizeC].append(item)
        zCompleteRingIntensityMedian = [[] for _ in range(vSizeC)]
        for index, item in enumerate(zRingIntensityMedian):
            zCompleteRingIntensityMedian[index % vSizeC].append(item)
        zCompleteRingIntensityMax = [[] for _ in range(vSizeC)]
        for index, item in enumerate(zRingIntensityMax):
            zCompleteRingIntensityMax[index % vSizeC].append(item)

        for c in range (vSizeC-1):
            vSurfaceStatNames=[' IntensityMean Cell_Border ch' + str(c+1)]*vNumberOfNewStats
            vSurfaces.AddStatistics(vSurfaceStatNames, zCompleteRingIntensityMean[c],
                                          vSurfaceStatUnits, vSurfaceStatFactors,
                                          vSurfaceStatFactorName, vSurfaceIDs)
            vSurfaceStatNames=[' IntensityMedian Cell_Border ch' + str(c+1)]*vNumberOfNewStats
            vSurfaces.AddStatistics(vSurfaceStatNames, zCompleteRingIntensityMedian[c],
                                          vSurfaceStatUnits, vSurfaceStatFactors,
                                          vSurfaceStatFactorName, vSurfaceIDs)
            vSurfaceStatNames=[' IntensityMax Cell_Border ch' + str(c+1)]*vNumberOfNewStats
            vSurfaces.AddStatistics(vSurfaceStatNames, zCompleteRingIntensityMax[c],
                                          vSurfaceStatUnits, vSurfaceStatFactors,
                                          vSurfaceStatFactorName, vSurfaceIDs)
    ###########################################################
    ####################################################
    if  qIsPerimeterFail==True:
        vSurfaceIDs=vSurfaceIDsPerimeterFail
        vSurfaceStatFactors=(['Surface']*vNumberOfNewStatsPerimeterFail,
                              [str(e) for e in [i+1 for i in vAllTimeIndices]])
        vSurfaceStatUnits=['um']*vNumberOfNewStatsPerimeterFail
    ####################################################
    vSurfaceStatNames=[' Border Perimeter midline - Contour vertices']*vNumberOfNewStats
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatPerimeterContourVertices,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Diameter of Equvialent Circle']*vNumberOfNewStats
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatDiameterEquivCircle,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Compactness']*vNumberOfNewStats
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatCompactness,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Convexity']*vNumberOfNewStats
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatConvexity,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Border Perimeter midline (convexhull)']*vNumberOfNewStats
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatConvexhullPerimeter,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Chord Max length']*vNumberOfNewStats
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatMaxChordLength,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Area 2D (contour)']*vNumberOfNewStats
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStat_2D_Area_Contours,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Area 2D - ConvexHull']*vNumberOfNewStats
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStat_2D_Area_CrossSectionalConvexhull,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Circularity']*vNumberOfNewStats
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatCircularity,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Solidity']*vNumberOfNewStats
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatSolidity,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceIDs)

    vSurfaces.SetName(vSurfaces.GetName()+' - 2D Shape Analyzed')
    vImarisApplication.GetSurpassScene().AddChild(vSurfaces, -1)

    if qIsBadSurface==True:
        myError = tk.Tk()
        messagebox.showerror(title='2D shape Analysis ',
                              message='Z voxel scaling is not great\n'
                                  'Some surfaces can not be masked!\n'
                                  'They will not have statistics!')
    #######################################################
        myError.destroy()
