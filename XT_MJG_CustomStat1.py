#Written by Matthew J. Gastinger
#For Imaris 11
#Jan2025
    # <CustomTools>
    #     <Menu>
    #         <Submenu name="Spots Functions">
    #             <Item name="Custom Statistic" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_CustomStat1(%i)</Command>
    #             </Item>
    #         </Submenu>
    #         <Submenu name="Surfaces Functions">
    #             <Item name="Custom Statistic" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_CustomStat1(%i)</Command>
    #             </Item>
    #         </Submenu>
    #         <Submenu name="Filamernts Functions">
    #             <Item name="Custom Statistic" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_CustomStat1(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSpots">
    #             <Item name="Custom Statistic" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_CustomStat1(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #         <SurpassComponent name="bpSurfaces">
    #             <Item name="Custom Statistic" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_CustomStat1(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #         <SurpassComponent name="bpFilaments">
    #             <Item name="Custom Statistic" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_CustomStat1(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #     </SurpassTab>
    # </CustomTools>


# GUI imports - builtin
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog

# import sympy as sp
# from sympy import symbols, lambdify
import numexpr as ne

import ImarisLib
import numpy as np
from numpy import inf
import time
import sys
import math
import itertools


#aImarisId=0
def XT_MJG_CustomStat1(aImarisId):
    global vDataSize, wCustomStat1, wCustomStat2, wCustomStat3, vEntry_Formula_Value
    global vStatNameCustom, vUnitNameCustom
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
    
    vSurpassObject = vImarisApplication.GetSurpassSelection()
    qIsSurface=vImarisApplication.GetFactory().IsSurfaces(vSurpassObject)
    qIsSpot=vImarisApplication.GetFactory().IsSpots(vSurpassObject)
    qIsFilament = vImarisApplication.GetFactory().IsFilaments(vSurpassObject)
    qIsCells = vImarisApplication.GetFactory().IsCells(vSurpassObject)
    
    if qIsSpot:
        vObject = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
        vObjectPositionsXYZ = vObject.GetPositionsXYZ()
        vObjectRadius = vObject.GetRadiiXYZ()
        vObjectTimeIndices = vObject.GetIndicesT()
        vIds = vObject.GetIds()
    elif qIsSurface:
        vObject = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
        vIds = vObject.GetIds()
    elif qIsFilament:
        vObject = vFactory.ToFilaments(vImarisApplication.GetSurpassSelection())
    elif qIsCells:
        vObject = vFactory.ToCells(vImarisApplication.GetSurpassSelection())
    
    
    vNumberOfChannelsList = list(range(1,vImage.GetSizeC()+1))
    ############################################################################
    #Image Properties
    vDataMin = [vImage.GetExtendMinX(),vImage.GetExtendMinY(),vImage.GetExtendMinZ()]
    vDataMax = [vImage.GetExtendMaxX(),vImage.GetExtendMaxY(),vImage.GetExtendMaxZ()]
    vDataSize = [vImage.GetSizeX(),vImage.GetSizeY(),vImage.GetSizeZ()]
    vSizeT = vImage.GetSizeT()
    vSizeC = vImage.GetSizeC()
    vType = vImage.GetType()
    aXvoxelSpacing= (vDataMax[0]-vDataMin[0])/vDataSize[0]
    aYvoxelSpacing= (vDataMax[1]-vDataMin[1])/vDataSize[1]
    aZvoxelSpacing = round((vDataMax[2]-vDataMin[2])/vDataSize[2],3)
    
    qTotalMeanIntensity = 0
    #####################################################
    #Making the Listbox for the Surpass menu
    window = Tk()
    window.title("Custom Statistic Creation")
    window.geometry("700x250")
    window.attributes("-topmost", True)
    
    #################################################################
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
    def SubsetFilament():
        global vStatNamesFilamentAll, w1, w2, w3
        global wCustomStat1, wCustomStat2, wCustomStat3, vUnitNameCustom
        global qPerimeter, qSAtoVolumeRatio, qTotalMeanIntensity
        global qSelectedChannels, vStatNameCustom, vEntry_Formula_Value, qIsTrackStat    
        vStatNamesFilamentAll = np.unique(vStatisticsALL.mNames)[np.where(['Filament' in item for item in np.unique(vStatisticsALL.mNames)])[0].tolist()].tolist()
        if vStatNamesFilamentAll == []:
            messagebox.showerror(title='No Filaments Detected',
                          message='Create Filaments to use this')
            window.mainloop()    
        vStatNamesFilamentAll = [item for item in vStatNamesFilamentAll if "Total" not in item]
        vStatNamesFilamentAll = [item for item in vStatNamesFilamentAll if "Filament No. Segment Branches" not in item]
        vStatNamesFilamentAll = [item for item in vStatNamesFilamentAll if "Filament No. Sholl Intersections" not in item]
        vStatNamesFilamentAll = [item for item in vStatNamesFilamentAll if "per" not in item]
        w1 = OptionMenu(window, wCustomStat1, *vStatNamesFilamentAll).grid(row=3, column=0,padx=30, sticky=W)
        w2 = OptionMenu(window, wCustomStat2, *vStatNamesFilamentAll).grid(row=4, column=0,padx=30, sticky=W)
        w3 = OptionMenu(window, wCustomStat3, *vStatNamesFilamentAll).grid(row=5, column=0,padx=30, sticky=W)
        wCustomStat1.set("Filament Stat1") # default value
        wCustomStat2.set("Filament Stat2") # default value
        wCustomStat3.set("Filament Stat3") # default value
        vUnitNameCustom = Entry_UnitName.get()
        window.update()
        window.mainloop()
        
    def SubsetSegment():
        global vStatNamesSegmentAll, w1, w2, w3
        global wCustomStat1, wCustomStat2, wCustomStat3,vUnitNameCustom
        global qPerimeter, qSAtoVolumeRatio, qTotalMeanIntensity
        global qSelectedChannels, vStatNameCustom, vEntry_Formula_Value, qIsTrackStat    
        vStatNamesSegmentAll = np.unique(vStatisticsALL.mNames)[np.where(['Segment' in item for item in np.unique(vStatisticsALL.mNames)])[0].tolist()].tolist()
        if vStatNamesSegmentAll == []:
            messagebox.showerror(title='No Segments Detected',
                          message='Create segments to use this')
            window.mainloop()
        vStatNamesSegmentAll = [item for item in vStatNamesSegmentAll if "Filament" not in item]
        w1 = OptionMenu(window, wCustomStat1, *vStatNamesSegmentAll).grid(row=3, column=0,padx=30, sticky=W)
        w2 = OptionMenu(window, wCustomStat2, *vStatNamesSegmentAll).grid(row=4, column=0,padx=30, sticky=W)
        w3 = OptionMenu(window, wCustomStat3, *vStatNamesSegmentAll).grid(row=5, column=0,padx=30, sticky=W)
        wCustomStat1.set("Segment Stat1") # default value
        wCustomStat2.set("Segment Stat2") # default value
        wCustomStat3.set("Segment Stat3") # default value 
        vUnitNameCustom = Entry_UnitName.get()
        window.update()
        window.mainloop()
        
    def SubsetSpines():
        global vStatNamesSpineAll, w1, w2, w3
        global wCustomStat1, wCustomStat2, wCustomStat3, vUnitNameCustom
        global qPerimeter, qSAtoVolumeRatio, qTotalMeanIntensity
        global qSelectedChannels, vStatNameCustom, vEntry_Formula_Value, qIsTrackStat
        vStatNamesSpineAll = np.unique(vStatisticsALL.mNames)[np.where(['Spine' in item for item in np.unique(vStatisticsALL.mNames)])[0].tolist()].tolist()
        if vStatNamesSpineAll == []:
            messagebox.showerror(title='No Spines Detected',
                          message='Create spines to use this')
            window.mainloop()
        
        
        vStatNamesSpineAll = [item for item in vStatNamesSpineAll if "Branch" not in item]
        vStatNamesSpineAll = [item for item in vStatNamesSpineAll if "Branchings" not in item]  
        vStatNamesSpineAll = [item for item in vStatNamesSpineAll if "Filament" not in item]  
        vStatNamesSpineAll = [item for item in vStatNamesSpineAll if "Pt" not in item]  
        w1 = OptionMenu(window, wCustomStat1, *vStatNamesSpineAll).grid(row=3, column=0,padx=30, sticky=W)
        w2 = OptionMenu(window, wCustomStat2, *vStatNamesSpineAll).grid(row=4, column=0,padx=30, sticky=W)
        w3 = OptionMenu(window, wCustomStat3, *vStatNamesSpineAll).grid(row=5, column=0,padx=30, sticky=W)
        wCustomStat1.set("Spine Stat1") # default value
        wCustomStat2.set("Spine Stat2") # default value
        wCustomStat3.set("Spine Stat3") # default value
        vUnitNameCustom = Entry_UnitName.get()
        window.update()
        window.mainloop()
        
    def SubsetNucleus():
        global vStatNamesNucleusAll, w1, w2, w3
        global wCustomStat1, wCustomStat2, wCustomStat3, vUnitNameCustom
        global qPerimeter, qSAtoVolumeRatio, qTotalMeanIntensity
        global qSelectedChannels, vStatNameCustom, vEntry_Formula_Value, qIsTrackStat
        vStatNamesNucleusAll = np.unique(vStatisticsALL.mNames)[np.where(['Nucleus' in item for item in np.unique(vStatisticsALL.mNames)])[0].tolist()].tolist()
        if vStatNamesNucleusAll == []:
            messagebox.showerror(title='No Nuclei Detected',
                          message='Create nuclei to use this')
            window.mainloop()
        vStatNamesNucleusAll = [item for item in vStatNamesNucleusAll if "Cell" not in item]
        vStatNamesNucleusAll = [item for item in vStatNamesNucleusAll if "Type" not in item]  
        w1 = OptionMenu(window, wCustomStat1, *vStatNamesNucleusAll).grid(row=3, column=0,padx=30, sticky=W)
        w2 = OptionMenu(window, wCustomStat2, *vStatNamesNucleusAll).grid(row=4, column=0,padx=30, sticky=W)
        w3 = OptionMenu(window, wCustomStat3, *vStatNamesNucleusAll).grid(row=5, column=0,padx=30, sticky=W)
        wCustomStat1.set("Nucleus Stat1") # default value
        wCustomStat2.set("Nucleus Stat2") # default value
        wCustomStat3.set("Nuclues Stat3") # default value
        vUnitNameCustom = Entry_UnitName.get()
        window.update()
        window.mainloop()
        
    def SubsetCells():
        global vStatNamesCellAll, w1, w2, w3
        global wCustomStat1, wCustomStat2, wCustomStat3, vUnitNameCustom
        global qPerimeter, qSAtoVolumeRatio, qTotalMeanIntensity
        global qSelectedChannels, vStatNameCustom, vEntry_Formula_Value, qIsTrackStat
        vStatNamesCellAll = np.unique(vStatisticsALL.mNames)[np.where(['Cell' in item for item in np.unique(vStatisticsALL.mNames)])[0].tolist()].tolist()
        vStatNamesCellAll = [item for item in vStatNamesCellAll if "Type" not in item]
        vStatNamesCellAll = [item for item in vStatNamesCellAll if "Total" not in item]
        vStatNamesCellAll = [item for item in vStatNamesCellAll if "per" not in item]
        vStatNamesCellAll = [item for item in vStatNamesCellAll if "Nucleus Distance" not in item]
        w1 = OptionMenu(window, wCustomStat1, *vStatNamesCellAll).grid(row=3, column=0,padx=30, sticky=W)
        w2 = OptionMenu(window, wCustomStat2, *vStatNamesCellAll).grid(row=4, column=0,padx=30, sticky=W)
        w3 = OptionMenu(window, wCustomStat3, *vStatNamesCellAll).grid(row=5, column=0,padx=30, sticky=W)
        wCustomStat1.set("Cells Stat1") # default value
        wCustomStat2.set("Cells Stat2") # default value
        wCustomStat3.set("Cells Stat3") # default value 
        vUnitNameCustom = Entry_UnitName.get()
    
        window.update() 
        window.mainloop()
    
    def SubsetVesicles():
        global vStatNamesVesiclesAll, w1, w2, w3
        global wCustomStat1, wCustomStat2, wCustomStat3
        global qPerimeter, qSAtoVolumeRatio, qTotalMeanIntensity, vUnitNameCustom
        global qSelectedChannels, vStatNameCustom, vEntry_Formula_Value, qIsTrackStat
        vStatNamesVesiclesAll = np.unique(vStatisticsALL.mNames)[np.where(['Vesicles' in item for item in np.unique(vStatisticsALL.mNames)])[0].tolist()].tolist()
        if vStatNamesVesiclesAll == []:
            messagebox.showerror(title='No Vesicles Detected',
                          message='Create vesicles to use this')
            window.mainloop()
        vStatNamesVesiclesAll = [item for item in vStatNamesVesiclesAll if "Cell" not in item]
        vStatNamesVesiclesAll = [item for item in vStatNamesVesiclesAll if "Total" not in item]
        vStatNamesVesiclesAll = [item for item in vStatNamesVesiclesAll if "per" not in item]
        vStatNamesVesiclesAll = [item for item in vStatNamesVesiclesAll if "Number" not in item]
        w1 = OptionMenu(window, wCustomStat1, *vStatNamesVesiclesAll).grid(row=3, column=0,padx=30, sticky=W)
        w2 = OptionMenu(window, wCustomStat2, *vStatNamesVesiclesAll).grid(row=4, column=0,padx=30, sticky=W)
        w3 = OptionMenu(window, wCustomStat3, *vStatNamesVesiclesAll).grid(row=5, column=0,padx=30, sticky=W)
        wCustomStat1.set("Vesicles Stat1") # default value
        wCustomStat2.set("Vesicles Stat2") # default value
        wCustomStat3.set("Vesicles Stat3") # default value  
        vUnitNameCustom = Entry_UnitName.get()
    
        
        window.update()
        window.mainloop()
    
    def CustomTrackStat():
        global wCustomTrackStat1, wCustomTrackStat3, wCustomTrackStat3
        global qPerimeter, qSAtoVolumeRatio, qTotalMeanIntensity, vUnitNameCustom
        global qSelectedChannels, vStatNameCustom, vEntry_Formula_Value, qIsTrackStat
        wCustomTrackStat1.get()
        wCustomTrackStat2.get()
        wCustomTrackStat3.get()
        vUnitNameCustom = Entry_UnitName.get()
        qPerimeter = var1.get()
        qSAtoVolumeRatio = var2.get()
        qTotalMeanIntensity = var3.get()
        qSelectedChannels = var4.get()
        
        if "Intensity" in wCustomTrackStat1.get():
            wChannelStat1.get()
            if wChannelStat1.get() == 'Ch#':
                messagebox.showerror(title='Channel Selection',
                              message='Please Select Channel')
                window.mainloop()
        elif "Intensity" in wCustomTrackStat2.get():
            wChannelStat2.get()
            if wChannelStat2.get() == 'Ch#':
                messagebox.showerror(title='Channel Selection',
                              message='Please Select Channel')
                window.mainloop()
        elif "Intensity" in wCustomTrackStat3.get():
            wChannelStat3.get()
            if wChannelStat3.get() == 'Ch#':
                messagebox.showerror(title='Channel Selection',
                              message='Please Select Channel')
                window.mainloop()   
        vEntry_Formula_Value = Entry_Formula.get()
        vStatNameCustom = Entry_StatName.get()
        qIsTrackStat = 1
        window.destroy()
    
    def CustomStat():
        global wCustomStat1, wCustomStat2, wCustomStat3, vEntry_Formula_Value, vUnitNameCustom
        global wChannelStat1, wChannelStat2, wChannelStat3, qIsTrackStat,vDataSize
        global qPerimeter, qSAtoVolumeRatio, qTotalMeanIntensity, qSelectedChannels, vStatNameCustom
        qIsTrackStat = 0
        qPerimeter = var1.get()
        qSAtoVolumeRatio = var2.get()
        if qIsFilament:
            if "Filament" in (wCustomStat1.get()) or "Filament" in (wCustomStat2.get()) or "Filament" in (wCustomStat3.get()):
                qIsStat1Valid = 'Filament' in wCustomStat1.get() or 'Choose Stat1' in wCustomStat1.get()
                qIsStat2Valid = 'Filament' in wCustomStat2.get() or 'Choose Stat2' in wCustomStat2.get()
                qIsStat3Valid = 'Filament' in wCustomStat3.get() or 'Choose Stat3' in wCustomStat3.get()
            elif "Segment" in (wCustomStat1.get()) or "Segment" in (wCustomStat2.get()) or "Segment" in (wCustomStat3.get()):
                qIsStat1Valid = 'Segment' in wCustomStat1.get() or 'Choose Stat1' in wCustomStat1.get()
                qIsStat2Valid = 'Segment' in wCustomStat2.get() or 'Choose Stat2' in wCustomStat2.get()
                qIsStat3Valid = 'Segment' in wCustomStat3.get() or 'Choose Stat3' in wCustomStat3.get()
            elif "Spine" in (wCustomStat1.get()) or "Spine" in (wCustomStat2.get()) or "Spine" in (wCustomStat3.get()):
                qIsStat1Valid = 'Spine' in wCustomStat1.get() or 'Choose Stat1' in wCustomStat1.get()
                qIsStat2Valid = 'Spine' in wCustomStat2.get() or 'Choose Stat2' in wCustomStat2.get()
                qIsStat3Valid = 'Spine' in wCustomStat3.get() or 'Choose Stat3' in wCustomStat3.get()         
            elif "Pt" in (wCustomStat1.get()) or "Pt" in (wCustomStat2.get()) or "Pt" in (wCustomStat3.get()):
                qIsStat1Valid = 'Pt' in wCustomStat1.get() or 'Choose Stat1' in wCustomStat1.get()
                qIsStat2Valid = 'Pt' in wCustomStat2.get() or 'Choose Stat2' in wCustomStat2.get()
                qIsStat3Valid = 'Pt' in wCustomStat3.get() or 'Choose Stat3' in wCustomStat3.get()          
            
            #Test is at least 2 of 3 stats are valid
            if (qIsStat1Valid and qIsStat2Valid and qIsStat3Valid) or \
                (qIsStat1Valid and qIsStat2Valid and not qIsStat3Valid) or \
                (qIsStat2Valid and qIsStat3Valid and not qIsStat1Valid) or \
                (qIsStat1Valid and qIsStat3Valid and not qIsStat2Valid):
                
                vEntry_Formula_Value = Entry_Formula.get()
                vStatNameCustom = Entry_StatName.get()
                if vEntry_Formula_Value == '':
                    messagebox.showerror(title='Formula Selection',
                                         message='Please input a formula')
                    window.mainloop()
                wCustomStat1.get()
                wCustomStat2.get()
                wCustomStat3.get()  
            else:
                 messagebox.showerror(title='Stat Selection MisMatach ',
                                       message='Stat type does not match\n'
                                       'Please Select Stats of same type')
                 window.mainloop()         
            window.destroy()
        
        if qIsCells:
            if qPerimeter == 1 and vDataSize[2] > 1:
                messagebox.showerror(title='DataSet is 3D',
                                              message='3D Surfaces do NOT have Circularity Stat')   
                window.mainloop()
            elif qPerimeter == 1 and vDataSize[2] == 1:
                wCustomStat1.set("Cell Area") # default value
                wCustomStat2.set("Cell Circularity") # default value
                Entry_Formula.delete(0, END)
                Entry_Formula.insert(0, 'sqrt(4*pi*stat1/stat2)')
                Entry_StatName.insert(0,  ' Cell Perimeter') 
                vStatNameCustom = Entry_StatName.get()
                vUnitNameCustom = "um"
                window.update()
                vEntry_Formula_Value = Entry_Formula.get()
                time.sleep(5)
                wCustomStat1.get()
                wCustomStat2.get()
                qIsTrackStat = 0
                window.destroy()           
            else:       
                if "Cell" in (wCustomStat1.get()) or "Cell" in (wCustomStat2.get()) or 'Cell' in(wCustomStat3.get()):
                    qIsStat1Valid = 'Cell' in wCustomStat1.get() or 'Choose Stat1' in wCustomStat1.get()
                    qIsStat2Valid = 'Cell' in wCustomStat2.get() or 'Choose Stat2' in wCustomStat2.get()
                    qIsStat3Valid = 'Cell' in wCustomStat3.get() or 'Choose Stat3' in wCustomStat3.get()
                elif "Nucleus" in (wCustomStat1.get()) or "Nucleus" in (wCustomStat2.get()) or "Nucleus" in (wCustomStat3.get()):
                    qIsStat1Valid = 'Nucleus' in wCustomStat1.get() or 'Choose Stat1' in wCustomStat1.get()
                    qIsStat2Valid = 'Nucleus' in wCustomStat2.get() or 'Choose Stat2' in wCustomStat2.get()
                    qIsStat3Valid = 'Nucleus' in wCustomStat3.get() or 'Choose Stat3' in wCustomStat3.get()
                elif "Vesicles" in (wCustomStat1.get()) or "Vesicles" in (wCustomStat2.get()) or "Vesicles" in (wCustomStat3.get()):
                    qIsStat1Valid = 'Vesicles' in wCustomStat1.get() or 'Choose Stat1' in wCustomStat1.get()
                    qIsStat2Valid = 'Vesicles' in wCustomStat2.get() or 'Choose Stat2' in wCustomStat2.get()
                    qIsStat3Valid = 'Vesicles' in wCustomStat3.get() or 'Choose Stat3' in wCustomStat3.get()                 
                #Test is at least 2 of 3 stats are valid 
                if (qIsStat1Valid and qIsStat2Valid and qIsStat3Valid) or \
                    (qIsStat1Valid and qIsStat2Valid and not qIsStat3Valid) or \
                    (qIsStat2Valid and qIsStat3Valid and not qIsStat1Valid) or \
                    (qIsStat1Valid and qIsStat3Valid and not qIsStat2Valid):
                     
                    vEntry_Formula_Value = Entry_Formula.get()
                    vStatNameCustom = Entry_StatName.get()
                    vUnitNameCustom = "um"
    
                    if vEntry_Formula_Value == '':
                        messagebox.showerror(title='Formula Selection',
                                             message='Please input a formula')
                        window.mainloop()
                    wCustomStat1.get()
                    wCustomStat2.get()
                    wCustomStat3.get()
                    
                    if "Intensity" in wCustomStat1.get() or "Image Mass" in wCustomStat1.get():
                        wChannelStat1.get()
                        if wChannelStat1.get() == 'Ch#':
                            messagebox.showerror(title='Channel Selection',
                                          message='Please Select Channel')
                            window.mainloop()
                    elif "Intensity" in wCustomStat2.get() or "Image Mass" in wCustomStat2.get():
                        wChannelStat2.get()
                        if wChannelStat2.get() == 'Ch#':
                            messagebox.showerror(title='Channel Selection',
                                          message='Please Select Channel')
                            window.mainloop()
                    elif "Intensity" in wCustomStat3.get() or "Image Mass" in wCustomStat3.get():
                        wChannelStat3.get()
                        if wChannelStat3.get() == 'Ch#':
                            messagebox.showerror(title='Channel Selection',
                                          message='Please Select Channel')
                            window.mainloop()
                else:
                     messagebox.showerror(title='Stat Selection MisMatach ',
                                           message='Stat type does not match\n'
                                           'Please Select Stats of same type')
                     window.mainloop()         
                window.destroy()        
            
        qPerimeter = var1.get()
        qSAtoVolumeRatio = var2.get()
        qTotalMeanIntensity = var3.get()
        qSelectedChannels = var4.get()
        
        if qSAtoVolumeRatio == 1 and vDataSize[2] == 1:
            messagebox.showerror(title='DataSet is 2D',
                                          message='2D Surfaces do NOT have Volume Stat')   
            window.mainloop()         
        if qPerimeter == 1 and vDataSize[2] >1:
            messagebox.showerror(title='DataSet is 3D',
                                          message='3D Surfaces do NOT have Circularity Stat')   
            window.mainloop()         
        if qIsSurface or qIsSpot:
            if qPerimeter == 1:
                wCustomStat1.set("Area") # default value
                wCustomStat2.set("Circularity") # default value
                Entry_Formula.delete(0, END)
                Entry_Formula.insert(0, 'sqrt(4*pi*stat1/stat2)')
                Entry_StatName.insert(0,  ' Perimeter') 
                vStatNameCustom = Entry_StatName.get()
                vUnitNameCustom = "um"
                window.update()
                vEntry_Formula_Value = Entry_Formula.get()
                time.sleep(5)
                wCustomStat1.get()
                wCustomStat2.get()
                qIsTrackStat = 0
                window.destroy()
                
            if qSAtoVolumeRatio == 1:
                wCustomStat1.set("Area") # default value
                wCustomStat2.set("Volume") # default value
                Entry_Formula.delete(0, END)
                Entry_Formula.insert(0, 'stat1/stat2')
                Entry_StatName.insert(0,  ' SurfaceAreaToVolume ratio')   
                window.update()
                vEntry_Formula_Value = Entry_Formula.get()
                vStatNameCustom = Entry_StatName.get()
                vUnitNameCustom = "1/um"
                time.sleep(5)
                wCustomStat1.get()
                wCustomStat2.get()
                qIsTrackStat = 0
                window.destroy()               
                if "Intensity" in wCustomStat1.get():
                    wChannelStat1.get()
                    if wChannelStat1.get() == 'Ch#':
                        messagebox.showerror(title='Channel Selection',
                                      message='Please Select Channel')
                        window.mainloop()
                elif "Intensity" in wCustomStat2.get():
                    wChannelStat2.get()
                    if wChannelStat2.get() == 'Ch#':
                        messagebox.showerror(title='Channel Selection',
                                      message='Please Select Channel')
                        window.mainloop()
                elif "Intensity" in wCustomStat3.get():
                    wChannelStat3.get()
                    if wChannelStat3.get() == 'Ch#':
                        messagebox.showerror(title='Channel Selection',
                                      message='Please Select Channel')
                        window.mainloop()
                window.destroy()
            #########    
            qIsTrackStat = 0
            wCustomStat1.get()
            wCustomStat2.get()
            wCustomStat3.get()  
            vEntry_Formula_Value = Entry_Formula.get()
            vStatNameCustom = Entry_StatName.get()
            vUnitNameCustom = Entry_UnitName.get()
            window.destroy()
             
    var1 = tk.IntVar(value=0)#periemter yes = 1
    var2 = tk.IntVar(value=0)#SA/Volume ratio yes = 1
    var3 = tk.IntVar(value=0)#Total mean Intensity
    var4 = tk.IntVar(value=0)#Mean Intensity selected channels
    
    vStatisticsALL = vObject.GetStatistics()
    vStatNamesALL = np.unique(vStatisticsALL.mNames).tolist()
    
    vStatObjectNamesALL = np.unique(vStatisticsALL.mNames)[np.where(['Track' not in item for item in np.unique(vStatisticsALL.mNames)])[0].tolist()].tolist()
    vStatTrackNamesALL = np.unique(vStatisticsALL.mNames)[np.where(['Track' in item for item in np.unique(vStatisticsALL.mNames)])[0].tolist()].tolist()
    if vStatTrackNamesALL == []:
        vStatTrackNamesALL = ['no Tracking Stats']
    
    tk.Label(window, text='Stat1:').grid(row=3,column=0, sticky=W)
    tk.Label(window, text='Stat2:').grid(row=4,column=0, sticky=W)
    tk.Label(window, text='Stat3:').grid(row=5,column=0, sticky=W)
    
    wCustomStat1 = StringVar(window)
    wCustomStat1.set("Obj Stat1") # default value
    wCustomStat2 = StringVar(window)
    wCustomStat2.set("Obj Stat2") # default value
    wCustomStat3 = StringVar(window)
    wCustomStat3.set("Obj Stat3") # default value
    w1 = OptionMenu(window, wCustomStat1, *vStatObjectNamesALL).grid(row=3, column=0,padx=30,sticky=W)
    w2 = OptionMenu(window, wCustomStat2, *vStatObjectNamesALL).grid(row=4, column=0,padx=30, sticky=W)
    w3 = OptionMenu(window, wCustomStat3, *vStatObjectNamesALL).grid(row=5, column=0,padx=30, sticky=W)
    
    wCustomTrackStat1 = StringVar(window)
    wCustomTrackStat1.set("Track Stat1") # default value
    wCustomTrackStat2 = StringVar(window)
    wCustomTrackStat2.set("Track Stat2") # default value
    wCustomTrackStat3 = StringVar(window)
    wCustomTrackStat3.set("Track Stat3") # default value
    w4 = OptionMenu(window, wCustomTrackStat1, *vStatTrackNamesALL).grid(row=3, column=0,padx=145, sticky=W)
    w5 = OptionMenu(window, wCustomTrackStat2, *vStatTrackNamesALL).grid(row=4, column=0,padx=145, sticky=W)
    w6 = OptionMenu(window, wCustomTrackStat3, *vStatTrackNamesALL).grid(row=5, column=0,padx=145, sticky=W)
    
    wChannelStat1 = StringVar(window)
    wChannelStat1.set("Ch#") # default value
    wChannelStat2 = StringVar(window)
    wChannelStat2.set("Ch#") # default value
    wChannelStat3 = StringVar(window)
    wChannelStat3.set("Ch#") # default value
    w11 = OptionMenu(window, wChannelStat1, *vNumberOfChannelsList).grid(row=3, column=0,padx=285,sticky=W)
    w12 = OptionMenu(window, wChannelStat2, *vNumberOfChannelsList).grid(row=4, column=0,padx=285,sticky=W)
    w13 = OptionMenu(window, wChannelStat3, *vNumberOfChannelsList).grid(row=5, column=0,padx=285,sticky=W)
    tk.Label(window, text='Ch:').grid(row=3,column=0, padx=260, sticky=W)
    tk.Label(window, text='Ch:').grid(row=4,column=0, padx=260, sticky=W)
    tk.Label(window, text='Ch:').grid(row=5,column=0, padx=260, sticky=W)
    
    Create1 = Button(window, text="Create Object Stat",command=CustomStat, width=15, height=2,fg='white', bg='red')
    Create1.grid(row=1, column=0,padx=20,sticky=W)
    
    Create2 = Button(window, text="Create Track Stat",command=CustomTrackStat, width=15, height=2,fg='white', bg='blue')
    Create2.grid(row=1, column=0,padx=170,sticky=W)
    
    Create3 = Button(window, text="Subset Cells",command=SubsetCells, width=10, height=1)
    Create3.grid(row=8, column=0,padx=375,sticky=W)
    
    Create4 = Button(window, text="Subset Nucleus",command=SubsetNucleus, width=13, height=1)
    Create4.grid(row=8, column=0,padx=460,sticky=W)
    
    Create5 = Button(window, text="Subset Vesicles",command=SubsetVesicles, width=13, height=1)
    Create5.grid(row=8, column=0,padx=570,sticky=W)
    
    Create6 = Button(window, text="Subset Filament",command=SubsetFilament, width=12, height=1)
    Create6.grid(row=8, column=0,padx=60,sticky=W)
    
    Create7 = Button(window, text="Subset Segment",command=SubsetSegment, width=13, height=1)
    Create7.grid(row=8, column=0,padx=160,sticky=W)
    
    Create8 = Button(window, text="Subset Spines",command=SubsetSpines, width=13, height=1)
    Create8.grid(row=8, column=0,padx=265,sticky=W)
    
    ###########################################################
    Entry_Formula=Entry(window,justify='center',width=40)
    Entry_Formula.grid(row=2, column=0,padx=100, sticky=W)
    Entry_Formula.insert(0, 'stat1/stat2')
    
    Entry_StatName=Entry(window,justify='center',width=25)
    Entry_StatName.grid(row=1, column=0,padx=350, sticky=W)
    Entry_StatName.insert(0, '')
    
    Entry_UnitName=Entry(window,justify='center',width=10)
    Entry_UnitName.grid(row=1, column=0,padx=610, sticky=W)
    Entry_UnitName.insert(0, '')
    tk.Label(window, text='Units:').grid(row=1,column=0, padx=570, sticky=W)
    
    tk.Label(window, text='FORMULA:').grid(row=2,column=0, padx=20,sticky=W)
    tk.Label(window, text='StatName:').grid(row=1,column=0, padx=300, sticky=W)
    tk.Label(window, text='How to input formula calculation:').grid(row=6,column=0, sticky=W)
    tk.Label(window, text='Example: (stat1 + stat2)').grid(row=7,column=0, sticky=W)
    tk.Label(window, text='Mathematical operators: pi, sqrt, + , - , / , *').grid(row=6,column=0, sticky=W)
    
    tk.Checkbutton(window, text='Perimeter (2D)',
                   variable=var1, onvalue=1, offvalue=0).grid(row=3, column=0,sticky=W, padx=370)
    tk.Checkbutton(window, text='SurfaceArea to Volume Ratio (3D)',
                   variable=var2, onvalue=1, offvalue=0).grid(row=4, column=0,sticky=W, padx=370)
    tk.Checkbutton(window, text='Overall Mean Intensity(TotalIntSum/Total#Voxels)\n'
                   'ALL surfaces/channels/timepoints)',
                   variable=var3, onvalue=1, offvalue=0).grid(row=5, column=0,sticky=W, padx=370)
    tk.Checkbutton(window, text='Use Selected Channels',
                   variable=var4, onvalue=1, offvalue=0).grid(row=6, column=0,sticky=W, padx=390)
    
    window.mainloop()
    
    ##################################################################
    ##################################################################
    if qTotalMeanIntensity == 1:
        if not qIsSurface:
            messagebox.showerror(title='Invalid Stat',
                                          message='Invalid stat used:\n'
                                          'Surpass Object must be a Surface!')
            sys.exit()
        #Calculate Overall Intensity Stats
        vStat1SET = vObject.GetStatisticsByName('Number of Voxels')
        vStat_NumberofVoxels = np.array(vStat1SET.mValues)
        vStat_NumberofVoxels_Factors = vStat1SET.mFactors
    
        vStat1SET = vObject.GetStatisticsByName('Intensity Sum')
        vStat_IntensitySum = np.array(vStat1SET.mValues)
        vStat_IntensitySum_Factors = vStat1SET.mFactors
       
        if qSelectedChannels == 0 or vSizeC == 1: 
            #process all channels
            for channelIndex in range (vSizeC):
                vNewOverallStatIntensityMean=[]
                for timeindex in range (vSizeT):
                    vCombined_conditionSum = np.where((np.array(vStat_IntensitySum_Factors[3]) == str(timeindex+1)) & (np.array(vStat_IntensitySum_Factors[1]) == str(channelIndex+1)))[0].tolist()
                    vCombined_conditionVoxels = np.where((np.array(vStat_NumberofVoxels_Factors[2]) == str(timeindex+1)))
                    # np.sum(vStat_IntensitySum[vCombined_condition])
                    # np.sum(vStat_NumberofVoxels[vCombined_condition])
                    vNewOverallStatIntensityMean.append(np.sum(vStat_IntensitySum[vCombined_conditionSum])/np.sum(vStat_NumberofVoxels[vCombined_conditionVoxels]))
         
                #Convert Nan to "0" - no surfaces in that timepoint
                # vNewOverallStatIntensityMean = [0 if math.isnan(x) else x for x in vNewOverallStatIntensityMean]
                #Add Overall Statistic
    
                vOverallStatIds=[int(-1)] * len(vNewOverallStatIntensityMean) 
                vOverallStatUnits=['']*len(vNewOverallStatIntensityMean)
                vOverallStatFactorsTime=list(range(1,len(vNewOverallStatIntensityMean) + 1))
                vOverallStatFactors=[['Overall']*len(vNewOverallStatIntensityMean),[str(i) for i in vOverallStatFactorsTime]]
                vOverallStatFactorNames=['FactorName','Time']       
                vOverallStatNames = [' Overall Surface Mean Int_Ch_'+ str(channelIndex + 1)]*len(vNewOverallStatIntensityMean)  
                vObject.AddStatistics(vOverallStatNames, vNewOverallStatIntensityMean,
                                              vOverallStatUnits, vOverallStatFactors,
                                              vOverallStatFactorNames, vOverallStatIds)
        #Process selected channels from dialog box
        else:        
            if wChannelStat1.get() != "Ch#":
                #find all channel data thru time series
                for timeindex in range (vSizeT):
                    vCombined_conditionSum = np.where((np.array(vStat_IntensitySum_Factors[3]) == str(timeindex+1)) & (np.array(vStat_IntensitySum_Factors[1]) == str(wChannelStat1.get())))[0].tolist()
                    vCombined_conditionVoxels = np.where((np.array(vStat_NumberofVoxels_Factors[2]) == str(timeindex+1)))
                    #Calculate stat
                    vNewOverallStatIntensityMean.append(np.sum(vStat_IntensitySum[vCombined_conditionSum])/np.sum(vStat_NumberofVoxels[vCombined_conditionVoxels]))
                #Convert Nan to "0" - no surfaces in that timepoint
                # vNewOverallStatIntensityMean = [0 if math.isnan(x) else x for x in vNewOverallStatIntensityMean]
                #Add Overall Statistic
                vOverallStatIds=[int(-1)] * len(vNewOverallStatIntensityMean) 
                vOverallStatUnits=['']*len(vNewOverallStatIntensityMean)
                vOverallStatFactorsTime=list(range(1,len(vNewOverallStatIntensityMean) + 1))
                vOverallStatFactors=[['Overall']*len(vNewOverallStatIntensityMean),[str(i) for i in vOverallStatFactorsTime]]
                vOverallStatFactorNames=['FactorName','Time']       
                vOverallStatNames = [' Overall Surface Mean Int_Ch_'+ wChannelStat1.get()] * len(vNewOverallStatIntensityMean)  
                vObject.AddStatistics(vOverallStatNames, vNewOverallStatIntensityMean,
                                              vOverallStatUnits, vOverallStatFactors,
                                              vOverallStatFactorNames, vOverallStatIds)
            if wChannelStat2.get() != "Ch#":
                #find all channel data thru time series
                for timeindex in range (vSizeT):
                    vCombined_conditionSum = np.where((np.array(vStat_IntensitySum_Factors[3]) == str(timeindex+1)) & (np.array(vStat_IntensitySum_Factors[1]) == str(wChannelStat2.get())))[0].tolist()
                    vCombined_conditionVoxels = np.where((np.array(vStat_NumberofVoxels_Factors[2]) == str(timeindex+1)))
                    #Calculate stat
                    vNewOverallStatIntensityMean.append(np.sum(vStat_IntensitySum[vCombined_conditionSum])/np.sum(vStat_NumberofVoxels[vCombined_conditionVoxels]))
                #Convert Nan to "0" - no surfaces in that timepoint
                # vNewOverallStatIntensityMean = [0 if math.isnan(x) else x for x in vNewOverallStatIntensityMean]
                #Add Overall Statistic
                vOverallStatIds=[int(-1)] * len(vNewOverallStatIntensityMean) 
                vOverallStatUnits=['']*len(vNewOverallStatIntensityMean)
                vOverallStatFactorsTime=list(range(1,len(vNewOverallStatIntensityMean) + 1))
                vOverallStatFactors=[['Overall']*len(vNewOverallStatIntensityMean),[str(i) for i in vOverallStatFactorsTime]]
                vOverallStatFactorNames=['FactorName','Time']       
                vOverallStatNames = [' Overall Surface Mean Int_Ch_'+ wChannelStat2.get()] * len(vNewOverallStatIntensityMean)  
                vObject.AddStatistics(vOverallStatNames, vNewOverallStatIntensityMean,
                                              vOverallStatUnits, vOverallStatFactors,
                                              vOverallStatFactorNames, vOverallStatIds)
                if wChannelStat3.get() != "Ch#":
                    #find all channel data thru time series
                    for timeindex in range (vSizeT):
                        vCombined_conditionSum = np.where((np.array(vStat_IntensitySum_Factors[3]) == str(timeindex+1)) & (np.array(vStat_IntensitySum_Factors[1]) == str(wChannelStat3.get())))[0].tolist()
                        vCombined_conditionVoxels = np.where((np.array(vStat_NumberofVoxels_Factors[2]) == str(timeindex+1)))
                        #Calculate stat
                        vNewOverallStatIntensityMean.append(np.sum(vStat_IntensitySum[vCombined_conditionSum])/np.sum(vStat_NumberofVoxels[vCombined_conditionVoxels]))
                    #Convert Nan to "0" - no surfaces in that timepoint
                    # vNewOverallStatIntensityMean = [0 if math.isnan(x) else x for x in vNewOverallStatIntensityMean]
                    #Add Overall Statistic
                    vOverallStatIds=[int(-1)] * len(vNewOverallStatIntensityMean) 
                    vOverallStatUnits=['']*len(vNewOverallStatIntensityMean)
                    vOverallStatFactorsTime=list(range(1,len(vNewOverallStatIntensityMean) + 1))
                    vOverallStatFactors=[['Overall']*len(vNewOverallStatIntensityMean),[str(i) for i in vOverallStatFactorsTime]]
                    vOverallStatFactorNames=['FactorName','Time']       
                    vOverallStatNames = [' Overall Surface Mean Int_Ch_'+ wChannelStat3.get()] * len(vNewOverallStatIntensityMean)  
                    vObject.AddStatistics(vOverallStatNames, vNewOverallStatIntensityMean,
                                                  vOverallStatUnits, vOverallStatFactors,
                                                  vOverallStatFactorNames, vOverallStatIds)                
    ##################################################################
    ##################################################################
    if qIsTrackStat == 1:
        vStatTrack1SET = vObject.GetStatisticsByName(wCustomTrackStat1.get())
        vStatTrack2SET = vObject.GetStatisticsByName(wCustomTrackStat2.get())
        vStatTrack3SET = vObject.GetStatisticsByName(wCustomTrackStat3.get())
        vStatTrack1Factors = vStatTrack3SET.mFactors
        vStatTrack2Factors = vStatTrack3SET.mFactors
        vStatTrack3Factors = vStatTrack3SET.mFactors
        stat1 = np.array(vStatTrack1SET.mValues)
        stat2 = np.array(vStatTrack2SET.mValues)  
        stat3 = np.array(vStatTrack3SET.mValues)
         
        #Select specific Intensity channel
        if "Intensity" in wCustomTrackStat1.get():
            # wChannelStat1.get()
            # vStat1Factors=np.array(vStat1Factors)[1:]
            # zTestList=np.where(np.array(vStat1Factors[1]) == wChannelStat1.get())[0].tolist()
            # stat1[zTestList]
            stat1 = stat1[np.where(np.array(vStatTrack1Factors[1]) == wChannelStat1.get())[0].tolist()]
            vNumberOfObjectsStat1 = len(stat1)   
        if "Intensity" in wCustomTrackStat2.get():
            stat2 = stat2[np.where(np.array(vStatTrack2Factors[1]) == wChannelStat2.get())[0].tolist()]
            vNumberOfObjectsStat2 = len(stat2)   
        if "Intensity" in wCustomTrackStat3.get():
            stat3 = stat3[np.where(np.array(vStatTrack3Factors[1]) == wChannelStat3.get())[0].tolist()]
            vNumberOfObjectsStat3 = len(stat3)  
           
    else:
        vStat1SET = vObject.GetStatisticsByName(wCustomStat1.get())
        vStat2SET = vObject.GetStatisticsByName(wCustomStat2.get())
        vStat3SET = vObject.GetStatisticsByName(wCustomStat3.get())
        vStat1Factors = vStat1SET.mFactors
        vStat2Factors = vStat2SET.mFactors
        vStat3Factors = vStat3SET.mFactors
        # vStat1FactorNames = vStat1SET.mFactorNames
        # vStat2FactorNames = vStat2SET.mFactorNames 
        # vStat3FactorNames = vStat3SET.mFactorNames   
        stat1 = np.array(vStat1SET.mValues)
        stat2 = np.array(vStat2SET.mValues)  
        stat3 = np.array(vStat3SET.mValues)
           
        if "Filament No. Segment Branches" in (wCustomStat1.get(), wCustomStat2.get(), wCustomStat3.get()):
            messagebox.showerror(title='Invalid Stat',
                                          message='Invalid stat used:\n'
                                          'Filament No. Segment Branches')
            sys.exit()
        if "Filament No. Sholl Intersections" in (wCustomStat1.get(), wCustomStat2.get(), wCustomStat3.get()):
            messagebox.showerror(title='Invalid Stat',
                                          message='Invalid stat used:\n'
                                          'Filament No. Sholl Intersections')
            sys.exit()
    
        #Select specific Intensity channel
        if "Intensity" in wCustomStat1.get() or "Image Mass" in wCustomStat1.get():
            stat1 = stat1[np.where(np.array(vStat1Factors[1]) == wChannelStat1.get())[0].tolist()]
            vNumberOfObjectsStat1 = len(stat1)   
        if "Intensity" in wCustomStat2.get() or "Image Mass" in wCustomStat2.get():
            stat2 = stat2[np.where(np.array(vStat2Factors[1]) == wChannelStat2.get())[0].tolist()]
            vNumberOfObjectsStat2 = len(stat2)   
        if "Intensity" in wCustomStat3.get() or "Image Mass" in wCustomStat3.get():
            stat3 = stat3[np.where(np.array(vStat3Factors[1]) == wChannelStat3.get())[0].tolist()]
            vNumberOfObjectsStat3 = len(stat3)      
            
    #Set formula to all lower case
    vEntry_Formula_Value = vEntry_Formula_Value.lower()
    pi = 3.14592653
        
    # Evaluate the formula using numexpr
    vObjectNewStat = ne.evaluate(vEntry_Formula_Value)
    #Set inf values to "0"
    # vObjectNewStat[~np.isfinite(vObjectNewStat)] = 0   
    vObjectNewStatValues = vObjectNewStat[:].tolist()
    
    #Check if NEw Statistic already present
    if vStatNameCustom == "":
        vStatisticsALL = vObject.GetStatistics()
        vStatNamesALL = np.unique(vStatisticsALL.mNames).tolist()    
        if ' New Statistic' in vStatNamesALL:
            vStatNameCustom = ' New Statistic_2'
        if ' New Statistic_2' in vStatNamesALL:
            vStatNameCustom = ' New Statistic_3 '    
    
    #Add new object stat
    if qIsCells:
        if "Cell" in (wCustomStat1.get()) or "Cell" in (wCustomStat2.get()) or "Cell" in (wCustomStat3.get()):
            vNumberOfCells = vObject.GetNumberOfCells()
            vObjectIds = vObject.GetIds()
            vObjectTimeIndices = vObject.GetIndicesT()
            vObjectTimeIndices = [x + 1 for x in vObjectTimeIndices]
            vObjectStatUnits = [vUnitNameCustom]*vNumberOfCells  
            vObjectStatFactorName=['Category','Time']
            vObjectStatFactors=(['Cell']*vNumberOfCells, [str(x) for x in vObjectTimeIndices] )
            if vStatNameCustom == "":
                vObjectStatNames=[' Cell New Statistic']*vNumberOfCells
            else:
                vObjectStatNames=[vStatNameCustom]*vNumberOfCells  
            vObject.AddStatistics(vObjectStatNames, vObjectNewStatValues,
                                  vObjectStatUnits, vObjectStatFactors,
                                  vObjectStatFactorName, vObjectIds)
            
        if "Nucleus" in (wCustomStat1.get()) or "Nucleus" in(wCustomStat2.get()) or "Nucleus" in (wCustomStat3.get()):
            vNumberofNucleus = vObject.GetNumberOfNuclei()
            vObjectIds = vObject.GetNucleusIds()        
            vObjectTimeIndices = vStat1Factors[1]        
            vObjectStatFactorName=['Category','Time']
            vObjectStatUnits = [vUnitNameCustom]*len(vNumberofNucleus)  
            vObjectStatFactors = (['Nucleus']*len(vNumberofNucleus), [str(x) for x in vObjectTimeIndices] )
            if vStatNameCustom == "":
                vObjectStatNames = [' Nucleus New Statistic']*len(vNumberofNucleus)
            else:
                vObjectStatNames=[vStatNameCustom]*len(vNumberofNucleus)          
            vObject.AddStatistics(vObjectStatNames, vObjectNewStatValues,
                                  vObjectStatUnits, vObjectStatFactors,
                                  vObjectStatFactorName, vObjectIds)        
            
        if "Vesicles" in (wCustomStat1.get()) or "Vesicles" in (wCustomStat2.get()) or "Vesicles" in (wCustomStat3.get()):
            
            vObjectIds = vObject.GetVesicleIds(0)
            vNumberOfVesicles = len(vObjectIds)
            vObjectTimeIndices = vStat1Factors[1]   
            vObjectStatUnits = [vUnitNameCustom]*vNumberOfVesicles 
            vObjectStatFactorName=['Category','Time']
            vObjectStatFactors=(['Vesicle']*vNumberOfVesicles, [str(x) for x in vObjectTimeIndices] )
            if vStatNameCustom == "":
                vObjectStatNames=[' Vesicle New Statistic']*vNumberOfVesicles
            else:
                vObjectStatNames=[vStatNameCustom]*vNumberOfVesicles   
            vObject.AddStatistics(vObjectStatNames, vObjectNewStatValues,
                                  vObjectStatUnits, vObjectStatFactors,
                                  vObjectStatFactorName, vObjectIds)       
          
    if qIsSpot:
        vObjectIds = vObject.GetIds()
        #Add 1 to each time index to start this at "1" and not zero for customer stat creation
        vObjectTimeIndices = [value + 1 for value in vObject.GetIndicesT()]   
        vObjectStatFactors=(['Spot']*len(vObjectIds), [str(x) for x in vObjectTimeIndices] )
        vObjectStatUnits=[vUnitNameCustom]*len(vObjectIds)    
        vObjectStatFactorName=['Category','Time']
        #set Statname
        if vStatNameCustom == "":
            vObjectStatNames=[' New Statistic']*len(vObjectIds)
        else:
            vObjectStatNames=[vStatNameCustom]*len(vObjectIds)    
        #Add statistic to Imaris      
        vObject.AddStatistics(vObjectStatNames, vObjectNewStatValues,
                                      vObjectStatUnits, vObjectStatFactors,
                                      vObjectStatFactorName, vObjectIds)
        
    if qIsSurface:
        if qIsTrackStat == 1:
            vObjectTrackIds = vObject.GetTrackIds()
            vObjectTrackIDsUnique = np.unique(np.array(vObjectTrackIds))
            #set Statname
            if vStatNameCustom == "":
                vObjectStatNames=[' New Track Statistic']*len(vObjectTrackIDsUnique)
            else:
                vObjectStatNames=[vStatNameCustom]*len(vObjectTrackIDsUnique)  
            #Adding Track statistics
            vTrackStatUnits=[vUnitNameCustom]*len(vObjectTrackIDsUnique)
            vTrackStatFactors=[['Track']*len(vObjectTrackIDsUnique)]
            vTrackStatFactorName=['Category']
            vObject.AddStatistics(vObjectStatNames, vObjectNewStatValues,
                                          vTrackStatUnits, vTrackStatFactors,
                                          vTrackStatFactorName, vObjectTrackIDsUnique.tolist())
            
        else:
            vObjectTimeIndices = []
            vNumberOfSurfaces = vObject.GetNumberOfSurfaces()
            vObjectIds = vObject.GetIds()
            #set Statname
            if vStatNameCustom == "":
                vObjectStatNames=[' New Statistic']*vNumberOfSurfaces
            else:
                vObjectStatNames=[vStatNameCustom]*vNumberOfSurfaces  
            #loop surfaces to get time index    
            if vSizeT == 1:
                vObjectTimeIndices = [1]*vNumberOfSurfaces
            else:
                for vObjectIndex in range (vNumberOfSurfaces):
                    vObjectTimeIndices.append(vObject.GetTimeIndex(vObjectIndex)+1)  
            vObjectStatUnits=[vUnitNameCustom]*vNumberOfSurfaces
            vObjectStatFactors=(['Surface']*vNumberOfSurfaces, [str(x) for x in vObjectTimeIndices] )
            vObjectStatFactorName=['Category','Time']
            #Add statistic to Imaris 
            vObject.AddStatistics(vObjectStatNames, vObjectNewStatValues,
                                          vObjectStatUnits, vObjectStatFactors,
                                          vObjectStatFactorName, vObjectIds)
            
    if qIsFilament:
        vNumberOfFilaments = vObject.GetNumberOfFilaments()
        vObjectIds = vObject.GetIds()
        #loop surfaces to get time indices    
        if vSizeT == 1:
            vObjectTimeIndices = [1]*vNumberOfFilaments
        else:
            for vObjectIndex in range (vNumberOfFilaments):
                vObjectTimeIndices.append(vObject.GetTimeIndex(vObjectIndex)+1)
        vObjectStatUnits=[vUnitNameCustom]*vNumberOfFilaments
        vObjectStatFactors=(['Filament']*vNumberOfFilaments, [str(x) for x in vObjectTimeIndices] )
        vObjectStatFactorName=['Category','Time']
        vObjectStatNames=[' New Statistic']*vNumberOfFilaments   
        #set Statname
        if vStatNameCustom == "":
            vObjectStatNames=[' New Statistic']*len(vObjectIds)
        else:
            vObjectStatNames=[vStatNameCustom]*len(vObjectIds)    
            
        #Add statistic to Imaris 
        vObject.AddStatistics(vObjectStatNames, vObjectNewStatValues,
                                      vObjectStatUnits, vObjectStatFactors,
                                      vObjectStatFactorName, vObjectIds)
        
    vObject.SetName(vObject.GetName()+'_newStat')
    vImarisApplication.GetSurpassScene().AddChild(vObject, -1)