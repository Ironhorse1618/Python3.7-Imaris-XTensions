#Surface-Surface Overlap
#
#Written by Matthew J. Gastinger
#June 2020
#
    # <CustomTools>
    #     <Menu>
    #         <Submenu name="Surfaces Functions">
    #             <Item name="Coloc - Pearson Coeffient per Surface" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Surface_Surface_Correlation(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSurfaces">
    #             <Item name="Coloc - Pearson Coeffient per Surface" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Surface_Surface_Correlation(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #     </SurpassTab>
    # </CustomTools>

#Description
#


import ImarisLib
import numpy as np
import scipy
import scipy.stats

# GUI imports
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog

aImarisId=0
def XT_MJG_Surface_Surface_Correlation(aImarisId):
    
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
    
    # ############################################################################
    # window = tk.Tk()
    # window.title('Surface Overlap')
    # window.geometry('260x55')
    # window.attributes("-topmost", True)
    
    # w = window.winfo_reqwidth()
    # h = window.winfo_reqheight()
    # ws = window.winfo_screenwidth()
    # hs = window.winfo_screenheight()
    # x = (ws/2) - (w/2)
    # y = (hs/2) - (h/2)
    # window.geometry('+%d+%d' % (x, y))
    
    # def CreateSurface():
    #     global vSmoothingFactor
    #     if (var1.get() == 0):
    #         vSmoothingFactor=0
    #         window.destroy()
    #     else:
    #         vSmoothingFactor=[float(Entry1.get())]
    #         window.destroy()
    
    # var1 = tk.IntVar(value=0)
    # tk.Checkbutton(window, text='Smoothing',
    #                 variable=var1, onvalue=1, offvalue=0).grid(row=0, column=0, padx=40,sticky=W)
    # tk.Label(window, text='um').grid(row=0,column=1,padx=45)
    
    # Entry1=Entry(window,justify='center',width=4)
    # Entry1.grid(row=0, column=1, sticky=W)
    # Entry1.insert(0, str(vDefaultSmoothingFactor))
    
    # btn = Button(window, text="Create Overlap Surface",highlightbackground='blue',command=CreateSurface)
    # btn.grid(column=0, row=2, sticky=E)
    
    # window.mainloop()
    
    #########################################################
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
    
    # #####################################################
    # #Making the Listbox for the Surpass menu
    # main = Tk()
    # main.title("Surpass menu")
    # main.geometry("+50+150")
    # main.attributes("-topmost", True)
    
    # #################################################################
    # #Set input in center on screen
    # # Gets the requested values of the height and widht.
    # windowWidth = main.winfo_reqwidth()
    # windowHeight = main.winfo_reqheight()
    # # Gets both half the screen width/height and window width/height
    # positionRight = int(main.winfo_screenwidth()/2 - windowWidth/2)
    # positionDown = int(main.winfo_screenheight()/2 - windowHeight/2)
    # # Positions the window in the center of the page.
    # main.geometry("+{}+{}".format(positionRight, positionDown))
    # ##################################################################
    # names = StringVar()
    # names.set(NamesSurfaces)
    # lstbox = Listbox(main, listvariable=names, selectmode=MULTIPLE, width=20, height=10)
    # lstbox.grid(column=0, row=0, columnspan=2)
    # def select():
    #     global ObjectSelection
    #     ObjectSelection = list()
    #     selection = lstbox.curselection()
    #     for i in selection:
    #         entrada = lstbox.get(i)
    #         ObjectSelection.append(entrada)
    # #Test for the correct number selected
    #     if len(ObjectSelection)!=2:
    #         messagebox.showerror(title='Surface menu',
    #                           message='Please Select 2 surfaces')
    #         main.mainloop()
    #     else:
    #         main.destroy()
    
    # btn = Button(main, text="Choose 2 surfaces!", command=select)
    # btn.grid(column=1, row=1)
    # #Selects the top 2 items in the list
    # lstbox.selection_set(0,1)
    # main.mainloop()
    
    ####################################################################
    # # get the Selected surfaces Indices in Surpass for specific
    # vDataItem=vScene.GetChild(NamesSurfaceIndex[(NamesSurfaces.index( ''.join(map(str, ObjectSelection[0]))))])
    # vSurfaces1=vImarisApplication.GetFactory().ToSurfaces(vDataItem)
    
    # vDataItem=vScene.GetChild(NamesSurfaceIndex[(NamesSurfaces.index( ''.join(map(str, ObjectSelection[1]))))])
    # vSurfaces2=vImarisApplication.GetFactory().ToSurfaces(vDataItem)
    
    #clone Dataset
    # vDataSet = vImage.Clone()
    
    ########################
    ########################
    
    # Create the master object
    master = tk.Tk()
    # Create a progressbar widget
    progress_bar = ttk.Progressbar(master, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    # And a label for it
    label_1 = tk.Label(master, text="Colocalization analysis")
    # Use the grid manager
    label_1.grid(row=0, column=0,pady=10)
    progress_bar.grid(row=0, column=1)
    master.geometry('270x50')
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
    
    
    
    #Test retrieval
    vSurfaces = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
    vNumberOfSurfaces = vSurfaces.GetNumberOfSurfaces()
    
    # #add additional channel
    # vDataSet.SetSizeC(vSizeC+1)
    # vLastChannel=vSizeC#newest channel added (starting from "0")
    
    
    #Probably need to create dialog to slect specific channels
    vChannela = 0
    vChannelb = 1
    vIndexZ=23
    zPearsonCoefficentperSurfaceFinal = []
    zPearsonCoefficentScipyPearson = []
    # zPearsonCoefficentScipySpearmanr = []
    # zPearsonCoefficentScipyKendalltau = []
    
    vAllTimeIndices = []
    for vNextSurface in range (vNumberOfSurfaces):
        vSurfaceMask = vSurfaces.GetSingleMask(vNextSurface,vExtendMin[0],vExtendMin[1],vExtendMin[2],
                                            vExtendMax[0],vExtendMax[1],vExtendMax[2],
                                            vImageSize[0], vImageSize[1],vImageSize[2])
        zChannelaMaskFinal = []
        zChannelbMaskFinal = []
        for vIndexZ in range (0,vImageSize[2]):
            #Grab slice dtaa from the raw dataset channels
            zChannela = np.array(vImage.GetDataSubVolumeAs1DArrayFloats(0, 0, vIndexZ,
                                                               vChannela, 0,
                                                         vImageSize[0], vImageSize[1],1))
            zChannelb = np.array(vImage.GetDataSubVolumeAs1DArrayFloats(0, 0, vIndexZ,
                                                               vChannelb, 0,
                                                         vImageSize[0], vImageSize[1],1))
            #Mask Individual surface Signal == 1, background==0
            zSurfaceMask = np.array(vSurfaceMask.GetDataSubVolumeAs1DArrayFloats(0,0,vIndexZ,0,0,
                                                              vImageSize[0], vImageSize[1],1))
    
            #test is the slice has any part of surface mask
            if np.any(zSurfaceMask) == False:
                continue
            #Set non-Mask pixels to zero
            zChannelaMask = [zChannela[i] * zSurfaceMask[i] for i in range(len(zChannela))]
            zChannelaMaskFinal.extend([i for i in zChannelaMask if i != 0])
            zChannelbMask = [zChannelb[i] * zSurfaceMask[i] for i in range(len(zChannelb))]
            zChannelbMaskFinal.extend([i for i in zChannelbMask if i != 0])
    
        vAllTimeIndices.append(vSurfaces.GetTimeIndex(vNextSurface))
        zPearsonCoefficientSurface = np.corrcoef(np.array(zChannelaMaskFinal), np.array(zChannelbMaskFinal))
        zPearsonCoefficentperSurfaceFinal.append(zPearsonCoefficientSurface[0][1])
    
    
        zPearsonCoefficientSurfaceScipy = scipy.stats.pearsonr(zChannelaMaskFinal, zChannelbMaskFinal)
        # zPearsonCoefficientSurfaceScipy = scipy.stats.spearmanr(zChannelaMaskFinal, zChannelbMaskFinal)
        # zPearsonCoefficientSurfaceScipy = scipy.stats.kendalltau(zChannelaMaskFinal, zChannelbMaskFinal)
        zPearsonCoefficentScipyPearson.append(zPearsonCoefficientSurfaceScipy[0])
        # zPearsonCoefficentScipySpearmanr.append(zPearsonCoefficientSurfaceScipy[0])
        # zPearsonCoefficentScipyKendalltau.append(zPearsonCoefficientSurfaceScipy[0])
    
    
        progress_bar['value'] = int((vNextSurface+1)/vNumberOfSurfaces*100)
        master.update()
    
    master.destroy()
    master.mainloop()
    ##############################################################################
    ##############################################################################
    #Create statistics for indiviual surfaces
    vIndividualSurfaceIDs=vSurfaces.GetIds()
    vIndividualStatUnits=['um']*len(vIndividualSurfaceIDs)
    #Create Tuple list for each surface in time
    vSurfaceStatFactors=(['Surface']*len(vIndividualSurfaceIDs),
                  [str(e) for e in [i+1 for i in vAllTimeIndices]])
    vSurfaceStatFactorName=['Category','Time']
    ##############################################################################
    vSurfaceStatNames=[' Pearsons Coefficient']*len(vIndividualSurfaceIDs)
    vSurfaces.AddStatistics(vSurfaceStatNames, zPearsonCoefficentperSurfaceFinal,
                              vIndividualStatUnits, vSurfaceStatFactors,
                              vSurfaceStatFactorName, vIndividualSurfaceIDs)
    ##############################################################################
    vSurfaceStatNames=[' Pearsons Coefficient']*len(vIndividualSurfaceIDs)
    vSurfaces.AddStatistics(vSurfaceStatNames, zPearsonCoefficentScipyPearson,
                              vIndividualStatUnits, vSurfaceStatFactors,
                              vSurfaceStatFactorName, vIndividualSurfaceIDs)
    
    
