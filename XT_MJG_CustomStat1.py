#Written by Matthew J. Gastinger
#2023
#
    # <CustomTools>
    #     <Menu>
    #         <Submenu name="Spots Functions">
    #             <Item name="Synaptic_Pairing_beta7" icon="Python3">
    #                 <Command>Python3XT::XT_MJG_CustomStat1(%i)</Command>
    #             </Item>
    #         </Submenu>
    #     </Menu>
    #     <SurpassTab>
    #         <SurpassComponent name="bpSpots">
    #             <Item name="Synaptic Pairing_beta7" icon="Python3">
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

import ImarisLib
import numpy as np


aImarisId=0
#def XT_MJG_CustomStat1(aImarisId):

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
main = Tk()
main.title("Statistic Selection")
main.geometry("550x85")
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

def CustomStat():
    global wCustomStat1a, wCustomStat1b, wCustomStat1Math
    wCustomStat1a.get()
    wCustomStat1Math.get()
    wCustomStat1b.get()
    main.destroy()

vStatisticsALL = vObject.GetStatistics()
vStatNamesALL = np.unique(vStatisticsALL.mNames).tolist()

wCustomStat1a = StringVar(main)
wCustomStat1a.set("Choose Variable1") # default value
wCustomStat1Math = StringVar(main)
wCustomStat1Math.set("Choose Math") # default value
wCustomStat1b = StringVar(main)
wCustomStat1b.set("Choose Variable2") # default value

tk.Label(main, text='Calculate Custom Statistic#1').grid(row=1, column=1,sticky=W)
w1 = OptionMenu(main, wCustomStat1a, *vStatNamesALL).grid(row=2, column=1)
w2 = OptionMenu(main, wCustomStat1Math, "+", "-", "*","/").grid(row=2, column=2)
w3 = OptionMenu(main, wCustomStat1b, *vStatNamesALL).grid(row=2, column=3)

qWhatOS = platform.system()
if qWhatOS == 'Darwin':
    Single=Button(main, text="CREATE",command=CustomStat )
else:
    Single=Button(main, text="CREATE", bg='blue', fg='white',command=CustomStat )
Single.grid(row=1, column=0)

main.mainloop()

##################################################################
vStat1SET = vObject.GetStatisticsByName(wCustomStat1a.get())
vStat2SET = vObject.GetStatisticsByName(wCustomStat1b.get())
vStat1Values = np.array(vStat1SET.mValues)
vStat1Ids = vStat1SET.mIds
vStat2Values = np.array(vStat2SET.mValues)
vStat2Ids = vStat2SET.mIds


vMath = str(wCustomStat1Math.get())

if vMath == '+':
    vStat1SET

elif vMath=='-':
elif vMath=='/':
elif vMath=='*':