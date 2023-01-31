# Written by Matthew J. Gastinger
# Dec 2022 - Imaris 10


#    <CustomTools>
#      <Menu>
            #<Item name="Add Manual Reference Frame6" icon="Python3">
                #<Command>Python3XT::XT_MJG_ReferenceFrame6(%i)</Command>
            #</Item>
#      </Menu>
#      <SurpassTab>
#        <SurpassComponent name="bpSpots">
#          <Item name="Reference Frame Adjustment6" icon="Python3">
#            <Command>Python3XT::XT_MJG_ReferenceFrame6(%i)</Command>
#          </Item>
#        </SurpassComponent>
#        <SurpassComponent name="bpSurfaces">
#          <Item name="Reference Frame Adjustment6" icon="Python3">
#            <Command>Python3XT::XT_MJG_ReferenceFrame6(%i)</Command>
#          </Item>
#        </SurpassComponent>
#        <SurpassComponent name="bpFilaments">
#          <Item name="Reference Frame Adjustment6" icon="Python3">
#            <Command>Python3XT::XT_MJG_ReferenceFrame6(%i)</Command>
#          </Item>
#        </SurpassComponent>
#      </SurpassTab>
#    </CustomTools>

#Description:  Adjustment the placement of a Reference frame using either:
    # 1. manually inputted positions (XYZ)
    # 2. Selected spot
    # 3. Selected Surface
    # 4. Filament starting point

import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import ImarisLib

aImarisId=0
def XT_MJG_ReferenceFrame6(aImarisId):
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
    #Get image properties
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
    
    vCurrentVisibleTimeIndex=vImarisApplication.GetVisibleIndexT()
    
    
    #Test to see what is the Surpass object TYPE
    vIsSpots = vImarisApplication.GetFactory().IsSpots(vImarisApplication.GetSurpassSelection())
    vIsSurfaces = vImarisApplication.GetFactory().IsSurfaces(vImarisApplication.GetSurpassSelection())
    vIsFilaments = vImarisApplication.GetFactory().IsFilaments(vImarisApplication.GetSurpassSelection())
    qMethod = "manual"
    if vIsSpots == True:
        qMethod = "spot"
    if vIsSurfaces == True:
        qMethod = "surface"
    if vIsFilaments == True:
        qMethod = "filament"
    qCreateNew=False
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
    #Choose Reference Frame Surpass scene object
    if len(NamesReferenceFramesIndex) == 1:
        vDataItem=vSurpassScene.GetChild(NamesReferenceFramesIndex[0])
        qCurrentReferenceFrame=vImarisApplication.GetFactory().ToReferenceFrames(vDataItem)
    
    if not NamesReferenceFramesIndex:
        qCreateNew = True
    if len(NamesReferenceFramesIndex) > 1:
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
    
        btn = ttk.Button(frame, text="Choose Reference Frame To Move", command=select)
        btn.grid(column=1, row=1)
        #Selects the top items in the list
        lstbox.selection_set(0)
        main.mainloop()
    
        vDataItem=vSurpassScene.GetChild(NamesReferenceFramesIndex[(NamesReferenceFrames.index( ''.join(map(str, ObjectSelection[0]))))])
        qCurrentReferenceFrame=vImarisApplication.GetFactory().ToReferenceFrames(vDataItem)
    
    ##################################################################
    ##################################################################
    def ButtonManual ():
        global vNewPosX,vNewPosY,vNewPosZ,vNewTime, qCreateNew
        global vMidX, vMidY, vMidZ, vIsManual
        vNewPosX=EntryX.get()
        vNewPosY=EntryY.get()
        vNewPosZ=EntryZ.get()
        vNewTime=EntryTime.get()
        vIsManual = 1
        # qMethod = 'manual'
        if var1.get() == 1:
            qCreateNew = True
        qInputBox.destroy()
    
    def SelectedObject ():
        global qCreateNew, vIsManual
        vIsManual = 0
        if var1.get() == 1:
            qCreateNew = True
        qInputBox.destroy()
    
    qInputBox=Tk()
    qInputBox.title("Reference Frame")
    qInputBox.geometry("300x190")
    var1 = tk.IntVar(value=0)
    
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
    tk.Label(qInputBox, text=' ').grid(row=0, column=0)
    qButtonManual = Button(qInputBox, text="Reference Frame to manual position",command=ButtonManual)
    qButtonManual.grid(row=1, column=0, padx=10,sticky=W)
    
    Label(qInputBox,text="X:").grid(row=2, column=0, padx=10,pady=10,sticky=W)
    EntryX=Entry(qInputBox,justify='center',width=4)
    EntryX.grid(row=2, column=0, padx=30,sticky=W)
    EntryX.insert(0, str(vMidX))
    Label(qInputBox,text="Y:").grid(row=2, column=0, padx=80,sticky=W)
    EntryY=Entry(qInputBox,justify='center',width=4)
    EntryY.grid(row=2, column=0, padx=100,sticky=W)
    EntryY.insert(0, str(vMidY))
    Label(qInputBox,text="Z:").grid(row=2, column=0, padx=150, sticky=W)
    EntryZ=Entry(qInputBox,justify='center',width=4)
    EntryZ.grid(row=2, column=0, padx=170,sticky=W)
    EntryZ.insert(0, str(vMidZ))
    Label(qInputBox,text="T:").grid(row=2, column=0, padx=220, sticky=W)
    EntryTime=Entry(qInputBox,justify='center',width=4)
    EntryTime.grid(row=2, column=0, padx=240,sticky=W)
    EntryTime.insert(0, str(vCurrentVisibleTimeIndex))
    
    qButtonSpot = Button(qInputBox, text="Reference Frame to Selected Object",command=SelectedObject)
    qButtonSpot.grid(row=4, column=0,padx=10,sticky=W)
    
    tk.Label(qInputBox, text='Please Select one Object\n'
                             'Move Reference Frame\n'
                             '(Spot, Surface, or Filament)').grid(row=5, column=0, padx=30,sticky=W)
    
    tk.Checkbutton(qInputBox, text='Create a New Reference Frame',
                   variable=var1, onvalue=1, offvalue=0).grid(row=6, column=0,padx=10,sticky=W)
    
    qInputBox.mainloop()
    
    ##################################################################
    if vIsManual == 1:
        if qCreateNew == True:
            # #Add a new Reference Frame
            qCurrentReferenceFrame=vImarisApplication.GetFactory().CreateReferenceFrames()
            qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([vCurrentVisibleTimeIndex],[[float(vMidX),float(vMidY),float(vMidZ)]])
            vImarisApplication.GetSurpassScene().AddChild(qCurrentReferenceFrame, -1)
        else:
            qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([vCurrentVisibleTimeIndex],[[float(vNewPosX)-vExtendMin[0],
                                                                                          float(vNewPosZ)-vExtendMin[2]]])
    if qMethod == 'spot' and vIsManual == 0:
        #get the spot data
        vSpots = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
        vObjectPositionsXYZ = vSpots.GetPositionsXYZ()
        vSpotsRadius = vSpots.GetRadiiXYZ()
        vSpotsTimeIndices = vSpots.GetIndicesT()
        vSelectedIDs=vSpots.GetSelectedIndices()
        if len(vSelectedIDs) == 1:
            vSelectedObjectTimeIndex = vSpotsTimeIndices[vSelectedIDs[0]]
            if qCreateNew == True:
            # #Add a new Reference Frame
                qCurrentReferenceFrame=vImarisApplication.GetFactory().CreateReferenceFrames()
                qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([vSelectedObjectTimeIndex],[[float(vMidX),float(vMidY),float(vMidZ)]])
                vImarisApplication.GetSurpassScene().AddChild(qCurrentReferenceFrame, -1)
    
            qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([vSelectedObjectTimeIndex],
                                 [[vObjectPositionsXYZ[vSelectedIDs[0]][0]-vExtendMin[0],
                                  vObjectPositionsXYZ[vSelectedIDs[0]][1]-vExtendMin[1],
                                  vObjectPositionsXYZ[vSelectedIDs[0]][2]-vExtendMin[2]]])
    
            # vObjectPositionsXYZ[vSelectedIDs[0]][1]-vExtendMin[1]
    
        else:
            messagebox.showerror(title='Reference Frame menu',
                                        message='Please select one spot')
            vSelectedIDs=vSpots.GetSelectedIndices()
            vSelectedObjectTimeIndex = vSpotsTimeIndices[vSelectedIDs[0]]
            if len(vSelectedIDs) == 1:
                vSelectedObjectTimeIndex = vSpotsTimeIndices[vSelectedIDs[0]]
                if qCreateNew == True:
                # #Add a new Reference Frame
                    qCurrentReferenceFrame=vImarisApplication.GetFactory().CreateReferenceFrames()
                    qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([vSelectedObjectTimeIndex],[[float(vMidX),float(vMidY),float(vMidZ)]])
                    vImarisApplication.GetSurpassScene().AddChild(qCurrentReferenceFrame, -1)
    
                qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([vSelectedObjectTimeIndex],
                                 [[vObjectPositionsXYZ[vSelectedIDs[0]][0]-vExtendMin[0],
                                  vObjectPositionsXYZ[vSelectedIDs[0]][1]-vExtendMin[1],
                                  vObjectPositionsXYZ[vSelectedIDs[0]][2]-vExtendMin[2]]])
            else:
                messagebox.showerror(title='Reference Frame menu',
                                            message='XTension will shut down\n'
                                            'Please select one Spot and try again!')
    if qMethod == 'surface'and vIsManual == 0:
        vSurfaces = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
        vSelectedIDs=vSurfaces.GetSelectedIndices()
        
        
        if len(vSelectedIDs) == 1:
            vSelectedObjectTimeIndex = vSurfaces.GetTimeIndex(vSelectedIDs[0])
            if qCreateNew == True:
            # #Add a new Reference Frame
                qCurrentReferenceFrame=vImarisApplication.GetFactory().CreateReferenceFrames()
                qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([vSelectedObjectTimeIndex],[[float(vMidX),float(vMidY),float(vMidZ)]])
                vImarisApplication.GetSurpassScene().AddChild(qCurrentReferenceFrame, -1)
    
            vObjectPositionsXYZ = vSurfaces.GetCenterOfMass(vSelectedIDs[0])
            qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([vSelectedObjectTimeIndex],
                                 [[vObjectPositionsXYZ[0][0]-vExtendMin[0],
                                  vObjectPositionsXYZ[0][1]-vExtendMin[1],
                                  vObjectPositionsXYZ[0][2]-vExtendMin[2]]])
        else:
            messagebox.showerror(title='Reference Frame menu',
                                 message='Please select one surface')
            vSelectedIDs=vSurfaces.GetSelectedIndices()
            if len(vSelectedIDs) == 1:
                vSelectedObjectTimeIndex = vSurfaces.GetTimeIndex(vSelectedIDs[0])
                if qCreateNew == True:
                # #Add a new Reference Frame
                    qCurrentReferenceFrame=vImarisApplication.GetFactory().CreateReferenceFrames()
                    qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([vSelectedObjectTimeIndex],[[float(vMidX),float(vMidY),float(vMidZ)]])
                    vImarisApplication.GetSurpassScene().AddChild(qCurrentReferenceFrame, -1)
    
                vObjectPositionsXYZ = vSurfaces.GetCenterOfMass(vSelectedIDs[0])
                qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([vSelectedObjectTimeIndex],
                                     [[vObjectPositionsXYZ[0][0]-vExtendMin[0],
                                      vObjectPositionsXYZ[0][1]-vExtendMin[1],
                                      vObjectPositionsXYZ[0][2]-vExtendMin[2]]])
            else:
                messagebox.showerror(title='Reference Frame menu',
                                            message='XTension will shut down\n'
                                            'Please select one Surface and start again!')
    if qMethod == 'filament'and vIsManual == 0:
        vFilaments = vFactory.ToFilaments(vImarisApplication.GetSurpassSelection())
        vNumberOfFilaments = vFilaments.GetNumberOfFilaments()
        vFilamentIds = vFilaments.GetSelectedIds()
        
        
        if qCreateNew == True:
        # #Add a new Reference Frame
            qCurrentReferenceFrame=vImarisApplication.GetFactory().CreateReferenceFrames()
            vSelectedObjectTimeIndex = vFilaments.GetTimeIndex(0)
            qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([vSelectedObjectTimeIndex],[[float(vMidX),float(vMidY),float(vMidZ)]])
            vImarisApplication.GetSurpassScene().AddChild(qCurrentReferenceFrame, -1)
        
        for aNextFilament in range (vNumberOfFilaments):
            vSelectedObjectTimeIndex = vFilaments.GetTimeIndex(aNextFilament)
            qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([vSelectedObjectTimeIndex],
                            [[vFilaments.GetPositionsXYZ(aNextFilament)[0][0]-vExtendMin[0],
                            vFilaments.GetPositionsXYZ(aNextFilament)[0][1]-vExtendMin[1],
                            vFilaments.GetPositionsXYZ(aNextFilament)[0][2]-vExtendMin[2]]])
            qContinue=messagebox.askyesno(title='Reference Frame menu',
                            message='Is this the correct Position?')
            if qContinue==False:
                continue
            else:
                exit()
    #Need to add option to move specific Reference Frame at specific time.


