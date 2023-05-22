#Synaptic Pairing
#
#Written by Matthew J. Gastinger
#2023
#
    # <CustomTools>
    #     <Menu>
    #         <Submenu name="Spots Functions">
    #             <Item name="Synaptic_Pairing6" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Synaptic_Pairing6(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSpots">
    #             <Item name="Synaptic Pairing6" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Synaptic_Pairing6(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #     </SurpassTab>
    # </CustomTools>

#Description
# Colocalization between 2 sets of Spots objects

# Colocalization is measured by the closet distance between spot centers
# Threshold is set by the end user in dialog box

# Each spot is paired with its colocalized partner
# A custom statistic is generated for each set of paired spots
# This custom statistic will act like a ColocID between the Spots objects

# Types of colocalization identified
# --Singlets - one spot colocalized with one spot
# --Doublets - two spots colocalized with one spot
# --Doublets Shared - 2 sets of paired spots colocalized with one spot
# --Doublets Other
# --Triplets - three spots colocalized with one spot
# --Quadruplets - four spots colocalized with one spot

#******For each category above will be paired to the second spot via a custom ID statistic


# For each above cateogry a New Label is generated
# --Non colocalized
# --Singlets
# --Doublets
# --Doublets shared
# --Doublets others
# --Triplets
# --Quadrupets

import pandas as pd
import numpy as np
import scipy
import scipy.stats
from scipy.spatial.distance import cdist
import ImarisLib


# GUI imports - builtin
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import time
from collections import OrderedDict


aImarisId=0
def XT_MJG_Synaptic_Pairing6(aImarisId):
    
    # Create an ImarisLib object
    vImarisLib = ImarisLib.ImarisLib()
    # Get an imaris object with id aImarisId
    vImarisApplication = vImarisLib.GetApplication(aImarisId)
    # Get the factory
    vFactory = vImarisApplication.GetFactory()
    # Get the currently loaded dataset
    vImage = vImarisApplication.GetDataSet()
    # Get the Surpass scene
    vScene = vImarisApplication.GetSurpassScene()
    
    ############################################################################
    ############################################################################
    #Get image properties #timepoints #channels
    #Get the extents of the image
    vExtendMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vExtendMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vImageSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    Xvoxelspacing= (vExtendMax[1]-vExtendMin[1])/vImageSize[1];
    vDefaultSmoothingFactor=round(Xvoxelspacing*2,2);
    ############################################################################
    #Count and find Surpass objects in Scene
    vNumberSurpassItems=vImarisApplication.GetSurpassScene().GetNumberOfChildren()
    NamesSurfaces=[]
    NamesSpots=[]
    NamesFilaments=[]
    NamesFilamentIndex=[]
    NamesSurfaceIndex=[]
    NamesSpotsIndex=[]
    
    vSurpassSurfaces = 0;
    vSurpassSpots = 0;
    vSurpassFilaments = 0;
    for vChildIndex in range(0,vNumberSurpassItems):
        vDataItem=vScene.GetChild(vChildIndex)
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
            NamesFilaments.append(vDataItem.GetName(),)
            NamesFilamentIndex.append(vChildIndex)
    
    #####################################################
    #Making the Listbox for the Surpass menu
    main = Tk()
    main.title("Spot Selection")
    main.geometry("+50+150")
    main.attributes("-topmost", True)
    
    #################################################################
    #Set input in center on screen
    # Gets the requested values of the height and widht.
    windowWidth = main.winfo_reqwidth()
    windowHeight = main.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(main.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(main.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    main.geometry("+{}+{}".format(positionRight, positionDown))
    ##################################################################
    names = StringVar()
    names.set(NamesSpots)
    lstbox = Listbox(main, listvariable=names, selectmode=MULTIPLE, width=20, height=10)
    lstbox.grid(column=  0, row=1, sticky=W)
    def select():
        global ObjectSelection, vDistanceThreshold
        ObjectSelection = list()
        selection = lstbox.curselection()
        vTestEntry = Entry1.get()
        try :
            float(Entry1.get())
            vDistanceThreshold = float(Entry1.get())
            if float(vTestEntry) == 0:
                messagebox.showerror(title='Threshold',
                                      message='Please set Threshold > 0')
                main.mainloop()
        except :
            messagebox.showerror(title='Threshold',
                                  message='Please set Threshold\n'
                                  'To a real number > 0' )
            main.mainloop()
    
        for i in selection:
            entrada = lstbox.get(i)
            ObjectSelection.append(entrada)
    #Test for the correct number selected
        if len(ObjectSelection)!=2:
            messagebox.showerror(title='Surface menu',
                              message='Please Select 2 Spots')
            main.mainloop()
        else:
            main.destroy()
    
    tk.Label(main, text='Select 2 Spots!').grid(row=0,column=0, sticky=W, padx=20)
    btn = Button(main, text="Analyze Coloc", command=select)
    btn.grid(column=0, row=3, sticky=W,padx=20)
    tk.Label(main, text='Distance Threshold').grid(row=4,column=0,sticky=W,padx=10)
    
    Entry1=Entry(main,justify='center',width=5)
    Entry1.grid(row=5, column=0, sticky=W,padx=50)
    Entry1.insert(0, '0.5')
    tk.Label(main, text='um').grid(row=5,column=0,sticky=W, padx=90)
    
    #Selects the top 2 items in the list
    lstbox.selection_set(0,1)
    main.mainloop()
    
    ########################################################################
    ########################################################################
    # Create the master object
    master = tk.Tk()
    # Create a progressbar widget
    qProgressBar = ttk.Progressbar(master, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    # And a label for it
    label_1 = tk.Label(master, text="Synaptic analysis")
    # Use the grid manager
    label_1.grid(row=0, column=0,pady=10)
    qProgressBar.grid(row=0, column=1)
    master.geometry('270x50')
    master.attributes("-topmost", True)
    #######################
    #Set input in center on screen
    # Gets the requested values of the height and widht.
    windowWidth = master.winfo_reqwidth()
    windowHeight = master.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(master.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(master.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    master.geometry("+{}+{}".format(positionRight, positionDown))
    #######################
    # Necessary, as the master object needs to draw the progressbar widget
    # Otherwise, it will not be visible on the screen
    master.update()
    qProgressBar['value'] = 0
    master.update()
    ########################################################################
    ########################################################################
    
    # get the Selected surfaces Indices in Surpass for specific
    vDataItem=vScene.GetChild(NamesSpotsIndex[(NamesSpots.index( ''.join(map(str, ObjectSelection[0]))))])
    vSpots1=vImarisApplication.GetFactory().ToSpots(vDataItem)
    
    vDataItem=vScene.GetChild(NamesSpotsIndex[(NamesSpots.index( ''.join(map(str, ObjectSelection[1]))))])
    vSpots2=vImarisApplication.GetFactory().ToSpots(vDataItem)
    
    ####################################################################
    # get the Selected surfaces Indices in Surpass for specific
    vSpots1PositionsXYZ = vSpots1.GetPositionsXYZ()
    vSpots1Radius = vSpots1.GetRadiiXYZ()
    vSpots1TimeIndices = vSpots1.GetIndicesT()
    vSpots1Ids = vSpots1.GetIds()
    
    vSpots2PositionsXYZ = vSpots2.GetPositionsXYZ()
    vSpots2Radius = vSpots2.GetRadiiXYZ()
    vSpots2TimeIndices = vSpots2.GetIndicesT()
    vSpots2Ids = vSpots2.GetIds()
    
    vSpots2Length = len(vSpots2Ids)
    #Create working array for Spots2
    vNewSpots2_Stats = np.zeros([vSpots2Length,14])
    vNewSpots2_Stats[:,0]=vSpots2Ids
    
    #Second Set Inverted Coloc
    vSpots1Length = len(vSpots1Ids)
    #Create working array for Spots1
    vNewSpots1_Stats = np.zeros([vSpots1Length,14])
    vNewSpots1_Stats[:,0]=vSpots1Ids
    ####################
    
    qProgressBar['value'] = 10
    master.update()
    
    #find time with a vSpots1 object
    vTimeIndicesActive=np.intersect1d(np.unique(vSpots1TimeIndices), np.unique(vSpots1TimeIndices))
    aNextTimePoint=0
    aStatStart = 1
    
    for aNextTimePoint in range(len(vTimeIndicesActive)):
        vSpots1CurrrentIds=np.array(vSpots1Ids)[np.where(vSpots1TimeIndices==vTimeIndicesActive[aNextTimePoint])[0].tolist()][:]
        vSpots2CurrrentIds=np.array(vSpots2Ids)[np.where(vSpots2TimeIndices==vTimeIndicesActive[aNextTimePoint])[0].tolist()][:]
        wSpotToSpotDistances = cdist(np.array(vSpots1PositionsXYZ)[(np.where(vSpots1TimeIndices==vTimeIndicesActive[aNextTimePoint]))[0].tolist(),:],
                                   np.array(vSpots2PositionsXYZ)[(np.where(vSpots2TimeIndices==vTimeIndicesActive[aNextTimePoint]))[0].tolist(),:])
        wSpotToSpotDistances2 = wSpotToSpotDistances.T#Second Set Inverted Coloc
    
        qProgressBar['value'] = aNextTimePoint+1/len(vTimeIndicesActive)*50
        master.update()
    
    #### X axis is Spots1,   Y axis is Spots2
        wColocSrtd_vSpots2 = np.argwhere(wSpotToSpotDistances < vDistanceThreshold)
        #inverted
        wColocSrtd_vSpots1 = np.argwhere(wSpotToSpotDistances2 < vDistanceThreshold)
    
    ####################
        #Find true doublets from the combines ones....
        vUniqueSpecial_vSpots2, vCountSpecial_vSpots2 = np.unique(wColocSrtd_vSpots2[:,1], return_counts=True, axis = 0)
        vUniqueSpecial_vSpots1, vCountSpecial_vSpots1 = np.unique(wColocSrtd_vSpots1[:,1], return_counts=True, axis = 0)
    
    ######WORKING IT OUT#######
        wLengthColocDoublets_vSpots2_Special = vUniqueSpecial_vSpots2[vCountSpecial_vSpots2 >= 2].tolist()#find vSpots1 Index that appears more than once
        wtemp1=np.where(np.isin(wColocSrtd_vSpots2[:,1],vUniqueSpecial_vSpots2[vCountSpecial_vSpots2 >= 2].tolist()))#Find wColocSrtd_vSpots2 Index where vSpots1 is multiple
        wtemp2=wColocSrtd_vSpots2[:,0][np.where(np.isin(wColocSrtd_vSpots2[:,1],vUniqueSpecial_vSpots2[vCountSpecial_vSpots2 >= 2].tolist()))[0].tolist()]#Find vSpots2 index where vSpots1 is multiple
        wtemp3=np.isin(wColocSrtd_vSpots2[:,0],wtemp2)#create Boolean array where vSpots2 Index is True
        wtemp4=np.where(wtemp3)#Find wColocSrtd_vSpots2 Indices that at not traditional Doublets or Triplets
        wtemp4=np.where(np.isin(wColocSrtd_vSpots2[:,0],wColocSrtd_vSpots2[:,0][np.where(np.isin(wColocSrtd_vSpots2[:,1],vUniqueSpecial_vSpots2[vCountSpecial_vSpots2 >= 2].tolist()))[0].tolist()]))
    
        wColocSrtdAdj_vSpots1_Temp = wColocSrtd_vSpots1
        wColocSrtdAdj_vSpots2_Temp = wColocSrtd_vSpots2
        wColocSrtdDoubletsCombined_vSpots1_Temp=np.array([])
        wColocSrtdDoubletsCombined_vSpots2_Temp=np.array([])
    
        if not np.where(np.isin(wColocSrtd_vSpots2[:,1],vUniqueSpecial_vSpots2[vCountSpecial_vSpots2 >= 2].tolist()))[0].size == 0:#Find wColocSrtd_vSpots1 Index where vSpots2 is multiple
            wColocSrtdDoubletsCombined_vSpots2_Temp = np.array([])
            wColocSrtdDoubletsCombined_vSpots2_Temp = np.take(wColocSrtd_vSpots2,np.where(np.isin(wColocSrtd_vSpots2[:,0],wColocSrtd_vSpots2[:,0][np.where(np.isin(wColocSrtd_vSpots2[:,1],vUniqueSpecial_vSpots2[vCountSpecial_vSpots2 >= 2].tolist()))[0].tolist()])), axis=0)#extracts Doublets combined
            wColocSrtdAdj_vSpots2_Temp = np.delete(wColocSrtd_vSpots2,np.where(np.isin(wColocSrtd_vSpots2[:,0],wColocSrtd_vSpots2[:,0][np.where(np.isin(wColocSrtd_vSpots2[:,1],vUniqueSpecial_vSpots2[vCountSpecial_vSpots2 >= 2].tolist()))[0].tolist()])), axis=0)#Deletes Doublets combined
    ####################
        if not np.where(np.isin(wColocSrtd_vSpots1[:,1],vUniqueSpecial_vSpots1[vCountSpecial_vSpots1 >= 2].tolist()))[0].size == 0:#Find wColocSrtd_vSpots1 Index where vSpots2 is multiple
            wColocSrtdDoubletsCombined_vSpots1_Temp = np.array([])
            wColocSrtdDoubletsCombined_vSpots1_Temp = np.take(wColocSrtd_vSpots1,np.where(np.isin(wColocSrtd_vSpots1[:,0],wColocSrtd_vSpots1[:,0][np.where(np.isin(wColocSrtd_vSpots1[:,1],vUniqueSpecial_vSpots1[vCountSpecial_vSpots1 >= 2].tolist()))[0].tolist()])), axis=0)#extracts Doublets combined
            wColocSrtdAdj_vSpots1_Temp = np.delete(wColocSrtd_vSpots1,np.where(np.isin(wColocSrtd_vSpots1[:,0],wColocSrtd_vSpots1[:,0][np.where(np.isin(wColocSrtd_vSpots1[:,1],vUniqueSpecial_vSpots1[vCountSpecial_vSpots1 >= 2].tolist()))[0].tolist()])), axis=0)#Deletes Doublets combined
    
        #Spots2 colocalized with Spots1
        vUnique0, vCount0 = np.unique(wColocSrtdAdj_vSpots2_Temp[:,0], return_counts=True, axis = 0)
        vUnique00, vCount00 = np.unique(wColocSrtdAdj_vSpots1_Temp[:,0], return_counts=True, axis = 0)
    
    ####################
        wLengthColocSingles_vSpots2 = vUnique0[vCount0 == 1].tolist()#search 1st column for individual vSpots1
        wLengthColocDoublets_vSpots2 = vUnique0[vCount0 == 2].tolist()
        wLengthColocTriplets_vSpots2 = vUnique0[vCount0 == 3].tolist()
        wLengthColocQuadruplets_vSpots2 = vUnique0[vCount0 == 4].tolist()
    
        wLengthColocSingles_vSpots1 = vUnique00[vCount00 == 1].tolist()#search 1st column for individual vSpots2
        wLengthColocDoublets_vSpots1 = vUnique00[vCount00 == 2].tolist()
        wLengthColocTriplets_vSpots1 = vUnique00[vCount00 == 3].tolist()
        wLengthColocQuadruplets_vSpots1 = vUnique00[vCount00 == 4].tolist()
    
    ####################
        wColocIndexSingles_vSpots2 = np.unique(np.nonzero(np.isin(wColocSrtdAdj_vSpots2_Temp[:,0], wLengthColocSingles_vSpots2))[0])
        wColocIndexDoublets_vSpots2 = np.unique(np.nonzero(np.isin(wColocSrtdAdj_vSpots2_Temp[:,0], wLengthColocDoublets_vSpots2))[0])
        wColocIndexTriplets_vSpots2 = np.unique(np.nonzero(np.isin(wColocSrtdAdj_vSpots2_Temp[:,0], wLengthColocTriplets_vSpots2))[0])
        wColocIndexQuadruplets_vSpots2 = np.unique(np.nonzero(np.isin(wColocSrtdAdj_vSpots2_Temp[:,0], wLengthColocQuadruplets_vSpots2))[0])
    
        wColocIndexSingles_vSpots1 = np.unique(np.nonzero(np.isin(wColocSrtdAdj_vSpots1_Temp[:,0], wLengthColocSingles_vSpots1))[0])
        wColocIndexDoublets_vSpots1 = np.unique(np.nonzero(np.isin(wColocSrtdAdj_vSpots1_Temp[:,0], wLengthColocDoublets_vSpots1))[0])
        wColocIndexTriplets_vSpots1 = np.unique(np.nonzero(np.isin(wColocSrtdAdj_vSpots1_Temp[:,0], wLengthColocTriplets_vSpots1))[0])
        wColocIndexQuadruplets_vSpots1 = np.unique(np.nonzero(np.isin(wColocSrtdAdj_vSpots1_Temp[:,0], wLengthColocQuadruplets_vSpots1))[0])
    
    ####################
    
    #Create dummy variable to add for Spot2 Single,Doublets, etc...
    #Start new stats at previous time point to get continuous numbers across time
        vStatSingles_vSpots2 = np.arange(aStatStart + max(vNewSpots2_Stats[:,1]), len(wColocIndexSingles_vSpots2) + max(vNewSpots2_Stats[:,1]+1))
        vStatDoublets_vSpots2 = np.arange(aStatStart + max(vNewSpots2_Stats[:,2]), len(wColocIndexSingles_vSpots2)/2 + max(vNewSpots2_Stats[:,2]+1))
        vStatDoublets_vSpots2 = np.repeat(vStatDoublets_vSpots2, 2)
        vStatTriplets_vSpots2 = np.arange(aStatStart + max(vNewSpots2_Stats[:,3]), len(wColocIndexSingles_vSpots2)/3 + max(vNewSpots2_Stats[:,3]+1))
        vStatTriplets_vSpots2 = np.repeat(vStatTriplets_vSpots2, 3)
        vStatQuadruplets_vSpots2 = np.arange(aStatStart + max(vNewSpots2_Stats[:,4]), len(wColocIndexSingles_vSpots2)/4 + max(vNewSpots2_Stats[:,4]+1))
        vStatQuadruplets_vSpots2 = np.repeat(vStatQuadruplets_vSpots2, 4)
    
        vStatSingles_vSpots1 = np.arange(aStatStart + max(vNewSpots2_Stats[:,1]), len(wColocIndexSingles_vSpots1) + max(vNewSpots2_Stats[:,1]+1))
        vStatDoublets_vSpots1 = np.arange(aStatStart + max(vNewSpots2_Stats[:,2]), len(wColocIndexSingles_vSpots1)/2 + max(vNewSpots2_Stats[:,2]+1))
        vStatDoublets_vSpots1 = np.repeat(vStatDoublets_vSpots1, 2)
        vStatTriplets_vSpots1 = np.arange(aStatStart + max(vNewSpots2_Stats[:,3]), len(wColocIndexSingles_vSpots1)/3 + max(vNewSpots2_Stats[:,3]+1))
        vStatTriplets_vSpots1 = np.repeat(vStatTriplets_vSpots1, 3)
        vStatQuadruplets_vSpots1 = np.arange(aStatStart + max(vNewSpots2_Stats[:,4]), len(wColocIndexSingles_vSpots1)/4 + max(vNewSpots2_Stats[:,4]+1))
        vStatQuadruplets_vSpots1 = np.repeat(vStatQuadruplets_vSpots1, 4)
    
    ####################
    ####################
        #Create list of Indices vSpots2Ids - tradtional group ---  NO special groups
        wSpots2ListSingleIds = wColocSrtdAdj_vSpots2_Temp[wColocIndexSingles_vSpots2.tolist()][:,1]#Find  all spots2Id Singles
        wSpots2ListDoubletIds = wColocSrtdAdj_vSpots2_Temp[wColocIndexDoublets_vSpots2.tolist()][:,1]#Find  all spots2Id Doublets
        wSpots2ListTripletIds = wColocSrtdAdj_vSpots2_Temp[wColocIndexTriplets_vSpots2.tolist()][:,1]#Find  all spots2Id Triplets
        wSpots2ListQuadrupletIds = wColocSrtdAdj_vSpots2_Temp[wColocIndexQuadruplets_vSpots2.tolist()][:,1]#Find  all spots2Id Quadruplets
    ####################
        #find Spots1 partner for the Spots2 SingleIds
        wSortIndex= wColocSrtdAdj_vSpots2_Temp[:,1].argsort()
        wSpots1ListSinglePairedSpots2Ids=wColocSrtdAdj_vSpots2_Temp[:,0][wSortIndex[np.searchsorted(wColocSrtdAdj_vSpots2_Temp[:,1],wSpots2ListSingleIds,sorter = wSortIndex)].tolist()]
        #find Spots1 partners for the DoubletsIds
        wSpots1ListDoubletsPairedSpots2Ids=wColocSrtdAdj_vSpots2_Temp[:,0][wSortIndex[np.searchsorted(wColocSrtdAdj_vSpots2_Temp[:,1],wSpots2ListDoubletIds,sorter = wSortIndex)].tolist()]
        #find Spots1 partners for the DoubletsIds
        wSpots1ListTripletsPairedSpots2Ids=wColocSrtdAdj_vSpots2_Temp[:,0][wSortIndex[np.searchsorted(wColocSrtdAdj_vSpots2_Temp[:,1],wSpots2ListTripletIds,sorter = wSortIndex)].tolist()]
        #find Spots1 partners for the DoubletsIds
        wSpots1ListQuadrupletsPairedSpots2Ids=wColocSrtdAdj_vSpots2_Temp[:,0][wSortIndex[np.searchsorted(wColocSrtdAdj_vSpots2_Temp[:,1],wSpots2ListQuadrupletIds,sorter = wSortIndex)].tolist()]
    
    ####################
    ####################
        #Create list of Indices vSpots1Ids
        wSpots1ListSingleIds = wColocSrtdAdj_vSpots1_Temp[wColocIndexSingles_vSpots1.tolist()][:,1]#Find  all spots1Id Singles
        wSpots1ListDoubletIds = wColocSrtdAdj_vSpots1_Temp[wColocIndexDoublets_vSpots1.tolist()][:,1]#Find  all spots1Id Doublets
        wSpots1ListTripletIds = wColocSrtdAdj_vSpots1_Temp[wColocIndexTriplets_vSpots1.tolist()][:,1]#Find  all spots1Id Triplets
        wSpots1ListQuadrupletIds = wColocSrtdAdj_vSpots1_Temp[wColocIndexQuadruplets_vSpots1.tolist()][:,1]#Find  all spots1Id Quadruplets
    ####################
        #find Spots2 partner for the SPots1 SingleIds
        wSortIndex= wColocSrtdAdj_vSpots1_Temp[:,1].argsort()
        wSpots2ListSinglePairedSpots1Ids=wColocSrtdAdj_vSpots1_Temp[:,0][wSortIndex[np.searchsorted(wColocSrtdAdj_vSpots1_Temp[:,1],wSpots1ListSingleIds,sorter = wSortIndex)].tolist()]
        #find Spots1 partners for the DoubletsIds
        wSpots2ListDoubletPairedSpots1Ids=wColocSrtdAdj_vSpots1_Temp[:,0][wSortIndex[np.searchsorted(wColocSrtdAdj_vSpots1_Temp[:,1],wSpots1ListDoubletIds,sorter = wSortIndex)].tolist()]
        #find Spots1 partners for the TripletsIds
        wSpots2ListTripletsPairedSpots1Ids=wColocSrtdAdj_vSpots1_Temp[:,0][wSortIndex[np.searchsorted(wColocSrtdAdj_vSpots1_Temp[:,1],wSpots1ListTripletIds,sorter = wSortIndex)].tolist()]
        #find Spots1 partners for the TripletsIds
        wSpots2ListQuadrupletsPairedSpots1Ids=wColocSrtdAdj_vSpots1_Temp[:,0][wSortIndex[np.searchsorted(wColocSrtdAdj_vSpots1_Temp[:,1],wSpots1ListQuadrupletIds,sorter = wSortIndex)].tolist()]
    
        qProgressBar['value'] = aNextTimePoint+1/len(vTimeIndicesActive)*60
        master.update()
    
    ##############################################################################
    ##############################################################################
    ##############################################################################
        #For Spots2
        wSpots2SpecialDoubletsIndices=np.array([])
    
        if not wColocSrtdDoubletsCombined_vSpots2_Temp.size == 0:
        #Create array of Doublets colocalizations that did not fit the norm
            vUnique33, vCount33 = np.unique(wColocSrtdDoubletsCombined_vSpots2_Temp[0][:,0], return_counts=True, axis = 0)
            vUnique44, vCount44 = np.unique(wColocSrtdDoubletsCombined_vSpots2_Temp[0][:,1], return_counts=True, axis = 0)
    
            #Find 2 vSpots1 contacting single vSpots2
            wLengthColocSpecial = vUnique33[vCount33 == 2].tolist()#find vSpots1 Index that appears more than once
            wtemp1=np.where(np.isin(wColocSrtdDoubletsCombined_vSpots2_Temp[0][:,0],wLengthColocSpecial))#Find wColocSrtd_vSpots2 Index where vSpots1 is multiple
            wtemp2=wColocSrtdDoubletsCombined_vSpots2_Temp[0][:,0][np.where(np.isin(wColocSrtdDoubletsCombined_vSpots2_Temp[0][:,0],wLengthColocSpecial))[0].tolist()]#Find vSpots2 index where vSpots1 is multiple
            wtemp3=np.isin(wColocSrtdDoubletsCombined_vSpots2_Temp[0][:,0],wtemp2)#create Boolean array where vSpots2 Index is True
            wtemp4=np.where(wtemp3)#Find wColocSrtd_vSpots2 Indices that at not traditional Doublets or Triplets
            wSpots2SpecialDoubletsIndices=wColocSrtdDoubletsCombined_vSpots2_Temp[0][:,1][wtemp4[0].tolist()]
    
            vStatDoubletsSpecial_vSpots2 = np.arange(1,len(wSpots2SpecialDoubletsIndices)/2+1)
            vStatDoubletsSpecial_vSpots2 = np.repeat(vStatDoubletsSpecial_vSpots2, 2)
    ####################
            #Find 3 vSpots1 contacting single vSpots2
            wLengthColocSpecial = vUnique33[vCount33 == 3].tolist()#find vSpots1 Index that appears more than once
            wtemp1=np.where(np.isin(wColocSrtdDoubletsCombined_vSpots2_Temp[0][:,0],wLengthColocSpecial))#Find wColocSrtd_vSpots2 Index where vSpots1 is multiple
            wtemp2=wColocSrtdDoubletsCombined_vSpots2_Temp[0][:,0][np.where(np.isin(wColocSrtdDoubletsCombined_vSpots2_Temp[0][:,0],wLengthColocSpecial))[0].tolist()]#Find vSpots2 index where vSpots1 is multiple
            wtemp3=np.isin(wColocSrtdDoubletsCombined_vSpots2_Temp[0][:,0],wtemp2)#create Boolean array where vSpots2 Index is True
            wtemp4=np.where(wtemp3)#Find wColocSrtd_vSpots2 Indices that at not traditional Doublets or Triplets
            wSpots2SpecialTripletsIndices=wColocSrtdDoubletsCombined_vSpots2_Temp[0][:,1][wtemp4[0].tolist()]
    
            vStatTripletsSpecial_vSpots2 = np.arange(1,len(wSpots2SpecialTripletsIndices)/3+1)
            vStatTripletsSpecial_vSpots2 = np.repeat(vStatTripletsSpecial_vSpots2, 3)
    
    ##############################################################################
    ##############################################################################
        #For vSpots1
        wSpots1SpecialDoubletsIndices=np.array([])
        wSpots1SpecialTripletsIndices=np.array([])
    
        if not wColocSrtdDoubletsCombined_vSpots1_Temp.size == 0:
        #Create array of Doublets colocalizations that did not fit the norm
            vUnique33, vCount33 = np.unique(wColocSrtdDoubletsCombined_vSpots1_Temp[0][:,0], return_counts=True, axis = 0)
            vUnique44, vCount44 = np.unique(wColocSrtdDoubletsCombined_vSpots1_Temp[0][:,1], return_counts=True, axis = 0)
    
            #Find 2 vSpots1 contacting single vSpots2
            wLengthColocSpecial = vUnique33[vCount33 == 2].tolist()#find vSpots1 Index that appears more than once
            wtemp1=np.where(np.isin(wColocSrtdDoubletsCombined_vSpots1_Temp[0][:,0],wLengthColocSpecial))#Find wColocSrtd_vSpots2 Index where vSpots1 is multiple
            wtemp2=wColocSrtdDoubletsCombined_vSpots1_Temp[0][:,0][np.where(np.isin(wColocSrtdDoubletsCombined_vSpots1_Temp[0][:,0],wLengthColocSpecial))[0].tolist()]#Find vSpots2 index where vSpots1 is multiple
            wtemp3=np.isin(wColocSrtdDoubletsCombined_vSpots1_Temp[0][:,0],wtemp2)#create Boolean array where vSpots2 Index is True
            wtemp4=np.where(wtemp3)#Find wColocSrtd_vSpots2 Indices that at not traditional Doublets or Triplets
            wSpots1SpecialDoubletsIndices=wColocSrtdDoubletsCombined_vSpots1_Temp[0][:,1][wtemp4[0].tolist()]
    
            vStatDoubletsSpecial_vSpots1 = np.arange(1,len(wSpots1SpecialDoubletsIndices)/2+1)
            vStatDoubletsSpecial_vSpots1 = np.repeat(vStatDoubletsSpecial_vSpots1, 2)
    ####################
            #Find 3 vSpots1 contacting single vSpots2
            wLengthColocSpecial = vUnique33[vCount33 == 3].tolist()#find vSpots1 Index that appears more than once
            wtemp1=np.where(np.isin(wColocSrtdDoubletsCombined_vSpots1_Temp[0][:,0],wLengthColocSpecial))#Find wColocSrtd_vSpots2 Index where vSpots1 is multiple
            wtemp2=wColocSrtdDoubletsCombined_vSpots1_Temp[0][:,0][np.where(np.isin(wColocSrtdDoubletsCombined_vSpots1_Temp[0][:,0],wLengthColocSpecial))[0].tolist()]#Find vSpots2 index where vSpots1 is multiple
            wtemp3=np.isin(wColocSrtdDoubletsCombined_vSpots1_Temp[0][:,0],wtemp2)#create Boolean array where vSpots2 Index is True
            wtemp4=np.where(wtemp3)#Find wColocSrtd_vSpots2 Indices that at not traditional Doublets or Triplets
            wSpots1SpecialTripletsIndices=wColocSrtdDoubletsCombined_vSpots1_Temp[0][:,1][wtemp4[0].tolist()]
    
            vStatTripletsSpecial_vSpots1 = np.arange(1,len(wSpots1SpecialTripletsIndices)/3+1)
            vStatTripletsSpecial_vSpots1 = np.repeat(vStatTripletsSpecial_vSpots1, 3)
    
        qProgressBar['value'] = aNextTimePoint+1/len(vTimeIndicesActive)*75
        master.update()
    ###############################################################################
    ##############################################################################
    #Create new statID for Singles Doublets,Triplets,Quadruplets for Spots2
    ############
        #for vSpots2 singlets
        if not wSpots1ListSingleIds.size == 0:
            
            # start = time.time()
            np.put(vNewSpots2_Stats[:,1],
                   (pd.DataFrame({'A': vSpots2Ids}).reset_index().set_index('A').loc[vSpots2CurrrentIds[wSpots2ListSingleIds]].reset_index().set_index('index').index.values).tolist(),
                   vStatSingles_vSpots2.tolist())
            # elapsed = time.time() - start
            # print('NEWpandas - '+str(elapsed))
        #Spots1 paired with Single from Spots2
            np.put(vNewSpots1_Stats[:,5],
                   (pd.DataFrame({'A': vSpots1Ids}).reset_index().set_index('A').loc[vSpots1CurrrentIds[wSpots1ListSinglePairedSpots2Ids]].reset_index().set_index('index').index.values).tolist(),
                   vStatSingles_vSpots1.tolist())
    
    ###############################################################################
    ##############################################################################
            # xAll=[4,5,46,30,55,86,57,58,10,12,44,99]
            # xCur=np.array([30,55,12,44,57])
            # xSing=np.array([4,2,1])
            
            # [x[0] for x in [np.where(xAll==i)[0].tolist() for i in xCur[xSing]]]
            # [6,9,4]#final answer is right
    
            # pd.unique(np.where(np.isin(xAll, xCur[xSing]))[0].tolist())
            # [4,6,9]#Final anserr is WRONG!!!!
    
            # df = pd.DataFrame({'A': xAll})
            # df.set_index('A').loc[[57,12,55]].reset_index()
            # #we have a winner!!!!!!
            # xResult = df.reset_index().set_index('A').loc[xCur[xSing]].reset_index().set_index('index')
            # (xResult.index.values).tolist()
    
    
            # (pd.DataFrame({'A': xAll}).reset_index().set_index('A').loc[xCur[xSing]].reset_index().set_index('index').index.values).tolist()
    
    
            # (pd.DataFrame({'A': vSpots2Ids}).reset_index().set_index('A').loc[vSpots2CurrrentIds[wSpots2ListSingleIds]].reset_index().set_index('index').index.values).tolist()
    ###############################################################################
    ##############################################################################
            
    ############
    #for vSpots2 doublets
        if not wSpots2ListDoubletIds.size==0:
            np.put(vNewSpots2_Stats[:,2],
                   (pd.DataFrame({'A': vSpots2Ids}).reset_index().set_index('A').loc[vSpots2CurrrentIds[wSpots2ListDoubletIds]].reset_index().set_index('index').index.values).tolist(),
                   vStatDoublets_vSpots2.tolist())
            #Spots1 paired with Doublets from Spots2
            #use Dict to remove duplicates and keep order
            np.put(vNewSpots1_Stats[:,6],
                   list(OrderedDict.fromkeys((pd.DataFrame({'A': vSpots1Ids}).reset_index().set_index('A').loc[vSpots1CurrrentIds[wSpots1ListDoubletsPairedSpots2Ids]].reset_index().set_index('index').index.values).tolist())),
                   pd.unique(vStatDoublets_vSpots1.tolist()).tolist())
    
    ############
    #for vSpots2 triplets
        if not wSpots2ListTripletIds.size==0:
            np.put(vNewSpots2_Stats[:,3],
                   wSpots2ListTripletIds.tolist(),
                   vStatTriplets_vSpots2.tolist())
            #Spots1 paired with Triplets from Spots2
            np.put(vNewSpots1_Stats[:,7],
                   pd.unique(wSpots1ListTripletsPairedSpots2Ids).tolist(),
                   pd.unique(vStatTriplets_vSpots1.tolist()).tolist())
    ############
    #for vSpots2 quadruplets
        if not wSpots2ListQuadrupletIds.size==0:
            np.put(vNewSpots2_Stats[:,4],
                   wSpots2ListQuadrupletIds.tolist(),
                   vStatQuadruplets_vSpots2.tolist())
            #Spots1 paired with Quadruplets from Spots2
            np.put(vNewSpots1_Stats[:,8],
                   pd.unique(wSpots1ListQuadrupletsPairedSpots2Ids).tolist(),
                   pd.unique(vStatQuadruplets_vSpots1.tolist()).tolist())
    ############
    #for Doublets- Special
        if not wSpots2SpecialDoubletsIndices.size==0:
            np.put(vNewSpots2_Stats[:,9],
                   wSpots2SpecialDoubletsIndices.tolist(),
                   vStatDoubletsSpecial_vSpots2.tolist())
    ############
    #for Triplets- Special
        if not wSpots2SpecialTripletsIndices.size==0:
            np.put(vNewSpots2_Stats[:,10],
                   wSpots2SpecialTripletsIndices.tolist(),
                   vStatTripletsSpecial_vSpots2.tolist())
    ##############################################################################
    #Create new statID for Doublets,Triplets,Quadruplets for Spots1
    #for Singles
        if not wSpots1ListSingleIds.size==0:
            vStatSingles_vSpots2 = np.arange(1,len(np.unique(wSpots2ListSingleIds).tolist())+1)
            vStatSingles_vSpots1 = np.arange(1,len(np.unique(wSpots1ListSingleIds).tolist())+1)
            np.put(vNewSpots1_Stats[:,1],
                   (pd.DataFrame({'A': vSpots1Ids}).reset_index().set_index('A').loc[vSpots1CurrrentIds[wSpots1ListSingleIds]].reset_index().set_index('index').index.values).tolist(),
                   vStatSingles_vSpots1.tolist())
            np.put(vNewSpots2_Stats[:,5],
                   (pd.DataFrame({'A': vSpots2Ids}).reset_index().set_index('A').loc[vSpots2CurrrentIds[wSpots2ListSinglePairedSpots1Ids]].reset_index().set_index('index').index.values).tolist(),
                   vStatSingles_vSpots2.tolist())
    
    ############
    #for doublets
        if not wSpots1ListDoubletIds.size==0:
            np.put(vNewSpots1_Stats[:,2],
                   (pd.DataFrame({'A': vSpots1Ids}).reset_index().set_index('A').loc[vSpots1CurrrentIds[wSpots1ListDoubletIds]].reset_index().set_index('index').index.values).tolist(),
                   vStatDoublets_vSpots1.tolist())
            np.put(vNewSpots2_Stats[:,6],
                   list(OrderedDict.fromkeys((pd.DataFrame({'A': vSpots2Ids}).reset_index().set_index('A').loc[vSpots2CurrrentIds[wSpots2ListDoubletPairedSpots1Ids]].reset_index().set_index('index').index.values).tolist())),
                   pd.unique(vStatDoublets_vSpots2.tolist()).tolist())
            
    ############
    #for triplets
        if not wSpots1ListTripletIds.size==0:
            np.put(vNewSpots1_Stats[:,3],
                   wSpots1ListTripletIds.tolist(),
                   vStatTriplets_vSpots1.tolist())
            np.put(vNewSpots2_Stats[:,7],
                   pd.unique(wSpots2ListTripletsPairedSpots1Ids).tolist(),
                   pd.unique(vStatTriplets_vSpots2.tolist()).tolist())
    ############
    #for quadruplets
        if not wSpots1ListQuadrupletIds.size==0:
            np.put(vNewSpots1_Stats[:,4],
                   wSpots1ListQuadrupletIds.tolist(),
                   vStatQuadruplets_vSpots1.tolist())
            np.put(vNewSpots2_Stats[:,8],
                   pd.unique(wSpots2ListQuadrupletsPairedSpots1Ids).tolist(),
                   pd.unique(vStatQuadruplets_vSpots2.tolist()).tolist())
    ############
    #for Doublets- Special
        if not wSpots1SpecialDoubletsIndices.size==0:
            np.put(vNewSpots1_Stats[:,9],
                   wSpots1SpecialDoubletsIndices.tolist(),
                   vStatDoubletsSpecial_vSpots1.tolist())
    ############
    #for Triplets- Special
        if not wSpots1SpecialTripletsIndices.size==0:
            np.put(vNewSpots1_Stats[:,10],
                   wSpots1SpecialTripletsIndices.tolist(),
                   vStatTripletsSpecial_vSpots1.tolist())
    ##############################################################################
    ##############################################################################
    #Identify any uncategorized spots
    # np.where(~np.any(vNewSpots1_Stats[:,1:5][:],axis=1))
    # np.where(~np.any(vNewSpots2_Stats[:,1:5][:],axis=1))
    
    # #FindIds vSpots2
    # np.array(vSpots2Ids)[np.where(~np.any(vNewSpots2_Stats[:,1:5][:],axis=1))[0]]
    # #FindIds vSpots1
    # np.array(vSpots1Ids)[np.where(~np.any(vNewSpots1_Stats[:,1:5][:],axis=1))[0]]
    
    # #Find vSpots2 Index
    # np.where(~np.any(vNewSpots2_Stats[:,1:5][:],axis=1))[0]
    # #Find vSpots1 INdex
    # np.where(~np.any(vNewSpots1_Stats[:,1:5][:],axis=1))[0]
    
    #Compare to Coloc vSpot2Ids
    #vUniqueSpecial_vSpots2 & vUniqueSpecial_vSpots1------All thresholded spots
    #Find last catagorized vSpots2 Indices
    np.intersect1d(np.where(~np.any(vNewSpots2_Stats[:,1:5][:],axis=1))[0], vUniqueSpecial_vSpots2)
    #Find last catagorized vSpots1 Indices
    np.intersect1d(np.where(~np.any(vNewSpots1_Stats[:,1:5][:],axis=1))[0], vUniqueSpecial_vSpots1)
    
    vStatSingles_vSpots2new = np.arange(max(vNewSpots2_Stats[:,1])+1,max(vNewSpots2_Stats[:,1])+1+len(np.intersect1d(np.where(~np.any(vNewSpots2_Stats[:,1:5][:],axis=1))[0], vUniqueSpecial_vSpots2)))
    np.put(vNewSpots2_Stats[:,1],
           np.intersect1d(np.where(~np.any(vNewSpots2_Stats[:,1:5][:],axis=1))[0], vUniqueSpecial_vSpots2),
           vStatSingles_vSpots2new.tolist())
    #Find closest Paired vSpots1
    # np.put(vNewSpots1_Stats[:,5],
    #        pd.unique(np.where(np.isin(vSpots1Ids, vSpots1CurrrentIds[wSpots1ListSinglePairedSpots2Ids]))[0].tolist()),
    #        vStatSingles_vSpots1.tolist())
    
    
    #################
    vStatSingles_vSpots1new = np.arange(max(vNewSpots1_Stats[:,1])+1,max(vNewSpots1_Stats[:,1])+1+len(np.intersect1d(np.where(~np.any(vNewSpots1_Stats[:,1:5][:],axis=1))[0], vUniqueSpecial_vSpots1)))
    np.put(vNewSpots1_Stats[:,1],
           np.intersect1d(np.where(~np.any(vNewSpots1_Stats[:,1:5][:],axis=1))[0], vUniqueSpecial_vSpots1),
           vStatSingles_vSpots1new.tolist())
    #Find closest Paired vSpots2
    
    
    
    
    qProgressBar['value'] = 75
    master.update()
    ##############################################################################
    ##############################################################################
    #Create new statistic for Spots2
    vSpotsStatFactors_vSpots2 = (['Spot']*vSpots2Length, [str(x) for x in [i+1 for i in vSpots2TimeIndices]] )
    vSpotsStatUnits_vSpots2 = ['']*vSpots2Length
    vSpotsStatFactors_vSpots1 = (['Spot']*vSpots1Length, [str(x) for x in [i+1 for i in vSpots1TimeIndices]] )
    vSpotsStatUnits_vSpots1=['']*vSpots1Length
    vSpotsStatFactorName = ['Category','Time']
    if np.any(wLengthColocSingles_vSpots2):
        vSpotsStatNames = [' 1_SinglesID - w/' + str(vSpots1.GetName())]*vSpots2Length
        vSpots2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,1].tolist(),
                                      vSpotsStatUnits_vSpots2, vSpotsStatFactors_vSpots2,
                                      vSpotsStatFactorName, vSpots2Ids)
        vSpotsStatNames = [' Paired_1_SinglesID - w/' + str(vSpots2.GetName())]*vSpots1Length
        vSpots1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,5].tolist(),
                                      vSpotsStatUnits_vSpots1, vSpotsStatFactors_vSpots1,
                                      vSpotsStatFactorName, vSpots1Ids)
    if np.any(wLengthColocDoublets_vSpots2):
        vSpotsStatNames = [' 2_DoubletsID - w/' + str(vSpots1.GetName())]*vSpots2Length
        vSpots2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,2].tolist(),
                                      vSpotsStatUnits_vSpots2, vSpotsStatFactors_vSpots2,
                                      vSpotsStatFactorName, vSpots2Ids)
        vSpotsStatNames = [' Paired_2_DoubletsID - w/' + str(vSpots2.GetName())]*vSpots1Length
        vSpots1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,6].tolist(),
                                      vSpotsStatUnits_vSpots1, vSpotsStatFactors_vSpots1,
                                      vSpotsStatFactorName, vSpots1Ids)
    if np.any(wLengthColocTriplets_vSpots2):
        vSpotsStatNames = [' 3_TripletsID - w/' + str(vSpots1.GetName())]*vSpots2Length
        vSpots2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,3].tolist(),
                                      vSpotsStatUnits_vSpots2, vSpotsStatFactors_vSpots2,
                                      vSpotsStatFactorName, vSpots2Ids)
        vSpotsStatNames = [' Paired_3_TripletsID - w/' + str(vSpots2.GetName())]*vSpots1Length
        vSpots1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,7].tolist(),
                                      vSpotsStatUnits_vSpots1, vSpotsStatFactors_vSpots1,
                                      vSpotsStatFactorName, vSpots1Ids)
    if np.any(wLengthColocQuadruplets_vSpots2):
        vSpotsStatNames = [' 4_QuadrupletsID - w/' + str(vSpots1.GetName())]*vSpots2Length
        vSpots2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,4].tolist(),
                                      vSpotsStatUnits_vSpots2, vSpotsStatFactors_vSpots2,
                                      vSpotsStatFactorName, vSpots2Ids)
        vSpotsStatNames = [' Paired_4_QuadrupletsID - w/' + str(vSpots2.GetName())]*vSpots1Length
        vSpots1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,8].tolist(),
                                      vSpotsStatUnits_vSpots1, vSpotsStatFactors_vSpots1,
                                      vSpotsStatFactorName, vSpots1Ids)
    if not wSpots2SpecialDoubletsIndices.size==0:
        vSpotsStatNames = [' 2_DoubletsID_Special - w/' + str(vSpots1.GetName())]*vSpots2Length
        vSpots2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,9].tolist(),
                                      vSpotsStatUnits_vSpots2, vSpotsStatFactors_vSpots2,
                                      vSpotsStatFactorName, vSpots2Ids)
    ##############################################################################
    #Create new statistic for Spots1
    if np.any(wLengthColocSingles_vSpots1):
        vSpotsStatNames = [' 1_SinglesID w/' + str(vSpots2.GetName())]*vSpots1Length
        vSpots1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,1].tolist(),
                                      vSpotsStatUnits_vSpots1, vSpotsStatFactors_vSpots1,
                                      vSpotsStatFactorName, vSpots1Ids)
        vSpotsStatNames = [' Paired_1_SinglesID - w/' + str(vSpots1.GetName())]*vSpots2Length
        vSpots2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,5].tolist(),
                                      vSpotsStatUnits_vSpots2, vSpotsStatFactors_vSpots2,
                                      vSpotsStatFactorName, vSpots2Ids)
    if np.any(wLengthColocDoublets_vSpots1):
        vSpotsStatNames = [' 2_DoubletsID w/' + str(vSpots2.GetName()) ]*vSpots1Length
        vSpots1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,2].tolist(),
                                      vSpotsStatUnits_vSpots1, vSpotsStatFactors_vSpots1,
                                      vSpotsStatFactorName, vSpots1Ids)
        vSpotsStatNames = [' Paired_2_DoubletsID - w/' + str(vSpots1.GetName())]*vSpots2Length
        vSpots2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,6].tolist(),
                                      vSpotsStatUnits_vSpots2, vSpotsStatFactors_vSpots2,
                                      vSpotsStatFactorName, vSpots2Ids)
    if np.any(wLengthColocDoublets_vSpots1):
        vSpotsStatNames = [' 3_TripletsID']*vSpots1Length
        vSpots1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,3].tolist(),
                                      vSpotsStatUnits_vSpots1, vSpotsStatFactors_vSpots1,
                                      vSpotsStatFactorName, vSpots1Ids)
        vSpotsStatNames = [' Paired_3_TripletsID - w/' + str(vSpots1.GetName())]*vSpots2Length
        vSpots2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,7].tolist(),
                                      vSpotsStatUnits_vSpots2, vSpotsStatFactors_vSpots2,
                                      vSpotsStatFactorName, vSpots2Ids)
    if np.any(wLengthColocQuadruplets_vSpots1):
        vSpotsStatNames = [' 4_QuadrupletsID']*vSpots1Length
        vSpots1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,4].tolist(),
                                      vSpotsStatUnits_vSpots1, vSpotsStatFactors_vSpots1,
                                      vSpotsStatFactorName, vSpots1Ids)
        vSpotsStatNames = [' Paired_4_QuadrupletsID - w/' + str(vSpots1.GetName())]*vSpots2Length
        vSpots2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,8].tolist(),
                                      vSpotsStatUnits_vSpots2, vSpotsStatFactors_vSpots2,
                                      vSpotsStatFactorName, vSpots2Ids)
    
    if not wSpots1SpecialDoubletsIndices.size==0:
        vSpotsStatNames = [' 2_DoubletsID_Special - w/' + str(vSpots2.GetName())]*vSpots1Length
        vSpots1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,9].tolist(),
                                      vSpotsStatUnits_vSpots1, vSpotsStatFactors_vSpots1,
                                      vSpotsStatFactorName, vSpots1Ids)
    ###############################################################################
    ###############################################################################
    #Create Labels for vSpots2
    wLabelList = []
    wLabelIndices = np.where(vNewSpots2_Stats[:,1])
    for i in range(len(wLabelIndices[0])):
        vLabelCreate = vFactory.CreateObjectLabel(vSpots2Ids[wLabelIndices[0][i]], 'Coloc', '1_Singles')
        wLabelList.append(vLabelCreate)
    vSpots2.SetLabels(wLabelList)
    #######################
    wLabelList = []
    wLabelIndices = np.where(vNewSpots2_Stats[:,2])
    for i in range(len(wLabelIndices[0])):
        vLabelCreate = vFactory.CreateObjectLabel(vSpots2Ids[wLabelIndices[0][i]], 'Coloc', '2_Doublets')
        wLabelList.append(vLabelCreate)
    vSpots2.SetLabels(wLabelList)
    #######################
    wLabelList = []
    wLabelIndices = np.where(vNewSpots2_Stats[:,3])
    for i in range(len(wLabelIndices[0])):
        vLabelCreate = vFactory.CreateObjectLabel(vSpots2Ids[wLabelIndices[0][i]], 'Coloc', '3_Triplets')
        wLabelList.append(vLabelCreate)
    vSpots2.SetLabels(wLabelList)
    #######################
    wLabelList = []
    wLabelIndices = np.where(vNewSpots2_Stats[:,4])
    for i in range(len(wLabelIndices[0])):
        vLabelCreate = vFactory.CreateObjectLabel(vSpots2Ids[wLabelIndices[0][i]], 'Coloc', '4_Quadruplets')
        wLabelList.append(vLabelCreate)
    vSpots2.SetLabels(wLabelList)
    #######################
    wLabelList = []
    #Remove first column of the vNew StatDoublets
    #Find row indices that have all zeros
    #These are the non-Coloc spots
    wLabelIndices=np.where(~np.any(vNewSpots2_Stats[:,1:5][:],axis=1))
    for i in range(len(wLabelIndices[0])):
        vLabelCreate = vFactory.CreateObjectLabel(vSpots2Ids[wLabelIndices[0][i]], 'Coloc', ' Non-Colocalized')
        wLabelList.append(vLabelCreate)
    vSpots2.SetLabels(wLabelList)
    ########################
    wLabelList = []
    wLabelIndices = wSpots2SpecialDoubletsIndices
    for i in range(len(wLabelIndices)):
        vLabelCreate = vFactory.CreateObjectLabel(vSpots2Ids[wLabelIndices[i]], 'Coloc', '2_Doublets Special')
        wLabelList.append(vLabelCreate)
    vSpots2.SetLabels(wLabelList)
    ###############################################################################
    #Create Labels for vSpots1
    wLabelList = []
    wLabelIndices = np.where(vNewSpots1_Stats[:,1])
    for i in range(len(wLabelIndices[0])):
        vLabelCreate = vFactory.CreateObjectLabel(vSpots1Ids[wLabelIndices[0][i]], 'Coloc', '1_Singles')
        wLabelList.append(vLabelCreate)
    vSpots1.SetLabels(wLabelList)
    #######################
    wLabelList = []
    wLabelIndices = np.where(vNewSpots1_Stats[:,2])
    for i in range(len(wLabelIndices[0])):
        vLabelCreate = vFactory.CreateObjectLabel(vSpots1Ids[wLabelIndices[0][i]], 'Coloc', '2_Doublets')
        wLabelList.append(vLabelCreate)
    vSpots1.SetLabels(wLabelList)
    #######################
    wLabelList = []
    wLabelIndices = np.where(vNewSpots1_Stats[:,3])
    for i in range(len(wLabelIndices[0])):
        vLabelCreate = vFactory.CreateObjectLabel(vSpots1Ids[wLabelIndices[0][i]], 'Coloc', '3_Triplets')
        wLabelList.append(vLabelCreate)
    vSpots1.SetLabels(wLabelList)
    #######################
    wLabelList = []
    wLabelIndices = np.where(vNewSpots1_Stats[:,4])
    for i in range(len(wLabelIndices[0])):
        vLabelCreate = vFactory.CreateObjectLabel(vSpots1Ids[wLabelIndices[0][i]], 'Coloc', '4_Quadruplets')
        wLabelList.append(vLabelCreate)
    vSpots1.SetLabels(wLabelList)
    #######################
    wLabelList = []
    #Remove first column of the vNew StatDoublets
    #Find row indices that have all zeros
    #These are the non-Coloc spots
    wLabelIndices=np.where(~np.any(vNewSpots1_Stats[:,1:5][:],axis=1))
    for i in range(len(wLabelIndices[0])):
        vLabelCreate = vFactory.CreateObjectLabel(vSpots1Ids[wLabelIndices[0][i]], 'Coloc', ' Non-Colocalized')
        wLabelList.append(vLabelCreate)
    vSpots1.SetLabels(wLabelList)
    #######################
    wLabelList = []
    wLabelIndices = wSpots1SpecialDoubletsIndices
    for i in range(len(wLabelIndices)):
        vLabelCreate = vFactory.CreateObjectLabel(vSpots1Ids[wLabelIndices[i]], 'Coloc', '2_Doublets Special')
        wLabelList.append(vLabelCreate)
    vSpots1.SetLabels(wLabelList)
    ###############################################################################
    ###############################################################################
    qProgressBar['value'] = 100
    master.update()
    
    vSpots1.SetName(vSpots1.GetName()+' -- Analyzed')
    vImarisApplication.GetSurpassScene().AddChild(vSpots1, -1)
    vSpots2.SetName(vSpots2.GetName()+' -- Analyzed')
    vImarisApplication.GetSurpassScene().AddChild(vSpots2, -1)
    
    #######################
    #######################
    
    master.destroy()
    master.mainloop()
    
    
    
