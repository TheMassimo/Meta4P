#import config module for environmental variability
import config
#import my utility class and function
import MyUtility
#import my multi threading function to upload and download file
from MyMultiThreading import *


#tkinter import
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo

#Import all windows class
import WindowInformationLevel as wIL

class InputTypeWindow(tk.Toplevel): #tk.Tk):
    def __init__(self, wn_previous):
        super().__init__()

        #change icon
        img = PhotoImage(file=resource_path(config.icon))
        self.iconphoto(False, img)

        #take the root window (in this case is the same that previous)
        self.wn_root = wn_previous
        #take the previous windows
        self.wn_previous = wn_previous

        # configure the root window
        self.title('Meta4P') #Meta Protein Annotation Aggregation
        self.geometry('355x270')

        #title label
        self.lbl_title = tk.Label(self, text='Input file type',width=30, font=config.font_title)  
        self.lbl_title.grid(row=0, column=0, padx=6, pady=6)
        #Proteome Discoverer export button
        self.btn_proteome = tk.Button(self, text='Proteome Discoverer export', width=26, font=config.font_button, command=self.do_proteome)
        self.btn_proteome.grid(row=1, column=0, padx=5, pady=5)
        #mzTab button
        self.btn_mzTab = tk.Button(self, text='mzTab', width=26, font=config.font_button, command=self.do_mzTab)
        self.btn_mzTab.grid(row=2, column=0, padx=5, pady=5)
        #other button
        self.btn_other = tk.Button(self, text='Other/custom', width=26, font=config.font_button, command=self.do_other)
        self.btn_other.grid(row=3, column=0, padx=5, pady=5)

        #empty label
        self.lbl_empty = tk.Label(self, text='',width=30, font=config.font_subtitle)  
        self.lbl_empty.grid(row=4, column=0, padx=6, pady=6)
        #Previous Step
        self.btn_previous_step = tk.Button(self, text='← Previous step', font=config.font_button, width=20, command=self.previous_window)
        self.btn_previous_step.grid(row=5, column=0, padx=5, pady=5)
        #Next Step
        #self.btn_next_step = tk.Button(self, text='Next step →', font=self.config.font_button, width=20,  command=self.next_window)
        #self.btn_next_step.grid(row=11, column=5, padx=5, pady=5)

        #put this window up
        self.lift()

        #when i close window
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.wn_root.destroy()

    def do_proteome(self):
        #change input type value
        MyUtility.workDict["input_type"] = 'proteome'
        self.create_informationLevel()

    def do_mzTab(self):
        #change input type value
        MyUtility.workDict["input_type"] = 'mzTab'
        self.create_informationLevel()

    def do_other(self):
        #change input type value
        MyUtility.workDict["input_type"] = 'other'
        self.create_informationLevel()

    def create_informationLevel(self):
        #hide menu window
        self.withdraw()
        #create new window
        self.windowIL = wIL.InformationLevelWindow(self.wn_root, self)

    def previous_window(self):
        #hide this window
        #self.withdraw()
        #Destroy this window
        self.destroy()

        #show last window
        self.wn_previous.deiconify()
        self.wn_previous.lift()


'''
#create new window or show it if alredy exists
if( hasattr(self, 'windowPr') ):
    self.windowPr.deiconify()
    #put this window up
    self.windowPr.lift()
else:
    self.windowPr = wPr.ProteinsWindow(self)
'''
    

"""
window.configure(bg='lightgray')

# move window center
winWidth = window.winfo_reqwidth()
winwHeight = window.winfo_reqheight()
posRight = int(window.winfo_screenwidth() / 2 - winWidth / 2)
posDown = int(window.winfo_screenheight() / 2 - winwHeight / 2)
window.geometry("+{}+{}".format(posRight, posDown))

window.mainloop()
"""


'''
#import os
import os

#get the current path
dir_path = os.path.dirname(os.path.realpath(__file__))
#add folder dir
dir_path = dir_path + '/temp'
# Check whether the specified path exists or not
isExist = os.path.exists(dir_path)
if not isExist:
  # Create a new directory because it does not exist 
  os.makedirs(dir_path)
  print("The new directory is created!")
'''