#Spots Copy to all time points
#
# Written by Matthew J. Gastinger
# June 2020 - Imaris 9.5.1
#
#  Installation:
#
#  - Copy this file into the XTensions folder in the Imaris installation directory
#  - You will find this function in the Image Processing menu
#
#    <CustomTools>
#      <Menu>
#       <Submenu name="Spots Functions">
#        <Item name="Spots Copy to All Time Points" icon="Python3">
#          <Command>Python3XT::XT_MJG_SpotsCopyToAllTimepoints3(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#      <SurpassTab>
#        <SurpassComponent name="bpSpots">
#          <Item name="Spots Copy to All Time Points" icon="Python3">
#            <Command>Python3XT::XT_MJG_SpotsCopyToAllTimepoints3(%i)</Command>
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

import ImarisLib
# aImarisId=0
def XT_MJG_SpotsCopyToAllTimepoints3(aImarisId):
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
    vOption1=1
    #Process Spots
    #get all spots
    vSpots = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
    vNewSpots = vImarisApplication.GetFactory().CreateSpots()
    vSpotsRadius = vSpots.GetRadii()
    vSpotsPositionXYZ = vSpots.GetPositionsXYZ()
    vSpotsTime = vSpots.GetIndicesT()
    vSpotsIds = vSpots.GetIds()
    vNumberOfSpots = len(vSpotsTime)
    vCurrentTimeIndex = vImarisApplication.GetVisibleIndexT()

    vSpotsName = vSpots.GetName()
    vSpots.SetVisible(0)
    vSelectedSpotsIds = vSpots.GetSelectedIds()

    vSpotsTimeFinal= []
    vSpotsPositionXYZFinal = []
    vSpotsRadiusFinal= []
    qSpotsSelected=False
    #Remove TrackIDs ids >10000000
    vSelectedSpotsIds=[x for x in vSelectedSpotsIds if x < 1000000000]
    vNumberOfSelectedSpots = len(vSelectedSpotsIds)

    if vSelectedSpotsIds != []:
        qSpotsSelected=True
        #grab Selected Spot position and radius
        vSpotsIds=np.array(vSpotsIds)
        vSelectedSpotsIds=np.array(vSelectedSpotsIds)

        sorter = np.argsort(vSpotsIds)
        vSelectedSpotIndices=sorter[np.searchsorted(vSpotsIds, vSelectedSpotsIds, sorter=sorter)]
        if vNumberOfSelectedSpots>1:
            vSelectedPositionsXYZ=list(itemgetter(*vSelectedSpotIndices)(vSpotsPositionXYZ))
            vSelectedRadius=list(itemgetter(*vSelectedSpotIndices)(vSpotsRadius))
            vSelectedTimeIndex=list(itemgetter(*vSelectedSpotIndices)(vSpotsTime))
        else:
            vSelectedPositionsXYZ=[x[1] for x in enumerate(vSpotsPositionXYZ)
                          if x[0] in vSelectedSpotIndices]
            vSelectedRadius=[x[1] for x in enumerate(vSpotsRadius)
                          if x[0] in vSelectedSpotIndices]
            vSelectedTimeIndex=[x[1] for x in enumerate(vSpotsTime)
                          if x[0] in vSelectedSpotIndices]

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
    if vOption1==1:
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
