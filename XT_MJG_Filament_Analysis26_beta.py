# Filament Analysis
#
# Written by Matthew J. Gastinger
#
# Aug 2020 - Imaris 9.7.2
#
#
    #<CustomTools>
        #<Menu>
            #<Submenu name="Filaments Functions">
                #<Item name="Filament Analysis26 beta" icon="Python3">
                    #<Command>Python3XT::XT_MJG_Filament_Analysis26_beta(%i)</Command>
                #</Item>
            #</Submenu>
       #</Menu>
       #<SurpassTab>
           #<SurpassComponent name="bpFilaments">
               #<Item name="Filament Analysis26 beta" icon="Python3">
                   #<Command>Python3XT::XT_MJG_Filament_Analysis26_beta(%i)</Command>
               #</SurpassComponent>
           #</SurpassTab>
    #</CustomTools>

  # Description:
  #     This XTension will do several things:
  #     1)Estimate Dendrite and Filament intensity
  #           Each point along the filament consider a spot object at the current dendrite radius
  #           Intensity is calculated from the mean intensity of the spot object
  #     2)Find synaptic bouton(varicosities) place a spot at that point
  #           Diameter of the bouton (spot diameter)
  #     3)Find Spots Colocalized with Dendrite segements
  #           Number of  Spots per dendrite segment
  #           Distance of Colocalizaed spots to Starting point (soma)
  #           Number of Spots per Filament
  #     4)Intra Dendrite to Dendrite contacts
  #           Number of contacts per dendrtie
  #           Distance of contact to starting point (soma)
  #           Length of the contacts
  #           Number of contacts per Filament
  #     5)Filament to Filament contacts
  #           Finds all contacts with current filament with a new filament Object
  #     6)Generate NEW stats in the Filament object
  #           Dendrite mean intensity (for each channel)
  #           Spine intensity (not just the spine head, the whole spine)
  #           Bouton(varicosity) number per dendrite segment
  #           Bouton density
  #           Spot Colocalization within a certain distance of filament
  #           Spot Coloc Density per dendrite segment
  #     7)Display Filament as a population of Spots
  #           Visualize diameter/intensity along segments




#Python Dependancies:
    # numpy
    # tkinter
    # scipy
    # operator
    # itertools
    # statistics import mean
    # functools import reduce



import numpy as np
import time
import random
import statistics

# GUI imports
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
#import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.signal import peak_widths
from scipy.spatial.distance import cdist
from scipy.spatial.distance import pdist
from scipy.spatial import Delaunay

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
def XT_MJG_Filament_Analysis26_beta(aImarisId):
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
            NamesFilaments.append(vDataItem.GetName(),)
            NamesFilamentIndex.append(vChildIndex)
    ############################################################################

    #Dialog window
    ############################################################################
    window = tk.Tk()
    window.title('Filament Analysis')
    window.geometry('365x330')
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

    def Filament_options():
        global vOptionIntensity, vOptionFilamentToSpots,vOptionFilamentToSpotsMerge,vOptionBoutonThreshold, vOptionBoutonHeight, vOptionSomaThreshold,vOptionSomaThresholdValue
        global vOptionFilamentBoutonDetection, vOptionFilamentBoutoDetecionThreshold, vOptionFilamentCloseToSpots, vOptionFilamentToSpotsFill
        global vOptionFilamentSpotThreshold, vOptionDendriteToDendriteContact, vOptionFilamentToFilamentContact, NamesSpots, NamesSurfaces, NamesFilaments
        if (var1.get() == 0) and (var2.get() == 0) and (var4.get() == 0) and (var5.get() ==0) and (var7.get() ==0) and (var8.get()==0):
            messagebox.showerror(title='Filament Analysis menu',
                             message='Please Select ONE Analysis')
            window.mainloop()

        vOptionIntensity=var1.get()
        vOptionFilamentToSpots=var2.get()
        vOptionFilamentToSpotsMerge=var3.get()
        vOptionFilamentToSpotsFill=var6.get()
        vOptionFilamentBoutonDetection=var4.get()
        vOptionDendriteToDendriteContact=var7.get()
        vOptionFilamentCloseToSpots=var5.get()
        vOptionFilamentSpotThreshold=[float(Entry2.get())]
        vOptionFilamentToFilamentContact=var8.get()
        vOptionSomaThreshold=var9.get()

        if vOptionSomaThreshold==1:
            vOptionSomaThresholdValue=[float(Entry3.get())]
        else:
            vOptionSomaThresholdValue=0
        if NamesSpots==[] and vOptionFilamentCloseToSpots==1:
            messagebox.showerror(title='Spot Selection',
                             message='Please Create Spots Object!!')
            window.mainloop()
        if NamesFilaments==[] and vOptionFilamentToFilamentContact==1:
            messagebox.showerror(title='Filament Selection',
                             message='Please Create Filament Object!!')
            window.mainloop()

        if vOptionFilamentBoutonDetection==1 and (var4Low.get()+var4Med.get()+var4High.get())>1:
            messagebox.showerror(title='Filament Analysis menu',
                             message='Choose one Sensitivity')
            window.mainloop()

        if (var4.get() == 1) and (var4Low.get() == 1):
            vOptionBoutonThreshold=20
            vOptionBoutonHeight=0.5
        elif (var4.get() == 1) and (var4Med.get() == 1):
            vOptionBoutonThreshold=10
            vOptionBoutonHeight=.25
        elif (var4.get() == 1) and (var4High.get() == 1):
            vOptionBoutonThreshold=5
            vOptionBoutonHeight=0
        if (var2.get() == 0) and (var3.get() == 1):
            vOptionFilamentToSpots=1
        window.destroy()

    var1 = tk.IntVar(value=0)#intensity
    var2 = tk.IntVar(value=0)#Export Filament as a Spots object
    var3 = tk.IntVar(value=0)#Filament as spotd-- merge
    var4 = tk.IntVar(value=0)#Detect Boutons (varicosities)
    var5 = tk.IntVar(value=0)#Find Spots Close to Filaments
    var6 = tk.IntVar(value=0)#fill spots
    var7 = tk.IntVar(value=0)#dendrite dendrite contact
    var8 = tk.IntVar(value=0)#Filament filament contact
    var9 = tk.IntVar(value=0)#Filament filament contact


    var4Low=tk.IntVar(value=0)#bouton sensitivity
    var4Med=tk.IntVar(value=1)#bouton sensitivity
    var4High=tk.IntVar(value=0)#bouton sensitivity

    tk.Label(window, font="bold", text='Choose Analysis Options!').grid(row=0,column=0, padx=75,sticky=W)
    tk.Checkbutton(window, text='Measure Intensity of Dendrite',
                    variable=var1, onvalue=1, offvalue=0).grid(row=1, column=0, padx=40,sticky=W)
    tk.Checkbutton(window, text='Export Filament as a Spots object',
                    variable=var2, onvalue=1, offvalue=0).grid(row=2, column=0, padx=40,sticky=W)
    tk.Checkbutton(window, text='Fill Spots',
                    variable=var6, onvalue=1, offvalue=0).grid(row=4, column=0, padx=80,sticky=W)
    tk.Checkbutton(window, text='Merge all Filaments',
                    variable=var3, onvalue=1, offvalue=0).grid(row=3, column=0, padx=80,sticky=W)
    tk.Checkbutton(window, text='Detect Boutons (varicosities)',
                    variable=var4, onvalue=1, offvalue=0).grid(row=5, column=0, padx=40,sticky=W)

    tk.Checkbutton(window, text='Low',
                    variable=var4Low, onvalue=1, offvalue=0).grid(row=6, column=0, padx=80,sticky=W)
    tk.Checkbutton(window, text='Med',
                    variable=var4Med, onvalue=1, offvalue=0).grid(row=6, column=0, padx=130,sticky=W)
    tk.Checkbutton(window, text='High (sensitivity)',
                    variable=var4High, onvalue=1, offvalue=0).grid(row=6, column=0, padx=180,sticky=W)

    tk.Checkbutton(window, text='Find Spots Close to Filaments',
                    variable=var5, onvalue=1, offvalue=0).grid(row=7, column=0, padx=40,sticky=W)
    Entry2=Entry(window,justify='center',width=8)
    Entry2.grid(row=8, column=0, padx=80, sticky=W)
    Entry2.insert(0, '0.5')
    tk.Label(window, text='um (distance threshold)').grid(row=8,column=0, padx=130, sticky=W)
    tk.Checkbutton(window, text='Find Intra-Dendrite Contacts',
                    variable=var7, onvalue=1, offvalue=0).grid(row=9, column=0, padx=40,sticky=W)

    Entry3=Entry(window,justify='center',width=8)
    Entry3.grid(row=10, column=0, padx=275, sticky=W)
    Entry3.insert(0, '10')
    tk.Label(window, text='um').grid(row=10,column=0, padx=320, sticky=W)
    tk.Checkbutton(window, text='Remove Contacts near Starting Point',
                    variable=var9, onvalue=1, offvalue=0).grid(row=10, column=0, padx=65,sticky=W)


    tk.Checkbutton(window, text='Find Filament-Filament Contacts',
                    variable=var8, onvalue=1, offvalue=0).grid(row=11, column=0, padx=40,sticky=W)

    btn = Button(window, text="Analyze Filament", bg='blue', fg='white', command=Filament_options)
    btn.grid(column=0, row=12, sticky=W, padx=100, pady=5)


    window.mainloop()

    ############################################################################
    ############################################################################
    #Open Surpass menu to Select Spots Object
    if vOptionFilamentCloseToSpots==1:

        #####################################################
        #Making the Listbox for the Surpass menu
        main = tk.Tk()
        main.title("Surpass menu")
        main.geometry("+50+150")
        frame = ttk.Frame(main, padding=(3, 3, 12, 12))
        frame.grid(column=0, row=0, sticky=(N, S, E, W))
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
        lstbox = Listbox(frame, listvariable=names, selectmode=MULTIPLE, width=20, height=10)
        lstbox.grid(column=0, row=0, columnspan=2)
        def select():
            global ObjectSelection
            ObjectSelection = list()
            selection = lstbox.curselection()
            for i in selection:
                entrada = lstbox.get(i)
                ObjectSelection.append(entrada)
        #Test for the correct number selected
            if len(ObjectSelection)!=1:
                messagebox.showerror(title='Surface menu',
                                      message='Please Choose 1 Spots')
                main.mainloop()
            else:
                main.destroy()

        btn = ttk.Button(frame, text="Choose Spots Object", command=select)
        btn.grid(column=1, row=1)
        #Selects the top items in the list
        # lstbox.selection_set(0)
        main.mainloop()
    ####################################################################
    # get the Selected Spots in Surpass Scene
        vDataItem=vSurpassScene.GetChild(NamesSpotsIndex[(NamesSpots.index( ''.join(map(str, ObjectSelection[0]))))])
        vSpots=vImarisApplication.GetFactory().ToSpots(vDataItem)
    ####################################################################
    #Test if scene has Spots object
     #get the spot coordinates
        vSpotsColocPositionsXYZ = vSpots.GetPositionsXYZ()
        vSpotsColocRadius = vSpots.GetRadiiXYZ()
        vSpotsColocTimeIndices = vSpots.GetIndicesT()
        vSpotsColocCount = len(vSpotsColocRadius)
        vSpotsId = vSpots.GetIds()
    ####################################################################
    ####################################################################


    #Open Surpass menu to Select Filament Object
    if vOptionFilamentToFilamentContact==1:

        #####################################################
        #Making the Listbox for the Surpass menu
        main = tk.Tk()
        main.title("Surpass menu")
        main.geometry("+50+150")
        frame = ttk.Frame(main, padding=(3, 3, 12, 12))
        frame.grid(column=0, row=0, sticky=(N, S, E, W))
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
        names.set(NamesFilaments)
        lstbox = Listbox(frame, listvariable=names, selectmode=MULTIPLE, width=20, height=10)
        lstbox.grid(column=0, row=0, columnspan=2)
        def select():
            global ObjectSelection
            ObjectSelection = list()
            selection = lstbox.curselection()
            for i in selection:
                entrada = lstbox.get(i)
                ObjectSelection.append(entrada)
        #Test for the correct number selected
            if len(ObjectSelection)!=1:
                messagebox.showerror(title='Filament menu',
                                      message='Please Choose ONE Filament Object!')
                main.mainloop()
            #Test if selected filament name is the same as current one
            elif (''.join(map(str, ObjectSelection[0])))==vCurrentFilamentsSurpassName:
                messagebox.showerror(title='Filament menu',
                                      message='You CAN NOT use that Object\n'
                                      'Please Choose a Different Filament Object!')
                main.mainloop()
            else:
                main.destroy()

        btn = ttk.Button(frame, text="Choose Filament Object", command=select)
        btn.grid(column=1, row=1)
        #Selects the top items in the list
        # lstbox.selection_set(0)
        main.mainloop()
    ####################################################################
    # get the Selected Spots in Surpass Scene
        vDataItem=vSurpassScene.GetChild(NamesFilamentIndex[(NamesFilaments.index( ''.join(map(str, ObjectSelection[0]))))])
        vFilamentColoc=vImarisApplication.GetFactory().ToFilaments(vDataItem)
    ####################################################################
    #Test if scene has Spots object
    #get the Filament Data
        #Get the Current Filament Object
        vNumberOfFilamentsColoc = vFilamentColoc.GetNumberOfFilaments()
        vFilamentColocIds= vFilamentColoc.GetIds()
        vFilamentsColocFilamentId=[]
        vFilamentsColocIndexT=[]
        vFilamentsColocXYZ=[]
        vFilamentsColocRadius=[]
        vFilamentsColcPointIndex=[]
        vFilamentsColocEdgesSegmentId=[]
        vFilamentsColocFilamentIdEdges=[]
        vFilamentsColocEdges=[]
    #Collate all Filament Point positions and segment IDs
        for xFilamentColocIndex in range (vNumberOfFilamentsColoc):
            vFilamentsColocIndexT.append([vFilamentColoc.GetTimeIndex(xFilamentColocIndex)] * len(vFilamentColoc.GetRadii(xFilamentColocIndex)))
            vFilamentsColocXYZ.extend(vFilamentColoc.GetPositionsXYZ(xFilamentColocIndex))
            vFilamentsColocRadius.append(vFilamentColoc.GetRadii(xFilamentColocIndex))
            vFilamentsColocFilamentId.append([vFilamentColocIds[xFilamentColocIndex]] * len(vFilamentColoc.GetRadii(xFilamentColocIndex)))

            vFilamentsColocEdgesSegmentId.extend(vFilamentColoc.GetEdgesSegmentId(xFilamentColocIndex))
            vFilamentsColocEdges.extend(vFilamentColoc.GetEdges(xFilamentColocIndex))
            vFilamentsColocFilamentIdEdges.append([vFilamentColocIds[xFilamentColocIndex]] * len(vFilamentColoc.GetEdgesSegmentId(xFilamentColocIndex)))


    ####################################################################
    ####################################################################





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
    vNewSpotsDendritesFolder.SetName('Filament to Spots (dendrite) -- ' + vFilaments.GetName())
    vNewSpotsSpinesFolder.SetName('Spines to Spots -- ' + vFilaments.GetName())

    #Create a new folder object for Filament Intensity
    vNewIntensityFolder=vImarisApplication.GetFactory().CreateDataContainer()
    vNewIntensityFolder.SetName(vFilaments.GetName() + 'Filament Intensity -')
    vOriginalSpotsFromFilament=vImarisApplication.GetFactory().CreateSpots()

    #Create a new folder object for Bouton Spots
    vNewSpotsBoutons = vImarisApplication.GetFactory().CreateSpots()
    # vNewSpotsvNewSpotsAlongFilament = vImarisApplication.GetFactory().CreateSpots()
    vNewSpotsAnalysisFolder =vImarisApplication.GetFactory().CreateDataContainer()
    vNewSpotsAnalysisFolder.SetName('Filament Analysis -- ' + vFilaments.GetName())

    #Create a new folder object for Dendrite contacts
    # vNewSpotsDendriteDendriteContacts = vImarisApplication.GetFactory().CreateSpots()


    #Preset variable lists
    vTotalSpotsDendrite=[]
    vTotalSpotsDendriteTime=[]
    vTotalSpotsDendriteRadius=[]
    vTotalSpotsSpine=[]
    vTotalSpotsSpineRadius=[]
    vTotalSpotsSpineTime=[]
    wAllSegmentIds=[]
    TotalSegmentIndex=[]
    wCompleteFilamentTimeIndex=[]
    wCompleteDendriteTimeIndex=[]
    wCompleteSpineTimeIndex=[]
    vBoutonPositionAll=[]
    vBoutonRadiusAll=[]
    vStatisticFilamentBoutonsPerDendrite=[]
    vStatisticFilamentDendriteDendriteContacts=[]
    vStatisticFilamentDendriteDendriteContactsColoc=[]
    xCompleteNumberofContactsperFilament=[]
    xCompleteNumberofContactsperFilamentColoc=[]
    wCompleteFilamentNumberBoutons=[]
    vAllColocDensityPerDendrite=[]
    vFilamentCountActual=0
    wCompleteDendriteSegmentIds=[]
    wCompleteSpineSegmentIds=[]
    wCompleteDendriteBranchIntCenter=[]
    wCompleteDendriteBranchIntMean=[]
    wCompleteSpineBranchIntCenter=[]
    wCompleteSpineBranchIntMean=[]
    vStatisticDendriteBranchIntMean=[]
    vStatisticDendriteBranchIntCenter=[]
    vStatisticSpineBranchIntMean=[]
    vStatisticSpineBranchIntCenter=[]
    wNumberOfSpotsPerDendrite=[]
    wNumberOfSpotsPerSpine=[]
    wCompleteShortestDistanceToFilament=[]
    wCompleteShortestDistanceToALLFilaments=[]
    wCompleteShortestDistanceToSpine=[]
    wNewSpotsOnFilamentAll=[]
    wNewSpotsOnFilament=[]
    wNewSpotsOnFilamentRadius=[]
    wNewSpotsOnFilamentTime=[]
    wCompleteSpotDistAlongFilamentStat=[]
    wCompleteSpotDistAlongFilamentPosX=[]
    wCompleteSpotDistAlongFilamentPosY=[]
    wCompleteBoutonDistAlongFilamentStat=[]
    wCompleteBoutonDistAlongFilamentPosX=[]
    wCompleteBoutonDistAlongFilamentPosY=[]
    wCompleteSpotsonSpine=[]
    wCompleteSpotsonDendrite=[]
    wCompleteSpotsonFilament=[]
    wCompleteNumberSpotsPerFilament=[]
    wCompleteNumberSpotsonSpinePerFilament=[]
    wCompleteNumberSpotsonDendritePerFilament=[]
    wFilamentIntensityMean=[]
    wFilamentIntensityCenter=[]
    xContactBranchIndexId=[]
    xContactSegmentId=[]
    xContactSegmentIdColoc=[]
    xCompleteSpotDistAlongFilamentStat=[]
    xContactBranchIndexIdColoc=[]
    xCompleteSpotDistAlongFilamentStatColoc=[]
    zAllFilamentsRegularityIndexBP=[]
    zAllFilamentsRegularityIndexTP=[]



    IsRealFilament=[]
    wSpotsAllIndex=[]
    xBranchSharingNodesALL=[]
    xTerminalALL=[]
    xAllDendriteSegmentsId=[]
    SegmentCountALL=0


    aFilamentIndex=0
    qIsSpines=False
    ###############################################################################
    ###############################################################################
    #Progress Bar for Dendrites
    # if vNumberOfFilaments>10:
    # Create the master object
    master = tk.Tk()
    # Create a progressbar widget
    progress_bar = ttk.Progressbar(master, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    progress_bar2 = ttk.Progressbar(master, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    progress_bar3 = ttk.Progressbar(master, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    # progress_bar4 = ttk.Progressbar(master, orient="horizontal",
    #                               mode="determinate", maximum=100, value=0)
    # And a label for it
    label_1 = tk.Label(master, text="Dendrite Progress Bar ")
    label_2 = tk.Label(master, text="Filament Progress Bar ")
    label_3 = tk.Label(master, text="Dendrite Contact Progress Bar ")
    # label_4 = tk.Label(master, text="Distance to Soma Progress Bar ")

    # Use the grid manager
    label_1.grid(row=0, column=0,pady=10)
    label_2.grid(row=1, column=0,pady=10)
    label_3.grid(row=2, column=0,pady=10)
    # label_4.grid(row=3, column=0,pady=10)


    progress_bar.grid(row=0, column=1)
    progress_bar2.grid(row=1, column=1)
    progress_bar3.grid(row=2, column=1)
    # progress_bar4.grid(row=3, column=1)



    master.geometry('300x140')
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
    #################################################################

    # if vOptionDendriteToDendriteContact==0:
    #     progress_bar3['value'] = 100
    #     master.update()

    ###############################################################################
    ###############################################################################
    #if vNumberOfFilaments>50:
    if vNumberOfFilaments>50:

        qisVisible=messagebox.askquestion("Processing Warning - Large Number of Filaments",
                                      'Do you wish to Hide Imaris Application?\n'
                                      ' This will increase processing speed\n''\n'
                                      'Close Progress window to CANCEL script')
        if qisVisible=='yes':
                vImarisApplication.SetVisible(0)

    try:
            ###############################################################################
        zEmptyfilaments=[]
        for aFilamentIndex in range(vNumberOfFilaments):
            vFilamentsRadius = vFilaments.GetRadii(aFilamentIndex)
            if len(vFilamentsRadius)==1:
                zEmptyfilaments.append(int(aFilamentIndex))
        vFilamentIds=[v for i,v in enumerate(vFilamentIds) if i not in zEmptyfilaments]

        ###############################################################################
        ###############################################################################
        aFilamentIndex=0
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
            if max(vTypes)==1:
                qIsSpines=True
            #Get Filament stats
            vAllFilamentStatistics = vFilaments.GetStatistics()
            vAllFilamentStatNames = vAllFilamentStatistics.mNames
            vAllFilamentStatValues = vAllFilamentStatistics.mValues
            vAllFilamentStatIds = vAllFilamentStatistics.mIds
            vAllFilamentIndexDendriteLength=[i for i,val in enumerate(vAllFilamentStatNames)
                                              if val==('Dendrite Length')]
            if len(vAllFilamentIndexDendriteLength)>1:
                vAllFilamentDendriteLength=list(itemgetter(*vAllFilamentIndexDendriteLength)(vAllFilamentStatValues))
                vAllFilamentDendriteLengthIds=list(itemgetter(*vAllFilamentIndexDendriteLength)(vAllFilamentStatIds))
            else:
                vAllFilamentDendriteLength=[x[1] for x in enumerate(vAllFilamentStatValues)
                                        if x[0] in vAllFilamentIndexDendriteLength]
                vAllFilamentDendriteLengthIds=[x[1] for x in enumerate(vAllFilamentStatIds)
                                        if x[0] in vAllFilamentIndexDendriteLength]

            tmpUniq = {} # temp
            vAllFilamentDendriteLength = [tmpUniq.setdefault(i,i) for i in vAllFilamentDendriteLength if i not in tmpUniq]
            tmpUniq = {} # temp
            vAllFilamentDendriteLengthIds = [tmpUniq.setdefault(i,i) for i in vAllFilamentDendriteLengthIds if i not in tmpUniq]


        ###############################################################################
        ###############################################################################
        #Calculating Mean Intensity
            if vOptionIntensity==1:
            #Adjusting the All Filament Points that fall outside the edge of the volume for
            #Spot placement and calculation of Intensities
                xAdj = list(list(zip(*vFilamentsXYZ))[0])
                yAdj = list(list(zip(*vFilamentsXYZ))[1])
                zAdj = list(list(zip(*vFilamentsXYZ))[2])
                # xAdj=[i+0.001 if i <= vDataMin[0] else i for i in xAdj]
                # xAdj=[i-0.001 if i >= vDataMax[0] else i for i in xAdj]
                # xAdj=[i+0.001 if i <= vDataMin[1] else i for i in yAdj]
                # xAdj=[i-0.001 if i >= vDataMax[1] else i for i in yAdj]
                # xAdj=[i+0.001 if i <= vDataMin[2] else i for i in zAdj]
                # xAdj=[i-0.001 if i >= vDataMax[2] else i for i in zAdj]
                vFilamentsXYZAdj=[list(l) for l in zip(xAdj, yAdj, zAdj)]
                vOriginalSpotsFromFilament.Set(vFilamentsXYZAdj, vFilamentTimeIndex, vFilamentsRadius)

            #Get New adjusted spots intensity values
                vAllFilamentSpotsStatistics = vOriginalSpotsFromFilament.GetStatistics()
                vAllFilamentSpotsStatNames = vAllFilamentSpotsStatistics.mNames
                vAllFilamentSpotsStatValues = vAllFilamentSpotsStatistics.mValues
                vAllFilamentSpotsStatIds = vAllFilamentSpotsStatistics.mIds
                vAllFilamentSpotsIndexIntCnt=[i for i,val in enumerate(vAllFilamentSpotsStatNames)
                                              if val==('Intensity Center')]
                vAllFilamentSpotsIntCnt=list(itemgetter(*vAllFilamentSpotsIndexIntCnt)(vAllFilamentSpotsStatValues))
                vAllFilamentSpotsIndexIntMean=[i for i,val in enumerate(vAllFilamentSpotsStatNames)
                                              if val==('Intensity Mean')]
                vAllFilamentSpotsIntMean=list(itemgetter(*vAllFilamentSpotsIndexIntMean)(vAllFilamentSpotsStatValues))
                #for missing spots
                vAllFilamentSpotsIndexDiameter=[i for i,val in enumerate(vAllFilamentSpotsStatNames)
                                              if val==('Diameter X')]
                vAllFilamentSpotsIds=list(itemgetter(*vAllFilamentSpotsIndexDiameter)(vAllFilamentSpotsStatIds))

                vAllFilamentSpotsIdsIntensity=list(itemgetter(*vAllFilamentSpotsIndexIntCnt)(vAllFilamentSpotsStatIds))
        #Find Intensity spot Ids only
                vAllFilamentSpotsIdsIntensity=vAllFilamentSpotsIdsIntensity[0:int(len(vAllFilamentSpotsIdsIntensity)/(vSizeC))]

        ###############################################################################
                vAllFilamentSpotsIntCntChannels=[]
                vAllFilamentSpotsIntMeanChannels=[]
            #Split spot intensity on channel basis
                if vSizeC>1:
                    for c in range (vSizeC):
                        wNumber1=int(0*c+c*len(vAllFilamentSpotsIndexIntCnt)/vSizeC)
                        wNumber2=int(len(vAllFilamentSpotsIndexIntCnt)/vSizeC+len(vAllFilamentSpotsIndexIntCnt)/vSizeC*c)
                        vAllFilamentSpotsIntCntChannels.extend([vAllFilamentSpotsIntCnt[wNumber1:wNumber2]])
                        vAllFilamentSpotsIntMeanChannels.extend([vAllFilamentSpotsIntMean[wNumber1:wNumber2]])
                else:
                    vAllFilamentSpotsIntCntChannels.extend([vAllFilamentSpotsIntCnt[0:len(vAllFilamentSpotsIndexIntCnt)]])
                    vAllFilamentSpotsIntMeanChannels.extend([vAllFilamentSpotsIntMean[0:len(vAllFilamentSpotsIndexIntCnt)]])
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
            wFilamentBranchPoints2=wFilamentBranchPoints
            wFilamentTerminalPoints2=wFilamentTerminalPoints
            if len(wFilamentBranchPointIndex) == 1:
                wFilamentBranchPoints=np.array(wFilamentBranchPoints)[np.newaxis]
                wFilamentTerminalPoints=np.array(wFilamentTerminalPoints)[np.newaxis]
            else:
                wFilamentBranchPoints=np.array(wFilamentBranchPoints)
                wFilamentTerminalPoints=np.array(wFilamentTerminalPoints)

        ##############################################################################
        ###############################################################################
        #Calculation of Mean Nearest Neighbor based on branch points and terminal points

            #Create a set of Random Spots, same numebr of branch points or terminal points
            #limit creation of random spot to be withint he MinMax of XYZ of the filament points
            zArray=np.array(vFilamentsXYZ)
            isFilament2D=False
            zRandomLimitsMin=np.min(zArray, 0)
            zRandomLimitsMax=np.max(zArray, 0)
            zRandomSpotsTerminal=[]
            zRandomSpotsNode=[]
            if np.shape(wFilamentBranchPoints)[0] >3:
                zArrayNodes=cdist(wFilamentBranchPoints2,wFilamentBranchPoints2)
                zArrayNodesMin=np.where(zArrayNodes>0, zArrayNodes, np.inf).min(axis=1)
                zAverageNNBranchPoint=np.mean(zArrayNodesMin)

                for i in range(3):
                    zRandomSpotsNode.append(np.random.uniform(low=zRandomLimitsMin[i], high=zRandomLimitsMax[i], size= np.shape(wFilamentBranchPoints)[0]))
                zRandomSpotsNode=np.transpose(np.array(zRandomSpotsNode))
                #Find if set of Random Spots falls inside Convex hull on Filament
                if (np.all(zArray[:,2] == zArray[0][2]))==True:
                    zArray=np.delete(zArray,2,1)
                    zRandomSpotsNode=np.delete(zRandomSpotsNode,2,1)
                    isFilament2D=True
                zHullDelaunay = Delaunay(zArray)
                #Create Boolean arguement to define if in Convex hull
                zRandomSpotTestNode=np.array(zHullDelaunay.find_simplex(zRandomSpotsNode)>=0)
                #Keep True, replace false with new random spot
                if np.any(zRandomSpotTestNode):
                    #find indices that are True
                    zBrokenRandomSpots=np.where(zRandomSpotTestNode==False)
                    for i in range (len(zBrokenRandomSpots)):
                        #Create new random spot
                        zNEWRandomSpot=[]
                        for j in range(3):
                            zNEWRandomSpot.append(np.random.uniform(low=zRandomLimitsMin[j], high=zRandomLimitsMax[j], size= 1))
                        zNEWRandomSpot=np.transpose(np.array(zNEWRandomSpot))
                        if isFilament2D:
                            zNEWRandomSpot=np.delete(zNEWRandomSpot,2,1)
                        #Test if inConvex hull
                        while (zHullDelaunay.find_simplex(zNEWRandomSpot)>=0)==False:
                            #Create new random spot
                            zNEWRandomSpot=[]
                            for j in range(3):
                                zNEWRandomSpot.append(np.random.uniform(low=zRandomLimitsMin[j], high=zRandomLimitsMax[j], size= 1))
                            zNEWRandomSpot=np.transpose(np.array(zNEWRandomSpot))
                            if isFilament2D:
                                zNEWRandomSpot=np.delete(zNEWRandomSpot,2,1)
                        #Replace entire row with new positions
                        zRandomSpotsNode[zBrokenRandomSpots[0][i],:]=zNEWRandomSpot
                #Calculation of Mean Nearest Neighbor based on branch points and terminal points
                zArrayNodes=cdist(zRandomSpotsNode,zRandomSpotsNode)
                zArrayNodesMin=np.where(zArrayNodes>0, zArrayNodes, np.inf).min(axis=1)
                zAverageNNBranchPointRandom=np.mean(zArrayNodesMin)
                #Calculation of Regulatiry Index
                zAllFilamentsRegularityIndexBP.append(zAverageNNBranchPoint/zAverageNNBranchPointRandom)
            else:
                zAllFilamentsRegularityIndexBP.append(0)
        ###############################################################################
            if np.shape(wFilamentTerminalPoints)[0] >3:
                zArrayTerminal=cdist(wFilamentTerminalPoints2,wFilamentTerminalPoints2)
                zArrayTerminalMin=np.where(zArrayTerminal>0, zArrayTerminal, np.inf).min(axis=1)
                zAverageNNTerminalPoint=np.mean(zArrayTerminalMin)

                for i in range(3):
                    zRandomSpotsTerminal.append(np.random.uniform(low=zRandomLimitsMin[i], high=zRandomLimitsMax[i], size= np.shape(wFilamentTerminalPoints)[0]))
                zRandomSpotsTerminal=np.transpose(np.array(zRandomSpotsTerminal))
                #Find if set of Random Spots falls inside Convex hull on Filament
                if (np.all(zArray[:,2] == zArray[0][2]))==True:
                    zArray=np.delete(zArray,2,1)
                    zRandomSpotsTerminal=np.delete(zRandomSpotsTerminal,2,1)
                    isFilament2D=True
                zHullDelaunay = Delaunay(zArray)
                #Create Boolean arguement to define if in Convex hull
                zRandomSpotTestTerminal=np.array(zHullDelaunay.find_simplex(zRandomSpotsTerminal)>=0)
                if np.any(zRandomSpotTestTerminal):
                    #find indices that are True
                    zBrokenRandomSpots=np.where(zRandomSpotTestTerminal==False)
                    for i in range (len(zBrokenRandomSpots)):
                        #Create new random spot
                        zNEWRandomSpot=[]
                        for j in range(3):
                            zNEWRandomSpot.append(np.random.uniform(low=zRandomLimitsMin[j], high=zRandomLimitsMax[j], size= 1))
                        zNEWRandomSpot=np.transpose(np.array(zNEWRandomSpot))
                        if isFilament2D:
                            zNEWRandomSpot=np.delete(zNEWRandomSpot,2,1)
                        #Test if inConvex hull
                        while (zHullDelaunay.find_simplex(zNEWRandomSpot)>=0)==False:
                            #Create new random spot
                            zNEWRandomSpot=[]
                            for j in range(3):
                                zNEWRandomSpot.append(np.random.uniform(low=zRandomLimitsMin[j], high=zRandomLimitsMax[j], size= 1))
                            zNEWRandomSpot=np.transpose(np.array(zNEWRandomSpot))
                            if isFilament2D:
                                zNEWRandomSpot=np.delete(zNEWRandomSpot,2,1)
                        #Replace entire row with new positions
                        zRandomSpotsTerminal[zBrokenRandomSpots[0][i],:]=zNEWRandomSpot
                #Calculation of Mean Nearest Neighbor based on branch points and terminal points
                zArrayTerminal=cdist(zRandomSpotsTerminal,zRandomSpotsTerminal)
                zArrayTerminalMin=np.where(zArrayTerminal>0, zArrayTerminal, np.inf).min(axis=1)
                zAverageNNTerminaTPointRandom=np.mean(zArrayTerminalMin)
                #Calculation of Regulatiry Index
                zAllFilamentsRegularityIndexTP.append(zAverageNNTerminalPoint/zAverageNNTerminaTPointRandom)
            else:
                zAllFilamentsRegularityIndexTP.append(0)






##############################################################################
##############################################################################


            vAllSegmentsPerFilamentRadiusWorkingInserts=[]
            vAllSegmentsPerFilamentPositionsWorkingInserts=[]
            vAllSegmentsTypesPerFilamentWorkingInserts=[]
            vAllSegmentIdsPerFilamentInserts=[]
            vAllSegmentIdsPerFilamentDendriteIndex=[]
            vAllNewSpotsBoutonsPositionXYZ=[]
            vAllNewSpotsBoutonsRadius=[]
            vSegmentBranchLength=[]
            vStatisticBoutonWidth=[]
            wDendriteSegmentIds=[]
            wSpineSegmentIds=[]
            wShortestDistanceToSegment=[]
            zReOrderedFilamentPointIndex=[]
            zReOrderedFilamentPositions=[]
            zReOrderedFilamentRadius=[]
            zReOrderedFilamentPointIndexWorking=[]
            zReOrderedFilamentPositionsWorking=[]
            zReOrderedFilamentRadiusWorking=[]
            zReorderedvSegmentIds=[]
            zReorderedvSegmentType=[]
            wSpotsAllIndexPerFilament=[]
            wCompleteSpotDistAlongFilamentStatWorking=[]
            xCompleteSpotDistAlongFilamentStatWorking=[]
            xCompleteDendriteDendriteContactSpotPositions=[]
            xLengthContactsWorkingDendrite=[]
            xCompleteDendriteDendriteContactSpotPositionsColoc=[]
            xLengthContactsWorkingDendriteColoc=[]
            xCompleteSpotSizeforContact=[]
            xCompleteSpotSizeforContactColoc=[]

            dcount=0
            scount=0

        #Loop through dendrite segments, terminal segements and spine segments
            vBranchIndex=0
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

                #Collate branchindex in FilamentsXYZ
                xAllDendriteSegmentsId.extend([vBranchIndex]*len(vSegmentWorkingPointIndex))

                #Find unique edge indices using "set" and convert back to list
                vEdgesUniqueWorking=list(set(x for l in vSegmentEdgesWorking for x in l))

                #Collate all segmentsIds
                wAllSegmentIds.append(vSegmentIdWorking)
           #Find current Working Dendrite segment parts
                vSegmentPositionsWorking=list(itemgetter(*vEdgesUniqueWorking)(vFilamentsXYZ))
                vSegmentRadiusWorking=list(itemgetter(*vEdgesUniqueWorking)(vFilamentsRadius))
                vSegmentTypesWorking=list(itemgetter(*vEdgesUniqueWorking)(vTypes))

                #Unit length number of points that make it up
                vSegmentBranchLength.append(len(vEdgesUniqueWorking))

                #Collate all SegmentId by Type (dendrite or spine)
                if max(vSegmentTypesWorking)==0:
                    wDendriteSegmentIds.append(vSegmentIdWorking)
                else:
                    wSpineSegmentIds.append(vSegmentIdWorking)


        ###############################################################################
        #Calculate the  Intensity values on per dendrite basis
        #generate dendrite intensity values by averageing all spots for each segment, per channel
                if vOptionIntensity==1:
                    vSegmentIndexWorking=[]
                    for i in range (len(vSegmentRadiusWorking)):
                        xFindX = list(list(zip(*[(index_,sub_list.index(vSegmentPositionsWorking[i][0]))\
                             for index_, sub_list in enumerate(vFilamentsXYZ)\
                             if vSegmentPositionsWorking[i][0] in sub_list]))[0])
                        xFindY = list(list(zip(*[(index_,sub_list.index(vSegmentPositionsWorking[i][1]))\
                             for index_, sub_list in enumerate(vFilamentsXYZ)\
                             if vSegmentPositionsWorking[i][1] in sub_list]))[0])
                        xFindZ = list(list(zip(*[(index_,sub_list.index(vSegmentPositionsWorking[i][2]))\
                             for index_, sub_list in enumerate(vFilamentsXYZ)\
                             if vSegmentPositionsWorking[i][2] in sub_list]))[0])
                        vSegmentIndexWorking.append(max(list(set(xFindX) & set(xFindY) & set(xFindZ))))

                    #ids of the original spots
                    xFinalIds=[vAllFilamentSpotsIds[i] for i in vSegmentIndexWorking]
                    #match that id with id from FilamentSpotsID list, return index
                    xFinalFilamentIndex=([i for i, e in enumerate(vAllFilamentSpotsIdsIntensity) if e in set(xFinalIds)])
                    if xFinalFilamentIndex==[]:
                        #grab last measured intensity and add that here
                        if vStatisticDendriteBranchIntCenter==[] or vStatisticSpineBranchIntCenter==[]:#first in the list
                            xFinalValue=0.0001#unique value likley to be found in real data
                            if max(vSegmentTypesWorking)==1:
                                qIsSpines=True
                                for t in range (vSizeC):
                                        vStatisticSpineBranchIntCenter.append(xFinalValue)
                                        vStatisticSpineBranchIntMean.append(xFinalValue)
                            else:
                                for t in range (vSizeC):
                                    vStatisticDendriteBranchIntCenter.append(xFinalValue)
                                    vStatisticDendriteBranchIntMean.append(xFinalValue)
                        else:
                            if max(vSegmentTypesWorking)==1:
                                qIsSpines=True
                                for t in range (vSizeC):
                                        vStatisticSpineBranchIntCenter.append(vStatisticSpineBranchIntCenter[-1])
                                        vStatisticSpineBranchIntMean.append(vStatisticSpineBranchIntMean[-1])
                            else:
                                for t in range (vSizeC):
                                    vStatisticDendriteBranchIntCenter.append(vStatisticDendriteBranchIntCenter[-1])
                                    vStatisticDendriteBranchIntMean.append(vStatisticDendriteBranchIntMean[-1])

                    #Collate Intensity measures
                    else:
                        if max(vSegmentTypesWorking)==1:
                            qIsSpines=True
                            for t in range (vSizeC):
                                vStatisticSpineBranchIntCenter.append(mean([vAllFilamentSpotsIntCntChannels[t][index] for index in xFinalFilamentIndex]))
                                vStatisticSpineBranchIntMean.append(mean([vAllFilamentSpotsIntMeanChannels[t][index] for index in xFinalFilamentIndex]))
                        else:
                            for t in range (vSizeC):
                                vStatisticDendriteBranchIntCenter.append(mean([vAllFilamentSpotsIntCntChannels[t][index] for index in xFinalFilamentIndex]))
                                vStatisticDendriteBranchIntMean.append(mean([vAllFilamentSpotsIntMeanChannels[t][index] for index in xFinalFilamentIndex]))

        ###############################################################################
        ###############################################################################
        #find gaps in the dendrite length and fill with extra spots
        #For bouton detect and Spots display
                if vOptionFilamentToSpotsFill==1 or vOptionFilamentBoutonDetection==1 or vOptionFilamentCloseToSpots==1 or vOptionIntensity==1 or vOptionDendriteToDendriteContact==1 or vOptionFilamentToFilamentContact==1:
        ###########################
        ###########################
        #ReOrder segment
                #Reordering
                #flattten list
                    zNum=reduce(operator.concat, vSegmentEdgesWorking)
                    #Test for perfect edge sequence, no reordereding needed
                    # sorted_list_diffs = sum(np.diff(sorted(np.unique(zNum).tolist())))
                    # if sorted_list_diffs == (len(np.unique(zNum).tolist()) - 1):
                    #     zReOrderedFilamentPointIndex.append(np.unique(zNum).tolist())
                    #     zReOrderedFilamentPositions.extend(vSegmentPositionsWorking)
                    #     continue
                    # if zNum == sorted(zNum):
                    #     zReOrderedFilamentRadiusWorking=vSegmentRadiusWorking[:]
                    #     zReOrderedFilamentPositionsWorking=vSegmentPositionsWorking[:]
                    #     zReorderedvSegmentIds.extend([vSegmentIdWorking]*len(vSegmentRadiusWorking))
                    #     zReorderedvSegmentType.extend([max(vSegmentTypesWorking)]*len(vSegmentRadiusWorking))
                    # else:
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
        #fill spots in filament point gaps
                    # if(zNum != sorted(zNum)):
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
                    vAllSegmentsPerFilamentRadiusWorkingInserts.extend(vSegmentRadiusWorkingInserts)
                    vAllSegmentsPerFilamentPositionsWorkingInserts.extend(vSegmentPositionsWorkingInserts)
                    vAllSegmentsTypesPerFilamentWorkingInserts.extend([max(vSegmentTypesWorking)]*len(vSegmentRadiusWorkingInserts))
                    vAllSegmentIdsPerFilamentInserts.extend([vSegmentIdWorking]*len(vSegmentRadiusWorkingInserts))
                    #Create index for new segment points
                    vAllSegmentIdsPerFilamentDendriteIndex.extend([vBranchIndex]*len(vSegmentRadiusWorkingInserts))

        ###############################################################################
        ###############################################################################
        # Detect VaricositiesBoutons based on the radius of filled spot list
                if vOptionFilamentBoutonDetection==1 and max(vSegmentTypesWorking)==0:
                    peaks, _ = find_peaks(vSegmentRadiusWorkingInserts, height=vOptionBoutonHeight)
                    # peakwidths=peak_widths(vSegmentRadiusWorkingInserts,peaks)

                    #Grab Bouton dendrite working positions/radius from the detected Peak indices
                    if len(peaks)>1:
                        vNewSpotsBoutonsPositionXYZ=list(itemgetter(*peaks)(vSegmentPositionsWorkingInserts))
                        vNewSpotsBoutonsRadius=list(itemgetter(*peaks)(vSegmentRadiusWorkingInserts))
                    else:
                        vNewSpotsBoutonsPositionXYZ=[x[1] for x in enumerate(vSegmentPositionsWorkingInserts)
                                  if x[0] in peaks]
                        vNewSpotsBoutonsRadius=[x[1] for x in enumerate(vSegmentRadiusWorkingInserts)
                                  if x[0] in peaks]

            #Compile all boutons per dendrite for filament statistic
                    if peaks.size>0:
                        vStatisticFilamentBoutonsPerDendrite.append(len(vNewSpotsBoutonsRadius))
                    else:
                        vStatisticFilamentBoutonsPerDendrite.append(0)
                    vAllNewSpotsBoutonsPositionXYZ.extend(vNewSpotsBoutonsPositionXYZ)
                    vAllNewSpotsBoutonsRadius.extend(vNewSpotsBoutonsRadius)
         #############################
         # #Add Bouton Statistics to Filament object
            #Concatonate all boutons from all "real" filaments
                    if vBranchIndex==vNumberOfDendriteBranches-1:#Do when last dendrite branch is processed for filament
                        TotalSegmentIndex.extend(wAllSegmentIds)
                        #Add Spot for each bouton - ALL Filaments
                        vBoutonPositionAll.extend(vAllNewSpotsBoutonsPositionXYZ)
                        vBoutonRadiusAll.extend(vAllNewSpotsBoutonsRadius)
                        #number of Boutons per Filament for new Filament level stat
                        wCompleteFilamentNumberBoutons.append(len(vAllNewSpotsBoutonsRadius))

        ###############################################################################
        ###############################################################################
            #Spot to fIlament analysis
                if vOptionFilamentCloseToSpots==1:
                    if max(vSegmentTypesWorking)==1:
                        scount=scount+1
                    else:
                        dcount=dcount+1
            #Get all spots from same time index as current filament DO NOT need to do every branch index
                    vSpotsColocPositionsWorkingIndex = [i for i in range(len(vSpotsColocRadius))
                                            if vSpotsColocTimeIndices[i] == vFilamentsIndexT]
                    if len(vSpotsColocPositionsWorkingIndex)>1:
                        vSpotsColocPositionsWorking=list(itemgetter(*vSpotsColocPositionsWorkingIndex)(vSpotsColocPositionsXYZ))
                        vSpotsColocRadiusWorking=list(itemgetter(*vSpotsColocPositionsWorkingIndex)(vSpotsColocRadius))
                    else:
                        vSpotsColocPositionsWorking=[x[1] for x in enumerate(vSpotsColocPositionsXYZ)
                                  if x[0] in vSpotsColocPositionsWorkingIndex]
                        vSpotsColocRadiusWorking=[x[1] for x in enumerate(vSpotsColocRadius)
                                  if x[0] in vSpotsColocPositionsWorkingIndex]

            #Isolate spots on dendrites and spines
                    if max(vSegmentTypesWorking)==0:
                        #Find Spots "close" to current Filament min value per row in array
                        wSpotToFilamentDistanceArray=cdist(vSpotsColocPositionsWorking,vSegmentPositionsWorkingInserts)
                        #Adjust distance measure based on filament point radius and spot radius
                        wSpotToFilamentDistanceArray=wSpotToFilamentDistanceArray-vSegmentRadiusWorkingInserts-[max(vSpotsColocRadiusWorking[0])]*len(vSegmentRadiusWorkingInserts)
                        #per dendrite segment - dista of each spot to working dendrite segment
                        wShortestDistanceToSegment=wSpotToFilamentDistanceArray.min(axis=1)
                        wShortestDistanceToSegment[wShortestDistanceToSegment<0]=0
                        #SpotIndex for those the are less than threshold per dendrite segment
                        wSpotsIndexPerSegment = [i for i,val in enumerate(wShortestDistanceToSegment)
                                                  if val<=vOptionFilamentSpotThreshold]
                        #Collating dendrite segments
                        if dcount==1:
                            wCompleteShortestDistanceToFilament=wShortestDistanceToSegment
                        else:
                            wCompleteShortestDistanceToFilament=np.column_stack((wCompleteShortestDistanceToFilament,wShortestDistanceToSegment))

                        #Calculate spot density per segment
                        wCurrentIndexDendrite=[i for i,val in enumerate(vAllFilamentDendriteLengthIds)
                                                  if val==vSegmentIdWorking]
                        wCurrentDendriteLength=[x[1] for x in enumerate(vAllFilamentDendriteLength)
                                                if x[0] in wCurrentIndexDendrite]
                        #QUantify spots per dendrite
                        wNumberOfSpotsPerDendrite.append(np.count_nonzero(wShortestDistanceToSegment <= vOptionFilamentSpotThreshold))
                        vAllColocDensityPerDendrite.append(np.count_nonzero(wShortestDistanceToSegment <= vOptionFilamentSpotThreshold)/wCurrentDendriteLength[0]*10)
                    else:
                        #Find Spots "close" to current Filament min value per row in array
                        wSpotToFilamentDistanceArray=cdist(vSpotsColocPositionsWorking,vSegmentPositionsWorkingInserts)
                        #Adjust distance measure based on filament point radius and spot radius
                        wSpotToFilamentDistanceArray=wSpotToFilamentDistanceArray-vSegmentRadiusWorkingInserts-[max(vSpotsColocRadiusWorking[0])]*len(vSegmentRadiusWorkingInserts)
                        #per dendrite segment - dista of each spot to working dendrite segment
                        wShortestDistanceToSegment=wSpotToFilamentDistanceArray.min(axis=1)
                        wShortestDistanceToSegment[wShortestDistanceToSegment<0]=0
                        #SpotIndex for those the are less than threshold per dendrite segment
                        wSpotsIndexPerSegment = [i for i,val in enumerate(wShortestDistanceToSegment)
                                                  if val<=vOptionFilamentSpotThreshold]
                        #Collating spine segments
                        if scount==1:
                            wCompleteShortestDistanceToSpine=wShortestDistanceToSegment
                        else:
                            wCompleteShortestDistanceToSpine=np.column_stack((wCompleteShortestDistanceToSpine,wShortestDistanceToSegment))
                        #Quantify spot per spine
                        wNumberOfSpotsPerSpine.append(np.count_nonzero(wShortestDistanceToSegment <= vOptionFilamentSpotThreshold))

                    wShortestDistanceToSegment=[]
                    wSpotToFilamentDistanceArray=[]
                    wSpotsAllIndex.extend(wSpotsIndexPerSegment)
                    wSpotsAllIndexPerFilament.extend(wSpotsIndexPerSegment)
                    wSpotsIndexPerSegment=[]

        #Progress bar for dendrite segments
                progress_bar['value'] = int((vBranchIndex+1)/vNumberOfDendriteBranches*100) #  % out of 100
                master.update()
        ###############################################################################
        ###############################################################################
        ###############################################################################
        #After Each Filament
        #Process dendrite-dendrite contact after all dendrites spots filled and reordered
        ##############
            if vOptionDendriteToDendriteContact==1 or vOptionFilamentToFilamentContact==1:
                xAllFilamentPoints=np.array(vAllSegmentsPerFilamentPositionsWorkingInserts)
                #Find Starting point node Index
                xStartingPositionXYZ=vFilamentsXYZ[vBeginningVertex]
                xStartingPointIndex=np.where((xAllFilamentPoints[:,0] == xStartingPositionXYZ[0]) & (xAllFilamentPoints[:,1] == xStartingPositionXYZ[1]) & (xAllFilamentPoints[:,2] == xStartingPositionXYZ[2]))[0]
                xStartingPointIndex.tolist()
            #Find and search for indices of All points that match current node/branch point or startpoint
                for b in range (len(wFilamentBranchPointIndex)):
                    xNodeIndex=np.where((xAllFilamentPoints[:,0] == wFilamentBranchPoints[b][0]) & (xAllFilamentPoints[:,1] == wFilamentBranchPoints[b][1]) & (xAllFilamentPoints[:,2] == wFilamentBranchPoints[b][2]))[0]
                    xNodeIndex=xNodeIndex.tolist()

                    #Identify branchID for each node index
                    xBranchSharingNodes=list(itemgetter(*xNodeIndex)(vAllSegmentIdsPerFilamentDendriteIndex))
                    xBranchSharingNodesALL.append(xBranchSharingNodes)
                xStartingBranchSharingNodes=[x[1] for x in enumerate(vAllSegmentIdsPerFilamentDendriteIndex)
                                  if x[0] in xStartingPointIndex]
                xBranchSharingNodesALL.append(xStartingBranchSharingNodes)

        #############
            # #Find and search for indices of All points that match current Terminal ending
            #     for b in range (len(wFilamentTerminalPoints)):
            #         xTerminalIndex=np.where((xAllFilamentPoints[:,0] == wFilamentTerminalPoints[b][0]) &
            #                             (xAllFilamentPoints[:,1] == wFilamentTerminalPoints[b][1]) &
            #                             (xAllFilamentPoints[:,2] == wFilamentTerminalPoints[b][2]))[0]
            #         xTerminalIndex=xTerminalIndex.tolist()
            #         #Identify branchID for each Terminal index
            #         xTerminalBranch=DendriteCurrentWorkingPositions=list(itemgetter(*xTerminalIndex)(vAllSegmentIdsPerFilamentDendriteIndex))
            #         xTerminalBranchALL.append(xTerminalBranch)
        #############
                # vBranchIndex=4
                # vBranchIndex=3
                # vBranchIndex=2
                # vBranchIndex=1
                vBranchIndex=0
                for vBranchIndex in range (vNumberOfDendriteBranches):

                #Identify dendrite segment indices for current segment
                    xDendriteCurrentWorkingIndices=[i for i,val in enumerate(vAllSegmentIdsPerFilamentDendriteIndex)
                                              if val==vBranchIndex]
                #Grab current segment type
                    xDendriteTypeCurrent=vAllSegmentsTypesPerFilamentWorkingInserts[xDendriteCurrentWorkingIndices[0]]
                #Isolate Positions and Radii from current dendrite segment
                    if len(xDendriteCurrentWorkingIndices)>1:
                        xDendriteCurrentWorkingPositions=list(itemgetter(*xDendriteCurrentWorkingIndices)(vAllSegmentsPerFilamentPositionsWorkingInserts))
                        xDendriteCurrentWorkingRadii=list(itemgetter(*xDendriteCurrentWorkingIndices)(vAllSegmentsPerFilamentRadiusWorkingInserts))
                    else:
                        xDendriteCurrentWorkingPositions=[x[1] for x in enumerate(vAllSegmentsPerFilamentPositionsWorkingInserts)
                                  if x[0] in xDendriteCurrentWorkingIndices]
                        xDendriteCurrentWorkingRadii=[x[1] for x in enumerate(vAllSegmentsPerFilamentRadiusWorkingInserts)
                                  if x[0] in xDendriteCurrentWorkingIndices]

                #Remove Current Segment from Total Lists
                    xTotalPointPositionWorking=[i for j, i in enumerate(vAllSegmentsPerFilamentPositionsWorkingInserts) if j not in xDendriteCurrentWorkingIndices]
                    xTotalPointRadiiWorking=[i for j, i in enumerate(vAllSegmentsPerFilamentRadiusWorkingInserts) if j not in xDendriteCurrentWorkingIndices]
                    xTotalPointIDWorking=[i for j, i in enumerate(vAllSegmentIdsPerFilamentDendriteIndex) if j not in xDendriteCurrentWorkingIndices]

                #Measure Current segment distance to all Filament point except the current one not to spines.
                    if xDendriteTypeCurrent==0:
                        xSpotSizeforContinuousContactId=[]
                        xContactSpotPostionWorking=[]
                        xContinuousContactSpotSize=[]

        ##############################
                        if vOptionFilamentToFilamentContact==1:
                            #Find Dendrite Points that are  "close" to ALL Filament Points min value per row in array
                            xDendriteToDendriteDistanceArrayColoc=cdist(xDendriteCurrentWorkingPositions,vFilamentsColocXYZ)
                            #adjust for current dendrite point radius
                            xDendriteToDendriteDistanceArrayColoc=xDendriteToDendriteDistanceArrayColoc-np.vstack(xDendriteCurrentWorkingRadii)-vFilamentsColocRadius
                            #Dendrite Point index of points contacting same filament.
                            xCBIarrayColoc=np.array(np.where(xDendriteToDendriteDistanceArrayColoc <= 0))
                            #add row indicating Coloc filament Index
                            xCBIarrayColoc=np.vstack([xCBIarrayColoc,np.take(vFilamentsColocFilamentId,xCBIarrayColoc[1].tolist())])
                            a=xCBIarrayColoc[2,:]
                            b=xCBIarrayColoc[0,:]
                            ind = np.lexsort((b,a))
                            xCBIarrayColoc=xCBIarrayColoc[:,ind]
        ##############################
        ##############################
                            xSizeCBIarray=np.size(xCBIarrayColoc, axis=1)
                            xIsContinuous=False
                            xContactLengthColoc=0
                            xNumberDendriteContactsWorkingColoc=0

                            w=0
                            if xSizeCBIarray==1:#only one contact point
                                xCompleteDendriteDendriteContactSpotPositionsColoc.append(xDendriteCurrentWorkingPositions[xCBIarrayColoc[0,0]])
                                xNumberDendriteContactsWorkingColoc=xNumberDendriteContactsWorkingColoc+1
                                xContactLengthColoc=1
                                xLengthContactsWorkingDendriteColoc.append(xContactLengthColoc)
                                xCompleteSpotSizeforContactColoc.append(xDendriteCurrentWorkingRadii[xCBIarrayColoc[0,w]])
                                xContactBranchIndexIdColoc.append(vBranchIndex)
                                xContactSegmentIdColoc.append(vSegmentIds[vBranchIndex])
                                xContactLengthColoc=0
                                # print ('Only one contact')
                            elif xSizeCBIarray>1:#multiple contact points

                                w=0#Set to zero for single point contact only
                                for w in range (xSizeCBIarray):
                                    if (w==xSizeCBIarray-1) and xIsContinuous==False:#Test if last contact point
                                        xCompleteDendriteDendriteContactSpotPositionsColoc.append(xDendriteCurrentWorkingPositions[xCBIarrayColoc[0,w]])
                                        xNumberDendriteContactsWorkingColoc=xNumberDendriteContactsWorkingColoc+1
                                        xContactLengthColoc=1
                                        xLengthContactsWorkingDendriteColoc.append(xContactLengthColoc)
                                        xCompleteSpotSizeforContactColoc.append(xDendriteCurrentWorkingRadii[xCBIarrayColoc[0,w]])
                                        xContactBranchIndexIdColoc.append(vBranchIndex)
                                        xContactSegmentIdColoc.append(vSegmentIds[vBranchIndex])
                                        # print ('last point contact','w=', w)

                                    elif (w==xSizeCBIarray-1) and xIsContinuous==True:
                                        xContactLengthColoc=xContactLengthColoc+1
                                        xLengthContactsWorkingDendriteColoc.append(xContactLengthColoc)
                                        xNumberDendriteContactsWorkingColoc=xNumberDendriteContactsWorkingColoc+1
                                        xSpotSizeforContinuousContactId.append(xCBIarrayColoc[0,w])#mark working dendrite pointId for continuous contact

                                        ###############################
                                        if len(xDendriteCurrentWorkingPositions)==1:
                                            xContinuousContactSpotSize=xDendriteCurrentWorkingRadii[xCBIarrayColoc[0,w]]
                                        else:
                                            x = np.array([ xDendriteCurrentWorkingPositions[index][0] for index in xSpotSizeforContinuousContactId ])
                                            y = np.array([ xDendriteCurrentWorkingPositions[index][1] for index in xSpotSizeforContinuousContactId ])
                                            z = np.array([ xDendriteCurrentWorkingPositions[index][2] for index in xSpotSizeforContinuousContactId ])
                                            dist_array = (x[:-1]-x[1:])**2 + (y[:-1]-y[1:])**2 +(z[:-1]-z[1:])**2
                                            xContinuousContactSpotSize=(np.sum(np.sqrt(dist_array)))/2
                                        #Find Center position
                                        res_list = [xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId]
                                        if len([xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId])%2==0:
                                            first_middle = int(len(res_list) / 2) - 1
                                            second_middle = int(len(res_list) / 2)
                                            xContactSpotPostionWorking=res_list[second_middle]
                                        else:
                                            middleIndex = round((len(res_list) - 1)/2)
                                            xContactSpotPostionWorking=res_list[middleIndex]
                                ###############################


                                        xCompleteSpotSizeforContactColoc.append(xContinuousContactSpotSize)
                                        xCompleteDendriteDendriteContactSpotPositionsColoc.append(xContactSpotPostionWorking)
                                        xContactBranchIndexIdColoc.append(vBranchIndex)
                                        xContactSegmentIdColoc.append(vSegmentIds[vBranchIndex])
                                        # print ('last point with continuous contact','w=', w)
                                        xSpotSizeforContinuousContactId=[]#Reset to blank for next contact point
                                        xContactLengthColoc=0
                                    else:
                            ###############################
                                        if xIsContinuous:# but not yet identified as end on continuous contact
                                            xContactTest=np.isin(xCBIarrayColoc[:,w],xCBIarrayColoc[:,w+1]).astype(int)
                                            # is_all_zero = bool(np.all((xContactTest==0)))
                                            if ((xContactTest[2] == 0) and (xContactTest[0] == 0)):

                                                xNumberDendriteContactsWorkingColoc=xNumberDendriteContactsWorkingColoc+1
                                                xContactLengthColoc=xContactLengthColoc+1
                                                xLengthContactsWorkingDendriteColoc.append(xContactLengthColoc)
                                                xIsContinuous=False#Reset this marker
                                                xSpotSizeforContinuousContactId.append(xCBIarrayColoc[0,w])#mark working dendrite pointId for continuous contact

                                                ###############################
                                                if len(xDendriteCurrentWorkingPositions)==1:
                                                    xContinuousContactSpotSize=xDendriteCurrentWorkingRadii[xCBIarrayColoc[0,w]]
                                                else:
                                                    x = np.array([ xDendriteCurrentWorkingPositions[index][0] for index in xSpotSizeforContinuousContactId ])
                                                    y = np.array([ xDendriteCurrentWorkingPositions[index][1] for index in xSpotSizeforContinuousContactId ])
                                                    z = np.array([ xDendriteCurrentWorkingPositions[index][2] for index in xSpotSizeforContinuousContactId ])
                                                    dist_array = (x[:-1]-x[1:])**2 + (y[:-1]-y[1:])**2 +(z[:-1]-z[1:])**2
                                                    xContinuousContactSpotSize=(np.sum(np.sqrt(dist_array)))/2
                                                #Find Center position
                                                res_list = [xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId]
                                                if len([xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId])%2==0:
                                                    first_middle = int(len(res_list) / 2) - 1
                                                    second_middle = int(len(res_list) / 2)
                                                    xContactSpotPostionWorking=res_list[second_middle]
                                                else:
                                                    middleIndex = round((len(res_list) - 1)/2)
                                                    xContactSpotPostionWorking=res_list[middleIndex]
                                        ###############################

                                                xCompleteSpotSizeforContactColoc.append(xContinuousContactSpotSize)
                                                xCompleteDendriteDendriteContactSpotPositionsColoc.append(xContactSpotPostionWorking)
                                                xContactBranchIndexIdColoc.append(vBranchIndex)
                                                xContactSegmentIdColoc.append(vSegmentIds[vBranchIndex])
                                                xSpotSizeforContinuousContactId=[]#Reset to blank for next contact point
                                                # print('Final continuous point')
                                                xContactLengthColoc=0
                                                continue
                                            elif ((xContactTest[0] == 1) and (xContactTest[2] == 1)):
                                                # if xCBIarrayColoc[1,w]-3 <= xCBIarrayColoc[1,w+1] <= xCBIarrayColoc[1,w]+3:
                                                #     #continuous but does not add to length of contact
                                                #     # print('skip one - 2 consecutive contacts same dendrite same point','w=', w)
                                                #     continue
                                                xIsContinuous=True
                                                continue
                                            elif ((xContactTest[0] == 0) and (xContactTest[2] == 1)):
                                                if ((xCBIarrayColoc[0,w]==(xCBIarrayColoc[0,w+1])-1) or (xCBIarrayColoc[0,w]==(xCBIarrayColoc[0,w+1])-2)):# and xCBIarrayColoc[1,w]-3 <= xCBIarrayColoc[1,w+1] <= xCBIarrayColoc[1,w]+3:
                                                    #continuous and add to length of contact
                                                    xContactLengthColoc=xContactLengthColoc+1
                                                    xSpotSizeforContinuousContactId.append(xCBIarrayColoc[0,w])#mark working dendrite pointId for continuous contact
                                                    xIsContinuous=True
                                                    # print ('continuous contact on working denrite-next','w=', w)
                                                    continue
                                                else:
                                                    xNumberDendriteContactsWorkingColoc=xNumberDendriteContactsWorkingColoc+1
                                                    xContactLengthColoc=xContactLengthColoc+1
                                                    xLengthContactsWorkingDendriteColoc.append(xContactLengthColoc)
                                                    xContactLengthColoc=0
                                                    xIsContinuous=False#Reset this marker
                                                    xSpotSizeforContinuousContactId.append(xCBIarrayColoc[0,w])#mark working dendrite pointId for continuous contact

                                                    ###############################
                                                    if len(xDendriteCurrentWorkingPositions)==1:
                                                        xContinuousContactSpotSize=xDendriteCurrentWorkingRadii[xCBIarrayColoc[0,w]]
                                                    else:
                                                        x = np.array([ xDendriteCurrentWorkingPositions[index][0] for index in xSpotSizeforContinuousContactId ])
                                                        y = np.array([ xDendriteCurrentWorkingPositions[index][1] for index in xSpotSizeforContinuousContactId ])
                                                        z = np.array([ xDendriteCurrentWorkingPositions[index][2] for index in xSpotSizeforContinuousContactId ])
                                                        dist_array = (x[:-1]-x[1:])**2 + (y[:-1]-y[1:])**2 +(z[:-1]-z[1:])**2
                                                        xContinuousContactSpotSize=(np.sum(np.sqrt(dist_array)))/2
                                                    #Find Center position
                                                    res_list = [xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId]
                                                    if len([xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId])%2==0:
                                                        first_middle = int(len(res_list) / 2) - 1
                                                        second_middle = int(len(res_list) / 2)
                                                        xContactSpotPostionWorking=res_list[second_middle]
                                                    else:
                                                        middleIndex = round((len(res_list) - 1)/2)
                                                        xContactSpotPostionWorking=res_list[middleIndex]
                                        ###############################


                                                    xCompleteSpotSizeforContactColoc.append(xContinuousContactSpotSize)
                                                    xCompleteDendriteDendriteContactSpotPositionsColoc.append(xContactSpotPostionWorking)
                                                    xContactBranchIndexIdColoc.append(vBranchIndex)
                                                    xContactSegmentIdColoc.append(vSegmentIds[vBranchIndex])
                                                    xSpotSizeforContinuousContactId=[]
                                                    # print('final point contact', 'w=', w)
                                                    continue

                                            elif ((xContactTest[0] == 1) and (xContactTest[2] == 0)):

                                                xNumberDendriteContactsWorkingColoc=xNumberDendriteContactsWorkingColoc+1
                                                xContactLengthColoc=xContactLengthColoc+1
                                                xLengthContactsWorkingDendriteColoc.append(xContactLengthColoc)
                                                xContactLengthColoc=0
                                                xIsContinuous=False#Reset this marker
                                                xSpotSizeforContinuousContactId.append(xCBIarrayColoc[0,w])#mark working dendrite pointId for continuous contact

                                                ###############################
                                                if len(xDendriteCurrentWorkingPositions)==1:
                                                    xContinuousContactSpotSize=xDendriteCurrentWorkingRadii[xCBIarrayColoc[0,w]]
                                                else:
                                                    x = np.array([ xDendriteCurrentWorkingPositions[index][0] for index in xSpotSizeforContinuousContactId ])
                                                    y = np.array([ xDendriteCurrentWorkingPositions[index][1] for index in xSpotSizeforContinuousContactId ])
                                                    z = np.array([ xDendriteCurrentWorkingPositions[index][2] for index in xSpotSizeforContinuousContactId ])
                                                    dist_array = (x[:-1]-x[1:])**2 + (y[:-1]-y[1:])**2 +(z[:-1]-z[1:])**2
                                                    xContinuousContactSpotSize=(np.sum(np.sqrt(dist_array)))/2
                                                #Find Center position
                                                res_list = [xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId]
                                                if len([xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId])%2==0:
                                                    first_middle = int(len(res_list) / 2) - 1
                                                    second_middle = int(len(res_list) / 2)
                                                    xContactSpotPostionWorking=res_list[second_middle]
                                                else:
                                                    middleIndex = round((len(res_list) - 1)/2)
                                                    xContactSpotPostionWorking=res_list[middleIndex]
                                        ###############################

                                                xCompleteSpotSizeforContactColoc.append(xContinuousContactSpotSize)
                                                xCompleteDendriteDendriteContactSpotPositionsColoc.append(xContactSpotPostionWorking)
                                                xContactBranchIndexIdColoc.append(vBranchIndex)
                                                xContactSegmentIdColoc.append(vSegmentIds[vBranchIndex])
                                                xSpotSizeforContinuousContactId=[]
                                                # print('final point contact', 'w=', w)
                                                continue

                                        xContactTest=np.isin(xCBIarrayColoc[:,w],xCBIarrayColoc[:,w+1]).astype(int)
                                        is_all_zero = bool(np.all((xContactTest==0)))
                                        if is_all_zero:
                                            xCompleteDendriteDendriteContactSpotPositionsColoc.append(xDendriteCurrentWorkingPositions[xCBIarrayColoc[0,w]])
                                            xNumberDendriteContactsWorkingColoc=xNumberDendriteContactsWorkingColoc+1
                                            xContactLengthColoc=xContactLengthColoc+1
                                            xLengthContactsWorkingDendriteColoc.append(xContactLengthColoc)
                                            xCompleteSpotSizeforContactColoc.append(xDendriteCurrentWorkingRadii[xCBIarrayColoc[0,w]])
                                            xContactBranchIndexIdColoc.append(vBranchIndex)
                                            xContactSegmentIdColoc.append(vSegmentIds[vBranchIndex])
                                            # print ('single point contact','w=', w)
                                            xContactLengthColoc=0
                            ###############################
                            ###############################
                                        elif ((xContactTest[0] == 1) and (xContactTest[2] == 1)):
                                            # if ((xCBIarrayColoc[1,w]==(xCBIarrayColoc[1,w+1])-1) or (xCBIarrayColoc[1,w]==(xCBIarrayColoc[1,w+1])-2) or (xCBIarrayColoc[1,w]==(xCBIarrayColoc[1,w+1])+1)):
                                            #     # print('skip one - 2 consecutive contacts same dendrite same point','w=', w)
                                            #     continue
                                            xIsContinuous=True
                                            continue
                            ###############################
                            ###############################
                                        elif ((xContactTest[0] == 0) and (xContactTest[2] == 1)):
                                            if ((xCBIarrayColoc[0,w]==(xCBIarrayColoc[0,w+1])-1) or (xCBIarrayColoc[0,w]==(xCBIarrayColoc[0,w+1])-2)):# or ((xCBIarrayColoc[1,w]==xCBIarrayColoc[1,w+1]+1) or (xCBIarrayColoc[1,w]+1==xCBIarrayColoc[1,w+1]) or (xCBIarrayColoc[1,w]==xCBIarrayColoc[1,w+1])):
                                                xContactLengthColoc=xContactLengthColoc+1
                                                xIsContinuous=True
                                                xSpotSizeforContinuousContactId.append(xCBIarrayColoc[0,w])#mark working dendrite pointId for continuous contact
                                                # print ('continuous contact on working denrite#1','w=', w)
                                            else:
                                                xNumberDendriteContactsWorkingColoc=xNumberDendriteContactsWorkingColoc+1
                                                xContactLengthColoc=xContactLengthColoc+1
                                                xCompleteDendriteDendriteContactSpotPositionsColoc.append(xDendriteCurrentWorkingPositions[xCBIarrayColoc[0,w]])
                                                xLengthContactsWorkingDendriteColoc.append(xContactLengthColoc)
                                                xCompleteSpotSizeforContactColoc.append(xDendriteCurrentWorkingRadii[xCBIarrayColoc[0,w]])
                                                xContactBranchIndexIdColoc.append(vBranchIndex)
                                                xContactSegmentIdColoc.append(vSegmentIds[vBranchIndex])
                                                xContactLengthColoc=0
                                                # print ('single contact on working denrite','w=', w)
                                        elif ((xContactTest[0] == 1) and (xContactTest[2] == 0)):
                                                xNumberDendriteContactsWorkingColoc=xNumberDendriteContactsWorkingColoc+1
                                                xContactLengthColoc=xContactLengthColoc+1
                                                xCompleteDendriteDendriteContactSpotPositionsColoc.append(xDendriteCurrentWorkingPositions[xCBIarrayColoc[0,w]])
                                                xLengthContactsWorkingDendriteColoc.append(xContactLengthColoc)
                                                xCompleteSpotSizeforContactColoc.append(xDendriteCurrentWorkingRadii[xCBIarrayColoc[0,w]])
                                                xContactBranchIndexIdColoc.append(vBranchIndex)
                                                xContactSegmentIdColoc.append(vSegmentIds[vBranchIndex])
                                                xContactLengthColoc=0
                                                # print ('single contact on working denrite','w=', w)
                            else:
                                # print ('no contacts')
                                xNumberDendriteContactsWorkingColoc=0
                                ###########################################################
                            #Collate number of contacts per dendrite segment
                            vStatisticFilamentDendriteDendriteContactsColoc.append(xNumberDendriteContactsWorkingColoc)


        ##############################################################################
        ##############################################################################
                        if vOptionDendriteToDendriteContact==1:
                            #Find Dendrite Points that are  "close" to ALL Filament Points min value per row in array
                            xDendriteToDendriteDistanceArray=cdist(xDendriteCurrentWorkingPositions,xTotalPointPositionWorking)
                            #Subtract Radii of other segment from the array
                            xDendriteToDendriteDistanceArray=xDendriteToDendriteDistanceArray-xTotalPointRadiiWorking
                            #Dendrite Point index of points contacting same filament.
                            xCBIarray=np.array(np.where(xDendriteToDendriteDistanceArray <= 0))
                            #add row indicating branchindex
                            xCBIarray=np.vstack([xCBIarray,np.take(xTotalPointIDWorking,xCBIarray[1].tolist())])

                            xNodeAttachedSegments=list(set(chain(*([xBranchSharingNodesALL[i] for i in [i for i, lst in enumerate(xBranchSharingNodesALL) if vBranchIndex in lst]]))))
                            #Identify which contact points are on Node attached segments
                            xNodeTest=np.vstack([np.isin(xCBIarray[2], xNodeAttachedSegments),
                                                    np.isin(xCBIarray[0], np.array([0,1,2,3,4,5,len(xDendriteCurrentWorkingPositions)-6,len(xDendriteCurrentWorkingPositions)-5,len(xDendriteCurrentWorkingPositions)-4,len(xDendriteCurrentWorkingPositions)-3,len(xDendriteCurrentWorkingPositions)-2,len(xDendriteCurrentWorkingPositions)-1]))])
                            #Delete contact point at ends with Node attached branches
                            xCBIarray=np.delete(xCBIarray, np.where(np.all(xNodeTest,axis=0)),axis=1)
                            a=xCBIarray[2,:]
                            b=xCBIarray[0,:]
                            ind = np.lexsort((b,a))
                            xCBIarray=xCBIarray[:,ind]
                            w=1
                            w=0
                            # xCompleteDendriteDendriteContactSpotPositions=[]
                            xSizeCBIarray=np.size(xCBIarray, axis=1)
                            xIsContinuous=False
                            xContactLength=0
                            xNumberDendriteContactsWorking=0
                            xSpotSizeforContinuousContactId=[]
                            xContactSpotPostionWorking=[]
                            if xSizeCBIarray==1:#only one contact point
                                xDistToSoma = np.sqrt((vFilamentsXYZ[vBeginningVertex][0]-xDendriteCurrentWorkingPositions[xCBIarray[0,0]][0])**2 + (vFilamentsXYZ[vBeginningVertex][1]-xDendriteCurrentWorkingPositions[xCBIarray[0,0]][1])**2 +(vFilamentsXYZ[vBeginningVertex][2]-xDendriteCurrentWorkingPositions[xCBIarray[0,0]][2])**2)
                                if xDistToSoma < vOptionSomaThresholdValue:
                                    continue
                                else:
                                    xCompleteDendriteDendriteContactSpotPositions.append(xDendriteCurrentWorkingPositions[xCBIarray[0,0]])
                                    xNumberDendriteContactsWorking=xNumberDendriteContactsWorking+1
                                    xContactLength=1
                                    xLengthContactsWorkingDendrite.append(xContactLength)
                                    xCompleteSpotSizeforContact.append(xDendriteCurrentWorkingRadii[xCBIarray[0,w]])
                                    xContactBranchIndexId.append(vBranchIndex)
                                    xContactSegmentId.append(vSegmentIds[vBranchIndex])
                                    xContactLength=0
                                    # print ('Only one contact')
                            elif xSizeCBIarray>1:#multiple contact points
                                # w=2
                                # w=1
                                w=0#Set to zero for single point contact only
                                for w in range (xSizeCBIarray):
                                    if (w==xSizeCBIarray-1) and xIsContinuous==False:#Test if last contact point
                                        xDistToSoma = np.sqrt((vFilamentsXYZ[vBeginningVertex][0]-xDendriteCurrentWorkingPositions[xCBIarray[0,w]][0])**2 + (vFilamentsXYZ[vBeginningVertex][1]-xDendriteCurrentWorkingPositions[xCBIarray[0,w]][1])**2 +(vFilamentsXYZ[vBeginningVertex][2]-xDendriteCurrentWorkingPositions[xCBIarray[0,w]][2])**2)
                                        if xDistToSoma < vOptionSomaThresholdValue:
                                            xContactLength=0
                                            continue
                                        else:
                                            xCompleteDendriteDendriteContactSpotPositions.append(xDendriteCurrentWorkingPositions[xCBIarray[0,w]])
                                            xNumberDendriteContactsWorking=xNumberDendriteContactsWorking+1
                                            xContactLength=1
                                            xLengthContactsWorkingDendrite.append(xContactLength)
                                            xCompleteSpotSizeforContact.append(xDendriteCurrentWorkingRadii[xCBIarray[0,w]])
                                            xContactBranchIndexId.append(vBranchIndex)
                                            xContactSegmentId.append(vSegmentIds[vBranchIndex])
                                        # print ('last point contact','w=', w)

                                    elif (w==xSizeCBIarray-1) and xIsContinuous==True:
                                        xContactLength=xContactLength+1
                                        xLengthContactsWorkingDendrite.append(xContactLength)
                                        xNumberDendriteContactsWorking=xNumberDendriteContactsWorking+1
                                        xSpotSizeforContinuousContactId.append(xCBIarray[0,w])#mark working dendrite pointId for continuous contact

                                        ###############################
                                        if len(xDendriteCurrentWorkingPositions)==1:
                                            xContinuousContactSpotSize=xDendriteCurrentWorkingRadii[xCBIarray[0,w]]
                                        else:
                                            x = np.array([ xDendriteCurrentWorkingPositions[index][0] for index in xSpotSizeforContinuousContactId ])
                                            y = np.array([ xDendriteCurrentWorkingPositions[index][1] for index in xSpotSizeforContinuousContactId ])
                                            z = np.array([ xDendriteCurrentWorkingPositions[index][2] for index in xSpotSizeforContinuousContactId ])
                                            dist_array = (x[:-1]-x[1:])**2 + (y[:-1]-y[1:])**2 +(z[:-1]-z[1:])**2
                                            xContinuousContactSpotSize=(np.sum(np.sqrt(dist_array)))/2
                                        #Find Center position
                                        res_list = [xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId]
                                        if len([xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId])%2==0:
                                            first_middle = int(len(res_list) / 2) - 1
                                            second_middle = int(len(res_list) / 2)
                                            xContactSpotPostionWorking=res_list[second_middle]
                                        else:
                                            middleIndex = round((len(res_list) - 1)/2)
                                            xContactSpotPostionWorking=res_list[middleIndex]
                                        ###############################

                                        xDistToSoma = np.sqrt((vFilamentsXYZ[vBeginningVertex][0]-xContactSpotPostionWorking[0])**2 + (vFilamentsXYZ[vBeginningVertex][1]-xContactSpotPostionWorking[1])**2 +(vFilamentsXYZ[vBeginningVertex][2]-xContactSpotPostionWorking[2])**2)
                                        if xDistToSoma < vOptionSomaThresholdValue:
                                            xSpotSizeforContinuousContactId=[]#Reset to blank for next contact point
                                            xContactLength=0
                                            continue
                                        else:
                                        ###############################

                                            #CalculateContactSpotSize(xSpotSizeforContinuousContactId,xDendriteCurrentWorkingPositions,w)#calculate length of contact
                                            xCompleteSpotSizeforContact.append(xContinuousContactSpotSize)
                                            xCompleteDendriteDendriteContactSpotPositions.append(xContactSpotPostionWorking)
                                            xContactBranchIndexId.append(vBranchIndex)
                                            xContactSegmentId.append(vSegmentIds[vBranchIndex])
                                            # print ('last point with continuous contact','w=', w)
                                            xSpotSizeforContinuousContactId=[]#Reset to blank for next contact point
                                            xContactLength=0
                                    else:
                            ###############################
                                        if xIsContinuous:# but not yet identified as end on continuous contact
                                            xContactTest=np.isin(xCBIarray[:,w],xCBIarray[:,w+1]).astype(int)
                                            if ((xContactTest[2] == 0) and (xContactTest[0] == 0)):

                                                xNumberDendriteContactsWorking=xNumberDendriteContactsWorking+1
                                                xContactLength=xContactLength+1
                                                xLengthContactsWorkingDendrite.append(xContactLength)
                                                xIsContinuous==False#Reset this marker
                                                xSpotSizeforContinuousContactId.append(xCBIarray[0,w])#mark working dendrite pointId for continuous contact

                                                ###############################
                                                if len(xDendriteCurrentWorkingPositions)==1:
                                                    xContinuousContactSpotSize=xDendriteCurrentWorkingRadii[xCBIarray[0,w]]
                                                else:
                                                    x = np.array([ xDendriteCurrentWorkingPositions[index][0] for index in xSpotSizeforContinuousContactId ])
                                                    y = np.array([ xDendriteCurrentWorkingPositions[index][1] for index in xSpotSizeforContinuousContactId ])
                                                    z = np.array([ xDendriteCurrentWorkingPositions[index][2] for index in xSpotSizeforContinuousContactId ])
                                                    dist_array = (x[:-1]-x[1:])**2 + (y[:-1]-y[1:])**2 +(z[:-1]-z[1:])**2
                                                    xContinuousContactSpotSize=(np.sum(np.sqrt(dist_array)))/2
                                                #Find Center position
                                                res_list = [xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId]
                                                if len([xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId])%2==0:
                                                    first_middle = int(len(res_list) / 2) - 1
                                                    second_middle = int(len(res_list) / 2)
                                                    xContactSpotPostionWorking=res_list[second_middle]
                                                else:
                                                    middleIndex = round((len(res_list) - 1)/2)
                                                    xContactSpotPostionWorking=res_list[middleIndex]
                                                ###############################
                                                xDistToSoma = np.sqrt((vFilamentsXYZ[vBeginningVertex][0]-xContactSpotPostionWorking[0])**2 + (vFilamentsXYZ[vBeginningVertex][1]-xContactSpotPostionWorking[1])**2 +(vFilamentsXYZ[vBeginningVertex][2]-xContactSpotPostionWorking[2])**2)
                                                if xDistToSoma < vOptionSomaThresholdValue:
                                                    xSpotSizeforContinuousContactId=[]#Reset to blank for next contact point
                                                    xContactLength=0
                                                    continue
                                                else:
                                                ###############################

                                                    xCompleteSpotSizeforContact.append(xContinuousContactSpotSize)
                                                    xCompleteDendriteDendriteContactSpotPositions.append(xContactSpotPostionWorking)
                                                    xContactBranchIndexId.append(vBranchIndex)
                                                    xContactSegmentId.append(vSegmentIds[vBranchIndex])
                                                    xSpotSizeforContinuousContactId=[]#Reset to blank for next contact point
                                                    # print('Final continuous point')
                                                    xContactLength=0
                                                    continue
                                            elif ((xContactTest[0] == 1) and (xContactTest[2] == 1)) and xCBIarray[1,w]-3 <= xCBIarray[1,w+1] <= xCBIarray[1,w]+3:
                                                #continuous but does not add to length of contact
                                                # print('skip one - 2 consecutive contacts same dendrite same point','w=', w)
                                                continue
                                            elif ((xContactTest[0] == 0) and (xContactTest[2] == 1)):
                                                if ((xCBIarray[0,w]==(xCBIarray[0,w+1])-1) or (xCBIarray[0,w]==(xCBIarray[0,w+1])-2)) and xCBIarray[1,w]-3 <= xCBIarray[1,w+1] <= xCBIarray[1,w]+3:
                                                    #continuous and add to length of contact
                                                    xContactLength=xContactLength+1
                                                    xSpotSizeforContinuousContactId.append(xCBIarray[0,w])#mark working dendrite pointId for continuous contact
                                                    xIsContinuous==True
                                                    # print ('continuous contact on working denrite-next','w=', w)
                                                    continue
                                            elif ((xContactTest[0] == 1) and (xContactTest[2] == 0)):

                                                xNumberDendriteContactsWorking=xNumberDendriteContactsWorking+1
                                                xContactLength=xContactLength+1
                                                xLengthContactsWorkingDendrite.append(xContactLength)
                                                xContactLength=0
                                                xIsContinuous==False#Reset this marker
                                                xSpotSizeforContinuousContactId.append(xCBIarray[0,w])#mark working dendrite pointId for continuous contact

                                                                                    ###############################
                                                if len(xDendriteCurrentWorkingPositions)==1:
                                                    xContinuousContactSpotSize=xDendriteCurrentWorkingRadii[xCBIarray[0,w]]
                                                else:
                                                    x = np.array([ xDendriteCurrentWorkingPositions[index][0] for index in xSpotSizeforContinuousContactId ])
                                                    y = np.array([ xDendriteCurrentWorkingPositions[index][1] for index in xSpotSizeforContinuousContactId ])
                                                    z = np.array([ xDendriteCurrentWorkingPositions[index][2] for index in xSpotSizeforContinuousContactId ])
                                                    dist_array = (x[:-1]-x[1:])**2 + (y[:-1]-y[1:])**2 +(z[:-1]-z[1:])**2
                                                    xContinuousContactSpotSize=(np.sum(np.sqrt(dist_array)))/2
                                                #Find Center position
                                                res_list = [xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId]
                                                if len([xDendriteCurrentWorkingPositions[i] for i in xSpotSizeforContinuousContactId])%2==0:
                                                    first_middle = int(len(res_list) / 2) - 1
                                                    second_middle = int(len(res_list) / 2)
                                                    xContactSpotPostionWorking=res_list[second_middle]
                                                else:
                                                    middleIndex = round((len(res_list) - 1)/2)
                                                    xContactSpotPostionWorking=res_list[middleIndex]
                                                ###############################

                                                xDistToSoma = np.sqrt((vFilamentsXYZ[vBeginningVertex][0]-xContactSpotPostionWorking[0])**2 + (vFilamentsXYZ[vBeginningVertex][1]-xContactSpotPostionWorking[1])**2 +(vFilamentsXYZ[vBeginningVertex][2]-xContactSpotPostionWorking[2])**2)
                                                if xDistToSoma < vOptionSomaThresholdValue:
                                                    xSpotSizeforContinuousContactId=[]#Reset to blank for next contact point
                                                    xContactLength=0
                                                    continue
                                                else:
                                                ###############################

                                                    xCompleteSpotSizeforContact.append(xContinuousContactSpotSize)
                                                    xCompleteDendriteDendriteContactSpotPositions.append(xContactSpotPostionWorking)
                                                    xContactBranchIndexId.append(vBranchIndex)
                                                    xContactSegmentId.append(vSegmentIds[vBranchIndex])
                                                    xSpotSizeforContinuousContactId=[]
                                                    # print('final point contact', 'w=', w)
                                                    continue
                                        xContactTest=np.isin(xCBIarray[:,w],xCBIarray[:,w+1]).astype(int)
                                        is_all_zero = bool(np.all((xContactTest==0)))
                                        if is_all_zero:
                                            xDistToSoma = np.sqrt((vFilamentsXYZ[vBeginningVertex][0]-xDendriteCurrentWorkingPositions[xCBIarray[0,w]][0])**2 + (vFilamentsXYZ[vBeginningVertex][1]-xDendriteCurrentWorkingPositions[xCBIarray[0,w]][1])**2 +(vFilamentsXYZ[vBeginningVertex][2]-xDendriteCurrentWorkingPositions[xCBIarray[0,w]][2])**2)
                                            if xDistToSoma < vOptionSomaThresholdValue:
                                                xContactLength=0
                                                continue
                                            else:
                                                xCompleteDendriteDendriteContactSpotPositions.append(xDendriteCurrentWorkingPositions[xCBIarray[0,w]])
                                                xNumberDendriteContactsWorking=xNumberDendriteContactsWorking+1
                                                xContactLength=xContactLength+1
                                                xLengthContactsWorkingDendrite.append(xContactLength)
                                                xCompleteSpotSizeforContact.append(xDendriteCurrentWorkingRadii[xCBIarray[0,w]])
                                                xContactBranchIndexId.append(vBranchIndex)
                                                xContactSegmentId.append(vSegmentIds[vBranchIndex])
                                                # print ('single point contact','w=', w)
                                                xContactLength=0
                            ###############################
                            ###############################
                                        elif ((xContactTest[0] == 1) and (xContactTest[2] == 1)):
                                            if ((xCBIarray[1,w]==(xCBIarray[1,w+1])-1) or (xCBIarray[1,w]==(xCBIarray[1,w+1])-2) or (xCBIarray[1,w]==(xCBIarray[1,w+1])+1)):
                                                # print('skip one - 2 consecutive contacts same dendrite same point','w=', w)
                                                continue
                            ###############################
                            ###############################
                                        elif ((xContactTest[0] == 0) and (xContactTest[2] == 1)):
                                            if ((xCBIarray[0,w]==(xCBIarray[0,w+1])-1) or (xCBIarray[0,w]==(xCBIarray[0,w+1])-2)) or ((xCBIarray[1,w]==xCBIarray[1,w+1]+1) or (xCBIarray[1,w]+1==xCBIarray[1,w+1]) or (xCBIarray[1,w]==xCBIarray[1,w+1])):
                                                xContactLength=xContactLength+1
                                                xIsContinuous=True
                                                xSpotSizeforContinuousContactId.append(xCBIarray[0,w])#mark working dendrite pointId for continuous contact
                                                # print ('continuous contact on working denrite#1','w=', w)
                                            else:
                                                xDistToSoma = np.sqrt((vFilamentsXYZ[vBeginningVertex][0]-xDendriteCurrentWorkingPositions[xCBIarray[0,w]][0])**2 + (vFilamentsXYZ[vBeginningVertex][1]-xDendriteCurrentWorkingPositions[xCBIarray[0,w]][1])**2 +(vFilamentsXYZ[vBeginningVertex][2]-xDendriteCurrentWorkingPositions[xCBIarray[0,w]][2])**2)
                                                if xDistToSoma < vOptionSomaThresholdValue:
                                                    xContactLength=0
                                                else:
                                                    xNumberDendriteContactsWorking=xNumberDendriteContactsWorking+1
                                                    xContactLength=xContactLength+1
                                                    xCompleteDendriteDendriteContactSpotPositions.append(xDendriteCurrentWorkingPositions[xCBIarray[0,w]])
                                                    xLengthContactsWorkingDendrite.append(xContactLength)
                                                    xCompleteSpotSizeforContact.append(xDendriteCurrentWorkingRadii[xCBIarray[0,w]])
                                                    xContactBranchIndexId.append(vBranchIndex)
                                                    xContactSegmentId.append(vSegmentIds[vBranchIndex])
                                                    xContactLength=0
                                                # print ('single contact on working denrite','w=', w)
                                        elif ((xContactTest[0] == 1) and (xContactTest[2] == 0)):
                                            xDistToSoma = np.sqrt((vFilamentsXYZ[vBeginningVertex][0]-xDendriteCurrentWorkingPositions[xCBIarray[0,w]][0])**2 + (vFilamentsXYZ[vBeginningVertex][1]-xDendriteCurrentWorkingPositions[xCBIarray[0,w]][1])**2 +(vFilamentsXYZ[vBeginningVertex][2]-xDendriteCurrentWorkingPositions[xCBIarray[0,w]][2])**2)
                                            if xDistToSoma < vOptionSomaThresholdValue:
                                                xContactLength=0
                                            else:
                                                xNumberDendriteContactsWorking=xNumberDendriteContactsWorking+1
                                                xContactLength=xContactLength+1
                                                xCompleteDendriteDendriteContactSpotPositions.append(xDendriteCurrentWorkingPositions[xCBIarray[0,w]])
                                                xLengthContactsWorkingDendrite.append(xContactLength)
                                                xCompleteSpotSizeforContact.append(xDendriteCurrentWorkingRadii[xCBIarray[0,w]])
                                                xContactBranchIndexId.append(vBranchIndex)
                                                xContactSegmentId.append(vSegmentIds[vBranchIndex])
                                                xContactLength=0
                                                # print ('single contact on working denrite','w=', w)
                            else:
                                # print ('no contacts')
                                xNumberDendriteContactsWorking=0
                            # print(xLengthContactsWorkingDendrite)
                            # print(xCompleteDendriteDendriteContactSpotPositions)
                            ###########################################################
                            #Collate number of contacts per dendrite segment
                            vStatisticFilamentDendriteDendriteContacts.append(xNumberDendriteContactsWorking)
                    progress_bar3['value'] = int((vBranchIndex+1)/vNumberOfDendriteBranches*100) #  % out of 100
                    master.update()
        #############################################################################
                #After processing entire Filament and all branches
                #Adding NEW spots object for the contact points
                if vOptionDendriteToDendriteContact==1:
                    if  vStatisticFilamentDendriteDendriteContacts == 0:
                        vNewSpotsDendriteDendriteContacts = vImarisApplication.GetFactory().CreateSpots()
                        vNewSpotsDendriteDendriteContacts.SetName('NO Intra Dendrite-Dendrite Contacts -- FilamentId:' + str(vFilamentIds[vFilamentCountActual-1]))
                        vNewSpotsAnalysisFolder.AddChild(vNewSpotsDendriteDendriteContacts, -1)
                    else:
                        vNewSpotsDendriteDendriteContacts = vImarisApplication.GetFactory().CreateSpots()
                        vNewSpotsDendriteDendriteContacts.SetName('Intra Dendrite-Dendrite Contacts -- FilamentId:' + str(vFilamentIds[vFilamentCountActual-1]))
                        vNewSpotsOnFilamentIndex=[vFilamentsIndexT]*len(xCompleteDendriteDendriteContactSpotPositions)
                        zRandomColor=((random.uniform(0, 1)) * 256 * 256 * 256 )
                        vNewSpotsDendriteDendriteContacts.SetColorRGBA(zRandomColor)
                        vNewSpotsDendriteDendriteContacts.Set(xCompleteDendriteDendriteContactSpotPositions, vNewSpotsOnFilamentIndex, xCompleteSpotSizeforContact)
                        vNewSpotsAnalysisFolder.AddChild(vNewSpotsDendriteDendriteContacts, -1)
                        vImarisApplication.GetSurpassScene().AddChild(vNewSpotsAnalysisFolder, -1)
            #############################################################################
                        ##ADD new Stat distance to starting points to new Spots objects
                        vNewSpotsOnFilamentIndex=[vFilamentsIndexT+1]*len(xCompleteDendriteDendriteContactSpotPositions)
                        vSpotsvIds=list(range(len(xCompleteDendriteDendriteContactSpotPositions)))
                        vSpotsStatUnits=['um']*len(xCompleteDendriteDendriteContactSpotPositions)
                        vSpotsStatFactors=(['Spot']*len(xCompleteDendriteDendriteContactSpotPositions), [str(x) for x in vNewSpotsOnFilamentIndex] )
                        vSpotsStatFactorName=['Category','Time']
                        vSpotsStatNames=[' Intra Dendrite contact length']*len(xCompleteDendriteDendriteContactSpotPositions)
                        vNewSpotsDendriteDendriteContacts.AddStatistics(vSpotsStatNames, xCompleteSpotSizeforContact,
                                                      vSpotsStatUnits, vSpotsStatFactors,
                                                      vSpotsStatFactorName, vSpotsvIds)
        #############################################################################
                if vOptionFilamentToFilamentContact==1:
                    if vStatisticFilamentDendriteDendriteContactsColoc == 0:
                        vNewSpotsFilamentFilamentContacts = vImarisApplication.GetFactory().CreateSpots()
                        vNewSpotsFilamentFilamentContacts.SetName('NO contacts '+ str(vFilaments.GetName())+' - & - '+ str(vFilamentColoc.GetName()) +' -- FilamentId:' + str(vFilamentIds[vFilamentCountActual-1]))
                        vNewSpotsAnalysisFolder.AddChild(vNewSpotsFilamentFilamentContacts, -1)
                    else:
                        vNewSpotsFilamentFilamentContacts = vImarisApplication.GetFactory().CreateSpots()
                        vNewSpotsFilamentFilamentContacts.SetName(str(vFilaments.GetName())+' -- '+ str(vFilamentColoc.GetName()) + 'CONTACTS -- FilamentId:' + str(vFilamentIds[vFilamentCountActual-1]))
                        vNewSpotsOnFilamentIndex=[vFilamentsIndexT]*len(xCompleteDendriteDendriteContactSpotPositionsColoc)
                        zRandomColor=((random.uniform(0, 1)) * 256 * 256 * 256 )
                        vNewSpotsFilamentFilamentContacts.SetColorRGBA(zRandomColor)
                        vNewSpotsFilamentFilamentContacts.Set(xCompleteDendriteDendriteContactSpotPositionsColoc, vNewSpotsOnFilamentIndex, xCompleteSpotSizeforContactColoc)
                        vNewSpotsAnalysisFolder.AddChild(vNewSpotsFilamentFilamentContacts, -1)
                        vImarisApplication.GetSurpassScene().AddChild(vNewSpotsAnalysisFolder, -1)
            #############################################################################
                        ##ADD new Stat distance to starting points to new Spots objects
                        vNewSpotsOnFilamentIndex=[vFilamentsIndexT+1]*len(xCompleteDendriteDendriteContactSpotPositionsColoc)
                        vSpotsvIds=list(range(len(xCompleteDendriteDendriteContactSpotPositionsColoc)))
                        vSpotsStatUnits=['um']*len(xCompleteDendriteDendriteContactSpotPositionsColoc)
                        vSpotsStatFactors=(['Spot']*len(xCompleteDendriteDendriteContactSpotPositionsColoc), [str(x) for x in vNewSpotsOnFilamentIndex] )
                        vSpotsStatFactorName=['Category','Time']
                        vSpotsStatNames=[' Filament Coloc contact length']*len(xCompleteDendriteDendriteContactSpotPositionsColoc)
                        vNewSpotsFilamentFilamentContacts.AddStatistics(vSpotsStatNames, xCompleteSpotSizeforContactColoc,
                                                      vSpotsStatUnits, vSpotsStatFactors,
                                                      vSpotsStatFactorName, vSpotsvIds)
        #############################################################################

                #After cycling through all segment branches
                #Filament contact statistics
                xCompleteNumberofContactsperFilament.append(sum(vStatisticFilamentDendriteDendriteContacts))
                xCompleteNumberofContactsperFilamentColoc.append(sum(vStatisticFilamentDendriteDendriteContactsColoc))
        ###############################################################################

        #New Stat -- Measure distance of that Spot to Soma
                            #
        ###############################################################################
        ###############################################################################
                if xCompleteDendriteDendriteContactSpotPositions!=[]:
                    wNewSpotsOnFilament=xCompleteDendriteDendriteContactSpotPositions

                    if vBeginningVertex !=-1:
                        wNewFilamentsEdges=list(vFilamentsEdges)
                        wNewFilamentsRadius=list(vFilamentsRadius)
                        wNewFilamentsXYZ=list(vFilamentsXYZ)
                        wNewFilamentsTypes=list(vTypes)

                        # xContactBranchIndexId#Segment Id where the contact was found.  Need to make sure distance to soma selects point on this segment
                        # vFilamentsXYZ
                        # xAllDendriteSegmentsId


                        # for b in range (len(xContactBranchIndexId)):
                        #     xNewStuffIndex=[i for i,val in enumerate(x) if val!=xContactBranchIndexId(b)]

                        #     if len(xContactBranchIndexId)>1:
                        #         xFilamentsXYZTemp=list(itemgetter(*xNewStuffIndex)(xFilamentsXYZ))
                        #     else:
                        #         xFilamentsXYZTemp=[x[1] for x in enumerate(xFilamentsXYZ)
                        #                                                 if x[0] in xNewStuffIndex]
                        #     wSpotToAllFilamentDistanceArrayOriginal=cdist(xCompleteDendriteDendriteContactSpotPositions,xFilamentsXYZTemp)
                        # # wSpotToAllFilamentDistanceArrayOriginal=wSpotToAllFilamentDistanceArrayOriginal- vFilamentsRadius -[max(vSpotsColocRadiusWorking[0])]*len(vFilamentsRadius)

                        # #For each spot, find index on filament of closest point
                        #     wSpotsFilamentClosestDistancePointIndex=np.argmin(wSpotToAllFilamentDistanceArrayOriginal, axis=1)




                        #Create array of distance measures to original filament points
                        wSpotToAllFilamentDistanceArrayOriginal=cdist(xCompleteDendriteDendriteContactSpotPositions,vFilamentsXYZ)
                        # wSpotToAllFilamentDistanceArrayOriginal=wSpotToAllFilamentDistanceArrayOriginal- vFilamentsRadius -[max(vSpotsColocRadiusWorking[0])]*len(vFilamentsRadius)

                        #For each spot, find index on filament of closest point
                        wSpotsFilamentClosestDistancePointIndex=np.argmin(wSpotToAllFilamentDistanceArrayOriginal, axis=1)

                        #test is spine attachment point is branch point, if so add one
                        for i in range (len(wSpotsFilamentClosestDistancePointIndex)):
                            if wSpotsFilamentClosestDistancePointIndex[i] in wFilamentBranchPointIndex or wSpotsFilamentClosestDistancePointIndex[i] in wFilamentTerminalPointIndex:
                                wSpotNearest = cdist([xCompleteDendriteDendriteContactSpotPositions[i]],vFilamentsXYZ)
                                wSpotNearest = wSpotNearest - vFilamentsRadius
                                wSpotsNearestIndex=np.argpartition(wSpotNearest, 2)
                                wSpotsFilamentClosestDistancePointIndex[i]=wSpotsNearestIndex[0][1]
                                if wSpotsFilamentClosestDistancePointIndex[i] in wFilamentBranchPointIndex or wSpotsFilamentClosestDistancePointIndex[i] in wFilamentTerminalPointIndex:
                                    wSpotsFilamentClosestDistancePointIndex[i]=wSpotsNearestIndex[0][2]
                                if wSpotsFilamentClosestDistancePointIndex[i] in wFilamentBranchPointIndex or wSpotsFilamentClosestDistancePointIndex[i] in wFilamentTerminalPointIndex:
                                    wSpotsFilamentClosestDistancePointIndex[i]=wSpotsNearestIndex[0][3]

        #Test if attachment point is on contact dendrite, if not take another point (second closest),etc...
                        # xAllDendriteSegmentsId
                        # xFinal=[]
                        # #Find DendriteDendrite contact position in the ReOrdered FilamentXYZ List
                        # for b in range(len(xCompleteDendriteDendriteContactSpotPositions)):
                        #     xFinal.append(np.where((vFilamentsXYZ == x[b]).all(axis=1)))

                        #loop for each spot within threshold
                        #append new filament and create list of new spots
                        for i in range (len(xCompleteDendriteDendriteContactSpotPositions)):
                            wNewFilamentsXYZ.append(xCompleteDendriteDendriteContactSpotPositions[i])
                            wNewFilamentsRadius.append(1)
                            wNewFilamentsEdges.append([wSpotsFilamentClosestDistancePointIndex[i],len(vFilamentsRadius)+i])
                            wNewFilamentsTypes.append(1)

                        vNewFilament=vImarisApplication.GetFactory().CreateFilaments()
                        vNewFilament.AddFilament(wNewFilamentsXYZ, wNewFilamentsRadius, wNewFilamentsTypes, wNewFilamentsEdges, vFilamentsIndexT)
                        vNewFilament.SetBeginningVertexIndex(0, 0)
                        #Reset the "new filament"
                        wNewFilamentsXYZ=[]
                        wNewFilamentsRadius=[]
                        wNewFilamentsEdges=[]
                        wNewFilamentsTypes=[]

                    #Grab New Filament Spine Statistics for attachment point distance.
                        vNewFilamentStatistics = vNewFilament.GetStatistics()
                        vNewFilamentStatNames = vNewFilamentStatistics.mNames
                        vNewFilamentStatValues = vNewFilamentStatistics.mValues
                        vNewFilamentStatIds = vNewFilamentStatistics.mIds
                        vNewFilamentSpineAttPtDistIndex=[i for i,val in enumerate(vNewFilamentStatNames)
                                                          if val==('Spine Attachment Pt Distance')]
                        vNewFilamentSpinePtPosXIndex=[i for i,val in enumerate(vNewFilamentStatNames)
                                                          if val==('Spine Terminal Pt Position X')]
                        if len(vNewFilamentSpineAttPtDistIndex)>1:
                            vNewFilamentSpineAttPtDist=list(itemgetter(*vNewFilamentSpineAttPtDistIndex)(vNewFilamentStatValues))
                            vNewFilamentSpinePtPosX=list(itemgetter(*vNewFilamentSpinePtPosXIndex)(vNewFilamentStatValues))
                            vNewFilamentStatIdsPosX=list(itemgetter(*vNewFilamentSpinePtPosXIndex)(vNewFilamentStatIds))
                            vNewFilamentStatIdsDist=list(itemgetter(*vNewFilamentSpineAttPtDistIndex)(vNewFilamentStatIds))
                        else:
                            vNewFilamentSpineAttPtDist=[x[1] for x in enumerate(vNewFilamentStatValues)
                                                    if x[0] in vNewFilamentSpineAttPtDistIndex]
                            vNewFilamentSpinePtPosX=[x[1] for x in enumerate(vNewFilamentStatValues)
                                                    if x[0] in vNewFilamentSpinePtPosXIndex]
                            vNewFilamentStatIdsDist=[x[1] for x in enumerate(vNewFilamentStatIds)
                                                    if x[0] in vNewFilamentSpineAttPtDistIndex]
                            vNewFilamentStatIdsPosX=[x[1] for x in enumerate(vNewFilamentStatIds)
                                                    if x[0] in vNewFilamentSpinePtPosXIndex]


                        #Collate all spots for each filament
                        for i in range (len(xCompleteDendriteDendriteContactSpotPositions)):
                            #find nearest index
                            idx = (np.abs(np.array(vNewFilamentSpinePtPosX)-wNewSpotsOnFilament[i][0])).argmin()
                            xCompleteSpotDistAlongFilamentStat.append(vNewFilamentSpineAttPtDist[vNewFilamentStatIdsDist.index(vNewFilamentStatIdsPosX[idx])])
                            xCompleteSpotDistAlongFilamentStatWorking.append(vNewFilamentSpineAttPtDist[vNewFilamentStatIdsDist.index(vNewFilamentStatIdsPosX[idx])])



                            # xCompleteSpotDistAlongFilamentStat.append(vNewFilamentSpineAttPtDist[vNewFilamentStatIdsDist.index(vNewFilamentStatIdsPosX[vNewFilamentSpinePtPosX.index(wNewSpotsOnFilament[i][0])])])
                            # xCompleteSpotDistAlongFilamentStatWorking.append(vNewFilamentSpineAttPtDist[vNewFilamentStatIdsDist.index(vNewFilamentStatIdsPosX[vNewFilamentSpinePtPosX.index(wNewSpotsOnFilament[i][0])])])
                        vSpotsStatNames=[' Distance of Contact to Soma']*len(xCompleteDendriteDendriteContactSpotPositions)
                        vNewSpotsDendriteDendriteContacts.AddStatistics(vSpotsStatNames, xCompleteSpotDistAlongFilamentStat,
                                                      vSpotsStatUnits, vSpotsStatFactors,
                                                      vSpotsStatFactorName, vSpotsvIds)
                        vSpotsStatNames=[' Contact SegmentIds']*len(xCompleteDendriteDendriteContactSpotPositions)
                        vNewSpotsDendriteDendriteContacts.AddStatistics(vSpotsStatNames, [i-510000000000 for i in xContactSegmentId],
                                                      vSpotsStatUnits, vSpotsStatFactors,
                                                      vSpotsStatFactorName, vSpotsvIds)

                    else:
                        vNewSpotsvNewSpotsAlongFilament = vImarisApplication.GetFactory().CreateSpots()
                        vNewSpotsvNewSpotsAlongFilament.SetName('NO Colocalized Spots -- FilamentId:' + str(vFilamentIds[vFilamentCountActual-1]))
                        vNewSpotsAnalysisFolder.AddChild(vNewSpotsvNewSpotsAlongFilament, -1)

        # i=1
        # value=wNewSpotsOnFilament[1][0]
        # A=np.array(vNewFilamentSpinePtPosX)
        # idx = (np.abs(A-value)).argmin()



        ###############################################################################
        ###############################################################################
        #After Each Filament
        #Find distance along Filament for all boutons
        #     if vOptionFilamentBoutonDetection==1 and any(vStatisticFilamentBoutonsPerDendrite):
        #         wNewFilamentsEdges=list(vFilamentsEdges)
        #         wNewFilamentsRadius=list(vFilamentsRadius)
        #         wNewFilamentsXYZ=list(vFilamentsXYZ)
        #         wNewFilamentsTypes=list(vTypes)
        #         #Create array of distance measures
        #         vAllNewSpotsBoutonsPositionXYZ=[[(i-.01) for i in row] for row in vAllNewSpotsBoutonsPositionXYZ]

        #         wSpotToAllFilamentDistanceArray=cdist(vAllNewSpotsBoutonsPositionXYZ,vFilamentsXYZ)
        #         #Find Closet distance to nearest Filament point
        #         wSpotsFilamentClosestDistance=wSpotToAllFilamentDistanceArray.min(axis=1)
        #         #For each spot, find index on filament of closest point
        #         wSpotsFilamentClosestDistancePointIndex=np.argmin(wSpotToAllFilamentDistanceArray, axis=1)
        #         wSpotsIndex = [i for i,val in enumerate(wSpotsFilamentClosestDistance)
        #                                       if val<=vOptionFilamentSpotThreshold]
        #         #loop for each spot within threshold
        #         #append new filament and create list of new spots
        #         for i in range (len(wSpotsIndex)):
        #             wNewSpotsOnFilament.append(vAllNewSpotsBoutonsPositionXYZ[wSpotsIndex[i]])
        #             wNewSpotsOnFilamentRadius.append(vAllNewSpotsBoutonsRadius[wSpotsIndex[i]])
        #             wNewFilamentsXYZ.append(vAllNewSpotsBoutonsPositionXYZ[wSpotsIndex[i]])
        #             wNewFilamentsRadius.append(1)
        #             wNewFilamentsEdges.append([wSpotsFilamentClosestDistancePointIndex[wSpotsIndex[i]],len(vFilamentsRadius)+i])
        #             wNewFilamentsTypes.append(1)

        #         vNewFilament=vImarisApplication.GetFactory().CreateFilaments()
        #         vNewFilament.AddFilament(wNewFilamentsXYZ, wNewFilamentsRadius, wNewFilamentsTypes, wNewFilamentsEdges, vFilamentsIndexT)
        #         vNewFilament.SetBeginningVertexIndex(0, 0)

        # #Grab New Filament Spine Statistics for attachment point distance.
        #         vNewFilamentStatistics = vNewFilament.GetStatistics()
        #         vNewFilamentStatNames = vNewFilamentStatistics.mNames
        #         vNewFilamentStatValues = vNewFilamentStatistics.mValues
        #         vNewFilamentSpineAttPtDistIndex=[i for i,val in enumerate(vNewFilamentStatNames)
        #                                           if val==('Spine Attachment Pt Distance')]
        #         vNewFilamentSpineAttPtPosXIndex=[i for i,val in enumerate(vNewFilamentStatNames)
        #                                           if val==('Spine Attachment Pt Position X')]
        #         vNewFilamentSpineAttPtPosYIndex=[i for i,val in enumerate(vNewFilamentStatNames)
        #                                           if val==('Spine Attachment Pt Position Y')]
        #         if len(vNewFilamentSpineAttPtDistIndex)>1:
        #             vNewFilamentSpineAttPtDist=list(itemgetter(*vNewFilamentSpineAttPtDistIndex)(vNewFilamentStatValues))
        #             vNewFilamentSpineAttPtPosX=list(itemgetter(*vNewFilamentSpineAttPtPosXIndex)(vNewFilamentStatValues))
        #             vNewFilamentSpineAttPtPosY=list(itemgetter(*vNewFilamentSpineAttPtPosYIndex)(vNewFilamentStatValues))
        #         else:
        #             vNewFilamentSpineAttPtDist=[x[1] for x in enumerate(vNewFilamentStatValues)
        #                                    if x[0] in vNewFilamentSpineAttPtDistIndex]
        #             vNewFilamentSpineAttPtPosX=[x[1] for x in enumerate(vNewFilamentStatValues)
        #                                     if x[0] in vNewFilamentSpineAttPtPosXIndex]
        #             vNewFilamentSpineAttPtPosY=[x[1] for x in enumerate(vNewFilamentStatValues)
        #                                     if x[0] in vNewFilamentSpineAttPtPosYIndex]

        #         #Collate all spots for each filament
        #         wCompleteBoutonDistAlongFilamentStat.append(vNewFilamentSpineAttPtDist)
        #         wCompleteBoutonDistAlongFilamentPosX.append(vNewFilamentSpineAttPtPosX)
        #         wCompleteBoutonDistAlongFilamentPosY.append(vNewFilamentSpineAttPtPosY)

        ###############################################################################
        ###############################################################################
        #After each Filament
        ###############################################################################
        # #Find Spot close to filament and measure distance along path to starting point
        # #Make spot position conect to filament as spine attachment point
            if vOptionFilamentCloseToSpots==1:
                #find duplicates and remove
                wSpotsAllIndexPerFilament=list(set(wSpotsAllIndexPerFilament))


                #number spots on dendrites and spines together
                wCompleteNumberSpotsPerFilament.append(len(wSpotsAllIndexPerFilament))
                #Calculate number of spots on spines and dendrites Per Filament
                if vFilamentCountActual==1:
                    wCompleteNumberSpotsonSpinePerFilament.append(sum(wNumberOfSpotsPerSpine))
                    wCompleteNumberSpotsonDendritePerFilament.append(sum(wNumberOfSpotsPerDendrite))
                else:
                    wCompleteNumberSpotsonSpinePerFilament.append(sum(wNumberOfSpotsPerSpine)-sum(wCompleteNumberSpotsonSpinePerFilament[0:vFilamentCountActual]))
                    wCompleteNumberSpotsonDendritePerFilament.append(sum(wNumberOfSpotsPerDendrite)-sum(wCompleteNumberSpotsonDendritePerFilament[0:vFilamentCountActual]))

                if wSpotsAllIndexPerFilament!=[]:
                    for i in range (len(wSpotsAllIndexPerFilament)):
                        wNewSpotsOnFilament.append(vSpotsColocPositionsWorking[wSpotsAllIndexPerFilament[i]])
                        wNewSpotsOnFilamentAll.append(vSpotsColocPositionsWorking[wSpotsAllIndexPerFilament[i]])
                        wNewSpotsOnFilamentRadius.append(vSpotsColocRadiusWorking[wSpotsAllIndexPerFilament[i]])

                    if vBeginningVertex !=-1:
                        wNewFilamentsEdges=list(vFilamentsEdges)
                        wNewFilamentsRadius=list(vFilamentsRadius)
                        wNewFilamentsXYZ=list(vFilamentsXYZ)
                        wNewFilamentsTypes=list(vTypes)

                        #Create array of distance measures to original filament points
                        wSpotToAllFilamentDistanceArrayOriginal=cdist(vSpotsColocPositionsWorking,vFilamentsXYZ)
                        wSpotToAllFilamentDistanceArrayOriginal=wSpotToAllFilamentDistanceArrayOriginal- vFilamentsRadius -[max(vSpotsColocRadiusWorking[0])]*len(vFilamentsRadius)
                        #For each spot, find index on filament of closest point
                        wSpotsFilamentClosestDistancePointIndex=np.argmin(wSpotToAllFilamentDistanceArrayOriginal, axis=1)
                        # i=0
                        #test if spine attachment point is branch point, if so add one
                        #for i in range (len(wSpotsFilamentClosestDistancePointIndex)):
                            # start = time.time()
                            # if wSpotsFilamentClosestDistancePointIndex[i] in wFilamentBranchPointIndex or wSpotsFilamentClosestDistancePointIndex[i] in wFilamentTerminalPointIndex:
                            #     wSpotNearest = cdist([vSpotsColocPositionsWorking[i]],vFilamentsXYZ)
                            #     wSpotNearest = wSpotNearest - vFilamentsRadius -[max(vSpotsColocRadiusWorking[0])]*len(vFilamentsRadius)
                            #     wSpotsNearestIndex=np.argpartition(wSpotNearest, 2)
                            #     wSpotsFilamentClosestDistancePointIndex[i]=wSpotsNearestIndex[0][1]
                            #     if wSpotsFilamentClosestDistancePointIndex[i] in wFilamentBranchPointIndex or wSpotsFilamentClosestDistancePointIndex[i] in wFilamentTerminalPointIndex:
                            #         wSpotsFilamentClosestDistancePointIndex[i]=wSpotsNearestIndex[0][2]
                            #     if wSpotsFilamentClosestDistancePointIndex[i] in wFilamentBranchPointIndex or wSpotsFilamentClosestDistancePointIndex[i] in wFilamentTerminalPointIndex:
                            #         wSpotsFilamentClosestDistancePointIndex[i]=wSpotsNearestIndex[0][3]
                            # elapsed = time.time() - start
                            # print(elapsed)
                            # progress_bar4['value'] = i/len(wSpotsFilamentClosestDistancePointIndex)*100 #  % out of 100
                            # master.update()
                        #loop for each spot within threshold
                        #append new filament and create list of new spots
                        for i in range (len(wSpotsAllIndexPerFilament)):
                            wNewFilamentsXYZ.append(vSpotsColocPositionsWorking[wSpotsAllIndexPerFilament[i]])
                            wNewFilamentsRadius.append(1)
                            wNewFilamentsEdges.append([wSpotsFilamentClosestDistancePointIndex[wSpotsAllIndexPerFilament[i]],len(vFilamentsRadius)+i])
                            wNewFilamentsTypes.append(1)

                        vNewFilament=vImarisApplication.GetFactory().CreateFilaments()
                        vNewFilament.AddFilament(wNewFilamentsXYZ, wNewFilamentsRadius, wNewFilamentsTypes, wNewFilamentsEdges, vFilamentsIndexT)
                        vNewFilament.SetBeginningVertexIndex(0, 0)

                #Grab New Filament Spine Statistics for attachment point distance.
                        vNewFilamentStatistics = vNewFilament.GetStatistics()
                        vNewFilamentStatNames = vNewFilamentStatistics.mNames
                        vNewFilamentStatValues = vNewFilamentStatistics.mValues
                        vNewFilamentStatIds = vNewFilamentStatistics.mIds
                        vNewFilamentSpineAttPtDistIndex=[i for i,val in enumerate(vNewFilamentStatNames)
                                                          if val==('Spine Attachment Pt Distance')]
                        vNewFilamentSpinePtPosXIndex=[i for i,val in enumerate(vNewFilamentStatNames)
                                                          if val==('Spine Terminal Pt Position X')]
                        if len(vNewFilamentSpineAttPtDistIndex)>1:
                            vNewFilamentSpineAttPtDist=list(itemgetter(*vNewFilamentSpineAttPtDistIndex)(vNewFilamentStatValues))
                            vNewFilamentSpinePtPosX=list(itemgetter(*vNewFilamentSpinePtPosXIndex)(vNewFilamentStatValues))
                            vNewFilamentStatIdsPosX=list(itemgetter(*vNewFilamentSpinePtPosXIndex)(vNewFilamentStatIds))
                            vNewFilamentStatIdsDist=list(itemgetter(*vNewFilamentSpineAttPtDistIndex)(vNewFilamentStatIds))
                        else:
                            vNewFilamentSpineAttPtDist=[x[1] for x in enumerate(vNewFilamentStatValues)
                                                    if x[0] in vNewFilamentSpineAttPtDistIndex]
                            vNewFilamentSpinePtPosX=[x[1] for x in enumerate(vNewFilamentStatValues)
                                                    if x[0] in vNewFilamentSpinePtPosXIndex]
                            vNewFilamentStatIdsDist=[x[1] for x in enumerate(vNewFilamentStatIds)
                                                    if x[0] in vNewFilamentSpineAttPtDistIndex]
                            vNewFilamentStatIdsPosX=[x[1] for x in enumerate(vNewFilamentStatIds)
                                                    if x[0] in vNewFilamentSpinePtPosXIndex]
                        #Collate all spots for each filament
                        for i in range (len(wSpotsAllIndexPerFilament)):
                            wCompleteSpotDistAlongFilamentStat.append(vNewFilamentSpineAttPtDist[vNewFilamentStatIdsDist.index(vNewFilamentStatIdsPosX[vNewFilamentSpinePtPosX.index(wNewSpotsOnFilament[i][0])])])
                            wCompleteSpotDistAlongFilamentStatWorking.append(vNewFilamentSpineAttPtDist[vNewFilamentStatIdsDist.index(vNewFilamentStatIdsPosX[vNewFilamentSpinePtPosX.index(wNewSpotsOnFilament[i][0])])])

                else:
                    vNewSpotsvNewSpotsAlongFilament = vImarisApplication.GetFactory().CreateSpots()
                    vNewSpotsvNewSpotsAlongFilament.SetName('NO Colocalization ' + str(vSpots.GetName())+ '-- FilamentId:' + str(vFilamentIds[vFilamentCountActual-1]))
                    vNewSpotsAnalysisFolder.AddChild(vNewSpotsvNewSpotsAlongFilament, -1)

            #################################################################################
                #Create a new Coloc Spots Object
                if len(wSpotsAllIndexPerFilament) != []:
                    vNewSpotsvNewSpotsAlongFilament = vImarisApplication.GetFactory().CreateSpots()
                    vNewSpotsvNewSpotsAlongFilament.SetName('Colocalized-'+ str(vSpots.GetName())+' -- FilamentId:' + str(vFilamentIds[vFilamentCountActual-1]))
                    vNewSpotsOnFilamentIndex=[vFilamentsIndexT]*len(wNewSpotsOnFilamentRadius)
                    zRandomColor=((random.uniform(0, 1)) * 256 * 256 * 256 )
                    vNewSpotsvNewSpotsAlongFilament.SetColorRGBA(zRandomColor)
                    vNewSpotsvNewSpotsAlongFilament.Set(wNewSpotsOnFilament, vNewSpotsOnFilamentIndex, [i[0] for i in wNewSpotsOnFilamentRadius])
                    vNewSpotsAnalysisFolder.AddChild(vNewSpotsvNewSpotsAlongFilament, -1)
                    vImarisApplication.GetSurpassScene().AddChild(vNewSpotsAnalysisFolder, -1);
        ############################################
                    ##ADD new Stat distance to starting points to new Spots objects
                    vNewSpotsOnFilamentIndex=[vFilamentsIndexT+1]*len(wSpotsAllIndexPerFilament)
                    vSpotsvIds=list(range(len(wSpotsAllIndexPerFilament)))
                    vSpotsStatUnits=['um']*len(wSpotsAllIndexPerFilament)
                    vSpotsStatFactors=(['Spot']*len(wSpotsAllIndexPerFilament), [str(x) for x in vNewSpotsOnFilamentIndex] )
                    vSpotsStatFactorName=['Category','Time']

                #Combine distance measure per filament (spine and dendrite)
                    if qIsSpines==True:
                        wCompleteFinalperFilament=np.column_stack((wCompleteShortestDistanceToFilament,wCompleteShortestDistanceToSpine))
                    else:
                        wCompleteFinalperFilament=wCompleteShortestDistanceToFilament
                    #Collate each Filament together for closest distance to all spots
                    if vFilamentCountActual==1:
                        wCompleteShortestDistanceToALLFilaments=wCompleteFinalperFilament
                    else:
                        wCompleteShortestDistanceToALLFilaments=np.column_stack((wCompleteShortestDistanceToALLFilaments,wCompleteFinalperFilament))


                    if len(wCompleteSpotDistAlongFilamentStatWorking) == 0:
                        #find shortest distance for Coloc spots to Dendrite
                        # if SegmentCountALL>1:
                        #     # vColocSpotToFilamentDistanceOnly = wCompleteFinalperFilament.min(axis=1)[wCompleteFinalperFilament.min(axis=1) <= vOptionFilamentSpotThreshold].tolist()
                        #     vColocSpotToFilamentDistanceOnly=wCompleteFinalperFilament.min(axis=1)[wSpotsAllIndexPerFilament].tolist()

                        # else:
                        #     vColocSpotToFilamentDistanceOnly = wCompleteFinalperFilament[wCompleteFinalperFilament<=vOptionFilamentSpotThreshold].tolist()
                        #     vColocSpotToFilamentDistanceOnly=wCompleteFinalperFilament.min(axis=1)[wSpotsAllIndexPerFilament].tolist()
                        vColocSpotToFilamentDistanceOnly=wCompleteFinalperFilament.min(axis=1)[wSpotsAllIndexPerFilament].tolist()


                        vSpotsStatNames=[' Shortest Distance to Filament']*len(wSpotsAllIndexPerFilament)
                        vNewSpotsvNewSpotsAlongFilament.AddStatistics(vSpotsStatNames, vColocSpotToFilamentDistanceOnly,
                                                      vSpotsStatUnits, vSpotsStatFactors,
                                                      vSpotsStatFactorName, vSpotsvIds)
                    else:
                        vSpotsStatNames=[' Distance to Starting Point']*len(wSpotsAllIndexPerFilament)
                        vColocSpotToFilamentDistanceOnly=wCompleteFinalperFilament.min(axis=1)[wSpotsAllIndexPerFilament].tolist()

                        vNewSpotsvNewSpotsAlongFilament.AddStatistics(vSpotsStatNames, wCompleteSpotDistAlongFilamentStatWorking,
                                                  vSpotsStatUnits, vSpotsStatFactors, vSpotsStatFactorName, vSpotsvIds)
                        # if SegmentCountALL>1:
                        #     vColocSpotToFilamentDistanceOnly = wCompleteFinalperFilament.min(axis=1)[wCompleteFinalperFilament.min(axis=1) <= vOptionFilamentSpotThreshold].tolist()
                        # else:
                        #     vColocSpotToFilamentDistanceOnly = wCompleteFinalperFilament[wCompleteFinalperFilament<=vOptionFilamentSpotThreshold].tolist()
                        vSpotsStatNames=[' Shortest Distance to Filament']*len(vColocSpotToFilamentDistanceOnly)
                        vNewSpotsvNewSpotsAlongFilament.AddStatistics(vSpotsStatNames, vColocSpotToFilamentDistanceOnly,
                                                      vSpotsStatUnits, vSpotsStatFactors,
                                                      vSpotsStatFactorName, vSpotsvIds)
                        # if scount>1:
                        #     vColocSpotToSpineDistanceOnly = wCompleteShortestDistanceToSpine.min(axis=1)[wCompleteShortestDistanceToSpine.min(axis=1) <= vOptionFilamentSpotThreshold].tolist()
                        # else:
                        #     vColocSpotToSpineDistanceOnly = wCompleteShortestDistanceToSpine[wCompleteShortestDistanceToSpine<=vOptionFilamentSpotThreshold].tolist()
                        # vSpotsStatNames=[' Shortest Distance to Spine']*len(wSpotsAllIndexPerFilament)
                        # vNewSpotsvNewSpotsAlongFilament.AddStatistics(vSpotsStatNames, vColocSpotToSpineDistanceOnly,
                        #                               vSpotsStatUnits, vSpotsStatFactors,
                        #                               vSpotsStatFactorName, vSpotsvIds)

                wSpotsAllIndexPerFilament=[]
                wNewSpotsOnFilamentRadius=[]
                wNewSpotsOnFilament=[]

        ###############################################################################
        ###############################################################################
        #After Each Filament collate spots to Display
        # Convert the Filament points into Spots
            if vOptionFilamentToSpots==1:# and vOptionFilamentToSpotsMerge==0:
                vNewSpotsDendrites = vImarisApplication.GetFactory().CreateSpots()
                vNewSpotsSpines = vImarisApplication.GetFactory().CreateSpots()

                for c  in range (2): #loop twice for each filamant, 0=dendrite 1=spine, and generate a
                    if vOptionFilamentToSpotsFill==0:
                        #find index for dendrites and spines
                        vTypeIndex=[i for i,val in enumerate(vTypes) if val==c]
                       #Grab all type object from Filament object
                        vSegmentPositionsWorking=[vFilamentsXYZ[i] for i in vTypeIndex]
                        vSegmentRadiusWorking=[vFilamentsRadius[i] for i in vTypeIndex]
                        vDendritevTypesWorking=[vTypes[i] for i in vTypeIndex]
                        vTimeIndex=[vFilamentsIndexT]*len(vSegmentRadiusWorking)
                    else:#Use Filled spots for display
                        vTypeIndex=[i for i,val in enumerate(vAllSegmentsTypesPerFilamentWorkingInserts) if val==c]
                    #Grab all type object from Filament object
                        vSegmentPositionsWorking=[vAllSegmentsPerFilamentPositionsWorkingInserts[i] for i in vTypeIndex]
                        vSegmentRadiusWorking=[vAllSegmentsPerFilamentRadiusWorkingInserts[i] for i in vTypeIndex]
                        vDendritevTypesWorking=[vAllSegmentsTypesPerFilamentWorkingInserts[i] for i in vTypeIndex]
                        vTimeIndex=[vFilamentsIndexT]*len(vSegmentRadiusWorking)

                    #Collate all filaments into one
                    if vOptionFilamentToSpotsMerge==1:
                        vTotalSpotsDendrite.extend(vSegmentPositionsWorking)
                        vTotalSpotsDendriteRadius.extend(vSegmentRadiusWorking)
                        vTotalSpotsDendriteTime.extend(vTimeIndex)
                        if c==1 and vSegmentPositionsWorking != []:
                            qSpinesPresent=True
                            vTotalSpotsSpine.extend(vSegmentPositionsWorking)
                            vTotalSpotsSpineRadius.extend(vSegmentRadiusWorking)
                            vTotalSpotsSpineTime.extend(vTimeIndex)

                    if vOptionFilamentToSpotsMerge==0:
                        if c==0: #Do first look for dendrites
                            vNewSpotsDendrites.Set(vSegmentPositionsWorking, vTimeIndex, vSegmentRadiusWorking)
                            zRandomColor=((random.uniform(0, 1)) * 256 * 256 * 256 )
                            vNewSpotsDendrites.SetColorRGBA(zRandomColor)
                            vNewSpotsDendrites.SetName(str(vFilaments.GetName())+" dendrite_ID:"+ str(vFilamentIds[vFilamentCountActual-1]))
                            #Add new surface to Surpass Scene
                            vNewSpotsDendrites.SetVisible(0)
                            vNewSpotsDendritesFolder.AddChild(vNewSpotsDendrites, -1)
                        else:
                            if qIsSpines==True:#test second loop if spines exist, if not do not make spine spots object
                                vNewSpotsSpines.Set(vSegmentPositionsWorking, vTimeIndex, vSegmentRadiusWorking)
                                zRandomColor=((random.uniform(0, 1)) * 256 * 256 * 256 )
                                vNewSpotsSpines.SetColorRGBA(zRandomColor)
                                vNewSpotsSpines.SetName(str(vFilaments.GetName())+" Spine_ID:"+ str(vFilamentIds[vFilamentCountActual-1]))
                                vNewSpotsSpines.SetVisible(0)
                                vNewSpotsSpinesFolder.AddChild(vNewSpotsSpines, -1)

                        #After the last Spot creation Place the folders
                        if aFilamentIndex+1==vNumberOfFilaments:
                            vImarisApplication.GetSurpassScene().AddChild(vNewSpotsDendritesFolder, -1)
                            if qIsSpines == True:
                                vImarisApplication.GetSurpassScene().AddChild(vNewSpotsSpinesFolder, -1)

        ###############################################################################
        ###############################################################################
            #After each filament
            #Find overall Filament Intensity from SPots vNewSpotsDendrites
            if vOptionIntensity==1:
                vNewSpotsDendrites = vImarisApplication.GetFactory().CreateSpots()
                vTimeIndex=[vFilamentsIndexT]*len(vAllSegmentsPerFilamentRadiusWorkingInserts)
                vNewSpotsDendrites.Set(vAllSegmentsPerFilamentPositionsWorkingInserts, vTimeIndex, vAllSegmentsPerFilamentRadiusWorkingInserts)
                vNewSpotsFilamentStatistics = vNewSpotsDendrites.GetStatistics()
                vNewSpotsFilamentStatNames = vNewSpotsFilamentStatistics.mNames
                vNewSpotsFilamentStatValues = vNewSpotsFilamentStatistics.mValues
                vNewSpotsFilamentIndexCenter=[i for i,val in enumerate(vNewSpotsFilamentStatNames)
                                                  if val==('Intensity Mean')]
                vNewSpotsFilamentIndexMean=[i for i,val in enumerate(vNewSpotsFilamentStatNames)
                                                  if val==('Intensity Center')]
                vNewSpotsIntensityMean=list(itemgetter(*vNewSpotsFilamentIndexMean)(vNewSpotsFilamentStatValues))
                vNewSpotsIntensityCenter=list(itemgetter(*vNewSpotsFilamentIndexCenter)(vNewSpotsFilamentStatValues))

        #Spilt Intensity by channels and calculate average
                if vSizeC>1:
                    for c in range (vSizeC):
                        wNumber1=int( c*len(vNewSpotsFilamentIndexMean)/vSizeC)
                        wNumber2=int(len(vNewSpotsFilamentIndexMean)/vSizeC+len(vNewSpotsFilamentIndexMean)/vSizeC*c)
                        wFilamentIntensityCenter.append(mean(vNewSpotsIntensityCenter[wNumber1:wNumber2]))
                        wFilamentIntensityMean.append(mean(vNewSpotsIntensityMean[wNumber1:wNumber2]))
                else:
                    wFilamentIntensityCenter.append(mean(vNewSpotsIntensityCenter[0:len(vNewSpotsFilamentIndexMean)]))
                    wFilamentIntensityMean.append(mean(vNewSpotsIntensityMean[0:len(vNewSpotsFilamentIndexMean)]))

        ###############################################################################
        ###############################################################################
        #After Each Filament collate SegmentIds fro dendrites and spines
            wCompleteDendriteSegmentIds.extend(wDendriteSegmentIds)
            wCompleteSpineSegmentIds.extend(wSpineSegmentIds)
            wCompleteFilamentTimeIndex.extend([vFilamentsIndexT+1]*vFilamentCountActual)
            wCompleteDendriteTimeIndex.extend([vFilamentsIndexT+1]*len(wDendriteSegmentIds))
            wCompleteSpineTimeIndex.extend([vFilamentsIndexT+1]*len(wSpineSegmentIds))

        ###############################################################################
        ###############################################################################
            progress_bar2['value'] = int((aFilamentIndex+1)/vNumberOfFilaments*100) #  % out of 100
            master.update()
        master.destroy()
        master.mainloop()
        ###############################################################################
        ###############################################################################
        #After last Filament in Bouton Statistics
        #create new Bouton spot object and Filament Statistic
        if vOptionFilamentBoutonDetection==1:
            if vAllNewSpotsBoutonsRadius==[]:
                vNewSpotsBoutons.SetName(' NO Boutons Found')
                vNewSpotsBoutonsTimeIndex=[vFilamentsIndexT]*len(vBoutonRadiusAll)
                vNewSpotsBoutons.Set(vBoutonPositionAll, vNewSpotsBoutonsTimeIndex, vBoutonRadiusAll)
                vNewSpotsAnalysisFolder.AddChild(vNewSpotsBoutons, -1)
            else:
                vNewSpotsBoutonsTimeIndex=[vFilamentsIndexT]*len(vBoutonRadiusAll)
                vNewSpotsBoutons.SetName('Detected Varicosities (Boutons)')
                vNewSpotsBoutons.SetColorRGBA(18000)
                vNewSpotsBoutons.Set(vBoutonPositionAll, vNewSpotsBoutonsTimeIndex, vBoutonRadiusAll)
                vNewSpotsAnalysisFolder.AddChild(vNewSpotsBoutons, -1)

                # #ADD Spot to Filament Distance statistic.
                # vSpotsvIds=list(range(len(vBoutonRadiusAll)))
                # vSpotsStatUnits=['um']*len(vBoutonRadiusAll)
                # vSpotsStatFactors=(['Spot']*len(vBoutonRadiusAll),
                #                       ['1']*(len(vBoutonRadiusAll)))
                # vSpotsStatFactorName=['Category','Time']
                # vSpotsStatNames=[' Distance to StartingPoint']*len(vBoutonRadiusAll)
                # vNewSpotsBoutons.AddStatistics(vSpotsStatNames, list(itertools.chain(*wCompleteBoutonDistAlongFilamentStat)),
                #                               vSpotsStatUnits, vSpotsStatFactors,
                #                               vSpotsStatFactorName, vSpotsvIds)

        ###############################################################################
            #Add Filament Bouton Statistics

            vFilamentStatvIds=list(range(len(vAllFilamentDendriteLength)))
            vFilamentStatUnits=['']*(len(vAllFilamentDendriteLength))
            vFilamentStatFactors=(['Dendrite']*len(vAllFilamentDendriteLength), [str(x) for x in wCompleteDendriteTimeIndex] )
            vFilamentStatFactorName=['Category','Time']
        #######################
            vFilamentStatNames=[' Dendrite Bouton Number']*(len(vAllFilamentDendriteLength))
            vFilaments.AddStatistics(vFilamentStatNames, vStatisticFilamentBoutonsPerDendrite,
                                  vFilamentStatUnits, vFilamentStatFactors,
                                  vFilamentStatFactorName, wCompleteDendriteSegmentIds)
        #######################
            vFilamentStatUnits=['']*(len(vAllFilamentDendriteLength))
            vNewStatBoutonDensityPerSegment=[vStatisticFilamentBoutonsPerDendrite[i] / vAllFilamentDendriteLength[i] for i in range(len(vAllFilamentDendriteLength))]
            vFilamentStatNames=[' Dendrite Bouton Density (per um)']*(len(vNewStatBoutonDensityPerSegment))
            vFilaments.AddStatistics(vFilamentStatNames, vNewStatBoutonDensityPerSegment,
                                  vFilamentStatUnits, vFilamentStatFactors,
                                  vFilamentStatFactorName, wCompleteDendriteSegmentIds)

        ###############################################################################
        if vOptionDendriteToDendriteContact==1:
            vFilamentStatvIds=list(range(len(vAllFilamentDendriteLength)))
            vFilamentStatUnits=['']*(len(vAllFilamentDendriteLength))
            vFilamentStatFactors=(['Dendrite']*len(vAllFilamentDendriteLength), [str(x) for x in wCompleteDendriteTimeIndex] )
            vFilamentStatFactorName=['Category','Time']
        #######################
            vFilamentStatNames=[' Dendrite-Dendrite Contacts']*(len(vAllFilamentDendriteLength))
            vFilaments.AddStatistics(vFilamentStatNames, vStatisticFilamentDendriteDendriteContacts,
                                  vFilamentStatUnits, vFilamentStatFactors,
                                  vFilamentStatFactorName, wCompleteDendriteSegmentIds)
        ###############################################################################
        if vOptionFilamentToFilamentContact==1:
            vFilamentStatvIds=list(range(len(vAllFilamentDendriteLength)))
            vFilamentStatUnits=['']*(len(vAllFilamentDendriteLength))
            vFilamentStatFactors=(['Dendrite']*len(vAllFilamentDendriteLength), [str(x) for x in wCompleteDendriteTimeIndex] )
            vFilamentStatFactorName=['Category','Time']
        #######################
            vFilamentStatNames=[' Filament-Filament Coloc Contacts']*(len(vAllFilamentDendriteLength))
            vFilaments.AddStatistics(vFilamentStatNames, vStatisticFilamentDendriteDendriteContactsColoc,
                                  vFilamentStatUnits, vFilamentStatFactors,
                                  vFilamentStatFactorName, wCompleteDendriteSegmentIds)


        #######################
            # vFilamentStatUnits=['']*(len(vAllFilamentDendriteLength))
            # vNewStatContactDensityPerSegment=[vStatisticFilamentDendriteDendriteContacts[i] / vAllFilamentDendriteLength[i] for i in range(len(vAllFilamentDendriteLength))]
            # vFilamentStatNames=[' Dendrite Contact Density (per um)']*(len(vNewStatContactDensityPerSegment))
            # vFilaments.AddStatistics(vFilamentStatNames, vNewStatContactDensityPerSegment,
            #                       vFilamentStatUnits, vFilamentStatFactors,
            #                       vFilamentStatFactorName, wCompleteDendriteSegmentIds)

        ###############################################################################
        ###############################################################################
        #After last Filament in Scene generate intensity statistics
        if vOptionIntensity==1:
        #Reorder reshape intensity stats
            wCompleteDendriteBranchIntCenter = [[] for _ in range(vSizeC)]
            for index, item in enumerate(vStatisticDendriteBranchIntCenter):
                wCompleteDendriteBranchIntCenter[index % vSizeC].append(item)
            wCompleteDendriteBranchIntMean = [[] for _ in range(vSizeC)]
            for index, item in enumerate(vStatisticDendriteBranchIntMean):
                wCompleteDendriteBranchIntMean[index % vSizeC].append(item)

            if qIsSpines==True:
                wCompleteSpineBranchIntCenter = [[] for _ in range(vSizeC)]
                for index, item in enumerate(vStatisticSpineBranchIntCenter):
                    wCompleteSpineBranchIntCenter[index % vSizeC].append(item)
                wCompleteSpineBranchIntMean = [[] for _ in range(vSizeC)]
                for index, item in enumerate(vStatisticSpineBranchIntMean):
                    wCompleteSpineBranchIntMean[index % vSizeC].append(item)


        #######################
        #Test if the first value is equal to 0.0001 the fixed value if the first dendrite
        #has no intensity spots.
            if any(0.0001 in x for x in wCompleteDendriteBranchIntMean)==True:
                x=1
            if any(0.0001 in x for x in wCompleteSpineBranchIntMean)==True:
                x=1
        ########################
            vFilamentStatvIds=list(range(len(wCompleteDendriteSegmentIds)))
            vFilamentStatUnits=['']*(len(wCompleteDendriteSegmentIds))
            vFilamentStatFactors=(['Dendrite']*len(wCompleteDendriteSegmentIds), [str(x) for x in wCompleteDendriteTimeIndex] )

            vFilamentStatFactorName=['Category','Time']
        #######################
            for c in range (vSizeC):
                vFilamentStatNames=[' Dendrite Intensity Mean ch' + str(c+1)]*(len(wCompleteDendriteSegmentIds))
                vFilaments.AddStatistics(vFilamentStatNames, wCompleteDendriteBranchIntMean[c],
                                      vFilamentStatUnits, vFilamentStatFactors,
                                      vFilamentStatFactorName, wCompleteDendriteSegmentIds)
                #######################
                vFilamentStatNames=[' Dendrite Intensity Center ch' + str(c+1)]*(len(wCompleteDendriteSegmentIds))
                vFilaments.AddStatistics(vFilamentStatNames, wCompleteDendriteBranchIntCenter[c],
                                      vFilamentStatUnits, vFilamentStatFactors,
                                      vFilamentStatFactorName, wCompleteDendriteSegmentIds)
            if wSpineSegmentIds!=[]:
                vSpineStatvIds=list(range(len(wCompleteSpineSegmentIds)))
                vSpineStatUnits=['']*(len(wCompleteSpineSegmentIds))
                vSpineStatFactors=(['Spine']*len(wCompleteSpineSegmentIds), [str(x) for x in wCompleteSpineTimeIndex] )

                vSpineStatFactorName=['Category','Time']
                for c in range (vSizeC):
                    vFilamentStatNames=[' Spine Intensity Mean ch' + str(c+1)]*(len(wCompleteSpineSegmentIds))
                    vFilaments.AddStatistics(vFilamentStatNames, wCompleteSpineBranchIntMean[c],
                                          vSpineStatUnits, vSpineStatFactors,
                                          vSpineStatFactorName, wCompleteSpineSegmentIds)
                    #######################
                    vFilamentStatNames=[' Spine Intensity Center Mean ch' + str (c+1)]*(len(wCompleteSpineSegmentIds))
                    vFilaments.AddStatistics(vFilamentStatNames, wCompleteSpineBranchIntCenter[c],
                                          vSpineStatUnits, vSpineStatFactors,
                                          vFilamentStatFactorName, wCompleteSpineSegmentIds)

        ###############################################################################
        ###############################################################################
        #After last Filament - Processing end of Filament to Spots Merge
        if vOptionFilamentToSpots==1 and vOptionFilamentToSpotsMerge==1:
            vNewSpotsDendrites = vImarisApplication.GetFactory().CreateSpots()
            vNewSpotsDendrites.Set(vTotalSpotsDendrite, vTotalSpotsDendriteTime, vTotalSpotsDendriteRadius)
            vNewSpotsDendrites.SetName(str(vFilaments.GetName())+" All Dendrites")
            #Add new surface to Surpass Scene
            vNewSpotsDendritesFolder.AddChild(vNewSpotsDendrites, -1)
            vImarisApplication.GetSurpassScene().AddChild(vNewSpotsDendritesFolder, -1)
            if qSpinesPresent==True:
                vNewSpotsSpines = vImarisApplication.GetFactory().CreateSpots()
                vNewSpotsSpines.Set(vTotalSpotsSpine, vTotalSpotsSpineTime, vTotalSpotsSpineRadius)
                vNewSpotsSpines.SetName(str(vFilaments.GetName())+" All Spines")
                 #Add new surface to Surpass Scene
                vNewSpotsSpinesFolder.AddChild(vNewSpotsSpines, -1)
                vImarisApplication.GetSurpassScene().AddChild(vNewSpotsSpinesFolder, -1)
        ###############################################################################
        ###############################################################################
        #After the last Filament - Spot to fIlament Stats
        if vOptionFilamentCloseToSpots==1:
            #ADD Spot to Filament Distance statistic.
            vSpotsStatUnits=['um']*len(vSpotsColocRadius)
            vSpotsStatFactors=(['Spot']*len(vSpotsColocRadius), [str(x) for x in [i+1 for i in vSpotsColocTimeIndices]] )
            vSpotsStatFactorName=['Category','Time']
            vSpotsStatNames=[' Shortest Distance to Filament']*len(vSpotsColocRadius)
            vSpots.SetName(vSpots.GetName()+' -- Analyzed')

            wCompleteShortestDistanceStat=[]
            # Get the minimum values of each column i.e. along axis 0
            if SegmentCountALL>1:
                wCompleteShortestDistanceStat = np.amin(wCompleteShortestDistanceToALLFilaments, axis=1).tolist()
            else:
                wCompleteShortestDistanceStat=wCompleteShortestDistanceToALLFilaments.tolist()
            vSpots.AddStatistics(vSpotsStatNames, wCompleteShortestDistanceStat,
                                          vSpotsStatUnits, vSpotsStatFactors,
                                          vSpotsStatFactorName, vSpotsId)

        ###########
            #ADD Spot number&Density to Filament Distance statistic.
            vFilamentStatvIds=list(range(len(wCompleteDendriteSegmentIds)))
            vFilamentStatUnits=['']*(len(wCompleteDendriteSegmentIds))
            vFilamentStatFactors=(['Dendrite']*len(wCompleteDendriteSegmentIds), [str(x) for x in wCompleteDendriteTimeIndex] )
            vFilamentStatFactorName=['Category','Time']
            vFilamentStatNames=[' Dendrite Coloc Number Spots']*(len(wCompleteDendriteSegmentIds))
            vFilaments.AddStatistics(vFilamentStatNames, wNumberOfSpotsPerDendrite,
                                          vFilamentStatUnits, vFilamentStatFactors,
                                          vFilamentStatFactorName, wCompleteDendriteSegmentIds)

            vNewStatSpotColocDensityPerDendrite=[(wNumberOfSpotsPerDendrite[i]*10) / vAllFilamentDendriteLength[i] for i in range(len(vAllFilamentDendriteLength))]
            vFilamentStatNames=[' Dendrite Coloc Spot Density (per 10um)']*(len(wCompleteDendriteSegmentIds))
            vFilaments.AddStatistics(vFilamentStatNames, vAllColocDensityPerDendrite,
                                          vFilamentStatUnits, vFilamentStatFactors,
                                          vFilamentStatFactorName, wCompleteDendriteSegmentIds)
            #Spine Stat
            if wNumberOfSpotsPerSpine!=[]:
                vFilamentStatvIds=list(range(len(wCompleteSpineSegmentIds)))
                vFilamentStatUnits=['']*(len(wCompleteSpineSegmentIds))
                vFilamentStatFactorName=['Category','Time']
                vFilamentStatFactors=(['Spine']*len(wCompleteSpineSegmentIds), [str(x) for x in wCompleteSpineTimeIndex] )
                vFilamentStatNames=[' Spine Coloc Number Spots']*len(wCompleteSpineSegmentIds)
                vFilaments.AddStatistics(vFilamentStatNames, wNumberOfSpotsPerSpine,
                                          vFilamentStatUnits, vFilamentStatFactors,
                                          vFilamentStatFactorName, wCompleteSpineSegmentIds)
        ###############################################################################
        ###############################################################################
        #Produce Report the Filament level stats
        vFilamentStatUnits=['']*vFilamentCountActual
        vFilamentStatFactors=(['Filament']*vFilamentCountActual, [str(x) for x in wCompleteFilamentTimeIndex] )
        vFilamentStatFactorName=['Category','Time']

        if vOptionIntensity==1:
            #Reshape reorder filament Intensity stats
            wCompleteFilamentIntCenter = [[] for _ in range(vSizeC)]
            for index, item in enumerate(wFilamentIntensityCenter):
                wCompleteFilamentIntCenter[index % vSizeC].append(item)
            wCompleteFilamentIntMean = [[] for _ in range(vSizeC)]
            for index, item in enumerate(wFilamentIntensityMean):
                wCompleteFilamentIntMean[index % vSizeC].append(item)
            for c in range (vSizeC):
                vFilamentStatNames=[' Filament IntensityMean ch' + str(c+1)]*vFilamentCountActual
                vFilaments.AddStatistics(vFilamentStatNames, wCompleteFilamentIntMean[c],
                                          vFilamentStatUnits, vFilamentStatFactors,
                                          vFilamentStatFactorName, vFilamentIds)
                vFilamentStatNames=[' Filament IntensityCenter ch' + str(c+1)]*vFilamentCountActual
                vFilaments.AddStatistics(vFilamentStatNames, wCompleteFilamentIntCenter[c],
                                          vFilamentStatUnits, vFilamentStatFactors,
                                          vFilamentStatFactorName, vFilamentIds)
        if vOptionFilamentBoutonDetection==1:
            vFilamentStatNames=[' Filament Number Boutons']*vFilamentCountActual
            vFilaments.AddStatistics(vFilamentStatNames, wCompleteFilamentNumberBoutons,
                                      vFilamentStatUnits, vFilamentStatFactors,
                                      vFilamentStatFactorName, vFilamentIds)
        if vOptionFilamentCloseToSpots==1:
            vFilamentStatNames=[' Filament Number Coloc Spots']*vFilamentCountActual
            vFilaments.AddStatistics(vFilamentStatNames, wCompleteNumberSpotsPerFilament,
                                      vFilamentStatUnits, vFilamentStatFactors,
                                      vFilamentStatFactorName, vFilamentIds)
            if qIsSpines==True:
                vFilamentStatNames=[' Filament Number Coloc Spots on Spines']*vFilamentCountActual
                vFilaments.AddStatistics(vFilamentStatNames, wCompleteNumberSpotsonSpinePerFilament,
                                          vFilamentStatUnits, vFilamentStatFactors,
                                          vFilamentStatFactorName, vFilamentIds)
                vFilamentStatNames=[' Filament Number Coloc Spots on Dendrites']*vFilamentCountActual
                vFilaments.AddStatistics(vFilamentStatNames, wCompleteNumberSpotsonDendritePerFilament,
                                         vFilamentStatUnits, vFilamentStatFactors,
                                         vFilamentStatFactorName, vFilamentIds)

        if vOptionDendriteToDendriteContact==1:
            vFilamentStatNames=[' Filament Number Dendrite-Dendrite Contacts']*vFilamentCountActual
            vFilaments.AddStatistics(vFilamentStatNames, xCompleteNumberofContactsperFilament,
                                      vFilamentStatUnits, vFilamentStatFactors,
                                      vFilamentStatFactorName, vFilamentIds)
        if vOptionFilamentToFilamentContact==1:
            vFilamentStatNames=[' Filament Number FilamentColoc Contacts']*vFilamentCountActual
            vFilaments.AddStatistics(vFilamentStatNames, xCompleteNumberofContactsperFilamentColoc,
                                      vFilamentStatUnits, vFilamentStatFactors,
                                      vFilamentStatFactorName, vFilamentIds)
        ###################################################################################
        ###################################################################################
        #Apply SpotAnalysis folder to Surpass scene
        if vOptionFilamentCloseToSpots==1 or vOptionFilamentBoutonDetection==1:
            vImarisApplication.GetSurpassScene().AddChild(vNewSpotsAnalysisFolder, -1)

        if vOptionFilamentBoutonDetection==1 or vOptionFilamentCloseToSpots==1 or vOptionIntensity==1:
            vFilaments.SetName(vFilaments.GetName()+' -- Analyzed')
            vImarisApplication.GetSurpassScene().AddChild(vFilaments, -1)

        if vOptionFilamentCloseToSpots==1:
            vSpots.SetVisible(0)

        # # #Adjust Visibility
        # if vOptionFilamentToSpots==1 and vOptionFilamentCloseToSpots==1 or vOptionFilamentBoutonDetection==1:
        #     vNewSpotsDendritesFolder.SetVisible(0)
        #     vNewSpotsSpinesFolder.SetVisible(0)

        if vNumberOfFilaments>50 and qisVisible=='yes':
            vImarisApplication.SetVisible(1)

    except:
        vImarisApplication.SetVisible(1)



