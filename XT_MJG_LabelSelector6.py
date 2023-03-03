#LAbel Class Selector
##Written by Matthew J. Gastinger
#2023
#
    # <CustomTools>
    #     <Menu>
    #         <Submenu name="Spots Functions">
    #             <Item name="Label Selector6" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector6(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSpots">
    #             <Item name="Label Selector6" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector6(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #     </SurpassTab>
    #     <Menu>
    #         <Submenu name="Surfaces Functions">
    #             <Item name="Label Selector6" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector6(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSurfaces">
    #             <Item name="Label Selector6" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector6(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #     </SurpassTab>
    # </CustomTools>

#Description
#List All Labels and Select all through time
#Works for SPots and SUrfaces

import pandas as pd
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

def XT_MJG_LabelSelector6 (aImarisId)
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
    
    ########################################################################
    ########################################################################
    # Create the master object
    master = tk.Tk()
    # Create a progressbar widget
    qProgressBar = ttk.Progressbar(master, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    # And a label for it
    label_1 = tk.Label(master, text="Duplicate Labels")
    # Use the grid manager
    label_1.grid(row=0, column=0,pady=10)
    qProgressBar.grid(row=0, column=1)
    master.geometry('270x50')
    master.attributes("-topmost", True)
    #######################
    #Set input in center on screen
    # Gets the requested values of the height and widht.
    windowWidth = master.winfo_reqwidth()
    windowHeight = master.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(master.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(master.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    master.geometry("+{}+{}".format(positionRight, positionDown))
    #######################
    # Necessary, as the master object needs to draw the progressbar widget
    # Otherwise, it will not be visible on the screen
    master.update()
    qProgressBar['value'] = 0
    master.update()
    ########################################################################
    ########################################################################
    
    vSurpassObject = vImarisApplication.GetSurpassSelection()
    qIsSurface = vImarisApplication.GetFactory().IsSurfaces(vSurpassObject)
    qIsSpot = vImarisApplication.GetFactory().IsSpots(vSurpassObject)
    
    if qIsSpot:
        vObject = vFactory.ToSpots(vImarisApplication.GetSurpassSelection())
        vObjectPositionsXYZ = vObject.GetPositionsXYZ()
        vObjectRadius = vObject.GetRadiiXYZ()
        vObjectTimeIndices = vObject.GetIndicesT()
        vIds = vObject.GetIds()
    else:
        vObject = vFactory.ToSurfaces(vImarisApplication.GetSurpassSelection())
        vIds = vObject.GetIds()
    
    vLabelClass = []
    vLabelGroup = []
    vLabelValuesALL = []
    vLabelIdsALL = []
    vLabelsALLGroupName = []
    
    vGetAllObjectLabels = vObject.GetLabels()
    if len(vGetAllObjectLabels) == []:
        messagebox.showerror(title='Label Object Duplicate',
                              message='PLease create some labels!!!')
        master.destroy()
        exit()
    
    for i in range (len(vGetAllObjectLabels)):
        vLabelValuesALL.append(vGetAllObjectLabels[i].mLabelValue)
        vLabelsALLGroupName.append(vGetAllObjectLabels[i].mGroupName)
        vLabelIdsALL.append(vGetAllObjectLabels[i].mId)
        if vGetAllObjectLabels[i].mLabelValue not in vLabelClass:
            vLabelClass.append(vGetAllObjectLabels[i].mLabelValue)
        qProgressBar['value'] = i/len(vGetAllObjectLabels)*100
        master.update()
    # elapsed = time.time() - start
    # print('new--'+str(elapsed))
    master.destroy()
    master.mainloop()
    
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
    names.set(vLabelClass)
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
    vLabelChoice=vLabelClass[vLabelSelection[0]]
    
    ########################################################################
    # Create the master object
    master = tk.Tk()
    # Create a progressbar widget
    qProgressBar = ttk.Progressbar(master, orient="horizontal",
                                  mode="determinate", maximum=100, value=0)
    # And a label for it
    label_1 = tk.Label(master, text="Duplicating Surface Labels")
    # Use the grid manager
    label_1.grid(row=0, column=0,pady=10)
    qProgressBar.grid(row=0, column=1)
    master.geometry('270x50')
    master.attributes("-topmost", True)
    #######################
    #Set input in center on screen
    # Gets the requested values of the height and widht.
    windowWidth = master.winfo_reqwidth()
    windowHeight = master.winfo_reqheight()
    # Gets both half the screen width/height and window width/height
    positionRight = int(master.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(master.winfo_screenheight()/2 - windowHeight/2)
    # Positions the window in the center of the page.
    master.geometry("+{}+{}".format(positionRight, positionDown))
    #######################
    # Necessary, as the master object needs to draw the progressbar widget
    # Otherwise, it will not be visible on the screen
    master.update()
    qProgressBar['value'] = 0
    master.update()
    ########################################################################
    ########################################################################
    if qIsSpot:
    #Original Spot data
        vObjectPositionsXYZ = vObject.GetPositionsXYZ()
        vObjectRadius = vObject.GetRadiiXYZ()
        vObjectTimeIndices = vObject.GetIndicesT()
        vObject.GetColorRGBA()
        
        #Parsed Spot data only in the Select Group/Class
        sorter = np.argsort(vIds)
        vNewObjectPositionsXYZ = list(pd.Series(vObject.GetPositionsXYZ())[(sorter[np.searchsorted(vIds, np.array(vLabelIdsALL)[(np.where(np.array(vLabelValuesALL)==vLabelChoice))[0].tolist()], sorter=sorter)]).tolist()])
        vNewObjectRadius = list(pd.Series(np.array(vObjectRadius)[:,0])[(sorter[np.searchsorted(vIds, np.array(vLabelIdsALL)[(np.where(np.array(vLabelValuesALL)==vLabelChoice))[0].tolist()], sorter=sorter)]).tolist()])
        vNewObjectTimeIndices = list(pd.Series(vObject.GetIndicesT())[(sorter[np.searchsorted(vIds, np.array(vLabelIdsALL)[(np.where(np.array(vLabelValuesALL)==vLabelChoice))[0].tolist()], sorter=sorter)]).tolist()])
    
        ###Create New Spots object
        vNewObject = vImarisApplication.GetFactory().CreateSpots()
        vNewObject.SetName(vObject.GetName() + '--' + vLabelChoice + ' -- Copied')
        vNewObject.Set(vNewObjectPositionsXYZ, vNewObjectTimeIndices, vNewObjectRadius)
        vImarisApplication.GetSurpassScene().AddChild(vNewObject, -1)
    else:
        sorter = np.argsort(vIds)
        zLabelIDsFinal = (sorter[np.searchsorted(vIds, np.array(vLabelIdsALL)[(np.where(np.array(vLabelValuesALL)==vLabelChoice))[0].tolist()], sorter=sorter)]).tolist()
        vNewObject = vImarisApplication.GetFactory().CreateSurfaces()
        for aIdIndex in range (len(np.array(vLabelIdsALL)[(np.where(np.array(vLabelValuesALL)==vLabelChoice))[0].tolist()])):
            vTimeIndex = vObject.GetTimeIndex(zLabelIDsFinal[aIdIndex])
            vNewObject.AddSurfaceWithNormals(vObject.GetSurfaceData(zLabelIDsFinal[aIdIndex]),
                                     vObject.GetSurfaceNormals(zLabelIDsFinal[aIdIndex]),
                                     vTimeIndex)
            qProgressBar['value'] = aIdIndex/len(np.array(vLabelIdsALL)[(np.where(np.array(vLabelValuesALL)==vLabelChoice))[0].tolist()])*100
            master.update()
        vNewObject.SetName(vObject.GetName() + '--' + vLabelChoice + ' -- Copied')
    ########################################################################
    ########################################################################
    vImarisApplication.GetSurpassScene().AddChild(vNewObject, -1)
    vObject.SetVisible(0)
    
    master.destroy()
    master.mainloop()
    
