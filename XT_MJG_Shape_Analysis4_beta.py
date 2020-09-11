# 2D shape analysis
#
#Written by Matthew J. Gastinger
#
#Aug 2020 - Imaris 9.6.0

# <CustomTools>
#     <Menu>
#         <Submenu name="Surfaces Functions">
#             <Item name="2D Shape Analysis4 beta" icon="Python3">
#                 <Command>Python3XT::XT_MJG_Shape_Analysis4_beta(%i)</Command>
#             </Item>
#         </Submenu>
#     </Menu>
#     <SurpassTab>
#         <SurpassComponent name="bpSurfaces">
#             <Item name="2D Shape Analysis4 beta" icon="Python3">
#                 <Command>Python3XT::XT_MJG_Shape_Analysis4_beta(%i)</Command>
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

#Definition of New Statistics:
# 1.Perimeter midline
#     1)Measurement of the length of the perimeter of the calculated 2D convexhull
#     2)Measurement of the contour vertices and walking distances between vertices (better)
# 2.2D cross-sectional area (at midline)
#     -Quantification of voxels inside the mask multiplied by size of one pixel
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
# 10. Intensity of the pixel that make up the border around surface at midline
#       (calculated without physically making ring)
#     -IntensityMean
#     -IntensityMedian
#     -IntensityMax
# 10a. Expands the border about 2 pixel outside surface edge ly.
#           Will NOT affect any other morphology measurement.

#NOTE: If Imaris Ring surfaces are not made:
#            FeretDiameterMax = BoundingBoxOOLengthC (for original surface)
#            FeretDiameterMax90 = BoundingBoxOOLengthB (for original surface)

#Dependancies
# SciPy, OpenCV, Shapely



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
from shapely.geometry import LineString


# GUI imports
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import ImarisLib

#aImarisId=0
def XT_MJG_Shape_Analysis4_beta(aImarisId):
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
    var2 = tk.IntVar(value=1)
    var3 = tk.IntVar(value=0)

    tk.Label(window, font="bold", text='Choose the Features').grid(row=0,column=0)
    tk.Checkbutton(window, text='Create midline Perimeter Surface (Longer Processing Time)',
                    variable=var1, onvalue=1, offvalue=0).grid(row=1, column=0, padx=40,sticky=W)
    tk.Checkbutton(window, text='Calculate Border Intensity at midline',
                    variable=var2, onvalue=1, offvalue=0).grid(row=2, column=0, padx=40,sticky=W)
    tk.Checkbutton(window, text='Expand Border',
                    variable=var3, onvalue=1, offvalue=0).grid(row=3, column=0, padx=85,sticky=W)

    btn = Button(window, text="Analyze Surfaces", bg='blue', fg='white', command=ShapeAnalysis_Options)
    btn.grid(column=0, row=4, sticky=W, padx=100)
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

    #Get Surface colorMask stats
    vAllSurfaceStatistics = vSurfaces.GetStatistics()
    vAllSurfaceStatNames = vAllSurfaceStatistics.mNames
    vAllSurfaceStatValues = vAllSurfaceStatistics.mValues
    vAllSurfaceStatIds = vAllSurfaceStatistics.mIds
    vAllSurfaceIndexIntensityMedian=[i for i,val in enumerate(vAllSurfaceStatNames)
                                      if val==('Intensity Median')]
    if len(vAllSurfaceIndexIntensityMedian)>1:
        vAllSurfaceIntensityMedian=list(itemgetter(*vAllSurfaceIndexIntensityMedian)(vAllSurfaceStatValues))
        vAllSurfaceIntensityMedianIds=list(itemgetter(*vAllSurfaceIndexIntensityMedian)(vAllSurfaceStatIds))

    else:
        vAllSurfaceIntensityMedian=[x[1] for x in enumerate(vAllSurfaceStatValues)
                                if x[0] in vAllSurfaceIndexIntensityMedian]
        vAllSurfaceIntensityMedianIds=[x[1] for x in enumerate(vAllSurfaceStatIds)
                                if x[0] in vAllSurfaceIndexIntensityMedian]
    #Grab Last Intensity stats
    zIntensityMedianLastCh=vAllSurfaceIntensityMedian[int((vNumberOfSurfaces*vSizeC)-(vNumberOfSurfaces*vSizeC)/vSizeC):int(((vNumberOfSurfaces*vSizeC)))]
    zIntensityMedianLastChIds=vAllSurfaceIntensityMedianIds[int((vNumberOfSurfaces*vSizeC)-(vNumberOfSurfaces*vSizeC)/vSizeC):int(((vNumberOfSurfaces*vSizeC)))]

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
    vNewStatPerimeter=[]
    vNewStatPerimeterBinaryPixels=[]
    vNewStatPerimeterContourVertices=[]
    vAllTimeIndices=[]
    vNewStatMaxChordLength=[]
    vNewStatDiameterEquivCircle=[]
    vNewStat_2D_Area_CrossSectional=[]
    vNewStat_2D_Area_CrossSectionalConvex=[]
    vNewStatCircularity=[]
    vNewStatCompactness=[]
    vNewStatConvexity=[]
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
            vSlice = zMaskSingleSurface.GetDataSliceFloats(vSurfaceIndexMiddle-1, 0, vAllTimeIndices[vSurfaceIndex]);
        else:
            # vSlice = vImage.GetDataSliceFloats(vSurfaceIndexMiddle,vSizeC-1,vAllTimeIndices[vSurfaceIndex])
            vSlice = zMaskSingleSurface.GetDataSliceFloats(vSurfaceIndexMiddle, 0, vAllTimeIndices[vSurfaceIndex]);
        vSliceNumpy=np.array(vSlice)
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
        # imshow(vFinalMask)


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
        #Compare vSlice and ring slice - find all values in vSlice that are in ring
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

    ###############################################################################
    #Find points on perimeter or boundary
    #Find indexed pixel position in slice
        vPositions=np.where(vVarianceFilterResult > 0)
        vPositionX=(vPositions[0]*aXvoxelSpacing+vDataMin[0]).tolist()
        vPositionY=(vPositions[1]*aYvoxelSpacing+vDataMin[1]).tolist()
        newPositions=np.array([vPositionX,vPositionY])
        newPositions=np.swapaxes(newPositions,0,1)

    ####################################################################################
    ##################################################################################
    ##Find Feret diameter
        vDistanceArray=cdist(newPositions,newPositions)
        vNewStatMaxChordLength.append(np.max(vDistanceArray))
    #Do the convex hull and 2D shape analysis
        hull = ConvexHull(newPositions)
        # plt.plot(newPositions[:,0], newPositions[:,1], 'o')
        # for simplex in hull.simplices:
        #     plt.plot(newPositions[simplex, 0], newPositions[simplex, 1], 'k-')
        vertices = hull.vertices.tolist() + [hull.vertices[0]]
        #Calculate the perimeter from the convex hull vertices
        vNewStatPerimeter.append(float(np.sum([euclidean(x, y) for x, y
                                               in zip(newPositions[vertices],
                                                      newPositions[vertices][1:])])))

    ##########################
    # #  Calculate perimeter from the XY positions from the ring
    #     vSliceNumpy[vSliceNumpy > 0] = 1#if pixel >0 set to 0 numpy solution
    #     vNewStatPerimeterBinaryPixels.append(perimeter(vSliceNumpy, neighbourhood=4)*aXvoxelSpacing)

    #############################################
    ###############################################
    #Calculate contour periemeter
        zVertices=[]
        ret,zThresh = cv2.threshold(vSliceNumpy,0,255,0)
        zThreshBinary=zThresh.astype(np.uint8)
        zContours,zHierarchy = cv2.findContours(zThreshBinary, 1, 2)

        # Grab all through every contours found in the image.
        for cnt in zContours:
            zVertices.append(cnt)
        z=zVertices[0]
        zPerimeterVertices = (z.reshape(-1, z.shape[-1]))*aXvoxelSpacing
        zPerimeterCalc=LineString(zPerimeterVertices)
        vNewStatPerimeterContourVertices.append(zPerimeterCalc.length)

    #############################################
    ###############################################
    #Quantify cross-sectional area by voxel count
        vNewStat_2D_Area_CrossSectional.append(np.count_nonzero(vSlicecropped)*aXvoxelSpacing*aYvoxelSpacing)

    #Find diameter from equivalent circle
        vNewStatDiameterEquivCircle.append(vNewStatPerimeterContourVertices[vSurfaceIndex]/3.1415926)

    #Find 2D area of convex hull
        vNewStat_2D_Area_CrossSectionalConvex.append(hull.volume)

    #Circularity= 4*pi*Area/(P*P) Excludes local irregularities
        vNewStatCircularity.append(4*3.1415926*vNewStat_2D_Area_CrossSectional[vSurfaceIndex]/(vNewStatPerimeter[vSurfaceIndex]**2))

    #Compactness (alternative)
    # Objects which have an elliptical shape, or a boundary that is irregular rather than smooth, will decrease the measure.
        vNewStatCompactness.append(4*3.1415926*vNewStat_2D_Area_CrossSectional[vSurfaceIndex]/(vNewStatPerimeterContourVertices[vSurfaceIndex]**2))

    #Elongation

    #Convexity is the relative amount that an object differs from a convex object
        vNewStatConvexity.append(vNewStatPerimeter[vSurfaceIndex]/vNewStatPerimeterContourVertices[vSurfaceIndex])

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
    #Generate Surface stats
    vNumberOfRings=len(vNewStatPerimeter)
    vSurfaceStatvIds=list(range(len(vNewStatPerimeter)))
    vSurfaceStatUnits=['um']*(len(vNewStatPerimeter))
    ##############
    #Create Tuple list for each surface in time
    vSurfaceStatFactors=(['Surface']*len(vNewStatPerimeter),
                          [str(e) for e in [i+1 for i in vAllTimeIndices]])
    vSurfaceStatFactorName=['Category','Time']
    ####################################################
    if vOptionMakeRings==1:
        vSurfaceStatNames=[' Perimeter2D midline (convexhull)']*(len(vNewStatPerimeter))
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatPerimeter,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        # vSurfaceStatNames=[' Perimeter2D midline - binary pixels']*(len(vNewStatPerimeter))
        # vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatPerimeterBinaryPixels,
        #                               vSurfaceStatUnits, vSurfaceStatFactors,
        #                               vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Perimeter2D midline - Contour vertices']*(len(vNewStatPerimeter))
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatPerimeterContourVertices,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Chord Max Length']*(len(vNewStatPerimeter))
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatMaxChordLength,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Diameter of Equvialent Circle']*(len(vNewStatPerimeter))
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatDiameterEquivCircle,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Feret Diameter Max']*(len(vNewStatPerimeter))
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatFeretDiameterMax,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Ferret Diameter Max90']*(len(vNewStatPerimeter))
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatFeretDiameterMax90,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Area2D']*(len(vNewStatPerimeter))
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStat_2D_Area_CrossSectional,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Compactness']*(len(vNewStatPerimeter))
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatCompactness,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Circularity']*(len(vNewStatPerimeter))
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatCircularity,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
        vSurfaceStatNames=[' Convexity']*(len(vNewStatPerimeter))
        vPerimeterRings.AddStatistics(vSurfaceStatNames, vNewStatConvexity,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ###############################################
    ###############################################
    # if vOptionMakeRings==0:
    #     vAllvSurfacesStatNames = vAllvSurfacesStatistics.mNames
    #     vAllvSurfacesStatValues = vAllvSurfacesStatistics.mValues
    #     vNewStatFeretDiameterMaxIndex=[i for i,val in enumerate(vAllvSurfacesStatNames)
    #                                    if val==('BoundingBoxOO Length C')]
    #     vNewStatFeretDiameterMax90Index=[i for i,val in enumerate(vAllvSurfacesStatNames)
    #                                    if val==('BoundingBoxOO Length B')]
    #     if len(vNewStatFeretDiameterMaxIndex)>1:
    #         vNewStatFeretDiameterMax=list(itemgetter(*vNewStatFeretDiameterMaxIndex)(vAllvSurfacesStatValues))
    #         vNewStatFeretDiameterMax90=list(itemgetter(*vNewStatFeretDiameterMax90Index)(vAllvSurfacesStatValues))
    #     else:
    #         vNewStatFeretDiameterMax=[x[1] for x in enumerate(vAllvSurfacesStatValues)
    #                           if x[0] in vNewStatFeretDiameterMaxIndex]
    #         vNewStatFeretDiameterMax90=[x[1] for x in enumerate(vAllvSurfacesStatValues)
    #                           if x[0] in vNewStatFeretDiameterMax90Index]

    #     vSurfaces.SetName(vSurfaces.GetName()+' - 2D Shape Analyzed')
    #     vImarisApplication.GetSurpassScene().AddChild(vSurfaces, -1)

    ####################################################
    vSurfaceIDs=vSurfaces.GetIds()
    vSurfaceStatNames=[' Perimeter2D midline (convexhull)']*(len(vNewStatPerimeter))
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatPerimeter,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    # vSurfaceStatNames=[' Border Perimeter midline - binary pixels']*(len(vNewStatPerimeter))
    # vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatPerimeterBinaryPixels,
    #                                   vSurfaceStatUnits, vSurfaceStatFactors,
    #                                   vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
    vSurfaceStatNames=[' Perimeter2D midline - Contour vertices']*(len(vNewStatPerimeter))
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatPerimeterContourVertices,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
    vSurfaceStatNames=[' Chord Max Length']*(len(vNewStatPerimeter))
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatMaxChordLength,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Diameter of Equvialent Circle']*(len(vNewStatPerimeter))
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatDiameterEquivCircle,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Area 2D']*(len(vNewStatPerimeter))
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStat_2D_Area_CrossSectional,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Compactness']*(len(vNewStatPerimeter))
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatCompactness,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
    vSurfaceStatNames=[' Circularity']*(len(vNewStatPerimeter))
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatCircularity,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Convexity']*(len(vNewStatPerimeter))
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatConvexity,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceStatvIds)
    ####################################################
    vSurfaceStatNames=[' Feret Diameter Max']*(len(vNewStatPerimeter))
    vSurfaces.AddStatistics(vSurfaceStatNames, vNewStatFeretDiameterMax,
                                      vSurfaceStatUnits, vSurfaceStatFactors,
                                      vSurfaceStatFactorName, vSurfaceIDs)
    ####################################################
    vSurfaceStatNames=[' Ferret Diameter Max90']*(len(vNewStatPerimeter))
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
            vSurfaceStatNames=[' IntensityMean Cell_Border ch' + str(c+1)]*(len(vNewStatPerimeter))
            vSurfaces.AddStatistics(vSurfaceStatNames, zCompleteRingIntensityMean[c],
                                          vSurfaceStatUnits, vSurfaceStatFactors,
                                          vSurfaceStatFactorName, vSurfaceIDs)
            vSurfaceStatNames=[' IntensityMedian Cell_Border ch' + str(c+1)]*(len(vNewStatPerimeter))
            vSurfaces.AddStatistics(vSurfaceStatNames, zCompleteRingIntensityMedian[c],
                                          vSurfaceStatUnits, vSurfaceStatFactors,
                                          vSurfaceStatFactorName, vSurfaceIDs)
            vSurfaceStatNames=[' IntensityMax Cell_Border ch' + str(c+1)]*(len(vNewStatPerimeter))
            vSurfaces.AddStatistics(vSurfaceStatNames, zCompleteRingIntensityMax[c],
                                          vSurfaceStatUnits, vSurfaceStatFactors,
                                          vSurfaceStatFactorName, vSurfaceIDs)
    vSurfaces.SetName(vSurfaces.GetName()+' - 2D Shape Analyzed')
    vImarisApplication.GetSurpassScene().AddChild(vSurfaces, -1)

    #######################################################
