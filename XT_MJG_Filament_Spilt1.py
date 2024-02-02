# Filament Analysis
#
# Written by Matthew J. Gastinger
#
# Jan2024 - Imaris 10.1
#
#
    #<CustomTools>
        #<Menu>
            #<Submenu name="Filaments Functions">
                #<Item name="Filament Split 1" icon="Python3">
                    #<Command>Python3XT::XT_MJG_Filament_Split1(%i)</Command>
                #</Item>
            #</Submenu>
       #</Menu>
       #<SurpassTab>
           #<SurpassComponent name="bpFilaments">
               #<Item name="Filament Split 1" icon="Python3">
                   #<Command>Python3XT::XT_MJG_Filament_Split1(%i)</Command>
               #</SurpassComponent>
           #</SurpassTab>
    #</CustomTools>

  # Description:
    #   This XTension will find all semgents (large and small) and convert them
    #   into Filament objects.
      
    #   Purpose:  This is so that the user will be able to track the change in 
    #   the length of the segments over time.
      
    #   Usage:  
    #       ---Run Xtension
    #       ---Result will generate a new Filament object with multiple individual 
    #           filaments
    #       ---User shoud be able to "reBuild" the tracks by clicking the magic wand
    #       ---Make sure "Keep data and Process all time points is checked"
    #       ---Set tracking parameter and new Filament-segments can be tracked over time


    # NOTE: 
    #     ---In Imaris10.1, if the data is 2D the Xtension will run and filament will be generated,
    #         but the filaments will not appear.  
    #     ---To make filaments appear...
    #         1.  If you open the Imaris preferences menu, and close it
    #         2. If you open the FIJI/Options menu, and close it

#Python Dependancies:
    # numpy
    # tkinter
    # operator
    # itertools
    # statistics import mean
    # functools import reduce


import numpy as np
import time
import random
import statistics
import math
import os
import platform
# GUI imports
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog

from operator import add
from operator import itemgetter
import operator
import itertools
from itertools import chain

from statistics import mean
from functools import reduce
import collections



import ImarisLib
aImarisId=0
def XT_MJG_Filament_Split1(aImarisId):
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
    vCurrentFilamentsSurpassName=vFilaments.GetName()
    
    #Get Imaris Version
    aVersion = vImarisApplication.GetVersion()
    # aVersionValue=float(aVersion[7:11])
    aVersionValue = 10
    
    
    ############################################################################
    global Entry2, NamesSurfaces, NamesSpots,NamesFilaments
    
    NamesSurfaces=[]
    NamesSpots=[]
    NamesFilaments=[]
    NamesFilamentIndex=[]
    NamesSurfaceIndex=[]
    NamesSpotsIndex=[]
    
    vSurpassSurfaces = 0
    vSurpassSpots = 0
    vSurpassFilaments = 0
    vNumberSurpassItems=vImarisApplication.GetSurpassScene().GetNumberOfChildren()
    for vChildIndex in range(0,vNumberSurpassItems):
        vDataItem=vSurpassScene.GetChild(vChildIndex)
        IsSurface=vImarisApplication.GetFactory().IsSurfaces(vDataItem)
        IsSpot=vImarisApplication.GetFactory().IsSpots(vDataItem)
        IsFilament=vImarisApplication.GetFactory().IsFilaments(vDataItem)
        if IsSurface:
            vSurpassSurfaces = vSurpassSurfaces+1
            NamesSurfaces.append(vDataItem.GetName())
            NamesSurfaceIndex.append(vChildIndex)
        elif IsSpot:
            vSurpassSpots = vSurpassSpots+1
            NamesSpots.append(vDataItem.GetName())
            NamesSpotsIndex.append(vChildIndex)
        elif IsFilament:
            vSurpassFilaments = vSurpassFilaments+1
            NamesFilamentIndex.append(vChildIndex)
            NamesFilaments.append(vDataItem.GetName())
    
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
    vType = vImage.GetType()
    
    #Get the Current Filament Object
    vNumberOfFilaments=vFilaments.GetNumberOfFilaments()
    vFilamentIds= vFilaments.GetIds()
    
    ###############################################################################
    ###############################################################################
    #Progress Bar for Dendrites
    # Create the master object
    master = tk.Tk()
    master.title("Filament_Split")
    
    # Create a progressbar widget
    progress_bar1 = ttk.Progressbar(master, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    # And a label for it
    label_1 = tk.Label(master, text="FilamentSpilt ")
    # Use the grid manager
    label_1.grid(row=0, column=0,pady=10)
    progress_bar1.grid(row=0, column=1)
    
    
    master.geometry('270x130')
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
    progress_bar1['value'] = 0
    # progress_bar3['value'] = 0
    master.update()
    
    
    ###############################################################################
    #If filament has no size skip and modify the main list VFilamentIds
    zEmptyfilaments=[]
    for aFilamentIndex in range(vNumberOfFilaments):
        vFilamentsRadius = vFilaments.GetRadii(aFilamentIndex)
        if len(vFilamentsRadius)==1:
            zEmptyfilaments.append(int(aFilamentIndex))
    vFilamentIds=[v for i,v in enumerate(vFilamentIds) if i not in zEmptyfilaments]
    
    ###############################################################################
    ###############################################################################
    #Get Filament stats
    vAllFilamentDendriteLengthSET = vFilaments.GetStatisticsByName('Segment Length')
    vAllFilamentDendriteLength = vAllFilamentDendriteLengthSET.mValues
    vAllFilamentDendriteLengthIds = vAllFilamentDendriteLengthSET.mIds
    vAllFilamentLengthSum = vFilaments.GetStatisticsByName('Filament Length (sum)').mValues
    vAllFilamentDendriteBranchDepthSET = vFilaments.GetStatisticsByName('Segment Branch Depth')
    vAllFilamentDendriteBranchDepthIds = vAllFilamentDendriteBranchDepthSET.mIds
    vAllFilamentDendriteBranchDepth = vAllFilamentDendriteBranchDepthSET.mValues
    
    vAllFilamentSpineLengthSET = vFilaments.GetStatisticsByName('Spine Length')
    vAllFilamentSpineLength = vAllFilamentSpineLengthSET.mValues
    vAllFilamentSpineLengthIds = vAllFilamentSpineLengthSET.mIds
    
    aVersionValue = 10
    if not vAllFilamentDendriteLength:
        aVersionValue = 9
        vAllFilamentDendriteLengthSET = vFilaments.GetStatisticsByName('Dendrite Length')
        vAllFilamentDendriteLength = vAllFilamentDendriteLengthSET.mValues
        vAllFilamentDendriteLengthIds = vAllFilamentDendriteLengthSET.mIds
        vAllFilamentDendriteBranchDepthSET = vFilaments.GetStatisticsByName('Dendrite Branch Depth')
        vAllFilamentDendriteBranchDepthIds = vAllFilamentDendriteBranchDepthSET.mIds
        vAllFilamentDendriteBranchDepth = vAllFilamentDendriteBranchDepthSET.mValues
    
    vStatPtPositionXSet = vFilaments.GetStatisticsByName('Pt Position X')
    vStatPtPositionYSet = vFilaments.GetStatisticsByName('Pt Position Y')
    vStatPtPositionZSet = vFilaments.GetStatisticsByName('Pt Position Z')
    vStatPtPosition = []
    vStatPtPosition.append(vStatPtPositionXSet.mValues)
    vStatPtPosition.append(vStatPtPositionYSet.mValues)
    vStatPtPosition.append(vStatPtPositionZSet.mValues)
    vStatPtPositionFactors = vStatPtPositionXSet.mFactors
    vStatPtPositionIds =  vStatPtPositionXSet.mIds
    
    wFilamentTerminalPointsNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[3]=='Segment Terminal')[0].tolist()]
    wFilamentBranchPointsNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[3]=='Segment Branch')[0].tolist()]
    wFilamentStartingPointsNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[3]=='Segment Beginning')[0].tolist()]
    wSpineTerminalPtPositionNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[3]=='Spine Terminal')[0].tolist()]
    wSpineAttachmentPtPositionNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[3]=='Spine Attachmentf')[0].tolist()]
    
    #if not wFilamentTerminalPointsNEW.any():# == []:
    if aVersionValue == 9:
        wFilamentTerminalPointsNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[3]=='Dendrite Terminal')[0].tolist()]
        wFilamentBranchPointsNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[3]=='Dendrite Branch')[0].tolist()]
        wFilamentStartingPointsNEW = np.array(vStatPtPosition).T[np.where(np.array(vStatPtPositionFactors)[3]=='Dendrite Beginning')[0].tolist()]
    
    vFilamentCountActual=0
    vCompleteNumberofSegments = 0
    vNewFilamentsFinalPositions = []
    vNewFilamentsFinalRadius = []
    vNewFilamentsFinalType = []
    vNewFilamentsFinalTimePoint = []
    vNewNumberofPointsPerFilament = []
    vNewNumberofEdgesPerFilament = []
    vNewFilamentFinalEdges = []
    
    ###############################################################################
    ###############################################################################
    #Loop each Filament
    for aFilamentIndex in range(vNumberOfFilaments):
        vFilamentsIndexT = vFilaments.GetTimeIndex(aFilamentIndex)
        vFilamentsXYZ = vFilaments.GetPositionsXYZ(aFilamentIndex)
        vFilamentsRadius = vFilaments.GetRadii(aFilamentIndex)
        vFilamentTimepoint = vImage.GetTimePoint(vFilamentsIndexT)
    
    #Test if the time point has empty filament matrix or filament start
    #point and nothing more
        if len(vFilamentsRadius)==1:
            continue
    #count the filaments processed
        vFilamentCountActual=vFilamentCountActual+1
    
        vFilamentsEdgesSegmentId = vFilaments.GetEdgesSegmentId(aFilamentIndex)
    #Find unique values of variable using set, the copnvert back to list
        vSegmentIds=list(set(vFilamentsEdgesSegmentId))
        vNumberOfSegmentsALL = len(vSegmentIds)#total number segments (dendrites and spines)
        vCompleteNumberofSegments = vCompleteNumberofSegments + vNumberOfSegmentsALL
        vNumberOfFilamentPoints= len(vFilamentsRadius)#including starting point
        vFilamentTimeIndex=[vFilamentsIndexT]*len(vFilamentsRadius)#for filament spot creation
        vFilamentsEdges = vFilaments.GetEdges(aFilamentIndex)
        vTypes = vFilaments.GetTypes(aFilamentIndex)
        vBeginningVertex = vFilaments.GetBeginningVertexIndex(aFilamentIndex)
        if max(vTypes)==1:
            qIsSpines=True
    
    ##############################################################################
    ###############################################################################
        #Find in Branch, Terminal and starting point - in current filament
        wFilamentBranchPointsNEWCurrent = np.array(wFilamentBranchPointsNEW)[np.where((wFilamentBranchPointsNEW[:, None] == np.array(vFilamentsXYZ)).all(-1).any(-1))[0].tolist()]
        wFilamentTerminalPointsNEWCurrent = np.array(wFilamentTerminalPointsNEW)[np.where((wFilamentTerminalPointsNEW[:, None] == np.array(vFilamentsXYZ)).all(-1).any(-1))[0].tolist()]
        wFilamentStartingPointsNEWCurrent = np.array(wFilamentStartingPointsNEW)[np.where((wFilamentStartingPointsNEW[:, None] == np.array(vFilamentsXYZ)).all(-1).any(-1))[0].tolist()]
        wFilamentSpineTerminalPointsNEWCurrent = np.array(wSpineTerminalPtPositionNEW)[np.where((wSpineTerminalPtPositionNEW[:, None] == np.array(vFilamentsXYZ)).all(-1).any(-1))[0].tolist()]
        wFilamentSpineAttachmentPointsNEWCurrent = np.array(wSpineAttachmentPtPositionNEW)[np.where((wSpineAttachmentPtPositionNEW[:, None] == np.array(vFilamentsXYZ)).all(-1).any(-1))[0].tolist()]
        
    #Find matching rows for the branch points and identify the point index to delete
        wFilamentBranchPointIndex = np.argwhere(np.isin(vFilamentsXYZ, wFilamentBranchPointsNEW).all(axis=1))
        # wFilamentBranchPointIndex.flatten().tolist()
    
        zReorderedvSegmentIds =[]
        zReorderedvSegmentType = []
        
        #Add multiple filaments
        for vBranchIndex in range (vNumberOfSegmentsALL):
            zReOrderedFilamentPointIndexWorking = []
            zReOrderedFilamentPositionsWorking = []
            zReOrderedFilamentRadiusWorking = []
                  
            vSegmentIdWorking = vSegmentIds[vBranchIndex] 
            
            vSegmentWorkingPointIndex = np.where(np.array(vFilamentsEdgesSegmentId)==vSegmentIdWorking)[0].tolist()    
            if len(vSegmentWorkingPointIndex)>1:
                vSegmentEdgesWorking=list(itemgetter(*vSegmentWorkingPointIndex)(vFilamentsEdges))
            else:
                vSegmentEdgesWorking=[x[1] for x in enumerate(vFilamentsEdges)
                              if x[0] in vSegmentWorkingPointIndex]    
    
    #Find unique edge indices using "set" and convert back to list
            vEdgesUniqueWorking=list(set(x for l in vSegmentEdgesWorking for x in l))
    #Find current Working Dendrite segment parts
            vSegmentTypesWorking=list(itemgetter(*vEdgesUniqueWorking)(vTypes))
     
    #################################################################################       
    #################################################################################        
            if max(vSegmentTypesWorking)==0:# and vOptionFilamentToSpotsFill==1 or vOptionFilamentBoutonDetection==1 or vOptionFilamentCloseToSpots==1 or vOptionDendriteToDendriteContact==1 or vOptionFilamentToFilamentContact==1:
    #ReOrder segment
            #Reordering
            #flattten list
                zNum=reduce(operator.concat, vSegmentEdgesWorking)
                #find duplicates
                zDup=[zNum[i] for i in range(len(zNum)) if not i == zNum.index(zNum[i])]
                #find individuals - start and end index
                zIndiv=list(set(zNum).difference(zDup))
    
                zStartIndex=zIndiv[0]
                zEndIndex=zIndiv[1]
                zReOrderedFilamentPointIndexWorking.append(zStartIndex)
                zReOrderedFilamentPositionsWorking.append(vFilamentsXYZ[zStartIndex])
                zReOrderedFilamentRadiusWorking.append(vFilamentsRadius[zStartIndex])
                zNextPointIndex = [zIndiv[0]]
            #start of loop for each dendrite segment
                for k in range (len(vSegmentTypesWorking)-1):      
                    #find index where zStartIndex is in the WorkingEdges
                    zTestEdgeIndex = np.where(np.array(vSegmentEdgesWorking) == zNextPointIndex[0])[0].tolist()
                    #find value that is not the zStartIndex                    
                    zTestList = vSegmentEdgesWorking[zTestEdgeIndex[0]]               
                    zNextPointIndex = [i for i in zTestList if i not in zNextPointIndex]              
                    #collate new order for objects
                    zReOrderedFilamentPointIndexWorking.append(zNextPointIndex[0])
                    zReOrderedFilamentPositionsWorking.append(vFilamentsXYZ[zNextPointIndex[0]])
                    zReOrderedFilamentRadiusWorking.append(vFilamentsRadius[zNextPointIndex[0]])            
                    #Delete last edges points
                    vSegmentEdgesWorking.pop(zTestEdgeIndex[0])
    #################################################################################       
    #################################################################################
    #compile each segment as its own Filament object
            vNewFilamentsFinalPositions.extend(zReOrderedFilamentPositionsWorking)
            vNewNumberofPointsPerFilament.append(len(zReOrderedFilamentPositionsWorking))
            vNewFilamentsFinalRadius.extend(zReOrderedFilamentRadiusWorking)
            vNewFilamentsFinalType.extend(vSegmentTypesWorking)
            vNewFilamentsFinalTimePoint.extend([vFilamentTimeIndex[0]])
            vNewNumberofEdgesPerFilament.append(len(zReOrderedFilamentPositionsWorking)-1)
    #Create new edges starting at [[0,1],[1,2],[2,3], etc...] 
            x = np.arange(len(zReOrderedFilamentPositionsWorking)-1)
            y = np.arange(1,len(zReOrderedFilamentPositionsWorking),1)
            vNewSegmentEdgesWorking = np.vstack((x, y)).T.tolist()    
    #Concatonate working edges into a new Edges list for multiple Filament creation
            vNewFilamentFinalEdges.extend(vNewSegmentEdgesWorking)
                    
            progress_bar1['value'] = int((vBranchIndex+1)/vNumberOfSegmentsALL*100) #  % out of 100
            master.update()
        master.update()    
        label_1 = tk.Label(master, text=("Processing Next Filament_"+ str(aFilamentIndex)+" "))
        label_1.grid(row=0, column=0,pady=10)
        master.update()   
            
    #Create New filament for each segment        
    vNewFilament = vImarisApplication.GetFactory().CreateFilaments()
    progress_bar1['value'] = 50 #  % out of 100
    label_1 = tk.Label(master, text=("  Adding Filaments to Scene"))
    if vCompleteNumberofSegments <4000:
        label_2 = tk.Label(master, text=("~4000 filaments\n"
                                         "take minutes to add"))
        label_2.grid(row=1, column=0,pady=10)
    elif vCompleteNumberofSegments < 6000:
        label_2 = tk.Label(master, text=("~6000 filaments\n"
                                         "Please wait...\n"
                                         "may take several minutes to add"))
        label_2.grid(row=1, column=0,pady=10)
    else:
        label_2 = tk.Label(master, text=(">6000 filaments\n"
                                         "Please wait...\n"
                                         "Adding many filaments"))
        label_2.grid(row=1, column=0,pady=10)
    
        
        label_2.grid(row=1, column=0,pady=10)
    label_1.grid(row=0, column=0,pady=10)
    master.update()
    
    vNewFilament.AddFilamentsList(vNewFilamentsFinalPositions,
                             vNewNumberofPointsPerFilament,
                             vNewFilamentsFinalRadius,
                             vNewFilamentsFinalType,
                             vNewFilamentFinalEdges,
                             vNewNumberofEdgesPerFilament,
                             vNewFilamentsFinalTimePoint)  
    
    #Create new Filament object
    vNewFilamentFolder = vImarisApplication.GetFactory().CreateDataContainer()
    vNewFilamentFolder.SetName('Split Filament - '+ str(vFilaments.GetName()))                            
    vNewFilament.SetName('Split Filaments')
    vNewFilamentFolder.AddChild(vNewFilament, -1)
    vImarisApplication.GetSurpassScene().AddChild(vNewFilamentFolder, -1)
    
    if aVersion == "Imaris x64 10.1.0" and vDataSize[2]==1:
            messagebox.showerror(title='Filament 2D Display Error',
                             message='Due to new 2Dview in Imaris 10.1.0\n'
                             'These new filaments are hidden from view\n'
                             '\n'
                             'To view the New Filament objects:\n'
                             '--Open Imaris Preferences menu\n'
                             '--Then close the window\n'
                             '   NEW filaments should appear')
    
    
    
    master.destroy()

