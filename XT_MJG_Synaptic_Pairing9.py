#Synaptic Pairing
#
#Written by Matthew J. Gastinger
#2023
#
    # <CustomTools>
    #     <Menu>
    #         <Submenu name="Spots Functions">
    #             <Item name="Synaptic_Pairing_9" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Synaptic_Pairing9(%i)</Command>
    #             </Item>
    #         </Submenu>
    #         <Submenu name="Surfaces Functions">
    #             <Item name="Synaptic_Pairing_9" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Synaptic_Pairing9(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSpots">
    #             <Item name="Synaptic Pairing9" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Synaptic_Pairing9(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #         <SurpassComponent name="bpSurfaces">
    #             <Item name="Synaptic Pairing9" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Synaptic_Pairing9(%i)</Command>
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



#####################################################
# FOR SURFACES
#Convert surfaces to spots (faster)
#adjust the distance to distance measures
#by the mean X and Y AxisAlignedBoundingBox Radius for each surface
#Threshold for "contact event is '0'
#Stats/labels the same as SPots calculation, just applied to surface objects



#Surface Overlap (much slower)
# We generate maskId for each surface object in both Objects
#---this process could take a litle time depending on the number of surfaces in each Surpass object
#
# Colocalization will be determined by whether the surface masks have at least
# one pixel of overlap.

# Label generate for each of the classifications below.
# --singlets
# --doublets
# --triplets
# --quadruplets


# ---An option to "dilate" the parent surface to "look" for coloc may be an option
#Does not EXIST YET


# For each above cateogry a New Label is generated
# --Non colocalized
# --Singlets
# --Doublets
# --Doublets shared
# --Doublets others
# --Triplets
# --Quadrupets

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
def XT_MJG_Synaptic_Pairing9(aImarisId):
    
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
    
    vSurpassObject = vImarisApplication.GetSurpassSelection()
    qIsSurface = vImarisApplication.GetFactory().IsSurfaces(vSurpassObject)
    qIsSpot = vImarisApplication.GetFactory().IsSpots(vSurpassObject)
    
    ############################################################################
    ############################################################################
    #Get image properties #timepoints #channels
    #Get the extents of the image
    vDataMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vDataMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vDataSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    Xvoxelspacing= (vDataMax[1]-vDataMin[1])/vDataSize[1];
    vDefaultSmoothingFactor=round(Xvoxelspacing*2,2);
    ############################################################################
    #Count and find Surpass objects in Scene
    vNumberSurpassItems=vImarisApplication.GetSurpassScene().GetNumberOfChildren()
    NamesSurfaces=[]
    NamesSpots=[]
    NamesFilaments=[]
    NamesFilamentIndex=[]
    NamesSurfacesIndex=[]
    NamesSpotsIndex=[]
    
    vSurpassSurfaces = 0
    vSurpassSpots = 0
    vSurpassFilaments = 0
    for vChildIndex in range(0,vNumberSurpassItems):
        vDataItem=vScene.GetChild(vChildIndex)
        IsSurface=vImarisApplication.GetFactory().IsSurfaces(vDataItem)
        IsSpot=vImarisApplication.GetFactory().IsSpots(vDataItem)
        IsFilament=vImarisApplication.GetFactory().IsFilaments(vDataItem)
        if IsSurface:
            vSurpassSurfaces = vSurpassSurfaces+1
            NamesSurfaces.append(vDataItem.GetName())
            NamesSurfacesIndex.append(vChildIndex)
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
    main.title("Surpass Object Selection")
    main.geometry("+50+180")
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
    
    if qIsSpot:
        names.set(NamesSpots)
    if qIsSurface:
        names.set(NamesSurfaces)
    
    lstbox = Listbox(main, listvariable=names, selectmode=MULTIPLE, width=20, height=10)
    lstbox.grid(column=  0, row=1, sticky=W)
    def select():
        global ObjectSelection, vDistanceThreshold,vOptionSurfaceSurfaceOverlap
        vOptionSurfaceSurfaceOverlap=var1.get()
    
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
    
    var1 = tk.IntVar(value=0)#Use surface-surface overlap
    
    tk.Label(main, text='Select 2 Surpass Objects!').grid(row=0,column=0, sticky=W, padx=20)
    btn = Button(main, text="Analyze Coloc", command=select)
    btn.grid(column=0, row=3, sticky=W,padx=20)
    tk.Label(main, text='Distance Threshold').grid(row=4,column=0,sticky=W,padx=10)
    
    Entry1=Entry(main,justify='center',width=5)
    Entry1.grid(row=5, column=0, sticky=W,padx=50)
    Entry1.insert(0, '1.5')
    tk.Label(main, text='um').grid(row=5,column=0,sticky=W, padx=90)
    
    tk.Checkbutton(main, text='Surface Overlap (much slower)',
                    variable=var1, onvalue=1, offvalue=0).grid(row=6, column=0, padx=20,sticky=W)
    
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
    if qIsSurface and vOptionSurfaceSurfaceOverlap == 0:
        vDistanceThreshold = 0
        vDataItem=vScene.GetChild(NamesSurfacesIndex[(NamesSurfaces.index( ''.join(map(str, ObjectSelection[0]))))])
        vObjects1=vImarisApplication.GetFactory().ToSurfaces(vDataItem)
    
        vDataItem=vScene.GetChild(NamesSurfacesIndex[(NamesSurfaces.index( ''.join(map(str, ObjectSelection[1]))))])
        vObjects2=vImarisApplication.GetFactory().ToSurfaces(vDataItem)
    
        vNumberOfSurfaces1 = vObjects1.GetNumberOfSurfaces()
        vNumberOfSurfaces2 = vObjects2.GetNumberOfSurfaces()
        vSurfaces1Ids = vObjects1.GetIds()
        vSurfaces2Ids = vObjects2.GetIds()
    
        vObjects1TimeIndices = np.array(vObjects1.GetStatisticsByName('Time Index').mValues).tolist()
        vObjects2TimeIndices = np.array(vObjects2.GetStatisticsByName('Time Index').mValues).tolist()
        vObjects1Ids = np.array(vObjects1.GetStatisticsByName('BoundingBoxAA Length X').mIds).tolist()
        vObjects2Ids = np.array(vObjects2.GetStatisticsByName('BoundingBoxAA Length X').mIds).tolist()
    
        vSurfaces1DiameterX = np.array(vObjects1.GetStatisticsByName('BoundingBoxAA Length X').mValues)
        vSurfaces1DiameterY = np.array(vObjects1.GetStatisticsByName('BoundingBoxAA Length Y').mValues)
        vSurfaces2DiameterX = np.array(vObjects2.GetStatisticsByName('BoundingBoxAA Length X').mValues)
        vSurfaces2DiameterY = np.array(vObjects2.GetStatisticsByName('BoundingBoxAA Length Y').mValues)
        vObjects1Radius = ((vSurfaces1DiameterX+vSurfaces1DiameterY)/2)/2
        vObjects2Radius = ((vSurfaces2DiameterX+vSurfaces2DiameterY)/2)/2
    
        vSurfaces1XPos = np.array(vObjects1.GetStatisticsByName('Position X').mValues)
        vSurfaces1YPos = np.array(vObjects1.GetStatisticsByName('Position Y').mValues)
        vSurfaces1ZPos = np.array(vObjects1.GetStatisticsByName('Position Z').mValues)
        vSurfaces2XPos = np.array(vObjects2.GetStatisticsByName('Position X').mValues)
        vSurfaces2YPos = np.array(vObjects2.GetStatisticsByName('Position Y').mValues)
        vSurfaces2ZPos = np.array(vObjects2.GetStatisticsByName('Position Z').mValues)
    
        vObjects1PositionsXYZ = np.vstack((vSurfaces1XPos,
                                         vSurfaces1YPos,
                                         vSurfaces1ZPos)).T
    
        vObjects2PositionsXYZ = np.vstack((vSurfaces2XPos,
                                         vSurfaces2YPos,
                                         vSurfaces2ZPos)).T
    
    ########################################################################
    ########################################################################
    if qIsSpot and vOptionSurfaceSurfaceOverlap == 0:
        # get the Selected surfaces Indices in Surpass for specific
        vDataItem=vScene.GetChild(NamesSpotsIndex[(NamesSpots.index( ''.join(map(str, ObjectSelection[0]))))])
        vObjects1=vImarisApplication.GetFactory().ToSpots(vDataItem)
    
        vDataItem=vScene.GetChild(NamesSpotsIndex[(NamesSpots.index( ''.join(map(str, ObjectSelection[1]))))])
        vObjects2=vImarisApplication.GetFactory().ToSpots(vDataItem)
    
        ####################################################################
        # get the Selected surfaces Indices in Surpass for specific
        vObjects1PositionsXYZ = vObjects1.GetPositionsXYZ()
        vObjects1Radius = vObjects1.GetRadiiXYZ()
        vObjects1TimeIndices = vObjects1.GetIndicesT()
        vObjects1Ids = vObjects1.GetIds()
    
        vObjects2PositionsXYZ = vObjects2.GetPositionsXYZ()
        vObjects2Radius = vObjects2.GetRadiiXYZ()
        vObjects2TimeIndices = vObjects2.GetIndicesT()
        vObjects2Ids = vObjects2.GetIds()
    
    ########################################################################
    ########################################################################
    if vOptionSurfaceSurfaceOverlap == 0:
        vObjects2Length = len(vObjects2Ids)
        #Create working array for Spots2
        vNewSpots2_Stats = np.zeros([vObjects2Length,14])
        vNewSpots2_Stats[:,0]=vObjects2Ids
    
        #Second Set Inverted Coloc
        vObjects1Length = len(vObjects1Ids)
        #Create working array for Spots1
        vNewSpots1_Stats = np.zeros([vObjects1Length,14])
        vNewSpots1_Stats[:,0]=vObjects1Ids
    ####################
    
        qProgressBar['value'] = 10
        master.update()
    
        #find time with a vObjects1 object
        vTimeIndicesActive=np.intersect1d(np.unique(vObjects1TimeIndices), np.unique(vObjects2TimeIndices))
        aNextTimePoint=0
        aStatStart = 1
        wCountSpecialsDoubles = 0
        wCountSpecialsDoubles2 = 0
        
        for aNextTimePoint in range(len(vTimeIndicesActive)):
            vObjects1CurrrentIds=np.array(vObjects1Ids)[np.where(vObjects1TimeIndices==vTimeIndicesActive[aNextTimePoint])[0].tolist()][:]
            vObjects2CurrrentIds=np.array(vObjects2Ids)[np.where(vObjects2TimeIndices==vTimeIndicesActive[aNextTimePoint])[0].tolist()][:]
            if qIsSpot:
                wSpotToSpotDistances = cdist(np.array(vObjects1PositionsXYZ)[(np.where(vObjects1TimeIndices==vTimeIndicesActive[aNextTimePoint]))[0].tolist(),:],
                                      np.array(vObjects2PositionsXYZ)[(np.where(vObjects2TimeIndices==vTimeIndicesActive[aNextTimePoint]))[0].tolist(),:])
            else:
                wSpotToSpotDistances = cdist(np.array(vObjects1PositionsXYZ)[(np.where(vObjects1TimeIndices==vTimeIndicesActive[aNextTimePoint]))[0].tolist(),:],
                                      np.array(vObjects2PositionsXYZ)[(np.where(vObjects2TimeIndices==vTimeIndicesActive[aNextTimePoint]))[0].tolist(),:])
                #Subtract mean BoundingBox Radius from each surface from each measure
                wSpotToSpotDistances = wSpotToSpotDistances - vObjects1Radius[:,None]
                wSpotToSpotDistances = wSpotToSpotDistances - vObjects2Radius[None,:]
    
            wSpotToSpotDistances2 = wSpotToSpotDistances.T#Second Set Inverted Coloc
            qProgressBar['value'] = aNextTimePoint+1/len(vTimeIndicesActive)*50
            master.update()
    
        #### X axis is Spots1,   Y axis is Spots2
            wColocSrtd = np.argwhere(wSpotToSpotDistances < vDistanceThreshold)
    
        ####################
            #Find true doublets from the combines ones....
            #Finds index for the unique objects that are coloc with at least 1 colocspot
    
            #Unique Index for vObject2 that coloc with VObjects1
            vUniqueSpecial_vObjects1, vCountSpecial_vObjects1 = np.unique(wColocSrtd[:,0], return_counts=True, axis = 0)
            #Unique Index for vObject1 that coloc with VObjects2
            vUniqueSpecial_vObjects2, vCountSpecial_vObjects2 = np.unique(wColocSrtd[:,1], return_counts=True, axis = 0)
    
    ##################
            #Find colocated spots that do not fit the norm
            #For example one Obj2 that is a part of a singlet and doublet
            #wColocSrtd indices where Objects2 is a doublet or more
            #Objects2 indices where Object1 is doublet or more
            wTemp1=wColocSrtd[np.where(np.isin(wColocSrtd[:,0],vUniqueSpecial_vObjects1[vCountSpecial_vObjects1 >= 2].tolist()))[0].tolist()]
            wTemp2=wColocSrtd[np.where(np.isin(wColocSrtd[:,0],vUniqueSpecial_vObjects1[vCountSpecial_vObjects1 == 1].tolist()))[0].tolist()]
            #Find Objects2 Indices that overlaps with doublet indices
            wTempOverlap_Obj1 = np.where(np.isin(wColocSrtd[:,0],np.intersect1d(wTemp1[:,0],wTemp2[:,0]).tolist()))
            wTempOverlap_Obj2 = np.where(np.isin(wColocSrtd[:,1],np.intersect1d(wTemp1[:,1],wTemp2[:,1]).tolist()))
    
            #Find Objects1 Specials
            wObjectsSpecials = []
            wObjectsSpecials.extend(wTempOverlap_Obj1[0].tolist())
            wObjectsSpecials.extend(wTempOverlap_Obj2[0].tolist())
    #####################################
            #Objects1 indices where Objects2 is doublet or more
            wTemp1=wColocSrtd[np.where(np.isin(wColocSrtd[:,1],vUniqueSpecial_vObjects2[vCountSpecial_vObjects2 >= 2].tolist()))[0].tolist()]
            #objects1 indices where red is a single
            wTemp2=wColocSrtd[np.where(np.isin(wColocSrtd[:,1],vUniqueSpecial_vObjects2[vCountSpecial_vObjects2 == 1].tolist()))[0].tolist()]
            #Find Objects2 Indices that overlaps with doublet indices
            wTempOverlap_Obj1 = np.where(np.isin(wColocSrtd[:,0],np.intersect1d(wTemp1[:,0],wTemp2[:,0]).tolist()))
            wTempOverlap_Obj2 = np.where(np.isin(wColocSrtd[:,1],np.intersect1d(wTemp1[:,1],wTemp2[:,1]).tolist()))
            #Find Objects1 Specials
            wObjectsSpecials.extend(wTempOverlap_Obj1[0].tolist())
            wObjectsSpecials.extend(wTempOverlap_Obj2[0].tolist())
    ###########
            #Duplicate wColocsortd
            wColocSrtdAdj = np.copy(wColocSrtd)
            #If special combos, delete from main list of coloc spots
            if wObjectsSpecials:
                # wColocSrtdAdj = np.delete(wColocSrtdAdj,(np.where(np.isin(wColocSrtd[:,0],wObjects1Specials))[0].tolist()),axis=0)
                wColocSrtdAdj = np.delete(wColocSrtdAdj, [np.unique(wObjectsSpecials)],0)
                wColocSrtdSpecials = wColocSrtd[np.unique(wObjectsSpecials)]
    
            #Spots2 colocalized with Spots1
            vUnique0, vCount0 = np.unique(wColocSrtdAdj[:,1], return_counts=True, axis = 0)
            vUnique00, vCount00 = np.unique(wColocSrtdAdj[:,0], return_counts=True, axis = 0)
    
    ####################
            wLengthColocSingles_vObjects1 = vUnique0[vCount0 == 1].tolist()#search 1st column for individual vObjects1
            wLengthColocDoublets_vObjects1 = vUnique0[vCount0 == 2].tolist()
            wLengthColocTriplets_vObjects1 = vUnique0[vCount0 == 3].tolist()
            wLengthColocQuadruplets_vObjects1 = vUnique0[vCount0 == 4].tolist()
    
            wLengthColocSingles_vObjects2 = vUnique00[vCount00 == 1].tolist()#search 1st column for individual vObjects2
            wLengthColocDoublets_vObjects2 = vUnique00[vCount00 == 2].tolist()
            wLengthColocTriplets_vObjects2 = vUnique00[vCount00 == 3].tolist()
            wLengthColocQuadruplets_vObjects2 = vUnique00[vCount00 == 4].tolist()
    
    ####################
            wColocIndexSingles_vObjects2 = np.unique(np.nonzero(np.isin(wColocSrtdAdj[:,0], wLengthColocSingles_vObjects2))[0])
            wColocIndexDoublets_vObjects2 = np.unique(np.nonzero(np.isin(wColocSrtdAdj[:,0], wLengthColocDoublets_vObjects2))[0])
            wColocIndexTriplets_vObjects2 = np.unique(np.nonzero(np.isin(wColocSrtdAdj[:,0], wLengthColocTriplets_vObjects2))[0])
            wColocIndexQuadruplets_vObjects2 = np.unique(np.nonzero(np.isin(wColocSrtdAdj[:,0], wLengthColocQuadruplets_vObjects2))[0])
    
            wColocIndexSingles_vObjects1 = np.unique(np.nonzero(np.isin(wColocSrtdAdj[:,1], wLengthColocSingles_vObjects1))[0])
            wColocIndexDoublets_vObjects1 = np.unique(np.nonzero(np.isin(wColocSrtdAdj[:,1], wLengthColocDoublets_vObjects1))[0])
            wColocIndexTriplets_vObjects1 = np.unique(np.nonzero(np.isin(wColocSrtdAdj[:,1], wLengthColocTriplets_vObjects1))[0])
            wColocIndexQuadruplets_vObjects1 = np.unique(np.nonzero(np.isin(wColocSrtdAdj[:,1], wLengthColocQuadruplets_vObjects1))[0])
    
    #############
            # wTest = wColocSrtdAdj[wColocIndexSingles_vObjects2]
            # wColocSrtdAdj[wColocIndexDoublets_vObjects2]
            # wColocSrtdAdj[wColocIndexTriplets_vObjects2]
            # wColocSrtdAdj[wColocIndexQuadruplets_vObjects2]
    
            #Reorder by first column by increasing value to organize the doublets, triplets, quadruplets
            # wColocSrtdAdj[wColocIndexSingles_vObjects2][wColocSrtdAdj[wColocIndexSingles_vObjects2][:, 0].argsort()]
            # wColocSrtdAdj[wColocIndexDoublets_vObjects2][wColocSrtdAdj[wColocIndexDoublets_vObjects2][:, 0].argsort()]
            # wColocSrtdAdj[wColocIndexTriplets_vObjects2][wColocSrtdAdj[wColocIndexTriplets_vObjects2][:, 0].argsort()]
            # wColocSrtdAdj[wColocIndexQuadruplets_vObjects2][wColocSrtdAdj[wColocIndexQuadruplets_vObjects2][:, 0].argsort()]
    
            # wColocSrtdAdj[wColocIndexSingles_vObjects1][wColocSrtdAdj[wColocIndexSingles_vObjects1][:, 1].argsort()]
            # wColocSrtdAdj[wColocIndexDoublets_vObjects1][wColocSrtdAdj[wColocIndexDoublets_vObjects1][:, 1].argsort()]
            # wColocSrtdAdj[wColocIndexTriplets_vObjects1][wColocSrtdAdj[wColocIndexTriplets_vObjects1][:, 1].argsort()]
            # wColocSrtdAdj[wColocIndexQuadruplets_vObjects1][wColocSrtdAdj[wColocIndexQuadruplets_vObjects1][:, 1].argsort()]
    
            # #Reorder first colum by increasing value
            # # x=np.array(([3,4],[7,2],[5,4],[5,6],[7,8]))
            # # x[x[:, 0].argsort()]
    
            #Reorder by first column by increasing value to organize the doublets, triplets, quadruplets
            #Select first column only
            wObjects2IndexSinglets = wColocSrtdAdj[wColocIndexSingles_vObjects2][wColocSrtdAdj[wColocIndexSingles_vObjects2][:, 0].argsort()][:,0]
            wObjects2IndexDoublets = wColocSrtdAdj[wColocIndexDoublets_vObjects2][wColocSrtdAdj[wColocIndexDoublets_vObjects2][:, 0].argsort()][:,0]
            wObjects2IndexTriplets = wColocSrtdAdj[wColocIndexTriplets_vObjects2][wColocSrtdAdj[wColocIndexTriplets_vObjects2][:, 0].argsort()][:,0]
            wObjects2IndexQuadruplets = wColocSrtdAdj[wColocIndexQuadruplets_vObjects2][wColocSrtdAdj[wColocIndexQuadruplets_vObjects2][:, 0].argsort()][:,0]
            #Reorder by first column by increasing value to organize the doublets, triplets, quadruplets
            #Select second column only
            wObjects1IndexSinglets = wColocSrtdAdj[wColocIndexSingles_vObjects1][wColocSrtdAdj[wColocIndexSingles_vObjects1][:, 1].argsort()][:,1]
            wObjects1IndexDoublets = wColocSrtdAdj[wColocIndexDoublets_vObjects1][wColocSrtdAdj[wColocIndexDoublets_vObjects1][:, 1].argsort()][:,1]
            wObjects1IndexTriplets = wColocSrtdAdj[wColocIndexTriplets_vObjects1][wColocSrtdAdj[wColocIndexTriplets_vObjects1][:, 1].argsort()][:,1]
            wObjects1IndexQuadruplets = wColocSrtdAdj[wColocIndexQuadruplets_vObjects1][wColocSrtdAdj[wColocIndexQuadruplets_vObjects1][:, 1].argsort()][:,1]
    
    #####################
            aStatStart=1
            vStatSingles_vObjects1 = list(range(aStatStart+int(max(vNewSpots1_Stats[:,1])),
                                                np.unique(wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexSinglets.tolist()))[0].tolist()]).size+1))
            vStatDoublets_vObjects1 = list(range(aStatStart+int(max(vNewSpots1_Stats[:,2])),
                                                 int(float(np.unique(wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexDoublets.tolist()))[0].tolist()]).size)/2)+1))
            vStatDoublets_vObjects1 = np.repeat(vStatDoublets_vObjects1,2)
            vStatTriplets_vObjects1 = list(range(aStatStart+int(max(vNewSpots1_Stats[:,3])),
                                                 int(float(np.unique(wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexTriplets.tolist()))[0].tolist()]).size)/3)+1))
            vStatTriplets_vObjects1 = np.repeat(vStatTriplets_vObjects1,3)
            vStatQuadruplets_vObjects1 = list(range(aStatStart+int(max(vNewSpots2_Stats[:,4])),
                                                 int(float(np.unique(wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexQuadruplets.tolist()))[0].tolist()]).size)/4)+1))
            vStatQuadruplets_vObjects1 = np.repeat(vStatQuadruplets_vObjects1,4)
    #####################
            vStatSingles_vObjects2 = list(range(aStatStart+int(max(vNewSpots2_Stats[:,1])),
                                                np.unique(wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexSinglets.tolist()))[0].tolist()]).size+1))
            vStatDoublets_vObjects2 = list(range(aStatStart+int(max(vNewSpots2_Stats[:,2])),
                                                 int(float(np.unique(wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexDoublets.tolist()))[0].tolist()]).size)/2)+1))
            vStatDoublets_vObjects2 = np.repeat(vStatDoublets_vObjects2,2)
            vStatTriplets_vObjects2 = list(range(aStatStart+int(max(vNewSpots2_Stats[:,3])),
                                                 int(float(np.unique(wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexTriplets.tolist()))[0].tolist()]).size)/3)+1))
            vStatTriplets_vObjects2 = np.repeat(vStatTriplets_vObjects2,3)
            vStatQuadruplets_vObjects2 = list(range(aStatStart+int(max(vNewSpots2_Stats[:,4])),
                                                 int(float(np.unique(wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexQuadruplets.tolist()))[0].tolist()]).size)/4+1)))
            vStatQuadruplets_vObjects2 = np.repeat(vStatQuadruplets_vObjects2,4)
    
        ####################
            qProgressBar['value'] = aNextTimePoint+1/len(vTimeIndicesActive)*60
            master.update()
    ###############################################################################
    ###############################################################################
        #Create new statID for Singles Doublets,Triplets,Quadruplets for Spots2
    ############
            #for vObjects1 singlets
            if not wObjects1IndexSinglets.size == 0:
                vUnique000, vRepeat = np.unique(wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexSinglets.tolist()))[0].tolist()], return_counts=True, axis = 0)
                np.put(vNewSpots1_Stats[:,1],
                       sorted(set(wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexSinglets.tolist()))[0].tolist()].tolist()), key=wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexSinglets.tolist()))[0].tolist()].tolist().index),
                       vStatSingles_vObjects1)
                #Paired
                np.put(vNewSpots2_Stats[:,5],
                       sorted(set(wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexSinglets.tolist()))[0].tolist()].tolist()), key=wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexSinglets.tolist()))[0].tolist()].tolist().index),
                       np.repeat(list(range(1,np.unique(wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexSinglets.tolist()))[0].tolist()]).size+1)),vRepeat.tolist()).tolist())
    ############
        #for vObjects1 doublets
            if not wObjects1IndexDoublets.size==0:
                np.put(vNewSpots1_Stats[:,2],
                       wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexDoublets.tolist()))[0].tolist()].tolist(),
                       vStatDoublets_vObjects1)
                #Paired
                np.put(vNewSpots2_Stats[:,6],
                       sorted(set(wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexDoublets.tolist()))[0].tolist()].tolist()), key=wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexDoublets.tolist()))[0].tolist()].tolist().index),
                       sorted(set(vStatDoublets_vObjects2.tolist()), key=vStatDoublets_vObjects2.tolist().index))
    ############
        #for vObjects1 triplets
            if not wObjects1IndexTriplets.size==0:
                np.put(vNewSpots1_Stats[:,3],
                       wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexTriplets.tolist()))[0].tolist()].tolist(),
                       vStatDoublets_vObjects1)
                #Paired
                np.put(vNewSpots2_Stats[:,7],
                       sorted(set(wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexTriplets.tolist()))[0].tolist()].tolist()), key=wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexTriplets.tolist()))[0].tolist()].tolist().index),
                       sorted(set(vStatTriplets_vObjects2.tolist()), key=vStatTriplets_vObjects2.tolist().index))
    ############
        #for vObjects1 quadruplets
            if not wObjects1IndexQuadruplets.size==0:
                np.put(vNewSpots1_Stats[:,4],
                       wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexQuadruplets.tolist()))[0].tolist()].tolist(),
                       vStatDoublets_vObjects1)
                #Paired
                np.put(vNewSpots2_Stats[:,8],
                       sorted(set(wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexQuadruplets.tolist()))[0].tolist()].tolist()), key=wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexQuadruplets.tolist()))[0].tolist()].tolist().index),
                       sorted(set(vStatQuadruplets_vObjects2.tolist()), key=vStatQuadruplets_vObjects2.tolist().index))
    
                #remove duplictaes and keep order
                            # sorted(set(wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexSinglets.tolist()))[0].tolist()].tolist()), key=wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,1],wObjects1IndexSinglets.tolist()))[0].tolist()].tolist().index)
                # my_list=[1,4,7,7 5,5]
                # result = sorted(set(my_list), key=my_list.index)
                # result [1,4,7,5]
    ###############################################################################
    ###############################################################################
        #for vObjects2 singlets
            if not wObjects2IndexSinglets.size == 0:
                vUnique000, vRepeat = np.unique(wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexSinglets.tolist()))[0].tolist()], return_counts=True, axis = 0)
                np.put(vNewSpots2_Stats[:,1],
                       sorted(set(wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexSinglets.tolist()))[0].tolist()].tolist()), key=wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexSinglets.tolist()))[0].tolist()].tolist().index),
                       vStatSingles_vObjects2)
                #Paired
                np.put(vNewSpots1_Stats[:,5],
                       sorted(set(wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexSinglets.tolist()))[0].tolist()].tolist()), key=wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexSinglets.tolist()))[0].tolist()].tolist().index),
                       np.repeat(list(range(1,np.unique(wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexSinglets.tolist()))[0].tolist()]).size+1)),vRepeat.tolist()).tolist())
    ############
        #for vObjects2 doublets
            if not wObjects2IndexDoublets.size==0:
                np.put(vNewSpots2_Stats[:,2],
                       wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexDoublets.tolist()))[0].tolist()].tolist(),
                       vStatDoublets_vObjects2)
                #Paired
                np.put(vNewSpots1_Stats[:,6],
                       sorted(set(wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexDoublets.tolist()))[0].tolist()].tolist()), key=wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexDoublets.tolist()))[0].tolist()].tolist().index),
                       sorted(set(vStatDoublets_vObjects2.tolist()), key=vStatDoublets_vObjects2.tolist().index))
    ############
        #for vObjects2 triplets
            if not wObjects2IndexTriplets.size==0:
                np.put(vNewSpots2_Stats[:,3],
                       wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexTriplets.tolist()))[0].tolist()].tolist(),
                       vStatTriplets_vObjects2)
                #Paired
                np.put(vNewSpots1_Stats[:,7],
                       sorted(set(wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexTriplets.tolist()))[0].tolist()].tolist()), key=wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexTriplets.tolist()))[0].tolist()].tolist().index),
                       sorted(set(vStatTriplets_vObjects2.tolist()), key=vStatTriplets_vObjects2.tolist().index))
    ############
        #for vObjects2 quadruplets
            if not wObjects2IndexQuadruplets.size==0:
                np.put(vNewSpots2_Stats[:,4],
                       wColocSrtdAdj[:,1][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexQuadruplets.tolist()))[0].tolist()].tolist(),
                       vStatQuadruplets_vObjects2)
                #Paired
                np.put(vNewSpots1_Stats[:,8],
                       sorted(set(wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexQuadruplets.tolist()))[0].tolist()].tolist()), key=wColocSrtdAdj[:,0][np.where(np.isin(wColocSrtdAdj[:,0],wObjects2IndexQuadruplets.tolist()))[0].tolist()].tolist().index),
                       sorted(set(vStatQuadruplets_vObjects2.tolist()), key=vStatQuadruplets_vObjects2.tolist().index))
    #good to here:
    ###############################################################################
    ###############################################################################
            # wColocSrtdSpecials
    
            #Find Duplets. triplets or more
            #Spots2 colocalized with Spots1
            vUnique00, vCount00 = np.unique(wColocSrtdSpecials[:,0], return_counts=True, axis = 0)
            vUnique0, vCount0 = np.unique(wColocSrtdSpecials[:,1], return_counts=True, axis = 0)
    
            wLengthColocDoubletsSpecial_vObjects2 = vUnique0[vCount0 == 2].tolist()
            wLengthColocDoubletsSpecial_vObjects1 = vUnique00[vCount00 == 2].tolist()
    
            for i in range(len(wLengthColocDoubletsSpecial_vObjects1)):
                wCountSpecialsDoubles = wCountSpecialsDoubles + 1
                wObjects2SpecialIndicesDoublets = wColocSrtdSpecials[:,0][np.where(np.isin(wColocSrtdSpecials[:,1],wColocSrtdSpecials[:,1][np.where(np.isin(wColocSrtdSpecials[:,0],wLengthColocDoubletsSpecial_vObjects1[i]))[0].tolist()].tolist()))[0].tolist()]
                wObjects2SpecialIndicesDoubletsPaired = wColocSrtdSpecials[:,1][np.where(np.isin(wColocSrtdSpecials[:,0],wLengthColocDoubletsSpecial_vObjects1[i]))[0].tolist()]
                np.put(vNewSpots1_Stats[:,9],
                       np.unique(wObjects2SpecialIndicesDoublets),
                       [wCountSpecialsDoubles]*len(np.unique(wObjects2SpecialIndicesDoublets)))
                np.put(vNewSpots2_Stats[:,9],
                       np.unique(wObjects2SpecialIndicesDoubletsPaired),
                       [wCountSpecialsDoubles]*len(np.unique(wObjects2SpecialIndicesDoubletsPaired)))
                
    
        qProgressBar['value'] = 75
        master.update()
        ##############################################################################
        ##############################################################################
        #For any overallStats
        vOverallStatIds=[int(-1)]
        vOverallStatUnits=['um']*vSizeT
        vOverallStatFactorsTime=list(range(1,vSizeT+1))
        vOverallStatFactors=[['Overall'],[str(i) for i in vOverallStatFactorsTime]]
        vOverallStatFactorNames=['FactorName','Time']
        #########
        #Create new statistic for Spots2
        
        list(map(int, vObjects2TimeIndices))
        
        if qIsSurface:
            vSpotsStatFactors_vObjects2 = (['Surface']*vObjects2Length, [str(x) for x in [i for i in  list(map(int, vObjects2TimeIndices))]] )
            vSpotsStatFactors_vObjects1 = (['Surface']*vObjects1Length, [str(x) for x in [i for i in  list(map(int, vObjects1TimeIndices))]] )
        else:
            vSpotsStatFactors_vObjects2 = (['Spot']*vObjects2Length, [str(x) for x in [i+1 for i in vObjects2TimeIndices]] )
            vSpotsStatFactors_vObjects1 = (['Spot']*vObjects1Length, [str(x) for x in [i+1 for i in vObjects1TimeIndices]] )
    
            
        vSpotsStatUnits_vObjects2 = ['']*vObjects2Length
        vSpotsStatUnits_vObjects2NN = ['um']*vObjects2Length
        vSpotsStatUnits_vObjects1=['']*vObjects1Length
        vSpotsStatUnits_vObjects1NN=['um']*vObjects1Length
    
        vSpotsStatFactorName = ['Category','Time']
        if np.any(wLengthColocSingles_vObjects2):
            vSpotsStatNames = [' 1_SinglesID - w/' + str(vObjects1.GetName())]*vObjects2Length
            vObjects2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,1].tolist(),
                                          vSpotsStatUnits_vObjects2, vSpotsStatFactors_vObjects2,
                                          vSpotsStatFactorName, vObjects2Ids)
            vSpotsStatNames = [' Paired_1_SinglesID - w/' + str(vObjects2.GetName())]*vObjects1Length
            vObjects1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,5].tolist(),
                                          vSpotsStatUnits_vObjects1, vSpotsStatFactors_vObjects1,
                                          vSpotsStatFactorName, vObjects1Ids)
        ####################################################
            #Find only paired singlets, reomve all other and calcualte NN values
            # zColoc = np.array(vObjects1PositionsXYZ)[np.where(vNewSpots1_Stats[:,5])[0].tolist()]
            # # #Create some Overall Coloc Stats
            # # #MeanNN, MaxNN, MinNN
            # zColocArray = cdist(zColoc,zColoc)
            # zColocArrayMin = np.where(zColocArray>0, zColocArray, np.inf).min(axis=1)
            # zColocMeanNNOverall = np.mean(zColocArrayMin)
            # zColocMaxNNOverall = np.max(zColocArrayMin)
            # zColocMinNNOverall = np.min(zColocArrayMin)
            # vOverallStatNames = [' Coloc Singlets meanNN ']
            # vObjects1.AddStatistics(vOverallStatNames, [zColocMeanNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Singlets maxNN ']
            # vObjects1.AddStatistics(vOverallStatNames, [zColocMaxNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Singlets minNN ']
            # vObjects1.AddStatistics(vOverallStatNames, [zColocMinNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
    
    
            # vSpotsStatNames = [' Paired_1_Doublets NN distance']*vObjects1Length
            # vObjects1.AddStatistics(vSpotsStatNames, np.argmin(zColocArray, axis=1),
            #                               vSpotsStatUnits_vObjects1, vSpotsStatFactors_vObjects1,
            #                               vSpotsStatFactorName, vObjects1Ids)
    
    
    
        ####################################################
        if np.any(wLengthColocDoublets_vObjects2):
            vSpotsStatNames = [' 2_DoubletsID - w/' + str(vObjects1.GetName())]*vObjects2Length
            vObjects2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,2].tolist(),
                                          vSpotsStatUnits_vObjects2, vSpotsStatFactors_vObjects2,
                                          vSpotsStatFactorName, vObjects2Ids)
            vSpotsStatNames = [' Paired_2_DoubletsID - w/' + str(vObjects2.GetName())]*vObjects1Length
            vObjects1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,6].tolist(),
                                          vSpotsStatUnits_vObjects1, vSpotsStatFactors_vObjects1,
                                          vSpotsStatFactorName, vObjects1Ids)
    
        ####################################################
            #Find only paired duplets, REMOVE all other and calcualte NN values
            zColoc = np.array(vObjects1PositionsXYZ)[np.where(vNewSpots1_Stats[:,6])[0].tolist()]
            #Create some Overall Coloc Stats
            #MeanNN, MaxNN, MinNN
            # zColocArray = cdist(zColoc,zColoc)
            # zColocArrayMin = np.where(zColocArray>0, zColocArray, np.inf).min(axis=1)
            # zColocMeanNNOverall = np.mean(zColocArrayMin)
            # zColocMaxNNOverall = np.max(zColocArrayMin)
            # zColocMinNNOverall = np.min(zColocArrayMin)
            # vOverallStatNames = [' Coloc Doublets meanNN ']
            # vObjects1.AddStatistics(vOverallStatNames, [zColocMeanNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Doublets maxNN ']
            # vObjects1.AddStatistics(vOverallStatNames, [zColocMaxNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Doublets minNN ']
            # vObjects1.AddStatistics(vOverallStatNames, [zColocMinNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
        ####################################################
        if np.any(wLengthColocTriplets_vObjects2):
            vSpotsStatNames = [' 3_TripletsID - w/' + str(vObjects1.GetName())]*vObjects2Length
            vObjects2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,3].tolist(),
                                          vSpotsStatUnits_vObjects2, vSpotsStatFactors_vObjects2,
                                          vSpotsStatFactorName, vObjects2Ids)
            vSpotsStatNames = [' Paired_3_TripletsID - w/' + str(vObjects2.GetName())]*vObjects1Length
            vObjects1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,7].tolist(),
                                          vSpotsStatUnits_vObjects1, vSpotsStatFactors_vObjects1,
                                          vSpotsStatFactorName, vObjects1Ids)
        ####################################################
            #Find only paired duplets, reomve all other and calcualte NN values
            # zColoc = np.array(vObjects1PositionsXYZ)[np.where(vNewSpots1_Stats[:,7])[0].tolist()]
            # #Create some Overall Coloc Stats
            # #MeanNN, MaxNN, MinNN
            # zColocArray = cdist(zColoc,zColoc)
            # zColocArrayMin = np.where(zColocArray>0, zColocArray, np.inf).min(axis=1)
            # zColocMeanNNOverall = np.mean(zColocArrayMin)
            # zColocMaxNNOverall = np.max(zColocArrayMin)
            # zColocMinNNOverall = np.min(zColocArrayMin)
            # vOverallStatNames = [' Coloc Triplets meanNN ']
            # vObjects1.AddStatistics(vOverallStatNames, [zColocMeanNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Triplets maxNN ']
            # vObjects1.AddStatistics(vOverallStatNames, [zColocMaxNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Triplets minNN ']
            # vObjects1.AddStatistics(vOverallStatNames, [zColocMinNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
        ####################################################
        if np.any(wLengthColocQuadruplets_vObjects2):
            vSpotsStatNames = [' 4_QuadrupletsID - w/' + str(vObjects1.GetName())]*vObjects2Length
            vObjects2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,4].tolist(),
                                          vSpotsStatUnits_vObjects2, vSpotsStatFactors_vObjects2,
                                          vSpotsStatFactorName, vObjects2Ids)
            vSpotsStatNames = [' Paired_4_QuadrupletsID - w/' + str(vObjects2.GetName())]*vObjects1Length
            vObjects1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,8].tolist(),
                                          vSpotsStatUnits_vObjects1, vSpotsStatFactors_vObjects1,
                                          vSpotsStatFactorName, vObjects1Ids)
        ####################################################
            #Find only paired Quadrupliets, reomve all other and calcualte NN values
            # zColoc = np.array(vObjects1PositionsXYZ)[np.where(vNewSpots1_Stats[:,8])[0].tolist()]
            # #Create some Overall Coloc Stats
            # #MeanNN, MaxNN, MinNN
            # zColocArray = cdist(zColoc,zColoc)
            # zColocArrayMin = np.where(zColocArray>0, zColocArray, np.inf).min(axis=1)
            # zColocMeanNNOverall = np.mean(zColocArrayMin)
            # zColocMaxNNOverall = np.max(zColocArrayMin)
            # zColocMinNNOverall = np.min(zColocArrayMin)
            # vOverallStatNames = [' Coloc Quadruplets meanNN ']
            # vObjects1.AddStatistics(vOverallStatNames, [zColocMeanNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Quadruplets maxNN ']
            # vObjects1.AddStatistics(vOverallStatNames, [zColocMaxNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Quadruplets minNN ']
            # vObjects1.AddStatistics(vOverallStatNames, [zColocMinNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
        ####################################################
    
        # if not wSpots2SpecialDoubletsIndices.size==0:
        #     vSpotsStatNames = [' 2_DoubletsID_Special - w/' + str(vObjects1.GetName())]*vObjects2Length
        #     vObjects2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,9].tolist(),
        #                                   vSpotsStatUnits_vObjects2, vSpotsStatFactors_vObjects2,
        #                                   vSpotsStatFactorName, vObjects2Ids)
    
        ##############################################################################
        #Create new statistic for Spots1
        if np.any(wLengthColocSingles_vObjects1):
            vSpotsStatNames = [' 1_SinglesID w/' + str(vObjects2.GetName())]*vObjects1Length
            vObjects1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,1].tolist(),
                                          vSpotsStatUnits_vObjects1, vSpotsStatFactors_vObjects1,
                                          vSpotsStatFactorName, vObjects1Ids)
            vSpotsStatNames = [' Paired_1_SinglesID - w/' + str(vObjects1.GetName())]*vObjects2Length
            vObjects2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,5].tolist(),
                                          vSpotsStatUnits_vObjects2, vSpotsStatFactors_vObjects2,
                                          vSpotsStatFactorName, vObjects2Ids)
        ####################################################
            #Find only paired singlets, reomve all other and calcualte NN values
            # zColoc = np.array(vObjects1PositionsXYZ)[np.where(vNewSpots1_Stats[:,5])[0].tolist()]
            # #Create some Overall Coloc Stats
            # #MeanNN, MaxNN, MinNN
            # zColocArray = cdist(zColoc,zColoc)
            # zColocArrayMin = np.where(zColocArray>0, zColocArray, np.inf).min(axis=1)
            # zColocMeanNNOverall = np.mean(zColocArrayMin)
            # zColocMaxNNOverall = np.max(zColocArrayMin)
            # zColocMinNNOverall = np.min(zColocArrayMin)
            # vOverallStatNames = [' Coloc Singlets meanNN ']
            # vObjects2.AddStatistics(vOverallStatNames, [zColocMeanNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Singlets maxNN ']
            # vObjects2.AddStatistics(vOverallStatNames, [zColocMaxNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Singlets minNN ']
            # vObjects2.AddStatistics(vOverallStatNames, [zColocMinNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
        ####################################################
        if np.any(wLengthColocDoublets_vObjects1):
            vSpotsStatNames = [' 2_DoubletsID w/' + str(vObjects2.GetName()) ]*vObjects1Length
            vObjects1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,2].tolist(),
                                          vSpotsStatUnits_vObjects1, vSpotsStatFactors_vObjects1,
                                          vSpotsStatFactorName, vObjects1Ids)
            vSpotsStatNames = [' Paired_2_DoubletsID - w/' + str(vObjects1.GetName())]*vObjects2Length
            vObjects2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,6].tolist(),
                                          vSpotsStatUnits_vObjects2, vSpotsStatFactors_vObjects2,
                                          vSpotsStatFactorName, vObjects2Ids)
        ####################################################
            #Find only paired duplets, reomve all other and calcualte NN values
            # zColoc = np.array(vObjects1PositionsXYZ)[np.where(vNewSpots1_Stats[:,6])[0].tolist()]
            # #Create some Overall Coloc Stats
            # #MeanNN, MaxNN, MinNN
            # zColocArray = cdist(zColoc,zColoc)
            # zColocArrayMin = np.where(zColocArray>0, zColocArray, np.inf).min(axis=1)
            # zColocMeanNNOverall = np.mean(zColocArrayMin)
            # zColocMaxNNOverall = np.max(zColocArrayMin)
            # zColocMinNNOverall = np.min(zColocArrayMin)
            # vOverallStatNames = [' Coloc Doublets meanNN ']
            # vObjects2.AddStatistics(vOverallStatNames, [zColocMeanNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Doublets maxNN ']
            # vObjects2.AddStatistics(vOverallStatNames, [zColocMaxNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Doublets minNN ']
            # vObjects2.AddStatistics(vOverallStatNames, [zColocMinNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
        ####################################################
        if np.any(wLengthColocTriplets_vObjects1):
            vSpotsStatNames = [' 3_TripletsID']*vObjects1Length
            vObjects1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,3].tolist(),
                                          vSpotsStatUnits_vObjects1, vSpotsStatFactors_vObjects1,
                                          vSpotsStatFactorName, vObjects1Ids)
            vSpotsStatNames = [' Paired_3_TripletsID - w/' + str(vObjects1.GetName())]*vObjects2Length
            vObjects2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,7].tolist(),
                                          vSpotsStatUnits_vObjects2, vSpotsStatFactors_vObjects2,
                                          vSpotsStatFactorName, vObjects2Ids)
        ####################################################
            #Find only paired duplets, reomve all other and calcualte NN values
            # zColoc = np.array(vObjects1PositionsXYZ)[np.where(vNewSpots1_Stats[:,7])[0].tolist()]
            # #Create some Overall Coloc Stats
            # #MeanNN, MaxNN, MinNN
            # zColocArray = cdist(zColoc,zColoc)
            # zColocArrayMin = np.where(zColocArray>0, zColocArray, np.inf).min(axis=1)
            # zColocMeanNNOverall = np.mean(zColocArrayMin)
            # zColocMaxNNOverall = np.max(zColocArrayMin)
            # zColocMinNNOverall = np.min(zColocArrayMin)
            # vOverallStatNames = [' Coloc Triplets meanNN ']
            # vObjects2.AddStatistics(vOverallStatNames, [zColocMeanNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Triplets maxNN ']
            # vObjects2.AddStatistics(vOverallStatNames, [zColocMaxNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Triplets minNN ']
            # vObjects2.AddStatistics(vOverallStatNames, [zColocMinNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
        ####################################################
        if np.any(wLengthColocQuadruplets_vObjects1):
            vSpotsStatNames = [' 4_QuadrupletsID']*vObjects1Length
            vObjects1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,4].tolist(),
                                          vSpotsStatUnits_vObjects1, vSpotsStatFactors_vObjects1,
                                          vSpotsStatFactorName, vObjects1Ids)
            vSpotsStatNames = [' Paired_4_QuadrupletsID - w/' + str(vObjects1.GetName())]*vObjects2Length
            vObjects2.AddStatistics(vSpotsStatNames, vNewSpots2_Stats[:,8].tolist(),
                                          vSpotsStatUnits_vObjects2, vSpotsStatFactors_vObjects2,
                                          vSpotsStatFactorName, vObjects2Ids)
        ####################################################
            #Find only paired Quadrupliets, reomve all other and calcualte NN values
            # zColoc = np.array(vObjects1PositionsXYZ)[np.where(vNewSpots1_Stats[:,8])[0].tolist()]
            # #Create some Overall Coloc Stats
            # #MeanNN, MaxNN, MinNN
            # zColocArray = cdist(zColoc,zColoc)
            # zColocArrayMin = np.where(zColocArray>0, zColocArray, np.inf).min(axis=1)
            # zColocMeanNNOverall = np.mean(zColocArrayMin)
            # zColocMaxNNOverall = np.max(zColocArrayMin)
            # zColocMinNNOverall = np.min(zColocArrayMin)
            # vOverallStatNames = [' Coloc Quadruplets meanNN ']
            # vObjects2.AddStatistics(vOverallStatNames, [zColocMeanNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Quadruplets maxNN ']
            # vObjects2.AddStatistics(vOverallStatNames, [zColocMaxNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
            # vOverallStatNames = [' Coloc Quadruplets minNN ']
            # vObjects2.AddStatistics(vOverallStatNames, [zColocMinNNOverall],
            #                               vOverallStatUnits, vOverallStatFactors,
            #                               vOverallStatFactorNames, vOverallStatIds)
        ####################################################
        # if not wSpots1SpecialDoubletsIndices.size==0:
        #     vSpotsStatNames = [' 2_DoubletsID_Special - w/' + str(vObjects2.GetName())]*vObjects1Length
        #     vObjects1.AddStatistics(vSpotsStatNames, vNewSpots1_Stats[:,9].tolist(),
        #                                   vSpotsStatUnits_vObjects1, vSpotsStatFactors_vObjects1,
        #                                   vSpotsStatFactorName, vObjects1Ids)
        ###############################################################################
        ###############################################################################
        #Create Labels for vObjects2
        wLabelList = []
        wLabelIndices = np.where(vNewSpots2_Stats[:,1])
        for i in range(len(wLabelIndices[0])):
            vLabelCreate = vFactory.CreateObjectLabel(vObjects2Ids[wLabelIndices[0][i]], 'Coloc', '1_Singles')
            wLabelList.append(vLabelCreate)
        vObjects2.SetLabels(wLabelList)
        #######################
        wLabelList = []
        wLabelIndices = np.where(vNewSpots2_Stats[:,2])
        for i in range(len(wLabelIndices[0])):
            vLabelCreate = vFactory.CreateObjectLabel(vObjects2Ids[wLabelIndices[0][i]], 'Coloc', '2_Doublets')
            wLabelList.append(vLabelCreate)
        vObjects2.SetLabels(wLabelList)
        #######################
        wLabelList = []
        wLabelIndices = np.where(vNewSpots2_Stats[:,3])
        for i in range(len(wLabelIndices[0])):
            vLabelCreate = vFactory.CreateObjectLabel(vObjects2Ids[wLabelIndices[0][i]], 'Coloc', '3_Triplets')
            wLabelList.append(vLabelCreate)
        vObjects2.SetLabels(wLabelList)
        #######################
        wLabelList = []
        wLabelIndices = np.where(vNewSpots2_Stats[:,4])
        for i in range(len(wLabelIndices[0])):
            vLabelCreate = vFactory.CreateObjectLabel(vObjects2Ids[wLabelIndices[0][i]], 'Coloc', '4_Quadruplets')
            wLabelList.append(vLabelCreate)
        vObjects2.SetLabels(wLabelList)
        #######################
        wLabelList = []
        wLabelIndices = np.where(vNewSpots2_Stats[:,9])
        for i in range(len(wLabelIndices[0])):
            vLabelCreate = vFactory.CreateObjectLabel(vObjects2Ids[wLabelIndices[0][i]], 'Coloc', '2_Doublets Special')
            wLabelList.append(vLabelCreate)
        vObjects2.SetLabels(wLabelList)
        ###############################################################################
        wLabelList = []
        #Remove first column of the vNew StatDoublets
        #Find row indices that have all zeros
        #These are the non-Coloc spots
        wLabelIndices=np.where((~np.any(vNewSpots2_Stats[:,1:5][:],axis=1) & ~np.any(vNewSpots2_Stats[:,9:10][:],axis=1)))
        for i in range(len(wLabelIndices[0])):
            vLabelCreate = vFactory.CreateObjectLabel(vObjects2Ids[wLabelIndices[0][i]], 'Coloc', ' Non-Colocalized')
            wLabelList.append(vLabelCreate)
        vObjects2.SetLabels(wLabelList)
        ########################
    
        #Create Labels for vObjects1
        wLabelList = []
        wLabelIndices = np.where(vNewSpots1_Stats[:,1])
        for i in range(len(wLabelIndices[0])):
            vLabelCreate = vFactory.CreateObjectLabel(vObjects1Ids[wLabelIndices[0][i]], 'Coloc', '1_Singles')
            wLabelList.append(vLabelCreate)
        vObjects1.SetLabels(wLabelList)
        #######################
        wLabelList = []
        wLabelIndices = np.where(vNewSpots1_Stats[:,2])
        for i in range(len(wLabelIndices[0])):
            vLabelCreate = vFactory.CreateObjectLabel(vObjects1Ids[wLabelIndices[0][i]], 'Coloc', '2_Doublets')
            wLabelList.append(vLabelCreate)
        vObjects1.SetLabels(wLabelList)
        #######################
        wLabelList = []
        wLabelIndices = np.where(vNewSpots1_Stats[:,3])
        for i in range(len(wLabelIndices[0])):
            vLabelCreate = vFactory.CreateObjectLabel(vObjects1Ids[wLabelIndices[0][i]], 'Coloc', '3_Triplets')
            wLabelList.append(vLabelCreate)
        vObjects1.SetLabels(wLabelList)
        #######################
        wLabelList = []
        wLabelIndices = np.where(vNewSpots1_Stats[:,4])
        for i in range(len(wLabelIndices[0])):
            vLabelCreate = vFactory.CreateObjectLabel(vObjects1Ids[wLabelIndices[0][i]], 'Coloc', '4_Quadruplets')
            wLabelList.append(vLabelCreate)
        vObjects1.SetLabels(wLabelList)
        #######################
        wLabelList = []
        wLabelIndices = np.where(vNewSpots1_Stats[:,9])
        for i in range(len(wLabelIndices[0])):
            vLabelCreate = vFactory.CreateObjectLabel(vObjects1Ids[wLabelIndices[0][i]], 'Coloc', '2_Doublets Special')
            wLabelList.append(vLabelCreate)
        vObjects1.SetLabels(wLabelList)
        ############################################################################### 
        #######################
        wLabelList = []
        #Remove first column of the vNew StatDoublets
        #Find row indices that have all zeros
        #These are the non-Coloc spots
        wLabelIndices=np.where((~np.any(vNewSpots1_Stats[:,1:5][:],axis=1)& ~np.any(vNewSpots1_Stats[:,9:10][:],axis=1)))
        for i in range(len(wLabelIndices[0])):
            vLabelCreate = vFactory.CreateObjectLabel(vObjects1Ids[wLabelIndices[0][i]], 'Coloc', ' Non-Colocalized')
            wLabelList.append(vLabelCreate)
        vObjects1.SetLabels(wLabelList)
    
        ###############################################################################
        qProgressBar['value'] = 100
        master.update()
    
        vObjects1.SetName(vObjects1.GetName()+' -- ColocAnalyzed')
        vImarisApplication.GetSurpassScene().AddChild(vObjects1, -1)
        vObjects2.SetName(vObjects2.GetName()+' -- ColocAnalyzed')
        vImarisApplication.GetSurpassScene().AddChild(vObjects2, -1)
    
    
    #######################
    #######################
    if vOptionSurfaceSurfaceOverlap == 1:
        vDataItem=vScene.GetChild(NamesSurfacesIndex[(NamesSurfaces.index( ''.join(map(str, ObjectSelection[0]))))])
        vSurfaces1=vImarisApplication.GetFactory().ToSurfaces(vDataItem)
    
        vDataItem=vScene.GetChild(NamesSurfacesIndex[(NamesSurfaces.index( ''.join(map(str, ObjectSelection[1]))))])
        vSurfaces2=vImarisApplication.GetFactory().ToSurfaces(vDataItem)
    
        vNumberOfSurfaces1 = vSurfaces1.GetNumberOfSurfaces()
        vNumberOfSurfaces2 = vSurfaces2.GetNumberOfSurfaces()
        vSurfaces1Ids = vSurfaces1.GetIds()
        vSurfaces2Ids = vSurfaces2.GetIds()
    
    
        vTimeIndexSurfaces1 = np.array(vSurfaces1.GetStatisticsByName('Time Index').mValues)
        vTimeIndexSurfaces2 = np.array(vSurfaces2.GetStatisticsByName('Time Index').mValues)
        vTimeIndicesActive=np.intersect1d(np.unique(vTimeIndexSurfaces1), np.unique(vTimeIndexSurfaces2))
    
    
    
        #########################################
        #Create Random Color mask in Volume as 1D array ALL surfaces
        #Surfaces1
        vRandomColorMaskALL= []
        vRandomColorMaskSurfaces1 = np.zeros(vDataSize[0]*vDataSize[1]*vDataSize[2])
        vRandomColorMaskSurfaces2 = np.zeros(vDataSize[0]*vDataSize[1]*vDataSize[2])
        start = time.time()
        for aSurfaceIndex in range (vNumberOfSurfaces1):
            vSurpassObjectIndexT = vSurfaces1.GetTimeIndex(aSurfaceIndex)
            zMaskSingleSurface = vSurfaces1.GetSingleMask(aSurfaceIndex,
                                                     vDataMin[0],
                                                     vDataMin[1],
                                                     vDataMin[2],
                                                     vDataMax[0],
                                                     vDataMax[1],
                                                     vDataMax[2],
                                                     vDataSize[0],
                                                     vDataSize[1],
                                                     vDataSize[2])
            vRandomColorMaskCurrent = np.array(zMaskSingleSurface.GetDataSubVolumeAs1DArrayShorts(0,0,0,
                                                                          0,
                                                                          vSurpassObjectIndexT,
                                                                          vDataSize[0], vDataSize[1],vDataSize[2]))
            # vRandomColorMaskCurrent[vRandomColorMaskCurrent!=0] += aSurfaceIndex
            # np.where(x==1)[0].tolist()
            np.put(vRandomColorMaskSurfaces1,
                                        np.where(vRandomColorMaskCurrent==1)[0].tolist(),
                                    [(aSurfaceIndex + 1)]*np.size(np.where(vRandomColorMaskCurrent)))
            qProgressBar['value'] = ((aSurfaceIndex+1)/vNumberOfSurfaces1*100) #  % out of 100
            qProgressBar.update()
        elapsed = time.time() - start
        print(elapsed)
        label_2 = tk.Label(master, text="Synaptic analysis 2/4")
        label_2.grid(row=0, column=0,pady=10)
        qProgressBar.update()
    
        ########
        start = time.time()
        for aSurfaceIndex in range (vNumberOfSurfaces2):
            vSurpassObjectIndexT = vSurfaces2.GetTimeIndex(aSurfaceIndex)
            zMaskSingleSurface = vSurfaces2.GetSingleMask(aSurfaceIndex,
                                                     vDataMin[0],
                                                     vDataMin[1],
                                                     vDataMin[2],
                                                     vDataMax[0],
                                                     vDataMax[1],
                                                     vDataMax[2],
                                                     vDataSize[0],
                                                     vDataSize[1],
                                                     vDataSize[2])
            vRandomColorMaskCurrent = np.array(zMaskSingleSurface.GetDataSubVolumeAs1DArrayFloats(0,0,0,
                                                                          0,
                                                                          vSurpassObjectIndexT,
                                                                          vDataSize[0], vDataSize[1],vDataSize[2]))
            # progress_bar2['value'] = ((aSurfaceIndex+1)/vNumberOfSurfaces2*100) #  % out of 100
            # qProgressBar.update()
            # vRandomColorMaskCurrent[vRandomColorMaskCurrent!=0] += aSurfaceIndex
            # np.where(x==1)[0].tolist()
            # vRandomColorMaskSurfaces2 = np.put(vRandomColorMaskSurfaces2,
            #                             np.where(vRandomColorMaskCurrent==1)[0].tolist(),
            #                             [(aSurfaceIndex + 1)]*len(np.where(vRandomColorMaskCurrent==1)[0].tolist()))
            np.put(vRandomColorMaskSurfaces2,
                                        np.where(vRandomColorMaskCurrent==1)[0].tolist(),
                                        [(aSurfaceIndex + 1)]*np.size(np.where(vRandomColorMaskCurrent)))
            qProgressBar['value'] = ((aSurfaceIndex+1)/vNumberOfSurfaces1*100) #  % out of 100
            qProgressBar.update()
        elapsed = time.time() - start
        print(elapsed)
        label_3 = tk.Label(master, text="Synaptic analysis 3/4")
        label_3.grid(row=0, column=0,pady=10)
        qProgressBar.update()
        start = time.time()
        #####################################
        #####################################
        vRandomColorMaskChannel = 3
        vSurfaces1ColorMaskIntIdColcowithvSurfaces2 = []
        vSurfaces2ColorMaskIntIdColcowithvSurfaces1 = []
        #loop through each Surface1 object
        #find randomcolorMask Ids for Surface2 that overlap each surface
        for aSurfaceIndex in range (vNumberOfSurfaces1):
            vSurpassObjectIndexT = vSurfaces1.GetTimeIndex(aSurfaceIndex)
            zMaskSingleSurface = vSurfaces1.GetSingleMask(aSurfaceIndex,
                                                     vDataMin[0],
                                                     vDataMin[1],
                                                     vDataMin[2],
                                                     vDataMax[0],
                                                     vDataMax[1],
                                                     vDataMax[2],
                                                     vDataSize[0],
                                                     vDataSize[1],
                                                     vDataSize[2])
            # vRandomColorMaskSurfaces2 = np.array(vImage.GetDataSubVolumeAs1DArrayFloats(0,0,0,
            #                                                               vRandomColorMaskChannel,
            #                                                               vSurpassObjectIndexT,
            #                                                               vDataSize[0], vDataSize[1],vDataSize[2]))
            vBinaryMaskCurrent = np.array(zMaskSingleSurface.GetDataSubVolumeAs1DArrayFloats(0,0,0,
                                                                          0,
                                                                          vSurpassObjectIndexT,
                                                                          vDataSize[0], vDataSize[1],vDataSize[2]))
            #Potential to dilate binary mask before next step.
            #reshape---dilate--return to 1D array
    
            # np.where(vBinaryMaskCurrent)[0].tolist()
            vSurfaces2ColorMaskIntIdColcowithvSurfaces1.append(np.unique(vRandomColorMaskSurfaces2[np.where(vBinaryMaskCurrent)[0].tolist()]).tolist())
            qProgressBar['value'] = ((aSurfaceIndex+1)/vNumberOfSurfaces1*100) #  % out of 100
            qProgressBar.update()
        elapsed = time.time() - start
        print(elapsed)
        label_4 = tk.Label(master, text="Synaptic analysis 4/4")
        label_4.grid(row=0, column=0,pady=10)
        qProgressBar.update()
        #####################################
        start = time.time()
        vRandomColorMaskChannel = 2
        #loop through each Surface2 object
        #find randomcolorMask Ids for Surfaces1 that overlap each surface
        for aSurfaceIndex in range (vNumberOfSurfaces2):
            vSurpassObjectIndexT = vSurfaces2.GetTimeIndex(aSurfaceIndex)
            zMaskSingleSurface = vSurfaces2.GetSingleMask(aSurfaceIndex,
                                                     vDataMin[0],
                                                     vDataMin[1],
                                                     vDataMin[2],
                                                     vDataMax[0],
                                                     vDataMax[1],
                                                     vDataMax[2],
                                                     vDataSize[0],
                                                     vDataSize[1],
                                                     vDataSize[2])
            # vRandomColorMaskSurfaces1 = np.array(vImage.GetDataSubVolumeAs1DArrayFloats(0,0,0,
            #                                                               vRandomColorMaskChannel,
            #                                                               vSurpassObjectIndexT,
            #                                                               vDataSize[0], vDataSize[1],vDataSize[2]))
            vBinaryMaskCurrent = np.array(zMaskSingleSurface.GetDataSubVolumeAs1DArrayFloats(0,0,0,
                                                                          0,
                                                                          vSurpassObjectIndexT,
                                                                          vDataSize[0], vDataSize[1],vDataSize[2]))
            # np.where(vBinaryMaskCurrent)[0].tolist()
            vSurfaces1ColorMaskIntIdColcowithvSurfaces2.append(np.unique(vRandomColorMaskSurfaces1[np.where(vBinaryMaskCurrent)[0].tolist()]))
            qProgressBar['value'] = ((aSurfaceIndex+1)/vNumberOfSurfaces1*100) #  % out of 100
            qProgressBar.update()
        elapsed = time.time() - start
        print(elapsed)
        #####################################
        #####################################
    
    #Remove doublet/triplets specials....to new adj list
    
        vSurfaces2ColorMaskIntIdColcowithvSurfaces1Adj = vSurfaces2ColorMaskIntIdColcowithvSurfaces1.copy()
        vSurfaces1ColorMaskIntIdColcowithvSurfaces2Adj = vSurfaces1ColorMaskIntIdColcowithvSurfaces2.copy()
    
        flattenedSurfaces1  = [val for sublist in vSurfaces1ColorMaskIntIdColcowithvSurfaces2 for val in sublist]
        flattenedSurfaces2  = [val for sublist in vSurfaces2ColorMaskIntIdColcowithvSurfaces1 for val in sublist]
        vUniqueSpecial_vSurfaces2, vCountSpecial_vSurfaces2 = np.unique(np.array(flattenedSurfaces2), return_counts=True, axis = 0)
        vUniqueSpecial_vSurfaces1, vCountSpecial_vSurfaces1 = np.unique(np.array(flattenedSurfaces1), return_counts=True, axis = 0)
    
        wColocSpecialIdx = np.delete(np.where(vCountSpecial_vSurfaces2>=2),0).tolist()
        wColocSpecialIdx = np.delete(np.where(vCountSpecial_vSurfaces1>=2),0).tolist()
    
        for i in range(len(np.delete(np.where(vCountSpecial_vSurfaces2>=2),0).tolist())):
            vSurfaces2ColorMaskIntIdColcowithvSurfaces1Adj.pop(np.delete(np.where(vCountSpecial_vSurfaces2>=2),0).tolist()[i])
        for i in range(len(np.delete(np.where(vCountSpecial_vSurfaces1>=2),0).tolist())):
            vSurfaces1ColorMaskIntIdColcowithvSurfaces2Adj.pop(np.delete(np.where(vCountSpecial_vSurfaces1>=2),0).tolist()[i])
    
        #Find singlets,doublets, triplets Ids
        # vColocNumbersSurfaces1 = [len(i) for i in vSurfaces2ColorMaskIntIdColcowithvSurfaces1]
        wSurfaces1ListSingleIdx = np.where(np.array([len(i) for i in vSurfaces2ColorMaskIntIdColcowithvSurfaces1]) == 2)
        wSurfaces1ListDoubletIdx = np.where(np.array([len(i) for i in vSurfaces2ColorMaskIntIdColcowithvSurfaces1]) == 3)
        wSurfaces1ListTripletIdx = np.where(np.array([len(i) for i in vSurfaces2ColorMaskIntIdColcowithvSurfaces1]) == 4)
        wSurfaces1ListQuadrupletIdx = np.where(np.array([len(i) for i in vSurfaces2ColorMaskIntIdColcowithvSurfaces1]) == 5)
    
        # vColocNumbersSurfcaes2 = [len(i) for i in vSurfaces1ColorMaskIntIdColcowithvSurfaces2]
        wSurfaces2ListSingleIdx = np.where(np.array([len(i) for i in vSurfaces1ColorMaskIntIdColcowithvSurfaces2]) == 2)
        wSurfaces2ListDoubletIdx = np.where(np.array([len(i) for i in vSurfaces1ColorMaskIntIdColcowithvSurfaces2]) == 3)
        wSurfaces2ListTripletIdx = np.where(np.array([len(i) for i in vSurfaces1ColorMaskIntIdColcowithvSurfaces2]) == 4)
        wSurfaces2ListQuadrupletIdx = np.where(np.array([len(i) for i in vSurfaces1ColorMaskIntIdColcowithvSurfaces2]) == 5)
    
        wSurfaces1ListSingleIds = np.array(vSurfaces1Ids)[wSurfaces1ListSingleIdx[0].tolist()]
        wSurfaces1ListDoubletIds = np.array(vSurfaces1Ids)[wSurfaces1ListDoubletIdx[0].tolist()]
        wSurfaces1ListTripletIds = np.array(vSurfaces1Ids)[wSurfaces1ListTripletIdx[0].tolist()]
        wSurfaces1ListQuadrupletIds = np.array(vSurfaces1Ids)[wSurfaces1ListQuadrupletIdx[0].tolist()]
    
        wSurfaces2ListSingleIds = np.array(vSurfaces2Ids)[wSurfaces2ListSingleIdx[0].tolist()]
        wSurfaces2ListDoubletIds = np.array(vSurfaces2Ids)[wSurfaces2ListDoubletIdx[0].tolist()]
        wSurfaces2ListTripletIds = np.array(vSurfaces2Ids)[wSurfaces2ListTripletIdx[0].tolist()]
        wSurfaces2ListQuadrupletIds = np.array(vSurfaces2Ids)[wSurfaces2ListQuadrupletIdx[0].tolist()]
    
    
    #PairedSurfaces2 with surfaces1
        # wSurfaces1ListSingleIds
        # zTest=np.array(vSurfaces2ColorMaskIntIdColcowithvSurfaces1)
        # vSurfaces2ColorMaskIntIdColcowithvSurfaces1[[1,5]]
        #ColormaskIdx is one more that the SurfacesIDIdx
        property_asel = [vSurfaces2ColorMaskIntIdColcowithvSurfaces1[i] for i in wSurfaces1ListSingleIdx[0].tolist()]
        flattened  = [val for sublist in property_asel for val in sublist]
        flattened = [int(i)-1 for i in flattened if i != 0]#convert to int and Subtract one to get act surface Index
        wSurfaces2ListSinglePairedSurfaces1Ids = np.array(vSurfaces2Ids)[flattened]
    
        property_asel = [vSurfaces2ColorMaskIntIdColcowithvSurfaces1[i] for i in wSurfaces1ListDoubletIdx[0].tolist()]
        flattened  = [val for sublist in property_asel for val in sublist]
        flattened = [int(i)-1 for i in flattened if i != 0]#convert to int and Subtract one to get act surfaceIndex
        wSurfaces2ListDoubletPairedSurfaces1Ids = np.array(vSurfaces2Ids)[flattened]
    
        property_asel = [vSurfaces2ColorMaskIntIdColcowithvSurfaces1[i] for i in wSurfaces1ListTripletIdx[0].tolist()]
        flattened  = [val for sublist in property_asel for val in sublist]
        flattened = [int(i)-1 for i in flattened if i != 0]#convert to int and Subtract one to get act surface INdex
        wSurfaces2ListTripletPairedSurfaces1Ids = np.array(vSurfaces2Ids)[flattened]
    
        property_asel = [vSurfaces2ColorMaskIntIdColcowithvSurfaces1[i] for i in wSurfaces1ListQuadrupletIdx[0].tolist()]
        flattened  = [val for sublist in property_asel for val in sublist]
        flattened = [int(i)-1 for i in flattened if i != 0]#convert to int and Subtract one to get act surface Index
        wSurfaces2ListQuadrupletPairedSurfaces1Ids = np.array(vSurfaces2Ids)[flattened]
    
    #PairedSurfaces1 with surfaces2
        property_asel = [vSurfaces1ColorMaskIntIdColcowithvSurfaces2[i] for i in wSurfaces2ListSingleIdx[0].tolist()]
        flattened  = [val for sublist in property_asel for val in sublist]
        flattened = [int(i)-1 for i in flattened if i != 0]#convert to int and Subtract one to get act surface Index
        wSurfaces1ListSinglePairedSurfaces2Ids = np.array(vSurfaces1Ids)[flattened]
    
        property_asel = [vSurfaces1ColorMaskIntIdColcowithvSurfaces2[i] for i in wSurfaces2ListDoubletIdx[0].tolist()]
        flattened  = [val for sublist in property_asel for val in sublist]
        flattened = [int(i)-1 for i in flattened if i != 0]#convert to int and Subtract one to get act surface Index
        wSurfaces1ListDoubletPairedSurfaces2Ids = np.array(vSurfaces1Ids)[flattened]
    
        property_asel = [vSurfaces1ColorMaskIntIdColcowithvSurfaces2[i] for i in wSurfaces2ListTripletIdx[0].tolist()]
        flattened  = [val for sublist in property_asel for val in sublist]
        flattened = [int(i)-1 for i in flattened if i != 0]#convert to int and Subtract one to get act surface Index
        wSurfaces1ListTripletPairedSurfaces2Ids = np.array(vSurfaces1Ids)[flattened]
    
        property_asel = [vSurfaces1ColorMaskIntIdColcowithvSurfaces2[i] for i in wSurfaces2ListQuadrupletIdx[0].tolist()]
        flattened  = [val for sublist in property_asel for val in sublist]
        flattened = [int(i)-1 for i in flattened if i != 0]#convert to int and Subtract one to get act surface Idx
        wSurfaces1ListQuadrupletPairedSurfaces2Ids = np.array(vSurfaces1Ids)[flattened]
    
        #Create working array for Spots2
        vNewSpots2_Stats = np.zeros([vNumberOfSurfaces2,14])
        vNewSpots2_Stats[:,0]=vSurfaces2Ids
    
        #Second Set Inverted Coloc
        #Create working array for Spots1
        vNewSpots1_Stats = np.zeros([vNumberOfSurfaces1,14])
        vNewSpots1_Stats[:,0]=vSurfaces1Ids
        ####################
    ###############################################################################
    ##############################################################################
    
        ####################
        aStatStart = 1
        #Create dummy variable to add for Spot2 Single,Doublets, etc...
        #Start new stats at previous time point to get continuous numbers across time
        vStatSingles_vObjects2 = np.arange(aStatStart + max(vNewSpots2_Stats[:,1]), len(wSurfaces2ListSingleIds) + max(vNewSpots2_Stats[:,1]+1))
        vStatDoublets_vObjects2 = np.arange(aStatStart + max(vNewSpots2_Stats[:,2]), len(wSurfaces2ListDoubletIds)/2 + max(vNewSpots2_Stats[:,2]+1))
        vStatDoublets_vObjects2 = np.repeat(vStatDoublets_vObjects2, 2)
        vStatTriplets_vObjects2 = np.arange(aStatStart + max(vNewSpots2_Stats[:,3]), len(wSurfaces2ListTripletIds)/3 + max(vNewSpots2_Stats[:,3]+1))
        vStatTriplets_vObjects2 = np.repeat(vStatTriplets_vObjects2, 3)
        vStatQuadruplets_vObjects2 = np.arange(aStatStart + max(vNewSpots2_Stats[:,4]), len(wSurfaces2ListQuadrupletIds)/4 + max(vNewSpots2_Stats[:,4]+1))
        vStatQuadruplets_vObjects2 = np.repeat(vStatQuadruplets_vObjects2, 4)
    
        vStatSingles_vObjects1 = np.arange(aStatStart + max(vNewSpots2_Stats[:,1]), len(wSurfaces1ListSingleIds) + max(vNewSpots2_Stats[:,1]+1))
        vStatDoublets_vObjects1 = np.arange(aStatStart + max(vNewSpots2_Stats[:,2]), len(wSurfaces1ListDoubletIds)/2 + max(vNewSpots2_Stats[:,2]+1))
        vStatDoublets_vObjects1 = np.repeat(vStatDoublets_vObjects1, 2)
        vStatTriplets_vObjects1 = np.arange(aStatStart + max(vNewSpots2_Stats[:,3]), len(wSurfaces1ListTripletIds)/3 + max(vNewSpots2_Stats[:,3]+1))
        vStatTriplets_vObjects1 = np.repeat(vStatTriplets_vObjects1, 3)
        vStatQuadruplets_vObjects1 = np.arange(aStatStart + max(vNewSpots2_Stats[:,4]), len(wSurfaces1ListQuadrupletIds)/4 + max(vNewSpots2_Stats[:,4]+1))
        vStatQuadruplets_vObjects1 = np.repeat(vStatQuadruplets_vObjects1, 4)
    
    
    #Create new statID for Singles Doublets,Triplets,Quadruplets for Surfaces1
    ############
        if not wSurfaces1ListSingleIds.size == 0:
            np.put(vNewSpots1_Stats[:,1],
                   wSurfaces1ListSingleIdx,
                   np.arange(aStatStart + max(vNewSpots1_Stats[:,1]), len(wSurfaces1ListSingleIds) + max(vNewSpots1_Stats[:,1]+1)).tolist())
        if not wSurfaces1ListDoubletIds.size == 0:
            np.put(vNewSpots1_Stats[:,2],
                   wSurfaces1ListDoubletIdx,
                   np.arange(aStatStart + max(vNewSpots1_Stats[:,2]), len(wSurfaces1ListDoubletIds) + max(vNewSpots1_Stats[:,2]+1)).tolist())
        if not wSurfaces1ListTripletIds.size == 0:
            np.put(vNewSpots1_Stats[:,3],
                   wSurfaces1ListTripletIdx,
                   np.arange(aStatStart + max(vNewSpots1_Stats[:,3]), len(wSurfaces1ListTripletIds) + max(vNewSpots1_Stats[:,3]+1)).tolist())
        if not wSurfaces1ListQuadrupletIds.size == 0:
            np.put(vNewSpots1_Stats[:,4],
                   wSurfaces1ListQuadrupletIdx,
                   np.arange(aStatStart + max(vNewSpots1_Stats[:,4]), len(wSurfaces1ListQuadrupletIds) + max(vNewSpots1_Stats[:,4]+1)).tolist())
    
    #Create new statID for Singles Doublets,Triplets,Quadruplets for Surfaces2
    ############
        if not wSurfaces2ListSingleIds.size == 0:
            np.put(vNewSpots2_Stats[:,1],
                   wSurfaces2ListSingleIdx,
                   np.arange(aStatStart + max(vNewSpots2_Stats[:,1]), len(wSurfaces2ListSingleIds) + max(vNewSpots2_Stats[:,1]+1)).tolist())
        if not wSurfaces2ListDoubletIds.size == 0:
            np.put(vNewSpots2_Stats[:,2],
                   wSurfaces2ListDoubletIdx,
                   np.arange(aStatStart + max(vNewSpots2_Stats[:,2]), len(wSurfaces2ListDoubletIds) + max(vNewSpots2_Stats[:,2]+1)).tolist())
        if not wSurfaces2ListTripletIds.size == 0:
            np.put(vNewSpots2_Stats[:,3],
                   wSurfaces2ListTripletIdx,
                   np.arange(aStatStart + max(vNewSpots2_Stats[:,3]), len(wSurfaces2ListTripletIds) + max(vNewSpots2_Stats[:,3]+1)).tolist())
        if not wSurfaces1ListQuadrupletIds.size == 0:
            np.put(vNewSpots2_Stats[:,4],
                   wSurfaces2ListQuadrupletIdx,
                   np.arange(aStatStart + max(vNewSpots2_Stats[:,4]), len(wSurfaces2ListQuadrupletIds) + max(vNewSpots2_Stats[:,4]+1)).tolist())
    ############
    ############
        #Create Labels for vSurfaces1
        wLabelList = []
        for i in range(len(wSurfaces1ListSingleIds)):
            vLabelCreate = vFactory.CreateObjectLabel(wSurfaces1ListSingleIds[i], 'Coloc', '1_Singles')
            wLabelList.append(vLabelCreate)
        vSurfaces1.SetLabels(wLabelList)
        wLabelList = []
        for i in range(len(wSurfaces1ListDoubletIds)):
            vLabelCreate = vFactory.CreateObjectLabel(wSurfaces1ListDoubletIds[i], 'Coloc', '2_Doublets')
            wLabelList.append(vLabelCreate)
        vSurfaces1.SetLabels(wLabelList)
        wLabelList = []
        for i in range(len(wSurfaces1ListTripletIds)):
            vLabelCreate = vFactory.CreateObjectLabel(wSurfaces1ListTripletIds[i], 'Coloc', '3_Triplets')
            wLabelList.append(vLabelCreate)
        vSurfaces1.SetLabels(wLabelList)
        wLabelList = []
        for i in range(len(wSurfaces1ListQuadrupletIds)):
            vLabelCreate = vFactory.CreateObjectLabel(wSurfaces1ListQuadrupletIds[i], 'Coloc', '4_Quadruplets')
            wLabelList.append(vLabelCreate)
        vSurfaces1.SetLabels(wLabelList)
        wLabelList = []
        wLabelIndices=np.where(~np.any(vNewSpots1_Stats[:,1:5][:],axis=1))
        for i in range(wLabelIndices[0].size):
            vLabelCreate = vFactory.CreateObjectLabel(vSurfaces1Ids[wLabelIndices[0][i]], 'Coloc', ' Non-Colocalized')
            wLabelList.append(vLabelCreate)
        vSurfaces1.SetLabels(wLabelList)
        wLabelList = []
        # for i in range(len(wLabelIndices)):
        #     vLabelCreate = vFactory.CreateObjectLabel(wLabelIndices[i], 'Coloc', ' Special')
        #     wLabelList.append(vLabelCreate)
        # vSurfaces1.SetLabels(wLabelList)
    
    
        ##############################################################################
        #Create Labels for vSurfaces2
        wLabelList = []
        for i in range(len(wSurfaces2ListSingleIds)):
            vLabelCreate = vFactory.CreateObjectLabel(wSurfaces2ListSingleIds[i], 'Coloc', '1_Singles')
            wLabelList.append(vLabelCreate)
        vSurfaces2.SetLabels(wLabelList)
        wLabelList = []
        for i in range(len(wSurfaces2ListDoubletIds)):
            vLabelCreate = vFactory.CreateObjectLabel(wSurfaces2ListDoubletIds[i], 'Coloc', '2_Doublets')
            wLabelList.append(vLabelCreate)
        vSurfaces2.SetLabels(wLabelList)
        wLabelList = []
        for i in range(len(wSurfaces2ListTripletIds)):
            vLabelCreate = vFactory.CreateObjectLabel(wSurfaces2ListTripletIds[i], 'Coloc', '3_Triplets')
            wLabelList.append(vLabelCreate)
        vSurfaces2.SetLabels(wLabelList)
        wLabelList = []
        for i in range(len(wSurfaces2ListQuadrupletIds)):
            vLabelCreate = vFactory.CreateObjectLabel(wSurfaces2ListQuadrupletIds[i], 'Coloc', '4_Quadruplets')
            wLabelList.append(vLabelCreate)
        vSurfaces2.SetLabels(wLabelList)
        wLabelList = []
        wLabelIndices=np.where(~np.any(vNewSpots2_Stats[:,1:5][:],axis=1))
        for i in range(wLabelIndices[0].size):
            vLabelCreate = vFactory.CreateObjectLabel(vSurfaces2Ids[wLabelIndices[0][i]], 'Coloc', ' Non-Colocalized')
            wLabelList.append(vLabelCreate)
        vSurfaces2.SetLabels(wLabelList)
        wLabelList = []
        # for i in range(len(wLabelIndices)):
        #     vLabelCreate = vFactory.CreateObjectLabel(wLabelIndices[i], 'Coloc', ' Special')
        #     wLabelList.append(vLabelCreate)
        # vSurfaces2.SetLabels(wLabelList)
    
    
        vSurfaces1.SetName(vSurfaces1.GetName()+' -- ColocAnalyzed')
        vImarisApplication.GetSurpassScene().AddChild(vSurfaces1, -1)
        vSurfaces2.SetName(vSurfaces2.GetName()+' -- ColocAnalyzed')
        vImarisApplication.GetSurpassScene().AddChild(vSurfaces2, -1)
    
    
    #######################
    #######################
    master.destroy()
    master.mainloop()
    
    

