# Export Filament
# By Sarun Gulyanon 28 July 2018
#
# <CustomTools>
#  <Menu>
#    <Item name="Export Filament as SWC" icon="Python">
#      <Command>PythonXT::ExportSWC(#i)</Command>
#    </Item>
#  </Menu>
# </CustomTools>

import ImarisLib
import Tkinter
import tkFileDialog
import numpy as np
import time

def ExportSWC(aImarisId):
    # Create an ImarisLib object
    vImarisLib = ImarisLib.ImarisLib()
    # Get an imaris object with id aImarisId
    vImaris = vImarisLib.GetApplication(aImarisId)
    # Check if the object is valid
    if vImaris is None:
        print 'Could not connect to Imaris!'
        time.sleep(2)
        return
    
    vFactory = vImaris.GetFactory()
    vFilaments = vFactory.ToFilaments(vImaris.GetSurpassSelection())
    
    if vFilaments is None:
        print('Pick a filament first')
        time.sleep(2)
        return
    
    # get pixel scale in XYZ resolution (pixel/um)
    V = vImaris.GetDataSet()
    pixel_scale = np.array([V.GetSizeX() / (V.GetExtendMaxX() - V.GetExtendMinX()), \
                            V.GetSizeY() / (V.GetExtendMaxY() - V.GetExtendMinY()), \
                            V.GetSizeZ() / (V.GetExtendMaxZ() - V.GetExtendMinZ())])
    pixel_offset = np.array([V.GetExtendMinX(), V.GetExtendMinY(), V.GetExtendMinZ()])
    # ad-hoc fix Z-flip when |maxZ| < |minZ|
    if abs(V.GetExtendMinZ()) > abs(V.GetExtendMaxZ()):
        pixel_offset = np.array([V.GetExtendMinX(), V.GetExtendMinY(), V.GetExtendMaxZ()])
        pixel_scale[2] = -pixel_scale[2]
    
    # get filename
    root = Tkinter.Tk()
    root.withdraw()
    savename = tkFileDialog.asksaveasfilename(defaultextension=".swc")
    root.destroy()
    if not savename: # asksaveasfilename return '' if dialog closed with "cancel".
        print('No files selected')
        time.sleep(2)
        return
    print(savename)
    
    # go through Filaments and convert to SWC format
    head = 0;
    swcs = np.zeros((0,7))
    
    vCount = vFilaments.GetNumberOfFilaments()
    for vFilamentIndex in range(vCount):
        vFilamentsXYZ = vFilaments.GetPositionsXYZ(vFilamentIndex)
        vFilamentsEdges = vFilaments.GetEdges(vFilamentIndex)
        vFilamentsRadius = vFilaments.GetRadii(vFilamentIndex)
        vFilamentsTypes = vFilaments.GetTypes(vFilamentIndex)
        #vFilamentsTime = vFilaments.GetTimeIndex(vFilamentIndex)
        
        N = len(vFilamentsXYZ)
        G = np.zeros((N,N),np.bool)
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
            pos = vFilamentsXYZ[cur] - pixel_offset
            swc[head,2:5] = pos*pixel_scale
            for idx in np.where(G[cur])[0]:
                if not visited[idx]:
                    visited[idx] = True
                    queue.append(idx)
                    prevs.append(head+1)
            head = head + 1
        swcs = np.concatenate((swcs,swc),axis=0)
    # write to file
    np.savetxt(savename, swcs, '%d %d %f %f %f %f %d')
    print('Export to ' + savename + ' completed')
