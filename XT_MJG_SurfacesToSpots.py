#Convert Surface center of homogeneous mass into Spot object

#Written by Matthew J. Gastinger
#July 2020.
#
#<CustomTools>
#      <Menu>
#       <Submenu name="Surfaces Functions">
#        <Item name="Python - Center of Mass to Spots" icon="Python3">
#          <Command>Python3XT::XT_MJG_SurfacesToSpots(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#      <SurpassTab>
#        <SurpassComponent name="bpSurfaces">
#          <Item name="Python - Center of Mass to Spots" icon="Python3">
#            <Command>Python3XT::XT_MJG_SurfacesToSpots(%i)</Command>
#          </Item>
#        </SurpassComponent>
#      </SurpassTab>
#    </CustomTools>
#
#Description
#
#This XTension wil collect the XYZ positon of the surface based on the
#center of homogeneous mass, and plot those positions as a Spots object.  It will do
#this in all time points, for all or a selected group of surfaces.

#Python libraries - no special libraries are required for this XTension


#import time
# import random

# GUI imports
# GUI imports
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog

import ImarisLib
#aImarisId=0
def XT_MJG_SurfacesToSpots(aImarisId):
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
    global Entry1, aCopyAll
    ###########################################################################
    aCopyAll=False

    root=Tk()
    root.geometry("200x50")
    #Set input as the top level window
    root.attributes("-topmost", True)
    root.title("SurfacetoSpots")

    def dialog():
        global Entry1, vNewRadius, aCopyAll
        vNewRadius=Entry1.get()
        vNewRadius=float(vNewRadius)
        aCopyAll=False
        root.destroy()

    def All():
        global Entry1, vNewRadius, aCopyAll
        aCopyAll=True
        vNewRadius=Entry1.get()
        vNewRadius=float(vNewRadius)
        root.destroy()

    ##################################################################
    #Set input in center on screen
    # Gets the requested values of the height and widht.
    windowWidth = root.winfo_reqwidth()
    windowHeight = root.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(root.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(root.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    root.geometry("+{}+{}".format(positionRight, positionDown))
    ##################################################################

    Label(root,text="New Spot Size:").grid(row=0)
    Entry1=Entry(root,justify='center',width=10)
    Entry1.grid(row=0, column=1)
    Entry1.insert(0, 5)

    Single=Button(root, text="Selected Surfaces", bg='blue', fg='white',command=dialog)
    Alltime=Button(root, text="All Surfaces",bg='red', command=All)
    Single.grid(row=2, column=1)
    Alltime.grid(row=2, column=0)

    root.mainloop()

    ############################################################################
    ############################################################################

    #Image properties
    vDataMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vDataMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vDataSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    aXvoxelSpacing= (vDataMax[0]-vDataMin[0])/vDataSize[0]
    aYvoxelSpacing= (vDataMax[1]-vDataMin[1])/vDataSize[1]
    aZvoxelSpacing = round((vDataMax[2]-vDataMin[2])/vDataSize[2],3)
    vSmoothingFactor=aXvoxelSpacing*2

    vSurfaces = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
    vNumberOfSurfaces = vSurfaces.GetNumberOfSurfaces()

    vPositionFinal = []
    vTimeIndexFinal=[]
    vSelectedSurfaces = vSurfaces.GetSelectedIndices()
    vNewSpots = vImarisApplication.GetFactory().CreateSpots()

    if aCopyAll==True:
        for i in range (vNumberOfSurfaces):
            vPositionFinal.extend(vSurfaces.GetCenterOfMass(i))
            vTimeIndexFinal.append(vSurfaces.GetTimeIndex(i))
        vSpotsRadius = [vNewRadius]*vNumberOfSurfaces
        vNewSpots.SetName('All Surfaces - ' + vSurfaces.GetName())
    else:
        for i in range (len(vSelectedSurfaces)):
            vPositionFinal.extend(vSurfaces.GetCenterOfMass(vSelectedSurfaces[i]))
            vTimeIndexFinal.append(vSurfaces.GetTimeIndex(vSelectedSurfaces[i]))
        vSpotsRadius = [vNewRadius]*len(vSelectedSurfaces)
        vNewSpots.SetName('Selected Surfaces - ' + vSurfaces.GetName())



    ##############################################################################
    vRGBA = 65535 #for yellow
    vNewSpots.SetColorRGBA(vRGBA)
    vNewSpots.Set(vPositionFinal, vTimeIndexFinal, vSpotsRadius)
    vNewSpots.SetTrackEdges(vSurfaces.GetTrackEdges())
    vSurfaces.SetVisible(0)
    vImarisApplication.GetSurpassScene().AddChild(vNewSpots, -1)
