#Written by Matthew J. Gastinger
#2025
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
import platform

from sympy import sympify, symbols
import numexpr as ne

import ImarisLib
import numpy as np
import time


aImarisId=0
def XT_MJG_CustomStat1(aImarisId):
    
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
    
    
    #####################################################
    #Making the Listbox for the Surpass menu
    window = Tk()
    window.title("Statistic Selection")
    window.geometry("550x200")
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
    
    def CustomStat():
        global wCustomStat1a, wCustomStat1b, wCustomStat1c, Entry_Formula_Value
        global qPerimeter, vStatNameCustom
        
        qPerimeter = var1.get()
        if qPerimeter == 1:
            # wCustomStat1a = StringVar(window)
            wCustomStat1a.set("Area") # default value
            # wCustomStat1b = StringVar(window)
            wCustomStat1b.set("Circularity") # default value
            Entry_Formula.insert(0, 'sqrt(4*pi*stat1/stat2)')
            Entry_StatName.insert(0,  ' Perimeter')   
            window.update()
            Entry_Formula_Value = Entry_Formula.get()
            vStatNameCustom = Entry_StatName.get()
            time.sleep(5)
    
            # wCustomStat1a.get()
            # wCustomStat1b.get()
            window.destroy()
        else:
            Entry_Formula_Value = Entry_Formula.get()
            vStatNameCustom = Entry_StatName.get()
        # if Entry_Formula_Value == '':
        #     messagebox.showerror(title='Formula Selection',
        #                      message='Please input a formula')
        #     window.mainloop()
            wCustomStat1a.get()
            wCustomStat1b.get()
            wCustomStat1c.get()
            window.destroy()
    
    var1 = tk.IntVar(value=0)#periemter yes = 1
    
    vStatisticsALL = vObject.GetStatistics()
    vStatNamesALL = np.unique(vStatisticsALL.mNames).tolist()
    
    wCustomStat1a = StringVar(window)
    # wCustomStat1a.set("Choose Stat1") # default value
    wCustomStat1b = StringVar(window)
    # wCustomStat1b.set("Choose Stat2") # default value
    wCustomStat1c = StringVar(window)
    # wCustomStat1c.set("Choose Stat3") # default value
    
    w1 = OptionMenu(window, wCustomStat1a, *vStatNamesALL).grid(row=3, column=0,padx=50,sticky=W)
    w3 = OptionMenu(window, wCustomStat1b, *vStatNamesALL).grid(row=4, column=0,padx=50, sticky=W)
    w4 = OptionMenu(window, wCustomStat1c, *vStatNamesALL).grid(row=5, column=0,padx=50, sticky=W)
    
    tk.Label(window, text='FORMULA:').grid(row=2,column=0, padx=20,sticky=W)
    tk.Label(window, text='Stat1:').grid(row=3,column=0, sticky=W)
    tk.Label(window, text='Stat2:').grid(row=4,column=0, sticky=W)
    tk.Label(window, text='Stat3:').grid(row=5,column=0, sticky=W)
    
    Create1 = Button(window, text="Create Custom Stat",command=CustomStat, width=20, height=2)
    Create1.grid(row=1, column=0,padx=50,sticky=W)
    
    ###########################################################
    Entry_Formula=Entry(window,justify='center',width=40)
    Entry_Formula.grid(row=2, column=0,padx=100, sticky=W)
    #Entry_Formula.insert(0, 'stat1/stat2')
    
    Entry_StatName=Entry(window,justify='center',width=20)
    Entry_StatName.grid(row=1, column=0,padx=350, sticky=W)
    Entry_StatName.insert(0, ' ')
    
    tk.Label(window, text='StatName:').grid(row=1,column=0, padx=280, sticky=W)
    tk.Label(window, text='How to input formula calculation:').grid(row=6,column=0, sticky=W)
    tk.Label(window, text='Example: stat1 / (2*stat2)').grid(row=7,column=0, sticky=W)
    tk.Label(window, text='Mathematical operators: pi, sqrt, + , - , / , *').grid(row=6,column=0, sticky=W)
    
    #Create perimeter button to insert into formula for 2D
    # CreatePerimeter = Button(window, text="Perimeter (2D only)",command=Perimeter, width=15, height=1)
    # CreatePerimeter.grid(row=3, column=0,padx=360,sticky=W)
    
    
    tk.Checkbutton(window, text='Calculate Perimeter',
                   variable=var1, onvalue=1, offvalue=0).grid(row=3, column=0,sticky=W, padx=280)
    window.update()

    
    
    window.mainloop()
    
    ##################################################################
    vStat1SET = vObject.GetStatisticsByName(wCustomStat1a.get())
    vStat1Values = np.array(vStat1SET.mValues)
    vStat1Ids = vStat1SET.mIds
    
    vStat2SET = vObject.GetStatisticsByName(wCustomStat1b.get())
    vStat2Values = np.array(vStat2SET.mValues)
    vStat2Ids = vStat2SET.mIds
    
    # # vStatMath = str(wCustomStat1Math.get())
    
    # if vStatMath == '+':
    #     vStatNew = vStat1Values + vStat2Values
    # if vStatMath == '-':
    #     vStatNew = vStat1Values - vStat2Values
    # if vStatMath == '*':
    #     vStatNew = vStat1Values * vStat2Values
    # if vStatMath == '/':
    #     vStatNew = vStat1Values / vStat2Values    
    # if vStatMath == 'formula':   
            
    pi=[np.pi]*np.size(vStat1Values)
    
    stat1 = np.array(vStat1SET.mValues)
    stat2 = np.array(vStat2SET.mValues)    
    # Evaluate the formula using numexpr
    vObjectResult = ne.evaluate(Entry_Formula_Value)
    vObjectNewStatValues = vObjectResult.tolist()
    
    #Add new stat
    if qIsSpot:
        vObjectTimeIndices = vObject.GetIndicesT()
        vObjectIds = vObject.GetIds()
        vObjectStatFactorName=['Category','Time']
        vObjectStatNames=[' New Statistic']*len(vObjectIds)  
        vObjectStatFactors=(['Spot']*len(vObjectIds), [str(x) for x in vObjectTimeIndices] )
        vObject.AddStatistics(vObjectStatNames, vObjectNewStatValues,
                                      vObjectStatUnits, vObjectStatFactors,
                                      vObjectStatFactorName, vObjectIds)
    if qIsSurface:
        vObjectTimeIndices = []
        vNumberOfSurfaces = vObject.GetNumberOfSurfaces()
        vObjectIds = vObject.GetIds()
        for vObjectIndex in range (vNumberOfSurfaces):
            vObjectTimeIndices.append(vObject.GetTimeIndex(vObjectIndex)+1)
        vObjectStatUnits=['um']*len(vObjectIds)
        vObjectStatFactors=(['Surface']*len(vObjectIds), [str(x) for x in vObjectTimeIndices] )
        vObjectStatFactorName=['Category','Time']
        vObjectStatNames=[' New Statistic']*len(vObjectIds)
        # set preset name for perimter
        if qPerimeter == 1:
            vObjectStatNames = [vStatNameCustom]*len(vObjectIds) 
        vObject.AddStatistics(vObjectStatNames, vObjectNewStatValues,
                                      vObjectStatUnits, vObjectStatFactors,
                                      vObjectStatFactorName, vObjectIds)
    if qIsFilament:
        vObjectTimeIndices = vObject.GetIndicesT()
        vNumberOfFilaments = vObject.GetNumberOfFilaments()
        vObjectIds = vObject.GetIds()
        for vObjectIndex in range (vNumberOfFilaments):
            vObjectTimeIndices.append(vObject.GetTimeIndex(vObjectIndex)+1)
        vObjectStatUnits=['um']*len(vObjectIds)
        vObjectStatFactors=(['Filament']*len(vObjectIds), [str(x) for x in vObjectTimeIndices] )
        vObjectStatFactorName=['Category','Time']
        vObjectStatNames=[' New Statistic']*len(vObjectIds)  
        vObject.AddStatistics(vObjectStatNames, vObjectNewStatValues,
                                      vObjectStatUnits, vObjectStatFactors,
                                      vObjectStatFactorName, vObjectIds)
    
    
        
