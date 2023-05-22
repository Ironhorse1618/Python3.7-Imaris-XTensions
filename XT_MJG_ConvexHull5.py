#Convex Hull

    #<CustomTools>
        #<Menu>
            #<Submenu name="Filaments Functions">
                #<Item name="ConvexHull5 - Python" icon="Python3">
                    #<Command>Python3XT::XT_MJG_ConvexHull5(%i)</Command>
                #</Item>
            #</Submenu>
            #<Submenu name="Surfaces Functions">
                #<Item name="ConvexHull5 - Python" icon="Python3">
                    #<Command>Python3XT::XT_MJG_ConvexHull5(%i)</Command>
                #</Item>
            #</Submenu>       #</Menu>
       #<SurpassTab>
           #<SurpassComponent name="bpFilaments">
               #<Item name="ConvexHull5 - Python" icon="Python3">
                   #<Command>Python3XT::XT_MJG_ConvexHull5(%i)</Command>
               #</SurpassComponent>
           #</SurpassTab>
        #<SurpassTab>
            #<SurpassComponent name="bpSurfaces">
                #<Item name="ConvexHull5 - Python" icon="Python3">
                    #<Command>Python3XT::XT_MJG_ConvexHull5(%i)</Command>
                #</SurpassComponent>
            #</SurpassTab>
    #</CustomTools>


#Description
#Convex hul calculatioon for the Filament Points, Filament Terminal Points

#Convexhull created from surface mask



import ImarisLib

from scipy.spatial import Delaunay
from scipy.spatial import ConvexHull

import numpy as np
import time
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import math
import platform

aImarisId=0
def XT_MJG_ConvexHull5(aImarisId):
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

    vSurpassObject = vImarisApplication.GetSurpassSelection()
    qIsSurface = vImarisApplication.GetFactory().IsSurfaces(vSurpassObject)
    qIsSpot = vImarisApplication.GetFactory().IsSpots(vSurpassObject)
    qIsFilament = vImarisApplication.GetFactory().IsFilaments(vSurpassObject)


    if qIsFilament == True:
        #Get the Current Filament Object
        vSurpassObject = vFactory.ToFilaments(vImarisApplication.GetSurpassSelection())
        vNumberOfFilaments=vSurpassObject.GetNumberOfFilaments()
        vFilamentIds= vSurpassObject.GetIds()
        vFilamentIdsSelected = vSurpassObject.GetSelectedIds()

        zEmptyfilaments=[]
        for aFilamentIndex in range(vNumberOfFilaments):
            vSurpassObjectRadius = vSurpassObject.GetRadii(aFilamentIndex)
            if len(vSurpassObjectRadius)==1:
                zEmptyfilaments.append(int(aFilamentIndex))
        vFilamentIds=[v for i,v in enumerate(vFilamentIds) if i not in zEmptyfilaments]

    ##################################################################
    ##################################################################
    qInputBox=Tk()
    qInputBox.title("Convex Hull Creation")
    qInputBox.geometry("250x85")
    qInputBox.attributes("-topmost", True)

    ##################################################################
    # Set Input Window to center of screen
    # Gets the requested values of the height and widht.
    windowWidth = qInputBox.winfo_reqwidth()
    windowHeight = qInputBox.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(qInputBox.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(qInputBox.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    qInputBox.geometry("+{}+{}".format(positionRight, positionDown))
    ##################################################################
    def ConvexHullCreate():
        global qOptionConvexHullTerminal
        qOptionConvexHullTerminal = var1.get()
        qInputBox.destroy()

    var1 = tk.IntVar(value = 0)
    tk.Label(qInputBox, text=' ').grid(row=1, column=0)

    qWhatOS = platform.system()
    if qWhatOS == 'Darwin':
        Single=Button(qInputBox, text="Create ConvexHull Surfaces",command=ConvexHullCreate )
    else:
        Single=Button(qInputBox, text="Create ConvexHull Surfaces", bg='blue', fg='white',command=ConvexHullCreate )


    Single.grid(row=2, column=0,padx=40,sticky=W)
    tk.Checkbutton(qInputBox, text='Use Terminal Points',
                   variable=var1, onvalue=1, offvalue=0).grid(row=3, column=0, padx=50,sticky=W)

    qInputBox.mainloop()

    ##################################################################
    ##################################################################
    #Create the Progress bars
    #Creating a separate Tkinter qProgressBar for progress bars
    qProgressBar=tk.Tk()
    qProgressBar.title("ConvexHull")

    # Create a progressbar widget
    progress_bar1 = ttk.Progressbar(qProgressBar, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    progress_bar2 = ttk.Progressbar(qProgressBar, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    # And a label for it
    label_1 = tk.Label(qProgressBar, text="ConvexHull")
    label_2 = tk.Label(qProgressBar, text="Working...")

    # Use the grid manager
    label_1.grid(row=0, column=0,pady=10)
    label_2.grid(row=1, column=0,pady=10)

    progress_bar1.grid(row=0, column=1)
    progress_bar2.grid(row=1, column=1)

    ##################################################################
    # Set Input Window to center of screen
    # Gets the requested values of the height and widht.
    windowWidth = qProgressBar.winfo_reqwidth()
    windowHeight = qProgressBar.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(qProgressBar.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(qProgressBar.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    qProgressBar.geometry("+{}+{}".format(positionRight, positionDown))
    ##################################################################
    qProgressBar.geometry('230x80')
    qProgressBar.attributes("-topmost", True)

    # Necessary, as the qProgressBar object needs to draw the progressbar widget
    # Otherwise, it will not be visible on the screen
    qProgressBar.update_idletasks()
    progress_bar1['value'] = 0
    progress_bar2['value'] = 0
    qProgressBar.update()

    start = time.time()

    ##################################################################
    ##################################################################
    #Get Image properties
    vDataMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vDataMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vDataSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    vType = vImage.GetType()

    aXvoxelSpacing= (vDataMax[0]-vDataMin[0])/vDataSize[0]
    aYvoxelSpacing= (vDataMax[1]-vDataMin[1])/vDataSize[1]
    aZvoxelSpacing = round((vDataMax[2]-vDataMin[2])/vDataSize[2],3)
    vSmoothingFactor=aXvoxelSpacing*2


    vSurfaceHull = vFactory.CreateSurfaces()
    vSurfaceConvexHull = vImarisApplication.GetFactory().CreateDataContainer()
    vSurfaceConvexHull.SetName(' Dendritic Field Analysis - '+ str(vSurpassObject.GetName()))

    ###############################################################################
    def AddMaskToDataSet(vSliceMask):
        global DataSet,vIndexZ
        #Add slice to dataset
        #whole volume
        vDataSet.SetDataSubVolumeAs1DArrayFloats(vSliceMask.tolist(),
                                        0,
                                        0,
                                        vIndexZ,
                                        0,
                                        0,
                                        vDataSize[0],
                                        vDataSize[1],
                                        1)
    ###############################################################################

    wNewStatConvexHullVolumePerFilament = []
    wNewStatConvexHullAreaPerFilament = []

    startALL = time.time()
    ###############################################################################
    ###############################################################################
    if qIsFilament == True:

        zEmptyfilaments=[]
        for aFilamentIndex in range(vNumberOfFilaments):
            vFilamentsRadius = vSurpassObject.GetRadii(aFilamentIndex)
            if len(vFilamentsRadius)==1:
                zEmptyfilaments.append(int(aFilamentIndex))
        vFilamentIds=[v for i,v in enumerate(vFilamentIds) if i not in zEmptyfilaments]

        #Loop each Filament
        vFilamentCountActual=0
        for aFilamentIndex in range(vNumberOfFilaments):

            #Test if the time point has empty filament matrix or filament start
            #point and nothing more
            if len(vFilamentsRadius)==1:
                continue
            vFilamentCountActual=vFilamentCountActual+1

            vSurpassObjectIndexT = vSurpassObject.GetTimeIndex(aFilamentIndex)
            vSurpassObjectXYZ = vSurpassObject.GetPositionsXYZ(aFilamentIndex)
            vSurpassObjectRadius = vSurpassObject.GetRadii(aFilamentIndex)

            ###############################################################################
            #Easier way to identify branch point and terminal points per filament object

            vStatPtPositionXSet = vSurpassObject.GetStatisticsByName('Pt Position X')
            vStatPtPositionYSet = vSurpassObject.GetStatisticsByName('Pt Position Y')
            vStatPtPositionZSet = vSurpassObject.GetStatisticsByName('Pt Position Z')
            vStatPtPosition = []
            vStatPtPosition.append(vStatPtPositionXSet.mValues)
            vStatPtPosition.append(vStatPtPositionYSet.mValues)
            vStatPtPosition.append(vStatPtPositionZSet.mValues)

            vStatPtPositionFactors = vStatPtPositionXSet.mFactors
            vStatPtPositionIds =  vStatPtPositionXSet.mIds

            wFilamentTerminalPointsNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[4]=='Segment Terminal')[0].tolist()]
            wFilamentBranchPointsNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[4]=='Segment Branch')[0].tolist()]
            wFilamentStartingPointsNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[4]=='Segment Beginning')[0].tolist()]

            if not wFilamentTerminalPointsNEW.any():# == []:
                wFilamentTerminalPointsNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[4]=='Dendrite Terminal')[0].tolist()]
                wFilamentBranchPointsNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[4]=='Dendrite Branch')[0].tolist()]
                wFilamentStartingPointsNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[4]=='Dendrite Beginning')[0].tolist()]

        #Find in Branch, Terminal and starting point - in current filament
            wFilamentBranchPointsNEWCurrent = np.array(wFilamentBranchPointsNEW)[np.where(np.isin(wFilamentBranchPointsNEW[:,0],np.array(vSurpassObjectXYZ)[:,0]))[0].tolist()]
            wFilamentTerminalPointsNEWCurrent = np.array(wFilamentTerminalPointsNEW)[np.where(np.isin(wFilamentTerminalPointsNEW[:,0],np.array(vSurpassObjectXYZ)[:,0]))[0].tolist()]
            wFilamentStartingPointsNEWCurrent = np.array(wFilamentStartingPointsNEW)[np.where(np.isin(wFilamentStartingPointsNEW[:,0],np.array(vSurpassObjectXYZ)[:,0]))[0].tolist()]

        #choose Terminal points or ALL points
            if qOptionConvexHullTerminal == 1:
                vFilamentXYZPointsConvexHullPixelPos = np.copy(wFilamentTerminalPointsNEWCurrent)
                vFilamentXYZPointsConvexHullPixelPos = np.vstack([vFilamentXYZPointsConvexHullPixelPos, wFilamentStartingPointsNEWCurrent])
                vFilamentsXYZArray = np.array(vFilamentXYZPointsConvexHullPixelPos)
            else:
                vFilamentsXYZArray = np.array(vSurpassObjectXYZ)
                vFilamentXYZPointsConvexHullPixelPos = np.copy(vFilamentsXYZArray)
        #Calculate Convexhull and Delauney 2d and 3D
        #convert xyz position into closest pixel coordinates
            wConversionX = (vDataMax[0]-vDataMin[0])/vDataSize[0]
            wConversionY = (vDataMax[1]-vDataMin[1])/vDataSize[1]
            wConversionZ = (vDataMax[2]-vDataMin[2])/vDataSize[2]

            vFilamentXYZPointsConvexHullPixelPos[:,0] = (vFilamentXYZPointsConvexHullPixelPos[:,0]-vDataMin[0])/wConversionX
            vFilamentXYZPointsConvexHullPixelPos[:,1] = (vFilamentXYZPointsConvexHullPixelPos[:,1]-vDataMin[1])/wConversionY
            vFilamentXYZPointsConvexHullPixelPos[:,2] = (vFilamentXYZPointsConvexHullPixelPos[:,2]-vDataMin[2])/wConversionZ
            vFilamentXYZPointsConvexHullPixelPos = vFilamentXYZPointsConvexHullPixelPos.astype(int)

            vFilamentXYZPointsConvexHullPixelPos[:,0][np.where(vFilamentXYZPointsConvexHullPixelPos[:,0] == vDataSize[0])[0]]=vDataSize[0]-1
            vFilamentXYZPointsConvexHullPixelPos[:,1][np.where(vFilamentXYZPointsConvexHullPixelPos[:,1] == vDataSize[1])[0]]=vDataSize[1]-1
            # vFilamentXYZPointsConvexHullPixelPos[:,2][np.where(vFilamentXYZPointsConvexHullPixelPos[:,2] == vDataSize[2])[0]]=vDataSize[2]-1

        #for stat calculation
            if len(set(wFilamentTerminalPointsNEWCurrent[:,2])) == 1:
            #Remove Z-position for stat calcualtion
                vSurpassObjectXYZArray2D = np.delete(vFilamentsXYZArray,2,1)
                wFilamentConvexHullCurrentStat = ConvexHull(vSurpassObjectXYZArray2D)
            #Remove Z position coordinate for pixels
                vFilamentXYZPointsCurrentPixelPos2D = np.delete(vFilamentXYZPointsConvexHullPixelPos,2,1)
                wFilamentConvexHullCurrent = ConvexHull(vFilamentXYZPointsCurrentPixelPos2D)
                wFilamentConvexHullDelaunyCurrent = Delaunay(vFilamentXYZPointsCurrentPixelPos2D[wFilamentConvexHullCurrent.vertices])
            else:
                wFilamentConvexHullCurrentStat = ConvexHull(vFilamentsXYZArray)

        #Calculate Dendritic Field Size (2D and 3D) and surface area...from ConvexHull
            wNewStatConvexHullVolumePerFilament.append(wFilamentConvexHullCurrentStat.volume)
            wNewStatConvexHullAreaPerFilament.append(wFilamentConvexHullCurrentStat.area)

          # #create new Dataset full volume
            vDataSet = vImarisApplication.GetFactory().CreateDataSet()
            vDataSet.Create(vType, vDataSize[0], vDataSize[1], vDataSize[2], 1, 1)
            vDataSet.SetExtendMinX(vDataMin[0])
            vDataSet.SetExtendMinY(vDataMin[1])
            vDataSet.SetExtendMinZ(vDataMin[2])
            vDataSet.SetExtendMaxX(vDataMax[0])
            vDataSet.SetExtendMaxY(vDataMax[1])
            vDataSet.SetExtendMaxZ(vDataMax[2])
            vFilamentTimepoint = vImage.GetTimePoint(vSurpassObjectIndexT)
            vDataSet.SetTimePoint(vSurpassObjectIndexT, vFilamentTimepoint)

          #Create Convex hull mask and generate surface
            if vDataSize[2] == 1:
                #for 2D whole image
                idx = np.stack(np.indices([vDataSize[0],vDataSize[1]]), axis = -1)
                out_idx = np.nonzero(wFilamentConvexHullDelaunyCurrent.find_simplex(idx) + 1)
                vSlice = np.zeros([vDataSize[0],vDataSize[1]])
                vSlice[out_idx] = 1
                #convert to single column per slice for import into Channel
                vSlice = vSlice.flatten('F')
                vIndexZ=0
                #Add mask to DataSet
                AddMaskToDataSet(vSlice)
            else:
                #create tuple and flip so that Z is first column, follow by x ,then Y
                points = tuple((vFilamentXYZPointsConvexHullPixelPos[:,2],
                               vFilamentXYZPointsConvexHullPixelPos[:,0],
                               vFilamentXYZPointsConvexHullPixelPos[:,1]))
                image = np.zeros((vDataSize[2],vDataSize[0],vDataSize[1]))

                #Replace Points in blank image for ConvexHull calculation
                image[points] = 1

                #Find Indices in volume where value is >1
                points = np.transpose(np.where(image))
                #Process COnvex hull and Delauney
                hull = ConvexHull(points)
                deln = Delaunay(points[hull.vertices])
                vVolume = np.zeros((vDataSize[2],vDataSize[0],vDataSize[1]))
                #for 3D whole image
                idx = np.stack(np.indices(vVolume.shape), axis = -1)
                out_idx = np.nonzero(deln.find_simplex(idx) + 1)
                #Set value=1 for pixels inside Convexhull
                vVolume[out_idx] = 1

                progress_bar1['value'] = int((aFilamentIndex+.5)/vNumberOfFilaments*100) #  % out of 100
                qProgressBar.update()

                #loop each Z and creat Convexhull mask channel
                for vIndexZ in range (vDataSize[2]):
                    vSlice = vVolume[vIndexZ].flatten('F')
                    #Use function to Add mask to DataSet
                    AddMaskToDataSet(vSlice)

          #make surface convex hull
            ip = vImarisApplication.GetImageProcessing()
            vConvexHull = ip.DetectSurfaces(vDataSet, [],
                                      0,
                                      vSmoothingFactor,
                                      0,
                                      True,
                                      55,
                                      '')
        #copy surface to sceneobject named vSurfaceHull
            vConvexHull.CopySurfacesToSurfaces([0], vSurfaceHull)

            progress_bar1['value'] = int((aFilamentIndex+1)/vNumberOfFilaments*100) #  % out of 100
            qProgressBar.update()
    ###############################################################################
    if qIsSurface == True:
        vSurpassObject = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
        vSurfaceIds = vSurpassObject.GetIds()
        vNumberOfSurfaces = vSurpassObject.GetNumberOfSurfaces()

        for vSurfaceIndex in range (vNumberOfSurfaces):
            vSurpassObjectIndexT = vSurpassObject.GetTimeIndex(vSurfaceIndex)

            vDataSet = vImarisApplication.GetFactory().CreateDataSet()
            vDataSet.Create(vType, vDataSize[0], vDataSize[1], vDataSize[2], 1, 1)
            vDataSet.SetExtendMinX(vDataMin[0])
            vDataSet.SetExtendMinY(vDataMin[1])
            vDataSet.SetExtendMinZ(vDataMin[2])
            vDataSet.SetExtendMaxX(vDataMax[0])
            vDataSet.SetExtendMaxY(vDataMax[1])
            vDataSet.SetExtendMaxZ(vDataMax[2])
            vObjectTimepoint = vImage.GetTimePoint(vSurpassObjectIndexT)
            vDataSet.SetTimePoint(vSurpassObjectIndexT, vObjectTimepoint)

            zMaskSingleSurface = vSurpassObject.GetSingleMask(vSurfaceIndex,
                                                 vDataMin[0],
                                                 vDataMin[1],
                                                 vDataMin[2],
                                                 vDataMax[0],
                                                 vDataMax[1],
                                                 vDataMax[2],
                                                 vDataSize[0],
                                                 vDataSize[1],
                                                 vDataSize[2])

            if vDataSize[2] == 1:#For 2D surface object
                image = np.zeros((vDataSize[0],vDataSize[1]))
                vSlice = np.array(zMaskSingleSurface.GetDataSliceShorts(0,0,vSurpassObjectIndexT))
                idx = np.where(vSlice)
                zTest = np.array([0]*len(idx[0]))
                # points =tuple((zTest,idx[0],idx[1]))
                image[idx]=1
               #Find Indices in volume where value is >1
                points = np.transpose(np.where(image))
                wSurfaceConvexHullCurrent = ConvexHull(points)
                wSurfaceConvexHullDelaunyCurrent = Delaunay(points[wSurfaceConvexHullCurrent.vertices])
                #for 2D whole image
                idx = np.stack(np.indices([vDataSize[0],vDataSize[1]]), axis = -1)
                out_idx = np.nonzero(wSurfaceConvexHullDelaunyCurrent.find_simplex(idx) + 1)
                vSlice = np.zeros([vDataSize[0],vDataSize[1]])
                vSlice[out_idx] = 1
                #convert to single column per slice for import into Channel
                vSlice = vSlice.flatten('F')
                vIndexZ=0
                #Add mask to DataSet
                AddMaskToDataSet(vSlice)
            else:#For 3D surface object
                image = np.zeros((vDataSize[2],vDataSize[0],vDataSize[1]))
                for vIndexZ in range (0,vDataSize[2]):
                        vSlice = np.array(zMaskSingleSurface.GetDataSliceShorts(vIndexZ,0,vSurpassObjectIndexT))
                        idx = np.where(vSlice)
                        if any (idx[0]):
                            zTest = np.array([vIndexZ]*len(idx[0]))
                            points =tuple((zTest,idx[0],idx[1]))
                            image[points]=1
                        else:
                            progress_bar2['value'] = ((vIndexZ+1)/vDataSize[2]*100) #  % out of 100
                            qProgressBar.update()
                            continue
                        progress_bar2['value'] = ((vIndexZ+1)/vDataSize[2]*100) #  % out of 100
                        qProgressBar.update()


                #Find Indices in volume where value is >1
                points = np.transpose(np.where(image))

                #Randomly remove % of points....
                test_index = np.random.choice(range(len(points)), math.floor(len(points)/25))
                points=points[test_index]

                start = time.time()

                progress_bar1['value'] = int((vSurfaceIndex+.5)/vNumberOfSurfaces*100) #  % out of 100
                qProgressBar.update()


                #Process COnvex hull and Delauney
                hull = ConvexHull(points)
                deln = Delaunay(points[hull.vertices])
                vVolume = np.zeros((vDataSize[2],vDataSize[0],vDataSize[1]))
                #for 3D whole image
                idx = np.stack(np.indices(vVolume.shape), axis = -1)
                out_idx = np.nonzero(deln.find_simplex(idx) + 1)
                #Set value=1 for pixels inside Convexhull
                vVolume[out_idx] = 1

                #loop each Z and creat Convexhull mask channel
                for vIndexZ in range (vDataSize[2]):
                    vSlice = vVolume[vIndexZ].flatten('F')
                    #Use function to Add mask to DataSet
                    AddMaskToDataSet(vSlice)
                    progress_bar2['value'] = int((vIndexZ+1)/vDataSize[2]*100) #  % out of 100
                    qProgressBar.update()

                elapsed = time.time() - start
                print(elapsed)

          #make surface convex hull
            ip = vImarisApplication.GetImageProcessing()
            vConvexHull = ip.DetectSurfaces(vDataSet, [],
                                      0,
                                      vSmoothingFactor,
                                      0,
                                      True,
                                      55,
                                      '')
        #copy surface to sceneobject named vSurfaceHull
            vConvexHull.CopySurfacesToSurfaces([0], vSurfaceHull)


            progress_bar1['value'] = int((vSurfaceIndex+1)/vNumberOfSurfaces*100) #  % out of 100
            qProgressBar.update()
    #Add Convex Hull surfaces
    vSurfaceHull.SetName('Filament ConvexHull Surfaces')
    vSurfaceHull.SetColorRGBA(vSurpassObject.GetColorRGBA())
    # #Add new surface convex hull folder
    vSurfaceConvexHull.AddChild(vSurfaceHull, -1)
    vImarisApplication.GetSurpassScene().AddChild(vSurfaceConvexHull, -1)

    ###############################################################################
    ###############################################################################
    #Add Surface labels with FilamentID as name

    if qIsFilament == True:
        #Create Labels for Convex hull surfaces to match filament ID
        vLabelIndices=list(range(vFilamentCountActual))
        wLabelList=[]
        for j in range (len(vLabelIndices)):
            vLabelCreate = vFactory.CreateObjectLabel(vLabelIndices[j],
                                                      'FilamentIds',
                                                      str(vFilamentIds[j]))
            wLabelList.append(vLabelCreate)
        vSurfaceHull.SetLabels(wLabelList)
    if qIsSurface==True:
        #Create Labels for Convex hull surfaces to match filament ID
        vLabelIndices=list(range(vNumberOfSurfaces))
        wLabelList=[]
        for j in range (len(vLabelIndices)):
            vLabelCreate = vFactory.CreateObjectLabel(vLabelIndices[j],
                                                      'ConvexHull Surfaces',
                                                      str(vSurfaceIds[j]))
            wLabelList.append(vLabelCreate)
        vSurfaceHull.SetLabels(wLabelList)
        #Add labels to the original surface
        vLabelIndices=vSurfaceIds
        wLabelList=[]
        for j in range (len(vLabelIndices)):
            vLabelCreate = vFactory.CreateObjectLabel(vLabelIndices[j],
                                                      'ConvexHull Surfaces',
                                                      str(vSurfaceIds[j]))
            wLabelList.append(vLabelCreate)
        vSurpassObject.SetLabels(wLabelList)


    elapsedALL = time.time() - startALL
    print('Total Time--' + str(elapsedALL))

    qProgressBar.destroy()
    qProgressBar.mainloop()