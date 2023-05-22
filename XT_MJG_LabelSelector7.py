#LAbel Class Selector
##Written by Matthew J. Gastinger
#2023
#
    # <CustomTools>
    #     <Menu>
    #         <Submenu name="Spots Functions">
    #             <Item name="Label Selector7" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector7(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSpots">
    #             <Item name="Label Selector7" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector7(%i)</Command>
    #             </Item>
    #         </SurpassComponent>
    #     </SurpassTab>
    #     <Menu>
    #         <Submenu name="Surfaces Functions">
    #             <Item name="Label Selector7" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector7(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSurfaces">
    #             <Item name="Label Selector7" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_LabelSelector7(%i)</Command>
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

aImarisId=0
def XT_MJG_LabelSelector7(aImarisId):
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
    # Create the master object for progress bar
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
    vALL_LabelValues = []
    vALL_Label_Ids = []
    vALL_GroupNames = []
    
    vGetAllObjectLabels = vObject.GetLabels()
    if len(vGetAllObjectLabels) == []:
        messagebox.showerror(title='Label Object Duplicate',
                              message='PLease create some labels!!!')
        master.destroy()
        exit()
    
    for i in range (len(vGetAllObjectLabels)):
        vALL_LabelValues.append(vGetAllObjectLabels[i].mLabelValue)
        vALL_GroupNames.append(vGetAllObjectLabels[i].mGroupName)
        vALL_Label_Ids.append(vGetAllObjectLabels[i].mId)
        if vGetAllObjectLabels[i].mLabelValue not in vLabelClass:
            vLabelClass.append(vGetAllObjectLabels[i].mLabelValue)
        qProgressBar['value'] = i/len(vGetAllObjectLabels)*100
        master.update()
    # elapsed = time.time() - start
    # print('new--'+str(elapsed))
    master.destroy()
    master.mainloop()
    
    i=0
    vGroupNames = np.unique(np.array(vALL_GroupNames))
    vGroupLabels=[]
    for i in range(len(vGroupNames)):
        test=(np.where(np.array(vALL_GroupNames)==vGroupNames[i]))[0].tolist()
        vGroupLabels.append(np.unique(np.array(vALL_LabelValues)[test]))
    
    #create set for ListBox
    zListboxNames = []
    zListboxIndex = []
    for i in range(len(vGroupNames)):
        for j in range(len(vGroupLabels[i])):
            zListboxNames.append(str(vGroupNames[i]) + ' - ' + str(vGroupLabels[i][j]))
            zListboxIndex.append([i, j])
    
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
    names.set(zListboxNames)
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
    #Group and Label Selection
    vLabelChoice=zListboxNames[vLabelSelection[0]]
    
    vSelectedGroup = vGroupNames[zListboxIndex[vLabelSelection[0]][0]]
    vSelectedLabel = vGroupLabels[zListboxIndex[vLabelSelection[0]][0]][zListboxIndex[vLabelSelection[0]][1]]
    x1=np.where(np.array(vALL_GroupNames)==vSelectedGroup)[0].tolist()
    x2=np.where(np.array(vALL_LabelValues)==vSelectedLabel)[0].tolist()
    
    if qIsSpot:
    #Original Spot data
        vObjectPositionsXYZ = vObject.GetPositionsXYZ()
        vObjectRadius = vObject.GetRadiiXYZ()
        vObjectTimeIndices = vObject.GetIndicesT()
        vObject.GetColorRGBA()
    
        #Parsed Spot data only in the Select Group/Class
        sorter = np.argsort(vIds)
        vNewObjectPositionsXYZ = list(pd.Series(vObject.GetPositionsXYZ())[(sorter[np.searchsorted(vIds,np.array(vALL_Label_Ids)[np.intersect1d(x1,x2).tolist()],sorter=sorter)])])
        vNewObjectRadius = list(pd.Series(np.array(vObjectRadius)[:,0])[(sorter[np.searchsorted(vIds,np.array(vALL_Label_Ids)[np.intersect1d(x1,x2).tolist()],sorter=sorter)])])
        vNewObjectTimeIndices = list(pd.Series(vObject.GetIndicesT())[(sorter[np.searchsorted(vIds,np.array(vALL_Label_Ids)[np.intersect1d(x1,x2).tolist()],sorter=sorter)])])
    
        ###Create New Spots object
        vNewObject = vImarisApplication.GetFactory().CreateSpots()
        vNewObject.SetName(vObject.GetName() + '--' + vLabelChoice + ' -- Copied')
        vNewObject.Set(vNewObjectPositionsXYZ, vNewObjectTimeIndices, vNewObjectRadius)
        vImarisApplication.GetSurpassScene().AddChild(vNewObject, -1)
    else:
        sorter = np.argsort(vIds)
        zLabelIDsFinal = (sorter[np.searchsorted(vIds,np.array(vALL_Label_Ids)[np.intersect1d(x1,x2).tolist()],sorter=sorter)])
        vNewObject = vImarisApplication.GetFactory().CreateSurfaces()
        for aIdIndex in range (len(zLabelIDsFinal)):
            vTimeIndex = vObject.GetTimeIndex(zLabelIDsFinal[aIdIndex])
            vNewObject.AddSurfaceWithNormals(vObject.GetSurfaceData(zLabelIDsFinal[aIdIndex]),
                                     vObject.GetSurfaceNormals(zLabelIDsFinal[aIdIndex]),
                                     vTimeIndex)
            qProgressBar['value'] = aIdIndex/len(zLabelIDsFinal)*100
            master.update()
        vNewObject.SetName(vObject.GetName() + '--' + vLabelChoice + ' -- Copied')
    ########################################################################
    ########################################################################
    vImarisApplication.GetSurpassScene().AddChild(vNewObject, -1)
    vObject.SetVisible(0)
    
    master.destroy()
    master.mainloop()
    
