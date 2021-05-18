    #<CustomTools>
        #<Menu>
            #<Submenu name="Filaments Functions">
                #<Item name="Filament Merge Starting Points" icon="Python3">
                    #<Command>Python3XT::XT_MJG_Filament_MergeStartingPoints1_beta(%i)</Command>
                #</Item>
            #</Submenu>
       #</Menu>
       #<SurpassTab>
           #<SurpassComponent name="bpFilaments">
               #<Item name="Filament Merge Starting Points" icon="Python3">
                   #<Command>Python3XT::XT_MJG_Filament_MergeStartingPoints1_beta(%i)</Command>
               #</SurpassComponent>
           #</SurpassTab>
    #</CustomTools>

import numpy as np
import time
import random
import statistics
import ImarisLib
aImarisId=0
def XT_MJG_Filament_MergeStartingPoints1_beta(aImarisId):
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

    vFilaments = vFactory.ToFilaments(vImarisApplication.GetSurpassSelection())
    vNumberOfFilaments=vFilaments.GetNumberOfFilaments()

    #Find Selected Filament IDs that is selected in the Filament Object
    vFilamentsSelectedFilamentID = vFilaments.GetSelectedIds()
    vFilamentsSelectedFilamentIDALL = vFilaments.GetIds()
    vFilamentsStartingPointIndexFINAL=vFilamentsSelectedFilamentIDALL.index(vFilamentsSelectedFilamentID[0])
    vFilamentsSelectedTimeIndex=vFilaments.GetTimeIndex(vFilamentsStartingPointIndexFINAL)

    #Grab XYZ position of NEW starting Point
    vFilamentsNEWStartingPosition=vFilaments.GetPositionsXYZ(vFilamentsStartingPointIndexFINAL)[vFilaments.GetBeginningVertexIndex(vFilamentsStartingPointIndexFINAL)]
    #Test proximity select filament starting point

    #Set empty variables
    vFilamentsXYZALL=[]
    vFilamentsRadiusALL=[]
    vFilamentsEdgesALL=[]
    vFilamentsBeginningIndexALL=[]
    vFilamentsTypesALL=[]
    vFilamentPointLengthPrevious=0
    aFilamentIndex=1
    aFilamentIndex=0

    for aFilamentIndex in range(vNumberOfFilaments):
        if vFilaments.GetTimeIndex(aFilamentIndex)==vFilamentsSelectedTimeIndex:
            vFilamentsEdgesWorking=vFilaments.GetEdges(aFilamentIndex)
            vFilamentsTypesALL.extend(vFilaments.GetTypes(aFilamentIndex))
            vFilamentsXYZALL.extend(vFilaments.GetPositionsXYZ(aFilamentIndex))
            vFilamentsRadiusALL.extend(vFilaments.GetRadii(aFilamentIndex))
            vFilamentsBeginningIndexWorking=vFilaments.GetBeginningVertexIndex(aFilamentIndex)
            #Fix/add edge to join to common point
            if aFilamentIndex == 0:
                vFilamentsEdgesALL.extend(vFilamentsEdgesWorking)
                vFilamentsBeginningIndexALL.append(vFilamentsBeginningIndexWorking+vFilamentPointLengthPrevious)
                vFilamentPointLengthPrevious=vFilamentPointLengthPrevious+len(vFilamentsEdgesWorking)+1
                if aFilamentIndex==vFilamentsStartingPointIndexFINAL:
                    vFilamentNEWSOMAIndex=vFilamentsBeginningIndexWorking
            else:#Adjust Edges Beginnning vertice by number of points in previous filament
                vFilamentsEdgesWorking=[[(i+vFilamentPointLengthPrevious) for i in row] for row in vFilamentsEdgesWorking]
                vFilamentsEdgesALL.extend(vFilamentsEdgesWorking)
                vFilamentsBeginningIndexALL.append(vFilamentsBeginningIndexWorking+vFilamentPointLengthPrevious)
                if aFilamentIndex==vFilamentsStartingPointIndexFINAL:
                    vFilamentNEWSOMAIndex=vFilamentsBeginningIndexWorking+vFilamentPointLengthPrevious
                vFilamentPointLengthPrevious=vFilamentPointLengthPrevious+len(vFilamentsEdgesWorking)+1

    #Only merge StartingPoints with 10um of slected filament startpoint
    # xDistToSomaSP = np.sqrt((vFilamentsXYZ[vBeginningVertex][0]-xContactSpotPostionWorking[0])**2 + (vFilamentsXYZ[vBeginningVertex][1]-xContactSpotPostionWorking[1])**2 +(vFilamentsXYZ[vBeginningVertex][2]-xContactSpotPostionWorking[2])**2)

    #join All starting point indices to common soma starting point
    for i in range (len(vFilamentsBeginningIndexALL)):
        if i==vFilamentsStartingPointIndexFINAL:
            continue
        else:
            vFilamentsEdgesALL.append([vFilamentsBeginningIndexALL[i],vFilamentNEWSOMAIndex])

    vNewFilaments=vImarisApplication.GetFactory().CreateFilaments()
    vNewFilaments.AddFilament(vFilamentsXYZALL, vFilamentsRadiusALL, vFilamentsTypesALL, vFilamentsEdgesALL, vFilamentsSelectedTimeIndex)
    vNewFilaments.SetBeginningVertexIndex(0, vFilamentNEWSOMAIndex)
    vNewFilaments.SetName('Merged Starting Points'+ str(vFilaments.GetName()))
    vFilaments.SetVisible(0)

    vSurpassScene.AddChild(vNewFilaments, -1)
