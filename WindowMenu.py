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
import WindowInputType as wIT
import WindowRenameColumns as wRC

class MenuWindow(tk.Tk): #tk.Toplevel):
    def __init__(self):
        super().__init__()

        #change icon
        img = PhotoImage(file=resource_path(config.icon))
        self.iconphoto(False, img)

        # configure the root window
        self.title('Meta4P') #Meta Protein Annotation Aggregation

        #New Analysis button
        self.btn_newAnalysis = tk.Button(self, text='Start a new analysis', width=26, font=config.font_button, command=self.create_inputType)
        self.btn_newAnalysis.grid(row=0, column=0, padx=30, pady=(30,10))
        #Rename Columns button
        self.btn_renameColumns = tk.Button(self, text='Rename/reorder columns of\n existing Meta4P outputs', width=26, font=config.font_button, command=self.create_renameColumns)
        self.btn_renameColumns.grid(row=1, column=0, padx=30, pady=(10,30))

        #put this window up
        self.lift()

        #when i close window
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def create_inputType(self):
        #hide menu window
        self.withdraw()
        #create new window
        self.windowIT = wIT.InputTypeWindow(self)

    def create_renameColumns(self):
        #hide menu window
        self.withdraw()
        #create new window
        self.windowRC = wRC.RenameColumnsWindow(self, self)

