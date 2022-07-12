# Filament Analysis
#
# Written by Matthew J. Gastinger
#
# June 2022 - Imaris 9.9.1
#
# ---  Updates:
#   1. Adding a new feature to segment dendrites within each Sholl sphere
#   2. Improving the multi-Filament functionality
#
#
    #<CustomTools>
        #<Menu>
            #<Submenu name="Filaments Functions">
                #<Item name="Filament Sholl Analysis10" icon="Python3">
                    #<Command>Python3XT::XT_MJG_Filament_ShollAnalysis10(%i)</Command>
                #</Item>
            #</Submenu>
       #</Menu>
       #<SurpassTab>
           #<SurpassComponent name="bpFilaments">
               #<Item name="Filament Sholl Analysis10" icon="Python3">
                   #<Command>Python3XT::XT_MJG_Filament_ShollAnalysis10(%i)</Command>
               #</SurpassComponent>
           #</SurpassTab>
    #</CustomTools>


# Description:
#
# Finds and displays Sholl intersections for each Filament that has been traced
# and contains a Starting Point.  Works for both single and multiple filaments.
# Sholl sphere radius is defined by the user.  Each dendrite segments is
# quantified that crosses these intervals at least once.


# RESULTS:
# 1.	 Advanced Sholl Analysis
#         - A Group folder is generated.
#         - Each valid filament will generate a Spots object (named using original FilamentID)
#             and is set with a custom label for each Sholl Radius.
#     ---Overall Statistics Tab
#         i.   Critical Radius (um)
#                 ---Sholl distance with the maximum number of intersections from the defined Sholl intervals
#         ii.  Max # Intersections
#                 ---Maximum Number of Intersections at the Critical Radius
#         iii. Critical Radius HighRes (um)
#                 ---Sholl distance with the maximum number of intersections using 1um Sholl Radius
#         iv.  Max # Intersections HighRes
#                 ---Maximum Number of Intersections at the Critical Radius HighRes
#         v.   Dendrite Length Sum
#                 ---Cumulative Sum of all dendrite segments that fall within the
#                     boundaries of the Sholl Spheres (i.e. 10 um Sholl Ring
#                     quantifies dendrites between 0 and 10 um from Starting Point

#     ---Detailed Statistics Tab
#         i. Shortest Distance to Starting Point
#                 ---Measures the distance of the Sholl Intersection point to the starting point along the dendrite path
#                         ---Smaller values are closer to the soma
#         ii. Ratio ShollDistance to Distance to Starting Point
#                 ---Values close to “1” correlate highly to Sholl Radius distance
#                 ---Values far from “1” likely possess a non-direct line to soma

# 2.	Sholl Dendrites
#         -A new filament is created that splits the filament object at each Sholl intersection.
#             This is primarily used for visualization purposes.
#             ---Each Dendrite is classified and visualized using a
#                 statistics-coded custom statistic for “Sholl Sphere”

# This is not an exact replica of the Sholl intersections reported by the
# Filament object (built into Imaris).  The values are very similar, but the rules
# for identifying a single intersection differ slightly, especially
# around where a branch point intersects a Sholl sphere. (See Readme.doc of
# an report of comparison)

import numpy as np
import time
import random
from numpy import array
import platform

# GUI imports
# GUI imports
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog

import matplotlib.pyplot as plt
from scipy import stats
from scipy.signal import find_peaks
from scipy.signal import peak_widths
from scipy.spatial.distance import cdist
from scipy.spatial.distance import pdist
from operator import add
from operator import itemgetter
import operator
import itertools
from statistics import mean
from functools import reduce
import collections

import ImarisLib

aImarisId=0
def XT_MJG_Filament_ShollAnalysis10(aImarisId):
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

    # vSurfaces = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
    # vSpots = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
    vFilaments = vFactory.ToFilaments(vImarisApplication.GetSurpassSelection())

    #Create a new folder object for new Sholl Spot intersections
    vNew_Spots = vImarisApplication.GetFactory()
    result2 = vNew_Spots.CreateDataContainer()
    result2.SetName('Sholl Intersections - ' + str(vFilaments.GetName))

    # vFilaments.SetVisible(0)

    ##################################################################
    ##################################################################
    def ShollInput ():
        global vShollRadius,qSplitShollspheres
        qSplitShollspheres=var1.get()
        vShollRadius=Entry1.get()
        # vMaxShollSphere=Entry2.get()
        vShollRadius=int(vShollRadius)
        # vMaxShollSphere=int(vMaxShollSphere)
        qInputBox.destroy()

    qInputBox=Tk()
    qInputBox.title("Sholl Analysis")
    qInputBox.geometry("250x115")
    var1 = tk.IntVar(value=0)

    # qInputBoxTitle = Label(qInputBox, text = "Sholl Analysis")
    # qInputBoxTitle.pack()
    Label(qInputBox,text="Sholl Sphere Radius (um):").grid(row=0, column=0)
    # Label(qInputBox,text="Maxiumum Sholl Sphere (um)").grid(row=1, column=0)
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
    Entry1=Entry(qInputBox,justify='center',width=7)
    Entry1.grid(row=0, column=1)
    Entry1.insert(0, 20)

    # Entry2=Entry(qInputBox,justify='center',width=10)
    # Entry2.grid(row=1, column=1)
    # Entry2.insert(0, 200)

    tk.Checkbutton(qInputBox, text='Create Spots Objects \n'
                   'per Sholl sphere',
                   variable=var1, onvalue=1, offvalue=0).grid(row=2, column=0)
    tk.Label(qInputBox, text='').grid(row=3, column=0)
    qWhatOS=platform.system()
    if qWhatOS='Darwin'
        Single=Button(qInputBox, fg="black", text="Process Sholl Analysis",command=ShollInput )
    else:
        Single=Button(qInputBox, bg="blue", fg="white", text="Process Sholl Analysis",command=ShollInput )
    Single.grid(row=4, column=0, sticky=E)


    qInputBox.mainloop()
    ##################################################################
    ##################################################################
    #Create the Progress bars
    #Creating a separate Tkinter qProgressBar for progress bars
    qProgressBar=tk.Tk()
    qProgressBar.title("Sholl Analysis")

    # Create a progressbar widget
    progress_bar1 = ttk.Progressbar(qProgressBar, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    progress_bar2 = ttk.Progressbar(qProgressBar, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    # And a label for it
    label_1 = tk.Label(qProgressBar, text="Dendrite ReOrder")
    label_2 = tk.Label(qProgressBar, text="Filament Progress")

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
    qProgressBar.geometry('250x100')
    qProgressBar.attributes("-topmost", True)

    # Necessary, as the qProgressBar object needs to draw the progressbar widget
    # Otherwise, it will not be visible on the screen
    qProgressBar.update_idletasks()
    progress_bar1['value'] = 0
    qProgressBar.update_idletasks()

    # start = time.time()

    ##################################################################
    ##################################################################
    #Get Image properties
    vDataMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vDataMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vDataSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    aXvoxelSpacing= (vDataMax[0]-vDataMin[0])/vDataSize[0]
    aYvoxelSpacing= (vDataMax[1]-vDataMin[1])/vDataSize[1]
    aZvoxelSpacing = round((vDataMax[2]-vDataMin[2])/vDataSize[2],3)
    vSmoothingFactor=aXvoxelSpacing*2

    #Get the Current Filament Object
    vNumberOfFilaments=vFilaments.GetNumberOfFilaments()
    vFilamentIds= vFilaments.GetIds()

    ################################################
    ################################################
    #Create a new folder object for new Sholl Spot intersections
    # vGroupFolder_ShollSpots = vImarisApplication().GetFactory()
    vShollResult = vImarisApplication.GetFactory().CreateDataContainer()
    vShollResult.SetName('Sholl Intersections per sphere - '+ str(vFilaments.GetName()))

    vShollDendrites = vImarisApplication.GetFactory().CreateDataContainer()
    vShollDendrites.SetName('Sholl Dendrites - '+ str(vFilaments.GetName()))

    vShollResult2 = vImarisApplication.GetFactory().CreateDataContainer()
    vShollResult2.SetName(' Advanced Sholl Analysis - '+ str(vFilaments.GetName()))

    ################################################
    ################################################
    vSegmentBranchLength=[]
    wSegmentIdsSpine=[]
    wSegmentIdsDendrite=[]
    wSegmentIdsALL=[]

    vSpotPositionAllShollSpheresALL= []
    vSpotPositionAllShollSpheresPerFilamentALL = []
    vNumberofShollIntersectionsALL = []
    vNewStatSpotShollDistanceALL = []

    vSpotPositionAllShollSpheres=[]
    vFilamentCountActual=0
    vSpotPositionAllShollSpheresPerFilament=[]
    vNumberofShollIntersections=[]
    vNewStatSpotShollDistance=[]
    vNewStatNumberShollIntersectionPerFilament=[]
    vNewStatSpotNumberShollIntersections=[]
    vNumberofIntersectionsPerShollSphere=[]
    wCompleteShollSpotDistAlongFilamentStat=[]
    vNumberOfShollIntersectionPerSpherePerFilament=[]
    ###############################################################################
    ###############################################################################
    zEmptyfilaments=[]
    for aFilamentIndex in range(vNumberOfFilaments):
        vFilamentsRadius = vFilaments.GetRadii(aFilamentIndex)
        if len(vFilamentsRadius)==1:
            zEmptyfilaments.append(int(aFilamentIndex))
    vFilamentIds=[v for i,v in enumerate(vFilamentIds) if i not in zEmptyfilaments]
    ###############################################################################
    ###############################################################################
    #Loop each Filament
    for aFilamentIndex in range(vNumberOfFilaments):
        vFilamentsIndexT = vFilaments.GetTimeIndex(aFilamentIndex)
        vFilamentsXYZ = vFilaments.GetPositionsXYZ(aFilamentIndex)
        vFilamentsRadius = vFilaments.GetRadii(aFilamentIndex)

    #Test if the time point has empty filament matrix or filament start
    #point and nothing more
        if len(vFilamentsRadius)==1:
            continue
        vFilamentCountActual=vFilamentCountActual+1
        vFilamentsEdgesSegmentId = vFilaments.GetEdgesSegmentId(aFilamentIndex)
    #Find unique values of variable using set, the copnvert back to list
        vSegmentIds=list(set(vFilamentsEdgesSegmentId))
        vNumberOfDendriteBranches = len(vSegmentIds)#total number dendrite segments
        vNumberOfFilamentPoints= len(vFilamentsRadius)#including starting point
        vFilamentTimeIndex=[vFilamentsIndexT]*len(vFilamentsRadius)#for filament spot creation
        vFilamentsEdges = vFilaments.GetEdges(aFilamentIndex)
        vTypes = vFilaments.GetTypes(aFilamentIndex)
        vBeginningVertex = vFilaments.GetBeginningVertexIndex(aFilamentIndex)
        #Test whether filament has a starting point
        if vBeginningVertex==[]:
            continue
        else:
            vBeginningVertexPositionXYZ=vFilamentsXYZ[vBeginningVertex]
        SegmentCountALL=0
        vBranchIndex=0

        #create new FilamentXYZ for dendrite spilting
        zNewFilamentsXYZ = vFilamentsXYZ[:]
        zNewFilamentsRadius = vFilamentsRadius[:]
        zNewFilamentsEdges = np.array(vFilamentsEdges[:])
        zNewFilamentsTypes = vTypes[:]

    ###############################################################################
    ###############################################################################
    #Find Starting point and terminal point indices
    # Efficient Python program to print all non-
    # repeating elements.
        def firstNonRepeating(arr, n):
            global wFilamentTerminalPointIndex, x
            wFilamentTerminalPointIndex=[]
            # Insert all array elements in hash
            # table
            mp={}
            for i in range(n):
                if arr[i] not in mp:
                    mp[arr[i]]=0
                mp[arr[i]]+=1

            # Traverse through map only and
            for x in mp:
                if (mp[x]== 1):
                    # print(x,end=" ")
                    wFilamentTerminalPointIndex.append(x)
        #Flatten Filament edges
        # arr = vFilamentsEdges1DAll=reduce(operator.concat, vFilamentsEdges)
        arr = reduce(operator.concat, vFilamentsEdges)

        n = len(arr)
    #run function firstNonRepeating to find Terminal Indices
        firstNonRepeating(arr, n)
    #Remove Beginning Vertex
        # wStartingIndex=[i for i in range(len(wFilamentTerminalPointIndex))
        #                                if wFilamentTerminalPointIndex[i] == vBeginningVertex]
        # del wFilamentTerminalPointIndex[[i for i in range(len(wFilamentTerminalPointIndex))
        #                                if wFilamentTerminalPointIndex[i] == vBeginningVertex][0]]

    # Find Branch point Indices
        wFilamentBranchPointIndex=[x for x, y in collections.Counter(arr).items() if y > 2]
    #Extract the Filament Point Position from the determined indices
        if len(wFilamentTerminalPointIndex) > 1:
            wFilamentTerminalPoints=list(itemgetter(*wFilamentTerminalPointIndex)(vFilamentsXYZ))
            if wFilamentBranchPointIndex!=[]:
                wFilamentBranchPoints=list(itemgetter(*wFilamentBranchPointIndex)(vFilamentsXYZ))
        else:
            wFilamentTerminalPoints=[x[1] for x in enumerate(vFilamentsXYZ)
                          if x[0] in wFilamentTerminalPointIndex]
            if wFilamentBranchPointIndex!=[]:
                wFilamentBranchPoints=[x[1] for x in enumerate(vFilamentsXYZ)
                          if x[0] in wFilamentBranchPointIndex]
    ###############################################################################
    ###############################################################################
        vAllSegmentsPerFilamentRadiusWorkingInserts=[]
        vAllSegmentsPerFilamentPositionsWorkingInserts=[]
        vAllSegmentsTypesPerFilamentWorkingInserts=[]
        vAllSegmentIdsPerFilamentInserts=[]
        wDistanceValuesMax=[]
        wDistanceValuesMin=[]
    ###############################################################################
        #Loop through dendrite segments, terminal segements and spine segments
        for vBranchIndex in range (vNumberOfDendriteBranches):
            SegmentCountALL=SegmentCountALL+1
            zReOrderedFilamentPointIndexWorking=[]
            zReOrderedFilamentPositionsWorking=[]
            zReOrderedFilamentRadiusWorking=[]
    #Set the ID for dendrite segment
            vSegmentIdWorking = vSegmentIds[vBranchIndex]
            #Isolate all edges for the working segment
            vSegmentWorkingPointIndex=[i for i in range(len(vFilamentsEdgesSegmentId))
                                       if vFilamentsEdgesSegmentId[i] == vSegmentIdWorking]
            if len(vSegmentWorkingPointIndex)>1:
                vSegmentEdgesWorking=list(itemgetter(*vSegmentWorkingPointIndex)(vFilamentsEdges))
            else:
                vSegmentEdgesWorking=[x[1] for x in enumerate(vFilamentsEdges)
                              if x[0] in vSegmentWorkingPointIndex]

            #Find unique edge indices using "set" and convert back to list
            vEdgesUniqueWorking=list(set(x for l in vSegmentEdgesWorking for x in l))

       #Find current Working Dendrite segment parts
            vSegmentPositionsWorking=list(itemgetter(*vEdgesUniqueWorking)(vFilamentsXYZ))
            vSegmentRadiusWorking=list(itemgetter(*vEdgesUniqueWorking)(vFilamentsRadius))
            vSegmentTypesWorking=list(itemgetter(*vEdgesUniqueWorking)(vTypes))

            #Unit length number of points that make it up
            vSegmentBranchLength.append(len(vEdgesUniqueWorking))

            #Collate all SegmentId by Type (dendrtie or spine)
            if max(vSegmentTypesWorking)==0:
                wSegmentIdsDendrite.append(vSegmentIdWorking)
                wSegmentIdsALL.append(vSegmentIdWorking)
            else:
                wSegmentIdsSpine.append(vSegmentIdWorking)
                wSegmentIdsALL.append(vSegmentIdWorking)
    ##################################################################
    #Test is the segmentlength is too short to reoreeder or fil spots. Currently set to 5
            if len(vSegmentPositionsWorking)<3:
            #Collate with all data but bypass reorder and Fill steps.
                vAllSegmentsPerFilamentRadiusWorkingInserts.extend([vSegmentRadiusWorking])
                vAllSegmentsPerFilamentPositionsWorkingInserts.extend([vSegmentPositionsWorking])
    ##############################################################################
            #Measure distance of all FilamentPoint position to Filament Startingn point
            #To find out which Denrite segment intersects with each sphere, to
            #hopefully reduce the time of process irrelevant segments
                wDistanceValuesMax.append(np.amax(cdist([vBeginningVertexPositionXYZ], vSegmentPositionsWorking)))
                wDistanceValuesMin.append(np.amin(cdist([vBeginningVertexPositionXYZ], vSegmentPositionsWorking)))
                continue
    ##############################################################################
    ##############################################################################
    #ReOrderDendrite
        #Reordering
        #flattten list
            zNum=reduce(operator.concat, vSegmentEdgesWorking)
            #Test for perfect edge sequence, no reordereding needed
            # if zNum == sorted(zNum):
            #     zReOrderedFilamentRadiusWorking=vSegmentRadiusWorking[:]
            #     zReOrderedFilamentPositionsWorking=vSegmentPositionsWorking[:]
            #     # zReorderedvSegmentIds.extend([vSegmentIdWorking]*len(vSegmentRadiusWorking))
            #     # zReorderedvSegmentType.extend([max(vSegmentTypesWorking)]*len(vSegmentRadiusWorking))
            # else:
            #find duplicates
            zDup=[zNum[i] for i in range(len(zNum)) if not i == zNum.index(zNum[i])]
            #find individuals - start and end index
            zIndiv=list(set(zNum).difference(zDup))

            if len(zIndiv)<2:
                vAllSegmentsPerFilamentRadiusWorkingInserts.append([vSegmentRadiusWorking])
                vAllSegmentsPerFilamentPositionsWorkingInserts.append([vSegmentPositionsWorking])
                vAllSegmentsTypesPerFilamentWorkingInserts.extend([max(vSegmentTypesWorking)]*len(vSegmentRadiusWorking))
                vAllSegmentIdsPerFilamentInserts.extend([vSegmentIdWorking]*len(vSegmentRadiusWorking))

            else:

                zStartIndex=zIndiv[0]
                zEndIndex=zIndiv[1]
                zReOrderedFilamentPointIndexWorking.append(zStartIndex)
                zReOrderedFilamentPositionsWorking.append(vFilamentsXYZ[zStartIndex])
                zReOrderedFilamentRadiusWorking.append(vFilamentsRadius[zStartIndex])

            #start of loop for each dendrite segment
                for k in range (len(vSegmentRadiusWorking)-1):
                    if k==0:
                        #find nested list index that contains StartIndex (5,1)--next point is (5,0)
                        #convert tuple to list
                        zEdgesNext=list(reduce(operator.concat, [(index_,sub_list.index(zStartIndex))\
                             for index_, sub_list in enumerate(vSegmentEdgesWorking)\
                             if zStartIndex in sub_list]))

                        #find next segment index delete previous one
                        if zEdgesNext[1]==1:
                            zNextSegmentIndex=vSegmentEdgesWorking[zEdgesNext[0]][0]#next index in sequence
                            vSegmentEdgesWorking.pop(zEdgesNext[0])#remove list of list
                        else:
                            zNextSegmentIndex=vSegmentEdgesWorking[zEdgesNext[0]][1]#next index in sequence
                            vSegmentEdgesWorking.pop(zEdgesNext[0])#remove list of list
                        #collate segment indices
                        zReOrderedFilamentPointIndexWorking.append(zNextSegmentIndex)
                        zReOrderedFilamentPositionsWorking.append(vFilamentsXYZ[zNextSegmentIndex])
                        zReOrderedFilamentRadiusWorking.append(vFilamentsRadius[zNextSegmentIndex])

                    else:
                       #find nested list index that contains NextIndex
                       #convert tuple to list
                        zEdgesNext=list(reduce(operator.concat, [(index_,sub_list.index(zNextSegmentIndex))\
                             for index_, sub_list in enumerate(vSegmentEdgesWorking)\
                             if zNextSegmentIndex in sub_list]))

                        if zEdgesNext[1]==1:
                            zNextSegmentIndex=vSegmentEdgesWorking[zEdgesNext[0]][0]#next index in sequence
                            vSegmentEdgesWorking.pop(zEdgesNext[0])#remove list of list
                        else:
                            zNextSegmentIndex=vSegmentEdgesWorking[zEdgesNext[0]][1]#next index in sequence
                            vSegmentEdgesWorking.pop(zEdgesNext[0])#remove list of list

                        zReOrderedFilamentPointIndexWorking.append(zNextSegmentIndex)
                        zReOrderedFilamentPositionsWorking.append(vFilamentsXYZ[zNextSegmentIndex])
                        zReOrderedFilamentRadiusWorking.append(vFilamentsRadius[zNextSegmentIndex])
                # zReorderedvSegmentIds.extend([vSegmentIdWorking]*len(vSegmentRadiusWorking))
                # zReorderedvSegmentType.extend([max(vSegmentTypesWorking)]*len(vSegmentRadiusWorking))

        ##############################################################################
        ##############################################################################
        #fill spots in filament point gaps
                vSegmentRadiusWorkingInserts=zReOrderedFilamentRadiusWorking[:]
                vSegmentPositionsWorkingInserts=zReOrderedFilamentPositionsWorking[:]
                if max(vSegmentTypesWorking)==0:
                    for loop in range (3):#loop through 3 times
                        i=0
                        while i<=(len(vSegmentPositionsWorkingInserts)-2):
                            vFillFilamentPairDist=pdist([vSegmentPositionsWorkingInserts[i],vSegmentPositionsWorkingInserts[i+1]])
                            vFillFilamentRadialSum=vSegmentRadiusWorkingInserts[i]+vSegmentRadiusWorkingInserts[i+1]
                            if vFillFilamentPairDist>vFillFilamentRadialSum:
            #insert Radius at next spot
                                vSegmentRadiusWorkingInserts[i+1:i+1]=[vFillFilamentRadialSum/2]
                                vSegmentPositionsWorkingInserts[i+1:i+1]=[np.divide(np.add(vSegmentPositionsWorkingInserts[i+1],
                                                                                            vSegmentPositionsWorkingInserts[i]),2).tolist()]
                            i=i+1
                vAllSegmentsPerFilamentRadiusWorkingInserts.extend([vSegmentRadiusWorkingInserts])
                vAllSegmentsPerFilamentPositionsWorkingInserts.extend([vSegmentPositionsWorkingInserts])
                # vAllSegmentsTypesPerFilamentWorkingInserts.extend([max(vSegmentTypesWorking)]*len(vSegmentRadiusWorkingInserts))
                # vAllSegmentIdsPerFilamentInserts.extend([vSegmentIdWorking]*len(vSegmentRadiusWorkingInserts))
    ##############################################################################
            #Measure distance of all FilamentPoint position to Filament Startingn point
            #To find out which Denrite segment intersects with each sphere, to
            #hopefully reduce the time of process irrelevant segments
            if len(zIndiv)<2:
                wDistanceValuesMax.append(np.amax(cdist([vBeginningVertexPositionXYZ], vSegmentPositionsWorking)))
                wDistanceValuesMin.append(np.amin(cdist([vBeginningVertexPositionXYZ], vSegmentPositionsWorking)))
            else:
                wDistanceValuesMax.append(np.amax(cdist([vBeginningVertexPositionXYZ], vSegmentPositionsWorkingInserts)))
                wDistanceValuesMin.append(np.amin(cdist([vBeginningVertexPositionXYZ], vSegmentPositionsWorkingInserts)))
    ##############################################################################
    ##############################################################################
    # Insert dual progress bar one dendrite branches
    # one for filaments
        #Progress bar for dendrite segments
            progress_bar1['value'] = int((vBranchIndex+1)/vNumberOfDendriteBranches*100) #  % out of 100
            qProgressBar.update()

    ##############################################################################
    ##############################################################################

    #Create a normalize color basd on the number of potential Sholl spheres
            wApproxNumSpheres=(max(wDistanceValuesMax)/vShollRadius).astype(int)
            wColorList=np.linspace(start=.1,stop=.9,num=wApproxNumSpheres)

            zShollLabelsFinal=list(range(vShollRadius, vShollRadius*(wApproxNumSpheres+1), vShollRadius))


    ##############################################################################
        vShollSpotCount=0
        vShollNodeCount=0
    ################################################
        wCompleteShollSpotDistAlongFilamentStatWorking=[]
        vDendriteALLXSphere=[]
        qSpotinQuestionALL=[]
    ################################################
    ################################################
        aIntensityLowerThresholdManual=0
        aShollIndex=0
        vBranchIndex=0
        zShollLabelsAll=[]
        vShollFinalIndex=0

    #Progress through each Sholl Sphere
        for aShollIndex in range (round(max(wDistanceValuesMax))):
            vSpotPositionCurrentShollSphere=[]#Clears current Sholl spots
            count=0
            #Set lower and upper threshold for the Sholl Mask
            aIntensityLowerThresholdManual=aIntensityLowerThresholdManual+1
            aIntensityUpperThresholdManual=aIntensityLowerThresholdManual+(aXvoxelSpacing*2)
            qSpotinQuestion=[]
            qNodeinQuestion=[]
            qShollSpotNodeClassify=[]

    #Create list of Sholl labels
            zShollLabelsAll.append(str(aIntensityLowerThresholdManual))


        # Process a each branch and find point distance to starting point
        # filter by current sholl sphere distance
        # Test if Dendrite fails on the Sholl sphere
        #find the indices of segments that cross the current Sholl Sphere
            vSegmentsCurrentShollSphereIndexMax=[index for index,value in enumerate(wDistanceValuesMax)
                                              if value >= aIntensityLowerThresholdManual]
            vSegmentsCurrentShollSphereIndexMin=[index for index,value in enumerate(wDistanceValuesMin)
                                              if value <= aIntensityLowerThresholdManual]
            wSegmentIndexIntersectSholl=list(set(vSegmentsCurrentShollSphereIndexMax).intersection(vSegmentsCurrentShollSphereIndexMin))

            if wSegmentIndexIntersectSholl==[]:
                break
    ##############################################################################
            for vBranchIndex in range (len(wSegmentIndexIntersectSholl)):
                vDendritePositionsNEW=vAllSegmentsPerFilamentPositionsWorkingInserts[wSegmentIndexIntersectSholl[vBranchIndex]]
                #Measure distance from each point to starting for current segment
                vDistanceListValues=cdist([vBeginningVertexPositionXYZ],
                                          vAllSegmentsPerFilamentPositionsWorkingInserts[wSegmentIndexIntersectSholl[vBranchIndex]])
                #Set base for each filament point to false
                vDendriteXSphere = np.array([0]*(np.size(vDistanceListValues)))
                #Test filament points to find those near current sholl sphere
                wShollIntersectionIndex=np.where(np.logical_and(vDistanceListValues>float(aIntensityLowerThresholdManual), vDistanceListValues<aIntensityUpperThresholdManual))
                wShollIntersectionIndex = wShollIntersectionIndex[1].tolist()

            #if no filament point is detected, within these defined limits
                #find the closest point and use that as the lone Sholl intersection
                if len(wShollIntersectionIndex)==0:#if list array is empty
                    wShollIntersectionIndex = np.where(abs(vDistanceListValues-aIntensityLowerThresholdManual) == np.amin(abs(vDistanceListValues-aIntensityLowerThresholdManual)))[1].tolist()
                #convert to real numbers
                vDendriteXSphere[np.array(wShollIntersectionIndex)]=int(1)
                #convert to positionsXYZ
                # vDendriteXSpherePositionXYZ=itemgetter(*wShollIntersectionIndex[1].tolist())(vAllSegmentsPerFilamentPositionsWorkingInserts[wSegmentIndexIntersectSholl[vBranchIndex]])
                if len(vDendriteXSphere)>0:
                    #Need to add one zero to the end of series so that a peak can be identified at the tail end
                    vDendriteXSphere=np.pad(vDendriteXSphere, (0,2), 'constant')
                    PeakIndex, _ = find_peaks(vDendriteXSphere, height=0.25)
                    # remove the trailing zero
                    PeakIndexWorking=PeakIndex.tolist()
                    #Test for single gaps in the dendrite peak and fill them. Likely not
                    #enough to warrrent a true Sholl intersection cross
                    if len(PeakIndexWorking)>1:
                        for i in range(len(PeakIndexWorking)-1):
                            if PeakIndexWorking[i]+1==PeakIndexWorking[i+1]-1:
                                vDendriteXSphere[PeakIndexWorking[i]+1]=1

                    #reset binary segment to original removing doube pad
                    vDendriteXSphere = vDendriteXSphere[:-1]
                    vDendriteXSphere = vDendriteXSphere[:-1]
    #qSpotinQuestion Scenarios
    #1---single point at begining of segment
    #2---multiple points at beginning of segment
    #3---all points including fist and last
    #4---single point at the end
    #5---multiple points at the end
    #0---no issues

    #########################
        #Scenario#1----Test if first point is a sholl intersection -add to peak index list
                    if vDendriteXSphere[0]==1:
                        PeakIndexWorking=np.insert(PeakIndexWorking, 0, 0).astype(int)
    ##################################################
                    #compile each segments peaks
                    vDendriteALLXSphere.append(vDendriteXSphere)

                #Analysis of each Peak index and surrounding peaks
                    for i in range(len(PeakIndexWorking)):
                        count=0
                        b=vDendriteXSphere[PeakIndexWorking[i]:]#generated series starting from next peakpoint
                        b=np.append(b,0)
                        while b[count]==1:
                            count=count+1
                    #Is peak at front end of semgent (2 in length)
                        if PeakIndexWorking[i]==0:
                            # vSpotPositionCurrentShollSphere.append(vDendritePositionsNEW[PeakIndexWorking[i]])
                            qSpotinQuestion=True
                            if count==1:
                                qShollSpotNodeClassify.append(1)
                            else:
                                qShollSpotNodeClassify.append(2)
                            qNodeinQuestion.append(vDendritePositionsNEW[PeakIndexWorking[i]])
                            vShollNodeCount=vShollNodeCount+1
                            vShollSpotCount=vShollSpotCount+1

                    #Is peak at tail end of semgent (2 in length)- branch or terminal
                        elif PeakIndexWorking[i]!=0 and vDendriteXSphere[-1]==1:
                            vSpotPositionCurrentShollSphere.append(vDendritePositionsNEW[-1])# grab last point in segment
                        #Test if this Sholl Intersection is a Terminal point
                            qIsSpotaTerminalPoint =  any(item in wFilamentTerminalPoints for item in vSpotPositionCurrentShollSphere[-1])
                            if qIsSpotaTerminalPoint == True:
                                vShollSpotCount=vShollSpotCount+1
                            else:
                                del vSpotPositionCurrentShollSphere[-1]#Remove added Sholl spot position
                                qSpotinQuestion=True
                                if count==1:
                                    qShollSpotNodeClassify.append(3)
                                else:
                                    qShollSpotNodeClassify.append(4)
                                qNodeinQuestion.append(vDendritePositionsNEW[-1])
                                vShollNodeCount=vShollNodeCount+1
                                vShollSpotCount=vShollSpotCount+1
                        else:
                            vSpotPositionCurrentShollSphere.append(vDendritePositionsNEW[PeakIndexWorking[i]])
                            vShollSpotCount=vShollSpotCount+1

    ###############################################################################
    ###############################################################################

    ###############################################
    ###############################################
    #Correct the edge related intersections - after last branch index
    #Process and remove duplicate spots and reduce spots near node.
            if qSpotinQuestion==True:#Test if there are any questionable intersections
                #Find Unique Spots, counts and indices in question
                qUniqueNodes, qUniqueIndex,qUniqueCounts = np.unique(np.array(qNodeinQuestion), return_counts=True, return_index=True, axis=0)
                for qIndex in range (len(qUniqueIndex)):
                    #Find index of unique nodes in question
                    qNodeinQuestionIndexWorking=np.where((qNodeinQuestion == qUniqueNodes[qIndex]).all(axis=1))[0].tolist()
                    if qUniqueCounts[qIndex]==1:
                        vSpotPositionCurrentShollSphere.append(qUniqueNodes[qIndex].tolist())
                        vShollSpotCount=vShollSpotCount-1
                    if qUniqueCounts[qIndex]==2:
                        vSpotPositionCurrentShollSphere.append(qUniqueNodes[qIndex].tolist())
                        vShollSpotCount=vShollSpotCount-1
                    if qUniqueCounts[qIndex]==3:
                        vSpotPositionCurrentShollSphere.append(qUniqueNodes[qIndex].tolist())
                        vShollSpotCount=vShollSpotCount-2
                    if qUniqueCounts[qIndex]==4:
                        vSpotPositionCurrentShollSphere.append(qUniqueNodes[qIndex].tolist())
                        vShollSpotCount=vShollSpotCount-3

    ###############################################################################
            #Compile all Sholl Intersections per Sholl sphere (uneditted)
            vSpotPositionAllShollSpheresALL.extend([vSpotPositionCurrentShollSphere])
            vSpotPositionAllShollSpheresPerFilamentALL.extend([vSpotPositionCurrentShollSphere])
            #Number of sholl intersections per filament
            vNumberofShollIntersectionsALL.append(len(vSpotPositionCurrentShollSphere))
            vNewStatSpotShollDistanceALL.extend([aIntensityLowerThresholdManual]*len(vSpotPositionAllShollSpheresPerFilamentALL[aShollIndex]))

            if aIntensityLowerThresholdManual in zShollLabelsFinal:
                #Compile all Sholl Intersections per Sholl sphere (uneditted)
                vSpotPositionAllShollSpheres.extend([vSpotPositionCurrentShollSphere])
                vSpotPositionAllShollSpheresPerFilament.extend([vSpotPositionCurrentShollSphere])
                #Number of sholl intersections per filament
                vNumberofShollIntersections.append(len(vSpotPositionCurrentShollSphere))
                vNewStatSpotShollDistance.extend([aIntensityLowerThresholdManual]*len(vSpotPositionAllShollSpheresPerFilament[vShollFinalIndex]))

    ###############################################################################
        #Create Sholl Spots for the current Sholl Sphere for current Filament
                vShollCurrentSpotRadius=[1]*len(vSpotPositionAllShollSpheresPerFilament[vShollFinalIndex])
                vShollCurrentSpotTime=[vFilamentsIndexT]*len(vSpotPositionAllShollSpheresPerFilament[vShollFinalIndex])

                if len(vShollCurrentSpotRadius) > 0 and qSplitShollspheres == 1:
                    #Create the a new Spots generated from teh center of Mass
                    vNewSpots = vImarisApplication.GetFactory().CreateSpots()
                    vNewSpots.Set(vSpotPositionAllShollSpheresPerFilament[vShollFinalIndex],
                                  [vFilamentsIndexT]*len(vSpotPositionAllShollSpheresPerFilament[vShollFinalIndex]),
                                  [1]*len(vSpotPositionAllShollSpheresPerFilament[vShollFinalIndex]))
                    vNewSpots.SetName('FilamentID:'+str(vFilamentIds[vFilamentCountActual-1]) +
                        ' -- ' + str(aIntensityLowerThresholdManual) +
                                      ' um Sholl Sphere')
                    zRandomColor=((wColorList[vShollFinalIndex]) * 256 * 256 * 256 )
                    vNewSpots.SetColorRGBA(zRandomColor)#Set Random color
                    #Add new spots to Surpass Scene
                    vShollResult.AddChild(vNewSpots, -1)
                    vImarisApplication.GetSurpassScene().AddChild(vShollResult, -1)

            #Number of sholl intersections per sholl sphere
                vNumberofIntersectionsPerShollSphere.append(len(vSpotPositionCurrentShollSphere))
                vNewStatSpotNumberShollIntersections.extend([vNumberofIntersectionsPerShollSphere[vShollFinalIndex]]*vNumberofIntersectionsPerShollSphere[vShollFinalIndex])


        #Reset stat for next Sholl Sphere
                vSpotPositionCurrentShollSphere=[]
                vShollSpotTime=[]
                vShollSpotRadius=[]
                vShollSpotCount=0
                vDendriteALLXSphere=[]
                vShollFinalIndex=vShollFinalIndex+1

        #after the last sholl sphere
        vNewStatNumberShollIntersectionPerFilament.append(sum(vNumberofShollIntersections))
        vNumberOfShollIntersectionPerSpherePerFilament.extend(vNumberofIntersectionsPerShollSphere)
        vNumberofShollIntersections=[]
        vNumberofIntersectionsPerShollSphere=[]

        vNewFilamentStatCriticalRadiusHighRes=(np.argmax(np.array(vNumberofShollIntersectionsALL))+1).tolist()
        vNewFilamentStatMaxIntersectionsHighRes=(np.max(np.array(vNumberofShollIntersectionsALL))).tolist()

    ###############################################################################
        #Calculate slope???Linear regression
        #From Critical radius to outer ring
        # x = vNumberofShollIntersectionsALL[vNewFilamentStatMaxIntersectionsHighRes:len(vNumberofShollIntersectionsALL)+1]
        # y = list(range(vNewFilamentStatMaxIntersectionsHighRes, len(vNumberofShollIntersectionsALL)))

        # zLinearRegressionSlope, zLinearRegressionIntercept, zLinearRegression_r, zLinearRegression_p, zLinearRegression_std_err = stats.linregress(x, y)

        # def myfunc(x):
        #   return slope * x + intercept

        # mymodel = list(map(myfunc, x))

        # plt.scatter(x, y)
        # plt.plot(x, mymodel)
        # plt.show()

    ###############################################################################
        #Logaithmic Regression
        # import math
        # from math import log

        # x = vNumberofShollIntersectionsALL[vNewFilamentStatMaxIntersectionsHighRes:len(vNumberofShollIntersectionsALL)+1]
        # y = list(range(vNewFilamentStatMaxIntersectionsHighRes, len(vNumberofShollIntersectionsALL)))

        # x=[log(i) for i in x]
        # xNEW=[x[i]/(y[i]*y[i]*math.pi) for i in range(len(x))]

        #fit the model
        # plt.scatter(x, y)
        # plt.show()
        # fit = np.polyfit(np.array(xNEW), np.array(y), 1)

        # #view the output of the model
        # print(fit)



    ###############################################################################
    ###############################################################################
    #Spilt Dendrite segments at the point of Sholl intersection
    #Create new label/statistic to id
        #Spilt out Final defined sholl spheres to new value
        # vFinalShollSpheres=[vSpotPositionAllShollSpheresPerFilament[i] for i in [i-1 for i in zShollLabelsFinal]]
        #flatten all Sholl intersection to single list
        vSpotPositionAllShollSpheresFlat = [x for xs in vSpotPositionAllShollSpheresPerFilament for x in xs]

    #Find spot on each filament and delete the spot to split dendrite at the sholl intersection
        for qIndexShollPosition in range(len(vSpotPositionAllShollSpheresFlat)):
            zShollxyzCurrent=vSpotPositionAllShollSpheresFlat[qIndexShollPosition]
            zShollxyz=np.array(vFilamentsXYZ).T
            zClosestDistanced3D = ( (zShollxyz[0] - zShollxyzCurrent[0]) ** 2 + (zShollxyz[1] - zShollxyzCurrent[1]) ** 2 + (zShollxyz[2] - zShollxyzCurrent[2]) ** 2) ** 0.5#for3D
            zClosest_index = np.argmin(zClosestDistanced3D)
            zClosest = vFilamentsXYZ[zClosest_index]
            #Find/delete Edges Index from original FilamentEdges
            # zNewFilamentsEdges=(np.delete(zNewFilamentsEdges,zClosest_index,0)).tolist()
            zNewFilamentsEdges=(np.delete(zNewFilamentsEdges, np.where(zNewFilamentsEdges==zClosest_index)[0][0],0)).tolist()


    #Create a NEW Filament object with dendrite segments split
        vNewFilaments=vImarisApplication.GetFactory().CreateFilaments()
        vNewFilaments.AddFilament(zNewFilamentsXYZ, zNewFilamentsRadius, zNewFilamentsTypes, zNewFilamentsEdges, vFilamentsIndexT)
        vNewFilaments.SetName('Sholl Dendrites (ID: ' + str(vFilamentIds[vFilamentCountActual-1])+')')

        vNewFilaments.SetName('FilamentID:'+ str(vFilamentIds[vFilamentCountActual-1])+' -- Sholl Dendrites')

        vShollDendrites.AddChild(vNewFilaments, -1)
        vImarisApplication.GetSurpassScene().AddChild(vShollDendrites, -1)

    #Get Dendrite position stats
        # zStatisticNames = vNewFilaments.GetStatisticsNames()
        zStatisticDendritePosX = vNewFilaments.GetStatisticsByName('Dendrite Position X').mValues
        zStatisticDendritePosY = vNewFilaments.GetStatisticsByName('Dendrite Position Y').mValues
        zStatisticDendritePosZ = vNewFilaments.GetStatisticsByName('Dendrite Position Z').mValues
        zStatisticDendriteLength= vNewFilaments.GetStatisticsByName('Dendrite Length').mValues
        zStatisticDendriteIds = vNewFilaments.GetStatisticsByName('Dendrite Position X').mIds

    #Measure distance from each Dendrite position to starting point
         #Collate XYZ positions in to a single list
        zNewDendritesPosXYZ=[list(t) for t in zip(zStatisticDendritePosX, zStatisticDendritePosY, zStatisticDendritePosZ)]
        zDistanceDendriteListValues=cdist([vBeginningVertexPositionXYZ], zNewDendritesPosXYZ)
        zDistanceDendriteListValues=zDistanceDendriteListValues.transpose()

    #CreateLabels for each Sholl sphere
        # scount=0
        # zShollLabelsAll = [20]
        # i=0
        vNewFilamentsStatId=[]
        vNewFilamentsStatLength=[]
        vNewFilamentsStatShollSphere=[]

        zShollLabelsInt=list(range(vShollRadius, vShollRadius*(wApproxNumSpheres+2), vShollRadius))


        # zShollLabelsInt = [int(i) for i in zShollLabelsFinal]
        zShollLabelsInt.insert(0,0)#insert a zero at start of list
        vLabelIndices=[]
        for i in range (len(zShollLabelsInt)-1):
            zDistanceDendriteListValues=np.where((zDistanceDendriteListValues > zShollLabelsInt[i]) &
                             (zDistanceDendriteListValues <= zShollLabelsInt[i+1]),zShollLabelsInt[i+1], zDistanceDendriteListValues)
    ###Creating new statistics for segmented dendrite length
            vNewFilamentsStatLength.append(sum([zStatisticDendriteLength[i]
                                                for i in np.where(zDistanceDendriteListValues==zShollLabelsInt[i+1])[0].tolist()]))

    ###############################################################################
        #Add Sholl Statistics
        vNewFilamentsStatvIds=list(range(len(zStatisticDendriteIds)))
        vNewFilamentsStatUnits=['']*(len(zStatisticDendriteIds))
        vNewFilamentsStatFactors=(['Dendrite']*len(zStatisticDendriteIds), [str(vFilamentsIndexT+1)]*len(zStatisticDendriteIds))
        vNewFilamentsStatFactorName=['Category','Time']
    #######################
        vNewFilamentsIdStat=[vFilamentIds[vFilamentCountActual-1]-100000000]*len(zStatisticDendriteIds)
        vNewFilamentsStatNames=[' xFilament ID']*(len(zStatisticDendriteIds))
        vNewFilaments.AddStatistics(vNewFilamentsStatNames, vNewFilamentsIdStat,
                              vNewFilamentsStatUnits, vNewFilamentsStatFactors,
                              vNewFilamentsStatFactorName, zStatisticDendriteIds)
    ########################
        vNewFilamentsStatShollSphere=zDistanceDendriteListValues.tolist()
        vNewFilamentsStatShollSphere = [x for xs in vNewFilamentsStatShollSphere for x in xs]
        vNewFilamentsStatNames=[' Sholl Sphere']*(len(zStatisticDendriteIds))
        vNewFilaments.AddStatistics(vNewFilamentsStatNames, vNewFilamentsStatShollSphere,
                              vNewFilamentsStatUnits, vNewFilamentsStatFactors,
                              vNewFilamentsStatFactorName, zStatisticDendriteIds)

    ###############################################################################
    ###############################################################################

    ###############################################################################
    #Create Sholl Spots object for each filament with new stats
        vNewShollSpotsPerFilament = vImarisApplication.GetFactory().CreateSpots()


        # vFinalShollSpheres=[vSpotPositionAllShollSpheresPerFilament[i] for i in [i-1 for i in zShollLabelsFinal]]
        #may need to flatten spot list of lists
        vSpotPositionAllShollSpheresPerFilament = [num for elem in vSpotPositionAllShollSpheresPerFilament for num in elem]


        vNewShollSpotsPerFilament.Set(vSpotPositionAllShollSpheresPerFilament,
                              [vFilamentsIndexT]*len(vSpotPositionAllShollSpheresPerFilament),
                              [1]*len(vSpotPositionAllShollSpheresPerFilament))
        # vNewShollSpotsPerFilament.SetName(' Sholl Intersections FilamentID: ' +
        #                           str(vFilamentIds[vFilamentCountActual-1]))
        vNewShollSpotsPerFilament.SetName(' FilamentID:'+ str(vFilamentIds[vFilamentCountActual-1]))
        zRandomColor=(random.uniform(0, 1) * 256 * 256 * 256 )
        vNewShollSpotsPerFilament.SetColorRGBA(zRandomColor)#Set Random color
        vShollResult2.AddChild(vNewShollSpotsPerFilament, -1)
        vImarisApplication.GetSurpassScene().AddChild(vShollResult2, -1)

        # vShollResult2.SetVisible(0)
        # vNewShollSpotsPerFilament.SetVisible(0)

        #############################################################
        #Add new stats
        vSpotsTimeIndex=[vFilamentsIndexT+1]*len(vSpotPositionAllShollSpheresPerFilament)
        vSpotsvIds=list(range(len(vSpotPositionAllShollSpheresPerFilament)))
        vSpotsStatUnits=['um']*len(vSpotPositionAllShollSpheresPerFilament)
        vSpotsStatFactors=(['Spot']*len(vSpotPositionAllShollSpheresPerFilament), [str(x) for x in vSpotsTimeIndex] )
        vSpotsStatFactorName=['Category','Time']
        ###########################
        # vSpotsStatNames=[' Sholl Sphere Distance']*len(vSpotPositionAllShollSpheresPerFilament)
        # vNewShollSpotsPerFilament.AddStatistics(vSpotsStatNames, vNewStatSpotShollDistance,
        #                               vSpotsStatUnits, vSpotsStatFactors,
        #                               vSpotsStatFactorName, vSpotsvIds)
        # ###########################
        # vSpotsStatUnits=['']*len(vSpotPositionAllShollSpheresPerFilament)
        # vSpotsStatNames=[' Number of Intersections']*len(vSpotPositionAllShollSpheresPerFilament)
        # vNewShollSpotsPerFilament.AddStatistics(vSpotsStatNames, vNewStatSpotNumberShollIntersections,
        #                               vSpotsStatUnits, vSpotsStatFactors,
        #                               vSpotsStatFactorName, vSpotsvIds)

    ###############################################################################
    ###############################################################################
    #Add Overall statistics for sum dendrite length per sholl sphere
            #Insert an overall Statistics
        vOverallStatIds=[int(-1)]
        vOverallStatUnits_um=['um']*vSizeT
        vOverallStatUnits=['']*vSizeT
        vOverallStatFactorsTime=list(range(1,vSizeT+1))
        vOverallStatFactors=[['Overall'],[str(i) for i in vOverallStatFactorsTime]]
        vOverallStatFactorNames=['FactorName','Time']

    #loop for each sphere and create overall stat
        #main loop adds one for last sholl ring
        for i in range (len(zShollLabelsInt)-1):
            # vOverallStatNames = [' zFilamentID:'+ str(vFilamentIds[vFilamentCountActual-1])+'--'+ str(zShollLabelsInt[i+1]) + ' um Sholl Dendrite Length Sum']
            if zShollLabelsInt[i] >= 100:
                vOverallStatNames = [' Dendrite Length Sum - ' + str(zShollLabelsInt[i+1]) + ' um Sholl Ring']
            else:
                vOverallStatNames = [' Dendrite Length Sum - ' + '0' + str(zShollLabelsInt[i+1]) + ' um Sholl Ring']

            vNewShollSpotsPerFilament.AddStatistics(vOverallStatNames, [vNewFilamentsStatLength[i]],
                                      vOverallStatUnits_um, vOverallStatFactors,
                                      vOverallStatFactorNames, vOverallStatIds)
            #Loop just the sholl sphere values
            if i > 0 and i < len(zShollLabelsInt)-1:
                # vOverallStatNames = [' Number Intersections - ' + str(zShollLabelsInt[i]) + ' um Sholl Sphere']
                # vNewShollSpotsPerFilament.AddStatistics(vOverallStatNames, [vNumberOfShollIntersectionPerSpherePerFilament[i-1]],
                #                           vOverallStatUnits, vOverallStatFactors,
                #                           vOverallStatFactorNames, vOverallStatIds)

                #Set Sholl sphere Labels for each filament
                vLabelIndices = (np.where(np.array(vNewStatSpotShollDistance)==zShollLabelsInt[i]))[0].tolist()
                wLabelList=[]
                for j in range (len(vLabelIndices)):
                    vLabelCreate = vFactory.CreateObjectLabel(vLabelIndices[j], "Sholl Intersections", ' '+str(zShollLabelsInt[i]))
                    wLabelList.append(vLabelCreate)
                vNewShollSpotsPerFilament.SetLabels(wLabelList)

            # vNewFilaments.AddStatistics(vOverallStatNames, [vNewFilamentsStatLength[i]],
            #                           vOverallStatUnits, vOverallStatFactors,
            #                           vOverallStatFactorNames, vOverallStatIds)
    ###########
    #Calculate and report the Critical Radius (radius with the highest density)
        vNewFilamentStatCriticalRadius=[vNewStatSpotShollDistance[vNewStatSpotNumberShollIntersections.index(max(vNewStatSpotNumberShollIntersections))]]
        vNewFilamentStatMaxIntersections=[max(vNewStatSpotNumberShollIntersections)]

        vOverallStatNames = [' Critical Radius']
        vNewShollSpotsPerFilament.AddStatistics(vOverallStatNames, vNewFilamentStatCriticalRadius,
                                                vOverallStatUnits_um, vOverallStatFactors,
                                                vOverallStatFactorNames, vOverallStatIds)
        vOverallStatNames = [' Max # Intersections']
        vNewShollSpotsPerFilament.AddStatistics(vOverallStatNames, vNewFilamentStatMaxIntersections,
                                                vOverallStatUnits, vOverallStatFactors,
                                                vOverallStatFactorNames, vOverallStatIds)
        HighResStats=1
        if HighResStats==1:
            vOverallStatNames = [' Critical Radius HighRes']
            vNewShollSpotsPerFilament.AddStatistics(vOverallStatNames, [vNewFilamentStatCriticalRadiusHighRes],
                                                    vOverallStatUnits_um, vOverallStatFactors,
                                                    vOverallStatFactorNames, vOverallStatIds)
            vOverallStatNames = [' Max # Intersections HighRes']
            vNewShollSpotsPerFilament.AddStatistics(vOverallStatNames, [vNewFilamentStatMaxIntersectionsHighRes],
                                                    vOverallStatUnits, vOverallStatFactors,
                                                    vOverallStatFactorNames, vOverallStatIds)

    ###############################################################################
    ###############################################################################
    #Calculate sholl intersection distance on dendrite to starting point
    ###############################################################################
    # #Find Spot close to filament and measure distance along path to starting point
    # #Make spot position conect to filament as spine attachment point
        # if vOptionShollIntersectionDistanceAlongFilament==1:

        if vSpotPositionAllShollSpheresPerFilament!=[]:

            if vBeginningVertex !=-1:
                wNewFilamentsEdges=list(vFilamentsEdges)
                wNewFilamentsRadius=list(vFilamentsRadius)
                wNewFilamentsXYZ=list(vFilamentsXYZ)
                wNewFilamentsTypes=list(vTypes)

                #Create array of distance measures to original filament points
                wSpotToAllFilamentDistanceArrayOriginal=cdist(vSpotPositionAllShollSpheresPerFilament,vFilamentsXYZ)
                wSpotToAllFilamentDistanceArrayOriginal=wSpotToAllFilamentDistanceArrayOriginal - vFilamentsRadius

                #For each spot, find index on filament of closest point
                wSpotsFilamentClosestDistancePointIndex=np.argmin(wSpotToAllFilamentDistanceArrayOriginal, axis=1)

                #test is spine attachment point is branch point, if so add one
                for i in range (len(wSpotsFilamentClosestDistancePointIndex)):
                    if wSpotsFilamentClosestDistancePointIndex[i] in wFilamentBranchPointIndex or wSpotsFilamentClosestDistancePointIndex[i] in wFilamentTerminalPointIndex:
                        wSpotNearest=cdist([vSpotPositionAllShollSpheresPerFilament[i]],vFilamentsXYZ)
                        # wSpotNearest = wSpotNearest - vFilamentsRadius -[max(vSpotsColocRadiusWorking[0])]*len(vFilamentsRadius)
                        wSpotsNearestIndex=np.argpartition(wSpotNearest, 2)
                        wSpotsFilamentClosestDistancePointIndex[i]=wSpotsNearestIndex[0][1]
                        if wSpotsFilamentClosestDistancePointIndex[i] in wFilamentBranchPointIndex or wSpotsFilamentClosestDistancePointIndex[i] in wFilamentTerminalPointIndex:
                            wSpotsFilamentClosestDistancePointIndex[i]=wSpotsNearestIndex[0][2]
                        if wSpotsFilamentClosestDistancePointIndex[i] in wFilamentBranchPointIndex or wSpotsFilamentClosestDistancePointIndex[i] in wFilamentTerminalPointIndex:
                            wSpotsFilamentClosestDistancePointIndex[i]=wSpotsNearestIndex[0][3]

                #loop for each spot within threshold
                #append new filament and create list of new spots
                for i in range (len(vSpotPositionAllShollSpheresPerFilament)):
                    wNewFilamentsXYZ.append(vSpotPositionAllShollSpheresPerFilament[i])
                    wNewFilamentsRadius.append(1)
                    wNewFilamentsEdges.append([wSpotsFilamentClosestDistancePointIndex[i],len(vFilamentsRadius)+i])
                    wNewFilamentsTypes.append(1)

                vNewFilament=vImarisApplication.GetFactory().CreateFilaments()
                vNewFilament.AddFilament(wNewFilamentsXYZ, wNewFilamentsRadius, wNewFilamentsTypes, wNewFilamentsEdges, vFilamentsIndexT)
                vNewFilament.SetBeginningVertexIndex(0, vBeginningVertex)

        #Grab New Filament Spine Statistics for attachment point distance.
                vNewFilamentStatistics = vNewFilament.GetStatistics()
                vNewFilamentStatNames = vNewFilamentStatistics.mNames
                vNewFilamentStatValues = vNewFilamentStatistics.mValues
                vNewFilamentStatIds = vNewFilamentStatistics.mIds
                vNewFilamentSpineAttPtDistIndex=[i for i,val in enumerate(vNewFilamentStatNames)
                                                  if val==('Spine Attachment Pt Distance')]
                vNewFilamentSpineAttPtPosXIndex=[i for i,val in enumerate(vNewFilamentStatNames)
                                                  if val==('Spine Attachment Pt Position X')]
                if len(vNewFilamentSpineAttPtDistIndex)>1:
                    vNewFilamentSpineAttPtDist=list(itemgetter(*vNewFilamentSpineAttPtDistIndex)(vNewFilamentStatValues))
                    vNewFilamentStatIdsDist=list(itemgetter(*vNewFilamentSpineAttPtDistIndex)(vNewFilamentStatIds))
                    vNewFilamentSpineAttPtPosX=list(itemgetter(*vNewFilamentSpineAttPtPosXIndex)(vNewFilamentStatValues))
                    vNewFilamentStatIdsAttPosX=list(itemgetter(*vNewFilamentSpineAttPtPosXIndex)(vNewFilamentStatIds))
                else:
                    vNewFilamentSpineAttPtDist=[x[1] for x in enumerate(vNewFilamentStatValues)
                                            if x[0] in vNewFilamentSpineAttPtDistIndex]
                    vNewFilamentStatIdsDist=[x[1] for x in enumerate(vNewFilamentStatIds)
                                            if x[0] in vNewFilamentSpineAttPtDistIndex]
                    vNewFilamentSpineAttPtPosX=[x[1] for x in enumerate(vNewFilamentStatValues)
                                               if x[0] in vNewFilamentSpineAttPtPosXIndex]
                    vNewFilamentStatIdsAttPosX=[x[1] for x in enumerate(vNewFilamentStatIds)
                                             if x[0] in vNewFilamentSpineAttPtPosXIndex]

                #Collate all spots for each filament
                for i in range (len(vSpotPositionAllShollSpheresPerFilament)):
                    wCompleteShollSpotDistAlongFilamentStatWorking.append(vNewFilamentSpineAttPtDist[vNewFilamentStatIdsDist.index(vNewFilamentStatIdsAttPosX[vNewFilamentSpineAttPtPosX.index(wNewFilamentsXYZ[wSpotsFilamentClosestDistancePointIndex[i]][0])])])

    ###########################
    #Create stats for distance along dendrite to starting point
            vSpotsStatUnits=['um']*len(vSpotPositionAllShollSpheresPerFilament)
            vSpotsStatNames=[' Distance to Starting Point']*len(vSpotPositionAllShollSpheresPerFilament)
            vNewShollSpotsPerFilament.AddStatistics(vSpotsStatNames, wCompleteShollSpotDistAlongFilamentStatWorking,
                                          vSpotsStatUnits, vSpotsStatFactors,
                                          vSpotsStatFactorName, vSpotsvIds)
    ################################
            vSpotsStatUnits=['']*len(vSpotPositionAllShollSpheresPerFilament)
            vSpotsStatNames=[' Ratio ShollDistance to Distance to Starting Point']*len(vSpotPositionAllShollSpheresPerFilament)
            vNewShollSpotsPerFilament.AddStatistics(vSpotsStatNames, [vNewStatSpotShollDistance[i]/wCompleteShollSpotDistAlongFilamentStatWorking[i] for i in range(len(vNewStatSpotShollDistance))],
                                          vSpotsStatUnits, vSpotsStatFactors,
                                          vSpotsStatFactorName, vSpotsvIds)
    ###############################################################################
    ###############################################################################
    #Calcualte Arbor Orientation Index
    #Equation:
    #    AOE = (Number of Shollpoints in vertical Quadrants -Number of Shollpoints in horizaontal Quadrants) / Total Numerb of Sholl points
    #AOE =  1  vertically aligned
    #AOE = -1  horizontally aligned
    #AOE =  0 are equal in all directions
    #     vSpotPositionAllShollSpheresPerFilamentAdjusted=[vSpotPositionAllShollSpheresPerFilament[i] - vBeginningVertexPositionXYZ
    #                                                      for i in range(len(vSpotPositionAllShollSpheresPerFilament))]

    #Use a reference frame to set the orientation space to measure from
    #Extract out the sholl position relative to the Ref Frame
    #zStatisticDendritePosX = vNewFilaments.GetStatisticsByName('Dendrite Position X Reference frame').mValues
    #zStatisticDendritePosY = vNewFilaments.GetStatisticsByName('Dendrite Position Y Reference frame').mValues
    #zStatisticDendritePosZ = vNewFilaments.GetStatisticsByName('Dendrite Position Z Reference frame').mValues




    #If refernce is set to orient the orign axis
        #Grab New Filament Spine Statistics for attachment point distance.
        # vNewShollSpotsPerFilamentStatistics = vNewSpots.GetStatistics()
        # vNewShollSpotsPerFilamentStatNames = vNewShollSpotsPerFilamentStatistics.mNames
        # vNewShollSpotsPerFilamentStatValues = vNewShollSpotsPerFilamentStatistics.mValues
        # vNewShollSpotsPerFilamentStatIds = vNewShollSpotsPerFilamentStatistics.mIds



    #Maybe something different for 3D Sholl???
    ###############################################################################




    ###############################################################################
    #Reset Spots for next filament
        vNewStatSpotNumberShollIntersections=[]
        vNewStatSpotShollDistance=[]
        vSpotPositionAllShollSpheresPerFilament=[]
        vNumberOfShollIntersectionPerSpherePerFilament=[]
    ###############################################################################
    ###############################################################################
        progress_bar2['value'] = int((aFilamentIndex+1)/vNumberOfFilaments*100) #  % out of 100
        qProgressBar.update()


    #Sholl Branching Density
    #Make series of fixed (randomly placed lines in the volume)
    #Quantify the number of Sholl Intersections with these lines
    #Report NumberIntersections/um

    #Alternative:  create convexhull around terminal points, make sure the lines
    # fall inside of the convex hull

    ###############################################################################

    qProgressBar.destroy()
    qProgressBar.mainloop()

    ##############################################################################
    #Visibility of the Scene Objects

    # elapsed = time.time() - start
    # print(elapsed)