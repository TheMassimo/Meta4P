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
import WindowStandardTaxonomic as wST
import WindowDynamicTaxonomic as wDT

#if skip go directly to funcional menu
import WindowFunctionalMenu as wFnMn

class TaxonomicMenuWindow(tk.Toplevel): #tk.Tk):
    def __init__(self, wn_root, wn_previous, previousDf):
        super().__init__()

        #change icon
        img = PhotoImage(file=resource_path(config.icon))
        self.iconphoto(False, img)

        #take the root window (in this case is the same that previous)
        self.wn_root = wn_root
        #take the previous windows
        self.wn_previous = wn_previous
        #take the old df
        self.df = previousDf;

        # configure the root window
        self.title('Taxonomic menu') #Meta Protein Annotation Aggregation

        #Standard taxonomic button (only if the previous isn't Proteins)
        if(MyUtility.workDict['mode'] != 'Proteins'):
            self.btn_standard = tk.Button(self, text='Unipept output', width=30, font=config.font_button, command=self.create_standard)
            self.btn_standard.grid(row=0, column=0, padx=5, pady=5)
        #mzTab button
        self.btn_dynamic = tk.Button(self, text='Other/custom taxonomic annotation', width=30, font=config.font_button, command=self.create_dynamic)
        self.btn_dynamic.grid(row=1, column=0, padx=5, pady=5)
        #Skip Step
        self.btn_skip_step = tk.Button(self, text='Skip step', font=config.font_button, width=30,command=self.skip_window)
        self.btn_skip_step.grid(row=2, column=0, padx=5, pady=30)

        #empty label
        self.lbl_empty = tk.Label(self, text='',width=30, font=config.font_subtitle)  
        self.lbl_empty.grid(row=3, column=0, padx=6, pady=6)
        #Previous Step
        self.btn_previous_step = tk.Button(self, text='← Previous step', font=config.font_button, width=20, command=self.previous_window)
        self.btn_previous_step.grid(row=4, column=0, padx=5, pady=(5,10))
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

    def create_standard(self):
        #change input type value
        MyUtility.workDict["taxonomic_mode"] = 'standard'

        #hide this window
        self.withdraw()
        #crete new window
        self.WindowStandardTaxonomic = wST.StandardTaxonomicWindow(self.wn_root, self, self.df)

    def create_dynamic(self):
        #change input type value
        MyUtility.workDict["taxonomic_mode"] = 'dynamic'

        #hide this window
        self.withdraw()
        #crete new window
        self.WindowDynamicTaxonomic = wDT.DynamicTaxonomicWindow(self.wn_root, self, self.df)

    def previous_window(self):
        #hide this window
        #self.withdraw()
        #Destroy this window
        self.destroy()

        #show last window
        self.wn_previous.deiconify()
        self.wn_previous.lift()

    def skip_window(self):
        #Edit the previous dict
        MyUtility.workDict["taxonomic"] = False
        MyUtility.workDict["taxonomic_mode"] = 'standard'

        #hide this window
        self.withdraw()
        #create new window
        self.windowFunctionalMenu = wFnMn.FunctionalMenuWindow(self.wn_root, self, self.df)