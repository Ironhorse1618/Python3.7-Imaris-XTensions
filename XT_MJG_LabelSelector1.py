#Class Selector
#
#Written by Matthew J. Gastinger
#2023
#
    # <CustomTools>
    #     <Menu>
    #         <Submenu name="Spots Functions">
    #             <Item name="Label Selector1" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector1(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSpots">
    #             <Item name="Label Selector1" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector1(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #     </SurpassTab>
    # </CustomTools>

#Description
#List All Labels and Select all through time


import numpy as np

# GUI imports
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import time
import ImarisLib


aImarisId=0
def XT_MJG_LabelSelector1 (aImarisId)
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
    
    start = time.time()
    i=0
    vLabelValues=[]
    vLabelGroups=[]
    if qIsSpot:
        vSpots1 = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
        vSpots1PositionsXYZ = vSpots1.GetPositionsXYZ()
        vSpots1Radius = vSpots1.GetRadiiXYZ()
        vSpots1TimeIndices = vSpots1.GetIndicesT()
        vSpots1Ids = vSpots1.GetIds()
        for i in range (len(vSpots1Ids)):
            x = str(vSpots1.GetLabelsOfId(vSpots1Ids[i]))
            if x == '[]':
                continue
            else:
                vLabelValues.append(str(x[x.index('mLabelValue = ')+14:-3]))
                vLabelGroups.append(str(x[x.index('mGroupName = ')+13:-3]).split('\n')[0])     
        vLabelsUnique = []
        
        for item in vLabelValues:
            if item not in vLabelsUnique:
                vLabelsUnique.append(item)
    
    
    if qIsSurface:
        vSurfaces = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
        z=1
    
    # elapsed = time.time() - start
    # print(elapsed)
    
    
    #####################################################
    #Making the Listbox for the Surpass menu
    main = Tk()
    main.title("Label Selection")
    main.geometry("+50+50")
    main.attributes("-topmost", True)
    
    #################################################################
    #Set input in center on screen
    # Gets the requested values of the height and widht.
    windowWidth = main.winfo_reqwidth()
    windowHeight = main.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(main.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(main.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    main.geometry("+{}+{}".format(positionRight, positionDown))
    ##################################################################
    names = StringVar()
    names.set(vLabelsUnique)
    lstbox = Listbox(main, listvariable=names, selectmode=SINGLE, width=15, height=10)
    lstbox.grid(column=  0, row=1)
    
    def select():
        global vLabelSelection
        ObjectSelection = list()
        vLabelSelection = lstbox.curselection()
    
        if len(ObjectSelection) > 2:
            messagebox.showerror(title='Label Selection',
                              message='Please Select 1 Label')
            main.mainloop()
        else:
            main.destroy()
    
    
    btn = Button(main, text="Duplicate Labels", command=select)
    btn.grid(column=0, row=3, sticky=W)
    
    #Selects the top items in the list
    lstbox.selection_set(0)
    main.mainloop()
    
    ##############################################################################
    vLabelChoice=vLabelsUnique[vLabelSelection[0]]
    vNewSpotIndices = [i for i, s in enumerate(vLabelValues) if vLabelChoice in s]
    
    vSpots1PositionsXYZ = vSpots1.GetPositionsXYZ()
    vSpots1Radius = vSpots1.GetRadiiXYZ()
    vSpots1TimeIndices = vSpots1.GetIndicesT()
    
    vNewSpots1PositionsXYZ = (np.array(vSpots1PositionsXYZ)[np.array(vNewSpotIndices)]).tolist()
    vNewSpots1TimeIndices = (np.array(vSpots1TimeIndices)[np.array(vNewSpotIndices)]).tolist()
    vNewSpots1Radius = [(np.array(vSpots1Radius)[np.array(vNewSpotIndices)])][0][:,0]
    
    
    ###Create New Spots object
    vNewSpots1 = vImarisApplication.GetFactory().CreateSpots()
    vNewSpots1.SetName(vSpots1.GetName() + '--' + vLabelChoice + ' -- Copied')
    vNewSpots1.SetColorRGBA(18000)
    vNewSpots1.Set(vNewSpots1PositionsXYZ, vNewSpots1TimeIndices, vNewSpots1Radius)
    vImarisApplication.GetSurpassScene().AddChild(vNewSpots1, -1)
    vSpots1.SetVisible(0)


#Create Labels for vNewSpots1
# wLabelList = []
# wLabelIndices = np.arange(0,len(vNewSpotIndices)-1)
# for i in range(len(wLabelIndices[0])):
#     vLabelCreate = vFactory.CreateObjectLabel(wLabelIndices[i], 'Coloc', vLabelChoice)
#     wLabelList.append(vLabelCreate)
# vSpots1.SetLabels(wLabelList)



# np.arange(0,len(vNewSpotIndices)-1)
# vSurpassObject.GetLabelsOfId(vSpots1Ids[6])


# vLabelValues = (str(x[x.index('mLabelValue = ')+14:-3]))
# vLabelGroup = str(x[x.index('mGroupName = ')+13:-3]).split('\n')[0]     
                                                           

# newTest=[]
# newTest.extend(vTest)
