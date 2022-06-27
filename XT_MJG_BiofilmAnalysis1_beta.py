# Written by Matthew J. Gastinger
# June 2022 - Imaris 9.9.0
#
#<CustomTools>
    #<Menu>
        #<Submenu name="Surfaces Functions">
            #<Item name="Biofilm Analysis1_beta" icon="Python3">
                #<Command>Python3XT::XT_MJG_BiofilmAnalysis1_beta(%i)</Command>
            #</Item>
        #</Submenu>
   #</Menu>
   #<SurpassTab>
       #<SurpassComponent name="bpSurfaces">
           #<Item name="Biofilm Analysis1_beta" icon="Python3">
               #<Command>Python3XT::XT_MJG_BiofilmAnalysis1_beta(%i)</Command>
           #</SurpassComponent>
       #</SurpassTab>
#</CustomTools>

#Description:

# This XTension will measure the thickness and Roughness of isosurfaces,
# overall values and/or individual measurements using 3 methods:
# 1. Surface Mask
# 2. BioVolume (no gaps, to substratum)

# Additional overall measurements include:
# --color map of mean thickness values
# --Biomass (um3/um2)
# --BioVolume
# --Continuity Ratio (porosity)--Continuity Ratio is a dimensionless coefficient
#   that measures the continuity of the reconstructed surface. It is measured by
#   taking mean surface mask thickness divided by the mean BioVolume thickness.
#   A value of “1” represents perfect continuity through the Z-stack. Values
#   less than one, define how many gaps (holes) there are in the surface reconstruction.

import numpy as np

# GUI imports
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import time
from statistics import mean
from operator import itemgetter
from statistics import median

import ImarisLib
aImarisId=0
def XT_MJG_BiofilmAnalysis1_beta(aImarisId):
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

    vSurfaces = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())

    ############################################################################
    window = tk.Tk()
    window.title('Biofilm Analysis')
    window.geometry('350x200')
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
    global Entry1
    def Biofilm_options():
        global vOptionOverall, vOptionIndividual,vOptionSurfaceMask, vSubstratumStartSliceManual
        global vOptionSurfaceMask,vOptionBioVolume, vOptionAutoDetect
        if (var1.get() == 0) & (var2.get() == 0):
            messagebox.showerror(title='Biofilm menu',
                             message='Please Select Overall or Individual')
            window.mainloop()
        else:
            vOptionOverall=var1.get()
            vOptionIndividual=var2.get()
            vOptionSurfaceMask=var3.get()
            vOptionBioVolume=var4.get()
            vOptionAutoDetect=var5.get()
            vSubstratumStartSliceManual=[int(Entry1.get())]
            window.destroy()

    var1 = tk.IntVar(value=1)
    var2 = tk.IntVar()
    var3 = tk.IntVar()
    var4 = tk.IntVar(value=1)
    var5 = tk.IntVar(value=1)
    tk.Checkbutton(window, text='Overall Calculations',
                    variable=var1, onvalue=1, offvalue=0).grid(row=0, column=0, padx=40,sticky=W)
    tk.Checkbutton(window, text='Individual Surfaces measurements',
                    variable=var2, onvalue=1, offvalue=0).grid(row=1, column=0, padx=40,sticky=W)
    tk.Label(window, font="bold", text='Choose the Method of Measurement').grid(row=2,column=0,sticky=W)
    tk.Checkbutton(window, text='Surface Mask',
                    variable=var3, onvalue=1, offvalue=0).grid(row=3, column=0, sticky=W+S,ipadx=10)
    tk.Checkbutton(window, text='BioVolume (no gaps, to subtratum)',
                    variable=var4, onvalue=1, offvalue=0).grid(row=4, column=0,sticky=W+S,ipadx=10)
    tk.Label(window, width=30, text='Substratum start slice').grid(row=5, column=0,padx=90, sticky=W)

    Entry1=Entry(window,justify='center',width=4)
    Entry1.grid(row=5, column=0, padx=100, sticky=W)
    Entry1.insert(0, '0')
    tk.Checkbutton(window, text='AutoDetect',
                   variable=var5, onvalue=1, offvalue=0).grid(row=6, column=0, sticky=W, padx=135)
    btn = Button(window, text="Analyze Surface", command=Biofilm_options)
    btn.grid(column=0, row=8, sticky=W, padx=130)

    window.mainloop()
    ############################################################################
    #testing surface masking
    vExtendMin = (vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ())
    vExtendMax = (vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ())
    vImageSize = (vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ())
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    Xvoxelspacing= (vExtendMax[0]-vExtendMin[0])/vImageSize[0]
    Yvoxelspacing= (vExtendMax[1]-vExtendMin[1])/vImageSize[1]
    Zvoxelspacing = round((vExtendMax[2]-vExtendMin[2])/vImageSize[2],3)

    vSurfaces = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
    vNumberOfSurfaces = vSurfaces.GetNumberOfSurfaces()

    # #clone Dataset
    # vImarisDataSet = vImage.Clone()
    # #Convert to 32bit
    # import Imaris
    # vType = Imaris.tType.eTypeFloat
    # vImarisDataSet.SetType(vType)

    # Test for slected Surfaces
    vSelectedSurfaceIds = vSurfaces.GetSelectedIds()
    vSurfacesSelectedIndices = vSurfaces.GetSelectedIndices()
    vNumberOfSelectedSurfaces=len(vSurfacesSelectedIndices)
    vSurfaceIndicesAll=vSurfaces.GetIds()

    vSumSlice=[]
    if vOptionSurfaceMask==1 or vOptionBioVolume==1 and vOptionOverall==1:
    #Calculate Biovolume/BioMass
        vAllSurfaceStatistics = vSurfaces.GetStatistics()
        vSurfacesStatNames = vAllSurfaceStatistics.mNames
        vAllvSurfacesIds = vAllSurfaceStatistics.mIds
        vAllvSurfaceIdsSorted=sorted((e,i) for i,e in enumerate(vAllvSurfacesIds))

        vSurfacesStatValues = vAllSurfaceStatistics.mValues
        vSurfaceVolumeIndex=[i for i,val in enumerate(vSurfacesStatNames)
                                      if val==('Volume')]
        vSurfaceTimeIndex=[i for i,val in enumerate(vSurfacesStatNames)
                                      if val==('Time Index')]
        vSurfaceBoundingBoxAALengthZIndex=[i for i,val in enumerate(vSurfacesStatNames)
                                      if val==('BoundingBoxAA Length Z')]
        if len(vSurfaceVolumeIndex) > 1:
            vSurfacesVolume=list(itemgetter(*vSurfaceVolumeIndex)(vSurfacesStatValues))
            vSurfacesTimeIndex=list(itemgetter(*vSurfaceTimeIndex)(vSurfacesStatValues))
            vSurfacesBoundingBoxAALengthZ=list(itemgetter(*vSurfaceBoundingBoxAALengthZIndex)(vSurfacesStatValues))
        else:
            vSurfacesVolume=[x[1] for x in enumerate(vSurfacesStatValues)
                              if x[0] in vSurfaceVolumeIndex]
            vSurfacesTimeIndex=[x[1] for x in enumerate(vSurfacesStatValues)
                              if x[0] in vSurfaceTimeIndex]
            vSurfacesBoundingBoxAALengthZ=[x[1] for x in enumerate(vSurfacesStatValues)
                              if x[0] in vSurfaceBoundingBoxAALengthZIndex]

    ##############################################################################
    ##############################################################################
    vCountPixelsinSlice=[]
    vSubstratumStartSlice=[]
    vOverallMeanThicknessSurfaceMask=[]
    vOverallSubstratumArea=[]
    vOverallSubstratumAreaMean=[]
    vOverallSurfaceMaskMeanThickness=[]
    vOverallSurfaceMaskVariance=[]
    vOverallSurfaceMaskStdDev=[]
    vOverallSurfaceMaskMaxThickness=[]
    vOverallBioVolumeMaxThickness=[]
    vOverallBioVolumeMeanThickness=[]
    vOverallBioVolumeVariance=[]
    vOverallBioVolumeStdDev=[]
    vOverallBioVolumeVolume=[]
    vOverallBioMass=[]

    vIndividSurfaceMaskMeanThickness=[]
    vIndividSurfaceMaskMaxThickness=[]
    vOverallCount=0

    vTimeIndex=0
    #####################################################
    ####################################################
    if vOptionOverall==1:
        for vTimeIndex in range (vSizeT):
            vMaskDataSetBiofilm = vSurfaces.GetMask(vExtendMin[0],vExtendMin[1],vExtendMin[2],
                                                    vExtendMax[0],vExtendMax[1],vExtendMax[2],
                                                    vImageSize[0], vImageSize[1],vImageSize[2],
                                                    vTimeIndex)
        #Loop through volume stack, slice by slice, and sums the mass
            for vIndexZ in range (vImageSize[2]):
                vSlice = vMaskDataSetBiofilm.GetDataSubVolumeAs1DArrayShorts(0,0,vIndexZ,0,0,vImageSize[0],vImageSize[1],1)
                vSlice=np.array(vSlice)
                if vIndexZ==0:
                    vSliceAll=vSlice
                else:
                    vSliceAll=np.column_stack([vSliceAll,vSlice])

            if np.any(vSliceAll):
                vOverallCount=vOverallCount+1
            # else:
            #     continue

    #Calculate substratum start slice for each time point
            vNumberPixelsPerSlice=np.sum(vSliceAll > 0, axis=0)
            if vOptionAutoDetect==1:
                vSubstratumStartSlice.append(np.nonzero(vNumberPixelsPerSlice)[0][0])
            else:
                vSubstratumStartSlice.append(vSubstratumStartSliceManual[0])

    #Calculate cumulative thickness of surface mask per pixel column
    ####################################################
            # vOverallSurfaceMaskLocalThickness=np.sum(vSliceAll,axis=1).tolist()
            vOverallSurfaceMaskLocalThickness=np.sum(vSliceAll,axis=1)*Zvoxelspacing
    #Calcualte Area of Biovolume at each slice (does not include gaps)
            vOverallSurfaceMaskAreaPerSlice=np.multiply(vNumberPixelsPerSlice,Xvoxelspacing*Yvoxelspacing)
    #Substratum Area
            vOverallSubstratumArea.append(vOverallSurfaceMaskAreaPerSlice[vSubstratumStartSlice[vTimeIndex]])
            vOverallSubstratumAreaMean.append(median(vOverallSurfaceMaskAreaPerSlice[vSubstratumStartSlice[vTimeIndex]:vSubstratumStartSlice[vTimeIndex]+6]))
    #remove zeros from surface mask
            vOverallSurfaceMaskMeanThickness.append(np.mean(vOverallSurfaceMaskLocalThickness[vOverallSurfaceMaskLocalThickness>0]))
            vOverallSurfaceMaskMaxThickness.append(np.max(vOverallSurfaceMaskLocalThickness))
    ##################
            vOverallSurfaceMaskVariance.append(np.nanvar(vOverallSurfaceMaskLocalThickness[vOverallSurfaceMaskLocalThickness>0]))
            vOverallSurfaceMaskStdDev.append(np.std(vOverallSurfaceMaskLocalThickness[vOverallSurfaceMaskLocalThickness>0]))
    ####################################################
    ####################################################
    ####################################################
            #Find max non-zero index per Pixel column (no gaps to substratum)
            vOverallBioVolumeThicknessMaxIndexPerPixelColumn=(vSliceAll!=0).cumsum(1).argmax(1)
            #Add 1 to each column whose value >0
            np.add(1,vOverallBioVolumeThicknessMaxIndexPerPixelColumn,out=vOverallBioVolumeThicknessMaxIndexPerPixelColumn,
                   where=vOverallBioVolumeThicknessMaxIndexPerPixelColumn>0)

            vOverallBioVolumeThicknessMaxIndexPerPixelColumnAdjusted=vOverallBioVolumeThicknessMaxIndexPerPixelColumn-vSubstratumStartSlice[vTimeIndex]

     #Duplicate the array
            vOverallBioVolumeThicknessMaxForHeatMap=vOverallBioVolumeThicknessMaxIndexPerPixelColumnAdjusted[:]
            #create arrary for heatmap set negative value to zero
            vOverallBioVolumeThicknessMaxForHeatMap[vOverallBioVolumeThicknessMaxForHeatMap<0]=0

            vOverallBioVolumeThicknessMaxIndexPerPixelColumnAdjusted=vOverallBioVolumeThicknessMaxIndexPerPixelColumnAdjusted[vOverallBioVolumeThicknessMaxIndexPerPixelColumnAdjusted>0]
            #Statistic Thickness of Biovolume (no gaps, to substratum) per pixel column
            vOverallBioVolumeLocalThickness=vOverallBioVolumeThicknessMaxIndexPerPixelColumnAdjusted*Zvoxelspacing
            #Overall Mean thickness Biovolume per timepoint (no gaps)
            vOverallBioVolumeMeanThickness.append(np.mean(vOverallBioVolumeLocalThickness))
            #Overall Max thickness Biovolume per timepoint (no gaps)
            #vOverallBioVolumeMaxThickness.append(np.amax(vOverallBioVolumeLocalThickness)-vSubstratumStartSlice[vTimeIndex])
            vOverallBioVolumeMaxThickness.append(np.amax(vOverallBioVolumeLocalThickness))
    ##################
            vOverallBioVolumeVariance.append(np.var(vOverallBioVolumeLocalThickness))#Calculate population Variance
            vOverallBioVolumeStdDev.append(np.std(vOverallBioVolumeLocalThickness))
    ##################
            vOverallBioVolumeVolume.append(np.sum(vNumberPixelsPerSlice)*Xvoxelspacing*Yvoxelspacing*Zvoxelspacing)
            vOverallBioMass.append(np.divide(vOverallBioVolumeVolume,vOverallSubstratumAreaMean))
    ####################################################
    ####################################################
    ####################################################

    #Create heatmap
        #clone Dataset
        vImarisDataSet = vImage.Clone()
        vImarisDataSet.SetSizeC(vSizeC + 1)
        # #Convert to 32bit
        import Imaris
        vType = Imaris.tType.eTypeFloat
        vImarisDataSet.SetType(vType)

    #Create new channel
        vImarisDataSet.SetSizeC(vSizeC + 1)
        vImarisDataSet.SetChannelName(vSizeC,str('Biofilm thickness of ' + vSurfaces.GetName()))
        #looop eaxch slice and add local thickness values to channel
        for vIndexZ in range (vImageSize[2]):
            vImarisDataSet.SetDataSubVolumeAs1DArrayFloats(vOverallBioVolumeThicknessMaxForHeatMap.tolist(), 0,0,vIndexZ,vSizeC,vTimeIndex,vImageSize[0],vImageSize[1],1)
        vImarisDataSet.SetChannelRange(vSizeC,0,vOverallBioVolumeMaxThickness[vTimeIndex])
    ####################################################################################
    ####################################################################################
    #Create manual Sprectrum color table with black at bottom
        a=[5,5,5,4]*2+[5,5,4]
        a=a*2+[5,5,5,4,5]
        b=[-1024,-1280]*9+[-1024]
        b=b*3
        c=[262144,327680]*9+[262144]
        c=c*3
        d=[-4,-5]*9+[-4]
        d=d*3
        e=[1024,1280]*9+[1024]
        e=e*3
        wSpectrumColorCreate=np.array(a+b+c+d+e)
        wSpectrumColorTable=[16711808]
        wTemp=16711808
        for i in range (254):
            wSpectrumColorTable.append(wTemp-wSpectrumColorCreate[i])
            wTemp=wSpectrumColorTable[i+1]
        wSpectrumColorTable[0]=0
        #Set new channel in the volume as a Heat Map
        vImarisDataSet.SetChannelColorTable(vSizeC, wSpectrumColorTable, 0);
        vImarisApplication.SetDataSet(vImarisDataSet)
    ####################################################################################
    ####################################################################################
    ####################################################
    ####################################################
        if vOptionSurfaceMask==1:
            #Insert an overall Statistics
            vOverallStatIds=[int(-1)]
            vOverallStatUnits=['um']*vSizeT
            vOverallStatFactorsTime=list(range(1,vSizeT+1))
            vOverallStatFactors=[['Overall'],[str(i) for i in vOverallStatFactorsTime]]
            vOverallStatFactorNames=['FactorName','Time']

            ####################################################
            vOverallStatNames = [' Mean Thickness (um)(SurfaceMask)']
            vSurfaces.AddStatistics(vOverallStatNames, vOverallSurfaceMaskMeanThickness,
                                          vOverallStatUnits, vOverallStatFactors,
                                          vOverallStatFactorNames, vOverallStatIds)
            ####################################################
            vOverallStatNames = [' Max Thickness (um)(SurfaceMask)']
            vSurfaces.AddStatistics(vOverallStatNames, vOverallSurfaceMaskMaxThickness,
                                          vOverallStatUnits, vOverallStatFactors,
                                          vOverallStatFactorNames, vOverallStatIds)
            ####################################################
            vOverallStatUnits=['']*vSizeT
            vOverallStatNames = [' Roughness (Variance) (SurfaceMask)']
            vSurfaces.AddStatistics(vOverallStatNames, vOverallSurfaceMaskVariance,
                                          vOverallStatUnits, vOverallStatFactors,
                                          vOverallStatFactorNames, vOverallStatIds)
            ####################################################
            vOverallStatNames = [' Standard Deviation (SurfaceMask)']
            vSurfaces.AddStatistics(vOverallStatNames, vOverallSurfaceMaskStdDev,
                                          vOverallStatUnits, vOverallStatFactors,
                                          vOverallStatFactorNames, vOverallStatIds)
            ####################################################
            vOverallStatNames = [' Substratum StartSlice']
            vSurfaces.AddStatistics(vOverallStatNames, vSubstratumStartSlice,
                                          vOverallStatUnits, vOverallStatFactors,
                                          vOverallStatFactorNames, vOverallStatIds)
    ####################################################
    ####################################################
        if vOptionBioVolume==1:
            #Insert an overall Statistics
            vOverallStatIds=[int(-1)]
            vOverallStatUnits=['um']*vSizeT
            vOverallStatFactorsTime=list(range(1,vSizeT+1))
            vOverallStatFactors=[['Overall'],[str(i) for i in vOverallStatFactorsTime]]
            vOverallStatFactorNames=['FactorName','Time']

            ####################################################
            vOverallStatNames = [' Mean Thickness (um)(BioVolume, no gaps)']
            vSurfaces.AddStatistics(vOverallStatNames, vOverallBioVolumeMeanThickness,
                                          vOverallStatUnits, vOverallStatFactors,
                                          vOverallStatFactorNames, vOverallStatIds)
            ####################################################
            vOverallStatNames = [' Max Thickness (um)(BioVolume, no gaps)']
            vSurfaces.AddStatistics(vOverallStatNames, vOverallBioVolumeMaxThickness,
                                          vOverallStatUnits, vOverallStatFactors,
                                          vOverallStatFactorNames, vOverallStatIds)
            ####################################################
            vOverallStatUnits=['']*vSizeT
            vOverallStatNames = [' Roughness (Variance) (BioVolume)']
            vSurfaces.AddStatistics(vOverallStatNames, vOverallBioVolumeVariance,
                                          vOverallStatUnits, vOverallStatFactors,
                                          vOverallStatFactorNames, vOverallStatIds)
            ####################################################
            vOverallStatNames = [' Standard Deviation (BioVolume)']
            vSurfaces.AddStatistics(vOverallStatNames, vOverallBioVolumeStdDev,
                                          vOverallStatUnits, vOverallStatFactors,
                                          vOverallStatFactorNames, vOverallStatIds)
            ####################################################
            vOverallContinuityRatio=(np.divide(vOverallSurfaceMaskMeanThickness, vOverallBioVolumeMeanThickness)).tolist()
            vOverallStatNames = [' Continuity Ratio']
            vSurfaces.AddStatistics(vOverallStatNames, vOverallContinuityRatio,
                                          vOverallStatUnits, vOverallStatFactors,
                                          vOverallStatFactorNames, vOverallStatIds)
            ####################################################
            vOverallStatNames = [' BioMass (um3/um2)']
            vSurfaces.AddStatistics(vOverallStatNames, vOverallBioMass,
                                          vOverallStatUnits, vOverallStatFactors,
                                          vOverallStatFactorNames, vOverallStatIds)
            ####################################################
            vOverallStatNames = [' Substratum StartSlice']
            vSurfaces.AddStatistics(vOverallStatNames, vSubstratumStartSlice,
                                          vOverallStatUnits, vOverallStatFactors,
                                          vOverallStatFactorNames, vOverallStatIds)
        vSurfaces.SetName('Analyzed - Substratum Slice '+ str(vSubstratumStartSlice[0])+'--'+vSurfaces.GetName())
        vImarisApplication.GetSurpassScene().AddChild(vSurfaces, -1)




    if vOptionIndividual==1:
        wStatisticBBaa=[]
        ####################################################################
        #Get Statistics from Generation and Ids
        wStatisticNames = vSurfaces.GetStatisticsNames()
        wStatNameIndexBBaaX=[i for i,val in enumerate(wStatisticNames) if val==('BoundingBoxAA Length X')]
        wStatNameIndexBBaaY=[i for i,val in enumerate(wStatisticNames) if val==('BoundingBoxAA Length Y')]
        wStatNameIndexBBaaZ=[i for i,val in enumerate(wStatisticNames) if val==('BoundingBoxAA Length Z')]
        wStatisticValues = vSurfaces.GetStatisticsByName(wStatisticNames[wStatNameIndexBBaaX[0]])
        wStatisticBBaa=[wStatisticValues.mValues]
        wStatisticValues = vSurfaces.GetStatisticsByName(wStatisticNames[wStatNameIndexBBaaY[0]])
        wStatisticBBaa.extend([wStatisticValues.mValues])
        wStatisticValues = vSurfaces.GetStatisticsByName(wStatisticNames[wStatNameIndexBBaaZ[0]])
        wStatisticBBaa.extend([wStatisticValues.mValues])
        wStatisticIds=wStatisticValues.mIds
        wStatisticmFactor=wStatisticValues.mFactors
        #Collate all Surface BoundingBoxAA lengths XYZ
        wStatisticBBaa=np.asarray(wStatisticBBaa)
        vAllTimeIndices=[]
        for aSurfaceIndex in range (vNumberOfSurfaces):
            #Get the individual Surface mask
            vPositionXYZworking = vSurfaces.GetCenterOfMass(aSurfaceIndex)
            vAllTimeIndices.append(vSurfaces.GetTimeIndex(aSurfaceIndex))
            zMaskSingleSurface = vSurfaces.GetSingleMask(aSurfaceIndex,
                                             vDataMin[0],
                                             vDataMin[1],
                                             vDataMin[2],
                                             vDataMax[0],
                                             vDataMax[1],
                                             vDataMax[2],
                                             vDataSize[0],
                                             vDataSize[1],
                                             vDataSize[2])
            for vIndexZ in range (vImageSize[2]):
                vSlice = zMaskSingleSurface.GetDataSubVolumeAs1DArrayShorts(0,0,vIndexZ,0,0,vImageSize[0],vImageSize[1],1)
                vSlice=np.array(vSlice)
                if vIndexZ==0:
                    vSliceAll=vSlice
                else:
                    vSliceAll=np.column_stack([vSliceAll,vSlice])
                vNumberPixelsPerSlice=np.sum(vSliceAll > 0, axis=0)

            # vIndvidSurfaceMaskLocalThickness=np.sum(vSliceAll,axis=1).tolist()
            vIndividSurfaceMaskLocalThickness=np.multiply(np.sum(vSliceAll,axis=1),Zvoxelspacing)
            #Remove all zeros for the mean
            #Individual Mean thickness Biovolume per timepoint (no gaps)
            vIndividSurfaceMaskMeanThickness.append(np.mean(vIndividSurfaceMaskLocalThickness>0))
            #Overall Max thickness Biovolume per timepoint (no gaps)
            vIndividSurfaceMaskMaxThickness.append(np.amax(vIndividSurfaceMaskLocalThickness))




    #Good up to here!!!!
