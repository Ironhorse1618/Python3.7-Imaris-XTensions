# Filament Analysis
#
# Written by Matthew J. Gastinger
#
# JUne 2023 - Imaris 10.
#
#
    #<CustomTools>
        #<Menu>
            #<Submenu name="Filaments Functions">
                #<Item name="Filament Analysis39" icon="Python3">
                    #<Command>Python3XT::XT_MJG_Filament_Analysis39(%i)</Command>
                #</Item>
            #</Submenu>
       #</Menu>
       #<SurpassTab>
           #<SurpassComponent name="bpFilaments">
               #<Item name="Filament Analysis39" icon="Python3">
                   #<Command>Python3XT::XT_MJG_Filament_Analysis39(%i)</Command>
               #</SurpassComponent>
           #</SurpassTab>
    #</CustomTools>

  # Description:
  #     This XTension will do several things:
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
  #           Bouton(varicosity) number per dendrite segment
  #           Bouton density
  #           Spot Colocalization within a certain distance of filament
  #           Spot Coloc Density per dendrite segment
  #     7)Display Filament as a population of Spots
  #           Visualize diameter/intensity along segments
  #     8)Regularity Index Per Filament
  #           based on the average nearest neighbor (NN) distance between
  #           branch points, termination points or input points of a given
  #           dendritic tree to random disdribution in convex hull space
  #           ---As R approaches "1" points are closer to a random (Poisson) distribution (as the values of rExperimental and rRandom are more similar).
  #           ---As R approaches "0" corresponds to dendrites with more clustering (rExperimental < rRandom).
  #           ---As R greater than '1", nearest neighbors are further apart than it would be expected for a random distribution (rExperimental > rRandom).
  #     9)New Tortuosity statistic per dendrite segment
  #           measures the angle between adjacent points along the segment
  #             --The sum of angles divided the number of points * pi
  #             --better measure for the waviness of segment
#       10) Filament - Dendrite Complexity Index (DCI)
#              --- DCI = (Sum Terminal branch tip brnach depth + Number Terminaal branches) * (Total Filament length(um)/Total Number of primary dendrites)
#              --- Pillai et al. (2012). PLoS ONE 7(6): e38971. doi:10.1371/journal.pone.0038971
#              ---

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
import math
import os
import platform
# GUI imports
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
#import matplotlib.pyplot as plt
from scipy.signal import find_peaks, peak_prominences
from scipy.signal import peak_widths
from scipy.spatial.distance import cdist
from scipy.spatial.distance import pdist
from scipy.spatial import Delaunay
from scipy.spatial import ConvexHull

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
def XT_MJG_Filament_Analysis39(aImarisId):
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
    
    vOptionMergePoints=1
    
    
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
    
    #Dialog window
    ############################################################################
    window = tk.Tk()
    window.title('Filament Analysis')
    window.geometry('410x580')
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
        global vOptionFilamentToSpots,vOptionFilamentToSpotsMerge,vOptionBoutonThreshold, vOptionBoutonHeight, vOptionSomaThreshold,vOptionSomaThresholdValue
        global vOptionFilamentBoutonDetection, vOptionFilamentBoutoDetecionThreshold, vOptionFilamentCloseToSpots, vOptionFilamentToSpotsFill
        global vOptionBranchPoints,vOptionTerminalPoints, vOptionConvexHull, vOptionMergePoints, vOptionConvexHullwithTerminal
        global vOptionFilamentSpotThreshold, vOptionDendriteToDendriteContact, vOptionFilamentToFilamentContact, NamesSpots, NamesSurfaces, NamesFilaments
        # if (var2.get() == 0) and (var4.get() == 0) and (var5.get() ==0) and (var7.get() ==0) and (var8.get()==0):
        #     messagebox.showerror(title='Filament Analysis menu',
        #                      message='Please Select ONE Analysis')
        #     window.mainloop()
    
        vOptionFilamentToSpots=var2.get()
        vOptionFilamentToSpotsMerge=var3.get()
        vOptionFilamentToSpotsFill=1#var6.get()
        vOptionFilamentBoutonDetection=var4.get()
        vOptionDendriteToDendriteContact=var7.get()
        vOptionFilamentCloseToSpots=var5.get()
        vOptionFilamentSpotThreshold=[float(Entry2.get())]
        vOptionFilamentToFilamentContact=var8.get()
        vOptionSomaThreshold=var9.get()
        vOptionBranchPoints=var10.get()
        vOptionTerminalPoints=var11.get()
        vOptionConvexHull=var12.get()
        vOptionMergePoints= var101.get()
        vOptionConvexHullwithTerminal=var122.get()
    
    
    
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
            vOptionBoutonThreshold=15
            vOptionBoutonHeight=.4
        elif (var4.get() == 1) and (var4High.get() == 1):
            vOptionBoutonThreshold=5
            vOptionBoutonHeight=.25
        if (var2.get() == 0) and (var3.get() == 1):
            vOptionFilamentToSpots=1
        window.destroy()
    
    var2 = tk.IntVar(value=0)#Export Filament as a Spots object
    var3 = tk.IntVar(value=0)#Filament as spotd-- merge
    var4 = tk.IntVar(value=0)#Detect Boutons (varicosities)
    var5 = tk.IntVar(value=0)#Find Spots Close to Filaments
    var6 = tk.IntVar(value=0)#fill spots
    var7 = tk.IntVar(value=0)#dendrite dendrite contact
    var8 = tk.IntVar(value=0)#Filament filament contact
    var9 = tk.IntVar(value=0)#soma filter
    var10 = tk.IntVar(value=0)#Branch points
    var11 = tk.IntVar(value=0)#Terminal points
    var12 = tk.IntVar(value=0)#ConvexHull
    var101 = tk.IntVar(value=1)#Merge points
    var122 = tk.IntVar(value=0)#Use terminal points(starting point) for convex hull
    
    var4Low=tk.IntVar(value=0)#bouton sensitivity
    var4Med=tk.IntVar(value=1)#bouton sensitivity
    var4High=tk.IntVar(value=0)#bouton sensitivity
    
    tk.Label(window, font="bold", text='Choose Analysis Options!').grid(row=0,column=0, padx=75,sticky=W)
    
    tk.Checkbutton(window, text='Export Filament as a Spots object',
                    variable=var2, onvalue=1, offvalue=0).grid(row=2, column=0, padx=40,sticky=W)
    # tk.Checkbutton(window, text='Fill Spots',
    #                 variable=var6, onvalue=1, offvalue=0).grid(row=4, column=0, padx=80,sticky=W)
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
    
    tk.Label(window, text='____________________________________').grid(row=9, column=0,sticky=W)
    
    tk.Checkbutton(window, text='Find Intra-Dendrite Contacts',
                    variable=var7, onvalue=1, offvalue=0).grid(row=10, column=0, padx=40,sticky=W)
    
    Entry3=Entry(window,justify='center',width=8)
    Entry3.grid(row=11, column=0, padx=300, sticky=W)
    Entry3.insert(0, '10')
    tk.Label(window, text='um').grid(row=11,column=0, padx=350, sticky=W)
    tk.Checkbutton(window, text='Remove Contacts near Starting Point',
                    variable=var9, onvalue=1, offvalue=0).grid(row=11, column=0, padx=65,sticky=W)
    
    
    tk.Checkbutton(window, text='Find Filament-Filament Contacts',
                    variable=var8, onvalue=1, offvalue=0).grid(row=12, column=0, padx=40,sticky=W)
    
    tk.Label(window, text='____________________________________').grid(row=13, column=0,sticky=W)
    
    tk.Checkbutton(window, text='Create Branch Spots',
                   variable=var10, onvalue=1, offvalue=0).grid(row=14, column=0, padx=10,sticky=W)
    tk.Checkbutton(window, text='Merge Spots',
                   variable=var101, onvalue=1, offvalue=0).grid(row=14, column=0, padx=175,sticky=W)
    
    
    
    tk.Checkbutton(window, text='Create Terminal Spots',
                   variable=var11, onvalue=1, offvalue=0).grid(row=15, column=0, padx=10,sticky=W)
    
    tk.Label(window, text='____________________________________').grid(row=16, column=0,sticky=W)
    tk.Checkbutton(window, text='Create ConvexHull',
                   variable=var12, onvalue=1, offvalue=0).grid(row=17, column=0, padx=10,sticky=W)
    tk.Checkbutton(window, text='Use Terminal Points',
                   variable=var122, onvalue=1, offvalue=0).grid(row=17, column=0, padx=175,sticky=W)
    
    
    #Test if Mac
    qWhatOS = platform.system()
    if qWhatOS == 'Darwin':
        btn = Button(window, text="Analyze Filament", command=Filament_options)
    else:
        btn = Button(window, text="Analyze Filament", bg='blue', fg='white', command=Filament_options)
    
    btn.grid(column=0, row=18, sticky=W, padx=250)
    tk.Label(window, text='************************************').grid(row=18, column=0,sticky=W)
    
    
    
    tk.Label(window, text='New Statistics created:').grid(row=19,column=0, sticky=W)
    tk.Label(window, text='1) Regularity Index(BranchPoints)').grid(row=20,column=0, padx=40, sticky=W)
    tk.Label(window, text='2) Regularity Index(TerminalPoints)').grid(row=21,column=0, padx=40, sticky=W)
    tk.Label(window, text='3) Tortuosity (Filament & Segments)').grid(row=22,column=0, padx=40, sticky=W)
    
    tk.Label(window, text='New Statistics for "Find Spots close to Filaments":').grid(row=23,column=0, sticky=W)
    tk.Label(window, text='4) Number of Spots per dendrite segment').grid(row=24,column=0, padx=40, sticky=W)
    tk.Label(window, text='5) Distance of Colocalizaed spots to Starting point (soma)').grid(row=25,column=0, padx=40, sticky=W)
    tk.Label(window, text='6) Number Random Spots Coloc with filament/dendrites').grid(row=26,column=0, padx=40, sticky=W)
    
    
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
        lstbox.selection_set(0)
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
    # get the Selected Filaments in Surpass Scene
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
    vType = vImage.GetType()
    
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
    
    #Create a new folder object for Bouton Spots
    vNewSpotsBoutons = vImarisApplication.GetFactory().CreateSpots()
    # vNewSpotsvNewSpotsAlongFilament = vImarisApplication.GetFactory().CreateSpots()
    vNewSpotsAnalysisFolder =vImarisApplication.GetFactory().CreateDataContainer()
    vNewSpotsAnalysisFolder.SetName('Filament Analysis -- ' + vFilaments.GetName())
    
    vSpotFilamentPoints = vImarisApplication.GetFactory().CreateDataContainer()
    vSpotFilamentPoints.SetName(' Terminal/Branch Point Analysis - '+ str(vFilaments.GetName()))
    
    vSurfaceConvexHull = vImarisApplication.GetFactory().CreateDataContainer()
    vSurfaceConvexHull.SetName(' Dendritic Field Analysis - '+ str(vFilaments.GetName()))
    
    vSurfaceHull = vFactory.CreateSurfaces()
    
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
    xContactBranchIndexId=[]
    xContactSegmentId=[]
    xContactSegmentIdColoc=[]
    xCompleteSpotDistAlongFilamentStat=[]
    xCompleteBoutonDistAlongFilamentStat=[]
    xContactBranchIndexIdColoc=[]
    xCompleteSpotDistAlongFilamentStatColoc=[]
    zAllFilamentsRegularityIndexBP=[]
    zAllFilamentsRegularityIndexTP=[]
    vNewStatTortuosityPerFilament = []
    vCompleteSegmentsAnglesPerFilamentSpot = []
    vCompleteSegmentsAnglesPerFilamentSpotMean = []
    vNewStatCompleteTortuosityPerSegment = []
    vNewStatCompleteTortuosityPerSegmentSum = []
    wNumberRandomSpotColocPerFilament = []
    wNewStatRandomSpotColocPerFilament = []
    wFilamentBranchPointsComplete = []
    wFilamentTerminalPointsComplete =[]
    vNewStatCompleteFilamentBranchPointDistToSomaMean = []
    vNewStatCompleteFilamentTerminalPointDistToSomaMean = []
    vNewStatCompleteFilamentTerminalPointDistToSomaMax = []
    vNodeTypesComplete = []
    vNodeFilamentIdsComplete = []
    wNewStatConvexHullVolumePerFilament = []
    wNewStatConvexHullAreaPerFilament = []
    wCompleteTerminalPointsDistAlongFilamentStatALL = []
    wCompleteBranchPointsDistAlongFilamentStatALL = []
    wFilamentComplexityIndexComplete = []
    
    
    wLabelListTerminalPoints = []
    wLabelListBranchPoints = []
    
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
    if vOptionDendriteToDendriteContact == 1:
        label_3 = tk.Label(master, text="Dendrite Contact Progress Bar ")
    else:
        label_3 = tk.Label(master, text="Working... ")
    
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
    
    master.geometry('350x150')
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
    progress_bar3['value'] = 0
    master.update()
    #################################################################
    
    # if vOptionDendriteToDendriteContact==0:
    #     progress_bar3['value'] = 100
    #     master.update()
    
    ###############################################################################
    ###############################################################################
    if vNumberOfFilaments > 50:
        qisVisible=messagebox.askquestion("Processing Warning - Large Number of Filaments",
                                      'Do you wish to Hide Imaris Application?\n'
                                      ' This will increase processing speed\n''\n'
                                      'Close Progress window to CANCEL script')
        if qisVisible=='yes':
                vImarisApplication.SetVisible(0)
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
    
    aVersionValue = 10
    if not vAllFilamentDendriteLength:
        aVersionValue = 9
        vAllFilamentDendriteLengthSET = vFilaments.GetStatisticsByName('Dendrite Length')
        vAllFilamentDendriteLength = vAllFilamentDendriteLengthSET.mValues
        vAllFilamentDendriteLengthIds = vAllFilamentDendriteLengthSET.mIds
        vAllFilamentDendriteBranchDepthSET = vFilaments.GetStatisticsByName('Dendrite Branch Depth')
        vAllFilamentDendriteBranchDepthIds = vAllFilamentDendriteBranchDepthSET.mIds
        vAllFilamentDendriteBranchDepth = vAllFilamentDendriteBranchDepthSET.mValues
    
    
    if qIsSpines == True:
        vAllFilamentSpineLengthSET = vFilaments.GetStatisticsByName('Spine Length')
        vAllFilamentSpineLength = vAllFilamentSpineLengthSET.mValues
        vAllFilamentSpineLengthIds = vAllFilamentSpineLengthSET.mIds
    
    vStatPtPositionXSet = vFilaments.GetStatisticsByName('Pt Position X')
    vStatPtPositionYSet = vFilaments.GetStatisticsByName('Pt Position Y')
    vStatPtPositionZSet = vFilaments.GetStatisticsByName('Pt Position Z')
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
    
    wFilamentBranchPointsComplete.extend(wFilamentBranchPointsNEW.tolist())
    wFilamentTerminalPointsComplete.extend(wFilamentTerminalPointsNEW.tolist())
    
    
    # wFilamentTerminalPointsNEWCurrentBranchDepth = np.array(vAllFilamentDendriteBranchDepth)[np.where((wFilamentTerminalPointsNEW[:, None] == np.array(vFilamentsXYZ)).all(-1).any(-1))[0].tolist()]
    # wFilamentTerminalPointsNEWCurrentBranchLength = np.array(vAllFilamentDendriteLength)[np.where((wFilamentTerminalPointsNEW[:, None] == np.array(vFilamentsXYZ)).all(-1).any(-1))[0].tolist()]
    
    # wFilamentComplexityNumberPrimaryDendrites = np.size(np.where(wFilamentTerminalPointsNEWCurrentBranchDepth==0))
    # wFilamentComplexitySumTerminalBranchOrder = np.sum(wFilamentTerminalPointsNEWCurrentBranchDepth)
    
    # wFilamentComplexityIndexComplete.append((wFilamentComplexitySumTerminalBranchOrder + np.size(wFilamentTerminalPointsNEWCurrent[:,0]))/vAllFilamentLengthSum[aFilamentIndex]/wFilamentComplexityNumberPrimaryDendrites)
    
    
    
    ###############################################################################
    ###############################################################################
    
    
    aFilamentIndex=0
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
        vNumberOfDendriteBranches = len(vSegmentIds)#total number dendrite segments
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
    
    #Calculation of Mean Nearest Neighbor based on branch points and terminal points
        #Create a set of Random Spots, same numebr of branch points or terminal points
        #limit creation of random spot to be withint he MinMax of XYZ of the filament points
        zArray=np.array(vFilamentsXYZ)
        isFilament2D=False
        zRandomLimitsMin=np.min(zArray, 0)
        zRandomLimitsMax=np.max(zArray, 0)
        zRandomSpotsTerminal=[]
        zRandomSpotsNode=[]
        if np.shape(wFilamentBranchPointsNEWCurrent)[0] >3:
            zArrayNodes=cdist(wFilamentBranchPointsNEWCurrent,wFilamentBranchPointsNEWCurrent)
            zArrayNodesMin=np.where(zArrayNodes>0, zArrayNodes, np.inf).min(axis=1)
            zAverageNNBranchPoint=np.mean(zArrayNodesMin)
    
            for i in range(3):
                zRandomSpotsNode.append(np.random.uniform(low=zRandomLimitsMin[i], high=zRandomLimitsMax[i], size= np.shape(wFilamentBranchPointsNEW)[0]))
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
        if np.shape(wFilamentTerminalPointsNEWCurrent)[0] >3:
            zArrayTerminal=cdist(wFilamentTerminalPointsNEWCurrent,wFilamentTerminalPointsNEWCurrent)
            zArrayTerminalMin=np.where(zArrayTerminal>0, zArrayTerminal, np.inf).min(axis=1)
            zAverageNNTerminalPoint=np.mean(zArrayTerminalMin)
    
            for i in range(3):
                zRandomSpotsTerminal.append(np.random.uniform(low=zRandomLimitsMin[i], high=zRandomLimitsMax[i], size= np.shape(wFilamentTerminalPointsNEW)[0]))
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
    
    
    ###############################################################################
    #Branch Point Classification
        #Find Terminal segmentIds
        wTerminalSegmentIDs=[]
        for i in range(len(wFilamentTerminalPointsNEWCurrent)):
            wTerminalSegmentIDcurrent = np.where(np.array(vFilamentsEdges) == np.where((np.array(vFilamentsXYZ)==wFilamentTerminalPointsNEWCurrent[i].tolist()).all(1))[0].tolist())[0].tolist()[0]
            wTerminalSegmentIDs.append(vFilamentsEdgesSegmentId[wTerminalSegmentIDcurrent])
    
    ###############
        wNodeSegments = []
        vNodeTypePerFilament = []
        for i in range(len(wFilamentBranchPointsNEWCurrent)):
    
        #Identify segment IDs that are attached to branch point
            wNodeSegments.append(np.array(vFilamentsEdgesSegmentId)[np.where(np.array(vFilamentsEdges) == np.where(np.array(vFilamentsXYZ)[:,0] == wFilamentBranchPointsNEWCurrent[i][0])[0].tolist()[0])[0].tolist()].tolist())
            #Identify if segments attached to node are a terminal segment
            #count number per each node
            # len(np.intersect1d(wTerminalSegmentIDs,wNodeSegments[i]))
            vNodeTypePerFilament.append(len(np.intersect1d(wTerminalSegmentIDs,wNodeSegments[i])))
            vNodeTypesComplete.append(len(np.intersect1d(wTerminalSegmentIDs,wNodeSegments[i])))
        #list filamientID for each node
        vNodeFilamentIdsComplete.extend([vFilamentIds[vFilamentCountActual-1]]*len(wFilamentBranchPointsNEWCurrent))
    
            #categories.  1) Arborization, 2)Continuation, 3) Terminal
            #1)Arborization (A) nodes have two bifurcating children.
            #2)Continuation (C) nodes have one bifurcating and one terminating child.
            #3)Termination (T) nodes have two terminating children.
            #4)Other (T+) nodes more than 2 terminating children.
    
    ###############################################################################
        wFilamentTerminalPointsNEWCurrentBranchDepth = np.array(vAllFilamentDendriteBranchDepth)[np.where((wFilamentTerminalPointsNEW[:, None] == np.array(vFilamentsXYZ)).all(-1).any(-1))[0].tolist()]
        wFilamentTerminalPointsNEWCurrentBranchLength = np.array(vAllFilamentDendriteLength)[np.where((wFilamentTerminalPointsNEW[:, None] == np.array(vFilamentsXYZ)).all(-1).any(-1))[0].tolist()]
    
        wFilamentComplexityNumberPrimaryDendrites = np.size(np.where(wFilamentTerminalPointsNEWCurrentBranchDepth==0))
        wFilamentComplexitySumTerminalBranchOrder = np.sum(wFilamentTerminalPointsNEWCurrentBranchDepth)
    
        wFilamentComplexityIndexComplete.append((wFilamentComplexitySumTerminalBranchOrder + np.size(wFilamentTerminalPointsNEWCurrent[:,0]))/vAllFilamentLengthSum[aFilamentIndex]/wFilamentComplexityNumberPrimaryDendrites)
    
    
    
    
    ##############################################################################
    ##############################################################################
    
        vAllSegmentsPerFilamentRadiusWorkingInserts=[]
        vAllSegmentsPerFilamentPositionsWorkingInserts=[]
        vAllSegmentsTypesPerFilamentWorkingInserts=[]
        vAllSegmentIdsPerFilamentInserts=[]
        vAllSegmentIdsPerFilamentDendriteIndex=[]
        vAnglesPerCurrentSegment = []
        vNewStatTortuosityPerSegment = []
        vNewStatTortuosityPerSegmentSum = []
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
        wCompleteColocSpotDistAlongFilamentStatWorking=[]
        xCompleteSpotDistAlongFilamentStatWorking=[]
        xCompleteBoutonDistAlongFilamentStatWorking=[]
    
        wCompleteTerminalPointsDistAlongFilamentStatWorking=[]
        wCompleteBranchPointsDistAlongFilamentStatWorking=[]
        xCompleteDendriteDendriteContactSpotPositions=[]
        xLengthContactsWorkingDendrite=[]
        xCompleteDendriteDendriteContactSpotPositionsColoc=[]
        xLengthContactsWorkingDendriteColoc=[]
        xCompleteSpotSizeforContact=[]
        xCompleteSpotSizeforContactColoc=[]
        vNewStatAnglesPerCurrentFilamentSpot = []
        vNewStatAnglesPerCurrentFilamentSpotMean = []
    
    
    
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
    
            #test if Dendrite then move to next segment
            vOptionProcessOnlyDendrites = 0
            if vOptionProcessOnlyDendrites == 1:
                continue
            #Remove segments that have no length ID, likely in soma and cut out
            if not vSegmentIds[vBranchIndex] in vAllFilamentDendriteLengthIds:
                continue
    
            #Unit length number of points that make it up
            vSegmentBranchLength.append(len(vEdgesUniqueWorking))
    
            #Collate all processed SegmentIds by Type (dendrite or spine)
            if max(vSegmentTypesWorking)==0:
                wDendriteSegmentIds.append(vSegmentIdWorking)
            else:
                wSpineSegmentIds.append(vSegmentIdWorking)
    ###############################################################################
    ###############################################################################
            #Find/categorize branching nodes similar to Anze Testen experiment per filament
    
    
    
    
    ###############################################################################
    ###############################################################################
    #find gaps in the dendrite length and fill with extra spots
    #For bouton detect and Spots display
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
    #Calculating dendrite angles, by spiltting each segment into small bits
                ##Calcualte the angle between each adjacent points along the segment
                vSegmentAngles =[]
                vAnglesPerCurrentSegment =[]
                vAnglesPerCurrentSegmentMean =[]
                # if len(zNum)>2:
                if len(vSegmentPositionsWorkingInserts) > 2:
                    def TortuosityAngle(p1,p2,p3):
                        global ang
                        # These two vectors are in the plane
                        v1 = p3 - p1
                        v2 = p2 - p1
                        #dot product
                        p = v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]
                        #compute norms
                        n1 = math.sqrt(v1[0] * v1[0] + v1[1] * v1[1] + v1[2] * v1[2])
                        n2 = math.sqrt(v2[0] * v2[0] + v2[1] * v2[1] + v2[2] * v2[2])
                        #Compute angle
                        try:
                            ang = math.acos(p / (n1 * n2))
                        except:
                            ang = math.acos(1)
                        return ang
            #Set the first angle to zero
                    vSegmentAngles.append(float(0))
                    for i in range(len(vSegmentPositionsWorkingInserts)-2):
                        p1 = np.array(vSegmentPositionsWorkingInserts[i]) # Position of first point on plane
                        p2 = np.array(vSegmentPositionsWorkingInserts[i+1]) # Position of second point on plane
                        p3 = np.array(vSegmentPositionsWorkingInserts[i+2]) # Position of third point on plane
                        TortuosityAngle(p1,p2,p3)
                        vSegmentAngles.append(math.degrees(ang))
            #Set the last angle to zero
                    vSegmentAngles.append(float(0))
                else:
                    vSegmentAngles.extend([float(0) for i in range(len(vSegmentPositionsWorkingInserts))])
                vAnglesPerCurrentSegment.extend(vSegmentAngles)
                #Calcualte the average of every third
                #Every spot in current segment with mean angle
                for i in range (len(vAnglesPerCurrentSegment)):
                    vAnglesPerCurrentSegmentMean.append(mean(vAnglesPerCurrentSegment[i:i+2]))
                vAnglesPerCurrentSegmentMean[-1] = mean(vAnglesPerCurrentSegmentMean[-2:])
                vAnglesPerCurrentSegmentMean[-2] = mean(vAnglesPerCurrentSegmentMean[-3:])
    
                #compile all spot angle values for each point into single variable
                vCompleteSegmentsAnglesPerFilamentSpot.extend(vAnglesPerCurrentSegment)
                vCompleteSegmentsAnglesPerFilamentSpotMean.extend(vAnglesPerCurrentSegmentMean)
    
                #compile all angles for each point current filament
                vNewStatAnglesPerCurrentFilamentSpot.extend(vAnglesPerCurrentSegment)
                vNewStatAnglesPerCurrentFilamentSpotMean.extend(vAnglesPerCurrentSegmentMean)
    
                #Calculate Tortuosity
                vNewStatTortuosityPerSegment.append(sum(abs(np.array(vAnglesPerCurrentSegmentMean)))/(len(vSegmentPositionsWorkingInserts)-2)*math.pi)
    
                vNewStatCompleteTortuosityPerSegmentSum.append(sum(abs(np.array(vAnglesPerCurrentSegmentMean))))
                vNewStatCompleteTortuosityPerSegment.append(sum(abs(np.array(vAnglesPerCurrentSegmentMean)))/(len(vSegmentPositionsWorkingInserts)-2)*math.pi)
    
    
    ###############################################################################
    ###############################################################################
    # Detect VaricositiesBoutons based on the radius of filled spot list
            if vOptionFilamentBoutonDetection==1 and max(vSegmentTypesWorking)==0:
                peaks, _ = find_peaks(vSegmentRadiusWorkingInserts, height=vOptionBoutonHeight)
                # peakwidths=peak_widths(vSegmentRadiusWorkingInserts,zzpeaks)
                prominences = peak_prominences(vSegmentRadiusWorkingInserts, peaks)[0]
                PeakIndex=np.where(prominences>0.25)
                peaks=peaks[PeakIndex[0]]
    
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
                    #Test is segment has a valid length stat value, if not skip it
                    #Likely existed ib soma area, now in Imaris9.8 those are removed from overal stats
                    if np.any(vAllFilamentDendriteLengthIds == vSegmentIds[vBranchIndex]):
                        continue
    
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
    
                    wCurrentDendriteLength = np.where(vAllFilamentDendriteLengthIds==vSegmentIdWorking)
    
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
            for b in range (len(wFilamentBranchPointsNEW)):
                xNodeIndex=np.where((xAllFilamentPoints[:,0] == wFilamentBranchPointsNEW[b][0]) & (xAllFilamentPoints[:,1] == wFilamentBranchPointsNEW[b][1]) & (xAllFilamentPoints[:,2] == wFilamentBranchPointsNEW[b][2]))[0]
                xNodeIndex=xNodeIndex.tolist()
    
                #Identify branchID for each node index
                xBranchSharingNodes=list(itemgetter(*xNodeIndex)(vAllSegmentIdsPerFilamentDendriteIndex))
                xBranchSharingNodesALL.append(xBranchSharingNodes)
            xStartingBranchSharingNodes=[x[1] for x in enumerate(vAllSegmentIdsPerFilamentDendriteIndex)
                              if x[0] in xStartingPointIndex]
            xBranchSharingNodesALL.append(xStartingBranchSharingNodes)
    
    #############
        # #Find and search for indices of All points that match current Terminal ending
        #     for b in range (len(wFilamentTerminalPointsNEW)):
        #         xTerminalIndex=np.where((xAllFilamentPoints[:,0] == wFilamentTerminalPointsNEW[b][0]) &
        #                             (xAllFilamentPoints[:,1] == wFilamentTerminalPointsNEW[b][1]) &
        #                             (xAllFilamentPoints[:,2] == wFilamentTerminalPointsNEW[b][2]))[0]
        #         xTerminalIndex=xTerminalIndex.tolist()
        #         #Identify branchID for each Terminal index
        #         xTerminalBranch=DendriteCurrentWorkingPositions=list(itemgetter(*xTerminalIndex)(vAllSegmentIdsPerFilamentDendriteIndex))
        #         xTerminalBranchALL.append(xTerminalBranch)
    #############
            # vBranchIndex=6
            # vBranchIndex=3
            # vBranchIndex=2
            # vBranchIndex=59
            # vSegmentIdWorking = vSegmentIds[vBranchIndex]
            # np.where(np.array(vSegmentIds)==510000005409)
    
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
                                        xContactLength=1
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
                                    # xLengthContactsWorkingDendrite.append(xContactLength)
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
                                        xNumberDendriteContactsWorking=xNumberDendriteContactsWorking-1
                                        continue
                                    else:
                                    ###############################
                                        xLengthContactsWorkingDendrite.append(xContactLength)
    
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
                                    #w=22
    
                                    if xIsContinuous:# but not yet identified as end on continuous contact
                                        xContactTest=np.isin(xCBIarray[:,w],xCBIarray[:,w+1]).astype(int)
                                        if ((xContactTest[2] == 0) and (xContactTest[0] == 0)):
    
                                            xNumberDendriteContactsWorking=xNumberDendriteContactsWorking+1
                                            xContactLength=xContactLength+1
                                            # xLengthContactsWorkingDendrite.append(xContactLength)
                                            xIsContinuous=False#Reset this marker
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
                                                xNumberDendriteContactsWorking=xNumberDendriteContactsWorking-1
                                                continue
                                            else:
                                            ###############################
                                                xLengthContactsWorkingDendrite.append(xContactLength)
                                                xCompleteSpotSizeforContact.append(xContinuousContactSpotSize)
                                                xCompleteDendriteDendriteContactSpotPositions.append(xContactSpotPostionWorking)
                                                xContactBranchIndexId.append(vBranchIndex)
                                                xContactSegmentId.append(vSegmentIds[vBranchIndex])
                                                xSpotSizeforContinuousContactId=[]#Reset to blank for next contact point
                                                # print('Final continuous point')
                                                xContactLength=0
                                                continue
                                        elif ((xContactTest[0] == 1) and (xContactTest[2] == 1)):# and xCBIarray[1,w]-3 <= xCBIarray[1,w+1] <= xCBIarray[1,w]+3:
                                            #continuous but does not add to length of contact
                                            # print('skip one - 2 consecutive contacts same dendrite same point','w=', w)
                                            continue
                                        elif ((xContactTest[0] == 0) and (xContactTest[2] == 1)):
                                            if ((xCBIarray[0,w]==(xCBIarray[0,w+1])-1) or (xCBIarray[0,w]==(xCBIarray[0,w+1])-2)):# and xCBIarray[1,w]-3 <= xCBIarray[1,w+1] <= xCBIarray[1,w]+3:
                                                #continuous and add to length of contact
                                                xContactLength=xContactLength+1
                                                xSpotSizeforContinuousContactId.append(xCBIarray[0,w])#mark working dendrite pointId for continuous contact
                                                xIsContinuous==True
                                                # print ('continuous contact on working denrite-next','w=', w)
                                                continue
                                            else:
                                                xNumberDendriteContactsWorking=xNumberDendriteContactsWorking+1
                                                xContactLength=xContactLength+1
                                                # xLengthContactsWorkingDendrite.append(xContactLength)
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
                                                    xNumberDendriteContactsWorking=xNumberDendriteContactsWorking-1
                                                    continue
                                                else:
                                                ###############################
                                                    xLengthContactsWorkingDendrite.append(xContactLength)
                                                    xCompleteSpotSizeforContact.append(xContinuousContactSpotSize)
                                                    xCompleteDendriteDendriteContactSpotPositions.append(xContactSpotPostionWorking)
                                                    xContactBranchIndexId.append(vBranchIndex)
                                                    xContactSegmentId.append(vSegmentIds[vBranchIndex])
                                                    xSpotSizeforContinuousContactId=[]
                                                    # print('final point contact', 'w=', w)
                                                    continue
    
                                        elif ((xContactTest[0] == 1) and (xContactTest[2] == 0)):
    
                                            xNumberDendriteContactsWorking=xNumberDendriteContactsWorking+1
                                            xContactLength=xContactLength+1
                                            # xLengthContactsWorkingDendrite.append(xContactLength)
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
                                                xNumberDendriteContactsWorking=xNumberDendriteContactsWorking-1
                                                continue
                                            else:
                                            ###############################
                                                xLengthContactsWorkingDendrite.append(xContactLength)
    
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
                    vNewSpotsDendriteDendriteContacts.SetName('Dendrite Self Avoidance Contacts -- FilamentId:' + str(vFilamentIds[vFilamentCountActual-1]))
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
                    vSpotsStatNames=[' Intra Dendrite Contact Length']*len(xCompleteDendriteDendriteContactSpotPositions)
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
                    vNewSpotsFilamentFilamentContacts.SetName('Colocalization Contacts with '+ str(vFilamentColoc.GetName()) + '-- FilamentId:' + str(vFilamentIds[vFilamentCountActual-1]))
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
                    vSpotsStatNames=[' Filament Coloc Contact Length']*len(xCompleteDendriteDendriteContactSpotPositionsColoc)
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
    
                    #Create array of distance measures to original filament points
                    wSpotToAllFilamentDistanceArrayOriginal=cdist(xCompleteDendriteDendriteContactSpotPositions,vFilamentsXYZ)
                    # wSpotToAllFilamentDistanceArrayOriginal=wSpotToAllFilamentDistanceArrayOriginal- vFilamentsRadius -[max(vSpotsColocRadiusWorking[0])]*len(vFilamentsRadius)
                    wSpotBranchPointToAllFilamentDistanceArrayOriginal=cdist(wFilamentBranchPointsNEWCurrent,vFilamentsXYZ)
                    wSpotTerminalPointToAllFilamentDistanceArrayOriginal=cdist(wFilamentTerminalPointsNEWCurrent,vFilamentsXYZ)
    
                    wBranchIdxBlock = np.where(wSpotBranchPointToAllFilamentDistanceArrayOriginal==0)[1].tolist()
                    wTerminalIdxBlock = np.where(wSpotTerminalPointToAllFilamentDistanceArrayOriginal==0)[1].tolist()
    
                    #Replace zeros with large number
                    wSpotToAllFilamentDistanceArrayOriginal[:,wBranchIdxBlock]=9999
                    wSpotToAllFilamentDistanceArrayOriginal[:,wTerminalIdxBlock]=9999
    
                    #Replace Starting point from FilamentXYZ with col of large 9999
                    # (np.where(np.array(vFilamentsXYZ) == wFilamentStartingPointsNEWCurrent[0]))[0][0]
                    wSpotToAllFilamentDistanceArrayOriginal[:,[(np.where(np.array(vFilamentsXYZ) == wFilamentStartingPointsNEWCurrent[0]))[0][0]]]=9999
    
                    #For each spot, find index on filament of closest point
                    wSpotsFilamentClosestDistancePointIndex=np.argmin(wSpotToAllFilamentDistanceArrayOriginal, axis=1)
    
                    #loop for each spot within threshold
                    #append new filament and create list of new contact points
                    for i in range (len(xCompleteDendriteDendriteContactSpotPositions)):
                        wNewFilamentsXYZ.append(((np.array(xCompleteDendriteDendriteContactSpotPositions))+.00001)[i].tolist())
                        wNewFilamentsRadius.append(1)
                        wNewFilamentsEdges.append([wSpotsFilamentClosestDistancePointIndex[i],len(vFilamentsRadius)+i])
                        wNewFilamentsTypes.append(1)
    
                    #Create new temp filament object
                    vNewFilament=vImarisApplication.GetFactory().CreateFilaments()
                    vNewFilament.AddFilament(wNewFilamentsXYZ, wNewFilamentsRadius, wNewFilamentsTypes, wNewFilamentsEdges, vFilamentsIndexT)
                    vNewFilament.SetBeginningVertexIndex(0, vBeginningVertex)
    
                    #Reset the "new filament"
                    wNewFilamentsXYZ=[]
                    wNewFilamentsRadius=[]
                    wNewFilamentsEdges=[]
                    wNewFilamentsTypes=[]
    
        #Grab New Filament Spine Statistics for attachment point distance.
                    vNewFilamentSpineAttPtDistSET = vNewFilament.GetStatisticsByName('Spine Attachment Pt Distance')
                    vNewFilamentSpineAttPtPosXSET = vNewFilament.GetStatisticsByName('Spine Attachment Pt Position X')
                    vNewFilamentSpineAttPtDistValues = vNewFilamentSpineAttPtDistSET.mValues
                    vNewFilamentSpineAttPtDistIds = vNewFilamentSpineAttPtDistSET.mIds
                    vNewFilamentSpineAttPtPosXValues = vNewFilamentSpineAttPtPosXSET.mValues
                    vNewFilamentSpineAttPtPosXIds = vNewFilamentSpineAttPtPosXSET.mIds
    
                    #Collate all Filament contact point spots for each filament
                    for i in range (len(xCompleteDendriteDendriteContactSpotPositions)):
                        xCompleteSpotDistAlongFilamentStatWorking.append(vNewFilamentSpineAttPtDistValues[vNewFilamentSpineAttPtDistIds.index(vNewFilamentSpineAttPtPosXIds[vNewFilamentSpineAttPtPosXValues.index(wNewFilamentsXYZ[wSpotsFilamentClosestDistancePointIndex[i]][0])])])
                        xCompleteSpotDistAlongFilamentStat.append(vNewFilamentSpineAttPtDistValues[vNewFilamentSpineAttPtDistIds.index(vNewFilamentSpineAttPtPosXIds[vNewFilamentSpineAttPtPosXValues.index(wNewFilamentsXYZ[wSpotsFilamentClosestDistancePointIndex[i]][0])])])
    
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
                    vNewSpotsvNewSpotsAlongFilament.SetName('Can NOT calculate no Starting Point -- FilamentId:' + str(vFilamentIds[vFilamentCountActual-1]))
                    vNewSpotsAnalysisFolder.AddChild(vNewSpotsvNewSpotsAlongFilament, -1)
    
    ###############################################################################
    ###############################################################################
    #After Each Filament
    #Find distance along Filament for all boutons
        if vOptionFilamentBoutonDetection==1:
            vNewSpotsBoutons = vImarisApplication.GetFactory().CreateSpots()
            if vAllNewSpotsBoutonsRadius==[]:
                vNewSpotsBoutons.SetName(' NO Boutons Found -- FilamentId:' + str(vFilamentIds[vFilamentCountActual-1]))
                vNewSpotsBoutonsTimeIndex=[vFilamentsIndexT]*len(vAllNewSpotsBoutonsRadius)
                vNewSpotsBoutons.Set(vAllNewSpotsBoutonsPositionXYZ, vNewSpotsBoutonsTimeIndex, vAllNewSpotsBoutonsRadius)
                vNewSpotsAnalysisFolder.AddChild(vNewSpotsBoutons, -1)
                vImarisApplication.GetSurpassScene().AddChild(vNewSpotsAnalysisFolder, -1);
            else:
                vNewSpotsBoutonsTimeIndex=[vFilamentsIndexT]*len(vAllNewSpotsBoutonsRadius)
                vNewSpotsBoutons.SetName('Detected Varicosities (Boutons) -- FilamentId:' + str(vFilamentIds[vFilamentCountActual-1]))
                vNewSpotsBoutons.SetColorRGBA(18000)
                vNewSpotsBoutons.Set(vAllNewSpotsBoutonsPositionXYZ, vNewSpotsBoutonsTimeIndex, vAllNewSpotsBoutonsRadius)
                vNewSpotsAnalysisFolder.AddChild(vNewSpotsBoutons, -1)
                vImarisApplication.GetSurpassScene().AddChild(vNewSpotsAnalysisFolder, -1);
    
            if vBeginningVertex !=-1:
                wNewSpotsOnFilament=vAllNewSpotsBoutonsPositionXYZ
    
                wNewFilamentsEdges=list(vFilamentsEdges)
                wNewFilamentsRadius=list(vFilamentsRadius)
                wNewFilamentsXYZ=list(vFilamentsXYZ)
                wNewFilamentsTypes=list(vTypes)
    
                #Create array of distance measures to original filament points
                wSpotToAllFilamentDistanceArrayOriginal=cdist(wNewSpotsOnFilament,vFilamentsXYZ)
                # wSpotToAllFilamentDistanceArrayOriginal=wSpotToAllFilamentDistanceArrayOriginal- vFilamentsRadius -[max(vSpotsColocRadiusWorking[0])]*len(vFilamentsRadius)
                wSpotBranchPointToAllFilamentDistanceArrayOriginal=cdist(wFilamentBranchPointsNEWCurrent,vFilamentsXYZ)
                wSpotTerminalPointToAllFilamentDistanceArrayOriginal=cdist(wFilamentTerminalPointsNEWCurrent,vFilamentsXYZ)
    
                wBranchIdxBlock = np.where(wSpotBranchPointToAllFilamentDistanceArrayOriginal==0)[1].tolist()
                wTerminalIdxBlock = np.where(wSpotTerminalPointToAllFilamentDistanceArrayOriginal==0)[1].tolist()
    
                #Replace zeros with large number
                wSpotToAllFilamentDistanceArrayOriginal[wSpotToAllFilamentDistanceArrayOriginal==0]=9999
                wSpotToAllFilamentDistanceArrayOriginal[:,wBranchIdxBlock]=9999
                wSpotToAllFilamentDistanceArrayOriginal[:,wTerminalIdxBlock]=9999
    
                #Replace Starting point from FilamentXYZ with col of large 9999
                # (np.where(np.array(vFilamentsXYZ) == wFilamentStartingPointsNEWCurrent[0]))[0][0]
                wSpotToAllFilamentDistanceArrayOriginal[:,[(np.where(np.array(vFilamentsXYZ) == wFilamentStartingPointsNEWCurrent[0]))[0][0]]]=9999
    
                #For each spot, find index on filament of closest point
                wSpotsFilamentClosestDistancePointIndex=np.argmin(wSpotToAllFilamentDistanceArrayOriginal, axis=1)
    
                #loop for each spot within threshold
                #append new filament and create list of new contact points
                for i in range (len(wNewSpotsOnFilament)):
                    wNewFilamentsXYZ.append(((np.array(wNewSpotsOnFilament))+.00001)[i].tolist())
                    wNewFilamentsRadius.append(1)
                    wNewFilamentsEdges.append([wSpotsFilamentClosestDistancePointIndex[i],len(vFilamentsRadius)+i])
                    wNewFilamentsTypes.append(1)
    
                #Create new temp filament object
                vNewFilament=vImarisApplication.GetFactory().CreateFilaments()
                vNewFilament.AddFilament(wNewFilamentsXYZ, wNewFilamentsRadius, wNewFilamentsTypes, wNewFilamentsEdges, vFilamentsIndexT)
                vNewFilament.SetBeginningVertexIndex(0, vBeginningVertex)
    
                # #Reset the "new filament"
                # wNewFilamentsXYZ=[]
                # wNewFilamentsRadius=[]
                # wNewFilamentsEdges=[]
                # wNewFilamentsTypes=[]
    
    #Grab New Filament Spine Statistics for attachment point distance.
                vNewFilamentSpineAttPtDistSET = vNewFilament.GetStatisticsByName('Spine Attachment Pt Distance')
                vNewFilamentSpineAttPtPosXSET = vNewFilament.GetStatisticsByName('Spine Attachment Pt Position X')
                vNewFilamentSpineAttPtDistValues = vNewFilamentSpineAttPtDistSET.mValues
                vNewFilamentSpineAttPtDistIds = vNewFilamentSpineAttPtDistSET.mIds
                vNewFilamentSpineAttPtPosXValues = vNewFilamentSpineAttPtPosXSET.mValues
                vNewFilamentSpineAttPtPosXIds = vNewFilamentSpineAttPtPosXSET.mIds
    
                #Collate all Sholl spots for each filament
                for i in range (len(wNewSpotsOnFilament)):
                    xCompleteBoutonDistAlongFilamentStatWorking.append(vNewFilamentSpineAttPtDistValues[vNewFilamentSpineAttPtDistIds.index(vNewFilamentSpineAttPtPosXIds[vNewFilamentSpineAttPtPosXValues.index(wNewFilamentsXYZ[wSpotsFilamentClosestDistancePointIndex[i]][0])])])
                    xCompleteBoutonDistAlongFilamentStat.append(vNewFilamentSpineAttPtDistValues[vNewFilamentSpineAttPtDistIds.index(vNewFilamentSpineAttPtPosXIds[vNewFilamentSpineAttPtPosXValues.index(wNewFilamentsXYZ[wSpotsFilamentClosestDistancePointIndex[i]][0])])])
    
                vNewSpotsOnFilamentIndex=[vFilamentsIndexT+1]*len(vAllNewSpotsBoutonsRadius)
                vSpotsvIds=list(range(len(vAllNewSpotsBoutonsRadius)))
                vSpotsStatUnits=['um']*len(vAllNewSpotsBoutonsRadius)
                vSpotsStatFactors=(['Spot']*len(vAllNewSpotsBoutonsRadius), [str(x) for x in vNewSpotsOnFilamentIndex] )
                vSpotsStatFactorName=['Category','Time']
                vSpotsStatNames=[' Distance to Starting Point ']*len(vAllNewSpotsBoutonsRadius)
    
                vNewSpotsBoutons.AddStatistics(vSpotsStatNames, xCompleteBoutonDistAlongFilamentStatWorking,
                                          vSpotsStatUnits, vSpotsStatFactors, vSpotsStatFactorName, vSpotsvIds)
    
    #Calculate the mean Toruosity for all segments in the filament object
        # np.array(vNewStatTortuosityPerSegment)
        vNewStatTortuosityPerFilament.append(np.mean(np.array(vNewStatTortuosityPerSegment)[np.where(np.array(vNewStatTortuosityPerSegment)>0)]))
    
        # # x[x != 'nan']
        # test=np.array(vNewStatTortuosityPerSegment)[[np.array(vNewStatTortuosityPerSegment)]!='nan']
        # np.array(vNewStatTortuosityPerSegment)[np.where(np.array(vNewStatTortuosityPerSegment)>0)]
    ###############################################################################
    ###############################################################################
        if vOptionTerminalPoints == 1:
            # if vOptionMergePoints == 0:
            #     vNewSpotsTerminalPointsPerFilament = vImarisApplication.GetFactory().CreateSpots()
            #     vNewSpotsTerminalPointsPerFilament.Set(wFilamentTerminalPointsNEWCurrent.tolist(),
            #                           [vFilamentsIndexT]*len(wFilamentTerminalPointsNEWCurrent.tolist()),
            #                           [1]*len(wFilamentTerminalPointsNEWCurrent.tolist()))
            #     vNewSpotsTerminalPointsPerFilament.SetName(' TerminalPoints - FilamentID:'+ str(vFilamentIds[vFilamentCountActual-1]))
            #     zRandomColor=(random.uniform(0, 1) * 256 * 256 * 256 )
            #     vNewSpotsTerminalPointsPerFilament.SetColorRGBA(zRandomColor)#Set Random color
            #     vSpotFilamentPoints.AddChild(vNewSpotsTerminalPointsPerFilament, -1)
            #     vImarisApplication.GetSurpassScene().AddChild(vSpotFilamentPoints, -1)
    
            wNewFilamentsEdgesTerminal=list(vFilamentsEdges)
            wNewFilamentsRadiusTerminal=list(vFilamentsRadius)
            wNewFilamentsXYZTerminal=list(vFilamentsXYZ)
            wNewFilamentsTypesTerminal=list(vTypes)
    
            #Create array of distance measures to original filament points
            wSpotBranchPointToAllFilamentDistanceArrayOriginal=cdist(wFilamentBranchPointsNEWCurrent,vFilamentsXYZ)
            wSpotTerminalPointToAllFilamentDistanceArrayOriginal=cdist(wFilamentTerminalPointsNEWCurrent,vFilamentsXYZ)        #Replace zeros with large number
            # wSpotTerminalPointToAllFilamentDistanceArrayOriginal[wSpotTerminalPointToAllFilamentDistanceArrayOriginal==0]=9999
    
            wBranchIdxBlock = np.where(wSpotBranchPointToAllFilamentDistanceArrayOriginal==0)[1].tolist()
            wTerminalIdxBlock = np.where(wSpotTerminalPointToAllFilamentDistanceArrayOriginal==0)[1].tolist()
    
            wSpotTerminalPointToAllFilamentDistanceArrayOriginal[:,wBranchIdxBlock]=9999
            wSpotTerminalPointToAllFilamentDistanceArrayOriginal[:,wTerminalIdxBlock]=9999
    
            #Replace Starting point from FilamentXYZ with col of large 9999
            # (np.where(np.array(vFilamentsXYZ) == wFilamentStartingPointsNEWCurrent[0]))[0][0]
            wSpotTerminalPointToAllFilamentDistanceArrayOriginal[:,[(np.where(np.array(vFilamentsXYZ) == wFilamentStartingPointsNEWCurrent[0]))[0][0]]]=9999
    
            #find all indices that are "9999" and make whole column "9999"
            #np.where(wSpotBranchPointToAllFilamentDistanceArrayOriginal==9999)[1].tolist()
            # wSpotTerminalPointToAllFilamentDistanceArrayOriginal[:,np.where(wSpotTerminalPointToAllFilamentDistanceArrayOriginal==9999)[1].tolist()]=9999
    
    
            #For each spot, find index on filament of closest point
            wSpotsTerminalPointsFilamentClosestDistancePointIndex=np.argmin(wSpotTerminalPointToAllFilamentDistanceArrayOriginal, axis=1)
            #loop for each Terminal Point
            #append new filament and create list of new spots
            for i in range (len(wFilamentTerminalPointsNEWCurrent)):
                wNewFilamentsXYZTerminal.append((wFilamentTerminalPointsNEWCurrent+0.00001)[i].tolist())
                wNewFilamentsRadiusTerminal.append(1)
                wNewFilamentsEdgesTerminal.append([wSpotsTerminalPointsFilamentClosestDistancePointIndex[i],len(vFilamentsRadius)+i])
                wNewFilamentsTypesTerminal.append(1)
            vNewFilamentTerminal = vImarisApplication.GetFactory().CreateFilaments()
            vNewFilamentTerminal.AddFilament(wNewFilamentsXYZTerminal, wNewFilamentsRadiusTerminal, wNewFilamentsTypesTerminal, wNewFilamentsEdgesTerminal, vFilamentsIndexT)
            vNewFilamentTerminal.SetBeginningVertexIndex(0, vBeginningVertex)
    
            vNewFilamentSpineAttPtDistSET = vNewFilamentTerminal.GetStatisticsByName('Spine Attachment Pt Distance')
            vNewFilamentSpineAttPtPosXSET = vNewFilamentTerminal.GetStatisticsByName('Spine Attachment Pt Position X')
            vNewFilamentSpineAttPtDistValues = vNewFilamentSpineAttPtDistSET.mValues
            vNewFilamentSpineAttPtDistIds = vNewFilamentSpineAttPtDistSET.mIds
            vNewFilamentSpineAttPtPosXValues = vNewFilamentSpineAttPtPosXSET.mValues
            vNewFilamentSpineAttPtPosXIds = vNewFilamentSpineAttPtPosXSET.mIds
    
            for i in range (len(wFilamentTerminalPointsNEWCurrent)):
                wCompleteTerminalPointsDistAlongFilamentStatWorking.append(vNewFilamentSpineAttPtDistValues[vNewFilamentSpineAttPtDistIds.index(vNewFilamentSpineAttPtPosXIds[vNewFilamentSpineAttPtPosXValues.index(wNewFilamentsXYZTerminal[wSpotsTerminalPointsFilamentClosestDistancePointIndex[i]][0])])])
                wCompleteTerminalPointsDistAlongFilamentStatALL.append(vNewFilamentSpineAttPtDistValues[vNewFilamentSpineAttPtDistIds.index(vNewFilamentSpineAttPtPosXIds[vNewFilamentSpineAttPtPosXValues.index(wNewFilamentsXYZTerminal[wSpotsTerminalPointsFilamentClosestDistancePointIndex[i]][0])])])
    #################
                vLabelIndices=list(range(len(wCompleteTerminalPointsDistAlongFilamentStatWorking)))
                for j in range (len(vLabelIndices)):
                    vLabelCreate = vFactory.CreateObjectLabel(vLabelIndices[j],
                                                                  'FilamentIds',
                                                                  str(vFilamentIds[aFilamentIndex]))
                    wLabelListTerminalPoints.append(vLabelCreate)
    ##################
            #For  Filament stat
            vNewStatFilamentTerminalPointDistToSomaMax = max(wCompleteTerminalPointsDistAlongFilamentStatWorking)
            vNewStatFilamentTerminalPointDistToSomaMean = mean(wCompleteTerminalPointsDistAlongFilamentStatWorking)
            vNewStatFilamentBranchPointDistToSomaMax = max(wCompleteTerminalPointsDistAlongFilamentStatWorking)
            vNewStatFilamentBranchPointDistToSomaMean = mean(wCompleteTerminalPointsDistAlongFilamentStatWorking)
    
            vNewStatCompleteFilamentBranchPointDistToSomaMean.append(vNewStatFilamentBranchPointDistToSomaMean)
            vNewStatCompleteFilamentTerminalPointDistToSomaMean.append(vNewStatFilamentTerminalPointDistToSomaMean)
    
            vNewStatCompleteFilamentTerminalPointDistToSomaMax.append(vNewStatFilamentTerminalPointDistToSomaMax)
    
            if vOptionMergePoints == 0:
                vNewSpotsTerminalPointsPerFilament = vImarisApplication.GetFactory().CreateSpots()
                vNewSpotsTerminalPointsPerFilament.Set(wFilamentTerminalPointsNEWCurrent.tolist(),
                                      [vFilamentsIndexT]*len(wFilamentTerminalPointsNEWCurrent.tolist()),
                                      [1]*len(wFilamentTerminalPointsNEWCurrent.tolist()))
                vNewSpotsTerminalPointsPerFilament.SetName(' TerminalPoints - FilamentID:'+ str(vFilamentIds[vFilamentCountActual-1]))
                zRandomColor=(random.uniform(0, 1) * 256 * 256 * 256 )
                vNewSpotsTerminalPointsPerFilament.SetColorRGBA(zRandomColor)#Set Random color
                vSpotFilamentPoints.AddChild(vNewSpotsTerminalPointsPerFilament, -1)
                vImarisApplication.GetSurpassScene().AddChild(vSpotFilamentPoints, -1)
    
                vSpotsTimeIndex=[vFilamentsIndexT+1]*len(wFilamentTerminalPointsNEWCurrent)
                vSpotsvIds=list(range(len(wFilamentTerminalPointsNEWCurrent)))
                vSpotsStatUnits=['um']*len(wFilamentTerminalPointsNEWCurrent)
                vSpotsStatFactors=(['Spot']*len(wFilamentTerminalPointsNEWCurrent), [str(x) for x in vSpotsTimeIndex] )
                vSpotsStatFactorName=['Category','Time']
                vSpotsStatNames=[' Distance to soma from Terminal Point']*len(wFilamentTerminalPointsNEWCurrent)
                vNewSpotsTerminalPointsPerFilament.AddStatistics(vSpotsStatNames, wCompleteTerminalPointsDistAlongFilamentStatWorking,
                                              vSpotsStatUnits, vSpotsStatFactors,
                                              vSpotsStatFactorName, vSpotsvIds)
    
    #Create Spots for each Branch Point
        if vOptionBranchPoints == 1:
    
            # if vOptionMergePoints == 0:
            #     vNewSpotsBranchPointsPerFilament = vImarisApplication.GetFactory().CreateSpots()
            #     vNewSpotsBranchPointsPerFilament.Set(wFilamentBranchPointsNEWCurrent.tolist(),
            #                           [vFilamentsIndexT]*len(wFilamentBranchPointsNEWCurrent.tolist()),
            #                           [1]*len(wFilamentBranchPointsNEWCurrent.tolist()))
            #     vNewSpotsBranchPointsPerFilament.SetName(' BranchPoints - FilamentID:'+ str(vFilamentIds[vFilamentCountActual-1]))
            #     zRandomColor=(random.uniform(0, 1) * 256 * 256 * 256 )
            #     vNewSpotsBranchPointsPerFilament.SetColorRGBA(zRandomColor)#Set Random color
            #     vSpotFilamentPoints.AddChild(vNewSpotsBranchPointsPerFilament, -1)
            #     vImarisApplication.GetSurpassScene().AddChild(vSpotFilamentPoints, -1)
    
            wNewFilamentsEdgesBranch=list(vFilamentsEdges)
            wNewFilamentsRadiusBranch=list(vFilamentsRadius)
            wNewFilamentsXYZBranch=list(vFilamentsXYZ)
            wNewFilamentsTypesBranch=list(vTypes)
    
            #Create array of distance measures to original filament points
            wSpotBranchPointToAllFilamentDistanceArrayOriginal=cdist(wFilamentBranchPointsNEWCurrent,vFilamentsXYZ)
            wSpotTerminalPointToAllFilamentDistanceArrayOriginal=cdist(wFilamentTerminalPointsNEWCurrent,vFilamentsXYZ)
    
            wBranchIdxBlock = np.where(wSpotBranchPointToAllFilamentDistanceArrayOriginal==0)[1].tolist()
            wTerminalIdxBlock = np.where(wSpotTerminalPointToAllFilamentDistanceArrayOriginal==0)[1].tolist()
    
            #Replace zeros with large number
            wSpotBranchPointToAllFilamentDistanceArrayOriginal[:,wBranchIdxBlock] = 9999
            wSpotBranchPointToAllFilamentDistanceArrayOriginal[:,wTerminalIdxBlock] = 9999
    
            #Replace Starting point from FilamentXYZ with col of large 9999
            # (np.where(np.array(vFilamentsXYZ) == wFilamentStartingPointsNEWCurrent[0]))[0][0]
            wSpotBranchPointToAllFilamentDistanceArrayOriginal[:,[(np.where(np.array(vFilamentsXYZ) == wFilamentStartingPointsNEWCurrent[0]))[0][0]]]=9999
    
            #For each spot, find index on filament of closest point
            wSpotsBranchPointsFilamentClosestDistancePointIndex=np.argmin(wSpotBranchPointToAllFilamentDistanceArrayOriginal, axis=1)
            #loop for each Terminal Point
            #append new filament and create list of new spots
            for i in range (len(wFilamentBranchPointsNEWCurrent)):
                wNewFilamentsXYZBranch.append((wFilamentBranchPointsNEWCurrent+0.00001)[i].tolist())
                wNewFilamentsRadiusBranch.append(1)
                wNewFilamentsEdgesBranch.append([wSpotsBranchPointsFilamentClosestDistancePointIndex[i],len(vFilamentsRadius)+i])
                wNewFilamentsTypesBranch.append(1)
            vNewFilamentBranch = vImarisApplication.GetFactory().CreateFilaments()
            vNewFilamentBranch.AddFilament(wNewFilamentsXYZBranch, wNewFilamentsRadiusBranch, wNewFilamentsTypesBranch, wNewFilamentsEdgesBranch, vFilamentsIndexT)
            vNewFilamentBranch.SetBeginningVertexIndex(0, vBeginningVertex)
    
            vNewFilamentSpineAttPtDistSET = vNewFilamentBranch.GetStatisticsByName('Spine Attachment Pt Distance')
            vNewFilamentSpineAttPtPosXSET = vNewFilamentBranch.GetStatisticsByName('Spine Attachment Pt Position X')
            vNewFilamentSpineAttPtDistValues = vNewFilamentSpineAttPtDistSET.mValues
            vNewFilamentSpineAttPtDistIds = vNewFilamentSpineAttPtDistSET.mIds
            vNewFilamentSpineAttPtPosXValues = vNewFilamentSpineAttPtPosXSET.mValues
            vNewFilamentSpineAttPtPosXIds = vNewFilamentSpineAttPtPosXSET.mIds
    
            for i in range (len(wFilamentBranchPointsNEWCurrent)):
                wCompleteBranchPointsDistAlongFilamentStatWorking.append(vNewFilamentSpineAttPtDistValues[vNewFilamentSpineAttPtDistIds.index(vNewFilamentSpineAttPtPosXIds[vNewFilamentSpineAttPtPosXValues.index(wNewFilamentsXYZBranch[wSpotsBranchPointsFilamentClosestDistancePointIndex[i]][0])])])
                wCompleteBranchPointsDistAlongFilamentStatALL.append(vNewFilamentSpineAttPtDistValues[vNewFilamentSpineAttPtDistIds.index(vNewFilamentSpineAttPtPosXIds[vNewFilamentSpineAttPtPosXValues.index(wNewFilamentsXYZBranch[wSpotsBranchPointsFilamentClosestDistancePointIndex[i]][0])])])
    
                vLabelIndices=list(range(len(wCompleteBranchPointsDistAlongFilamentStatWorking)))
                for j in range (len(vLabelIndices)):
                    vLabelCreate = vFactory.CreateObjectLabel(vLabelIndices[j],
                                                                  'FilamentIds',
                                                                  str(vFilamentIds[aFilamentIndex]))
                    wLabelListBranchPoints.append(vLabelCreate)
    
    
            if vOptionMergePoints == 0:
                vNewSpotsBranchPointsPerFilament = vImarisApplication.GetFactory().CreateSpots()
                vNewSpotsBranchPointsPerFilament.Set(wFilamentBranchPointsNEWCurrent.tolist(),
                                      [vFilamentsIndexT]*len(wFilamentBranchPointsNEWCurrent.tolist()),
                                      [1]*len(wFilamentBranchPointsNEWCurrent.tolist()))
                vNewSpotsBranchPointsPerFilament.SetName(' BranchPoints - FilamentID:'+ str(vFilamentIds[vFilamentCountActual-1]))
                zRandomColor=(random.uniform(0, 1) * 256 * 256 * 256 )
                vNewSpotsBranchPointsPerFilament.SetColorRGBA(zRandomColor)#Set Random color
                vSpotFilamentPoints.AddChild(vNewSpotsBranchPointsPerFilament, -1)
                vImarisApplication.GetSurpassScene().AddChild(vSpotFilamentPoints, -1)
    
                vSpotsTimeIndex=[vFilamentsIndexT+1]*len(wFilamentBranchPointsNEWCurrent)
                vSpotsvIds=list(range(len(wFilamentBranchPointsNEWCurrent)))
                vSpotsStatUnits=['um']*len(wFilamentBranchPointsNEWCurrent)
                vSpotsStatFactors=(['Spot']*len(wFilamentBranchPointsNEWCurrent), [str(x) for x in vSpotsTimeIndex] )
                vSpotsStatFactorName=['Category','Time']
                #Create stats for distance along dendrite
                vSpotsStatUnits=['um']*len(wFilamentBranchPointsNEWCurrent)
                vSpotsStatNames=[' Distance to soma from Branch Point']*len(wFilamentBranchPointsNEWCurrent)
                vNewSpotsBranchPointsPerFilament.AddStatistics(vSpotsStatNames, wCompleteBranchPointsDistAlongFilamentStatWorking,
                                              vSpotsStatUnits, vSpotsStatFactors,
                                              vSpotsStatFactorName, vSpotsvIds)
    
    
    ###############################################################################
    #After each Filament
        if vOptionFilamentCloseToSpots==1:
    
    #Find the number of spots within boundingbox of filament
            wTestX = np.where((np.array(vSpotsColocPositionsXYZ)[:,0] < zRandomLimitsMax[0]) &
                                     (np.array(vSpotsColocPositionsXYZ)[:,0] > zRandomLimitsMin[0]))[0].tolist()
            wTestY = np.where((np.array(vSpotsColocPositionsXYZ)[:,1] < zRandomLimitsMax[1]) &
                                     (np.array(vSpotsColocPositionsXYZ)[:,1] > zRandomLimitsMin[1]))[0].tolist()
            wTestZ = np.where((np.array(vSpotsColocPositionsXYZ)[:,2] < zRandomLimitsMax[2]) &
                                     (np.array(vSpotsColocPositionsXYZ)[:,2] > zRandomLimitsMin[2]))[0].tolist()
            xNumberRandomSpots = len(np.intersect1d(np.intersect1d(wTestX,wTestY),wTestZ))
    
            #Creaet Random Spots in the bounding box
            zRandomSpots=[]
            for j in range (10): #loop ten times
            #Create Random SPots in the bounding box
                zRandomSpots=[]
                for i in range(3):
                    # zRandomSpots.append(np.random.uniform(low=zRandomLimitsMin[i], high=zRandomLimitsMax[i], size= np.shape(vSpotsColocPositionsXYZ)[0]))
                    zRandomSpots.append(np.random.uniform(low=zRandomLimitsMin[i], high=zRandomLimitsMax[i], size= xNumberRandomSpots))
                zRandomSpots=np.transpose(np.array(zRandomSpots))
    
                wSpotToFilamentDistanceArray = cdist(zRandomSpots,vAllSegmentsPerFilamentPositionsWorkingInserts)
                #per dendrite segment - dista of each spot to working dendrite segment
                wShortestDistanceToSegment=wSpotToFilamentDistanceArray.min(axis=1)
                wShortestDistanceToSegment[wShortestDistanceToSegment<0]=0
                #SpotIndex for those the are less than threshold per dendrite segment
                wSpotsIndexPerSegment = [i for i,val in enumerate(wShortestDistanceToSegment)
                                          if val<=vOptionFilamentSpotThreshold]
                wNumberRandomSpotColocPerFilament.append(len(wSpotsIndexPerSegment))
    
            wNewStatRandomSpotColocPerFilament.append(mean(wNumberRandomSpotColocPerFilament))
    
    
    ###############################################################################
    # #Find Spot close to filament and measure distance along path to starting point
    # #Make spot position conect to filament as spine attachment point
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
                wNewSpotsOnFilament=[]
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
                    wSpotToAllFilamentDistanceArrayOriginal=cdist((np.array(wNewSpotsOnFilament)),vFilamentsXYZ)
                    wSpotBranchPointToAllFilamentDistanceArrayOriginal=cdist(wFilamentBranchPointsNEWCurrent,vFilamentsXYZ)
                    wSpotTerminalPointToAllFilamentDistanceArrayOriginal=cdist(wFilamentTerminalPointsNEWCurrent,vFilamentsXYZ)
    
                    wBranchIdxBlock = np.where(wSpotBranchPointToAllFilamentDistanceArrayOriginal==0)[1].tolist()
                    wTerminalIdxBlock = np.where(wSpotTerminalPointToAllFilamentDistanceArrayOriginal==0)[1].tolist()
    
                    test2=np.array(vFilamentsXYZ)[wBranchIdxBlock]
                    test1=np.array(vFilamentsXYZ)[wTerminalIdxBlock]
    
                    testpoints=np.array(vFilamentsXYZ)
                    testedges = np.array(vFilamentsEdges)
                    testtypes = np.array(vTypes)
    
                    # #Replace zeros with large number
                    wSpotToAllFilamentDistanceArrayOriginal[:,wBranchIdxBlock]=9999
                    wSpotToAllFilamentDistanceArrayOriginal[:,wTerminalIdxBlock]=9999
    
                    #Replace Starting point from FilamentXYZ with col of large 9999
                    # (np.where(np.array(vFilamentsXYZ) == wFilamentStartingPointsNEWCurrent[0]))[0][0]
                    wSpotToAllFilamentDistanceArrayOriginal[:,[(np.where(np.array(vFilamentsXYZ) == wFilamentStartingPointsNEWCurrent[0]))[0][0]]]=9999
                    # wSpotTerminalPointToAllFilamentDistanceArrayOriginal[:,[(np.where(np.array(vFilamentsXYZ) == wFilamentStartingPointsNEWCurrent[0]))[0][0]]]=9999
    
                    #For each spot, find index on filament of closest point
                    wSpotsFilamentClosestDistancePointIndex=np.argmin(wSpotToAllFilamentDistanceArrayOriginal, axis=1)
    
                    #loop for each spot within threshold
                    #append new filament and create list of new spots
                    for i in range (len(wNewSpotsOnFilament)):
                        wNewFilamentsXYZ.append(((np.array(wNewSpotsOnFilament))+.00001)[i].tolist())
                        wNewFilamentsRadius.append(1)
                        wNewFilamentsEdges.append([wSpotsFilamentClosestDistancePointIndex[i],len(vFilamentsRadius)+i])
                        wNewFilamentsTypes.append(1)
    
                    vNewFilament = vImarisApplication.GetFactory().CreateFilaments()
                    vNewFilament.AddFilament(wNewFilamentsXYZ, wNewFilamentsRadius, wNewFilamentsTypes, wNewFilamentsEdges, vFilamentsIndexT)
                    vNewFilament.SetBeginningVertexIndex(0, vBeginningVertex)
    
                    vNewFilamentSpineAttPtDistSET = vNewFilament.GetStatisticsByName('Spine Attachment Pt Distance')
                    vNewFilamentSpineAttPtPosXSET = vNewFilament.GetStatisticsByName('Spine Attachment Pt Position X')
    
                    vNewFilamentSpineAttPtDistValues = vNewFilamentSpineAttPtDistSET.mValues
                    vNewFilamentSpineAttPtDistIds = vNewFilamentSpineAttPtDistSET.mIds
                    vNewFilamentSpineAttPtPosXValues = vNewFilamentSpineAttPtPosXSET.mValues
                    vNewFilamentSpineAttPtPosXIds = vNewFilamentSpineAttPtPosXSET.mIds
                    mCount=0
                    mSkippedSpotsIds=[]
                    for i in range (len(wNewSpotsOnFilament)):
                        try:
                            wCompleteColocSpotDistAlongFilamentStatWorking.append(vNewFilamentSpineAttPtDistValues[vNewFilamentSpineAttPtDistIds.index(vNewFilamentSpineAttPtPosXIds[vNewFilamentSpineAttPtPosXValues.index(wNewFilamentsXYZ[wSpotsFilamentClosestDistancePointIndex[i]][0])])])
                        except:
                            #count missed spots per filament
                            mCount=mCount+1
                            mSkippedSpotsIds.append(i)
    ###########################
            else:
                vNewSpotsvNewSpotsAlongFilament = vImarisApplication.GetFactory().CreateSpots()
                vNewSpotsvNewSpotsAlongFilament.SetName('NO Colocalization ' + str(vSpots.GetName())+ '-- FilamentId:' + str(vFilamentIds[vFilamentCountActual-1]))
                vNewSpotsAnalysisFolder.AddChild(vNewSpotsvNewSpotsAlongFilament, -1)
    
            # wNewSpotsOnFilament=[1,2,3,4,5]
            # mSkippedSpotsIds=[2,4]
            wNewSpotsOnFilament = [i for j, i in enumerate(wNewSpotsOnFilament) if j not in mSkippedSpotsIds]
            wNewSpotsOnFilamentRadius = [i for j, i in enumerate(wNewSpotsOnFilamentRadius) if j not in mSkippedSpotsIds]
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
                vNewSpotsOnFilamentIndex=[vFilamentsIndexT+1]*len(wNewSpotsOnFilamentRadius)
                vSpotsvIds=list(range(len(wNewSpotsOnFilamentRadius)))
                vSpotsStatUnits=['um']*len(wNewSpotsOnFilamentRadius)
                vSpotsStatFactors=(['Spot']*len(wNewSpotsOnFilamentRadius), [str(x) for x in vNewSpotsOnFilamentIndex] )
                vSpotsStatFactorName=['Category','Time']
    
            #Combine distance measure per filament (spine and dendrite)
                if qIsSpines==True:
                    wCompleteFinalperFilament=np.column_stack((wCompleteShortestDistanceToFilament,wCompleteShortestDistanceToSpine))
                    #wCompleteFinalperFilament=wCompleteShortestDistanceToSpine
    
                else:
                    wCompleteFinalperFilament=wCompleteShortestDistanceToFilament
                #Collate each Filament together for closest distance to all spots
                if vFilamentCountActual==1:
                    wCompleteShortestDistanceToALLFilaments=wCompleteFinalperFilament
                else:
                    wCompleteShortestDistanceToALLFilaments=np.column_stack((wCompleteShortestDistanceToALLFilaments,wCompleteFinalperFilament))
    
    
                if len(wCompleteColocSpotDistAlongFilamentStatWorking) > 0:
                #     vColocSpotToFilamentDistanceOnly=wCompleteFinalperFilament.min(axis=1)[wSpotsAllIndexPerFilament].tolist()
                #     vSpotsStatNames=[' Shortest Distance to Filament']*len(wSpotsAllIndexPerFilament)
                #     vNewSpotsvNewSpotsAlongFilament.AddStatistics(vSpotsStatNames, vColocSpotToFilamentDistanceOnly,
                #                                   vSpotsStatUnits, vSpotsStatFactors,
                #                                   vSpotsStatFactorName, vSpotsvIds)
                # else:
                    vSpotsStatNames=[' Distance to Starting Point']*len(wNewSpotsOnFilamentRadius)
                    # vColocSpotToFilamentDistanceOnly=wCompleteFinalperFilament.min(axis=1)[wSpotsAllIndexPerFilament].tolist()
                    # wCompleteColocSpotDistAlongFilamentStatWorking = [i for j, i in enumerate(wCompleteColocSpotDistAlongFilamentStatWorking) if j not in mSkippedSpotsIds]
                    vNewSpotsvNewSpotsAlongFilament.AddStatistics(vSpotsStatNames, wCompleteColocSpotDistAlongFilamentStatWorking,
                                              vSpotsStatUnits, vSpotsStatFactors, vSpotsStatFactorName, vSpotsvIds)
    
                    # vSpotsStatNames=[' Shortest Distance to Filament']*len(vColocSpotToFilamentDistanceOnly)
                    # vNewSpotsvNewSpotsAlongFilament.AddStatistics(vSpotsStatNames, vColocSpotToFilamentDistanceOnly,
                    #                               vSpotsStatUnits, vSpotsStatFactors,
                    #                               vSpotsStatFactorName, vSpotsvIds)
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
                        # vNewSpotsDendrites.SetVisible(0)
                        vNewSpotsDendritesFolder.AddChild(vNewSpotsDendrites, -1)
    
                        #Create new Angle statistics
                        vSpotStatIds=list(range(len(vSegmentRadiusWorking)))
                        vSpotStatUnits=['um']*(len(vSegmentRadiusWorking))
                        vSpotsTimeIndex=[vFilamentsIndexT+1]*len(vSegmentRadiusWorking)
                        vSpotStatFactors=(['Spot']*len(vSegmentRadiusWorking), [str(x) for x in vSpotsTimeIndex] )
                        vSpotStatFactorName=['Category','Time']
                        vSpotStatNames=[' Tortuosity Angle']*(len(vSegmentRadiusWorking))
                        vNewSpotsDendrites.AddStatistics(vSpotStatNames, vNewStatAnglesPerCurrentFilamentSpot,
                                              vSpotStatUnits, vSpotStatFactors,
                                              vSpotStatFactorName, vSpotStatIds)
                        vSpotStatNames=[' Tortuosity Angle Mean3']*(len(vSegmentRadiusWorking))
                        vNewSpotsDendrites.AddStatistics(vSpotStatNames, vNewStatAnglesPerCurrentFilamentSpotMean,
                                              vSpotStatUnits, vSpotStatFactors,
                                              vSpotStatFactorName, vSpotStatIds)
    
                    else:
                        if qIsSpines==True:#test second loop if spines exist, if not do not make spine spots object
                            vNewSpotsSpines.Set(vSegmentPositionsWorking, vTimeIndex, vSegmentRadiusWorking)
                            zRandomColor=((random.uniform(0, 1)) * 256 * 256 * 256 )
                            vNewSpotsSpines.SetColorRGBA(zRandomColor)
                            vNewSpotsSpines.SetName(str(vFilaments.GetName())+" Spine_ID:"+ str(vFilamentIds[vFilamentCountActual-1]))
                            vNewSpotsSpines.SetVisible(0)
                            vNewSpotsSpinesFolder.AddChild(vNewSpotsSpines, -1)
    
                    #After the last Spot creation Place the folders
                    if aFilamentIndex+1==vNumberOfFilaments-len(zEmptyfilaments):
                        vImarisApplication.GetSurpassScene().AddChild(vNewSpotsDendritesFolder, -1)
                        if qIsSpines == True:
                            vImarisApplication.GetSurpassScene().AddChild(vNewSpotsSpinesFolder, -1)
    
    
    ###############################################################################
    ###############################################################################
    #Calculate Convexhull and Delauney 2d and 3D
    #convert xyz position into closest pixel coordinates
        wConversionX = (vDataMax[0]-vDataMin[0])/vDataSize[0]
        wConversionY = (vDataMax[1]-vDataMin[1])/vDataSize[1]
        wConversionZ = (vDataMax[2]-vDataMin[2])/vDataSize[2]
    
        if vOptionConvexHull == 1:
    
            if vOptionConvexHullwithTerminal == 1:
                vFilamentXYZPointsConvexHullPixelPos = np.copy(wFilamentTerminalPointsNEWCurrent)
                vFilamentXYZPointsConvexHullPixelPos = np.vstack([vFilamentXYZPointsConvexHullPixelPos, wFilamentStartingPointsNEWCurrent])
                vFilamentsXYZArray = np.array(vFilamentXYZPointsConvexHullPixelPos)
            else:
                vFilamentsXYZArray = np.array(vFilamentsXYZ)
                vFilamentXYZPointsConvexHullPixelPos = np.copy(vFilamentsXYZArray)
    
            vFilamentXYZPointsConvexHullPixelPos[:,0] = (vFilamentXYZPointsConvexHullPixelPos[:,0]-vDataMin[0])/wConversionX
            vFilamentXYZPointsConvexHullPixelPos[:,1] = (vFilamentXYZPointsConvexHullPixelPos[:,1]-vDataMin[1])/wConversionY
            vFilamentXYZPointsConvexHullPixelPos[:,2] = (vFilamentXYZPointsConvexHullPixelPos[:,2]-vDataMin[2])/wConversionZ
            vFilamentXYZPointsConvexHullPixelPos = vFilamentXYZPointsConvexHullPixelPos.astype(int)
    
            vFilamentXYZPointsConvexHullPixelPos[:,0][np.where(vFilamentXYZPointsConvexHullPixelPos[:,0] == vDataSize[0])[0]]=vDataSize[0]-1
            vFilamentXYZPointsConvexHullPixelPos[:,1][np.where(vFilamentXYZPointsConvexHullPixelPos[:,1] == vDataSize[1])[0]]=vDataSize[1]-1
            # vFilamentXYZPointsConvexHullPixelPos[:,2][np.where(vFilamentXYZPointsConvexHullPixelPos[:,2] == vDataSize[2])[0]]=vDataSize[2]-1
    
            if vDataSize[2] == 1:
                #for 2Dstat calculation
                vFilamentsXYZArray2D = np.delete(vFilamentsXYZArray,2,1)
                wFilamentConvexHullCurrentStat = ConvexHull(vFilamentsXYZArray2D)
    
                vFilamentXYZPointsCurrentPixelPos2D = np.delete(vFilamentXYZPointsConvexHullPixelPos,2,1)
                wFilamentConvexHullCurrent = ConvexHull(vFilamentXYZPointsCurrentPixelPos2D)
                wFilamentConvexHullDelaunyCurrent = Delaunay(vFilamentXYZPointsCurrentPixelPos2D[wFilamentConvexHullCurrent.vertices])
    
            else: #for 3Dstat calculation
                wFilamentConvexHullCurrentStat = ConvexHull(vFilamentsXYZArray)
    
        #Calculate Dendritic Field Size (2D and 3D) and surface area...from ConvexHull
            wNewStatConvexHullVolumePerFilament.append(wFilamentConvexHullCurrentStat.volume)
            wNewStatConvexHullAreaPerFilament.append(wFilamentConvexHullCurrentStat.area)
    
            progress_bar2['value'] = int((aFilamentIndex+.5)/(vNumberOfFilaments-len(zEmptyfilaments))*100) #  % out of 100
            master.update()
    
        #create new Dataset full volume
            vDataSet = vImarisApplication.GetFactory().CreateDataSet()
            vDataSet.Create(vType, vDataSize[0], vDataSize[1], vDataSize[2], 1, 1)
            vDataSet.SetExtendMinX(vDataMin[0])
            vDataSet.SetExtendMinY(vDataMin[1])
            vDataSet.SetExtendMinZ(vDataMin[2])
            vDataSet.SetExtendMaxX(vDataMax[0])
            vDataSet.SetExtendMaxY(vDataMax[1])
            vDataSet.SetExtendMaxZ(vDataMax[2])
            vDataSet.SetTimePoint(vFilamentsIndexT, vFilamentTimepoint)
    
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
                vDataSet.SetDataSubVolumeAs1DArrayFloats(vSlice.tolist(),
                                                0,
                                                0,
                                                vIndexZ,
                                                0,
                                                0,
                                                vDataSize[0],
                                                vDataSize[1],
                                                1)
            else:
                #create tuple and flip so that Z is first column, follow by x ,then Y
                points = tuple((vFilamentXYZPointsConvexHullPixelPos[:,2],
                               vFilamentXYZPointsConvexHullPixelPos[:,0],
                               vFilamentXYZPointsConvexHullPixelPos[:,1]))
                image = np.zeros((vDataSize[2],vDataSize[0],vDataSize[1]))
    
                #Replace Points in blank image for COnvexHull calculation
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
    
                #loop each Z and creat Convexhull mask channel
                for vIndexZ in range (vDataSize[2]):
                    vSlice = vVolume[vIndexZ].flatten('F')
                    #Add mask to DataSet
                    vDataSet.SetDataSubVolumeAs1DArrayFloats(vSlice.tolist(),
                                                    0,
                                                    0,
                                                    vIndexZ,
                                                    0,
                                                    0,
                                                    vDataSize[0],
                                                    vDataSize[1],
                                                    1)
                    progress_bar3['value'] = int((vIndexZ)/vDataSize[2]*100) #  % out of 100
                    master.update()
    
    
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
    
    
    ###############################################################################
    #After Each Filament collate SegmentIds fro dendrites and spines
        wCompleteDendriteSegmentIds.extend(wDendriteSegmentIds)
        wCompleteSpineSegmentIds.extend(wSpineSegmentIds)
        wCompleteFilamentTimeIndex.extend([vFilamentsIndexT+1]*vFilamentCountActual)
        wCompleteDendriteTimeIndex.extend([vFilamentsIndexT+1]*len(wDendriteSegmentIds))
        wCompleteSpineTimeIndex.extend([vFilamentsIndexT+1]*len(wSpineSegmentIds))
    
    ###############################################################################
        progress_bar2['value'] = int((aFilamentIndex+1)/(vNumberOfFilaments-len(zEmptyfilaments))*100) #  % out of 100
        master.update()
    master.destroy()
    master.mainloop()
    ###############################################################################
    ###############################################################################
    ###############################################################################
    #After last Filament in Bouton Statistics
    #create new Bouton spot object and Filament Statistic
    
    vFilamentStatvIds=list(range(len(vAllFilamentDendriteLength)))
    vFilamentStatUnits=['']*(len(vAllFilamentDendriteLength))
    
    if aVersionValue == 10:
        vFilamentStatFactors=(['Segment']*len(vAllFilamentDendriteLength), [str(x) for x in wCompleteDendriteTimeIndex] )
    else:
        vFilamentStatFactors=(['Dendrite']*len(vAllFilamentDendriteLength), [str(x) for x in wCompleteDendriteTimeIndex] )
    
    
    vFilamentStatFactorName=['Category','Time']
    if vOptionFilamentBoutonDetection==1:
    #     if vAllNewSpotsBoutonsRadius==[]:
    #         vNewSpotsBoutons.SetName(' NO Boutons Found')
    #         vNewSpotsBoutonsTimeIndex=[vFilamentsIndexT]*len(vBoutonRadiusAll)
    #         vNewSpotsBoutons.Set(vBoutonPositionAll, vNewSpotsBoutonsTimeIndex, vBoutonRadiusAll)
    #         vNewSpotsAnalysisFolder.AddChild(vNewSpotsBoutons, -1)
    #     else:
    #         vNewSpotsBoutonsTimeIndex=[vFilamentsIndexT]*len(vBoutonRadiusAll)
    #         vNewSpotsBoutons.SetName('Detected Varicosities (Boutons)')
    #         vNewSpotsBoutons.SetColorRGBA(18000)
    #         vNewSpotsBoutons.Set(vBoutonPositionAll, vNewSpotsBoutonsTimeIndex, vBoutonRadiusAll)
    #         vNewSpotsAnalysisFolder.AddChild(vNewSpotsBoutons, -1)
    
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
    #Tortuosity
    vFilamentStatNames=[' Dendrite Tortuosity ']*(len(vAllFilamentDendriteLengthIds))
    vFilaments.AddStatistics(vFilamentStatNames, vNewStatCompleteTortuosityPerSegment,
                          vFilamentStatUnits, vFilamentStatFactors,
                          vFilamentStatFactorName, wCompleteDendriteSegmentIds)
    
    vNewStatCompleteTortuosityPerSegmentSumPerum=[vNewStatCompleteTortuosityPerSegmentSum[i] / vAllFilamentDendriteLength[i] for i in range(len(vAllFilamentDendriteLength))]
    vFilamentStatNames=[' Dendrite Tortuosity Sum ']*(len(vAllFilamentDendriteLengthIds))
    vFilaments.AddStatistics(vFilamentStatNames, vNewStatCompleteTortuosityPerSegmentSum,
                          vFilamentStatUnits, vFilamentStatFactors,
                          vFilamentStatFactorName, wCompleteDendriteSegmentIds)
    
    
    
    
    ###############################################################################
    if vOptionDendriteToDendriteContact==1:
        vFilamentStatvIds=list(range(len(vAllFilamentDendriteLength)))
        vFilamentStatUnits=['']*(len(vAllFilamentDendriteLength))
        # vFilamentStatFactors=(['Dendrite']*len(vAllFilamentDendriteLength), [str(x) for x in wCompleteDendriteTimeIndex] )
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
        # vFilamentStatFactors=(['Dendrite']*len(vAllFilamentDendriteLength), [str(x) for x in wCompleteDendriteTimeIndex] )
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
    #     #ADD Spot to Filament Distance statistic.
    #     vSpotsStatUnits=['um']*len(vSpotsColocRadius)
    #     vSpotsStatFactors=(['Spot']*len(vSpotsColocRadius), [str(x) for x in [i+1 for i in vSpotsColocTimeIndices]] )
    #     vSpotsStatFactorName=['Category','Time']
    #     vSpotsStatNames=[' Shortest Distance to Filament']*len(vSpotsColocRadius)
    #     vSpots.SetName(vSpots.GetName()+' -- Analyzed')
    
    #     wCompleteShortestDistanceStat=[]
    #     # Get the minimum values of each column i.e. along axis 0
    #     if SegmentCountALL>1:
    #         wCompleteShortestDistanceStat = np.amin(wCompleteShortestDistanceToALLFilaments, axis=1).tolist()
    #     else:
    #         wCompleteShortestDistanceStat=wCompleteShortestDistanceToALLFilaments.tolist()
    #     vSpots.AddStatistics(vSpotsStatNames, wCompleteShortestDistanceStat,
    #                                   vSpotsStatUnits, vSpotsStatFactors,
    #                                   vSpotsStatFactorName, vSpotsId)
    
    ###########
        #ADD Spot number&Density to Filament Distance statistic.
        vFilamentStatvIds=list(range(len(wCompleteDendriteSegmentIds)))
        vFilamentStatUnits=['']*(len(wCompleteDendriteSegmentIds))
        # vFilamentStatFactors=(['Dendrite']*len(wCompleteDendriteSegmentIds), [str(x) for x in wCompleteDendriteTimeIndex] )
        vFilamentStatFactorName=['Category','Time']
        vFilamentStatNames=[' Dendrite Coloc Number Spots']*(len(wCompleteDendriteSegmentIds))
        vFilaments.AddStatistics(vFilamentStatNames, wNumberOfSpotsPerDendrite,
                                      vFilamentStatUnits, vFilamentStatFactors,
                                      vFilamentStatFactorName, wCompleteDendriteSegmentIds)
    
        vNewStatSpotColocDensityPerDendrite=[(wNumberOfSpotsPerDendrite[i]*10) / vAllFilamentDendriteLength[i] for i in range(len(vAllFilamentDendriteLength))]
        vFilamentStatNames=[' Dendrite Coloc Spot Density (per 10um)']*(len(wCompleteDendriteSegmentIds))
        vFilaments.AddStatistics(vFilamentStatNames, vNewStatSpotColocDensityPerDendrite,
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
    
    vFilamentStatNames=[' Filament - Dendrite Regularity Index BranchPoint']*vFilamentCountActual
    vFilaments.AddStatistics(vFilamentStatNames, zAllFilamentsRegularityIndexBP,
                              vFilamentStatUnits, vFilamentStatFactors,
                              vFilamentStatFactorName, vFilamentIds)
    vFilamentStatNames=[' Filament - Dendrite Regularity Index TerminalPoint']*vFilamentCountActual
    vFilaments.AddStatistics(vFilamentStatNames, zAllFilamentsRegularityIndexTP,
                              vFilamentStatUnits, vFilamentStatFactors,
                              vFilamentStatFactorName, vFilamentIds)
    vFilamentStatNames=[' Filament - Tortuosity']*vFilamentCountActual
    vFilaments.AddStatistics(vFilamentStatNames, vNewStatTortuosityPerFilament,
                              vFilamentStatUnits, vFilamentStatFactors,
                              vFilamentStatFactorName, vFilamentIds)
    ########################
    #Filament Dendrite Complexity Index
    vFilamentStatNames=[' Filament - Dendrite Complexity Index (DCI)']*vFilamentCountActual
    vFilaments.AddStatistics(vFilamentStatNames, wFilamentComplexityIndexComplete,
                          vFilamentStatUnits, vFilamentStatFactors,
                          vFilamentStatFactorName, vFilamentIds)
    
    if vOptionConvexHull == 1:
    
        if vDataSize[2]==1:
            vFilamentStatNames=[' Filament - Dendritic Field Area (um^2)(convexhull)']*vFilamentCountActual
        else:
            vFilamentStatNames=[' Filament - Dendritic Field Volume (um^3)(convexhull)']*vFilamentCountActual
        vFilaments.AddStatistics(vFilamentStatNames, wNewStatConvexHullVolumePerFilament,
                              vFilamentStatUnits, vFilamentStatFactors,
                              vFilamentStatFactorName, vFilamentIds)
        if vDataSize[2]==1:
            vFilamentStatNames=[' Filament - Dendritic Field Perimeter (um)(convexhull)']*vFilamentCountActual
        else:
            vFilamentStatNames=[' Filament - Dendritic Field SurfaceArea (um^2)(convexhull)']*vFilamentCountActual
        vFilaments.AddStatistics(vFilamentStatNames, wNewStatConvexHullAreaPerFilament,
                              vFilamentStatUnits, vFilamentStatFactors,
                              vFilamentStatFactorName, vFilamentIds)
    
    if vOptionTerminalPoints == 1:
    ########################
        #Mean distance to Terminal Point
        vFilamentStatNames=[' Filament - TerminalPoint Mean Distance to soma ']*vFilamentCountActual
        vFilaments.AddStatistics(vFilamentStatNames, vNewStatCompleteFilamentTerminalPointDistToSomaMean,
                              vFilamentStatUnits, vFilamentStatFactors,
                              vFilamentStatFactorName, vFilamentIds)
        ########################
        #Max distance to Terminal Point
        vFilamentStatNames=[' Filament - TerminalPoint Max Distance to soma ']*vFilamentCountActual
        vFilaments.AddStatistics(vFilamentStatNames, vNewStatCompleteFilamentTerminalPointDistToSomaMax,
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
        vFilamentStatNames=[' Filament Number Coloc Random Spot Distribution']*vFilamentCountActual
        vFilaments.AddStatistics(vFilamentStatNames, wNewStatRandomSpotColocPerFilament,
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
    
    
    ###################################
    #Create Branch points for all filaments and create labels for branch point classification
    if vOptionBranchPoints == 1 and vOptionMergePoints == 1:
        #Create Spots for all Branch Points
        vNewSpotsBranchPointsPerFilamentComplete = vImarisApplication.GetFactory().CreateSpots()
        vNewSpotsBranchPointsPerFilamentComplete.Set(wFilamentBranchPointsComplete,
                              [vFilamentsIndexT]*len(wFilamentBranchPointsComplete),
                              [1]*len(wFilamentBranchPointsComplete))
        vNewSpotsBranchPointsPerFilamentComplete.SetName(' BranchPoints - ALL:'+ str(vFilamentIds[vFilamentCountActual-1]))
        zRandomColor=(random.uniform(0, 1) * 256 * 256 * 256 )
        vNewSpotsBranchPointsPerFilamentComplete.SetColorRGBA(zRandomColor)#Set Random color
        vSpotFilamentPoints.AddChild(vNewSpotsBranchPointsPerFilamentComplete, -1)
        vImarisApplication.GetSurpassScene().AddChild(vSpotFilamentPoints, -1)
    ###########
        #Add new stat to each branch point
        vSpotsTimeIndex=[vFilamentsIndexT+1]*len(wCompleteBranchPointsDistAlongFilamentStatALL)
        vSpotsvIds=list(range(len(wCompleteBranchPointsDistAlongFilamentStatALL)))
        vSpotsStatUnits=['um']*len(wCompleteBranchPointsDistAlongFilamentStatALL)
        vSpotsStatFactors=(['Spot']*len(wCompleteBranchPointsDistAlongFilamentStatALL), [str(x) for x in vSpotsTimeIndex] )
        vSpotsStatFactorName=['Category','Time']
        vSpotsStatNames=[' Distance to soma from Branch Point']*len(wCompleteBranchPointsDistAlongFilamentStatALL)
        vNewSpotsBranchPointsPerFilamentComplete.AddStatistics(vSpotsStatNames, wCompleteBranchPointsDistAlongFilamentStatALL,
                                      vSpotsStatUnits, vSpotsStatFactors,
                                      vSpotsStatFactorName, vSpotsvIds)
    
    
        #Create Labels for the branch points
         #Set Sholl sphere Labels for each filament
        vLabelIndices=list(range(len(wFilamentBranchPointsComplete)))
        wLabelList=[]
        wLabelName = ('Arborization','Continuation', 'Termination')
        for i in range (3):
            wLabelList=[]
            for j in range (len(vLabelIndices)):
                if vNodeTypesComplete[j] == i:
                    # vLabelCreate = vFactory.CreateObjectLabel(vLabelIndices[j],
                    #                                       'Classified Nodes',
                    #                                       str(wLabelName[vNodeTypesComplete[j]]))
                    vLabelCreate = vFactory.CreateObjectLabel(vLabelIndices[j],
                                                          'Classified Nodes',
                                                          'FilamentId-' + str(vNodeFilamentIdsComplete[j]) + '--' + str(wLabelName[vNodeTypesComplete[j]]))
                    wLabelList.append(vLabelCreate)
            vNewSpotsBranchPointsPerFilamentComplete.SetLabels(wLabelList)
    
        vNewSpotsBranchPointsPerFilamentComplete.SetLabels(wLabelListBranchPoints)
    
    
    if vOptionTerminalPoints == 1 and vOptionMergePoints == 1:
        vNewSpotsTerminalPointsPerFilamentComplete = vImarisApplication.GetFactory().CreateSpots()
        vNewSpotsTerminalPointsPerFilamentComplete.Set(wFilamentTerminalPointsComplete,
                              [vFilamentsIndexT]*len(wFilamentTerminalPointsComplete),
                              [1]*len(wFilamentTerminalPointsComplete))
        vNewSpotsTerminalPointsPerFilamentComplete.SetName(' TerminalPoints - ALL:'+ str(vFilamentIds[vFilamentCountActual-1]))
        zRandomColor=(random.uniform(0, 1) * 256 * 256 * 256 )
        vNewSpotsTerminalPointsPerFilamentComplete.SetColorRGBA(zRandomColor)#Set Random color
        vSpotFilamentPoints.AddChild(vNewSpotsTerminalPointsPerFilamentComplete, -1)
        vImarisApplication.GetSurpassScene().AddChild(vSpotFilamentPoints, -1)
    
    ############
        #Add new stat to each terminal point
        vSpotsTimeIndex=[vFilamentsIndexT+1]*len(wCompleteTerminalPointsDistAlongFilamentStatALL)
        vSpotsvIds=list(range(len(wCompleteTerminalPointsDistAlongFilamentStatALL)))
        vSpotsStatUnits=['um']*len(wCompleteTerminalPointsDistAlongFilamentStatALL)
        vSpotsStatFactors=(['Spot']*len(wCompleteTerminalPointsDistAlongFilamentStatALL), [str(x) for x in vSpotsTimeIndex] )
        vSpotsStatFactorName=['Category','Time']
        vSpotsStatNames=[' Distance to soma from Branch Point']*len(wCompleteTerminalPointsDistAlongFilamentStatALL)
        vNewSpotsTerminalPointsPerFilamentComplete.AddStatistics(vSpotsStatNames, wCompleteTerminalPointsDistAlongFilamentStatALL,
                                      vSpotsStatUnits, vSpotsStatFactors,
                                      vSpotsStatFactorName, vSpotsvIds)
        ############
        #Create Labels for the terminal points
        vNewSpotsTerminalPointsPerFilamentComplete.SetLabels(wLabelListTerminalPoints)
    
    
    
    ###################################################################################
    ###################################################################################
    #Apply SpotAnalysis folder to Surpass scene
    if vOptionFilamentCloseToSpots==1 or vOptionFilamentBoutonDetection==1:
        vImarisApplication.GetSurpassScene().AddChild(vNewSpotsAnalysisFolder, -1)
    
    # if vOptionFilamentBoutonDetection==1 or vOptionFilamentCloseToSpots==1:
    vFilaments.SetName(vFilaments.GetName()+' -- Analyzed')
    vImarisApplication.GetSurpassScene().AddChild(vFilaments, -1)
    
    if vOptionFilamentCloseToSpots==1:
        vSpots.SetVisible(0)
    
    ##############################################################################
    #Add Convex Hull surfaces
    if vOptionConvexHull == 1:
        vSurfaceHull.SetName('Filament ConvexHull Surfaces')
        vSurfaceHull.SetColorRGBA(vFilaments.GetColorRGBA())
    
        # #Add new surface convex hull folder
        vSurfaceConvexHull.AddChild(vSurfaceHull, -1)
        vImarisApplication.GetSurpassScene().AddChild(vSurfaceConvexHull, -1)
    
        #Create Labels for Convex hull surfaces to match filament ID
        vLabelIndices=list(range(vFilamentCountActual))
        wLabelList=[]
        for j in range (len(vLabelIndices)):
            vLabelCreate = vFactory.CreateObjectLabel(vLabelIndices[j],
                                                      'FilamentIds',
                                                      str(vFilamentIds[j]))
            wLabelList.append(vLabelCreate)
        vSurfaceHull.SetLabels(wLabelList)
    ##############################################################################
    
    # # #Adjust Visibility
    # if vOptionFilamentToSpots==1 and vOptionFilamentCloseToSpots==1 or vOptionFilamentBoutonDetection==1:
    #     vNewSpotsDendritesFolder.SetVisible(0)
    #     vNewSpotsSpinesFolder.SetVisible(0)
    
    if vNumberOfFilaments>50 and qisVisible=='yes':
        vImarisApplication.SetVisible(1)
    
    # except:
    #     vImarisApplication.SetVisible(1)
    
    
    
