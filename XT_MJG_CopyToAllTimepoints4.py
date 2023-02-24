#Copy to all time points
#
# Written by Matthew J. Gastinger
# June 2022 - Imaris 10
#
#  Installation:
#
#  - Copy this file into the XTensions folder in the Imaris installation directory
#  - You will find this function in the Image Processing menu
#
#    <CustomTools>
#      <Menu>
#       <Submenu name="Spots Functions">
#        <Item name="Copy to All Time Points" icon="Python3">
#          <Command>Python3XT::XT_MJG_CopyToAllTimepoints4(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#      <SurpassTab>
#        <SurpassComponent name="bpSpots">
#          <Item name="Copy to All Time Points" icon="Python3">
#            <Command>Python3XT::XT_MJG_CopyToAllTimepoints4(%i)</Command>
#          </Item>
#        </SurpassComponent>
#      </SurpassTab>
#      <Menu>
#       <Submenu name="Surfaces Functions">
#        <Item name="Copy to All Time Points" icon="Python3">
#          <Command>Python3XT::XT_MJG_CopyToAllTimepoints4(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#      <SurpassTab>
#        <SurpassComponent name="bpSurfaces">
#          <Item name="Copy to All Time Points" icon="Python3">
#            <Command>Python3XT::XT_MJG_CopyToAllTimepoints4(%i)</Command>
#          </Item>
#        </SurpassComponent>
#      </SurpassTab>
#    </CustomTools>
#
#  Description:
#
#  This XTension will copy all or selected spots/surfaces from a single time frame to
#  all of the time points.  And it will generate Track edges to connect the spots over time.


from operator import itemgetter
import numpy as np

# GUI imports
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import ImarisLib


aImarisId=0
def XT_MJG_CopyToAllTimepoints4(aImarisId):
    # Create an ImarisLib object
    vImarisLib = ImarisLib.ImarisLib()
    #Get an imaris object with id aImarisId
    vImarisApplication = vImarisLib.GetApplication(aImarisId)
    # Get the factory
    vFactory = vImarisApplication.GetFactory()
    # Get the currently loaded dataset
    vImage = vImarisApplication.GetDataSet()
    # Get the Surpass scene
    vSurpassScene = vImarisApplication.GetSurpassScene()
    
    
    ########################################################################
    ########################################################################
    # Create the master object
    master = tk.Tk()
    # Create a progressbar widget
    qProgressBar = ttk.Progressbar(master, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    # And a label for it
    label_1 = tk.Label(master, text="Object Copy to All timepoints")
    # Use the grid manager
    label_1.grid(row=0, column=0,pady=10)
    qProgressBar.grid(row=0, column=1)
    master.geometry('270x50')
    master.attributes("-topmost", True)
    #######################
    #Set input in center on screen
    # Gets the requested values of the height and widht.
    windowWidth = master.winfo_reqwidth()
    windowHeight = master.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(master.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(master.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    master.geometry("+{}+{}".format(positionRight, positionDown))
    #######################
    # Necessary, as the master object needs to draw the progressbar widget
    # Otherwise, it will not be visible on the screen
    master.update()
    qProgressBar['value'] = 0
    master.update()
    ########################################################################
    ########################################################################
    
    vSurpassObject = vImarisApplication.GetSurpassSelection()
    qIsSurface=vImarisApplication.GetFactory().IsSurfaces(vSurpassObject)
    qIsSpot=vImarisApplication.GetFactory().IsSpots(vSurpassObject)
    vCurrentTimeIndex = vImarisApplication.GetVisibleIndexT()
    
    if qIsSpot:
        vObject = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
        vObjectPositionXYZ = vObject.GetPositionsXYZ()
        vObjectRadius = vObject.GetRadiiXYZ()
        vObjectTimeIndices = vObject.GetIndicesT()
        vNewObject = vImarisApplication.GetFactory().CreateSpots()
        vIds = vObject.GetIds()
        vSelectedObjectIds = vObject.GetSelectedIds()
    
    else:
        vObject = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
        vNewObject = vImarisApplication.GetFactory().CreateSurfaces()
        vIds = vObject.GetIds()
        vSelectedObjectIds = vObject.GetSelectedIds()
    
    ############################################################################
    #Get Image properties
    vDataMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vDataMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vDataSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    aXvoxelSpacing = (vDataMax[0]-vDataMin[0])/vDataSize[0]
    aYvoxelSpacing = (vDataMax[1]-vDataMin[1])/vDataSize[1]
    aZvoxelSpacing = round((vDataMax[2]-vDataMin[2])/vDataSize[2],3)
    ############################################################################
    
    vObjectTimeFinal = []
    vSpotsPositionXYZFinal = []
    vSpotsRadiusFinal = []
    qObjectSelected = False
    #Remove TrackIDs ids >10000000
    vSelectedObjectIds = [x for x in vSelectedObjectIds if x < 1000000000]
    vNumberOfSelectedObjects = len(vSelectedObjectIds)
    
    if vSelectedObjectIds != []:
        qObjectSelected = True
        #grab Selected Spot position and radius
        vIds=np.array(vIds)
        vSelectedObjectIds=np.array(vSelectedObjectIds)
        sorter = np.argsort(vIds)
        vSelectedObjectIndices=sorter[np.searchsorted(vIds, vSelectedObjectIds, sorter=sorter)]
        if qIsSpot:
            if vNumberOfSelectedObjects>1:
                vSelectedPositionsXYZ = list(itemgetter(*vSelectedObjectIndices)(vObjectPositionXYZ))
                vSelectedRadius = list(itemgetter(*vSelectedObjectIndices)(vObjectRadius))
                vSelectedTimeIndex = list(itemgetter(*vSelectedObjectIndices)(vObjectTimeIndices))
            else:
                vSelectedPositionsXYZ = [x[1] for x in enumerate(vObjectPositionXYZ)
                              if x[0] in vSelectedObjectIndices]
                vSelectedRadius = [x[1] for x in enumerate(vObjectRadius)
                              if x[0] in vSelectedObjectIndices]
                vSelectedTimeIndex = [x[1] for x in enumerate(vObjectTimeIndices)
                              if x[0] in vSelectedObjectIndices]
    
    ############################################################################
    #Copy selected or all spots to all timepoints
    if qObjectSelected == True:
        if qIsSpot:
            for t in range (vSizeT):
                vTimeIndex = [t]*vNumberOfSelectedObjects
                vObjectTimeFinal.extend(vTimeIndex)
                vSpotsPositionXYZFinal.extend(vSelectedPositionsXYZ)
                vSpotsRadiusFinal.extend(vSelectedRadius)
            vNewObject.Set(vSpotsPositionXYZFinal, vObjectTimeFinal, np.array(vSpotsRadiusFinal)[:,0])
        else:#for surfaces
            for t in range (vSizeT):
                for aIdIndex in range (vNumberOfSelectedObjects):
                    vNewObject.AddSurfaceWithNormals(vObject.GetSurfaceData( np.where(vIds == vSelectedObjectIds[aIdIndex])[0].tolist()[0]),
                                                 vObject.GetSurfaceNormals( np.where(vIds == vSelectedObjectIds[aIdIndex])[0].tolist()[0]),
                                                 t)
                qProgressBar['value'] = t/vSizeT*100
                master.update()
    else:
        if qIsSpot:
            for t in range (vSizeT):
                vTimeIndex= [t]*vSizeT
                vObjectTimeFinal.extend(vTimeIndex)
                vSpotsPositionXYZFinal.extend(vObjectPositionXYZ)
                vSpotsRadiusFinal.extend(vObjectRadius)
            np.array(vSpotsRadiusFinal)[:,0]
            vNewObject.Set(vSpotsPositionXYZFinal, vObjectTimeFinal, np.array(vSpotsRadiusFinal)[:,0])
        else: #for surfaces
            for t in range (vSizeT):
                for aIdIndex in range (len(vIds)):
                    vNewObject.AddSurfaceWithNormals(vObject.GetSurfaceData(vIds[aIdIndex]),
                                                     vObject.GetSurfaceNormals(vIds[aIdIndex]),
                                                     t)
                qProgressBar['value'] = t/vSizeT*100
                master.update()
    
    ############################################################################
    
    if qObjectSelected == True:
        vObjectIndicesFinal1 = list(range(int((vSizeT-1)*vNumberOfSelectedObjects)))
        vObjectIndicesFinal2 = [x + vNumberOfSelectedObjects for x in vObjectIndicesFinal1]
        vTrackEdges = []
        #Populate track edges [0,1],[1,2],[2,3], etc
        for i in range (len(vObjectIndicesFinal1)):
            vTrackEdges.append([vObjectIndicesFinal1[i],vObjectIndicesFinal2[i]])
    else:
        #Generate artificial Track edges for all spots in timelapse
        vObjectIndicesFinal1 = list(range(int((vSizeT-1)*len(vIds))))
        vObjectIndicesFinal2 = [x + len(vIds) for x in vObjectIndicesFinal1]
        vTrackEdges = []
        #Populate track edges [0,1],[1,2],[2,3], etc
        for i in range (len(vObjectIndicesFinal1)):
            vTrackEdges.append([vObjectIndicesFinal1[i],vObjectIndicesFinal2[i]])
    
    ###################################################################
    ###################################################################
    
    vNewObject.SetTrackEdges(vTrackEdges)
    vNewObject.SetName(str(vObject.GetName())+" copied to all timepoints")
    vRGBA = vObject.GetColorRGBA()
    vNewObject.SetColorRGBA(vRGBA)
    vSurpassScene.AddChild(vNewObject, -1)
    vObject.SetVisible(0)
    
    master.destroy()
    master.mainloop()
