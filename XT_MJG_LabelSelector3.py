#LAbel Class Selector
##Written by Matthew J. Gastinger
#2023
#
    # <CustomTools>
    #     <Menu>
    #         <Submenu name="Spots Functions">
    #             <Item name="Label Selector3" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector3(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSpots">
    #             <Item name="Label Selector3" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector3(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #     </SurpassTab>
    #     <Menu>
    #         <Submenu name="Surfaces Functions">
    #             <Item name="Label Selector3" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector3(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSurfaces">
    #             <Item name="Label Selector3" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector3(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #     </SurpassTab>
    # </CustomTools>

#Description
#List All Labels and Select all through time
#Works for SPots and SUrfaces


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
def XT_MJG_LabelSelector3 (aImarisId)
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
    
    vLabelValues=[]
    vLabelGroups=[]
    if qIsSpot:
        vObject = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
        vObjectPositionsXYZ = vObject.GetPositionsXYZ()
        vObjectRadius = vObject.GetRadiiXYZ()
        vObjectTimeIndices = vObject.GetIndicesT()
        vIds = vObject.GetIds()
    else:
        vObject = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
        vIds = vObject.GetIds()
    
    # x = str(vObject.GetLabelsOfId(vIds[0]))
    
    # for i in range (len(vIds)):
    #     x = str(vObject.GetLabelsOfId(vIds[i]))
    #     if x == '[]':
    #         continue
    #     else:
    #         # vLabelValues.append(str(x[x.index('mLabelValue = ')+14:-3]))
    #         # vLabelGroups.append(str(x[x.index('mGroupName = ')+13:-3]).split('\n')[0])     
    #         vLabelValues.append(str(x[x.index('mLabelValue = ')+14:x.index('mLabelValue = ')+14+str(x[x.index('mLabelValue = ')+14:-1]).find('\n')]))
    start = time.time()
    test=vObject.GetLabels()
    
    for i in range (len(test)):
        xNEW = str(str(test[i])[str(test[i]).index('mLabelValue = ')+14:str(test[i]).index('mLabelValue = ')+14+str(str(test[i])[str(test[i]).index('mLabelValue = ')+14:-1]).find('\n')])
        if xNEW not in vLabelValues:
            vLabelValues.append(xNEW)
    elapsed = time.time() - start
    print(elapsed)
            
            
    vLabelsUnique = []
    
    for item in vLabelValues:
        if item not in vLabelsUnique:
            vLabelsUnique.append(item)
    
    # str(x[x.index('mLabelValue = ')+14:x.index('mLabelValue = ')+14+str(x[x.index('mLabelValue = ')+14:-1]).find('\n')])
    
    
    
    
    
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
    lstbox = Listbox(main, listvariable=names, selectmode=SINGLE, width=25, height=10)
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
    #Group and Label Selection
    vLabelChoice=vLabelsUnique[vLabelSelection[0]]
    #vObject indices in the Selected Group/Class
    vNewObjectIndices = [i for i, s in enumerate(vLabelValues) if vLabelChoice in s]
    vObject.GetColorRGBA()
    
    if qIsSpot:
    #Original Spot data
        vObjectPositionsXYZ = vObject.GetPositionsXYZ()
        vObjectRadius = vObject.GetRadiiXYZ()
        vObjectTimeIndices = vObject.GetIndicesT()
        
        #Parsed Spot data only in the Select Group/Class
        vNewObjectPositionsXYZ = (np.array(vObjectPositionsXYZ)[np.array(vNewObjectIndices)]).tolist()
        vNewObjectTimeIndices = (np.array(vObjectTimeIndices)[np.array(vNewObjectIndices)]).tolist()
        vNewObjectRadius = [(np.array(vObjectRadius)[np.array(vNewObjectIndices)])][0][:,0]
        ###Create New Spots object
        vNewObject = vImarisApplication.GetFactory().CreateSpots()
        vNewObject.SetName(vObject.GetName() + '--' + vLabelChoice + ' -- Copied')
        vNewObject.Set(vNewObjectPositionsXYZ, vNewObjectTimeIndices, vNewObjectRadius)
        vImarisApplication.GetSurpassScene().AddChild(vNewObject, -1)
    else:
        vNewObject = vImarisApplication.GetFactory().CreateSurfaces()
        vNewObject = vObject.CopySurfaces(vNewObjectIndices)
        vNewObject.SetName(vObject.GetName() + '--' + vLabelChoice + ' -- Copied')
        
    vImarisApplication.GetSurpassScene().AddChild(vNewObject, -1)
    vObject.SetVisible(0)
    
    
