#Copy Filament to new time point
#
# Written by Matthew J. Gastinger
# June 2020 - Imaris 9.6.0
#
#    <CustomTools>
#      <Menu>
#       <Item name="Filaments Copy" icon="Python3">
#         <Command>Python3XT::XT_MJG_FilamentCopy4(%i)</Command>
#       </Item>
#      </Menu>
#      <SurpassTab>
#        <SurpassComponent name="bpFilaments">
#         <Item name="Filaments Copy" icon="Python3">
#           <Command>Python3XT::XT_MJG_FilamentCopy4(%i)</Command>
#         </Item>
#        </SurpassComponent>
#      </SurpassTab>
#    </CustomTools>

#  Description:
#  This XTension will copy the filament in the specified time point and
#  copy it to selected Destination timepoint.  All spines and dendrites
#  will be copied.   Default options will take filaments in current visible
#  timepoint to the next timepoint.

#  This process will NOT overwrite any existing filaments that may be in
#  the Destination timepoint.
#
#There is also and option to copy Filaments from a specific timepoint to all
#timepoints.   Note:  This will NOT duplicate filament in original timepoint.


import ImarisLib
import time
import random

# GUI imports
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
#aImarisId=0
def XT_MJG_FilamentCopy4(aImarisId):
    # Create an ImarisLib object
    vImarisLib = ImarisLib.ImarisLib()

# Get an imaris object with id aImarisId
    vImaris = vImarisLib.GetApplication(aImarisId)

# Get an imaris object with id aImarisId
    vImarisApplication = vImarisLib.GetApplication(aImarisId)
# Get the factory
    vFactory = vImarisApplication.GetFactory()
# Get the currently loaded dataset
    vImage = vImarisApplication.GetDataSet()
# Get the Surpass scene
    vSurpassScene = vImarisApplication.GetSurpassScene()

# Check if the object is valid
    if vImaris is None:
        print('Could not connect to Imaris!')
        messagebox.showwarning("connection failed",
                               "Could not connect to Imaris!")
        time.sleep(2)
        return

# Get the dataset
    vImage = vImaris.GetDataSet()
    if vImage is None:
        print('An image must be loaded to run this XTension!')
        messagebox.showwarning("Image needed",
                               "An image must be loaded to run this XTension!")
        time.sleep(2)
        return
############################################################################
############################################################################
#XTension start
    global vVisibleIndexT, vVisibleNextIndexT
    global vSizeT, CopyAll, Entry1,Entry2
# get the Filaments that are Selected in Surpass menu
    vFilaments = vFactory.ToFilaments(vImarisApplication.GetSurpassSelection())

#Get image properties #timepoints #channels
#Get the extents of the image
    vExtentMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vExtentMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()

#Get Timeindex that is currently Visible
    vVisibleIndexT = str(vImarisApplication.GetVisibleIndexT()+1)
    vVisibleNextIndexT = str(vImarisApplication.GetVisibleIndexT()+2)
    CopyAll=False
##################################################################
##################################################################
#dialog box
    InputBox = Tk()
    InputBox.title("Select")

    Label(InputBox,text="Original timepoint:").grid(row=0, column=0)
    Label(InputBox,text="Destination Timepoint:").grid(row=1, column=0)

#Set InputWindows to Top level window
    InputBox.attributes("-topmost", True)
    InputBox.geometry("200x70")
##################################################################
    def dialog():
        global vTimePointOriginal, vTimePointDestination
        vTimePointOriginal=Entry1.get()
        vTimePointDestination=Entry2.get()
        vTimePointDestination=int(vTimePointDestination)
        vTimePointOriginal=int(vTimePointOriginal)
        CopyAll=False
        if vTimePointDestination > vSizeT:
            messagebox.showerror(title='TimepointCopy Error',
                              message='Destination TimeFrame exceeds image timelapse - Can not copy')
            mainloop()
        else:
            InputBox.destroy()

    def All():
        global CopyAll
        CopyAll=True
        InputBox.destroy()
##################################################################
# Set Input Window to center of screen
# Gets the requested values of the height and widht.
    windowWidth = InputBox.winfo_reqwidth()
    windowHeight = InputBox.winfo_reqheight()
# Gets both half the screen width/height and window width/height
    positionRight = int(InputBox.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(InputBox.winfo_screenheight()/2 - windowHeight/2)
# Positions the window in the center of the page.
    InputBox.geometry("+{}+{}".format(positionRight, positionDown))
##################################################################
    Entry1=Entry(InputBox,justify='center',width=10)
    Entry1.grid(row=0, column=1)
    Entry1.insert(0, vVisibleIndexT)

    Entry2=Entry(InputBox,justify='center',width=10)
    Entry2.grid(row=1, column=1)
    Entry2.insert(0, vVisibleNextIndexT)

    Single=Button(InputBox, text="Single", bg='blue', fg='white',command=dialog)
    Alltime=Button(InputBox, text="Copy To All Timepoints",bg='red', command=All)
    Single.grid(row=2, column=1)
    Alltime.grid(row=2, column=0)

    mainloop()
##################################################################
##################################################################
# XT continuation
# Adjust timeIndex to fit TimeIndex start at 0
    if CopyAll==False:
        vTimePointDestination_Imaris=vTimePointDestination-1
        vTimePointOriginal_Imaris=vTimePointOriginal-1

    vNumberOfFilaments=vFilaments.GetNumberOfFilaments()
    vRGBA = vFilaments.GetColorRGBA()
    vNewFilaments=vImarisApplication.GetFactory().CreateFilaments()

# Identify Time Index for all Filaments and put into Matrix
    vTimeIndexAll=[]
    FilamentIndexAll=[]
    FilamentsIndexToCopy=[]
    for s in range (0,vNumberOfFilaments):#Wierd that this only loops twice
        vTimeIndexAll.append(vFilaments.GetTimeIndex(s))
        FilamentIndexAll.append(s)
        if vFilaments.GetTimeIndex(s)==vImarisApplication.GetVisibleIndexT():
            FilamentsIndexToCopy.append(s)
#########################################################################
#Loop all Filaments in All timepoints to duplicate starting at index "0"
    AllPoints=[]
    AllEdges=[]
    AllRadii=[]
    AllTypes=[]
    AllEdgesperFilament=[]
    AllPointperFilament=[]
    AllTimeIndexperFilament=[]
    NewFilamentCount=0
    for d in range (0,vNumberOfFilaments):
        vNumberOfEdgesPerFilament =len(vFilaments.GetEdges(d))
        AllTimeIndexperFilament.append(vFilaments.GetTimeIndex(d))
        AllPointperFilament.append(len(vFilaments.GetPositionsXYZ(d)))
        AllEdgesperFilament.append(vNumberOfEdgesPerFilament)
        AllPoints.extend(vFilaments.GetPositionsXYZ(d))
        AllEdges.extend(vFilaments.GetEdges(d))
        AllRadii.extend(vFilaments.GetRadii(d))
        AllTypes.extend(vFilaments.GetTypes(d))
        NewFilamentCount=NewFilamentCount+1

#########################################################################
# Loop each Filament in Original TimeFrame - add to new time Frame
    if CopyAll==True:
        for t in range (0,vSizeT):
            if vImarisApplication.GetVisibleIndexT()==t:
                continue
            for f in range(0,len(FilamentsIndexToCopy)):
                c=(FilamentsIndexToCopy[f])#find Indices from Original timepoint
                vNumberOfEdgesPerFilament =len(vFilaments.GetEdges(c))
                AllTimeIndexperFilament.append(t)
                AllPointperFilament.append(len(vFilaments.GetPositionsXYZ(c)))
                AllEdgesperFilament.append(vNumberOfEdgesPerFilament)
                AllPoints.extend(vFilaments.GetPositionsXYZ(c))
                AllEdges.extend(vFilaments.GetEdges(c))
                AllRadii.extend(vFilaments.GetRadii(c))
                AllTypes.extend(vFilaments.GetTypes(c))
                NewFilamentCount=NewFilamentCount+1
                DestinationTimePoint=0
    else:
        for f in range (0,len(FilamentsIndexToCopy)):
            c=(FilamentsIndexToCopy[f])#find Indices from Original timepoint
            vNumberOfEdgesPerFilament =len(vFilaments.GetEdges(c));
            AllTimeIndexperFilament.append(vTimePointDestination_Imaris)
            AllPointperFilament.append(len(vFilaments.GetPositionsXYZ(c)))
            AllEdgesperFilament.append(vNumberOfEdgesPerFilament)
            AllPoints.extend(vFilaments.GetPositionsXYZ(c))
            AllEdges.extend(vFilaments.GetEdges(c))
            AllRadii.extend(vFilaments.GetRadii(c))
            AllTypes.extend(vFilaments.GetTypes(c))
            NewFilamentCount=NewFilamentCount+1

#########################################################################
# Add new filaments
    vNewFilaments.AddFilamentsList(AllPoints,AllPointperFilament,AllRadii,AllTypes,AllEdges,AllEdgesperFilament,AllTimeIndexperFilament)
    vNewFilaments.SetName(str(vFilaments.GetName())+" copied")
    vNewFilaments.SetColorRGBA(vRGBA)
#Delete original Filament Surpass object
    vFilamentItem = vImarisApplication.GetSurpassSelection();
    vImarisApplication.GetSurpassScene().RemoveChild(vFilamentItem)

#Set all BeginningPoints for each filament - in all timepoints
    vSurpassScene.AddChild(vNewFilaments, -1)
    for g in range(0,NewFilamentCount):
        vNewFilaments.SetBeginningVertexIndex(g,0)

    if CopyAll==True:
        vImarisApplication.SetVisibleIndexT(0)
    else:
        vImarisApplication.SetVisibleIndexT(vTimePointDestination_Imaris)
