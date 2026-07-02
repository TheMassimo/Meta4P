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
import WindowStandardFunctional as wSF
import WindowDynamicFunctional as wDF

#if skip go directly to Summary Metrics Pre
import WindowSummaryMetricsPre as wSMpr

class FunctionalMenuWindow(tk.Toplevel): #tk.Tk):
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
        self.title('Functional menu') #Meta Protein Annotation Aggregation

        #Radio button
        if( (MyUtility.workDict['mode'] == 'Peptides') or (MyUtility.workDict['mode'] == 'PSMs') ):
            self.rdb_type_var = StringVar(value='protein')
            self.rdb_type_protein = tk.Radiobutton(self, text="Protein functional input", width=30, anchor="w", variable=self.rdb_type_var, value='protein')
            self.rdb_type_protein.grid(row=0, column=0, padx=5, pady=5, sticky='n', columnspan=2)#, sticky="W")
            self.rdb_type_protein.config( font = config.font_checkbox )
            self.rdb_type_peptide = tk.Radiobutton(self, text="Peptide functional input", width=30, anchor="w", variable=self.rdb_type_var, value='peptide')
            self.rdb_type_peptide.grid(row=1, column=0, padx=5, pady=5, sticky='n', columnspan=2)#, sticky="E")
            self.rdb_type_peptide.config( font = config.font_checkbox )

        self.var_chc_view_protein_description = IntVar(value=0)
        self.chc_view_protein_description = tk.Checkbutton(self, text='Use protein description information as functional annotation',
                                               wraplength=250, width=34, anchor="w", variable=self.var_chc_view_protein_description, onvalue=1, offvalue=0)
        self.chc_view_protein_description.grid(row=2, column=0, padx=5, pady=10, columnspan=2)
        self.chc_view_protein_description.config(font = config.font_checkbox )
    
        #mzTab button
        self.btn_dynamic = tk.Button(self, text='Add another functional annotation', width=34, font=config.font_button, command=self.create_dynamic)
        self.btn_dynamic.grid(row=4, column=0, padx=5, pady=5, columnspan=2)

        #empty label
        self.lbl_empty = tk.Label(self, text='',width=30, font=config.font_subtitle)  
        self.lbl_empty.grid(row=6, column=0, padx=6, pady=6, columnspan=2)
        #Previous Step
        self.btn_previous_step = tk.Button(self, text='← Previous step', font=config.font_button, width=20, command=self.previous_window)
        self.btn_previous_step.grid(row=7, column=0, padx=5, pady=(5,10))
        #Next Step
        self.btn_next_step = tk.Button(self, text='Next step →', font=config.font_button, width=20,  command=self.skip_window)
        self.btn_next_step.grid(row=7, column=1, padx=5, pady=(5,10))

        #put this window up
        self.lift()

        #when i close window
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.wn_root.destroy()

    def set_database_protein_description(self):
        MyUtility.workDict['functional_table1'] = []
        MyUtility.workDict['functional_to_display1'] = []
        if( hasattr(self, 'chc_view_protein_description') and (self.chc_view_protein_description.grid_info() != {}) ):
          if(self.var_chc_view_protein_description.get() == 1):
            MyUtility.workDict["functional"] = True
            if(MyUtility.workDict['mode'] == 'Proteins'):
              MyUtility.workDict['functional_table1'].append('Description')
              MyUtility.workDict['functional_to_display1'].append('Description')
            elif(MyUtility.workDict['mode'] == 'Peptides'):
              MyUtility.workDict['functional_table1'].append('Master Protein Descriptions')
              MyUtility.workDict['functional_to_display1'].append('Master Protein Descriptions')
          else:
            MyUtility.workDict["functional"] = False
        else:
          MyUtility.workDict["functional"] = False

    def create_standard(self):
        self.set_database_protein_description()

        #change input type value
        MyUtility.workDict["functional_mode"] = 'standard'
        if( hasattr(self, 'rdb_type_var') ):
            MyUtility.workDict["functional_match"] = self.rdb_type_var.get()
        else:
            MyUtility.workDict["functional_match"] = 'protein'

        #hide this window
        self.withdraw()
        #crete new window
        self.WindowStandardFunctional = wSF.StandardFunctionalWindow(self.wn_root, self, self.df)

    def create_dynamic(self):
        self.set_database_protein_description()

        #change input type value
        MyUtility.workDict["functional_mode"] = 'dynamic'
        if( hasattr(self, 'rdb_type_var') ):
            MyUtility.workDict["functional_match"] = self.rdb_type_var.get()
        else:
            MyUtility.workDict["functional_match"] = 'protein'

        #hide this window
        self.withdraw()
        #crete new window
        self.WindowDynamicFunctional = wDF.DynamicFunctionalWindow(self.wn_root, self, self.df)

    def previous_window(self):
        #hide this window
        #self.withdraw()
        #Destroy this window
        self.destroy()

        #show last window
        self.wn_previous.deiconify()
        self.wn_previous.lift()

    def skip_window(self):
        self.set_database_protein_description()

        #Edit the previous dict
        #MyUtility.workDict["functional"] = False
        MyUtility.workDict["functional_mode"] = 'standard'
        if( hasattr(self, 'rdb_type_var') ):
            MyUtility.workDict["functional_match"] = self.rdb_type_var.get()
        else:
            MyUtility.workDict["functional_match"] = 'protein'

        #hide this window
        self.withdraw()
        #create new window
        self.windowSummaryMetricsPre = wSMpr.SummaryMetricsPreWindow(self.wn_root, self, self.df)