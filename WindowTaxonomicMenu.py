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

        #Radio button
        if( (MyUtility.workDict['mode'] == 'Peptides') or (MyUtility.workDict['mode'] == 'PSMs') ):
            self.rdb_type_var = StringVar(value='peptide')
            self.rdb_type_protein = tk.Radiobutton(self, text="Protein taxonomic input", width=30, anchor="w", variable=self.rdb_type_var, value='protein', command=self.on_radio_button_change)
            self.rdb_type_protein.grid(row=0, column=0, padx=5, pady=5, sticky='n', columnspan=2)#, sticky="W")
            self.rdb_type_protein.config( font = config.font_checkbox )
            self.rdb_type_peptide = tk.Radiobutton(self, text="Peptide taxonomic input", width=30, anchor="w", variable=self.rdb_type_var, value='peptide', command=self.on_radio_button_change)
            self.rdb_type_peptide.grid(row=1, column=0, padx=5, pady=5, sticky='n', columnspan=2)#, sticky="E")
            self.rdb_type_peptide.config( font = config.font_checkbox )

        if(MyUtility.workDict["input_type"] == 'fragpipe'):
            self.var_chc_view_organism_lineage = IntVar(value=0)
            self.chc_view_organism_lineage = tk.Checkbutton(self, text='Use database organism and lineage information as taxonomic annotations',
                                                   wraplength=250, width=34, anchor="w", variable=self.var_chc_view_organism_lineage, onvalue=1, offvalue=0)
            self.chc_view_organism_lineage.grid(row=2, column=0, padx=5, pady=10, columnspan=2)
            self.chc_view_organism_lineage.config(font = config.font_checkbox )
    
        #Standard taxonomic button (only if the previous isn't Proteins)
        if(MyUtility.workDict['mode'] != 'Proteins'):
            self.btn_standard = tk.Button(self, text='Add Unipept annotation', width=30, font=config.font_button, command=self.create_standard)
            self.btn_standard.grid(row=3, column=0, padx=5, pady=5, columnspan=2)

        #mzTab button
        self.btn_dynamic = tk.Button(self, text='Add another taxonomic annotation', width=30, font=config.font_button, command=self.create_dynamic)
        self.btn_dynamic.grid(row=4, column=0, padx=5, pady=5, columnspan=2)
        #Skip Step
        #self.btn_skip_step = tk.Button(self, text='Next step →', font=config.font_button, width=30,command=self.skip_window)
        #self.btn_skip_step.grid(row=5, column=0, padx=5, pady=30)

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

    def on_radio_button_change(self):
        newValue = self.rdb_type_var.get()
        if(newValue == "peptide"):
            self.btn_standard.config(state="normal")
        else:
            self.btn_standard.config(state="disabled")

    def set_database_organism_and_lineage(self):
        MyUtility.workDict['taxonomic_table1'] = []
        if( hasattr(self, 'chc_view_organism_lineage') and (self.chc_view_organism_lineage.grid_info() != {}) ):
          if(self.var_chc_view_organism_lineage.get() == 1):
            MyUtility.workDict['taxonomic_table1'].append('Organism')
            MyUtility.workDict['taxonomic_table1'].append('Lineage')
            MyUtility.workDict["taxonomic"] = True
          else:
            MyUtility.workDict["taxonomic"] = False
        else:
          MyUtility.workDict["taxonomic"] = False
    
    def create_standard(self):
        self.set_database_organism_and_lineage()

        #change input type value
        MyUtility.workDict["taxonomic_mode"] = 'standard'
        if( hasattr(self, 'rdb_type_var') ):
            MyUtility.workDict["taxonomic_match"] = self.rdb_type_var.get()
        else:
            MyUtility.workDict["taxonomic_match"] = 'protein'

        #hide this window
        self.withdraw()
        #crete new window
        self.WindowStandardTaxonomic = wST.StandardTaxonomicWindow(self.wn_root, self, self.df)

    def create_dynamic(self):
        self.set_database_organism_and_lineage()

        #change input type value
        MyUtility.workDict["taxonomic_mode"] = 'dynamic'
        if( hasattr(self, 'rdb_type_var') ):
            MyUtility.workDict["taxonomic_match"] = self.rdb_type_var.get()
        else:
            MyUtility.workDict["taxonomic_match"] = 'protein'

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
        self.set_database_organism_and_lineage()

        #Edit the previous dict
        #MyUtility.workDict["taxonomic"] = False
        MyUtility.workDict["taxonomic_mode"] = 'standard'

        if( hasattr(self, 'rdb_type_var') ):
            MyUtility.workDict["taxonomic_match"] = self.rdb_type_var.get()
        else:
            MyUtility.workDict["taxonomic_match"] = 'protein'

        #hide this window
        self.withdraw()
        #create new window
        self.windowFunctionalMenu = wFnMn.FunctionalMenuWindow(self.wn_root, self, self.df)