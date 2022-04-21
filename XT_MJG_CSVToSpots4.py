#CSV file to Spots
# Written by Matthew J. Gastinger
# April 2022 - Imaris 9.9.0


#    <CustomTools>
#      <Menu>
      #   <Item name="CSV Postions to Spots" icon="Python3">
    #         <Command>Python3XT::XT_MJG_CSVToSpots4(%i)</Command>
  #       </Item>
#      </Menu>
#    </CustomTools>

#Description:
    #Converts .csv text document (comma delimited) with spot positions and labels
    #This script will work with both 3D and 2D spot postions.  No volume is
    #required to import Spots.  The NEW Volume is generated based on the
    #max and min Spot positions of the imported spots.

    #Expected format of the .csv file
        # Column 1 - X Position (um)
        # Column 2 - Y Position (um)
        # Column 3 - Z Position (um)
        # Column 4 - labeled region
    #Voxel size in XYZ are required for the import to be properly formatted.

#NOTES
#Currently only works on a Windows system.


import numpy as np
import ImarisLib
import tkinter as tk
from tkinter.filedialog import askopenfile
from tkinter import messagebox
from tkinter import *
from tkinter import ttk
import pandas
import Imaris
import os
import time
import random

#aImarisId=0

def XT_MJG_CSVToSpots4(aImarisId):

    # Create an ImarisLib object
    vImarisLib = ImarisLib.ImarisLib()
    #Get Current Imaris Version
    vImarisApplication = vImarisLib.GetApplication(aImarisId)
    aImarisVersion = str(vImarisApplication.GetVersion())[11 : 16]
    #Create Windows Imaris Application Path
    aNewImarisAppPath=str("C:\Program Files\Bitplane\Imaris " + aImarisVersion + "\imaris.exe")
    ############################################################################
    #Select CSV Data to import
    root = tk.Tk()
    root.withdraw() #use to hide tkinter window
    file = askopenfile(mode ='r', filetypes =[('All Files', '*.*')])
    dataframe = pandas.read_csv(file.name)
    vSpotsDataAll=dataframe.to_numpy()
    vSpotsPositionsOnly=vSpotsDataAll[:,:3]
    vSpotsXYZ = vSpotsPositionsOnly.tolist()# for spot creation needs to be list
    root.destroy()

    ############################################################################
    ############################################################################
    vSpotDataAllList=vSpotsDataAll.tolist()

    # Creating tkinter my_w
    my_w = tk.Tk()
    my_w.geometry("500x300")
    my_w.title("CHECK format of CSV file")

    # Set Treeview widget
    trv = ttk.Treeview(my_w)#, selectmode ='browse')
    trv.grid(row=0, column=0)
    trv.pack()

    #DEfining the STOP button to kill the import
    def STOP():
        messagebox.showerror(title='Failure to Import',
                              message='Text file needs to be in proper format\n'
                              'Column1---X Position\n'
                              'Column2---Y Position\n'
                              'Column3---Z Position\n'
                              'Column4--- labels, if present')
        my_w.destroy()
        sys.exit()
    #Defining the Continue button...
    def CONTINUE():
        global vVoxelSizeX, vVoxelSizeY, vVoxelSizeZ
        if float(EntryVoxelX.get())<=0 or float(EntryVoxelY.get())<=0 or float(EntryVoxelZ.get())<=0:
            messagebox.showerror(title='Improper Voxel Size',
                             message='Please Set Voxel Sizes!!\n'
                             'If 2D, set Z Voxel size to X Voxel size!')
            my_w.mainloop()
        vVoxelSizeX=[float(EntryVoxelX.get())]
        vVoxelSizeY=[float(EntryVoxelY.get())]
        vVoxelSizeZ=[float(EntryVoxelZ.get())]
        my_w.destroy()

    # column identifiers
    trv['columns']=('1', '2', '3','4','5','6')
    trv.column('#0', width=0, stretch=NO)
    trv.column('1', anchor=CENTER, width=75)
    trv.column('2', anchor=CENTER, width=75)
    trv.column('3', anchor=CENTER, width=75)
    trv.column('4', anchor=CENTER, width=50)
    trv.column('5', anchor=CENTER, width=60)
    trv.column('6', anchor=CENTER, width=60)

    # Defining headings, other option is tree
    trv.heading('#0', text='', anchor=CENTER)
    trv.heading('1', text='1', anchor=CENTER)
    trv.heading('2', text='2', anchor=CENTER)
    trv.heading('3', text='3', anchor=CENTER)
    trv.heading('4', text='4', anchor=CENTER)
    trv.heading('5', text='5', anchor=CENTER)
    trv.heading('6', text='6', anchor=CENTER)
    #define buttons
    ContinueButton=Button(my_w, text='Continue Import', bg='green', fg='white',command=CONTINUE)
    STOPBUtton=Button(my_w, text='STOP Import', bg='red', fg='white',command=STOP)
    ContinueButton.pack(side=tk.RIGHT,fill=tk.Y, padx=6)
    STOPBUtton.pack(side=tk.RIGHT,fill=tk.Y)

    #Insert the top 3 lines into TreeView
    trv.insert(parent='', index=0, iid=0, text='', values=vSpotDataAllList[0])
    trv.insert(parent='', index=1, iid=1, text='', values=vSpotDataAllList[1])
    trv.insert(parent='', index=2, iid=2, text='', values=vSpotDataAllList[2])

    #Create Label and Entry for VoxelSizes
    LabelVoxelX=Label(my_w, text="X Voxel")
    LabelVoxelY=Label(my_w, text="Y Voxel")
    LabelVoxelZ=Label(my_w, text="Z Voxel")
    EntryVoxelX = tk.Entry(my_w,width=6,justify='center')
    EntryVoxelY = tk.Entry(my_w,width=6,justify='center')
    EntryVoxelZ = tk.Entry(my_w,width=6,justify='center')
    EntryVoxelX.insert(0, '4.06')
    EntryVoxelY.insert(0, '4.06')
    EntryVoxelZ.insert(0, '3')
    LabelVoxelX.pack(side=tk.LEFT)
    EntryVoxelX.pack(side=tk.LEFT)
    LabelVoxelY.pack(side=tk.LEFT)
    EntryVoxelY.pack(side=tk.LEFT)
    LabelVoxelZ.pack(side=tk.LEFT)
    EntryVoxelZ.pack(side=tk.LEFT)

    my_w.mainloop()

    ###########################################################################
    ############################################################################
    # Do you want to create labels?
    question = Tk()
    question.withdraw()
    #Question = Toplevel(root) # (Manually put toplevel in front of root)
    w = question.winfo_reqwidth()
    h = question.winfo_reqheight()
    ws = question.winfo_screenwidth()
    hs = question.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    question.geometry('+%d+%d' % (x, y))
    #Smoothing or no smoothing for the Coloc result
    vQuestionAddLabels = messagebox.askyesno('Label Creation',
                            'Do you want to add Labels to the Spots?\n'
                            'WARNING:  If you have over 10000 Spots,\n'
                            '          this process could be slow')
    question.lift()

    question.destroy()


    ###########################################################################
    ############################################################################
    #Start new instance of Imaris
    os.startfile(aNewImarisAppPath)
    aImarisId=aImarisId+1
    #Test new Imaris application has started
    aAppTest=vImarisLib.GetApplication(aImarisId)
    while aAppTest==None:
        aAppTest=vImarisLib.GetApplication(aImarisId)
    ############################################################################
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

    ############################################################################
    ############################################################################
    #Set data for spots on 3D volume no time or track. Set all spot to time=0.
    vSpotsTotalNumber=vSpotsPositionsOnly.shape[0]#Number of spots
    vSpotsTime = [0]*vSpotsPositionsOnly.shape[0]#no time lapse
    vSpotsRadius = [1]*vSpotsPositionsOnly.shape[0]#Set spot radius to 1.
    #Set Voxel Size
    # vVoxelSizeX = 4.06
    # vVoxelSizeY = 4.06
    # vVoxelSizeZ = 3
    # #Input Voxel sizes - REquired
    # master = tk.Tk()

    # def VoxelValues():
    #     global vVoxelSizeX, vVoxelSizeY, vVoxelSizeZ
    #     vVoxelSizeX = e1.get()
    #     vVoxelSizeY = e2.get()
    #     vVoxelSizeZ = e3.get()


    # tk.Label(master, text="X - Voxel Size").grid(row=0)
    # tk.Label(master, text="Y - Voxel Size").grid(row=1)
    # tk.Label(master, text="Z - Voxel Size").grid(row=2)
    # e1 = tk.Entry(master)
    # e2 = tk.Entry(master)
    # e3 = tk.Entry(master)
    # e1.grid(row=0, column=1)
    # e2.grid(row=1, column=1)
    # e3.grid(row=2, column=1)
    # VoxelButton=Button(master, text='Get Voxel Values',command=VoxelValues)
    # VoxelButton.grid(row=3, column=1)

    # master.mainloop()
    ############################################################################
    ############################################################################


    vExtendMinX = vSpotsPositionsOnly.min(axis=0)[0]
    vExtendMinY = vSpotsPositionsOnly.min(axis=0)[1]
    vExtendMinZ = vSpotsPositionsOnly.min(axis=0)[2]
    vExtendMaxX = vSpotsPositionsOnly.max(axis=0)[0]
    vExtendMaxY = vSpotsPositionsOnly.max(axis=0)[1]
    vExtendMaxZ = vSpotsPositionsOnly.max(axis=0)[2]

    #For single time point
    vSizeC = 1
    vSizeT = 1
    vSizeX = int(round((vExtendMaxX-vExtendMinX)/vVoxelSizeX[0],0))#Number of Voxels in X direction
    vSizeY = int(round((vExtendMaxY-vExtendMinY)/vVoxelSizeY[0],0))#Number of Voxels in Y direction
    vSizeZ = int(round((vExtendMaxZ-vExtendMinZ)/vVoxelSizeZ[0],0)) #Number of Voxels in Z direction
    #Creat new Dataset image properties
    vType   = Imaris.tType.eTypeUInt8
    vDataSet = vFactory.CreateDataSet()
    vDataSet.SetType(vType)
    vDataSet.Create(vType, vSizeX, vSizeY, vSizeZ,vSizeC,vSizeT)
    #Add image to Imaris application
    vImarisApplication.SetImage(0, vDataSet)

    #Set image Extends boundaries
    vImarisApplication.GetDataSet().SetExtendMinX(vExtendMinX)
    vImarisApplication.GetDataSet().SetExtendMinY(vExtendMinY)
    vImarisApplication.GetDataSet().SetExtendMinZ(vExtendMinZ)
    vImarisApplication.GetDataSet().SetExtendMaxX(vExtendMaxX)
    vImarisApplication.GetDataSet().SetExtendMaxY(vExtendMaxY)
    vImarisApplication.GetDataSet().SetExtendMaxZ(vExtendMaxZ)
    ############################################################################
    ############################################################################
    #Create the a new spots object with imported positions
    vNewSpots = vImarisApplication.GetFactory().CreateSpots()
    vNewSpots.Set(vSpotsXYZ, vSpotsTime, vSpotsRadius)
    vNewSpots.SetColorRGBA(255)
    vNewSpots.SetName('All Spots added from CSV')
    vSurpassScene = vImarisApplication.GetSurpassScene()
    vSurpassScene.AddChild(vNewSpots, -1)

    vImarisApplication.SetChannelVisibility(0,0);
    vImarisApplication.GetSurpassCamera().Fit()

    ############################################################################
    #Add new SPots object for each label
    vNewSpotsLabelFolder = vImarisApplication.GetFactory().CreateDataContainer()
    vNewSpotsLabelFolder.SetName('Labeled Spots from CSV')

    vLabelNames = np.unique(vSpotsDataAll[:,3])
    for i in range (len(vLabelNames)):
        vNewSpotsRegion = vImarisApplication.GetFactory().CreateSpots()

        vLabelIndices = (np.where(vSpotsDataAll[:,3] == vLabelNames[i]))[0].tolist()
        vNewSpotsRegionXYZ=vSpotsDataAll[vLabelIndices]
        vNewSpotsRegionTime = [0]*len(vLabelIndices)
        vNewSpotsRegionRadius = [1]*len(vLabelIndices)
    #set new Spots object per region with Random color
        vNewSpotsRegion.Set(vNewSpotsRegionXYZ[:,:3].tolist(), vNewSpotsRegionTime, vNewSpotsRegionRadius)
        zRandomColor=((random.uniform(0, 1)) * 256 * 256 * 256 )
        vNewSpotsRegion.SetColorRGBA(zRandomColor)
        vNewSpotsRegion.SetName(str(vLabelNames[i]))
        vNewSpotsLabelFolder.AddChild(vNewSpotsRegion, -1)
        vImarisApplication.GetSurpassScene().AddChild(vNewSpotsLabelFolder, -1)

    # vNewSpotsRegionXYZ=vNewSpotsRegionXYZ[:,:3].tolist()

    ############################################################################
    ############################################################################
    #Add Labels
    #Find unique labels in column#4

    if vQuestionAddLabels == True:
        master = tk.Tk()
        # Create a progressbar widget
        progress_bar = ttk.Progressbar(master, orient="horizontal",
                                      mode="determinate", maximum=100, value=0)
        progressbarlabel = tk.Label(master, text="Creating Spot Labels...")
        progressbarlabel.grid(row=0, column=0)
        progress_bar.grid(row=0, column=1)
        master.update()
        progress_bar['value'] = 0
        master.update()

        # import time
        # start = time.time()
        # scount=0
        # vLabelNames = np.unique(vSpotsDataAll[:,3])
        # for i in range (len(vLabelNames)):
        #     vLabelIndices = (np.where(vSpotsDataAll[:,3] == vLabelNames[i]))[0].tolist()
        #     scount=scount+1
        #     for j in range (len(vLabelIndices)):
        #         vLabelCreate = vFactory.CreateObjectLabel(vLabelIndices[j], "LabelSet1", vLabelNames[i])
        #         wLabelList = [vLabelCreate]
        #         vNewSpots.SetLabels(wLabelList)
        #     progress_bar['value'] = scount/len(vLabelNames)*100 #  % out of 100
        #     master.update()

        # elapsed = time.time() - start
        # print(elapsed)
    ############################################################################
    # #Igors verison moves the SEt labels outside loop
    #     scount=0
    #     vLabelNames = np.unique(vSpotsDataAll[:,3])
    #     wLabelList=[]
    #     start = time.time()

    #     for i in range (len(vLabelNames)):
    #         vLabelIndices = (np.where(vSpotsDataAll[:,3] == vLabelNames[i]))[0].tolist()
    #         # scount=scount+1
    #         for j in range (len(vLabelIndices)):
    #             vLabelCreate = vFactory.CreateObjectLabel(vLabelIndices[j], "LabelSet1", vLabelNames[i])
    #             wLabelList.append(vLabelCreate)
    #             progress_bar['value'] = scount/len(vSpotsDataAll)*100 #  % out of 100
    #             scount=scount+1
    #             master.update()
    #         # progress_bar['value'] = scount/len(vLabelNames)*100 #  % out of 100
    #         # master.update()
    #     vNewSpots.SetLabels(wLabelList)

        # elapsed = time.time() - start
        # print(elapsed)
    ############################################################################
    #Igors verison moves the SEt labels outside loop once per region
        scount=0
        vLabelNames = np.unique(vSpotsDataAll[:,3])
        # start = time.time()
        for i in range (len(vLabelNames)):
            vLabelIndices = (np.where(vSpotsDataAll[:,3] == vLabelNames[i]))[0].tolist()
            wLabelList=[]
            for j in range (len(vLabelIndices)):
                vLabelCreate = vFactory.CreateObjectLabel(vLabelIndices[j], "LabelSet1", vLabelNames[i])
                wLabelList.append(vLabelCreate)
                progress_bar['value'] = scount/len(vSpotsDataAll)*100 #  % out of 100
                scount=scount+1
                master.update()
            vNewSpots.SetLabels(wLabelList)
            # elapsed = time.time() - start
            # print(str(elapsed) + ' = RegionTime')
            # start = time.time()

            # progress_bar['value'] = scount/len(vLabelNames)*100 #  % out of 100
            # master.update()

