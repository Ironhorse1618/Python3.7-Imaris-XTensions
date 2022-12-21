# Written by Matthew J. Gastinger
# Dec 2022 - Imaris 9.9.1


#    <CustomTools>
#      <Menu>
#      </Menu>
#      <SurpassTab>
#        <SurpassComponent name="bpSpots">
#          <Item name="Reference Frame Adjustment" icon="Python3">
#            <Command>Python3XT::XT_MJG_ReferenceFrame2(%i)</Command>
#          </Item>
#        </SurpassComponent>
#        <SurpassComponent name="bpSurfaces">
#          <Item name="Reference Frame Adjustment" icon="Python3">
#            <Command>Python3XT::XT_MJG_ReferenceFrame2(%i)</Command>
#          </Item>
#        </SurpassComponent>
#        <SurpassComponent name="bpFilaments">
#          <Item name="Reference Frame Adjustment" icon="Python3">
#            <Command>Python3XT::XT_MJG_ReferenceFrame2(%i)</Command>
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
def XT_MJG_ReferenceFrame2(aImarisId):
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
    #Choose Reference Frame Surpass scene object
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
#Test to see what is the Surpass object TYPE
    vIsSpots = vImarisApplication.GetFactory().IsSpots(vImarisApplication.GetSurpassSelection())
    vIsSurfaces = vImarisApplication.GetFactory().IsSurfaces(vImarisApplication.GetSurpassSelection())
    vIsFilament = vImarisApplication.GetFactory().IsFilaments(vImarisApplication.GetSurpassSelection())

    ##################################################################
    ##################################################################
    def ButtonManual ():
        global vNewPosX,vNewPosY,vNewPosZ, qMethod
        global vMidX, vMidY, vMidZ
        vNewPosX=EntryX.get()
        vNewPosY=EntryY.get()
        vNewPosZ=EntryZ.get()
        qMethod = 'manual'
        qInputBox.destroy()

    def SelectedObject ():
        global qMethod
        vIsSpots = vImarisApplication.GetFactory().IsSpots(vImarisApplication.GetSurpassSelection())
        vIsSurfaces = vImarisApplication.GetFactory().IsSurfaces(vImarisApplication.GetSurpassSelection())
        vIsFilaments = vImarisApplication.GetFactory().IsFilaments(vImarisApplication.GetSurpassSelection())
        if vIsSpots == True:
            qMethod = "spot"
        if vIsSurfaces == True:
            qMethod = "surface"
            qInputBox.destroy()
        if vIsFilaments == True:
            qMethod = "filament"
        qInputBox.destroy()

    qInputBox=Tk()
    qInputBox.title("Reference Frame")
    qInputBox.geometry("230x170")
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
    tk.Label(qInputBox, text=' ').grid(row=0, column=0)
    qButtonManual = Button(qInputBox, text="Manual Frame Position",command=ButtonManual)
    qButtonManual.grid(row=1, column=0, padx=50,sticky=W)

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

    qButtonSpot = Button(qInputBox, bg="red", fg="white", text="Selected Object",command=SelectedObject)
    qButtonSpot.grid(row=4, column=0, padx=60,sticky=W)

    tk.Label(qInputBox, text='Please Select one Object\n'
                             'Click Button to move Reference Frame\n'
                             'To a selected Spot, Surface, or Filament').grid(row=5, column=0, padx=10,sticky=W)
    qInputBox.mainloop()

    ##################################################################
    if qMethod == 'manual':
        qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([0],[[float(vNewPosX),float(vNewPosY),float(vNewPosZ)]])
    if qMethod == 'spot':
        #get the spot data
        vSpots = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
        vSpotsPositionsXYZ = vSpots.GetPositionsXYZ()
        vSpotsRadius = vSpots.GetRadiiXYZ()
        vSpotsTimeIndices = vSpots.GetIndicesT()
        vSelectedIDs=vSpots.GetSelectedIndices()
        vSelectedSpotTimeIndex = vSpotsTimeIndices(vSelectedIDs)

        if len(vSelectedIDs) == 1:
            vSelectedTimeIndex = vSpotsTimeIndices(vSelectedIDs)
            qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([0],
                                 [[vSpotsPositionsXYZ[vSelectedIDs[0]][0],
                                  vSpotsPositionsXYZ[vSelectedIDs[0]][1],
                                  vSpotsPositionsXYZ[vSelectedIDs[0]][2]]])
        else:
            messagebox.showerror(title='Reference Frame menu',
                                        message='Please select one spot')
            vSelectedIDs=vSpots.GetSelectedIndices()
            vSelectedTimeIndex = vSpotsTimeIndices(vSelectedIDs)
            if len(vSelectedIDs) == 1:
                qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([0],
                                 [[vSpotsPositionsXYZ[vSelectedIDs[0]][0],
                                  vSpotsPositionsXYZ[vSelectedIDs[0]][1],
                                  vSpotsPositionsXYZ[vSelectedIDs[0]][2]]])
            else:
                messagebox.showerror(title='Reference Frame menu',
                                            message='XTension will shut down\n'
                                            'Please select one Spot and try again!')
    if qMethod == 'surface':
        vSurfaces = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
        vSelectedIDs=vSurfaces.GetSelectedIndices()
        if len(vSelectedIDs) == 1:
            vSelectedTimeIndex = vSurfaces.GetTimeIndex(vSelectedIDs)
            qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([0],
                                  [[vSurfaces.GetCenterOfMass(vSelectedIDs[0])[0][0],
                                    vSurfaces.GetCenterOfMass(vSelectedIDs[0])[0][1],
                                    vSurfaces.GetCenterOfMass(vSelectedIDs[0])[0][2]]])
        else:
            messagebox.showerror(title='Reference Frame menu',
                                 message='Please select one spot')
            vSelectedIDs=vSurfaces.GetSelectedIndices()
            if len(vSelectedIDs) == 1:
                vSelectedTimeIndex = vSurfaces.GetTimeIndex(vSelectedIDs)
                qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([0],
                                 [[vSpotsColocPositionsXYZ[vSelectedIDs[0]][0],
                                  vSpotsColocPositionsXYZ[vSelectedIDs[0]][1],
                                  vSpotsColocPositionsXYZ[vSelectedIDs[0]][2]]])
            else:
                messagebox.showerror(title='Reference Frame menu',
                                            message='XTension will shut down\n'
                                            'Please select one Surface and try again!')
    if qMethod == 'filament':
        vFilaments = vFactory.ToFilaments(vImarisApplication.GetSurpassSelection())
        vNumberOfFilaments = vFilaments.GetNumberOfFilaments()
        for aNextFilament in range (vNumberOfFilaments):
            qCurrentReferenceFrame.SetKeyFramesPositionsXYZT([0],
                            [[vFilaments.GetPositionsXYZ(aNextFilament)[0][0],
                            vFilaments.GetPositionsXYZ(aNextFilament)[0][1],
                            vFilaments.GetPositionsXYZ(aNextFilament)[0][2]]])
            messagebox.askyesno(title='Reference Frame menu',
                            message='Is this the correct Position?')

#Need to add option to generate a new reference frame if one does not exist

#Need to add option to move specific Reference Frame at specific time.

# #Add a new Reference Frame
# vReferenceFrames=vImarisApplication.GetFactory().CreateReferenceFrames()
# posNEWXYZ=[[0,0,0]]
# vReferenceFrames.SetKeyFramesPositionsXYZT([0],posXYZ)

# vImarisApplication.GetSurpassScene().AddChild(vReferenceFrames, -1)

