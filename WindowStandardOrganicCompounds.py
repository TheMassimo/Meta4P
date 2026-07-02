#import config module for environmental variability
import config
#import my utility class and function
import MyUtility
#import my multi threading function to upload and download file
from MyMultiThreading import *
from collections import OrderedDict


#tkinter import
import tkinter as tk
import queue
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from tkinter.messagebox import showinfo
from tkinter.ttk import Separator, Style
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

#pandas import
import pandas as pd
#numpy import
import numpy as np
#random import
import random
#importo os
import os

# importing the threading module
from threading import Thread

#import loading window
import WindowLoading as wLd
#import next window
import WindowTaxonomicMenu as wTxMn

import requests


class StandardOrganicCompoundsWindow(tk.Toplevel): #tk.Tk):
  def __init__(self, wn_root, wn_previous):
    super().__init__()

    if not hasattr(self, "_gui_queue"):
        self._init_gui_queue()

    #change icon
    img = PhotoImage(file=resource_path(config.icon))
    self.iconphoto(False, img)

    #take the root window
    self.wn_root = wn_root
    #take the previous window
    self.wn_previous = wn_previous

    #preapre df
    self.df = pd.DataFrame()
    #check if file is load
    self.isFileLoad = False
    self.isFileLoad_MAGsdb = False
    self.isFileLoad_CNGBdb = False

    self.organismList = []
    self.lineageList = []
    self.ntr_database2_var_organism = ""
    self.ntr_database2_var_lineage = ""

    # configure the root window
    self.title(MyUtility.workDict["mode"])
    
    #for Entry widget
    self.vcmd = (self.register(self.onValidate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

    ### left area ###
    #Load/download frame
    self.frame_left = tk.Frame(self, borderwidth=2, relief='flat')
    self.frame_left.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
    #Load button
    self.btn_loadFile = tk.Button(self.frame_left, text='Upload input file', bg='yellow', font=config.font_button, width=24, command=self.upload_file)
    self.btn_loadFile.grid(row=0, column=0, padx=5, pady=5)
    #label template
    self.lbl_loadedFile = tk.Label(self.frame_left, text='No file',width=30,font=config.font_up_base)
    self.lbl_loadedFile.grid(row=1, column=0, padx=5, pady=5)

    if(MyUtility.workDict['input_type'] == 'fragpipe'):
      #label space
      self.lbl_space_1 = tk.Label(self.frame_left, text='',width=30,font=config.font_up_base)
      self.lbl_space_1.grid(row=2, column=0, padx=5, pady=50)
      #label template
      self.lbl_annotation_1 = tk.Label(self.frame_left, text='Database annotation',width=30,font=config.font_up_base)
      self.lbl_annotation_1.grid(row=3, column=0, padx=5, pady=5)
      #label warnings
      self.lbl_annotation_2 = tk.Label(self.frame_left, wraplength=180, text='To ensure that the input file is processed based on the database annotations, first upload the database annotation file and/or enable UniProt annotation retrieval and then (re)upload the input file',width=30,font=config.font_info)
      self.lbl_annotation_2.grid(row=4, column=0, padx=5, pady=5)
      #Load button MAGsdb
      self.btn_loadFile_MAGsdb = tk.Button(self.frame_left, text='Upload database annotation file', bg='yellow', font=config.font_button, width=28, command=self.upload_file_MAGsdb)
      self.btn_loadFile_MAGsdb.grid(row=5, column=0, padx=5, pady=5)
      #label template
      self.lbl_loadedFile_MAGsdb = tk.Label(self.frame_left, text='No file',width=30,font=config.font_up_base)
      self.lbl_loadedFile_MAGsdb.grid(row=6, column=0, padx=5, pady=5)
      #label warnings
      self.lbl_warnings_1 = tk.Label(self.frame_left, wraplength=180, text='Warning:\nlarge file uploads and data processing may take significant time and computing resources',width=30,font=config.font_info)
      self.lbl_warnings_1.grid(row=9, column=0, padx=5, pady=5)
      #label space
      self.lbl_space_2 = tk.Label(self.frame_left, text='',width=30,font=config.font_up_base)
      self.lbl_space_2.grid(row=10, column=0, padx=5, pady=10)
      #Fill with uniprot_annotation
      self.var_chc_uniprot_annotation = IntVar(value=0)
      self.chc_uniprot_annotation = tk.Checkbutton(self.frame_left, text='Retrieve UniProt taxonomic annotation',
                                             wraplength=400, width=30, anchor="w", variable=self.var_chc_uniprot_annotation, onvalue=1, offvalue=0)
      self.chc_uniprot_annotation.grid(row=11, column=0, padx=5, pady=5)
      self.chc_uniprot_annotation.config(font = config.font_checkbox )
      #label warnings
      self.lbl_warnings_2 = tk.Label(self.frame_left, wraplength=180, text='Warning: working internet connection needed',width=30,font=config.font_info)
      self.lbl_warnings_2.grid(row=12, column=0, padx=5, pady=5)
    
    ### centre area ###
    #title frame    
    self.frame_centre = tk.Frame(self, borderwidth=2, relief='flat')
    self.frame_centre.grid(row=0, column=1, padx=2, pady=2,sticky="nsew")
    #Fileter
    fileter_text = MyUtility.workDict["mode"]
    if(fileter_text != "PSMs"):
      fileter_text = fileter_text.lower()
    self.lbl_fileter = tk.Label(self.frame_centre,text='Filter '+fileter_text+' based on',width=20,font=config.font_title)  
    self.lbl_fileter.grid(row=0, column=0, columnspan=3, padx=6, pady=6, sticky='ew')
    #separator
    self.sp = MyUtility.Separator(self.frame_centre, orient='horizontal')
    self.sp.grid(row=1, column=0, columnspan=3, padx=6, sticky='ew')

    if(MyUtility.workDict['input_type'] == 'proteome'):
      if(MyUtility.workDict['mode'] == 'Proteins'):
        self.make_confidence(p_row=2, p_column=0, p_sticky='n')
        self.make_description(p_row=2, p_column=1, p_sticky='n')
        self.make_validValues(p_row=2, p_column=2, p_sticky='n')
        self.make_samples(p_row=3, p_column=0, p_sticky='n')
        self.make_makeAs(p_row=3, p_column=2, p_sticky='n')
      elif(MyUtility.workDict['mode'] == 'Peptides'):
        self.make_confidence(p_row=2, p_column=0, p_sticky='n')
        self.make_description(p_row=2, p_column=1, p_sticky='n')
        self.make_validValues(p_row=2, p_column=2, p_sticky='n')
        self.make_samples(p_row=3, p_column=0, p_sticky='n')
        self.make_quantInfo(p_row=3, p_column=1, p_sticky='n')
        self.make_makeAs(p_row=3, p_column=2, p_sticky='n') 
      elif(MyUtility.workDict['mode'] == 'PSMs'):
        self.make_confidence(p_row=2, p_column=0, p_sticky='n')
        self.make_description(p_row=2, p_column=1, p_sticky='n')
        self.make_makeAs(p_row=2, p_column=2, p_sticky='n')
    elif(MyUtility.workDict['input_type'] == 'fragpipe'):
      if(MyUtility.workDict['mode'] == 'Proteins'):
        self.make_quantitative(p_row=2, p_column=0, p_sticky='n')
        self.make_description(p_row=2, p_column=1, p_sticky='n')
        self.make_validValues(p_row=2, p_column=2, p_sticky='n')
        self.make_samples(p_row=3, p_column=0, p_sticky='n')
        self.make_databaseChoose1(p_row=3, p_column=1, p_sticky='n')
        self.make_databaseChoose2(p_row=3, p_column=2, p_sticky='n')
      elif(MyUtility.workDict['mode'] == 'Peptides'):
        self.make_quantitative(p_row=2, p_column=0, p_sticky='n')
        self.make_description(p_row=2, p_column=1, p_sticky='n')
        self.make_validValues(p_row=2, p_column=2, p_sticky='n')
        self.make_samples(p_row=3, p_column=0, p_sticky='n')
        self.make_databaseChoose1(p_row=3, p_column=1, p_sticky='n')
        self.make_databaseChoose2(p_row=3, p_column=2, p_sticky='n')
    else:
      if(MyUtility.workDict['mode'] == 'Proteins'):
        #create elements
        self.make_description(p_row=2, p_column=0, p_sticky='n')
        self.make_validValues(p_row=2, p_column=1, p_sticky='n')
      elif(MyUtility.workDict['mode'] == 'Peptides'):
        #create elements
        self.make_validValues(p_row=2, p_column=0, p_sticky='n')


    ### right area ###
    #Options frame
    self.frame_right = tk.Frame(self, borderwidth=2, relief='flat')
    self.frame_right.grid(row=0, column=2, padx=2, pady=2, sticky="nsew")

    #Frame checkbox
    self.frame_checkbox = tk.Frame(self.frame_right)
    self.frame_checkbox.pack(fill="x", side="top")

    #option label
    self.lbl_options = tk.Label(self.frame_checkbox,text='Options',width=32,font=config.font_title)  
    self.lbl_options.grid(row=0, column=0, padx=6, pady=6)

    #check the corret checkbox to insert according to input_type and mode
    if(MyUtility.workDict['input_type'] == 'proteome'):
      if(MyUtility.workDict['mode'] == 'Proteins'):
        self.make_fill_zero(p_row=1)
        self.make_master(p_row=2)
        self.make_normalized(p_row=3)
        self.make_re_normalized(p_row=4, p_text='Apply TSS normalization after filtering')
      elif(MyUtility.workDict['mode'] == 'Peptides'):
        self.make_fill_zero(p_row=1)
        self.make_ptrAccessions(p_row=2)
        self.make_normalized(p_row=3)
        self.make_re_normalized(p_row=4, p_text='Apply TSS normalization after filtering')
      elif(MyUtility.workDict['mode'] == 'PSMs'):
        self.make_fill_zero(p_row=1)
        self.make_ptrAccessions(p_row=2)
    elif(MyUtility.workDict['input_type'] == 'fragpipe'):
      if(MyUtility.workDict['mode'] == 'Proteins'):
        self.make_fill_empty(p_row=2)
        self.make_show_protein_id(p_row=3)
        self.make_re_normalized_choose(p_row=4)
      elif(MyUtility.workDict['mode'] == 'Peptides'):
        self.make_fill_empty(p_row=2)
        self.make_show_protein_id(p_row=3)
        self.make_show_mapped_proteins(p_row=4)
        self.make_re_normalized_choose(p_row=5)
    else:
      if(MyUtility.workDict['mode'] == 'Proteins'):
        self.make_fill_zero(p_row=1)
        self.make_re_normalized(p_row=2, p_text='Apply TSS normalization (after filtering)')
      elif(MyUtility.workDict['mode'] == 'Peptides'):
        self.make_fill_zero(p_row=1)
        self.make_re_normalized(p_row=2, p_text='Apply TSS normalization (after filtering)')
      elif(MyUtility.workDict['mode'] == 'PSMs'):
        self.make_fill_zero(p_row=1)



    #Frame download
    self.frame_download = tk.Frame(self.frame_right)
    self.frame_download.pack(fill="x", side="bottom")

    self.frame_download.grid_rowconfigure(0, weight=1)
    self.frame_download.grid_columnconfigure(0, weight=1)

    #Download button
    self.btn_download = tk.Button(self.frame_download, text='Download filtered table', bg='lime', font=config.font_button, width=20,command=self.download)
    self.btn_download.grid(row=0, column=0)


      
    ### down area ###
    self.frame_down = tk.Frame(self, borderwidth=2, relief='flat')
    self.frame_down.grid(row=1, column=0, columnspan=3, padx=2, pady=2, sticky="nsew")
    self.frame_down.columnconfigure(0, weight=1)
    self.frame_down.columnconfigure(1, weight=1)
    self.frame_down.columnconfigure(2, weight=1)
    #Previous Step
    self.btn_previous_step = tk.Button(self.frame_down, text='← Previous step', font=config.font_button, width=20, command=self.previous_window)
    self.btn_previous_step.grid(row=0, column=0, padx=20, pady=5, sticky="w")
    #Next Step
    self.btn_next_step = tk.Button(self.frame_down, text='Next step →', font=config.font_button, width=20, command=self.next_window)
    self.btn_next_step.grid(row=0, column=2, padx=20, pady=5, sticky="e")


    if((MyUtility.workDict['input_type'] != 'proteome') and (MyUtility.workDict['mode'] == 'PSMs')):
      #edit frame
      self.frame_centre.grid_remove()
      self.frame_right.grid(column=1)
      self.frame_down.grid(columnspan=2)

    #put this window up
    self.lift()

    #when I close window
    self.protocol("WM_DELETE_WINDOW", self.on_closing)

  ### Functions to create frame in window ###
  def make_confidence(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #Confidence frame
    self.frame_confidence = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_confidence.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)
    #Protein FDR label (Confidence)
    self.lbl_confidence = tk.Label(self.frame_confidence,text='Confidence',width=20, font=config.font_subtitle)  
    self.lbl_confidence.grid(row=0, column=0, padx=6, pady=6)
    #Protein FDR checkboxes (Confidence)
    self.var_chc_low = IntVar(value=1)
    self.var_chc_medium = IntVar(value=1)
    self.var_chc_high = IntVar(value=1)
    self.chc_low = tk.Checkbutton(self.frame_confidence, text='Low', width=20, anchor="w", variable=self.var_chc_low, onvalue=1, offvalue=0)
    self.chc_low.grid(row=1, column=0, padx=(50,5), pady=5)
    self.chc_low.select()
    self.chc_low.config( font = config.font_checkbox )
    self.chc_medium = tk.Checkbutton(self.frame_confidence, text='Medium', width=20, anchor="w", variable=self.var_chc_medium, onvalue=1, offvalue=0)
    self.chc_medium.grid(row=2, column=0, padx=(50,5), pady=5)
    self.chc_medium.select()
    self.chc_medium.config( font = config.font_checkbox )
    self.chc_high = tk.Checkbutton(self.frame_confidence, text='High', width=20, anchor="w", variable=self.var_chc_high, onvalue=1, offvalue=0)
    self.chc_high.grid(row=3, column=0, padx=(50,5), pady=5)
    self.chc_high.select()
    self.chc_high.config( font = config.font_checkbox )

  def make_quantInfo(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #Quan info frame
    self.frame_quanInfo = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_quanInfo.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)
    #Quan info label
    self.lbl_quanInfo = tk.Label(self.frame_quanInfo,text='Quan info', width=20, font=config.font_subtitle)  
    self.lbl_quanInfo.grid(row=0, column=0)
    #quantInfo scroll
    self.scl_check_quantInfo = MyUtility.VirtualCheckboxList(
                                                        self.frame_quanInfo, 
                                                        width=200,
                                                        height=270,
                                                        bg="grey", 
                                                        padx=1, 
                                                        pady=1,
                                                        select=True
                                                     )
    self.scl_check_quantInfo.grid(row=1,column=0, pady=6)

  def make_description(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #Description frame
    self.frame_description = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_description.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)
    #Description Label
    self.lbl_description = tk.Label(self.frame_description,text='Protein Description', width=22, font=config.font_subtitle)  
    self.lbl_description.grid(row=0, column=0, columnspan=2, padx=6, pady=6)
    #Radio button frame
    self.rbd_filter_frame = Frame(self.frame_description, width=20, height=20)
    self.rbd_filter_frame.grid(row=1, column=0, columnspan=2)
    #Radio button
    self.rdb_filter_var = StringVar(value='in')
    self.rdb_filter_in = tk.Radiobutton(self.rbd_filter_frame, text="Filter in", width=10, variable=self.rdb_filter_var, value='in')
    self.rdb_filter_in.grid(row=0, column=0, padx=(0,0), pady=0)#, sticky="W")
    self.rdb_filter_in.config( font = config.font_checkbox )
    self.rdb_filter_out = tk.Radiobutton(self.rbd_filter_frame, text="Filter out", width=10, variable=self.rdb_filter_var, value='out')
    self.rdb_filter_out.grid(row=0, column=1, padx=(0,0), pady=0)#, sticky="E")
    self.rdb_filter_out.config( font = config.font_checkbox )
    #Description Entry
    self.ntr_description = tk.Entry(self.frame_description, width=36)
    self.ntr_description.grid(row=2,column=0, padx=5, pady=5)
    #Description Add button
    self.btn_add = tk.Button(self.frame_description, text='Add', font=config.font_button, width=3, command=self.add_description_element)
    self.btn_add.grid(row=2, column=1, padx=5, pady=5)
    #Radio button frame
    self.rbd_condition_frame = Frame(self.frame_description, width=20, height=20)
    self.rbd_condition_frame.grid(row=3, column=0, columnspan=2)
    #Radio button
    self.rdb_condition_var = StringVar(value='and')
    self.rdb_condition_and = tk.Radiobutton(self.rbd_condition_frame, text="AND", width=10, variable=self.rdb_condition_var, value='and')
    self.rdb_condition_and.grid(row=0, column=0, padx=(0,0), pady=0)#, sticky="W")
    self.rdb_condition_and.config( font = config.font_checkbox )
    self.rdb_condition_or = tk.Radiobutton(self.rbd_condition_frame, text="OR", width=10, variable=self.rdb_condition_var, value='or')
    self.rdb_condition_or.grid(row=0, column=1, padx=(0,0), pady=0)#, sticky="E")
    self.rdb_condition_or.config( font = config.font_checkbox )
    #Create frame and scrollbar
    self.dsc_frame = Frame(self.frame_description)#, bg='red')
    self.dsc_frame.grid(row=5, column=0, rowspan=4, columnspan=2)
    #scrollbar
    self.dsc_scrollbar = Scrollbar(self.dsc_frame,  orient=VERTICAL)
    #Listbox
    #SINGLE, BROWSE, MULTIPLE, EXTENDED
    self.dsc_listbox = Listbox(self.dsc_frame, yscrollcommand=self.dsc_scrollbar.set, selectmode=EXTENDED) #background="Blue", fg="white", selectbackground="Red",highlightcolor="Red",
    self.dsc_listbox.grid(row=0, column=0)
    self.dsc_listbox.config(width=40, height=7)
    #configure scrollvar
    self.dsc_scrollbar.config(command=self.dsc_listbox.yview)
    self.dsc_scrollbar.grid(row=0, column=1, sticky="NS")
    #Description Remove button
    self.btn_remove = tk.Button(self.frame_description, text='Remove', font=config.font_button, width=23, command=self.remove_description_element)
    self.btn_remove.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

  def make_makeAs(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #MakedAs frame
    self.frame_marker = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_marker.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)
    #MakedAs label
    self.lbl_marker = tk.Label(self.frame_marker,text='Marker', width=20, font=config.font_subtitle)  
    self.lbl_marker.grid(row=0, column=0)
    #MakedAs scroll
    self.scl_check_marker = MyUtility.VirtualCheckboxList(
                                                    self.frame_marker, 
                                                    width=200,
                                                    height=270,
                                                    bg="grey", 
                                                    padx=1, 
                                                    pady=1,
                                                    select=True
                                                    )
    self.scl_check_marker.grid(row=1,column=0, pady=6)

  def make_validValues(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #Valid values frame
    self.frame_validValues = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_validValues.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)
    #Valid values (Abundance label)
    self.lbl_abundance = tk.Label(self.frame_validValues,text='Valid values threshold', width=20, font=config.font_subtitle)  
    self.lbl_abundance.grid(row=0, column=0, padx=6, pady=6)
    #Abundance option
    options_list = ["Absolute", "Percentage"]
    self.opt_abundance_var = StringVar(value='Absolute')
    self.opt_abundance = tk.OptionMenu(self.frame_validValues, self.opt_abundance_var, *options_list)
    self.opt_abundance.configure(width=12)
    self.opt_abundance.grid(row=1, column=0)
    self.opt_abundance.config( font = config.font_checkbox )
    #Abundance Entry
    self.ntr_abundance = tk.Entry(self.frame_validValues, width=20, validate="key", validatecommand=self.vcmd)
    self.ntr_abundance.insert(0, "0")
    self.ntr_abundance.grid(row=2, column=0, padx=5, pady=5)
    #Abundance info
    self.lbl_abundanceTot = tk.Label(self.frame_validValues,text='', width=20, font=config.font_base)
    self.lbl_abundanceTot.grid(row=3, column=0, padx=5, pady=(0,5))

  def make_databaseChoose1(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #databaseChoose frame
    self.frame_database1 = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_database1.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)
    #databaseChoose label
    self.lbl_database1 = tk.Label(self.frame_database1,text="", width=20, font=config.font_subtitle)  
    self.lbl_database1.grid(row=0, column=0)
    #Radio button frame
    self.rbd_database1_frame = Frame(self.frame_database1, width=20, height=20)
    self.rbd_database1_frame.grid(row=1, column=0, columnspan=2)
    #Radio button
    self.rdb_database1_var = StringVar(value='filter')
    self.rdb_database1_filter = tk.Radiobutton(self.rbd_database1_frame, text="Filter", width=10, variable=self.rdb_database1_var, value='filter', command=self.update_visibility_scl_database1)
    self.rdb_database1_filter.grid(row=0, column=0)
    self.rdb_database1_filter.config( font = config.font_checkbox )
    self.rdb_database1_view = tk.Radiobutton(self.rbd_database1_frame, text="View", width=10, variable=self.rdb_database1_var, value='view', command=self.update_visibility_scl_database1)
    self.rdb_database1_view.grid(row=0, column=1)
    self.rdb_database1_view.config( font = config.font_checkbox )

    #VirtualCheckboxList database
    self.scl_database1_filter = MyUtility.VirtualCheckboxList(
                                                self.frame_database1, 
                                                select=True, 
                                                width=200,
                                                height=244,
                                                bg="grey", 
                                                padx=1, 
                                                pady=1, 
                                                callback_on_change_set_checks=self.on_change_set_checks_database_filter
                                                )
    self.scl_database1_filter.grid(row=2,column=0, pady=6)

    #VirtualCheckboxList database view
    self.scl_database1_view = MyUtility.VirtualCheckboxList(
                                                self.frame_database1, 
                                                select=True, 
                                                width=200,
                                                height=244,
                                                bg="grey", 
                                                padx=1, 
                                                pady=1, 
                                                callback_on_change_set_checks=self.on_change_set_checks_database_view
                                                )
    self.scl_database1_view.grid(row=2,column=0, pady=6)

    self.rdb_database1_filter.invoke()

  def make_databaseChoose2(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #databaseChoose frame
    self.frame_database2 = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_database2.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)
    #databaseChoose label
    self.lbl_database2 = tk.Label(self.frame_database2,text="", width=20, font=config.font_subtitle)  
    self.lbl_database2.grid(row=0, column=0)
    #Radio button frame
    self.rbd_database2_frame = Frame(self.frame_database2, width=20, height=20)
    self.rbd_database2_frame.grid(row=1, column=0, columnspan=2)
    #Radio button
    self.rdb_database2_var = StringVar(value='organism')
    self.rdb_database2_organism = tk.Radiobutton(self.rbd_database2_frame, text="Organism", width=10, variable=self.rdb_database2_var, value='organism', command=self.update_visibility_scl_database2)
    self.rdb_database2_organism.grid(row=0, column=0)
    self.rdb_database2_organism.config( font = config.font_checkbox )
    self.rdb_database2_lineage = tk.Radiobutton(self.rbd_database2_frame, text="Lineage", width=10, variable=self.rdb_database2_var, value='lineage', command=self.update_visibility_scl_database2)
    self.rdb_database2_lineage.grid(row=0, column=1)
    self.rdb_database2_lineage.config( font = config.font_checkbox )

    #VirtualCheckboxList organism
    self.scl_database2_organism = MyUtility.VirtualCheckboxList(
                                                            self.frame_database2, 
                                                            search=True, 
                                                            select=True, 
                                                            width=200,
                                                            height=176,
                                                            bg="grey", 
                                                            padx=1, 
                                                            pady=1
                                                         )
    self.scl_database2_organism.grid(row=2,column=0, pady=6)

    #VirtualCheckboxList lineage
    self.scl_database2_lineage = MyUtility.VirtualCheckboxList(
                                                            self.frame_database2, 
                                                            search=True, 
                                                            select=True, 
                                                            width=200,
                                                            height=176,
                                                            bg="grey", 
                                                            padx=1, 
                                                            pady=1
                                                         )
    self.scl_database2_lineage.grid(row=2,column=0, pady=6)

    self.lbl_database2['text'] = "Organism / Lineage"
    self.scl_database2_lineage.grid_remove()

  ### Functions to create frame in window ###
  def make_quantitative(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #Valid values frame
    self.frame_quantitative = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_quantitative.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)
    #Valid values (Abundance label)
    self.lbl_quantitative = tk.Label(self.frame_quantitative,text='Quantitative values', width=20, font=config.font_subtitle)  
    self.lbl_quantitative.grid(row=0, column=0)
    #option to type_file
    self.idx_opt_quantitative = 0
    self.quantitative = [("")]
    self.opt_quantitative_var = StringVar(value="")
    self.opt_quantitative = tk.OptionMenu(self.frame_quantitative, self.opt_quantitative_var, *self.quantitative, command=self.on_change_opt_quantitative)
    self.opt_quantitative.configure(width=30)
    self.opt_quantitative.grid(row=1, column=0)
    self.opt_quantitative.config( font = config.font_checkbox )

  ### Functions to create frame in window ###
  def make_samples(self, p_row=0, p_column=0, p_rowspan=10, p_columnspan=1, p_sticky='nsew'):
    #Valid values frame
    self.frame_samples = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_samples.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)
    #abundance
    self.lbl_samples = tk.Label(self.frame_samples,text='Sample selection', width=20, font=config.font_subtitle)  
    self.lbl_samples.grid(row=2, column=0)
    #abundance scroll
    self.scl_samples = MyUtility.VirtualCheckboxList(
                                                self.frame_samples, 
                                                search=True, 
                                                select=True, 
                                                width=200,
                                                height=200,
                                                bg="grey", 
                                                padx=1, 
                                                pady=1,
                                                callback_on_change_set_checks=self.on_change_set_checks_samples
                                                )
    self.scl_samples.grid(row=3,column=0, pady=6)

  ### Functions to create Options in window ###
  def delete_all_zeros(self, p_row=0, p_column=0):
    #Fill with 0 in abundances
    self.var_chc_delete_all_zeros = IntVar(value=0)
    self.chc_delete_all_zeros = tk.Checkbutton(self.frame_checkbox, text='Delete rows with all zeros', width=32, anchor="w", variable=self.var_chc_delete_all_zeros, onvalue=1, offvalue=0)
    self.chc_delete_all_zeros.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_delete_all_zeros.config( font = config.font_checkbox )

  def make_fill_zero(self, p_row=0, p_column=0):
    #Fill with 0 in abundances
    self.var_chc_fill_zero = IntVar(value=0)
    self.chc_fill_zero = tk.Checkbutton(self.frame_checkbox, text='Replace missing values with 0', width=32, anchor="w", variable=self.var_chc_fill_zero, onvalue=1, offvalue=0)
    self.chc_fill_zero.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_fill_zero.config( font = config.font_checkbox )

  def make_master(self, p_row=0, p_column=0):
    #Master checkbox
    self.var_chc_master = IntVar(value=0)
    self.chc_master = tk.Checkbutton(self.frame_checkbox, text='Master proteins only', width=32, anchor="w", variable=self.var_chc_master, onvalue=1, offvalue=0)
    self.chc_master.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_master.config( font = config.font_checkbox )

  def make_ptrAccessions(self, p_row=0, p_column=0):
    #Protein Accessions checkbox
    self.var_chc_ptrAccessions = IntVar(value=0)
    self.chc_ptrAccessions = tk.Checkbutton(self.frame_checkbox, text='Show Protein Accessions', width=32, anchor="w", variable=self.var_chc_ptrAccessions, onvalue=1, offvalue=0)
    self.chc_ptrAccessions.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_ptrAccessions.config( font = config.font_checkbox )

  def make_normalized(self, p_row=0, p_column=0):
    #Normalized checkbox
    self.var_chc_normalized = IntVar(value=0)
    self.chc_normalized = tk.Checkbutton(self.frame_checkbox, text='Select normalized abundances', width=32, anchor="w", variable=self.var_chc_normalized, onvalue=1, offvalue=0, command=self.normalized_control )
    self.chc_normalized.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_normalized.config( font = config.font_checkbox )

  def make_re_normalized(self, p_row=0, p_column=0, p_text='Re Normalized'):
    #Re-Normalized checkbox
    self.var_chc_re_normalized = IntVar(value=0)
    self.chc_re_normalized = tk.Checkbutton(self.frame_checkbox, text=p_text, width=32, anchor="w", variable=self.var_chc_re_normalized, onvalue=1, offvalue=0, command=self.normalized_control )
    self.chc_re_normalized.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_re_normalized.config( font = config.font_checkbox )

  def make_fill_empty(self, p_row=0, p_column=0):
    #Fill with empty in abundances
    self.var_chc_fill_empty = IntVar(value=0)
    self.chc_fill_empty = tk.Checkbutton(self.frame_checkbox, text='Replace zeros with empty cells', width=32, anchor="w", variable=self.var_chc_fill_empty, onvalue=1, offvalue=0)
    self.chc_fill_empty.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_fill_empty.config( font = config.font_checkbox )

  def make_show_protein_id(self, p_row=0, p_column=0):
    #Fill with empty in abundances
    self.var_chc_fill_show_protein_id = IntVar(value=0)
    self.chc_fill_show_protein_id = tk.Checkbutton(self.frame_checkbox, text='Show Protein ID', width=32, anchor="w", variable=self.var_chc_fill_show_protein_id, onvalue=1, offvalue=0)
    self.chc_fill_show_protein_id.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_fill_show_protein_id.config( font = config.font_checkbox )

  def make_show_organism(self, p_row=0, p_column=0):
    #Fill with empty in abundances
    self.var_chc_fill_show_organism = IntVar(value=0)
    self.chc_fill_show_organism = tk.Checkbutton(self.frame_checkbox, text='Show Organism', width=32, anchor="w", variable=self.var_chc_fill_show_organism, onvalue=1, offvalue=0)
    self.chc_fill_show_organism.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_fill_show_organism.config( font = config.font_checkbox )

  def make_show_mapped_proteins(self, p_row=0, p_column=0):
    #Fill with empty in abundances
    self.var_chc_fill_show_mapped_proteins = IntVar(value=0)
    self.chc_fill_show_mapped_proteins = tk.Checkbutton(self.frame_checkbox, text='Show Mapped Proteins', width=32, anchor="w", variable=self.var_chc_fill_show_mapped_proteins, onvalue=1, offvalue=0)
    self.chc_fill_show_mapped_proteins.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_fill_show_mapped_proteins.config( font = config.font_checkbox )

  def make_re_normalized_choose(self, p_row=0, p_column=0):
    #Frame re_normalized_choose
    self.frame_re_normalized_choose = tk.Frame(self.frame_checkbox, borderwidth=2, relief='flat')
    self.frame_re_normalized_choose.grid(row=p_row, column=p_column)

    #Re-Normalized-choose checkbox
    self.var_chc_re_normalized_choose = IntVar(value=0)
    self.chc_re_normalized_choose = tk.Checkbutton(self.frame_re_normalized_choose, text='Apply TSS normalization', width=20, anchor="w", variable=self.var_chc_re_normalized_choose, onvalue=1, offvalue=0, command=self.normalized_choose_control )
    self.chc_re_normalized_choose.grid(row=0, column=0, padx=5, pady=5)
    self.chc_re_normalized_choose.config( font = config.font_checkbox )

    #option to type_file
    self.idx_opt_re_normalized_choose = 0
    self.opt_re_normalized_choose_var = StringVar(value=config.re_normalize[0])
    self.opt_re_normalized_choose = tk.OptionMenu(self.frame_re_normalized_choose, self.opt_re_normalized_choose_var, *config.re_normalize, command=self.on_change_opt_re_normalized_choose)
    self.opt_re_normalized_choose.configure(width=50)
    self.opt_re_normalized_choose.grid(row=1, column=0)
    self.opt_re_normalized_choose.config( font = config.font_checkbox )
    self.opt_re_normalized_choose.configure(state='disabled')



  def update_visibility_scl_database1(self):
    mode = self.rdb_database1_var.get()
    if mode == "filter":
      self.lbl_database1['text'] = "Database"
      self.scl_database1_filter.grid()
      self.scl_database1_view.grid_remove()
    else:  # "filter"
      self.lbl_database1['text'] = "Database"
      self.scl_database1_view.grid()
      self.scl_database1_filter.grid_remove()

  def update_visibility_scl_database2(self):
    mode = self.rdb_database2_var.get()
    if mode == "organism":
      self.lbl_database2['text'] = "Organism / Lineage"
      self.scl_database2_organism.grid()
      self.scl_database2_lineage.grid_remove()
    else:  # "lineage"
      self.lbl_database2['text'] = "Organism / Lineage"
      self.scl_database2_lineage.grid()
      self.scl_database2_organism.grid_remove()

  def update_optionmenu(self, widget_optionmenu, var, new_list, default_value=None, preserve_if_possible=True):
    menu = widget_optionmenu["menu"]
    menu.delete(0, "end")  # empty menu

    # choose the value after update
    curret_value = var.get()
    if preserve_if_possible and curret_value in new_list:
        new_value = curret_value
    elif default_value in new_list:
        new_value = default_value
    elif new_list is not None:
        new_value = new_list[0]
    else:
        new_value = ""  # null value

    # rebuild menu
    for item in new_list:
        menu.add_command(label=item, command=lambda v=item: var.set(v))

    var.set(new_value)

  def on_change_set_checks_samples(self):
    samples_list = self.scl_samples.selectedItems()
    num_samples_selected = len(samples_list)
    
    self.lbl_abundanceTot["text"] = "(# of samples: " + str(num_samples_selected) + " )"
     
  def on_change_set_checks_database_filter(self):
    database_list = self.scl_database1_filter.selectedItems()

    self.scl_database1_view.grid()
    self.scl_database1_view.insertItems(database_list)
    self.scl_database1_view.scrollToTop()

    self.scl_database2_organism.grid()
    self.organismList = MyUtility.create_unique_list(self.df[self.df["Database"].isin(database_list)], "Organism")
    self.scl_database2_organism.insertItems(self.organismList)
    self.scl_database2_organism.scrollToTop()

    self.scl_database2_lineage.grid()
    self.lineageList = MyUtility.create_unique_list(self.df[self.df["Database"].isin(database_list)], "Lineage")
    self.scl_database2_lineage.insertItems(self.lineageList)
    self.scl_database2_lineage.scrollToTop()

    self.ntr_database2_var_organism = ""
    self.ntr_database2_var_lineage = ""

    self.rdb_database1_filter.invoke()
    self.rdb_database2_organism.invoke()

  def on_change_set_checks_database_view(self):
    database_list = self.scl_database1_view.selectedItems()

    self.organismListViewed = MyUtility.create_unique_list(self.df[self.df["Database"].isin(database_list)], "Organism")
    self.scl_database2_organism.changeItemsViewed(self.organismListViewed)

    self.lineageListViewed = MyUtility.create_unique_list(self.df[self.df["Database"].isin(database_list)], "Lineage")
    self.scl_database2_lineage.changeItemsViewed(self.lineageListViewed)

  def on_change_opt_re_normalized_choose(self, selected_value):
    self.idx_opt_re_normalized = config.re_normalize.index(selected_value)

  def on_change_opt_quantitative(self, selected_value):
    self.idx_opt_quantitative = self.quantitative.index(selected_value)
    MyUtility.workDict["quantitative"] = self.opt_quantitative_var.get()

  #function called when user try to close window
  def on_closing(self):
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
      self.wn_root.destroy()

  #validate for some entry
  def onValidate(self, d, i, P, s, S, v, V, W):
    '''
    self.text.delete("1.0", "end")
    self.text.insert("end","OnValidate:\n")
    self.text.insert("end","d='%s'\n" % d)
    self.text.insert("end","i='%s'\n" % i)
    self.text.insert("end","P='%s'\n" % P)
    self.text.insert("end","s='%s'\n" % s)
    self.text.insert("end","S='%s'\n" % S)
    self.text.insert("end","v='%s'\n" % v)
    self.text.insert("end","V='%s'\n" % V)
    self.text.insert("end","W='%s'\n" % W)
    # Disallow anything but lowercase letters
    if S == S.lower():
        return True
    else:
        self.bell()
        return False
    '''
    return S.isdigit()  

  #control for nomalize variable
  def normalized_control(self):
    if( hasattr(self, 'var_chc_normalized') ):
      if(self.var_chc_normalized.get() == 1):
        self.var_chc_re_normalized.set(0)

  #control for nomalize variable
  def normalized_choose_control(self):
    if(self.var_chc_re_normalized_choose.get() == 1):
      self.opt_re_normalized_choose.configure(state='normal')
    else:
      self.opt_re_normalized_choose.configure(state='disabled')

  def monitor_upload(self, thread):
    if thread.is_alive():
      # check the thread every 100ms
      self.after(100, lambda: self.monitor_upload(thread))
    else:
      #delete load window
      self.winLoad.destroy()
      #put window in front
      self.lift()
      if(thread.fileOpen):
        if( not hasattr(thread, 'badFile') or (thread.badFile != True)):
          #self.winLoad = wLd.LoadingWindow("Init Entries...")

          #take the df
          self.df = thread.df
          #read it to create some button in the window and mark if the file is load
          self.isFileLoad = self.manage_the_upload()
    
          #self.winLoad.destroy()
        else:
          tk.messagebox.showerror(parent=self, title="Error", message=MyUtility.workDict["mode"]+" information not present")
      else:
        tk.messagebox.showerror(parent=self, title="Error", message="File not uploaded\nIt is probably in use by another program")

  def monitor_upload_MAGsdb(self, thread):
    if thread.is_alive():
      # check the thread every 100ms
      self.after(100, lambda: self.monitor_upload_MAGsdb(thread))
    else:
      #delete load window
      self.winLoad.destroy()
      #put window in front
      self.lift()
      if(thread.fileOpen):
        if( not hasattr(thread, 'badFile') or (thread.badFile != True)):
          self.winLoad = wLd.LoadingWindow("Init MAGsdb...")

          #take the df
          self.df_MAGsdb = thread.df
          #read it to create some button in the window and mark if the file is load
          self.isFileLoad_MAGsdb = self.manage_the_upload_MAGsdb()

          self.update()

          if(self.isFileLoad_MAGsdb):
            try:
              self.df_MAGsdb.loc[""]
            except KeyError:
              test = None

          self.update()
    
          self.winLoad.destroy()

        else:
          tk.messagebox.showerror(parent=self, title="Error", message=MyUtility.workDict["mode"]+" information not present")
      else:
        tk.messagebox.showerror(parent=self, title="Error", message="File not uploaded\nIt is probably in use by another program")

  def monitor_upload_CNGBdb(self, thread):
    if thread.is_alive():
      # check the thread every 100ms
      self.after(100, lambda: self.monitor_upload_CNGBdb(thread))
    else:
      #delete load window
      self.winLoad.destroy()
      #put window in front
      self.lift()
      if(thread.fileOpen):
        if( not hasattr(thread, 'badFile') or (thread.badFile != True)):
          self.winLoad = wLd.LoadingWindow("Init CNGBdb...")

          #take the df
          self.df_CNGBdb = thread.df
          #read it to create some button in the window and mark if the file is load
          self.isFileLoad_CNGBdb = self.manage_the_upload_CNGBdb()

          self.update()

          if(self.isFileLoad_CNGBdb):
            try:
              self.df_CNGBdb.loc[""]
            except KeyError:
              test = None

          self.update()
    
          self.winLoad.destroy()

        else:
          tk.messagebox.showerror(parent=self, title="Error", message=MyUtility.workDict["mode"]+" information not present")
      else:
        tk.messagebox.showerror(parent=self, title="Error", message="File not uploaded\nIt is probably in use by another program")
        
  def monitor_download(self, thread):
    if thread.is_alive():
      #check the thread every 100ms
      self.after(100, lambda: self.monitor_download(thread))
    else:
      #delete load window
      self.winLoad.destroy()
      #put window in front
      self.lift()
      if(not thread.fileSaved):
        tk.messagebox.showerror(parent=self, title="Error", message="File not saved\nIt is probably in use by another program")

  def manage_the_upload_MAGsdb(self):
    valid_columns = ['catalog','Lineage','Organism']
    check = all(item in self.df_MAGsdb.columns for item in valid_columns)
    if(not check):
      self.isFileLoad_MAGsdb = False
      self.lbl_loadedFile_MAGsdb['text'] = "No file"
      tk.messagebox.showerror(parent=self, title="Error", message="Incompatible columns in uploaded file")
      return False

    return True

  def manage_the_upload_CNGBdb(self):
    valid_columns = ['Catalog','KO annotation','Organism']
    check = all(item in self.df_CNGBdb.columns for item in valid_columns)
    if(not check):
      self.isFileLoad_CNGBdb = False
      self.lbl_loadedFile_CNGBdb['text'] = "No file"
      tk.messagebox.showerror(parent=self, title="Error", message="Incompatible columns in uploaded file")
      return False

    return True

  def manage_the_upload(self):
    #controlli per selezionare le colonne indispensabili per il coretto funzionamento delle diverse tipologie di file
    if(MyUtility.workDict['input_type'] == 'proteome'):
      #find all abundances columns
      abundances_columns = list(self.df.filter(regex = 'Abundance:')) + list(self.df.filter(regex = '(Normalized)'))
      self.samples_code = list(self.df.filter(regex = 'Abundance:'))
      self.samples_code = [s.replace("Abundance: ", "").replace(": Sample", "").strip() for s in self.samples_code]
      self.samples_description = self.samples_code

      if(MyUtility.workDict['mode'] == 'Proteins'):
        #create a valid list of columns and add abundaces columns
        valid_columns = ['Accession'] + abundances_columns

        #add extra optional column not used for the valid filter
        extra_valid_columns = valid_columns.copy()
        extra_valid_columns.append('Marked as')
        extra_valid_columns.append('Description')
        extra_valid_columns.append('Protein FDR Confidence: Combined')
        extra_valid_columns.append('Master')
        
      elif(MyUtility.workDict['mode'] == 'Peptides'):
        #create a valid list of columns and add abundaces columns
        valid_columns = ['Sequence', 'Master Protein Accessions'] + abundances_columns

        #add extra optional column not used for the valid filter
        extra_valid_columns = valid_columns.copy()
        extra_valid_columns.append('Marked as')
        extra_valid_columns.append('Protein Accessions')
        extra_valid_columns.append('Master Protein Descriptions')
        extra_valid_columns.append('Confidence')
        extra_valid_columns.append('Quan Info')

      elif(MyUtility.workDict['mode'] == 'PSMs'):
        #create a valid list of columns and add abundaces columns
        valid_columns = ['Sequence', 'Master Protein Accessions',
                         'File ID']

        #add extra optional column not used for the valid filter
        extra_valid_columns = valid_columns.copy()
        extra_valid_columns.append('Marked as')
        extra_valid_columns.append('Protein Accessions')
        extra_valid_columns.append('Master Protein Descriptions')
        extra_valid_columns.append('Confidence')

      #in the df keep only the useful columns
      self.df = self.df.filter(items=extra_valid_columns)

    elif(MyUtility.workDict['input_type'] == 'fragpipe'):
      #find all abundances columns
      abundances_columns = []

      if(MyUtility.workDict['mode'] == 'Proteins'):
        #drop unusable columns
        self.df = self.df.drop(columns=["Entry Name"], errors="ignore")
        self.df = self.df.drop(columns=["Gene"], errors="ignore")
        self.df = self.df.drop(columns=["Protein Length"], errors="ignore")
        self.df = self.df.drop(columns=["Protein Existence"], errors="ignore")
        self.df = self.df.drop(columns=["Protein Probability"], errors="ignore")
        self.df = self.df.drop(columns=["Top Peptide Probability"], errors="ignore")
        self.df = self.df.drop(columns=["Combined Total Peptides"], errors="ignore")
        self.df = self.df.drop(columns=["Combined Spectral Count"], errors="ignore")
        self.df = self.df.drop(columns=["Combined Unique Spectral Count"], errors="ignore")
        self.df = self.df.drop(columns=["Combined Total Spectral Count"], errors="ignore")
        self.df = self.df.drop(columns=["Indistinguishable Proteins"], errors="ignore")

        self.df = self.df.drop(columns=[c for c in self.df.columns if c.endswith("Match Type")])

        #change columns name
        if ("Peptide Sequence" not in self.df.columns):
          self.df = self.df.rename(columns={"Protein": "Accession"})

        #create a valid list of columns and add abundaces columns
        valid_columns = ['Accession','Description'] + abundances_columns

        #add extra optional column not used for the valid filter
        extra_valid_columns = valid_columns.copy()
        extra_valid_columns.append('Protein ID')
        extra_valid_columns.append('Description')
        extra_valid_columns.append('Organism')
        
      elif(MyUtility.workDict['mode'] == 'Peptides'):
        #drop unusable columns
        self.df = self.df.drop(columns=["Prev AA"], errors="ignore")
        self.df = self.df.drop(columns=["Next AA"], errors="ignore")
        self.df = self.df.drop(columns=["Start"], errors="ignore")
        self.df = self.df.drop(columns=["End"], errors="ignore")
        self.df = self.df.drop(columns=["Peptide Length"], errors="ignore")
        self.df = self.df.drop(columns=["Charges"], errors="ignore")
        self.df = self.df.drop(columns=["Entry Name"], errors="ignore")
        self.df = self.df.drop(columns=["Gene"], errors="ignore")
        self.df = self.df.drop(columns=["Mapped Genes"], errors="ignore")
        self.df = self.df.drop(columns=["Indistinguishable Proteins"], errors="ignore")

        self.df = self.df.drop(columns=[c for c in self.df.columns if c.endswith("Match Type")])

        #change columns name
        self.df = self.df.rename(columns={"Peptide Sequence": "Sequence"})
        self.df = self.df.rename(columns={"Protein": "Master Protein Accessions"})
        self.df = self.df.rename(columns={"Protein Description": "Master Protein Descriptions"})

        #create a valid list of columns and add abundaces columns
        valid_columns = ['Sequence', 'Master Protein Accessions'] + abundances_columns

        #add extra optional column not used for the valid filter
        extra_valid_columns = valid_columns.copy()
        extra_valid_columns.append('Protein ID')
        extra_valid_columns.append('Protein Description')
        extra_valid_columns.append('Mapped Proteins')

      #Any "samples" to be excluded (aggregates, totals, etc.)
      EXCLUDE_SAMPLES = {"Combined"}
      
      #Build the map: typology -> set of samples that have it
      map_type_to_samples = defaultdict(set)
      
      for col in map(str, self.df.columns):
          if " " in col:
              sample, typology = col.split(" ", 1)  # split on first space
              sample = sample.strip()
              typology = typology.strip()
              if sample not in EXCLUDE_SAMPLES:
                  map_type_to_samples[typology].add(sample)
      
      #Consider "abundance types" those that appear on >= 2 samples
      abundance_types = sorted([t for t, S in map_type_to_samples.items() if len(S) >= 2 ])
      
      #The samples are all those who have at least one valid typology
      self.samples_description = sorted({s for t in abundance_types for s in map_type_to_samples[t]})

      num_samples = len(self.samples_description)
      self.samples_code = []
      for i in range(num_samples):
          self.samples_code.append("F" + str(i+1))

      #reset optionmenu
      self.quantitative = abundance_types
      self.update_optionmenu(self.opt_quantitative, self.opt_quantitative_var, self.quantitative)

    else:
      #Rinomino anche le altre righe per omologarle con gli altri file (Nel caso che esistano altrimenti si solleverà un erroro poco dopo)
      if "accession" in self.df.columns:
        if(MyUtility.workDict['mode'] == 'Proteins'):
          self.df = self.df.rename(columns={"accession": "Accession"})
        else:
          self.df = self.df.rename(columns={"accession": "Master Protein Accessions"})
      if "description" in self.df.columns:
        self.df = self.df.rename(columns={"description": "Description"})
      if "sequence" in self.df.columns:
        self.df = self.df.rename(columns={"sequence": "Sequence"})
      if "spectra_ref" in self.df.columns:
        self.df = self.df.rename(columns={"spectra_ref": "Spectra_ref"})

      #Seleziono le colonne da rinominare e quelle utili per il coretto funzionamento del file 
      if(MyUtility.workDict['mode'] == 'Proteins'):
        abundances_columns_name = 'protein_abundance_assay['
        valid_columns = ['Accession', 'Description']
      elif(MyUtility.workDict['mode'] == 'Peptides'):
        abundances_columns_name = 'peptide_abundance_assay['
        valid_columns = ['Sequence', 'Master Protein Accessions']
      elif(MyUtility.workDict['mode'] == 'PSMs'):
        abundances_columns_name = 'peptide_abundance_assay['
        valid_columns = ['Sequence', 'Master Protein Accessions', 'PSM_ID', 'Spectra_ref']

      #Rename columns
      self.df = self.df.rename(columns=lambda x: f"Abundance F{x.split(abundances_columns_name)[1][:-1]}" if x.startswith(abundances_columns_name) else x)

      #find all abundances columns
      abundances_columns = list(self.df.filter(regex = 'Abundance F')) + list(self.df.filter(regex = '(Normalized)'))
      self.samples_code = list(self.df.filter(regex = 'Abundance F'))
      self.samples_code = [s.replace("Abundance ", "").strip() for s in self.samples_code]

      #create a valid list of columns and add abundaces columns
      valid_columns = valid_columns + abundances_columns

      #in the df keep only the useful columns
      self.df = self.df.filter(items=valid_columns)

    #check if the df_columns cointains all valid columns, otherwise return an error message and exit from method
    check = all(item in self.df.columns for item in valid_columns)
    if(not check):
      self.isFileLoad = False
      self.lbl_loadedFile['text'] = "No file"
      tk.messagebox.showerror(parent=self, title="Error", message="Problems with columns in uploaded file")
      return False

    ### check for remove filter if column is not present ###
    #Confidence
    if( hasattr(self, 'frame_confidence') ):
      column_name = ''
      if(MyUtility.workDict['mode'] == 'Proteins'):
        column_name = 'Protein FDR Confidence: Combined'
      else:
        column_name = 'Confidence'
      if(column_name not in self.df.columns):
        self.frame_confidence.grid_remove()
      else:
        self.frame_confidence.grid()

    #Quan Info
    if( hasattr(self, 'frame_quanInfo') ):
      if('Quan Info' not in self.df.columns):
        self.frame_quanInfo.grid_remove()
      else:
        self.frame_quanInfo.grid()
        self.quanList = MyUtility.create_unique_list(self.df, 'Quan Info')
        self.scl_check_quantInfo.insertItems(self.quanList)
        self.scl_check_quantInfo.scrollToTop()

    #Description
    if( hasattr(self, 'frame_description') ):
      columnDescription = ''
      if(MyUtility.workDict['mode'] == 'Proteins'):
        columnDescription = 'Description'
      else:
        columnDescription = 'Master Protein Descriptions'
      if(columnDescription not in self.df.columns):
        self.frame_description.grid_remove()
      else:
        self.frame_description.grid()

    #Marker
    if( hasattr(self, 'frame_marker') ):
      if('Marked as' not in self.df.columns):
        self.frame_marker.grid_remove()
      else:  
        self.frame_marker.grid()
        self.markedList = MyUtility.create_unique_list(self.df, 'Marked as')
        self.scl_check_marker.insertItems(self.markedList)
        self.scl_check_marker.scrollToTop()

    #Database
    if( hasattr(self, 'frame_database1') ):
      self.winLoad = wLd.LoadingWindow("")

      rowNum = str(len(self.df))

      self.winLoad.change_label("0 entries out of " + rowNum)
      self.update()

      #Set the column name of id protein
      if(MyUtility.workDict['mode'] == 'Proteins'):
        columnName = 'Accession'
      else:
        columnName = 'Master Protein Accessions'

      if(MyUtility.workDict['mode'] == 'Proteins'):
        columnDescription = 'Description'
      else:
        columnDescription = 'Master Protein Descriptions'

      #create 2 new columns
      self.df["Database"] = ""
      self.df["Lineage"] = ""
     
      #move col Database before Organism
      if("Organism" in self.df.columns):
        cols = [c for c in self.df.columns if c not in ("Database")]
        self.df = self.df[[*cols[:cols.index("Organism")], "Database", "Organism", *cols[cols.index("Organism")+1:]]]
      #or in second position
      else:
        cols = list(self.df.columns)
        first = cols[0]
        last = cols[-1]
        new_order = [first, last] + cols[1:-1]
        self.df = self.df[new_order]
      
      #move col Lineage after Database
      idx = self.df.columns.get_loc("Database") + 1
      cols = list(self.df.columns)
      cols.remove("Lineage")
      cols.insert(idx, "Lineage")
      self.df = self.df[cols]

      #iterate the rows and set the database columns 
      self.codesUniProt = []

      self.start_processing_rows(columnName, columnDescription)

      return False
    else:
      self.processing_ending()
      return True

  def upload_file(self):
    #ask file name
    if(MyUtility.workDict['input_type'] == 'proteome'):
      filepath = filedialog.askopenfilename(parent=self, title="Open",filetypes=config.file_types_generic)
    elif(MyUtility.workDict['input_type'] == 'fragpipe'):
      filepath = filedialog.askopenfilename(parent=self, title="Open",filetypes=config.file_types_fragpipe)
    else:
      filepath = filedialog.askopenfilename(parent=self, title="Open", filetypes=config.file_types_mzTab)

    #check if a file has been chosen
    if filepath:
      #load the name of file in label (if name is too long then resize it)
      tmp_path = os.path.basename(filepath)
      if(len(tmp_path)>25):
        tmp_path = tmp_path[:25] + "..."
      self.lbl_loadedFile['text'] = tmp_path

      #show loading windows
      self.winLoad = wLd.LoadingWindow("Uploading file...")

      #create thread to load file
      if(MyUtility.workDict["input_type"]=='proteome'):
        upload_thread = AsyncUpload(filepath)
      elif(MyUtility.workDict["input_type"]=='fragpipe'):
        upload_thread = AsyncUpload(filepath)
      else: #'mzTab'
        if(MyUtility.workDict["mode"]=='Proteins'):
          headerName = 'PRH'
          row_name = 'PRT'
        elif(MyUtility.workDict["mode"]=='Peptides'):
          headerName = 'PEH'
          row_name = 'PEP'
        elif(MyUtility.workDict["mode"]=='PSMs'):
          headerName = 'PSH'
          row_name = 'PSM'
        upload_thread = AsyncUpload_mzTab(filepath, headerName, row_name)
      upload_thread.start()
      self.monitor_upload(upload_thread)
    else:
      tk.messagebox.showwarning(parent=self, title="Warning", message="No file selected")

  def upload_file_MAGsdb(self):
    #ask file name
    filepath = filedialog.askopenfilename(parent=self, title="Open", filetypes=[("tsv", "*.tsv")])

    #check if a file has been chosen
    if filepath:
      #load the name of file in label (if name is too long then resize it)
      tmp_path = os.path.basename(filepath)
      if(len(tmp_path)>25):
        tmp_path = tmp_path[:25] + "..."
      self.lbl_loadedFile_MAGsdb['text'] = tmp_path

      #show loading windows
      self.winLoad = wLd.LoadingWindow("Uploading file...")

      #create thread to load file
      upload_thread = AsyncUpload(filepath, 'MAG')
      upload_thread.start()
      self.monitor_upload_MAGsdb(upload_thread)
    else:
      tk.messagebox.showwarning(parent=self, title="Warning", message="No file selected")

  def upload_file_CNGBdb(self):
    #ask file name
    filepath = filedialog.askopenfilename(parent=self, title="Open", filetypes=[("tsv", "*.tsv")])

    #check if a file has been chosen
    if filepath:
      #load the name of file in label (if name is too long then resize it)
      tmp_path = os.path.basename(filepath)
      if(len(tmp_path)>25):
        tmp_path = tmp_path[:25] + "..."
      self.lbl_loadedFile_CNGBdb['text'] = tmp_path

      #show loading windows
      self.winLoad = wLd.LoadingWindow("Uploading file...")

      #create thread to load file
      upload_thread = AsyncUpload(filepath, "Accession")
      upload_thread.start()
      self.monitor_upload_CNGBdb(upload_thread)
    else:
      tk.messagebox.showwarning(parent=self, title="Warning", message="No file selected")

  def proper_round(self, num, dec=0):
    num = str(num)[:str(num).index('.')+dec+2]
    if num[-1]>='5':
        return float(num[:-2-(not dec)]+str(int(num[-2-(not dec)])+1))
    return float(num[:-1])

  def add_description_element(self):
    #string to insert
    my_string = self.ntr_description.get()
    #check if alredy insert
    iscontain = my_string in self.dsc_listbox.get(0, "end")
    if(iscontain):
      tk.messagebox.showerror(parent=self, title="Error", message="These values have already been entered")
    else:
      #add new text to listbox
      self.dsc_listbox.insert(END, my_string)
      #delete old description text
      self.ntr_description.delete(0,END)

  def remove_description_element(self):
    #self.dsc_listbox.delete(ANCHOR)
    for item in reversed(self.dsc_listbox.curselection()):
      self.dsc_listbox.delete(item)

  def is_value_ok(self):
    #If area not exist then return True because there isn't problem
    if( not hasattr(self, 'ntr_abundance') ):
      return True

    #check for abundance
    if(not self.ntr_abundance.get().isdigit()):
      self.ntr_abundance.insert(0, "0")

    num_abundance = int(self.ntr_abundance.get())
    #control type
    if(self.opt_abundance_var.get() == 'Absolute'):
      if(num_abundance<0 or num_abundance>self.num_abundance_tot):
        tk.messagebox.showerror(parent=self, title="Error", message="Abundance value is out of range")
        return False
    elif(self.opt_abundance_var.get() == 'Percentage'):
      if(num_abundance<0 or num_abundance>100):
        tk.messagebox.showerror(parent=self, title="Error", message="Abundance value is out of range")
        return False

    #if ther aren't error, then return true
    return True

  def monitor_manage_file(self, thread, next_command):
    if thread.is_alive():
      # check the thread every 100ms
      self.after(100, lambda: self.monitor_manage_file(thread, next_command))
    else:
      #delete load window
      self.winLoad.destroy()
      #put window in front
      self.lift()
      if(next_command == "download"):
        self.ultimate_download()
      elif(next_command == "next_window"):
        self.ultimate_next_window()

  def download(self):
    #check if file is loadid
    if(self.isFileLoad):
      #Check if value are right
      if(not self.is_value_ok()):
        return

      #ask directory to save file
      file_path = filedialog.asksaveasfilename(parent=self, filetypes=config.file_types_generic, defaultextension=".xlsx")

      #check if a file has been chosen
      if file_path:
        #save file temporaneous
        self.file_path = file_path

        #show loading windows
        self.winLoad = wLd.LoadingWindow("Managing file...")
        
        #create thread to manage the file
        manage_file_thread = ManageData(self)
        manage_file_thread.start()
        self.monitor_manage_file(manage_file_thread, "download")
      else:
        tk.messagebox.showerror(parent=self, title="Error", message="No directory selected")
    else:
      tk.messagebox.showerror(parent=self, title="Error", message="No files uploaded")

  def ultimate_download(self):
    #show loading windows
    self.winLoad = wLd.LoadingWindow("Downloading file...")

    #create thread to download file
    download_thread = AsyncDownload(self.df_tmp, self.file_path)
    download_thread.start()
    self.monitor_download(download_thread)

  def previous_window(self):
    #hide this window
    #self.withdraw()
    #Destroy this window
    self.destroy()

    #show last window
    self.wn_previous.deiconify()
    self.wn_previous.lift()

  def next_window(self):
    #check if file is loadid
    if(self.isFileLoad):
      #Check if value are right
      if(not self.is_value_ok()):
        return

      if(MyUtility.workDict['input_type'] == 'fragpipe'):
        MyUtility.workDict["quantitative"] = self.opt_quantitative_var.get()
      else:
        MyUtility.workDict["quantitative"] = ""
        
      #show loading windows
      self.winLoad = wLd.LoadingWindow("Managing file...")
      
      #create thread to manage the file
      manage_file_thread = ManageData(self)
      manage_file_thread.start()
      self.monitor_manage_file(manage_file_thread, "next_window")
    else:
      tk.messagebox.showerror(parent=self, title="Error", message="No files uploaded")

  def ultimate_next_window(self):
    #Add information to dict
    if(hasattr(self,'var_chc_fill_zero')):
      MyUtility.workDict["fill0"] = self.var_chc_fill_zero.get()
    else:
      MyUtility.workDict["fill0"] = False

    #hide this window
    self.withdraw()
    #create new window
    self.windowTaxonomicMenu = wTxMn.TaxonomicMenuWindow(self.wn_root, self, self.df_tmp)

  def process_rows_with_threads(self, columnName: str, columnDescription: str, max_workers: int = None):
      """
      Esegue la stessa logica del ciclo originale ma in multithreading.
      - Letture senza lock
      - Scritture su self.df e self.codesUniProt protette con lock
      - Aggiornamenti GUI inoltrati al main thread
      """

      if max_workers is None:
          max_workers = min(32, (os.cpu_count() or 4) * 2)
  
      if columnName not in self.df.columns:
          raise KeyError(f"Colonna '{columnName}' non trovata in self.df")
      if columnDescription not in self.df.columns:
          raise KeyError(f"Colonna '{columnDescription}' non trovata in self.df")
  
      total_rows = len(self.df)
      progress_lock = Lock()
      write_lock = Lock()
      progress = {"done": 0}  # mutabile per clausura
  
      def safe_gui_update(txt: str):
          """Inserisce un messaggio nella coda da qualsiasi thread (nessuna chiamata Tkinter qui)."""
          try:
              #print(txt)
              self._gui_queue.put_nowait(txt)
          except Exception as e:
              # In casi estremi, non bloccare il worker per problemi GUI.
              print(f"[safe_gui_update] queue error: {e!r}")
        
      def replace_token_in_desc(desc_val, token: str):
          """Rimuove 'token ' dalla descrizione (se presente). Gestisce NaN."""
          if pd.isna(desc_val) or not isinstance(desc_val, str) or not token:
              return desc_val
          return desc_val.replace(token + " ", "")
  
      def worker(index: int):
          nonlocal progress
  
          try:
              # ---- Letture (senza lock)
              row = self.df.loc[index]
              value = row[columnName]
              desc_val = row[columnDescription]
  
              if pd.isna(value):
                  # solo avanzamento/GUI
                  pass
              else:
                  s = str(value)
  
                  updates = {}
                  uniprot_code = None
  
                  # --- CASO UniProt
                  if s.startswith(("sp|", "tr|")):
                      updates["Database"] = "UniProt"
                      parts = s.split("|", 2)
                      if len(parts) >= 2:
                          uniprot_code = parts[1]
  
                  # --- CASO "db|..."
                  elif s.startswith("db|"):
                      parts = s.split("|")
                      code = parts[1] if len(parts) > 1 else ""
  
                      #if code.startswith("MGYG"):
                      # rimuovi da description
                      new_desc = replace_token_in_desc(desc_val, code)
  
                      if getattr(self, "isFileLoad_MAGsdb", False):
                          code_trunc = code.split("_")[0]
                          new_desc = replace_token_in_desc(new_desc, code_trunc)
  
                          # Lookup su DF di riferimento (sola lettura)
                          try:
                              row_MAGsdb = self.df_MAGsdb.loc[code_trunc]
                              updates["Database"] = row_MAGsdb["catalog"]
                              updates["Lineage"]  = row_MAGsdb["Lineage"]
                              updates["Organism"] = row_MAGsdb["Organism"]
                          except KeyError:
                              pass
  
                      # applica descrizione solo se è cambiata
                      if new_desc is not None and new_desc != desc_val:
                          updates[columnDescription] = new_desc
  
                  # --- CASO stringa che inizia direttamente con "MGYG"
                  elif s.startswith("MGYG"):
                      new_desc = replace_token_in_desc(desc_val, s)
  
                      if getattr(self, "isFileLoad_MAGsdb", False):
                          code_trunc = s.split("_")[0]
                          try:
                              row_MAGsdb = self.df_MAGsdb.loc[code_trunc]
                              updates["Database"] = row_MAGsdb["catalog"]
                              updates["Lineage"]  = row_MAGsdb["Lineage"]
                              updates["Organism"] = row_MAGsdb["Organism"]
                          except KeyError:
                              pass
  
                          new_desc = replace_token_in_desc(new_desc, code_trunc)
  
                      if new_desc is not None and new_desc != desc_val:
                          updates[columnDescription] = new_desc
  
                  # ---- Scritture su DF/lista (con lock)
                  if updates or uniprot_code:
                      with write_lock:
                          for k, v in updates.items():
                              # at è più veloce e sicuro sul singolo elemento
                              self.df.at[index, k] = v
                          if uniprot_code:
                              if not hasattr(self, "codesUniProt"):
                                  self.codesUniProt = []
                              self.codesUniProt.append(uniprot_code)
  
          finally:
              # ---- Avanzamento + GUI (con lock leggero)
              with progress_lock:
                  progress["done"] += 1
                  done = progress["done"]
                  # throttling GUI: ~50 aggiornamenti massimo
                  step = max(1, total_rows // 50)
                  #if (done % step == 0) or (done == total_rows):
                  safe_gui_update(f"{done} entries of {total_rows}")
  
      # Avvio pool di thread
      with ThreadPoolExecutor(max_workers=max_workers) as ex:
          # Scorriamo tutti gli indici del DF
          ex.map(worker, list(self.df.index))
  
      # Aggiornamento finale GUI
      safe_gui_update(f"{total_rows} entries of {total_rows}")

  def _init_gui_queue(self):
      # Coda condivisa tra worker e GUI
      self._gui_queue = queue.Queue()
      self._gui_pump_running = False
  
  def _start_gui_pump(self, interval_ms: int = 150):
      if self._gui_pump_running:
          return
      self._gui_pump_running = True
  
      def pump():
          if not self._gui_pump_running:
              return
  
          try:
              last_txt = None
              while True:
                  txt = self._gui_queue.get_nowait()
                  last_txt = txt
          except queue.Empty:
              pass
  
          # Controlla se la loading window esiste ancora
          if last_txt is not None:
              try:
                  if getattr(self, "winLoad", None) is not None and self.winLoad.winfo_exists():
                      self.winLoad.change_label(last_txt)
              except Exception:
                  # Se la finestra è stata chiusa → stop pump
                  self._gui_pump_running = False
                  return
  
          if self._gui_pump_running:
              try:
                  self.after(interval_ms, pump)
              except:
                  self._gui_pump_running = False
  
      self.after(interval_ms, pump)
  
  def _stop_gui_pump(self):
      self._gui_pump_running = False

  def start_processing_rows(self, columnName, columnDescription):
      # Avvio pump nel main thread
      self.after(0, lambda: self._start_gui_pump(150))
  
      # Worker thread con il lavoro pesante
      worker = Thread(target=lambda: self.process_rows_with_threads(
          columnName, columnDescription, max_workers=None
      ))
      worker.daemon = True
      worker.start()
  
      # Attesa NON bloccante del worker
      self.wait_for_worker(worker, columnName, columnDescription)

  def wait_for_worker(self, thread, columnName, columnDescription):
      if thread.is_alive():
          # Continui ad “aspettare” ma SENZA bloccare la GUI
          self.after(100, lambda: self.wait_for_worker(thread, columnName, columnDescription))
      else:
          # Quando il worker FINISCE → puoi continuare
          self.processing_finished(columnName, columnDescription)

  def processing_finished(self, columnName, columnDescription):
      # Ferma il pump
      self._stop_gui_pump()

      #for all UniProt rows call the UniProt API to retrieve the lineage
      if(self.var_chc_uniprot_annotation.get() == 1):
        uniProtMaxQueries = 500
        lineage_map = {}
        organism_map = {}
        urlUniProt = "https://rest.uniprot.org/uniprotkb/accessions"
        for i in range(0, len(self.codesUniProt), uniProtMaxQueries):
          self.winLoad.change_label(str(int(i / uniProtMaxQueries) + 1) + " UniProt chunk of " + str((int(len(self.codesUniProt) / uniProtMaxQueries)) + 1))
          self.update()

          #Query UniProt in batches of uniProtMaxQueries 
          chunk = self.codesUniProt[i:i + uniProtMaxQueries]
          
          params = {
              "accessions": ",".join(chunk),
              "format": "tsv",
              "fields": "accession,lineage,organism_name"
          }
          
          try:
            response = requests.get(urlUniProt, params=params, timeout=60)
            if response.status_code == 200:
              batch_df = pd.read_csv(io.StringIO(response.text), sep="\t")
              for _, row in batch_df.iterrows():
                lineage = filter_to_canonical_string(row['Taxonomic lineage'], infer_species=True)
                organism = row['Organism']
                lineage_map[str(row['Entry'])] = lineage
                organism_map[str(row['Entry'])] = organism
          except Exception as e:
            print(f"Network error: {e}")
          
          time.sleep(0.2) # Courteous delay for UniProt servers

        #create a mask between Database and UniProt
        mask_uniprot = self.df['Database'].eq('UniProt')

        #create the codes with part of columnName
        codes = (
            self.df[columnName]
              .where(mask_uniprot)                       
              .str.split('|', n=2)                       
              .str[1]                                    
        )

        #map lineage with codes
        mapped_lineage = codes.map(lineage_map)

        #map organism with codes
        mapped_organism = codes.map(organism_map)

        #store linked data 
        self.df.loc[mask_uniprot & mapped_lineage.notna(), 'Lineage'] = mapped_lineage
        self.df.loc[mask_uniprot & mapped_organism.notna(), 'Organism'] = mapped_organism

      self.winLoad.change_label("")
      self.update()
  
      self.winLoad.destroy()
      
      self.processing_ending()

  def processing_ending(self):
      #Database
      if( hasattr(self, 'frame_database1') ):
        self.scl_database1_filter.grid()
        self.scl_database1_view.grid()
        self.databaseList = MyUtility.create_unique_list(self.df, 'Database')
        self.scl_database1_filter.insertItems(self.databaseList)
        self.scl_database1_view.insertItems(self.databaseList)
        self.scl_database1_filter.scrollToTop()
        self.scl_database1_view.scrollToTop()

      #Database
      if( hasattr(self, 'frame_database2') ):
        self.on_change_set_checks_database_filter()
        self.on_change_set_checks_database_view()
        self.rdb_database1_filter.invoke()
      
      #Valid values (for number of elements)
      if( hasattr(self, 'frame_validValues') ):
        if(MyUtility.workDict['input_type'] == 'proteome'):
          num_abundance = sum(['Abundance:' in col for col in self.df.columns])
          num_normalized = sum(['(Normalized):' in col for col in self.df.columns])
          if(num_abundance > 0) and (num_normalized > 0):
            abundances_divisor = 2
          else:
            abundances_divisor = 1  
      
          #add number of aboundance columns
          self.num_abundance_tot = int((len(list(self.df.filter(regex=r'F\d+'))))/abundances_divisor)
        elif(MyUtility.workDict['input_type'] == 'fragpipe'):
          self.num_abundance_tot = len(self.samples_code)
        else:
          #add number of aboundance columns
          self.num_abundance_tot = int((len(list(self.df.filter(regex=r'F\d+')))))
      
        self.lbl_abundanceTot["text"] = "(# of samples: " + str(self.num_abundance_tot) + " )"
      
      ### check for remove Options if column is not present ###
      #Master proteins only
      if( hasattr(self, 'chc_master') ):
        if('Master' not in self.df.columns):
          self.var_chc_master.set(0)
          self.chc_master.grid_remove()
        else:
          self.chc_master.grid()
      
      #Select normalize abundances
      if( hasattr(self, 'chc_normalized') ):
        num_abundance = sum(['Abundance:' in col for col in self.df.columns])
        num_normalized = sum(['(Normalized):' in col for col in self.df.columns])
      
        if(num_normalized == 0):
          self.var_chc_normalized.set(0)
          self.chc_normalized.grid_remove()
        else:
          self.chc_normalized.grid()
      
        if( (num_normalized > 0) and (num_abundance < 1) ):
          self.var_chc_normalized.set(1)
          self.chc_normalized.config(state="disabled")
        else:
          # Riabilitazione del checkbox
          self.chc_normalized.config(state="normal")
      
      #Show protein accession
      if( hasattr(self, 'chc_ptrAccessions') ):
        if('Protein Accessions' not in self.df.columns):
          self.var_chc_ptrAccessions.set(0)
          self.chc_ptrAccessions.grid_remove()
        else:
          self.chc_ptrAccessions.grid()
      
      if( hasattr(self, 'frame_samples') ):
        self.scl_samples.grid()
        self.scl_samples.insertItems(items=self.samples_code, itemsDescription=self.samples_description)
        self.scl_samples.scrollToTop()

      self.isFileLoad = True
      
      self.winLoad.destroy()


'''
if __name__ == "__main__":
  app = ProteinsWindow()
  app.mainloop()
'''

CANONICAL_RANKS = ["domain", "kingdom", "phylum", "class", "order", "family", "genus", "species"]

# Mappa di normalizzazione dei ranghi (aggiungi varianti se ne incontri)
RANK_NORMALIZER = {
    "no rank": "unranked",
    "domain": "domain",
    "kingdom": "kingdom",
    "phylum": "phylum",
    "subphylum": "subphylum",
    "class": "class",
    "superclass": "superclass",
    "order": "order",
    "suborder": "suborder",
    "family": "family",
    "subfamily": "subfamily",
    "genus": "genus",
    "species": "species",
    "clade": "clade",
    "superorder": "superorder",
    "infraorder": "infraorder",
    "parvorder": "parvorder",
    "superfamily": "superfamily",
}

def split_on_commas_outside_parens(s: str):
    """Divide la stringa sulle virgole non racchiuse tra parentesi."""
    parts, buf, depth = [], [], 0
    for ch in s:
        if ch == '(':
            depth += 1
            buf.append(ch)
        elif ch == ')':
            depth = max(0, depth - 1)
            buf.append(ch)
        elif ch == ',' and depth == 0:
            parts.append(''.join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append(''.join(buf).strip())
    return parts

def parse_taxonomy_string(taxostr: str):
    """
    Ritorna una lista di dict: [{"name": ..., "rank": ...}, ...]
    Accetta formati 'Nome (rank)' separati da virgole; ignora punto finale.
    Tollerante a elementi senza '(rank)' → rank=None.
    """
    taxostr = (taxostr or "").strip().rstrip('.')
    if not taxostr:
        return []
    chunks = split_on_commas_outside_parens(taxostr)
    items = []
    pattern = re.compile(r'^(.*?)\s*\((.*?)\)\s*$')
    for c in chunks:
        if not c:
            continue
        m = pattern.match(c)
        if m:
            name = m.group(1).strip()
            rank = m.group(2).strip()
        else:
            name = c.strip()
            rank = None
        items.append({"name": name, "rank": rank})
    return items

def normalize_ranks(items, normalizer=RANK_NORMALIZER):
    """Lowercase dei ranghi + mapping sinonimi; se rank manca resta None."""
    out = []
    for it in items:
        r = it['rank']
        r_norm = normalizer.get(r.lower(), r.lower()) if r else None
        out.append({"name": it['name'], "rank": r_norm})
    return out

# (Opzionale) inferenza species se serve
_BINOMIAL_RE = re.compile(r'^\s*([A-Z][a-zA-Z-]+)\s+([a-z][a-zA-Z-]+)(?:\s+([a-z][a-zA-Z-]+))?\b')

def maybe_infer_species(items):
    """Aggiunge 'species' se non presente ma si riconosce un binomiale alla fine."""
    if any((it.get('rank') == 'species') for it in items) or not items:
        return items
    candidates = [it for it in items[-3:] if it.get('rank') is None or it.get('rank') not in CANONICAL_RANKS]
    for it in reversed(candidates):
        m = _BINOMIAL_RE.match(it['name'])
        if m:
            genus, sp, ssp = m.group(1), m.group(2), m.group(3)
            species_name = f"{genus} {sp}" + (f" {ssp}" if ssp else "")
            return items + [{"name": species_name, "rank": "species"}]
    return items

def filter_to_canonical(items, canonical=CANONICAL_RANKS, keep='first', infer_species=False):
    """
    Filtra ai soli ranghi canonici, restituisce OrderedDict {rank: name} con tutte le chiavi presenti e valori None dove mancanti.
    """
    if infer_species:
        items = maybe_infer_species(items)
    od = OrderedDict((r, None) for r in canonical)
    for it in items:
        r, n = it['rank'], it['name']
        if r in canonical:
            if keep == 'first':
                if od[r] is None:
                    od[r] = n
            else:
                od[r] = n
    return od

def canonical_to_string(rank_to_name: OrderedDict, include_missing=False, trailing_dot=True):
    """
    Converte {rank: name} → 'Name (rank), Name (rank), ...'
    - include_missing=False: salta i ranghi con valore None
    - trailing_dot=True: aggiunge '.' finale
    Ordine delle voci: domain → … → species (ordine canonico)
    """
    parts = []
    for r in CANONICAL_RANKS:
        name = rank_to_name.get(r)
        if name is None and not include_missing:
            continue
        if name is None and include_missing:
            parts.append(f"( {r} )")  # oppure f"unknown ({r})"
        else:
            parts.append(f"{name} ({r})")
    out = ", ".join(parts)
    return out #+ ("." if trailing_dot and out else "")

def filter_to_canonical_string(taxostr: str, keep='first', infer_species=False, trailing_dot=True):
    """
    Scorciatoia: input = stringa tassonomica completa,
    output = stringa con soli ranghi canonici nello stesso formato 'Name (rank), ...'
    """
    items = normalize_ranks(parse_taxonomy_string(taxostr))
    r2n = filter_to_canonical(items, keep=keep, infer_species=infer_species)
    return canonical_to_string(r2n, include_missing=False, trailing_dot=trailing_dot)