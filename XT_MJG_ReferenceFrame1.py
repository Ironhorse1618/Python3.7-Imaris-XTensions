# Written by Matthew J. Gastinger
# Dec 2022 - Imaris 9.9.1


#    <CustomTools>
#      <Menu>
#       <Submenu name="Spots Functions">
#        <Item name="Reference Frame Adjustment" icon="Python3">
#          <Command>Python3XT::XT_MJG_ReferenceFrame1(%i)</Command>
#        </Item>
#       </Submenu>
#       <Submenu name="Surface Functions">
#        <Item name="Reference Frame Adjustment" icon="Python3">
#          <Command>Python3XT::XT_MJG_ReferenceFrame1(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#      <SurpassTab>
#        <SurpassComponent name="bpSpots">
#          <Item name="Reference Frame Adjustment" icon="Python3">
#            <Command>Python3XT::XT_MJG_ReferenceFrame1(%i)</Command>
#          </Item>
#        </SurpassComponent>
#        <SurpassComponent name="bpSurfaces">
#          <Item name="Reference Frame Adjustment" icon="Python3">
#            <Command>Python3XT::XT_MJG_ReferenceFrame1(%i)</Command>
#          </Item>
#        </SurpassComponent>
#      </SurpassTab>
#    </CustomTools>


#Description:  Adjustment the placement of a Reference frame using either:
    # 1. manually inputted positions (XYZ)
    # 2. Selected spot
    # 3. Selected Surface
    # 4. Filament starting point





import platform
import sys

import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import ImarisLib

aImarisId=0
def XT_MJG_ReferenceFrame1(aImarisId):
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
    
    ##################################################################
    ##################################################################
    global NamesSurfaces, NamesSpots,NamesFilaments
    
    NamesSurfaces=[]
    NamesSpots=[]
    NamesFilaments=[]
    NamesFilamentsIndex=[]
    NamesSurfacesIndex=[]
    NamesSpotsIndex=[]
    NamesReferenceFrames=[]
    NamesReferenceFramesIndex=[]
    
    vSurpassSurfaces = 0
    vSurpassSpots = 0
    vSurpassFilaments = 0
    vSurpassReferenceFrame = 0
    vNumberSurpassItems=vImarisApplication.GetSurpassScene().GetNumberOfChildren()
    for vChildIndex in range(0,vNumberSurpassItems):
        vDataItem=vSurpassScene.GetChild(vChildIndex)
        IsSurface=vImarisApplication.GetFactory().IsSurfaces(vDataItem)
        IsSpot=vImarisApplication.GetFactory().IsSpots(vDataItem)
        IsFilament=vImarisApplication.GetFactory().IsFilaments(vDataItem)
        IsReferenceFrame=vImarisApplication.GetFactory().IsReferenceFrames(vDataItem)
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
            NamesFilamentsIndex.append(vChildIndex)
        elif IsReferenceFrame:
            vSurpassReferenceFrame = vSurpassReferenceFrame+1
            NamesReferenceFrames.append(vDataItem.GetName(),)
            NamesReferenceFramesIndex.append(vChildIndex)
    
    ############################################################################
    #Choose reference frame Surpass scene object
    
    if len(NamesReferenceFramesIndex) == 1:
        vDataItem=vSurpassScene.GetChild(NamesReferenceFramesIndex[0])
        qCurrentReferenceFrame=vImarisApplication.GetFactory().ToReferenceFrames(vDataItem)
    else:
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
        names.set(NamesReferenceFrames)
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
                                      message='Please Choose 1 Rerence Frame')
                main.mainloop()
            else:
                main.destroy()
    
        btn = ttk.Button(frame, text="Choose Reference Frame Object", command=select)
        btn.grid(column=1, row=1)
        #Selects the top items in the list
        lstbox.selection_set(0)
        main.mainloop()
    
        vDataItem=vSurpassScene.GetChild(NamesReferenceFramesIndex[(NamesReferenceFrames.index( ''.join(map(str, ObjectSelection[0]))))])
        qCurrentReferenceFrame=vImarisApplication.GetFactory().ToReferenceFrames(vDataItem)
    
    ##################################################################
    ##################################################################
    vExtendMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vExtendMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vImageSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    Xvoxelspacing= (vExtendMax[0]-vExtendMin[0])/vImageSize[0]
    Yvoxelspacing= (vExtendMax[1]-vExtendMin[1])/vImageSize[1]
    Zvoxelspacing = round((vExtendMax[2]-vExtendMin[2])/vImageSize[2],3)
    
    vMidX = round((vExtendMax[0]-vExtendMin[0])/2,2)
    vMidY = round((vExtendMax[1]-vExtendMin[1])/2,2)
    vMidZ = round((vExtendMax[2]-vExtendMin[2])/2,2)
    
    ##################################################################
    ##################################################################
    def ButtonManual ():
        global vNewPosX,vNewPosY,vNewPosZ, qMethod
        global vMidX, vMidY, vMidZ
        vNewPosX=EntryX.get()
        vNewPosY=EntryY.get()
        vNewPosZ=EntryZ.get()
    
        # if (var1.get() + var2.get() + var3.get() + var4.get()) > 1:
        #     messagebox.showerror(title='Reference Frame menu',
        #                      message='Please Choose ONE Method')
        #     qInputBox.mainloop()
        # elif (var1.get() + var2.get() + var3.get() + var4.get()) == 0:
        #     messagebox.showerror(title='Reference Frame menu',
        #                      message='Please Choose ONE Method')
        #     qInputBox.mainloop()
    
        # if var1.get() == 1:
        #     qMethod = "manual"
        #     qInputBox.destroy()
        # if var2.get() == 1:
        #     qMethod = "spot"
        #     qInputBox.destroy()
        # if var3.get() == 1:
        #     qMethod = "surface"
        #     qInputBox.destroy()
        # if var4.get() == 1:
        #     qMethod = "filament"
        #     qInputBox.destroy()
    
    def ButtonSpot ():
        global qMethod
        qMethod = "spot"
        qInputBox.destroy()
    def ButtonSurface ():
        global qMethod
        qMethod = "surface"
        qInputBox.destroy()
    def ButtonFilament ():
        global qMethod
        qMethod = "filament"
        qInputBox.destroy()
    
    qInputBox=Tk()
    qInputBox.title("Click One Option")
    qInputBox.geometry("270x190")
    var1 = tk.IntVar(value=0)
    var2 = tk.IntVar(value=0)
    var3 = tk.IntVar(value=0)
    var4 = tk.IntVar(value=0)
    
    
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
    tk.Label(qInputBox, text='').grid(row=0, column=0)
    
    # tk.Checkbutton(qInputBox, text='Modify Existing Reference Frame (um)',
    #                variable=var1, onvalue=1, offvalue=0).grid(row=0, column=0,sticky=W)
    qButtonManual = Button(qInputBox, text="Manually enter Reference Frame Position",command=ButtonManual)
    qButtonManual.grid(row=0, column=0, sticky=W)
    
    Label(qInputBox,text="X:").grid(row=1, column=0, padx=40,sticky=W)
    EntryX=Entry(qInputBox,justify='center',width=4)
    EntryX.grid(row=1, column=0, padx=60,sticky=W)
    EntryX.insert(0, str(vMidX))
    Label(qInputBox,text="Y:").grid(row=1, column=0, padx=110,sticky=W)
    EntryY=Entry(qInputBox,justify='center',width=4)
    EntryY.grid(row=1, column=0, padx=130,sticky=W)
    EntryY.insert(0, str(vMidY))
    Label(qInputBox,text="Z:").grid(row=1, column=0, padx=180, sticky=W)
    EntryZ=Entry(qInputBox,justify='center',width=4)
    EntryZ.grid(row=1, column=0, padx=200,sticky=W)
    EntryZ.insert(0, str(vMidZ))
    
    # tk.Checkbutton(qInputBox, text='Selected Spot',
    #                variable=var2, onvalue=1, offvalue=0).grid(row=2, column=0,sticky=W)
    # tk.Checkbutton(qInputBox, text='Selected Surface',
    #                variable=var3, onvalue=1, offvalue=0).grid(row=3, column=0,sticky=W)
    # tk.Checkbutton(qInputBox, text='Selected Filament',
    #                variable=var4, onvalue=1, offvalue=0).grid(row=4, column=0,sticky=W)
    
    
    qButtonSpot = Button(qInputBox, bg="red", fg="white", text="Selected Spot",command=ButtonSpot)
    qButtonSpot.grid(row=4, column=0, padx=40,sticky=W)
    qButtonSurface = Button(qInputBox, bg="blue", fg="white", text="Selected Surface",command=ButtonSurface)
    qButtonSurface.grid(row=6, column=0, padx =40,sticky=W)
    qButtonFilament = Button(qInputBox, bg="green", fg="white", text="Selected Filament",command=ButtonFilament)
    qButtonFilament.grid(row=8, column=0, padx=40,sticky=W)
    
    
    tk.Label(qInputBox, text=' ').grid(row=3, column=0)
    tk.Label(qInputBox, text=' ').grid(row=5, column=0)
    tk.Label(qInputBox, text=' ').grid(row=7, column=0)
    
    # qWhatOS=platform.system()
    # if qWhatOS=='Darwin':
    #     Single=Button(qInputBox, fg="black", text="Set Reference Frame",command=ReferenceFrame )
    # else:
    #     Single=Button(qInputBox, bg="blue", fg="white", text="Set Reference Frame",command=ReferenceFrame )
    
    # Single.grid(row=7, column=0, padx=40, sticky=W)
    
    qInputBox.mainloop()
    
    ##################################################################
    ##################################################################
    vExtendMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vExtendMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vImageSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    Xvoxelspacing= (vExtendMax[0]-vExtendMin[0])/vImageSize[0]
    Yvoxelspacing= (vExtendMax[1]-vExtendMin[1])/vImageSize[1]
    Zvoxelspacing = round((vExtendMax[2]-vExtendMin[2])/vImageSize[2],3)
    
    ##################################################################
    if qMethod == 'manual':
        qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([0],[[float(vNewPosX),float(vNewPosY),float(vNewPosZ)]])
    else:
    #Making the Listbox for the Surpass menu
        main = tk.Tk()
        main.title("Surpass menu")
        main.geometry("+50+150")
        frame = ttk.Frame(main, padding=(3, 3, 12, 12))
        frame.grid(column=0, row=0, sticky=(N, S, E, W))
        main.attributes("-topmost", True)
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
    ##################################################################
        names = StringVar()
        ObjectSelection = []
        if qMethod == 'spot':
            names.set(NamesSpots)
            if len(NamesSpots) == 1:
                ObjectSelection = [NamesSpots[0]]
        elif qMethod == 'surface':
            names.set(NamesSurfaces)
            if len(NamesSurfaces) == 1:
                ObjectSelection = [NamesSurfaces[0]]
        else:
            names.set(NamesFilaments)
            if len(NamesFilaments) == 1:
                ObjectSelection = [NamesFilaments[0]]
        
        if ObjectSelection == []:
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
                    messagebox.showerror(title='Surpass Selection menu',
                                          message='Please Choose One!')
                    main.mainloop()
                else:
                    main.destroy()
            btn = ttk.Button(frame, text="Choose Surpass Object", command=select)
            btn.grid(column=1, row=1)
        #Selects the top items in the list
            lstbox.selection_set(0)
            main.mainloop()
    ##################################################################
    ##################################################################
        if qMethod == 'spot':
    #get the Selected Spots in Surpass Scene
            vDataItem=vSurpassScene.GetChild(NamesSpotsIndex[(NamesSpots.index( ''.join(map(str, ObjectSelection[0]))))])
            vSpots=vImarisApplication.GetFactory().ToSpots(vDataItem)
    #get the spot data
            vSpotsColocPositionsXYZ = vSpots.GetPositionsXYZ()
            # vSpotsColocRadius = vSpots.GetRadiiXYZ()
            vSpotsColocTimeIndices = vSpots.GetIndicesT()
            # vSpotsColocCount = len(vSpotsColocRadius)
            vSpotsId = vSpots.GetIds()
    #Make sure one spot is selected, if not loop until does one is
            if len(vSpotsId) > 1:
                vSelectedIDs=vSpots.GetSelectedIndices()
                while len(vSelectedIDs)>1 or vSelectedIDs == []:
                    messagebox.showerror(title='Select 1 Object',
                                     message='Please Return to Imaris\n'
                                     'Select one Spot within\n'
                                     '-----' + ObjectSelection[0] +'-----\n'
                                     'CLICK "OK" to Apply')
                    vSelectedIDs=vSpots.GetSelectedIndices()
            elif len(vSpotsId) == []:
                messagebox.showerror(title='Surpass menu',
                                 message='Please Create some Spots!')
                exit()
            elif len(vSpotsId) == 1:
                vSelectedIDs = 1
            qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([0],
                                     [[vSpotsColocPositionsXYZ[vSelectedIDs[0]][0],
                                      vSpotsColocPositionsXYZ[vSelectedIDs[0]][1],
                                      vSpotsColocPositionsXYZ[vSelectedIDs[0]][2]]])
    ##################################################################
    ##################################################################
        if qMethod=='surface':
        # get the Selected Spots in Surpass Scene
            vDataItem=vSurpassScene.GetChild(NamesSurfacesIndex[(NamesSurfaces.index( ''.join(map(str, ObjectSelection[0]))))])
            vSurfaces=vImarisApplication.GetFactory().ToSurfaces(vDataItem)
            vNumberofSurfaces=vSurfaces.GetNumberOfSurfaces()
            if vNumberofSurfaces > 1:
                vSelectedIDs=vSurfaces.GetSelectedIndices()
                while len(vSelectedIDs)>1 or vSelectedIDs == []:
                    messagebox.showerror(title='Select 1 Object',
                                     message='Please Return to Imaris\n'
                                     'Select one Surface within\n'
                                     '-----' + ObjectSelection[0] +'-----\n'
                                     'CLICK "OK" to Apply')
                    vSelectedIDs=vSurfaces.GetSelectedIndices()
            elif vNumberofSurfaces == []:
                messagebox.showerror(title='Surface menu',
                                 message='Please Create some Surfaces!')
                exit()
            elif vNumberofSurfaces == 1:
                vSelectedIDs = 0
    
            vSurfaces.GetCenterOfMass(vSelectedIDs[0])[0][0]
            vSurfaces.GetCenterOfMass(vSelectedIDs[0])[0][1]
            vSurfaces.GetCenterOfMass(vSelectedIDs[0])[0][2]
    
            qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([0],
                                     [[vSurfaces.GetCenterOfMass(vSelectedIDs[0])[0][0],
                                       vSurfaces.GetCenterOfMass(vSelectedIDs[0])[0][1],
                                       vSurfaces.GetCenterOfMass(vSelectedIDs[0])[0][2]]])
    ####################################################################
    ####################################################################
        if qMethod=='filament':
        # get the Selected Spots in Surpass Scene
            vDataItem = vSurpassScene.GetChild(NamesFilamentsIndex[(NamesFilaments.index( ''.join(map(str, ObjectSelection[0]))))])
            vFilaments = vImarisApplication.GetFactory().ToFilaments(vDataItem)
    
            # vSelectedIDs = vFilaments.GetSelectedIds()
    
            qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([0],
                                [[vFilaments.GetPositionsXYZ(0)[0][0],
                                vFilaments.GetPositionsXYZ(0)[0][1],
                                vFilaments.GetPositionsXYZ(0)[0][2]]])
    ####################################################################
    ####################################################################
    
    
    
    
    # test=vFactory.ToReferenceFrames(vImarisApplication.GetSurpassSelection())
    # vPosition = test.GetKeyFramesPositionsXYZT().mPositions
    # #position is based on upper left corner bein 0,0,0
    # vTimes = test.GetKeyFramesTimes()
    
    
    # # test.SetKeyFramesPositionsXYZT(0,732,300,0)
    # posXYZ=[[732,300,0]]
    # test.SetKeyFramesPositionsXYZT([0],posXYZ)
    
    
    # #Add a new Reference Frame
    # vReferenceFrames=vImarisApplication.GetFactory().CreateReferenceFrames()
    # posNEWXYZ=[[0,0,0]]
    # vReferenceFrames.SetKeyFramesPositionsXYZT([0],posXYZ)
    
    # vImarisApplication.GetSurpassScene().AddChild(vReferenceFrames, -1)

