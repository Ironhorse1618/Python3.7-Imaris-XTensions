#
#Written by Matthew J. Gastinger
#June 2022
#
    # <CustomTools>
    #     <Menu>
    #         <Submenu name="Surfaces Functions">
    #             <Item name="Kiss and Run2 - Python" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Kiss_and_Run_beta2(%i)</Command>
    #             </Item>
    #         </Submenu>
    #         <Submenu name="Spots Functions">
    #             <Item name="Kiss and Run2 - Python" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Kiss_and_Run_beta2(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSurfaces">
    #             <Item name="Kiss and Run2 - Python" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Kiss_and_Run_beta2(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #         <SurpassComponent name="bpSpots">
    #             <Item name="Kiss and Run2 - Python" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Kiss_and_Run_beta2(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #     </SurpassTab>
    # </CustomTools>

#Description:



# Track Statistics:
#     Number of Contacts
#     Percent Number of Contacts
#     Number of Non Contacts
#     Number of Prolonged Contacts - contact even 2 or more consecutive timepoints
#     Total Contact time - time duration of
#     Total non-contact time
#     Longest Contact event
#     Mean duration contact events

# Overall Statistics:
#     Total Number of Contacts per TimePoint
#     Percentage Contacts per TimePoint

from itertools import groupby
from statistics import mean
import numpy as np

import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter.ttk import *
import ImarisLib

def XT_MJG_Kiss_and_Run_beta2(aImarisId):
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
     # Get Surpass Selection
    vSurpassSelection= vImarisApplication.GetSurpassSelection()
    vSurpassSelectionName=vSurpassSelection.GetName()

    ############################################################################
    ############################################################################
     #Get image properties #timepoints #channels
     #Get the extents of the image
    vDataMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vDataMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vDataSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    aXvoxelSpacing= (vDataMax[0]-vDataMin[0])/vDataSize[0]
    aYvoxelspacing= (vDataMax[1]-vDataMin[1])/vDataSize[1]
    aZvoxelSpacing = round((vDataMax[2]-vDataMin[2])/vDataSize[2],3)
    vDefaultSmoothingFactor=round(aXvoxelSpacing*2,2)

    ############################################################################
    #########################################################
    #Count and find Surpass objects in Scene
    vNumberSurpassItems=vImarisApplication.GetSurpassScene().GetNumberOfChildren()
    vNamesSurfaces=[]
    vNamesSpots=[]
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
            vNamesSurfaces.append(vDataItem.GetName())
            NamesSurfaceIndex.append(vChildIndex)
        elif IsSpot:
            vSurpassSpots = vSurpassSpots+1
            vNamesSpots.append(vDataItem.GetName())
            NamesSpotsIndex.append(vChildIndex)
        elif IsFilament:
            vSurpassFilaments = vSurpassFilaments+1
            NamesFilaments.append(vDataItem.GetName(),)
            NamesFilamentIndex.append(vChildIndex)

    #####################################################
    #Making the Listbox for the Primary surface
    main = Tk()
    main.title("Choose one Primary Object")
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
    names.set(vNamesSurfaces)
    lstbox = Listbox(main, listvariable=names, selectmode=SINGLE, width=20, height=10)
    lstbox.grid(column=0, row=0, columnspan=2)
    def select():
        global PrimarySelection
        PrimarySelection = list()
        PrimarySurfaceSceneIndex = lstbox.curselection()
        for i in PrimarySurfaceSceneIndex:
            entrada = lstbox.get(i)
            PrimarySelection.append(entrada)
        #Test for the correct number selected
        if len(PrimarySelection)!=1:
            messagebox.showerror(title='Surface menu',
                          message='Please Select 1 surfaces')
            main.mainloop()
        else:
            main.destroy()

    btn = Button(main, text="Choose Primary Surface", command=select)
    btn.grid(column=1, row=1)
    #Selects the top 2 items in the list
    lstbox.selection_set(0)
    main.mainloop()
    ####################################################################
    ####################################################################
    #Making the Listbox for the Secondary converage surface
    main = Tk()
    main.title("Choose ONE tracked object to Analyze")
    main.geometry("+150+300")
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
    namesSurfaces = StringVar()
    namesSurfaces.set(vNamesSurfaces)
    lstbox = Listbox(main, listvariable=namesSurfaces, selectmode=SINGLE, width=20, height=10)
    lstbox.grid(column=0, row=0, columnspan=2)

    namesSpots = StringVar()
    namesSpots.set(vNamesSpots)
    lstbox2 = Listbox(main, listvariable=namesSpots, selectmode=SINGLE, width=20, height=10)
    lstbox2.grid(column=2, row=0, columnspan=2)
    def selectSurface():
        global SecondarySelectionSurfaces,qObjectAnalyzed
        SecondarySelectionSurfaces = list()
        selection = lstbox.curselection()
        for i in selection:
            entrada = lstbox.get(i)
            SecondarySelectionSurfaces.append(entrada)
    #Test for the correct number selected
        if len(SecondarySelectionSurfaces)!=1:
            messagebox.showerror(title='Surface menu',
                          message='Please Select 1 surfaces')
            main.mainloop()
        elif SecondarySelectionSurfaces==PrimarySelection:
            messagebox.showerror(title='Surface menu',
                          message='Primary and Target Object are the same!!/n'
                          'Please Select Different Object')
            main.mainloop()
        else:
            qObjectAnalyzed = 'Surfaces'
            main.destroy()

    def selectSpots():
        global SecondarySelectionSpots, qObjectAnalyzed
        SecondarySelectionSpots = list()
        selection = lstbox2.curselection()
        for i in selection:
            entrada = lstbox2.get(i)
            SecondarySelectionSpots.append(entrada)
    #Test for the correct number selected
        if len(SecondarySelectionSpots)!=1:
            messagebox.showerror(title='Surface menu',
                          message='Please Select 1 Spots')
            main.mainloop()
        elif SecondarySelectionSpots==PrimarySelection:
            messagebox.showerror(title='Surface menu',
                          message='Primary and Target Object are the same!!/n'
                          'Please Select Different Object')
            main.mainloop()
        else:
            qObjectAnalyzed = 'Spots'
            main.destroy()

    Button1 = Button(main, text="ANALYZE tracked Surfaces", command=selectSurface)
    Button1.grid(column=1, row=1)

    Button2 = Button(main, text="ANALYZE tracked Spots", command=selectSpots)
    Button2.grid(column=2, row=1)
    #Select Surpass Selected object
    qCheckSurfaces = [idx for idx, val in enumerate(vNamesSurfaces) if val in vSurpassSelectionName]
    qCheckSpots = [idx for idx, val in enumerate(vNamesSpots) if val in vSurpassSelectionName]
    if qCheckSurfaces:
        lstbox.selection_set([vNamesSurfaces.index(vSurpassSelectionName)])
    if qCheckSpots:
        lstbox2.selection_set([vNamesSpots.index(vSurpassSelectionName)])
        vNamesSpots.index(vSurpassSelectionName)
    main.mainloop()

    ####################################################################
    ####################################################################
    #INput Distance THreshold of Surface overlap %
    main2 = Tk()
    main2.title("Kiss and Run")
    main2.geometry("+250+100")
    main2.attributes("-topmost", True)

    #################################################################
    #Set input in center on screen
    # Gets the requested values of the height and widht.
    windowWidth = main2.winfo_reqwidth()
    windowHeight = main2.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(main2.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(main2.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    main2.geometry("+{}+{}".format(positionRight, positionDown))
    ##################################################################

    var1 = tk.IntVar(value=1)
    var2 = tk.IntVar(value=0)
    qOverlapMethod = False
    qDistanceMethod = False
    def Threshold ():
        global qDistanceThreshold, qSurfaceOverlapPercentage
        global qDistanceMethod,qOverlapMethod
        qDistanceThreshold=[float(Entry1.get())]
        qSurfaceOverlapPercentage=[float(Entry2.get())]

        if var1.get()==1 and var2.get()==1:
            messagebox.showerror(title='Selection',
                          message='Please Choose only 1 option!!!')
            main2.mainloop()
        elif var1.get()==0 and var2.get()==0:
            messagebox.showerror(title='Selection',
                          message='Please Choose 1 !!!')
            main2.mainloop()
        elif var1.get()==1 and var2.get()==0:
            qDistanceMethod = True
            qOverlapMethod = False
        elif var1.get()==0 and var2.get()==1:
            qOverlapMethod = True
            qDistanceMethod = False

        main2.destroy()
        main2.mainloop()

    tk.Label(main2, width=30, font=("Arial", 13, 'bold'),text='Choose One Contact Event Method').grid(row=0, column=0, sticky=W)
    tk.Checkbutton(main2, text='Distance Threshold',
                   variable=var1, onvalue=1, offvalue=0).grid(row=1, column=0, sticky=W)
    Entry1=Entry(main2,justify='center',width=4)
    Entry1.grid(row=1, column=0,sticky=W,padx=165)
    Entry1.insert(0, '0')

    tk.Checkbutton(main2, text='Overlap Percentage (%)',
                   variable=var2, onvalue=1, offvalue=0).grid(row=2, column=0, sticky=W)
    Entry2=Entry(main2,justify='center',width=4)
    Entry2.grid(row=2, column=0, sticky=W, padx=180)
    Entry2.insert(0, '20')

    btn = Button(main2, text="Analyze Contact Events", command=Threshold)
    btn.grid(column=0, row=3)

    main2.mainloop()


    ##################################################################
    ##################################################################
    #Create the Progress bar
    #Creating a separate Tkinter qProgressBar for progress bars
    qProgressBar=tk.Tk()
    qProgressBar.title("Kiss&Run Analysis")
    qProgressBar.geometry('280x70')
    qProgressBar.attributes("-topmost", True)
    # Create a progressbar widget
    progress_bar1 = ttk.Progressbar(qProgressBar, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)

    # And a label for it
    label_1 = tk.Label(qProgressBar, text="Kiss&Run Track Progress")

    # Use the grid manager
    label_1.grid(row=0, column=0,pady=10)

    progress_bar1.grid(row=0, column=1)
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

    # Necessary, as the qProgressBar object needs to draw the progressbar widget
    # Otherwise, it will not be visible on the screen
    qProgressBar.update_idletasks()
    progress_bar1['value'] = 0
    qProgressBar.update_idletasks()

    ####################################################################
    ####################################################################
    ####################################################################
    # get the Selected surfaces and Spots
    vDataItem=vScene.GetChild(NamesSurfaceIndex[(vNamesSurfaces.index( ''.join(map(str, PrimarySelection[0]))))])
    vSurfacesPrimary=vImarisApplication.GetFactory().ToSurfaces(vDataItem)

    if qObjectAnalyzed == 'Spots':
        vDataItem=vScene.GetChild(NamesSpotsIndex[(vNamesSpots.index( ''.join(map(str, SecondarySelectionSpots[0]))))])
        vObjects=vImarisApplication.GetFactory().ToSpots(vDataItem)
        vSpotsRadius = vObjects.GetRadii()
        vSpotsPositionXYZ = vObjects.GetPositionsXYZ()
    elif qObjectAnalyzed == 'Surfaces':
        vDataItem=vScene.GetChild(NamesSurfaceIndex[(vNamesSurfaces.index( ''.join(map(str, SecondarySelectionSurfaces[0]))))])
        vObjects=vImarisApplication.GetFactory().ToSurfaces(vDataItem)

    ####################################################################
    ####################################################################
    # get all spots in selected Surpass object
    if qObjectAnalyzed == 'Spots':
        # vSpotsRadius = vObjects.GetRadii()
        # vSpotsPositionXYZ = vObjects.GetPositionsXYZ()
        # vSpotsTime = vObjects.GetIndicesT()
        vObjectEdges = vObjects.GetTrackEdges()
        vObjectTrackIds = vObjects.GetTrackIds()
        vObjectTrackIDsUnique = np.unique(np.array(vObjectTrackIds))
        vObjectTotalNumberOfTracks = len(np.unique(np.array(vObjectTrackIds)))
        vAllObjectsIds = vObjects.GetIds()
    #Get Statistics
        zStatisticShortestDistance = np.array(vObjects.GetStatisticsByName('Shortest Distance to Surfaces').mValues)
        zStatisticShortestDistanceID = np.array(vObjects.GetStatisticsByName('Shortest Distance to Surfaces').mIds)
        zStatisticShortestDistancefactors = np.array(vObjects.GetStatisticsByName('Shortest Distance to Surfaces').mFactors)
        zStatisticTimeIndex = np.array([vObjects.GetStatisticsByName('Time Index').mValues])
        zStatisticTimePoint = np.array([vObjects.GetStatisticsByName('Time').mValues])

    elif qObjectAnalyzed == 'Surfaces':
        vObjectEdges = vObjects.GetTrackEdges()
        vObjectTrackIds = vObjects.GetTrackIds()
        vObjectTrackIDsUnique = np.unique(np.array(vObjectTrackIds))
        vObjectTotalNumberOfTracks = len(np.unique(np.array(vObjectTrackIds)))
        vAllObjectsIds = vObjects.GetIds()
    #Get Statistics
        zStatisticShortestDistance = np.array(vObjects.GetStatisticsByName('Shortest Distance to Surfaces').mValues)
        zStatisticShortestDistanceID = np.array(vObjects.GetStatisticsByName('Shortest Distance to Surfaces').mIds)
        zStatisticShortestDistancefactors = np.array(vObjects.GetStatisticsByName('Shortest Distance to Surfaces').mFactors)
        zStatisticTimeIndex = np.array([vObjects.GetStatisticsByName('Time Index').mValues])
        zStatisticTimePoint = np.array([vObjects.GetStatisticsByName('Time').mValues])

    #Get Statnames
    # zz=np.unique(np.array(vObjects.GetStatisticsNames()))
    # zz=np.unique(np.array(vObjects.GetStatisticsNames()))

    #Find Object Statsistics value and ID for PrimarySurface selected
    #Test to see if Spots object has matching statistic if not pop up error message
    if PrimarySelection in zStatisticShortestDistancefactors:
        zStatisticShortestDistancePrimary = np.array([zStatisticShortestDistance[(np.where(zStatisticShortestDistancefactors[1] == PrimarySelection))[0].tolist()]])
        zStatisticShortestDistanceIDPrimary = np.array([zStatisticShortestDistanceID[(np.where(zStatisticShortestDistancefactors[1] == PrimarySelection))[0].tolist()]])
        #Create compiled data
        #Row0=ShortestDistance
        #Row1=TimeIndex
        #Row2=TimePoint
        #Row3=ShortestDistance ObjectID
        zCombined=np.vstack([zStatisticShortestDistancePrimary, zStatisticTimeIndex,zStatisticTimePoint,zStatisticShortestDistanceIDPrimary])

        qAdjRow = 0
        qThreshold = qDistanceThreshold
        #Add Surface specific statistics (OverlapVolumeRatio)
        if (qObjectAnalyzed == 'Surfaces') and (qOverlapMethod == True):
            qAdjRow = 4
            qThreshold = qSurfaceOverlapPercentage
            zStatisticOverlapVolumeRatio = np.array(vObjects.GetStatisticsByName('Overlapped Volume Ratio to Surfaces').mValues)
            zStatisticOverlapVolumeRatioID = np.array(vObjects.GetStatisticsByName('Overlapped Volume Ratio to Surfaces').mIds)
            zStatisticOverlapVolumeRatiofactors = np.array(vObjects.GetStatisticsByName('Overlapped Volume Ratio to Surfaces').mFactors)
            zStatisticOverlapVolumeRatioPrimary = np.array([zStatisticOverlapVolumeRatio[(np.where(zStatisticOverlapVolumeRatiofactors[1] == PrimarySelection))[0].tolist()]])
            zStatisticOverlapVolumeRatioIDPrimary = np.array([zStatisticOverlapVolumeRatioID[(np.where(zStatisticOverlapVolumeRatiofactors[1] == PrimarySelection))[0].tolist()]])
            #Test is the NEw Surface stat matched ObjectID order compared to ShortestDistance...
            if np.array_equiv(zStatisticShortestDistanceIDPrimary, zStatisticOverlapVolumeRatioIDPrimary):
            #Row4=OverlapVolumeRatio
                zCombined=np.vstack([zCombined,zStatisticOverlapVolumeRatioPrimary])
            else:
                #ReOrder the values to match Shortest Distance ID order Row#3
                _,zReOrderIndex = np.where((zStatisticShortestDistanceIDPrimary[0])[:,None] == zStatisticOverlapVolumeRatioIDPrimary[0])
                zStatisticOverlapVolumeRatioPrimary=(zStatisticOverlapVolumeRatioPrimary[0])[zReOrderIndex]
                #Row4=OverlapVolumeRatio
                zCombined=np.vstack([zCombined,zStatisticOverlapVolumeRatioPrimary])
    #
                # xFirstArray = np.array([17,18,19,20,21,22])
                # xSecondArray = np.array([18,17,20,19,22,21])
                # xSecondArrayValues = np.array([222,111,333,444,555,999])

                # _,xReOrderIndex = np.where(xFirstArray[:,None] == xSecondArray)
                # xSecondArrayValues[xReOrderIndex]

    else:
        messagebox.showerror(title='Distance Calculation error',
                         message ='ERROR - Selected Tracked object \n'
                         'Does not have Object-Object Statsistics Checked!!! \n'
                         'Please check the Statistic measure and Restart XTension')
        main.destroy()
        exit()

    ###############################################################################
    ###############################################################################
    #loop each track
    wAllworkingTrackData = []
    wAllworkingTrackDataForOverallStat = []
    wPerTrackTotalNumberOfContacts = []
    wPerTrackPercentageOfContact = []
    wPerTrackTotalNumberOfNonContacts = []
    wPerTrackPercentageOfNonContact = []
    wPerTrackLengthMaxContactEvents = []
    wPerTrackLengthMeanContactEvents = []
    wOverallTrackLengthContactEventsALL = []
    wNumberOfProlongedContactEventsPerTrack = []
    wNumberOfContactEventsPerTrack = []

    for aTrackLoopIndex in range (len(vObjectTrackIDsUnique)):
        wPerTrackLengthContactEvents = []
        #grab current track edges
        zCurrentObjectsEdgesperTrack = [vObjectEdges[index] for index in np.where(vObjectTrackIds==vObjectTrackIDsUnique[aTrackLoopIndex])[0].tolist()]
        #grab current track indices
        zCurrentObjectIndex = np.unique(np.array([num for elem in zCurrentObjectsEdgesperTrack for num in elem])).tolist()
        #grab current track spotIDs
        zCurrentObjectIDs = [ vAllObjectsIds[i] for i in zCurrentObjectIndex]
        #Find indices for all ObjectIDs in current track
        zCurrentIndices=np.hstack([np.where(zCombined[3]==i) for i in zCurrentObjectIDs]).tolist()
        zCurrentIndices=[item for sublist in zCurrentIndices for item in sublist]
        #Grab values from the master list for current track
        zCurrentTrack = zCombined[:, zCurrentIndices]
        #ReOrder track based on Timeindex - assuming no branching
        zCurrentTrack=zCurrentTrack[:, zCurrentTrack[1, :].argsort()]

        #Test whether the current track has gap with no spot
        qTrackContinuity=sorted(zCurrentTrack[1]) == list(range(int(min(zCurrentTrack[1])), int(max(zCurrentTrack[1])+1)))

        aCount = 0
        if qTrackContinuity == False:
            #Find the missing integers
            wTrackContinuity = [x for x in range(int(min(zCurrentTrack[1])),int(max(zCurrentTrack[1]))+1)]#Perfect continuous range
            c,d = set(zCurrentTrack[1]),set(wTrackContinuity)
            zMissingInts = list(d-c)
            # print(list(d-c))
            zMissingInts.sort()
            #Add empty column with fixed value at that missing point
        #loop for each missing Integer
            for aIndex in range(len(zMissingInts)):
                #set fake colume at same height as current track
                if qOverlapMethod == True:
                    aNew_column = ['999999', zMissingInts[aIndex],999999,999999,-999999]
                    aCount = aCount + 1
                else:
                    aNew_column = ['999999', zMissingInts[aIndex],999999,999999]
                    aCount = aCount + 1
                aInsertIndex=(np.where(zCurrentTrack[1]==zMissingInts[aIndex]-1))[0].tolist()
                zCurrentTrack = np.insert(zCurrentTrack, aInsertIndex[0]+1, aNew_column, axis=1)

        wPerTrackTotalNumberOfContacts.append(np.count_nonzero((zCurrentTrack[0+qAdjRow] <= qThreshold)
                                              & (zCurrentTrack[0+qAdjRow]!=999999)))
        wPerTrackTotalNumberOfNonContacts.append(np.count_nonzero((zCurrentTrack[0+qAdjRow] > qThreshold)
                                              & (zCurrentTrack[0+qAdjRow]!=999999)))
        wPerTrackPercentageOfContact.append(np.count_nonzero(zCurrentTrack[0+qAdjRow] <= qThreshold)/((len(zCurrentTrack[0+qAdjRow])-aCount))*100)
        wPerTrackPercentageOfNonContact.append(np.count_nonzero(zCurrentTrack[0+qAdjRow] > qThreshold)/((len(zCurrentTrack[0+qAdjRow])-aCount))*100)
        #Test where corrected track objects have a contact event
        zCurrentTrackContactBoolean=(zCurrentTrack[0+qAdjRow] <= qThreshold)

        #Find All Contact Events by group
        #Create a boolean list for each sequential contact event
        wProlongedContactEventsPreview = [(list(group)) for key, group in groupby(zCurrentTrackContactBoolean) if key]
        wNumberOfProlongedContactEventsPerTrack.append(len([x for x in wProlongedContactEventsPreview if len(x)>1]))
        wNumberOfContactEventsPerTrack.append(len([x for x in wProlongedContactEventsPreview]))

        #Calculate time length for each contact event
        zCurrentTrackTemp = np.copy(zCurrentTrack)
        for j in range(len(wProlongedContactEventsPreview)):
            # len(wProlongedContactEventsPreview[j])#==4
            #Find first instance of contact
            # np.argmax(zCurrentTrack[0] < qThreshold)
            #First timepoint
            # zCurrentTrack[2][ np.argmax(zCurrentTrack[0] < qThreshold)]
            #Last timepoint
            # zCurrentTrack[2][np.argmax(zCurrentTrack[0] < qThreshold)+len(wProlongedContactEventsPreview[j])-1]
            #Test if contact even is single or multiple
            if len(wProlongedContactEventsPreview[j]) == 1:
                qTestIndex=np.argmax(zCurrentTrackTemp[0+qAdjRow] <= qThreshold)
                #Test is single contact event is at beginning or end or current track.
                if qTestIndex == 0:
                    wPerTrackLengthContactEvents.append((zCurrentTrackTemp[2][qTestIndex+1]-zCurrentTrackTemp[2][qTestIndex])/2)
                elif qTestIndex == (len(zCurrentTrackTemp[2])-1):
                    wPerTrackLengthContactEvents.append((zCurrentTrackTemp[2][qTestIndex]-zCurrentTrackTemp[2][qTestIndex-1])/2)
                #Delete single point at index
                zCurrentTrackTemp=np.delete(zCurrentTrack, np.argmax(zCurrentTrack[0+qAdjRow] <= qThreshold),1)
            else:
                wPerTrackLengthContactEvents.append((zCurrentTrackTemp[2][np.argmax(zCurrentTrackTemp[0+qAdjRow] <= qThreshold)+
                        len(wProlongedContactEventsPreview[j])-1]) - (zCurrentTrackTemp[2][ np.argmax(zCurrentTrackTemp[0+qAdjRow] <= qThreshold)]))
                #Crop numpy array at last index of the current contact event
                zCurrentTrackTemp=np.delete(zCurrentTrack,np.s_[0:np.argmax(zCurrentTrack[0+qAdjRow] <= qThreshold) + len(wProlongedContactEventsPreview[j])],axis=1)
                # np.argmax(zCurrentTrack[0] < qThreshold) + len(wProlongedContactEventsPreview[j])

        #Determine the MAX duration per track from all contact events
        if wPerTrackLengthContactEvents:
            wPerTrackLengthMaxContactEvents.append(max(wPerTrackLengthContactEvents))
            wPerTrackLengthMeanContactEvents.append(mean(wPerTrackLengthContactEvents))
            wOverallTrackLengthContactEventsALL.append(wPerTrackLengthContactEvents)
            wOverallContactTime=sum([x for xs in wOverallTrackLengthContactEventsALL for x in xs])

        else:
            wPerTrackLengthMaxContactEvents.append([0])
            wPerTrackLengthMeanContactEvents.append([0])
            wOverallTrackLengthContactEventsALL.append([0])

    ######################################
    #update progress bar
        progress_bar1['value'] = ((aTrackLoopIndex+1)/len(vObjectTrackIDsUnique)*100) #  % out of 100
        qProgressBar.update()

        #Collate all Tracks in one place
        wAllworkingTrackData.append(zCurrentTrack)

    zAllIndexOfContactEvents = []
    zAllTimePointsOfContactEvents = []
    wOverallTrackNumberContactEventsPerTimePoint = []

    # wAllworkingTrackData[aTrackIndex][1][np.where(wAllworkingTrackData[1][0] <= qThreshold)[0].tolist()].tolist()
    zAllTimePointsOfContactEvents.extend(zCombined[1][np.where(zCombined[0+qAdjRow] <= qThreshold)[0].tolist()].tolist())
    #find indices of all contact events - for LABEL creation??
    zAllIndexOfContactEvents.extend(zCombined[3][np.where(zCombined[0+qAdjRow] <= qThreshold)[0].tolist()].tolist())

    #count contact events per time point for Overall Stat object
    for aTimeIndex in range (vSizeT):
    # count numbers in the list which are greater than 5
        wOverallTrackNumberContactEventsPerTimePoint.append(len([elem for elem in zAllTimePointsOfContactEvents if elem == aTimeIndex+1]))

    #Calculate overl contact time
    wOverallContactTime=sum([x for xs in wOverallTrackLengthContactEventsALL for x in xs])

    #############################

    #Overall Stat Calcualtion
    wOverallTrackLengthContactEventsALL=np.array([x for xs in wOverallTrackLengthContactEventsALL for x in xs])
    #remove zeros
    wOverallTrackLengthContactEventsALL[wOverallTrackLengthContactEventsALL!=0]
    #Calculate Overall stats non-time related
    wOverallTrackMeanDurationContactEvents = np.mean(wOverallTrackLengthContactEventsALL)
    wOverallTrackNumberContactEvents = len(wOverallTrackLengthContactEventsALL)

    ###############################################################################
    #Adding Track statistics
    vTrackStatUnits=['']*len(vObjectTrackIDsUnique)
    vTrackStatFactors=[['Track']*len(vObjectTrackIDsUnique)]
    vTrackStatFactorName=['Category']
    ###############################################################################
    vTrackStatNames=[' Number of contacts'] * len(vObjectTrackIDsUnique)
    vObjects.AddStatistics(vTrackStatNames, wPerTrackTotalNumberOfContacts,
                                  vTrackStatUnits, vTrackStatFactors,
                                  vTrackStatFactorName, vObjectTrackIDsUnique.tolist())
    ###############################################################################
    vTrackStatNames=[' Number of non-contacts'] * len(vObjectTrackIDsUnique)
    vObjects.AddStatistics(vTrackStatNames, wPerTrackTotalNumberOfNonContacts,
                                  vTrackStatUnits, vTrackStatFactors,
                                  vTrackStatFactorName, vObjectTrackIDsUnique.tolist())
    ###############################################################################
    vTrackStatNames=[' Percentage contact'] * len(vObjectTrackIDsUnique)
    vObjects.AddStatistics(vTrackStatNames, wPerTrackPercentageOfContact,
                                  vTrackStatUnits, vTrackStatFactors,
                                  vTrackStatFactorName, vObjectTrackIDsUnique.tolist())
    ###############################################################################
    vTrackStatNames=[' Number of Prolonged contacts'] * len(vObjectTrackIDsUnique)
    vObjects.AddStatistics(vTrackStatNames, wNumberOfProlongedContactEventsPerTrack,
                                  vTrackStatUnits, vTrackStatFactors,
                                  vTrackStatFactorName, vObjectTrackIDsUnique.tolist())
    ###############################################################################
    # vTrackStatNames=[' Total time in Contact'] * len(vObjectTrackIDsUnique)
    # vObjects.AddStatistics(vTrackStatNames, wTotalTimeContactEventsPerTrack,
    #                               vTrackStatUnits, vTrackStatFactors,
    #                               vTrackStatFactorName, vObjectTrackIDsUnique.tolist())
    ###############################################################################
    #code to reflatten mixed list
    flatten = lambda *n: (e for a in n
        for e in (flatten(*a) if isinstance(a, (tuple, list)) else (a,)))
    wPerTrackLengthMaxContactEvents= list(flatten(wPerTrackLengthMaxContactEvents))

    vTrackStatNames=[' Max Duration Contact Event'] * len(vObjectTrackIDsUnique)
    vObjects.AddStatistics(vTrackStatNames, wPerTrackLengthMaxContactEvents,
                                  vTrackStatUnits, vTrackStatFactors,
                                  vTrackStatFactorName, vObjectTrackIDsUnique.tolist())
    ###############################################################################
    wPerTrackLengthMeanContactEvents= list(flatten(wPerTrackLengthMeanContactEvents))

    vTrackStatNames=[' Mean Duration Contact Events'] * len(vObjectTrackIDsUnique)
    vObjects.AddStatistics(vTrackStatNames, wPerTrackLengthMeanContactEvents,
                                  vTrackStatUnits, vTrackStatFactors,
                                  vTrackStatFactorName, vObjectTrackIDsUnique.tolist())
    ###############################################################################
    ###############################################################################
    #Insert an overall Statistics
    vOverallStatIds=[int(-1)]
    vOverallStatUnits=['']*vSizeT
    vOverallStatFactorsTime=list(range(1,vSizeT+1))
    vOverallStatFactors=[['Overall']*vSizeT,[str(i) for i in vOverallStatFactorsTime]]
    vOverallStatFactorNames=['FactorName','Time']
    ####################################################
    vOverallStatNames = [' Number of Contact Events per Time Point']*vSizeT
    vObjects.AddStatistics(vOverallStatNames, wOverallTrackNumberContactEventsPerTimePoint,
                                  vOverallStatUnits, vOverallStatFactors,
                                  vOverallStatFactorNames, vOverallStatIds*vSizeT)
    ####################################################
    # vOverallStatNames = [' Total Contact Time']*vSizeT
    # vObjects.AddStatistics(vOverallStatNames, wOverallContactTime,
    #                               vOverallStatUnits, vOverallStatFactors,
    #                               vOverallStatFactorNames, vOverallStatIds*vSizeT)


    vObjects.SetName(str(vObjects.GetName()) + ' - Analyzed Contact Events')
    vImarisApplication.GetSurpassScene().AddChild(vObjects, -1)

    qProgressBar.destroy()
    qProgressBar.mainloop()



    ###############################################################################
    ###############################################################################
    ###############################################################################
    # ###Find prolonged contact event!!! Working!!!
    # z=[0,0,0,1,1,1,0,0,0,0,1,1,1,1,0,0]
    # z=[False,False,False,True,True,True,True,False,False,False,False,True,True,False,False]
    # from itertools import groupby

    # wProlongedContactEvents=[(list(group)) for key, group in groupby(z) if key]
    # len(wProlongedContactEvents

    # z=[2,3,3,3,3],[1,2,3,5,6]
    # z=np.array(z)
    # #Check is time series is sequential
    # #If this statement is False there is a gap
    # sorted(z[1]) == list(range(min(z[1]), max(z[1])+1))

    # sorted(zCurrentTrack[1]) == list(range(int(min(zCurrentTrack[1])), int(max(zCurrentTrack[1])+1)))

    # np.count_nonzero((z[1]<6)&(z[1]>=0))

    # #Find the missing integers
    # # a=input() #[4,3,2,7,8,2,3,1]
    # b=[x for x in range(1,len(z[1])+1)]
    # c,d=set(z[1]),set(b)
    # zMissingInts=list(d-c)
    # print(list(d-c))


    # a=[1,2,4,6],[4,5,5,6]
    # a=np.array(a)
    # aNew_column = ['999999', 4]
    # aInsertIndex=1
    # aNEW = np.insert(a, aInsertIndex, new_column, axis=1)
