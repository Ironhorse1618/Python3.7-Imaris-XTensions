# Filament Analysis
#
# Written by Matthew J. Gastinger
#
# Sept 2020 - Imaris 9.6.0
#
#
    #<CustomTools>
        #<Menu>
            #<Submenu name="Filaments Functions">
                #<Item name="Filament Sholl Analysis4 beta" icon="Python3">
                    #<Command>Python3XT::XT_MJG_Filament_ShollAnalysis4_beta(%i)</Command>
                #</Item>
            #</Submenu>
       #</Menu>
       #<SurpassTab>
           #<SurpassComponent name="bpFilaments">
               #<Item name="Filament Sholl Analysis4 beta" icon="Python3">
                   #<Command>Python3XT::XT_MJG_Filament_ShollAnalysis4_beta(%i)</Command>
               #</SurpassComponent>
           #</SurpassTab>
    #</CustomTools>


# Description:
#
#This XTension finds and displays the Sholl intersections
# for each Filament that have been traced and contains a StartingPoint.  It
# will be functional for multiple filaments.

# For each sholl sphere interval that is defined by the user, the script
# identifies the dendrite segments that cross that interval at least once.
# All of the filament points in the segment are measured to the filament
# starting point.  Each intersection is identified and
# classified/reduced to a single position.  Number of Sholl intersections
# will be displayed as a Spots object for each Sholl pre-defined interval.

# A single Group folder is generated, even if multiple filaments are in the
# Filament Object.  They will be named similarly but differentiated but the
# actual Filament Index in Imaris.  This wil facilitate the export of Sholl
# intersections for mulitple filaments

# New Statistics
# 1)Distance to starting point
#    -----Path distance along dendrite to starting point
# 2)Ratio ShollDistance to Distance to Starting Point
    #-----Values range 1 to 0
        #---values closer to zero are positions much further away along the dendrite path


# This is not an exact replica of the Sholl intersections reported by the
# Filament object (built into Imaris).  The values are very similar, but the rules
# for identifying a single intersection differ slightly, especially
# around where a branch point intersects a Sholl sphere. (See Readme.doc of
# an report of comparison)

import numpy as np
import time
import random
from numpy import array

# GUI imports
# GUI imports
import tkinter as tk
from tkinter import ttk

from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
#import matplotlib.pyplot as plt
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

#aImarisId=0
def XT_MJG_Filament_ShollAnalysis4_beta(aImarisId):
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

##################################################################
##################################################################
#dialog box
InputBox = Tk()
InputBox.title("Sholl Analysis")

Label(InputBox,text="Sholl Sphere Radius:").grid(row=0, column=0)
Label(InputBox,text="Number of Sholl Spheres:").grid(row=1, column=0)

#Set InputWindows to Top level window
InputBox.attributes("-topmost", True)
InputBox.geometry("210x70")
##################################################################
def dialog():
    global vShollRadius,vNumberofSpheres
    vShollRadius=Entry1.get()
    vNumberofSpheres=Entry2.get()
    vShollRadius=int(vShollRadius)
    vNumberofSpheres=int(vNumberofSpheres)
    InputBox.destroy()

##################################################################
# Set Input Window to center of screen
# Gets the requested values of the height and widht.
windowWidth = InputBox.winfo_reqwidth()
windowHeight = InputBox.winfo_reqheight()
# Gets both half the screen width/height and window width/height
positionRight = int(InputBox.winfo_screenwidth()/2 - windowWidth/2)
positionDown = int(InputBox.winfo_screenheight()/2 - windowHeight/2)
# Positions the window in the center of the page.
InputBox.geometry("+{}+{}".format(positionRight, positionDown))
##################################################################
Entry1=Entry(InputBox,justify='center',width=10)
Entry1.grid(row=0, column=1)
Entry1.insert(0, 20)

Entry2=Entry(InputBox,justify='center',width=10)
Entry2.grid(row=1, column=1)
Entry2.insert(0, 50)

Single=Button(InputBox, text="Process Sholl Analysis", bg='blue', fg='white',command=dialog)
Single.grid(row=2, column=0)

mainloop()






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
# Insert dual progress bar one dendrite branches
# one for filaments
#Progress Bar for Dendrites
# if vNumberOfFilaments>10:
# Create the master object
master = tk.Tk()
# Create a progressbar widget
progress_bar = ttk.Progressbar(master, orient="horizontal",
                              mode="determinate", maximum=100, value=0)
progress_bar2 = ttk.Progressbar(master, orient="horizontal",
                              mode="determinate", maximum=100, value=0)
# And a label for it
label_1 = tk.Label(master, text="Filament ReOrder ")
label_2 = tk.Label(master, text="Filament Progress Bar ")
# Use the grid manager
label_1.grid(row=0, column=0,pady=10)
label_2.grid(row=1, column=0,pady=10)

progress_bar.grid(row=0, column=1)
progress_bar2.grid(row=1, column=1)

master.geometry('250x100')
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

################################################
################################################
#Create a new folder object for new Sholl Spot intersections
# vGroupFolder_ShollSpots = vImarisApplication().GetFactory()
vShollResult = vImarisApplication.GetFactory().CreateDataContainer()
vShollResult.SetName('Sholl Spheres - '+ str(vFilaments.GetName()))

vShollResult2 = vImarisApplication.GetFactory().CreateDataContainer()
vShollResult2.SetName('Filament Sholl Intersections - '+ str(vFilaments.GetName()))

################################################
################################################
vSegmentBranchLength=[]
wSegmentIdsSpine=[]
wSegmentIdsDendrite=[]
wSegmentIdsALL=[]
vSpotPositionAllShollSpheres=[]
vFilamentCountActual=0
vSpotPositionAllShollSpheresPerFilament=[]
vNumberofShollIntersections=[]
vNewStatSpotShollDistance=[]
vNewStatNumberShollIntersectionPerFilament=[]
vNewStatSpotNumberShollIntersections=[]
vNumberofIntersectionsPerShollSphere=[]
wCompleteShollSpotDistAlongFilamentStat=[]
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
        progress_bar['value'] = int((vBranchIndex+1)/vNumberOfDendriteBranches*100) #  % out of 100
        master.update()

##############################################################################
##############################################################################

#Create a normalize color basd on the number of potential Sholl spheres
    wApproxNumSpheres=round(max(wDistanceValuesMax)/vShollRadius)
    wColorList=np.linspace(.1,.9,wApproxNumSpheres)

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
#Progress through each Sholl Sphere
    for aShollIndex in range (vNumberofSpheres):
        vSpotPositionCurrentShollSphere=[]#Clears current Sholl spots
        count=0
        #Set lower and upper threshold for the Sholl Mask
        aIntensityLowerThresholdManual=aIntensityLowerThresholdManual+vShollRadius
        aIntensityUpperThresholdManual=aIntensityLowerThresholdManual+(aXvoxelSpacing*2)
        qSpotinQuestion=[]
        qNodeinQuestion=[]
        qShollSpotNodeClassify=[]

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
        vSpotPositionAllShollSpheres.extend([vSpotPositionCurrentShollSphere])
        vSpotPositionAllShollSpheresPerFilament.extend([vSpotPositionCurrentShollSphere])
        #Number of sholl intersections per filament
        vNumberofShollIntersections.append(len(vSpotPositionCurrentShollSphere[0]))
        vNewStatSpotShollDistance.extend([aIntensityLowerThresholdManual]*len(vSpotPositionAllShollSpheresPerFilament[aShollIndex]))
###############################################################################
#Create Sholl Spots for the current Sholl Sphere for current Filament
        vShollCurrentSpotRadius=[1]*len(vSpotPositionAllShollSpheresPerFilament[aShollIndex])
        vShollCurrentSpotTime=[vFilamentsIndexT]*len(vSpotPositionAllShollSpheresPerFilament[aShollIndex])
        if vShollSpotCount>0:
            #Create the a new Spots generated from teh center of Mass
            vNewSpots = vImarisApplication.GetFactory().CreateSpots()
            vNewSpots.Set(vSpotPositionAllShollSpheresPerFilament[aShollIndex],
                          [vFilamentsIndexT]*len(vSpotPositionAllShollSpheresPerFilament[aShollIndex]),
                          [1]*len(vSpotPositionAllShollSpheresPerFilament[aShollIndex]))
            vNewSpots.SetName(str(aIntensityLowerThresholdManual) +
                              ' um Sholl Sphere Filament (ID: ' +
                              str(vFilamentIds[vFilamentCountActual-1])+')')
            zRandomColor=((wColorList[aShollIndex]) * 256 * 256 * 256 )
            vNewSpots.SetColorRGBA(zRandomColor)#Set Random color
            #Add new spots to Surpass Scene
            vShollResult.AddChild(vNewSpots, -1)
            vImarisApplication.GetSurpassScene().AddChild(vShollResult, -1)

    #Number of sholl intersections per sholl sphere
        vNumberofIntersectionsPerShollSphere.append(len(vSpotPositionCurrentShollSphere))
        vNewStatSpotNumberShollIntersections.extend([vNumberofIntersectionsPerShollSphere[aShollIndex]]*vNumberofIntersectionsPerShollSphere[aShollIndex])

#Reset stat for next Sholl Sphere
        vSpotPositionCurrentShollSphere=[]
        vShollSpotTime=[]
        vShollSpotRadius=[]
        vShollSpotCount=0
        vDendriteALLXSphere=[]
    #after the last sholl sphere
    vNewStatNumberShollIntersectionPerFilament.append(sum(vNumberofShollIntersections))
    vNumberofShollIntersections=[]
    vNumberofIntersectionsPerShollSphere=[]
###############################################################################
#Create Sholl Spots object for each filament with new stats
    vNewShollSpotsPerFilament = vImarisApplication.GetFactory().CreateSpots()
    #may need to flatten spot list of lists
    vSpotPositionAllShollSpheresPerFilament = [num for elem in vSpotPositionAllShollSpheresPerFilament for num in elem]


    vNewShollSpotsPerFilament.Set(vSpotPositionAllShollSpheresPerFilament,
                          [vFilamentsIndexT]*len(vSpotPositionAllShollSpheresPerFilament),
                          [1]*len(vSpotPositionAllShollSpheresPerFilament))
    vNewShollSpotsPerFilament.SetName(' All Sholl Intersections Filament (ID: ' +
                              str(vFilamentIds[vFilamentCountActual-1])+')')
    zRandomColor=(random.uniform(0, 1) * 256 * 256 * 256 )
    vNewShollSpotsPerFilament.SetColorRGBA(zRandomColor)#Set Random color
    vShollResult2.AddChild(vNewShollSpotsPerFilament, -1)
    vImarisApplication.GetSurpassScene().AddChild(vShollResult2, -1)

    #############################################################
    #Add new stats
    vSpotsTimeIndex=[vFilamentsIndexT+1]*len(vSpotPositionAllShollSpheresPerFilament)
    vSpotsvIds=list(range(len(vSpotPositionAllShollSpheresPerFilament)))
    vSpotsStatUnits=['um']*len(vSpotPositionAllShollSpheresPerFilament)
    vSpotsStatFactors=(['Spot']*len(vSpotPositionAllShollSpheresPerFilament), [str(x) for x in vSpotsTimeIndex] )
    vSpotsStatFactorName=['Category','Time']
    ###########################
    vSpotsStatNames=[' Sholl Sphere Distance']*len(vSpotPositionAllShollSpheresPerFilament)
    vNewShollSpotsPerFilament.AddStatistics(vSpotsStatNames, vNewStatSpotShollDistance,
                                  vSpotsStatUnits, vSpotsStatFactors,
                                  vSpotsStatFactorName, vSpotsvIds)
    ###########################
    vSpotsStatUnits=['']*len(vSpotPositionAllShollSpheresPerFilament)
    vSpotsStatNames=[' Number of Intersections']*len(vSpotPositionAllShollSpheresPerFilament)
    vNewShollSpotsPerFilament.AddStatistics(vSpotsStatNames, vNewStatSpotNumberShollIntersections,
                                  vSpotsStatUnits, vSpotsStatFactors,
                                  vSpotsStatFactorName, vSpotsvIds)
###############################################################################
###############################################################################
#Calculate sholl intersection distance on dendrite to starting point
###############################################################################
# #Find Spot close to filament and measure distance along path to starting point
# #Make spot position conect to filament as spine attachment point
    # if vOptionShollIntersectionDistanceAlongFilament==1:

    if vSpotPositionAllShollSpheresPerFilament!=[]:
        # for i in range (len(vSpotPositionAllShollSpheresPerFilament)):
        #     wNewSpotsOnFilament.append(vSpotsColocPositionsWorking[wSpotsAllIndexPerFilament[i]])
        #     wNewSpotsOnFilamentAll.append(vSpotsColocPositionsWorking[wSpotsAllIndexPerFilament[i]])
        #     wNewSpotsOnFilamentRadius.append(vSpotsColocRadiusWorking[wSpotsAllIndexPerFilament[i]])

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
                    wSpotNearest = wSpotNearest - vFilamentsRadius -[max(vSpotsColocRadiusWorking[0])]*len(vFilamentsRadius)
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
#    Number of Shollpoints in vertical Quadrants -Number of Shollpoints in horizaontal Quadrants / Total Numerb of Sholl points
#AOE= 1 are vertically aligned
#AOE=-1 are horizontally aligned
# #AOE=0 are equal in all directions
#     vSpotPositionAllShollSpheresPerFilamentAdjusted=[vSpotPositionAllShollSpheresPerFilament[i] - vBeginningVertexPositionXYZ
#                                                      for i in range(len(vSpotPositionAllShollSpheresPerFilament))]

    ImageMin=[vDataMin[0],vDataMin[1],vDataMin[2]]
    ImageMax=[vDataMax[0],vDataMax[1],vDataMax[2]]


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
###############################################################################
###############################################################################
    progress_bar2['value'] = int((aFilamentIndex+1)/vNumberOfFilaments*100) #  % out of 100
    master.update()






#Sholl Branching Density
#Make series of fixed (randomly placed lines in the volume)
#Quantify the number of Sholl Intersections with these lines
#Report NumberIntersections/um

#Alternative:  create convexhull around terminal points, make sure the lines
# fall inside of the convex hull

###############################################################################



master.destroy()
master.mainloop()