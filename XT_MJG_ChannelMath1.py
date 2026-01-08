#Written by Matthew J. Gastinger
#2025
    # <CustomTools>
    #     <Menu>
    #         <Item name="Channel Math1" icon="Python3">
    #             <Command>Python3XT::XT_MJG_ChannelMath1(%i)</Command>
    #         </Item>
    #         <Submenu name="Spots Functions">
    #             <Item name="Channel Math1" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_ChannelMath1(%i)</Command>
    #             </Item>
    #         </Submenu>
    #         <Submenu name="Surfaces Functions">
    #             <Item name="Channel Math1" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_ChannelMath1(%i)</Command>
    #             </Item>
    #         </Submenu>
    #         <Submenu name="Filamernts Functions">
    #             <Item name="Channel Math1" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_ChannelMath1(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSpots">
    #             <Item name="Channel Math1" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_ChannelMath1(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #         <SurpassComponent name="bpSurfaces">
    #             <Item name="Channel Math1" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_ChannelMath1(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #         <SurpassComponent name="bpFilaments">
    #             <Item name="Channel Math1" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_ChannelMath1(%i)</Command>
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

import numexpr as ne
import re
import ImarisLib
import numpy as np
from numpy import inf
import time
import sys
import Imaris

 #aImarisId=0
def XT_MJG_ChannelMath1(aImarisId):
    global vEntry_Formula_Value, vEntry_ChannelName_Value, qRemoveInf
    global qAverage_zeropixels    
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
    
    #clone Dataset
    vImarisDataSet = vImage.Clone()
    vImarisDataSet.SetSizeC(vSizeC + 1)
    
    #Convert to 32bit
    vType = Imaris.tType.eTypeFloat
    vImarisDataSet.SetType(vType)
    
    #Dialog window
    ############################################################################
    qWindow = Tk()
    qWindow.title('Channel Math')
    qWindow.geometry("450x150")
    qWindow.attributes("-topmost", True)
    
    ##################################################################
    #Set input in center on screen
    # Gets the requested values of the height and widht.
    windowWidth = qWindow.winfo_reqwidth()
    windowHeight = qWindow.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(qWindow.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(qWindow.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    qWindow.geometry("+{}+{}".format(positionRight, positionDown))
    ##################################################################
    
    def ChannelMath ():
        global vEntry_Formula_Value, vEntry_ChannelName_Value, qRemoveInf
        global qAverage_zeropixels
        vEntry_Formula_Value = Entry_Formula.get()
        vEntry_ChannelName_Value = Entry_Channel_Name.get()
        qRemoveInf = var1.get()
        qAverage_zeropixels = var2.get()    
        qWindow.destroy()
    
    var1 = tk.IntVar(value=1)
    var2 = tk.IntVar(value=0)
    
    tk.Label(qWindow, text='FORMULA:').grid(row=2,column=0, padx=20,sticky=W)
    Entry_Formula=Entry(qWindow,justify='center',width=50)
    Entry_Formula.grid(row=2, column=0,padx=100, sticky=W)
    Entry_Formula.insert(0, 'sqrt(ch1*ch2)')
    
    Entry_Channel_Name=Entry(qWindow,justify='center',width=30)
    Entry_Channel_Name.grid(row=3, column=0,padx=200, sticky=W)
    Entry_Channel_Name.insert(0, 'New Channel Name')
    
    Create1 = Button(qWindow, text="Create New Channel",command=ChannelMath, width=18, height=2)
    Create1.grid(row=3, column=0,padx=30,sticky=W)
    
    tk.Label(qWindow, text='Arithmetic expressions: + , - , / , *, sqrt, pi\n'
                             ' Example: ch1-Ch2').grid(row=4,column=0, padx=30, sticky=W)
    Checkbutton(qWindow, text='Remove inf values, set to "0"',
                    variable=var1, onvalue=1, offvalue=0).grid(row=4, column=0, padx=265,sticky=W)
    Checkbutton(qWindow, text='Average surrounding "0" pixels',
                    variable=var2, onvalue=1, offvalue=0).grid(row=6, column=0, padx=265,sticky=W)
    
    qWindow.mainloop()
    ############################################################################
    
    ###############################################################################
    ###############################################################################
    #Progress Bar for Slices
    # Create the master object
    master = tk.Tk()
    # Create a progressbar widget
    progress_bar = ttk.Progressbar(master, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    
    # And a label for it
    label_1 = tk.Label(master, text="Z-Slice Progress Bar ")
    # Use the grid manager
    label_1.grid(row=0, column=0,pady=10)
    
    progress_bar.grid(row=0, column=1)
    
    master.geometry('250x100')
    master.attributes("-topmost", True)
    #################################################################
    #Set input in center on screen
    # Gets the requested values of the height and widht.
    windowWidth = master.winfo_reqwidth()
    windowHeight = master.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(master.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(master.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    master.geometry("+{}+{}".format(positionRight, positionDown))
    ##################################################################
    # Necessary, as the master object needs to draw the progressbar widget
    # Otherwise, it will not be visible on the screen
    master.update()
    progress_bar['value'] = 0
    master.update()
    ###############################################################################
    ###############################################################################
    #Set formula to all lower case
    vEntry_Formula_Value = vEntry_Formula_Value.lower()
    #find strings spilt by specific characters - to find channel numbers
    #re.split(r"[+|-|*|/|(|)]", vEntry_Formula_Value)
    
    #find duplicates and keep order list
    unique_strings_list = list(dict.fromkeys(re.split(r"[+|-|*|/|(|)]", vEntry_Formula_Value)))
    #Remove sqrt and pi
    unique_strings_list = [item for item in unique_strings_list if "ch" in item]
    
    #Remove 'ch' and convert result to integers
    #test if ch is followed by number, if not 
    try:
        vNumChannelsMath = [int(item) for item in [s.replace('ch', '') for s in unique_strings_list]]
    except ValueError:
        messagebox.showerror(title='Channel formula is invalid',
                                         message='Channel# may be missing (ch, should be ch1)')
        sys.exit
        
    pi= 3.1415926
    
    for vTimeIndex in range (vSizeT):
        for vZIndex in range (vDataSize[2]):
            vNewChannelValuesSlice = []
            for vChannelIndex in range (len(vNumChannelsMath)):
                vNewDataSliceTemp = vImarisDataSet.GetDataSubVolumeAs1DArrayFloats(0, 0, vZIndex, 
                                                            vNumChannelsMath[vChannelIndex]-1, vTimeIndex, 
                                                            vDataSize[0], vDataSize[1], 1)
                if vNumChannelsMath[vChannelIndex] == 1:
                    ch1 = vNewDataSliceTemp[0:]
                if vNumChannelsMath[vChannelIndex] == 2:
                    ch2 = vNewDataSliceTemp[0:] 
                if vNumChannelsMath[vChannelIndex] == 3:
                    ch3 = vNewDataSliceTemp[0:]
                if vNumChannelsMath[vChannelIndex] == 4:
                    ch4 = vNewDataSliceTemp[0:]
                if vNumChannelsMath[vChannelIndex] == 5:
                    ch5 = vNewDataSliceTemp[0:]
                if vNumChannelsMath[vChannelIndex] == 6:
                    ch6 = vNewDataSliceTemp[0:]    
                if vNumChannelsMath[vChannelIndex] == 7:
                    ch7 = vNewDataSliceTemp[0:]
                if vNumChannelsMath[vChannelIndex] == 8:
                    ch8 = vNewDataSliceTemp[0:]
                if vNumChannelsMath[vChannelIndex] == 9:
                    ch9 = vNewDataSliceTemp[0:]
                if vNumChannelsMath[vChannelIndex] == 10:
                    ch10 = vNewDataSliceTemp[0:]
            
            #Evaluate new Channel using formula using numexpr
            vNewChannelValuesSlice = ne.evaluate(vEntry_Formula_Value)
        
            if qRemoveInf == 1:#Set infinite positive and negative to "0"
                vNewChannelValuesSlice = np.nan_to_num(vNewChannelValuesSlice, posinf=0.0, neginf=0.0)
    
            #Find indices in slice that are "0"
            vNewChannel_0_Indices = np.where(vNewChannelValuesSlice == 0)[0].tolist()
    
            if qAverage_zeropixels == 1 and qRemoveInf == 1 and len(vNewChannel_0_Indices) > 1:     
     
                #Check how you use to handle the result
                #create list of edges indices
                vLeftEdgeIndices = list(range(0, len(vNewChannelValuesSlice), vDataSize[0]))
                vRightEdgeIndices = list(range(vDataSize[0]-1, len(vNewChannelValuesSlice), vDataSize[0]))
                vBottonEdgeIndices = list(range(0,vDataSize[0]))
                vTopEdgeIndices = list(range(len(vNewChannelValuesSlice)-vDataSize[0],len(vNewChannelValuesSlice),1))
    
                for  i in range (len(vNewChannel_0_Indices)):  
                    vWorkingsIndices = []
                    #LeftEdge
                    if vNewChannel_0_Indices[i] in vLeftEdgeIndices:
                        #corner bottomleft
                        if vNewChannel_0_Indices[i] == 0:
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + 1)#right of pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0])#top pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0] + 1)#topright
                        #corner topleft    
                        elif vNewChannel_0_Indices[i] == (len(vNewChannelValuesSlice) - vDataSize[0]):
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + 1)#right of pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0])#bottom pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0] + 1)#bottomright                    
                        else:
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + 1)#right of pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0])#top pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0] + 1)#topright
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0])#bottom pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0] + 1)#bottomright                   
                    #RightEdge
                    elif vNewChannel_0_Indices[i] in vRightEdgeIndices:
                        #corner bottomright
                        if vNewChannel_0_Indices[i] == (vDataSize[0] - 1):
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - 1)#left of pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0])#top pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0] - 1)#topleft
                        #corner topright
                        elif vNewChannel_0_Indices[i] == len(vNewChannelValuesSlice) - 1: 
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - 1)#left of pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0])#bottom pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0] - 1)#bottomleft  
                        else:
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - 1)#left of pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0])#top pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0] - 1)#topleft
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0])#bottom pixel
                            vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0] - 1)#bottomleft  
                    #BottomEdge
                    elif vNewChannel_0_Indices[i] in vBottonEdgeIndices:
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - 1)#left of pixel
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + 1)#right of pixel
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0])#top pixel
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0] + 1)#topright
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0] - 1)#topleft
                    #TopEdge
                    elif vNewChannel_0_Indices[i] in vTopEdgeIndices:
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - 1)#left of pixel
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + 1)#right of pixel
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0])#bottom pixel
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0] + 1)#bottomright
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0] - 1)#bottomleft
                    else:
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - 1)#left of pixel
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + 1)#right of pixel
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0])#top pixel
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0] + 1)#topright
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 - vDataSize[0] - 1)#topleft
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0])#bottom pixel
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0] + 1)#bottomright
                        vWorkingsIndices.append(vNewChannel_0_Indices[i] + 1 + vDataSize[0] - 1)#bottomleft     
                        
                    #grab all surrounding values and calculte mean (excluding any "0's")
                    vWorkingValue = np.take(vNewChannelValuesSlice,vWorkingsIndices)
                    #Add new value to the numpy array at specific index
                    vNewChannelValuesSlice[vNewChannel_0_Indices[i]] = np.mean(vWorkingValue[vWorkingValue != 0])    
            #Progress bar for slices thru time
            progress_bar['value'] = (vZIndex+1+(vDataSize[2]*vTimeIndex)) / (vDataSize[2]*vSizeT)*100#  % out of 100
            master.update()
            
            #Set to the new channel values
            vImarisDataSet.SetDataSubVolumeAs1DArrayFloats(vNewChannelValuesSlice.tolist(),
                                                           0,
                                                           0,
                                                           vZIndex,
                                                           vSizeC,
                                                           vTimeIndex,
                                                           vDataSize[0],
                                                           vDataSize[1],
                                                           1)
            #Set channel name to Formula used
            if vEntry_ChannelName_Value == 'New Channel Name':
                vImarisDataSet.SetChannelName(vSizeC, 'NewCh_' + vEntry_Formula_Value)
            else:
                vImarisDataSet.SetChannelName(vSizeC, 'NewCh_' + vEntry_ChannelName_Value)
            
    vImarisApplication.SetDataSet(vImarisDataSet)
    master.destroy()
    master.mainloop()
        







