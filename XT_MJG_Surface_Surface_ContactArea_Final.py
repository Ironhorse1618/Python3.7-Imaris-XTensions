# Surface Surface Contact Area

# Written by Matthew J. Gastinger
# June 2020 - Imaris 9.5.1

    # <CustomTools>
    #     <Menu>
    #         <Submenu name="Surfaces Functions">
    #             <Item name="Surface-Surface Contact Area" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Surface_Surface_ContactArea_Final(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSurfaces">
    #             <Item name="Surface-Surface Contact Area" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_Surface_Surface_ContactArea_Final(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #     </SurpassTab>
    # </CustomTools>

# Description
# This XTension will find the surface contact area between 2 surfaces.  The
# primary surface is the base, and secondary is one covering the primary.

# The result of the XTension will generate a one voxel thick unsmoothed
# surface object above the primary surface representing where the 2 surfaces
# physically overlap.

# Two new statistics will be generated.  1)The first will be a total surface
# area of each new surface object.  The measurement will be estimate by
# taking the number of voxels and multiplying by the area a a single (XY
# pixel).  2) The second statistic will be in the "overall" tab, reporting
# the percentage of surface contact area relative to the total surface area
# of the primary surfaces.

import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import *
from tkinter.ttk import *
import ImarisLib

#aImarisId=0
def XT_MJG_Surface_Surface_ContactArea_Final(aImarisId):
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

    ZLimit=((3*aXvoxelSpacing)+100*aXvoxelSpacing)/100
    endZadj=int(round((aZvoxelSpacing/aXvoxelSpacing*vDataSize[2])))
    #Test for isotopic voxels
    if aZvoxelSpacing>ZLimit:
        VoxelTest=tk.Tk()
        VoxelTest.withdraw()
        messagebox.showerror(title='ScalingError',
                         message='Warning this volume is does NOT have isotropic voxels \n' +
                         'To properly run this application go to:\n' +
                         'Edit--""Resample3D"" and adjust Z-size to '+ str(endZadj))
        VoxelTest.destroy

    ############################################################################
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
    #Making the Listbox for the Primary surface
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
    lstbox = Listbox(main, listvariable=names, selectmode=SINGLE, width=20, height=10)
    lstbox.grid(column=0, row=0, columnspan=2)
    def select():
        global PrimarySelection
        PrimarySelection = list()
        selection = lstbox.curselection()
        for i in selection:
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
    #Making the Listbox for the Secondary converage surface
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
    lstbox = Listbox(main, listvariable=names, selectmode=SINGLE, width=20, height=10)
    lstbox.grid(column=0, row=0, columnspan=2)
    def select():
        global SecondarySelection
        SecondarySelection = list()
        selection = lstbox.curselection()
        for i in selection:
            entrada = lstbox.get(i)
            SecondarySelection.append(entrada)
    #Test for the correct number selected
        if len(SecondarySelection)!=1:
            messagebox.showerror(title='Surface menu',
                          message='Please Select 1 surfaces')
            main.mainloop()
        elif SecondarySelection==PrimarySelection:
            main.mainloop()
        else:
            main.destroy()

    btn = Button(main, text="Secondary coverage Surface", command=select)
    btn.grid(column=1, row=1)
    #Selects the top 2 items in the list
    lstbox.selection_set(1)
    main.mainloop()
    ####################################################################
    # get the Selected surfaces Indices in Surpass for specific
    vDataItem=vScene.GetChild(NamesSurfaceIndex[(NamesSurfaces.index( ''.join(map(str, PrimarySelection[0]))))])
    vSurfaces1=vImarisApplication.GetFactory().ToSurfaces(vDataItem)

    vDataItem=vScene.GetChild(NamesSurfaceIndex[(NamesSurfaces.index( ''.join(map(str, SecondarySelection[0]))))])
    vSurfaces2=vImarisApplication.GetFactory().ToSurfaces(vDataItem)

    #clone Dataset
    vImarisDataSet = vImage.Clone()
    vImarisDataSet.SetSizeC(vSizeC + 3)

    # #Convert to 32bit
    import Imaris
    vType = Imaris.tType.eTypeFloat
    vImarisDataSet.SetType(vType)

    for vTimeIndex in range (vSizeT):
        vMaskDataSetPrimary = vSurfaces1.GetMask(vDataMin[0],vDataMin[1],vDataMin[2],
                                                vDataMax[0],vDataMax[1],vDataMax[2],
                                                vDataSize[0], vDataSize[1],vDataSize[2],
                                                vTimeIndex)
        vMaskDataSetSecondary = vSurfaces2.GetMask(vDataMin[0],vDataMin[1],vDataMin[2],
                                                vDataMax[0],vDataMax[1],vDataMax[2],
                                                vDataSize[0], vDataSize[1],vDataSize[2],
                                                vTimeIndex)

        for vIndexZ in range (vDataSize[2]):
            vSlice1D=[]
    #Mask for Primary surface (inside=1)
            vSlice = vMaskDataSetPrimary.GetDataSliceFloats(vIndexZ, 0, 0)
    #replace "1" at front and end with "0" for each row of surface mask
            for i in range (vDataSize[0]):
                vSlice[i][0]=0
                vSlice[i][-1]=0

           #Set first and last slice to all "0"" - plus all border pixels to "0"
            if vIndexZ==0 or vIndexZ==vDataSize[2]-1:
                vSlice=[[0 for i in row] for row in vSlice]
            else:
                for i in range (vDataSize[1]):
                    vSlice[0][i]=0
                    vSlice[-1][i]=0
                for i in range (vDataSize[0]):
                    vSlice[i][0]=0
                    vSlice[i][-1]=0

    #Reshape Slice mask into 1D array
            for j in range(vDataSize[1]):
                for i in range(vDataSize[0]):
                    vSlice1D.append(vSlice[i][j])

            vImarisDataSet.SetDataSubVolumeAs1DArrayFloats(vSlice1D,0,0,vIndexZ,
                                                         vSizeC,vTimeIndex,
                                                         vDataSize[0],vDataSize[1],1)
    #Mask for secondary Surface (inside=1)
            vSlice2=vMaskDataSetSecondary.GetDataSubVolumeAs1DArrayFloats(0,0,vIndexZ,0,0,
                                                           vDataSize[0], vDataSize[1],1)

            vImarisDataSet.SetDataSubVolumeAs1DArrayFloats(vSlice2,0,0,vIndexZ,
                                                         vSizeC+1,vTimeIndex,
                                                         vDataSize[0],vDataSize[1],1)


    #Run the Distance Transform on primary surface
    ip = vImarisApplication.GetImageProcessing()
    ip.DistanceTransformChannel(vImarisDataSet,vSizeC, 1, False)

    for vTime2 in range (vSizeT):
        for vSlice3 in range (vDataSize[2]):
            ch1=vImarisDataSet.GetDataSubVolumeAs1DArrayFloats(0, 0, vSlice3, vSizeC, vTime2, vDataSize[0], vDataSize[1], 1)
            ch2=vImarisDataSet.GetDataSubVolumeAs1DArrayFloats(0, 0, vSlice3, vSizeC+1, vTime2, vDataSize[0], vDataSize[1], 1)
     #Test slice for surface present
            # if ch1>999999999999:
            #     continue

    #Multiply distance transform by secondary surface mask
            vContact=[ch1*ch2 for ch1,ch2 in zip(ch1,ch2)]
    #set new channel for surface contact area
            vImarisDataSet.SetDataSubVolumeAs1DArrayFloats(vContact,0,0,vSlice3,vSizeC+2,vTime2,vDataSize[0], vDataSize[1],1)

    vImarisApplication.SetDataSet(vImarisDataSet)
    vSurfaces1.SetVisible(1)
    vSurfaces2.SetVisible(0)

    #Create a new folder object for new surfaces
    Newsurfaces = vImarisApplication.GetFactory()
    result = Newsurfaces.CreateDataContainer()
    result.SetName('Surface-Surface contact -' + vSurfaces1.GetName())

    #Generate Total surface area
    UpperThreshold=1.5*aXvoxelSpacing
    vAllSurfaceArea=ip.DetectSurfacesWithUpperThreshold(vImarisDataSet,[],vSizeC,0,0,True,False,0.003,True,False,UpperThreshold,'')
    vAllSurfaceArea.SetName('Total Surface Area - ' + vSurfaces2.GetName())
    #vRGBA=[255,255,255, 0]#;%for yellow
    #vRGBA = uint32(vRGBA * [1; 256; 256*256; 256*256*256]); % combine different components (four bytes) into one integer
    #vAllSurfaceArea.SetColorRGBA(vRGBA);
    #Add new surface to Surpass Scene
    result.AddChild(vAllSurfaceArea, -1)
    vImarisApplication.GetSurpassScene().AddChild(result, -1)
    vAllSurfaceArea.SetVisible(0)

    #Get Original Stats from Total surface area
    vAllSurfaceAreaStatistics = vAllSurfaceArea.GetStatistics()
    vAllSurfaceAreaStatNames = vAllSurfaceAreaStatistics.mNames
    vAllSurfaceAreaStatValues = vAllSurfaceAreaStatistics.mValues
    vAllSurfaceAreaTotalNumberOfVoxelsStatIndex=[i for i,val in enumerate(vAllSurfaceAreaStatNames)
                                  if val==('Total Number of Voxels')]
    vAllSurfaceAreaTotalNumberOfVoxelsStat=[x[1] for x in enumerate(vAllSurfaceAreaStatValues)
                          if x[0] in vAllSurfaceAreaTotalNumberOfVoxelsStatIndex]
    vAllSurfaceAreaFinal = vAllSurfaceAreaTotalNumberOfVoxelsStat[0]*aXvoxelSpacing*aXvoxelSpacing

    #Generate contact surface surface
    UpperThreshold=1.5*aXvoxelSpacing
    vSurfaceContact=ip.DetectSurfacesWithUpperThreshold(vImarisDataSet,[],vSizeC+2,0,0,True,False,0.003,True,False,UpperThreshold,'')
    vSurfaceContact.SetName('Surface contact Area - ' + vSurfaces2.GetName())
    vRGBA = 65535 #for yellow
    vSurfaceContact.SetColorRGBA(vRGBA);

    #Add new surface to Surpass Scene
    result.AddChild(vSurfaceContact, -1)
    vImarisApplication.GetSurpassScene().AddChild(result, -1)
    #Remove/crop the working channels
    vImarisDataSet.Crop(0,vDataSize[0],0,vDataSize[1],0,vDataSize[2],0,vSizeC,0,vSizeT)

    #Get surface contact area
    vSurfaceContactStatistics = vSurfaceContact.GetStatistics()
    vSurfaceContactStatNames = vSurfaceContactStatistics.mNames
    vSurfaceContactStatValues = vSurfaceContactStatistics.mValues
    vSurfaceContactStatIds = vSurfaceContactStatistics.mIds
    vSurfaceContactNumberOfVoxelIndex=[i for i,val in enumerate(vSurfaceContactStatNames)
                                  if val==('Number of Voxels')]
    vSurfaceContactIds=[x[1] for x in enumerate(vSurfaceContactStatIds)
                          if x[0] in vSurfaceContactNumberOfVoxelIndex]
    vSurfaceContactVoxels=[x[1] for x in enumerate(vSurfaceContactStatValues)
                          if x[0] in vSurfaceContactNumberOfVoxelIndex]
    vSurfaceContactArea = [i*aXvoxelSpacing*aYvoxelspacing for i in vSurfaceContactVoxels]

    #Find appropriate Ids and reorder so it matches in Imaris
    vSurfaceContactAreaFinal=[]
    vSurfaceContactNewInd=sorted((e,i) for i,e in enumerate(vSurfaceContactIds))
    for i in range (len(vSurfaceContactArea)):
        vSurfaceContactAreaFinal.append(vSurfaceContactArea[vSurfaceContactNewInd[i][1]])

    if vSurfaceContactStatValues==0:
         messagebox.showerror(title='ContactArea', message='No surface contact Found')
    #Generate Surface contact Area stat
    vNumberOfSurfaceContact=vSurfaceContact.GetNumberOfSurfaces()
    vSurfaceStatvIds=list(range(len(vSurfaceContactArea)))
    vSurfaceStatUnits=[' ']*(len(vSurfaceContactArea))
    vSurfaceStatNames=[' Contact surface area, um^2']*(len(vSurfaceContactArea))
    vSurfaceStatFactors=(['Surface']*len(vSurfaceContactArea),
                         ['1']*(len(vSurfaceContactArea)))
    vSurfaceStatFactorName=['Category','Time']
    vSurfaceContact.AddStatistics(vSurfaceStatNames, vSurfaceContactAreaFinal,
                                  vSurfaceStatUnits, vSurfaceStatFactors,
                                  vSurfaceStatFactorName, vSurfaceStatvIds)

    #Insert an overall Statistic
    vOverallStatIds=[int(-1)]
    vOverallStatUnits=['']*vSizeT
    vOverallStatFactorsTime=list(range(1,vSizeT+1))
    vOverallStatFactors=[['Overall'],[str(i) for i in vOverallStatFactorsTime]]
    vOverallStatNames = [' % Surface coverage']
    vOverallStatFactorNames=['FactorName','Time']
    vOverallNewStat=[float((sum(vSurfaceContactAreaFinal)/vAllSurfaceAreaFinal*100))]
    vSurfaceContact.AddStatistics(vOverallStatNames, vOverallNewStat,
                                  vOverallStatUnits, vOverallStatFactors,
                                  vOverallStatFactorNames, vOverallStatIds)






