# Export Filament
# By Sarun Gulyanon 28 July 2018
# May 2023 -- converted to Python 3.7 Matthew

    #<CustomTools>
        #<Menu>
                #<Item name="Export Filament in SWC format" icon="Python3">
                    #<Command>Python3XT::XT_MJG_Export_SWC1(%i)</Command>
                #</Item>
       #</Menu>
       #<SurpassTab>
           #<SurpassComponent name="bpFilaments">
               #<Item name="Export Filament in SWC format" icon="Python3">
                   #<Command>Python3XT::XT_MJG_Export_SWC1(%i)</Command>
               #</SurpassComponent>
           #</SurpassTab>
    #</CustomTools>


import time
import ImarisLib


# GUI imports - builtin
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import asksaveasfile

import io

aImarisId=0
def XT_MJG_Export_SWC1(aImarisId):
    # Create an ImarisLib object
    vImarisLib = ImarisLib.ImarisLib()
    # Get an imaris object with id aImarisId
    vImaris = vImarisLib.GetApplication(aImarisId)
    # Check if the object is valid
    if vImaris is None:
        print ('Could not connect to Imaris!')
        time.sleep(2)
    
    vFactory = vImaris.GetFactory()
    vFilaments = vFactory.ToFilaments(vImaris.GetSurpassSelection())
    
    if vFilaments is None:
        print('Pick a filament first')
        time.sleep(2)
    
    # get pixel scale in XYZ resolution (pixel/um)
    V = vImaris.GetDataSet()
    pixel_scale = np.array([V.GetSizeX() / (V.GetExtendMaxX() - V.GetExtendMinX()), \
                            V.GetSizeY() / (V.GetExtendMaxY() - V.GetExtendMinY()), \
                            V.GetSizeZ() / (V.GetExtendMaxZ() - V.GetExtendMinZ())])
    
    # # get filename
    root = Tk()
    root.geometry('200x150')
    files = [('SWC files', '*.swc*')]
    vNewFileName = asksaveasfilename(filetypes = files, defaultextension ='.swc')
    root.destroy()
    
    # teststr=str(vNewFileName)
    # vStartIdx=teststr.find('name=')
    # vEndIdx=teststr.find('swc')
    
    # # vNewFileNameadj = teststr[:30]
    # vNewFileName[:-4] + '1' + vNewFileName[-4:]
    
    # newfile = io.FileIO(str(vNewFileName), mode='w')
    # newfile = io.TextIOWrapper(buffer='',name=str(vNewFileName))
    
    
    # go through Filaments and convert to SWC format
    head = 0
    swcs = np.zeros((0,7))
    
    vCount = vFilaments.GetNumberOfFilaments()
    for vFilamentIndex in range(vCount):
        vNext=vFilamentIndex+1
    
    
        head=0
        swcs = np.zeros((0,7))
    
        vFilamentsXYZ = vFilaments.GetPositionsXYZ(vFilamentIndex)
        vFilamentsEdges = vFilaments.GetEdges(vFilamentIndex)
        vFilamentsRadius = vFilaments.GetRadii(vFilamentIndex)
        vFilamentsTypes = vFilaments.GetTypes(vFilamentIndex)
        #vFilamentsTime = vFilaments.GetTimeIndex(vFilamentIndex)
    
        N = len(vFilamentsXYZ)
        # gG = np.zeros((N,N),dtype(bool))
        G = np.full([N,N], False)
        visited = np.zeros(N, np.bool)
        for p1, p2 in vFilamentsEdges:
            G[p1,p2] = True
            G[p2,p1] = True
    
        # traverse through the Filament using BFS
        swc = np.zeros((N,7))
        visited[0] = True
        queue = [0]
        prevs = [-1]
        while queue:
            cur = queue.pop()
            prev = prevs.pop()
            swc[head] = [head+1, vFilamentsTypes[cur], 0, 0, 0, vFilamentsRadius[cur], prev]
            swc[head,2:5] = vFilamentsXYZ[cur]*pixel_scale
            for idx in np.where(G[cur])[0]:
                if not visited[idx]:
                    visited[idx] = True
                    queue.append(idx)
                    prevs.append(head+1)
            head = head + 1
        swcs = np.concatenate((swcs,swc),axis=0)
    # write to file
        np.savetxt(vNewFileName, swcs, '%d %d %f %f %f %f %d')
        vNewFileName=vNewFileName[:-5] + str(vNext) + vNewFileName[-4:]
        if vFilamentIndex < vCount-1:
            file = io.FileIO(str(vNewFileName), mode='w')
