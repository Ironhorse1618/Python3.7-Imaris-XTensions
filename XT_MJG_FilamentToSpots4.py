#Convert Filament to Spots

# Written by Matthew J. Gastinger
# May2025 - Imaris 10.2


#    <CustomTools>
#      <Menu>
#         <Submenu name="Surfaces Functions">
        #   <Item name="Filaments To Spots" icon="Python3">
    #         <Command>Python3XT::XT_MJG_FilamentToSpots4(%i)</Command>
    #       </Item>
         #</Submenu>
#      </Menu>
#      <SurpassTab>
#        <SurpassComponent name="bpFilaments">
    #       <Item name="Filaments To Spots" icon="Python3">
    #         <Command>Python3XT::XT_MJG_FilamentToSpots4(%i)</Command>
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
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from statistics import mean
#import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.signal import peak_widths
from scipy.spatial.distance import cdist
from scipy.spatial.distance import pdist
from functools import reduce
from operator import add
from operator import itemgetter
import operator

import ImarisLib
#aImarisId=0
def XT_MJG_FilamentToSpots4(aImarisId):
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
    
    
    ##################################################################
    ##################################################################
    qInputBox=Tk()
    qInputBox.title("Filament Points to Spots")
    qInputBox.geometry("250x95")
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
    def SmallDialog():
        global qFillFilamentPoints,qMergeFilaments
        qFillFilamentPoints = var1.get()
        qMergeFilaments = var2.get()
        qInputBox.destroy()
    
    var1 = tk.IntVar(value = 1)
    var2 = tk.IntVar(value = 0)
    tk.Label(qInputBox, text=' ').grid(row=1, column=0)
    Single=Button(qInputBox, text="Create Spots from Filament", bg='blue', fg='white',command=SmallDialog )
    Single.grid(row=2, column=0,padx=40,sticky=W)
    
    tk.Checkbutton(qInputBox, text='Fill gaps in Filament Points',
                   variable=var1, onvalue=1, offvalue=0).grid(row=3, column=0, padx=50,sticky=W)
    tk.Checkbutton(qInputBox, text='Merge Filaments',
                   variable=var2, onvalue=1, offvalue=0).grid(row=4, column=0, padx=50,sticky=W)
    
    qInputBox.mainloop()
    
    ##################################################################
    ##################################################################
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
    label_1 = tk.Label(qProgressBar, text="Filaments Processed")
    label_2 = tk.Label(qProgressBar, text="Dendrites Processing...")
    
    # Use the grid manager
    label_1.grid(row=0, column=0,pady=10)
    label_2.grid(row=1, column=0,pady=10)
    
    progress_bar1.grid(row=0, column=1)
    progress_bar2.grid(row=1, column=1)
        
    ##################################################################
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
    vAllSegmentsPerFilamentRadiusWorkingInsertsMerge=[]
    vAllSegmentsPerFilamentPositionsWorkingInsertsMerge=[]
    vAllSegmentsTypesPerFilamentWorkingInsertsMerge=[]
    
    
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
    
    ###############################################################################
    ###############################################################################
        vAllSegmentsPerFilamentRadiusWorkingInserts=[]
        vAllSegmentsPerFilamentPositionsWorkingInserts=[]
        vAllSegmentsTypesPerFilamentWorkingInserts=[]
        vAllSegmentIdsPerFilamentInserts=[]
        zReorderedvSegmentIds=[]
        zReorderedvSegmentType=[]
        vBranchIndex=0
        
        if qFillFilamentPoints == 0:
            vAllSegmentsPerFilamentRadiusWorkingInserts.extend(vFilamentsRadius)
            vAllSegmentsPerFilamentPositionsWorkingInserts.extend(vFilamentsXYZ)
            vAllSegmentsTypesPerFilamentWorkingInserts.extend(vTypes)   
        else:
        #Loop through dendrite segments, terminal segements and spine segments
            for vBranchIndex in range (vNumberOfDendriteBranches):
                zReOrderedFilamentPointIndexWorking=[]
                zReOrderedFilamentPositionsWorking=[]
                zReOrderedFilamentRadiusWorking=[]
        #Set the ID for dendrite segment
                vSegmentIdWorking = vSegmentIds[vBranchIndex]
                #Isolate all edges for the working segment
                
                # start=time.time()
                
                vSegmentWorkingPointIndex=[i for i in range(len(vFilamentsEdgesSegmentId))
                                           if vFilamentsEdgesSegmentId[i] == vSegmentIdWorking]
                        
                if len(vSegmentWorkingPointIndex)>1:
                    vSegmentEdgesWorking=list(itemgetter(*vSegmentWorkingPointIndex)(vFilamentsEdges))
                else:
                    vSegmentEdgesWorking=[x[1] for x in enumerate(vFilamentsEdges)
                                  if x[0] in vSegmentWorkingPointIndex]
        
                
                # vFilamnetEdgesNumpy=np.array(vFilamentsEdges)
                
                # test = np.take(vFilamnetEdgesNumpy, vSegmentWorkingPointIndex,0)
        
                # elapsed = time.time() - start
                # print(elapsed)   
        
                #Find unique edge indices using "set" and convert back to list
                vEdgesUniqueWorking=list(set(x for l in vSegmentEdgesWorking for x in l))
        
                #Collate all segmentsIds
                wAllSegmentIds.append(vSegmentIdWorking)
           #Find current Working Dendrite segment parts
                vSegmentPositionsWorking=list(itemgetter(*vEdgesUniqueWorking)(vFilamentsXYZ))
                vSegmentRadiusWorking=list(itemgetter(*vEdgesUniqueWorking)(vFilamentsRadius))
                vSegmentTypesWorking=list(itemgetter(*vEdgesUniqueWorking)(vTypes))
             
                # elapsed = time.time() - start
                # print(elapsed)   
             
                
             
        ###############################################################################
        ###############################################################################
                if  max(vSegmentTypesWorking) == 0 and qFillFilamentPoints == 1:
            #Reordering
            #flattten list
                    zNum=reduce(operator.concat, vSegmentEdgesWorking)
                    #find duplicates
                    zDup=[zNum[i] for i in range(len(zNum)) if not i == zNum.index(zNum[i])]
                    #find individuals - start and end index
                    zIndiv=list(set(zNum).difference(zDup))
                    
                    #loops back on different point
                    
                    if zIndiv == []:#this segments loops back to same point onto itself (no begining or end point)
                        zReOrderedFilamentPositionsWorking.append(vFilamentsXYZ[vSegmentEdgesWorking[0][0]])
                        zReOrderedFilamentRadiusWorking.append(vFilamentsRadius[vSegmentEdgesWorking[0][0]])
                        for k in range (len(vSegmentRadiusWorking)-1):
            
                            if k==0:
                                #find nested list index that contains StartIndex (5,1)--next point is (5,0)
                                #convert tuple to list
                                zEdgesNext=list(reduce(operator.concat, [(index_,sub_list.index(vSegmentEdgesWorking[0][0]))\
                                     for index_, sub_list in enumerate(vSegmentEdgesWorking)\
                                     if vSegmentEdgesWorking[0][0] in sub_list]))
            
                                #find next segment index delete previous one
                                if zEdgesNext[1]==1:
                                    zNextSegmentIndex=vSegmentEdgesWorking[zEdgesNext[0]][0]#next index in sequence
                                    vSegmentEdgesWorking.pop(zEdgesNext[0])#remove list of list
                                else:
                                    zNextSegmentIndex=vSegmentEdgesWorking[zEdgesNext[0]][1]#next index in sequence
                                    vSegmentEdgesWorking.pop(zEdgesNext[0])#remove list of list
                                #collate segment indices
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
            
                                zReOrderedFilamentPositionsWorking.append(vFilamentsXYZ[zNextSegmentIndex])
                                zReOrderedFilamentRadiusWorking.append(vFilamentsRadius[zNextSegmentIndex])              
                    else:#Terminal end or semgent between nodes
                        zStartIndex=zIndiv[0]
                        zEndIndex=zIndiv[1]
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
            
                                zReOrderedFilamentPositionsWorking.append(vFilamentsXYZ[zNextSegmentIndex])
                                zReOrderedFilamentRadiusWorking.append(vFilamentsRadius[zNextSegmentIndex])
                            
                    vSegmentRadiusWorkingInserts=zReOrderedFilamentRadiusWorking[:]
                    vSegmentPositionsWorkingInserts=zReOrderedFilamentPositionsWorking[:]   
        
        
        
        ##############################################################################
        ##############################################################################
        #fill spots in filament point gaps
        
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
         
                    vAllSegmentsPerFilamentRadiusWorkingInserts.extend(vSegmentRadiusWorkingInserts)
                    vAllSegmentsPerFilamentPositionsWorkingInserts.extend(vSegmentPositionsWorkingInserts)
                    vAllSegmentsTypesPerFilamentWorkingInserts.extend([max(vSegmentTypesWorking)]*len(vSegmentRadiusWorkingInserts))
    
                progress_bar2['value'] = int((vBranchIndex)/vNumberOfDendriteBranches*100) #  % out of 100
                qProgressBar.update()
    ###############################################################################
    ###############################################################################
    
        if qMergeFilaments == 1:
            vAllSegmentsPerFilamentRadiusWorkingInsertsMerge.extend(vAllSegmentsPerFilamentRadiusWorkingInserts)
            vAllSegmentsPerFilamentPositionsWorkingInsertsMerge.extend(vAllSegmentsPerFilamentPositionsWorkingInserts)
            if qFillFilamentPoints == 1:
                vAllSegmentsTypesPerFilamentWorkingInsertsMerge.extend([max(vAllSegmentsTypesPerFilamentWorkingInserts)]*len(vAllSegmentsPerFilamentRadiusWorkingInserts))
            else:
                vAllSegmentsTypesPerFilamentWorkingInsertsMerge.extend(vAllSegmentsTypesPerFilamentWorkingInserts)
        else:    
            vNewSpotsDendrites = vImarisApplication.GetFactory().CreateSpots()
            vNewSpotsSpines = vImarisApplication.GetFactory().CreateSpots()
            for c  in range (2): #loop twice for each filamant, 0=dendrite 1=spine, and generate a
            #find index for dendrites and spines
                vTypeIndex=[i for i,val in enumerate(vAllSegmentsTypesPerFilamentWorkingInserts) if val==c]
            #Grab all type object from Filament object
                vDendritePositionsWorking=[vAllSegmentsPerFilamentPositionsWorkingInserts[i] for i in vTypeIndex]
                vDendriteRadiusWorking=[vAllSegmentsPerFilamentRadiusWorkingInserts[i] for i in vTypeIndex]
                vDendritevTypesWorking=[vAllSegmentsTypesPerFilamentWorkingInserts[i] for i in vTypeIndex]
                vTimeIndex=[vFilamentsIndexT]*len(vDendriteRadiusWorking)
        
                if c==0: #Do first look for dendrites
                    vNewSpotsDendrites.Set(vDendritePositionsWorking, vTimeIndex, vDendriteRadiusWorking)
                    vNewSpotsDendrites.SetName(str(vFilaments.GetName())+" Dendrites_ID:"+ str(vFilamentIds[vFilamentCountActual-1]))
                #vNewSpotsDendrites.SetColorRGBA(vRGBA)
                    vSurpassScene.AddChild(vNewSpotsDendrites, -1)
        
                elif vDendritevTypesWorking!=[]:#test second loop if spines exist, if not do not make spine spots object
                    vNewSpotsSpines.Set(vDendritePositionsWorking, vTimeIndex, vDendriteRadiusWorking)
                    vNewSpotsSpines.SetName(str(vFilaments.GetName())+" Spines_ID:"+ str(vFilamentIds[vFilamentCountActual-1]))
                #vNewSpotsSpines.SetColorRGBA(vRGBA)
                    vSurpassScene.AddChild(vNewSpotsSpines, -1)
    
        progress_bar1['value'] = int((aFilamentIndex)/vNumberOfFilaments*100) #  % out of 100
        qProgressBar.update()
    
    if qMergeFilaments == 1:
        vNewSpotsDendrites = vImarisApplication.GetFactory().CreateSpots()
        vNewSpotsSpines = vImarisApplication.GetFactory().CreateSpots()
        for c  in range (2): #loop twice for each filamant, 0=dendrite 1=spine, and generate a
        #find index for dendrites and spines
            vTypeIndex=[i for i,val in enumerate(vAllSegmentsTypesPerFilamentWorkingInsertsMerge) if val==c]
        #Grab all type object from Filament object
            vDendritePositionsWorking=[vAllSegmentsPerFilamentPositionsWorkingInsertsMerge[i] for i in vTypeIndex]
            vDendriteRadiusWorking=[vAllSegmentsPerFilamentRadiusWorkingInsertsMerge[i] for i in vTypeIndex]
            vDendritevTypesWorking=[vAllSegmentsTypesPerFilamentWorkingInsertsMerge[i] for i in vTypeIndex]
            vTimeIndex=[vFilamentsIndexT]*len(vDendriteRadiusWorking)
        
            if c==0: #Do first look for dendrites
                vNewSpotsDendrites.Set(vDendritePositionsWorking, vTimeIndex, vDendriteRadiusWorking)
                vNewSpotsDendrites.SetName(str(vFilaments.GetName())+" Dendrites_All_Merged")
            #vNewSpotsDendrites.SetColorRGBA(vRGBA)
                vSurpassScene.AddChild(vNewSpotsDendrites, -1)
        
            elif vDendritevTypesWorking!=[]:#test second loop if spines exist, if not do not make spine spots object
                vNewSpotsSpines.Set(vDendritePositionsWorking, vTimeIndex, vDendriteRadiusWorking)
                vNewSpotsSpines.SetName(str(vFilaments.GetName())+" Spines_All_Merged")
            #vNewSpotsSpines.SetColorRGBA(vRGBA)
                vSurpassScene.AddChild(vNewSpotsSpines, -1)
        
    #Turn off the Filament Object
    vFilaments.SetVisible(0)
    
    qProgressBar.destroy()
    qProgressBar.mainloop()
