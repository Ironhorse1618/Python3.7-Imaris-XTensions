#Spots Copy to all time points
#
# Written by Matthew J. Gastinger
# June 2020 - Imaris 9.5.1#
#
#  Installation:
#
#  - Copy this file into the XTensions folder in the Imaris installation directory
#  - You will find this function in the Image Processing menu
#
#    <CustomTools>
#      <Menu>
#       <Submenu name="Spots Functions">
#        <Item name="Spots Copy to All Time Points 2_beta" icon="Python3">
#          <Command>Python3XT::XT_MJG_CopytoAllTimePoints2_beta(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#      <SurpassTab>
#        <SurpassComponent name="bpSpots">
#          <Item name="Spots Copy to All Time Points_2_beta" icon="Python3">
#            <Command>Python3XT::XT_MJG_CopytoAllTimePoints2_beta(%i)</Command>
#          </Item>
#        </SurpassComponent>
#      </SurpassTab>
#    </CustomTools>
#
#  Description:
#
#  This XTension will copy all or selected spots/surfaces from a single time frame to
#  all of the time points.  And it will generate Track edges to connect the spots over time.


# GUI imports
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from operator import itemgetter

import ImarisLib
#aImarisId=0
def XT_MJG_CopytoAllTimePoints2_beta(aImarisId):
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

    vSurfaces = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
    vSpots = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
    ############################################################################
    ############################################################################
    vExtendMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vExtendMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vImageSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()


    ############################################################################

    #Dialog window
    ############################################################################
    window = tk.Tk()
    window.title('Spots Copy')
    #window.geometry('75x100')
    window.attributes("-topmost", True)

    ##################################################################
    #Set input in center on screen
    # Gets the requested values of the height and widht.
    windowWidth = window.winfo_reqwidth()
    windowHeight = window.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(window.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(window.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    window.geometry("+{}+{}".format(positionRight, positionDown))
    ##################################################################
    global var1, var2

    def ShapeAnalysis_Options():
        global vOption1, vOption2,vOption3, var1, var2
        vOption1=var1.get()
        vOption2=var2.get()
        # vOption3=var3.get()

        if (vOption1+vOption2)>1:
            messagebox.showerror(title='Copy menu',
                                      message='Please Choose One Option!')
            window.mainloop()
        window.destroy()

    var1 = tk.IntVar(value=1)
    var2 = tk.IntVar(value=0)
    # var3 = tk.IntVar(value=0)

    tk.Label(window, font="bold", text='Choose the Copy Method').grid(row=0,column=0)
    tk.Checkbutton(window, text='Duplicate ALL (or Selected) Spots to ALL Timepoints',
                    variable=var1, onvalue=1, offvalue=0).grid(row=1, column=0, padx=40,sticky=W)
    tk.Checkbutton(window, text='Duplicate ALL (or Selected) Spots on Current Timepoint to ALL Timepoints',
                    variable=var2, onvalue=1, offvalue=0).grid(row=2, column=0, padx=40,sticky=W)
    # tk.Checkbutton(window, text='Duplicate Spots from Current Timepoint to ALL successive Timepoints',
    #                 variable=var3, onvalue=1, offvalue=0).grid(row=4, column=0, padx=40,sticky=W)

    btn = Button(window, text="Copy Spots", bg='blue', fg='white', command=ShapeAnalysis_Options)
    btn.grid(column=0, row=5, sticky=W, padx=100)
    window.mainloop()

    ############################################################################
    #Get Image properties
    vDataMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vDataMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vDataSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    aXvoxelSpacing= (vDataMax[0]-vDataMin[0])/vDataSize[0]
    aYvoxelSpacing= (vDataMax[1]-vDataMin[1])/vDataSize[1]
    aZvoxelSpacing = round((vDataMax[2]-vDataMin[2])/vDataSize[2],3)
    ############################################################################

    #Process Spots
    #get all spots
    vSpots = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
    vNewSpots = vImarisApplication.GetFactory().CreateSpots()
    vSpotsRadius = vSpots.GetRadii()
    vSpotsPositionXYZ = vSpots.GetPositionsXYZ()
    vSpotsTime = vSpots.GetIndicesT()
    vNumberOfSpots = len(vSpotsTime)
    vCurrentTimeIndex = vImarisApplication.GetVisibleIndexT()

    vSpotsName = vSpots.GetName()
    vSpots.SetVisible(0)
    vSelectedSpotsIds = vSpots.GetSelectedIds()
    vNumberOfSelectedSpots = len(vSelectedSpotsIds)
    vSpotsTimeFinal= []
    vSpotsPositionXYZFinal = []
    vSpotsRadiusFinal= []
    qSpotsSelected=False

    if vSelectedSpotsIds != []:
        qSpotsSelected=True

        #vSelectedSpotsIds = [x for x in vSelectedSpotsIds]#add one to each in list
        #grab Selected Spot position and radius
        if vNumberOfSpots>1:
            vSelectedPositionsXYZ=list(itemgetter(*vSelectedSpotsIds)(vSpotsPositionXYZ))
            vSelectedRadius=list(itemgetter(*vSelectedSpotsIds)(vSpotsRadius))
            vSelectedTimeIndex=list(itemgetter(*vSelectedSpotsIds)(vSpotsTime))
        else:
            vSelectedPositionsXYZ=[x[1] for x in enumerate(vSpotsPositionXYZ)
                          if x[0] in vSelectedSpotsIds]
            vSelectedRadius=[x[1] for x in enumerate(vSpotsRadius)
                          if x[0] in vSelectedSpotsIds]
            vSelectedTimeIndex=[x[1] for x in enumerate(vSpotsTime)
                          if x[0] in vSelectedSpotsIds]

    ############################################################################
    #Copy selected or all spots to all timepoints
    if vOption1==1:
        if qSpotsSelected==True:
            for t in range (vSizeT):
                vTimeIndex= [t]*len(vSelectedRadius)
                vSpotsTimeFinal.extend(vTimeIndex)
                vSpotsPositionXYZFinal.extend(vSelectedPositionsXYZ)
                vSpotsRadiusFinal.extend(vSelectedRadius)
            vNewSpots.Set(vSpotsPositionXYZFinal, vSpotsTimeFinal, vSpotsRadiusFinal)
        else:
            for t in range (vSizeT):
                vTimeIndex= [t]*vNumberOfSpots
                vSpotsTimeFinal.extend(vTimeIndex)
                vSpotsPositionXYZFinal.extend(vSpotsPositionXYZ)
                vSpotsRadiusFinal.extend(vSpotsRadius)
            vNewSpots.Set(vSpotsPositionXYZFinal, vSpotsTimeFinal, vSpotsRadiusFinal)
    ############################################################################
    ############################################################################
    #Copy selected or all spots from current timepoint to all timepoints
    if vOption2==1:
        #find indices of selected spots on Current time index only
        if qSpotsSelected==True:
            vCurrentSpotIndex = [i for i, value in enumerate(vSelectedTimeIndex) if value == vCurrentTimeIndex]
            if vNumberOfSpots>1:
                vSelectedPositionsXYZ=list(itemgetter(*vCurrentSpotIndex)(vSpotsPositionXYZ))
                vSelectedRadius=list(itemgetter(*vCurrentSpotIndex)(vSpotsRadius))
                vSelectedTimeIndex=list(itemgetter(*vCurrentSpotIndex)(vSpotsTime))
            else:
                vSelectedPositionsXYZ=[x[1] for x in enumerate(vSpotsPositionXYZ)
                              if x[0] in vCurrentSpotIndex]
                vSelectedRadius=[x[1] for x in enumerate(vSpotsRadius)
                              if x[0] in vCurrentSpotIndex]
                vSelectedTimeIndex=[x[1] for x in enumerate(vSpotsTime)
                              if x[0] in vCurrentSpotIndex]
            for t in range (vSizeT):
                vTimeIndex= [t]*len(vSelectedRadius)
                vSpotsTimeFinal.extend(vTimeIndex)
                vSpotsPositionXYZFinal.extend(vSelectedPositionsXYZ)
                vSpotsRadiusFinal.extend(vSelectedRadius)
            vNewSpots.Set(vSpotsPositionXYZFinal, vSpotsTimeFinal, vSpotsRadiusFinal)
        else:
            vCurrentSpotIndex = [i for i, value in enumerate(vSpotsTime) if value == vCurrentTimeIndex]
            #Number of spots in currrent timepoint
            vNumberOfSpots=len(vCurrentSpotIndex)
            if vNumberOfSpots>1:
                vSelectedPositionsXYZ=list(itemgetter(*vCurrentSpotIndex)(vSpotsPositionXYZ))
                vSelectedRadius=list(itemgetter(*vCurrentSpotIndex)(vSpotsRadius))
                vSelectedTimeIndex=list(itemgetter(*vCurrentSpotIndex)(vSpotsTime))
            else:
                vSelectedPositionsXYZ=[x[1] for x in enumerate(vSpotsPositionXYZ)
                              if x[0] in vCurrentSpotIndex]
                vSelectedRadius=[x[1] for x in enumerate(vSpotsRadius)
                              if x[0] in vCurrentSpotIndex]
                vSelectedTimeIndex=[x[1] for x in enumerate(vSpotsTime)
                              if x[0] in vCurrentSpotIndex]
            #Number of selected spots in selected timepoint
            vNumberOfSelectedSpots=len(vSelectedTimeIndex)
            for t in range (vSizeT):
                vTimeIndex= [t]*len(vSelectedRadius)
                vSpotsTimeFinal.extend(vTimeIndex)
                vSpotsPositionXYZFinal.extend(vSelectedPositionsXYZ)
                vSpotsRadiusFinal.extend(vSelectedRadius)
            vNewSpots.Set(vSpotsPositionXYZFinal, vSpotsTimeFinal, vSpotsRadiusFinal)
    ############################################################################
    ############################################################################
    #Copy selected or all spots from current timepoint to all successive timepoints
    # if vOption3==1:
    #     if qSpotsSelected==True:
    #         if vNumberOfSpots>1:
    #             vSelectedPositionsXYZ=list(itemgetter(*vCurrentSpotIndex)(vSpotsPositionXYZ))
    #             vSelectedRadius=list(itemgetter(*vCurrentSpotIndex)(vSpotsRadius))
    #             vSelectedTimeIndex=list(itemgetter(*vCurrentSpotIndex)(vSpotsTime))
    #         else:
    #             vSelectedPositionsXYZ=[x[1] for x in enumerate(vSpotsPositionXYZ)
    #                           if x[0] in vCurrentSpotIndex]
    #             vSelectedRadius=[x[1] for x in enumerate(vSpotsRadius)
    #                           if x[0] in vCurrentSpotIndex]
    #             vSelectedTimeIndex=[x[1] for x in enumerate(vSpotsTime)
    #                           if x[0] in vCurrentSpotIndex]
    #         for i in range (vNumberOfSelectedSpots):
    #             vSelectedPositionsXYZ[i]
    #             vSelectedRadius[i]
    #             vSelectedTimeIndex[i]
    #             vSizeT-vSelectedTimeIndex[i]
    #             vSpotsPositionXYZFinal.extend([vSelectedPositionsXYZ[i]]*(vSizeT-vSelectedTimeIndex[i]))
    #             vSpotsRadiusFinal.extend([vSelectedRadius[i]]*(vSizeT-vSelectedTimeIndex[i]))










    if vOption1==1 or vOption2==1:
        if qSpotsSelected==True:
            vSpotsIndicesFinal1=list(range(int((vSizeT-1)*vNumberOfSelectedSpots)))
            vSpotsIndicesFinal2=[x + vNumberOfSelectedSpots for x in vSpotsIndicesFinal1]
            vTrackEdges=[]
            #Populate track edges [0,1],[1,2],[2,3], etc
            for i in range (len(vSpotsIndicesFinal1)):
                vTrackEdges.append([vSpotsIndicesFinal1[i],vSpotsIndicesFinal2[i]])
        else:
            #Generate artificial Track edges for all spots in timelapse
            vSpotsIndicesFinal1=list(range(int((vSizeT-1)*vNumberOfSpots)))
            vSpotsIndicesFinal2=[x + vNumberOfSpots for x in vSpotsIndicesFinal1]
            vTrackEdges=[]
            #Populate track edges [0,1],[1,2],[2,3], etc
            for i in range (len(vSpotsIndicesFinal1)):
                vTrackEdges.append([vSpotsIndicesFinal1[i],vSpotsIndicesFinal2[i]])


    ###################################################################
    ###################################################################

    vNewSpots.SetTrackEdges(vTrackEdges)
    vNewSpots.SetName(str(vSpots.GetName())+" copied to all timepoints")
    vRGBA = vSpots.GetColorRGBA()
    vNewSpots.SetColorRGBA(vRGBA)
    vSurpassScene.AddChild(vNewSpots, -1)
