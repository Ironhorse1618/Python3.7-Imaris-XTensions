#Created on Fri Jan 16 17:08:59 2026 ,.,

#author: MatthewG


# Investigating the mechanism of invoking XT code from Imaris.

 

#<CustomTools>
# <Menu>
# <Item name="Python XT Test" icon="Python3">
# <Command>Python3XT::XTtest(%i)</Command>
# </Item>
# </Menu>
#</CustomTools>
import tkinter as tk
import ImarisLib

aImarisId = 0
def XTtest(aImarisId):
 
    
    root = tk.Tk()
    root.title("XT Test")
    label = tk.Label(root, text="This is a test XTension")
    label.pack(padx=20, pady=20)
    root.mainloop()