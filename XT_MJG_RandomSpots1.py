#Random Spots
#
#Written by Matthew J. Gastinger
#May 2025
#
    # <CustomTools>
    #     <Menu>
    #         <Submenu name="Spots Functions">
    #             <Item name="Random Spots" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_RandomSpots1(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSpots">
    #             <Item name="Random Spots" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_RandomSpots1(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #     </SurpassTab>
    # </CustomTools>

#Description
#


import ImarisLib
import numpy as np
import scipy
import scipy.stats

# GUI imports
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog

aImarisId=0
def XT_MJG_RandomSpots1(aImarisId):
    
    # Create an ImarisLib object
    vImarisLib = ImarisLib.ImarisLib()
    # Get an imaris object with id aImarisId
    vImarisApplication = vImarisLib.GetApplication(aImarisId)
    # Get the factory
    vFactory = vImarisApplication.GetFactory()
    # Get the currently loaded dataset
    vImage = vImarisApplication.GetDataSet()
    # Get the Surpass scene
    vScene = vImarisApplication.GetSurpassScene()
    
    ############################################################################
    ############################################################################
    #Get image properties #timepoints #channels
    #Get the extents of the image
    vExtendMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vExtendMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vImageSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    Xvoxelspacing= (vExtendMax[1]-vExtendMin[1])/vImageSize[1];
    vDefaultSmoothingFactor=round(Xvoxelspacing*2,2);
    
    vSpots = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
    vSpotsRadius = vSpots.GetRadii()
    vSpotsPositionXYZ = vSpots.GetPositionsXYZ()
    
    #Create random distribution within whole Volume
    # Define the boundaries of the space
    x_min, x_max = vExtendMin[0], vExtendMax[0]
    y_min, y_max = vExtendMin[1], vExtendMax[1]
    z_min, z_max = vExtendMin[2], vExtendMax[2]
    
    # Number of points to generate
    vNumberOfSpots = len(vSpotsRadius)
    
    # Generate random x and y coordinates
    x_coords = np.random.uniform(x_min, x_max, vNumberOfSpots)
    y_coords = np.random.uniform(y_min, y_max, vNumberOfSpots)
    z_coords = np.random.uniform(z_min, z_max, vNumberOfSpots)
    
    # Combine x and y coordinates into a list of points
    vRandomSpots = np.column_stack((x_coords, y_coords, z_coords)).tolist()
    vIndicesT = vSpots.GetIndicesT()
    
    #Create new Spots Object
    vNewRandomSpots = vImarisApplication.GetFactory().CreateSpots()
    vNewRandomSpots.Set(vRandomSpots, vIndicesT, vSpotsRadius)
    vNewRandomSpots.SetName(str(vSpots.GetName())+" Random Positions")
    #vNewSpotsDendrites.SetColorRGBA(vRGBA)
    #Add Random SPots to Scene
    vImarisApplication.GetSurpassScene().AddChild(vNewRandomSpots, -1)
    vSpots.SetVisible(0)




