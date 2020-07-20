#Surface-Surface Overlap
#
#Written by Matthew J. Gastinger
#June 2020
#
    # <CustomTools>
    #     <Menu>
    #         <Submenu name="Surfaces Functions">
    #             <Item name="Surface-Surface Overlap" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Surface_Surface_OverlapFinal(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSurfaces">
    #             <Item name="urface-Surface Overlap" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Surface_Surface_OverlapFinal(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #     </SurpassTab>
    # </CustomTools>

#Description
#
#This XTension will mask each of 2 surface scenes.  It will find the voxels
#inside each surface that overlap with each other.  A new channel will be
#made, and a new surface generated from the overlapping regions.

import ImarisLib
#import numpy
# GUI imports

import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog

#aImarisId=0
def XT_MJG_Surface_Surface_OverlapFinal(aImarisId):
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
    root = Tk()
    root.withdraw()
    #Question = Toplevel(root) # (Manually put toplevel in front of root)
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('+%d+%d' % (x, y))
    #Smoothing or no smoothing for the Coloc result
    Smoothing = messagebox.askyesno('Surface Creation',
                            'Do you want to smooth the Overlap surface?')
    root.lift()

    #Set smoothing factor
    vSmoothingFactor=0
    if Smoothing==True:
        vSmoothingFactor = simpledialog.askfloat('Set Creation Parameters',
                                    'Smoothing Factor: ', initialvalue=vDefaultSmoothingFactor)
        root.lift()
    root.destroy()

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

    #####################################################
    #Making the Listbox for the Surpass menu
    main = Tk()
    main.title("Surpass menu")
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
    names.set(NamesSurfaces)
    lstbox = Listbox(main, listvariable=names, selectmode=MULTIPLE, width=20, height=10)
    lstbox.grid(column=0, row=0, columnspan=2)
    def select():
        global ObjectSelection
        ObjectSelection = list()
        selection = lstbox.curselection()
        for i in selection:
            entrada = lstbox.get(i)
            ObjectSelection.append(entrada)
    #Test for the correct number selected
        if len(ObjectSelection)!=2:
            messagebox.showerror(title='Surface menu',
                              message='Please Select 2 surfaces')
            main.mainloop()
        else:
            main.destroy()

    btn = Button(main, text="Choose 2 surfaces!", command=select)
    btn.grid(column=1, row=1)
    #Selects the top 2 items in the list
    lstbox.selection_set(0,1)
    main.mainloop()

    ####################################################################
    # get the Selected surfaces Indices in Surpass for specific
    vDataItem=vScene.GetChild(NamesSurfaceIndex[(NamesSurfaces.index( ''.join(map(str, ObjectSelection[0]))))])
    vSurfaces1=vImarisApplication.GetFactory().ToSurfaces(vDataItem)

    vDataItem=vScene.GetChild(NamesSurfaceIndex[(NamesSurfaces.index( ''.join(map(str, ObjectSelection[1]))))])
    vSurfaces2=vImarisApplication.GetFactory().ToSurfaces(vDataItem)

    #clone Dataset
    vDataSet = vImage.Clone()

    #Test retrieval
    # vNumberOfSurfaces1 = vSurfaces1.GetNumberOfSurfaces()
    # vNumberOfSurfaces2 = vSurfaces2.GetNumberOfSurfaces()

    #add additional channel
    vDataSet.SetSizeC(vSizeC+1)
    vLastChannel=vSizeC#newest channel added (starting from "0")

    #Generate surface mask for each surface over time
    for vTimeIndex in range (0,vSizeT):
        vSurfaces1Mask = vSurfaces1.GetMask(vExtendMin[0],vExtendMin[1],vExtendMin[2],
                                            vExtendMax[0],vExtendMax[1],vExtendMax[2],
                                            vImageSize[0], vImageSize[1],vImageSize[2],
                                            vTimeIndex)
        vSurfaces2Mask = vSurfaces2.GetMask(vExtendMin[0],vExtendMin[1],vExtendMin[2],
                                            vExtendMax[0],vExtendMax[1],vExtendMax[2],
                                            vImageSize[0], vImageSize[1],vImageSize[2],
                                            vTimeIndex)

        for vIndexZ in range (0,vImageSize[2]):
            ch1=vSurfaces1Mask.GetDataSubVolumeAs1DArrayFloats(0,0,vIndexZ,0,0,
                                                              vImageSize[0], vImageSize[1],1)
            ch2=vSurfaces2Mask.GetDataSubVolumeAs1DArrayFloats(0,0,vIndexZ,0,0,
                                                              vImageSize[0], vImageSize[1],1)
    #Determine the Voxels that are colocalized
            Coloc = [ch1[i] + ch2[i] for i in range(len(ch1))]
            Coloc=[0 if x!=2 else x for x in Coloc]#replace >2 with "0"
            Coloc=[1 if x==2 else x for x in Coloc]#replace 2 with 1
            vDataSet.SetDataSubVolumeAs1DArrayFloats(Coloc,0,0,vIndexZ,
                                                     vLastChannel,vTimeIndex,
                                                     vImageSize[0],vImageSize[1],1)

    vDataSet.SetChannelName(vLastChannel,'ColocChannel')
    vDataSet.SetChannelRange(vLastChannel,0,1)

    vImarisApplication.SetDataSet(vDataSet)
    #Run the Surface Creation Wizard on the new channel
    ip = vImarisApplication.GetImageProcessing()
    Coloc_surfaces1 = ip.DetectSurfaces(vDataSet, [],
                                        vLastChannel,
                                        vSmoothingFactor, 0, True, 55, '')
    Coloc_surfaces1.SetName('ColocSurface')

    #Add new surface to Surpass Scene
    vSurfaces1.SetVisible(0)
    vSurfaces2.SetVisible(0)

    vScene.AddChild(Coloc_surfaces1, -1)