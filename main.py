#tkinter import
import tkinter as tk
from tkinter import *

#import start window
import WindowMenu as wMn

#create window menu
windowMenu = wMn.MenuWindow()
#change icon
windowMenu.iconbitmap("MetaPAnnA_icon.ico")
#pass main loop NOT REMOVE THIS!!!
windowMenu.mainloop()
