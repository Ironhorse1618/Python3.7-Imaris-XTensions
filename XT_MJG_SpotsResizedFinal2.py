#Resize Spots

# Written by Matthew J. Gastinger
# June 2020 - Imaris 9.5.1


#    <CustomTools>
#      <Menu>
#       <Submenu name="Spots Functions">
#        <Item name="Spots Resized" icon="Python3">
#          <Command>Python3XT::XT_MJG_SpotsResizedFinal2(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#      <SurpassTab>
#        <SurpassComponent name="bpSpots">
#          <Item name="Spots Resized" icon="Python3">
#            <Command>Python3XT::XT_MJG_SpotsResizedFinal2(%i)</Command>
#          </Item>
#        </SurpassComponent>
#      </SurpassTab>
#    </CustomTools>

#Description:
#Resize all Spots to defined diameter (default if not spot are selected)
#If a only a selected group of spots are selected, only thos will be resize.



import ImarisLib
import time
import random

# GUI imports
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog

#aImarisId=0
def XT_MJG_SpotsResizedFinal2(aImarisId):
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

############################################################################
############################################################################

#testing surface masking
    vExtendMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vExtendMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vImageSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())

# get all spots in selected Surpass object
    vSpots = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
    vSpotsRadius = vSpots.GetRadii()
    vSpotsPositionXYZ = vSpots.GetPositionsXYZ()
    vSpotsTime = vSpots.GetIndicesT()
    vAllSpotsIds = vSpots.GetIds()
    vNumberOfSpots = len(vSpotsTime)
    vSelectedSpotsIds = vSpots.GetSelectedIds()
    vNewSpots = vImarisApplication.GetFactory().CreateSpots()

    root = tk.Tk()
    root.eval('tk::PlaceWindow . center')
    root.withdraw()
    root.attributes("-topmost", True)

    # w = root.winfo_reqwidth()
    # h = root.winfo_reqheight()
    # ws = root.winfo_screenwidth()
    # hs = root.winfo_screenheight()
    # x = (ws/2) - (w/2)
    # y = (hs/2) - (h/2)
    # root.geometry('+%d+%d' % (x, y))

#Set new Spot size
    if vSpotsRadius!=[]:
        vNewSpotDiameter = simpledialog.askfloat('Set new Spot Size',
                                'NEW Spot Diameter: ', initialvalue=(round(float(vSpotsRadius[0]),2))*2)
        root.destroy()
    else:
        messagebox.showwarning("Resize Spot Fail",
                               "Please generate some Spots!")
        root.destroy()

    if len(vSelectedSpotsIds)==0:#checks if list is empty
        vNewSpotsRadius = [vNewSpotDiameter/2]*vNumberOfSpots
        vNewSpots.Set(vSpotsPositionXYZ, vSpotsTime, vNewSpotsRadius)
        vNewSpots.SetTrackEdges(vSpots.GetTrackEdges())
        vNewSpots.SetName(str(vSpots.GetName()) + ' Resized All')

    else:
        for s in range (len(vSelectedSpotsIds)):
            vCurrentSpotId = vSelectedSpotsIds[s]
            vCurrentIndex=vAllSpotsIds.index(vCurrentSpotId)#Find specific index
            vSpotsRadius[vCurrentIndex]=vNewSpotDiameter/2
        vNewSpots.Set(vSpotsPositionXYZ, vSpotsTime, vSpotsRadius)
        vNewSpots.SetName(str(vSpots.GetName()) + ' Resized Selected')


#Set Track edges if present
    vNewSpots.SetTrackEdges(vSpots.GetTrackEdges())
#Create the a new Spots with new size including tracks if they are there
    vRGBA = vSpots.GetColorRGBA()
    vNewSpots.SetColorRGBA(vRGBA)

    vSpots.SetVisible(0)
    vImarisApplication.GetSurpassScene().AddChild(vNewSpots, -1)
