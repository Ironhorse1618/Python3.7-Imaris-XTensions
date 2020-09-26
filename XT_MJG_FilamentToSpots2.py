#Convert Filament to Spots

# Written by Matthew J. Gastinger
# Aug 2020 - Imaris 9.6.0


#    <CustomTools>
#      <Menu>
#         <Submenu name="Surfaces Functions">
        #   <Item name="Filaments To Spots" icon="Python3">
    #         <Command>Python3XT::XT_MJG_FilamentToSpots2(%i)</Command>
    #       </Item>
         #</Submenu>
#      </Menu>
#      <SurpassTab>
#        <SurpassComponent name="bpFilaments">
    #       <Item name="Filaments To Spots" icon="Python3">
    #         <Command>Python3XT::XT_MJG_FilamentToSpots2(%i)</Command>
    #       </Item>
#        </SurpassComponent>
#      </SurpassTab>
#    </CustomTools>

#Description:
#This Xtension will take all the filament spots from dendrites and spines and
#turn them in spots.  Dendrites and spines will be put into separate objects.
#Each filamentID will will have its own Spots object

#Notes:  Filament Points will be reOrdered
#Notes:  Gaps in the Filament points will be filled
    #       New spot placed half between adjacent points and diameter set
    #        to the average of the 2 surrounding spots

# Python libraries - scipy


import numpy as np
import time
import random

# GUI imports
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from statistics import mean
from scipy.spatial.distance import pdist
from functools import reduce
from operator import add
from operator import itemgetter
import operator

import ImarisLib
#aImarisId=0
def XT_MJG_FilamentToSpots2(aImarisId):
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

    vSurfaces = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
    vSpots = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
    vFilaments = vFactory.ToFilaments(vImarisApplication.GetSurpassSelection())

    ############################################################################
    ############################################################################
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

    #Generate Surpass Scene folder locations

    #Create a new folder object for Filament to Spots
    #Generate new Factory for Surpass Scene objects
    vNewSpotsDendritesFolder = vImarisApplication.GetFactory().CreateDataContainer()
    vNewSpotsSpinesFolder =vImarisApplication.GetFactory().CreateDataContainer()
    vNewSpotsDendritesFolder.SetName('Dendrites All -' + vFilaments.GetName())
    vNewSpotsSpinesFolder.SetName('Spines All -' + vFilaments.GetName())

    #Preset variable lists
    vTotalSpotsSpineTime=[]
    wAllSegmentIds=[]
    vStatisticFilamentBoutonsPerDendrite=[]
    vFilamentCountActual=0
    wCompleteDendriteSegmentIds=[]
    wCompleteSpineSegmentIds=[]
    IsRealFilament=[]

    aFilamentIndex=0
    qIsSpines=False

    #Loop each Filament
    for aFilamentIndex in range(vNumberOfFilaments):
        vFilamentsIndexT = vFilaments.GetTimeIndex(aFilamentIndex)
        vFilamentsXYZ = vFilaments.GetPositionsXYZ(aFilamentIndex)
        vFilamentsRadius = vFilaments.GetRadii(aFilamentIndex)
    #Test if the time point has empty filament matrix or filament start
    #point and nothing more
        if len(vFilamentsRadius)==1:
            # IsRealFilament.append(False)
            #Add/Pad Filament Stat with Zeros for Filaments with no length or content
            #vFilamentIds.pop(aFilamentIndex)
            # for c in range (vSizeC):
            #     wCompleteFilamentIntMean[c].append(0)
            #     wCompleteFilamentIntCenter[c].append(0)
            continue
        vFilamentCountActual=vFilamentCountActual+1
        # IsRealFilament.append(True)

        vFilamentsEdgesSegmentId = vFilaments.GetEdgesSegmentId(aFilamentIndex)
    #Find unique values of variable using set, the copnvert back to list
        vSegmentIds=list(set(vFilamentsEdgesSegmentId))
        vNumberOfDendriteBranches = len(vSegmentIds)#total number dendrite segments
        vNumberOfFilamentPoints= len(vFilamentsRadius)#including starting point
        vFilamentTimeIndex=[vFilamentsIndexT]*len(vFilamentsRadius)#for filament spot creation
        vFilamentsEdges = vFilaments.GetEdges(aFilamentIndex)
        vTypes = vFilaments.GetTypes(aFilamentIndex)
        vBeginningVertex = vFilaments.GetBeginningVertexIndex(aFilamentIndex)

    ###############################################################################
    ###############################################################################
        vAllSegmentsPerFilamentRadiusWorkingInserts=[]
        vAllSegmentsPerFilamentPositionsWorkingInserts=[]
        vAllSegmentsTypesPerFilamentWorkingInserts=[]
        vAllSegmentIdsPerFilamentInserts=[]
        zReorderedvSegmentIds=[]
        zReorderedvSegmentType=[]
        vBranchIndex=0

    #Loop through dendrite segments, terminal segements and spine segments
        for vBranchIndex in range (vNumberOfDendriteBranches):
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

            #Collate all segmentsIds
            wAllSegmentIds.append(vSegmentIdWorking)
       #Find current Working Dendrite segment parts
            vSegmentPositionsWorking=list(itemgetter(*vEdgesUniqueWorking)(vFilamentsXYZ))
            vSegmentRadiusWorking=list(itemgetter(*vEdgesUniqueWorking)(vFilamentsRadius))
            vSegmentTypesWorking=list(itemgetter(*vEdgesUniqueWorking)(vTypes))

    ###############################################################################
    ###############################################################################
            #Reordering
            #flattten list
            zNum=reduce(operator.concat, vSegmentEdgesWorking)
            #Test for perfect edge sequence, no reordereding needed
            # sorted_list_diffs = sum(np.diff(sorted(np.unique(zNum).tolist())))
            # if sorted_list_diffs == (len(np.unique(zNum).tolist()) - 1):
            #     zReOrderedFilamentPointIndex.append(np.unique(zNum).tolist())
            #     zReOrderedFilamentPositions.extend(vSegmentPositionsWorking)
            #     continue

            #find duplicates
            zDup=[zNum[i] for i in range(len(zNum)) if not i == zNum.index(zNum[i])]
            #find individuals - start and end index
            zIndiv=list(set(zNum).difference(zDup))

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
            zReorderedvSegmentIds.extend([vSegmentIdWorking]*len(vSegmentRadiusWorking))
            zReorderedvSegmentType.extend([max(vSegmentTypesWorking)]*len(vSegmentRadiusWorking))

    ##############################################################################
    ##############################################################################

            vSegmentRadiusWorkingInserts=zReOrderedFilamentRadiusWorking[:]
            vSegmentPositionsWorkingInserts=zReOrderedFilamentPositionsWorking[:]

            for loop in range (3):#loop through 3 times
                #for i in range (len(vSegmentRadiusWorkingInserts)-1):
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
            vAllSegmentsPerFilamentRadiusWorkingInserts.extend(vSegmentRadiusWorkingInserts)
            vAllSegmentsPerFilamentPositionsWorkingInserts.extend(vSegmentPositionsWorkingInserts)
            vAllSegmentsTypesPerFilamentWorkingInserts.extend([0]*len(vSegmentRadiusWorkingInserts))
            vAllSegmentIdsPerFilamentInserts.extend([vSegmentIdWorking]*len(vSegmentRadiusWorkingInserts))

    ###############################################################################
    ###############################################################################
        vNewSpotsDendrites = vImarisApplication.GetFactory().CreateSpots()
        vNewSpotsSpines = vImarisApplication.GetFactory().CreateSpots()
        for c  in range (2): #loop twice for each filamant, 0=dendrite 1=spine, and generate a
        #find index for dendrites and spines
            vTypeIndex=[i for i,val in enumerate(vAllSegmentsTypesPerFilamentWorkingInserts) if val==c]
        #Grab all type object from Filament object
            # vDendritePositionsWorking=[vFilamentsXYZ[i] for i in vTypeIndex]
            # vDendriteRadiusWorking=[vFilamentsRadius[i] for i in vTypeIndex]
            vDendritePositionsWorking=[vAllSegmentsPerFilamentPositionsWorkingInserts[i] for i in vTypeIndex]
            vDendriteRadiusWorking=[vAllSegmentsPerFilamentRadiusWorkingInserts[i] for i in vTypeIndex]
            vDendritevTypesWorking=[vAllSegmentsTypesPerFilamentWorkingInserts[i] for i in vTypeIndex]
        #vNumberOfFilamentPoints=len(vDendriteRadiusWorking)
            vTimeIndex=[vFilamentsIndexT]*len(vDendriteRadiusWorking)

            if c==0: #Do first look for dendrites
                vNewSpotsDendrites.Set(vDendritePositionsWorking, vTimeIndex, vDendriteRadiusWorking)
                vNewSpotsDendrites.SetName(str(vFilaments.GetName())+" dendrites_ID:"+ str(vFilamentIds[vFilamentCountActual-1]))
            #vNewSpotsDendrites.SetColorRGBA(vRGBA)
                vSurpassScene.AddChild(vNewSpotsDendrites, -1)

            elif vDendritevTypesWorking!=[]:#test second loop if spines exist, if not do not make spine spots object
                vNewSpotsSpines.Set(vDendritePositionsWorking, vTimeIndex, vDendriteRadiusWorking)
                vNewSpotsSpines.SetName(str(vFilaments.GetName())+" Spines_ID:"+ str(vFilamentIds[vFilamentCountActual-1]))
            #vNewSpotsSpines.SetColorRGBA(vRGBA)
                vSurpassScene.AddChild(vNewSpotsSpines, -1)

    #Turn off the Filament Object
    vFilaments.SetVisible(0)


