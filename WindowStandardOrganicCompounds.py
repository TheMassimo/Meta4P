#import config module for environmental variability
import config
#import my utility class and function
import MyUtility
#import my multi threading function to upload and download file
from MyMultiThreading import *


#tkinter import
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from tkinter.messagebox import showinfo
from tkinter.ttk import Separator, Style
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

class StandardOrganicCompoundsWindow(tk.Toplevel): #tk.Tk):
  def __init__(self, wn_root, wn_previous):
    super().__init__()

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

    # configure the root window
    self.title(MyUtility.workDict["mode"])
    
    #for Entry widget
    self.vcmd = (self.register(self.onValidate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

    ### left area ###
    #Load/download frame
    self.frame_left = tk.Frame(self, borderwidth=2, relief='flat')
    self.frame_left.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
    #Load button
    self.btn_loadFile = tk.Button(self.frame_left, text='Upload input file', font=config.font_button, width=20, command=self.upload_file)
    self.btn_loadFile.grid(row=0, column=0, padx=5, pady=5)
    #label template
    self.lbl_loadedFile = tk.Label(self.frame_left, text='No file',width=30,font=config.font_up_base)
    self.lbl_loadedFile.grid(row=1, column=0, padx=5, pady=5)
    #Download button
    self.btn_download = tk.Button(self.frame_left, text='Download filtered table', font=config.font_button, width=20,command=self.download)
    self.btn_download.grid(row=2, column=0, padx=5, pady=5)

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
        self.make_makeAs(p_row=3, p_column=2, p_sticky='n')
      elif(MyUtility.workDict['mode'] == 'Peptides'):
        self.make_confidence(p_row=2, p_column=0, p_sticky='n')
        self.make_quantInfo(p_row=3, p_column=0, p_sticky='n')
        self.make_description(p_row=2, p_column=1, p_sticky='n')
        self.make_validValues(p_row=2, p_column=2, p_sticky='n')
        self.make_makeAs(p_row=3, p_column=2, p_sticky='n') 
      elif(MyUtility.workDict['mode'] == 'PSMs'):
        self.make_confidence(p_row=2, p_column=0, p_sticky='n')
        self.make_description(p_row=2, p_column=1, p_sticky='n')
        self.make_makeAs(p_row=2, p_column=2, p_sticky='n')
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

    #option label
    self.lbl_options = tk.Label(self.frame_right,text='Options',width=32,font=config.font_title)  
    self.lbl_options.grid(row=0, column=0, padx=6, pady=6)

    #check the corret checkbox to insert according to input_type and mode
    if(MyUtility.workDict['input_type'] == 'proteome'):
      if(MyUtility.workDict['mode'] == 'Proteins'):
        self.make_fill_zero(p_row=1)
        self.make_master(p_row=2)
        self.make_normalized(p_row=3)
        self.make_re_normalized(p_row=4, p_text='(Re)normalize abundances after filtering')
      elif(MyUtility.workDict['mode'] == 'Peptides'):
        self.make_fill_zero(p_row=1)
        self.make_ptrAccessions(p_row=2)
        self.make_normalized(p_row=3)
        self.make_re_normalized(p_row=4, p_text='(Re)normalize abundances after filtering')
      elif(MyUtility.workDict['mode'] == 'PSMs'):
        self.make_fill_zero(p_row=1)
        self.make_ptrAccessions(p_row=2)
    else:
      if(MyUtility.workDict['mode'] == 'Proteins'):
        self.make_fill_zero(p_row=1)
        self.make_re_normalized(p_row=2, p_text='Normalize abundances (after filtering)')
      elif(MyUtility.workDict['mode'] == 'Peptides'):
        self.make_fill_zero(p_row=1)
        self.make_re_normalized(p_row=2, p_text='Normalize abundances (after filtering)')
      elif(MyUtility.workDict['mode'] == 'PSMs'):
        self.make_fill_zero(p_row=1)

      
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
    self.lbl_quanInfo.grid(row=6, column=1, padx=6, pady=(24,6))
    #MakedAs scroll
    self.scl_check_quantInfo = MyUtility.CheckboxList(self.frame_quanInfo, bg="grey", padx=1, pady=1)
    self.scl_check_quantInfo.grid(row=7,column=1, rowspan=4)

  def make_description(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #Description frame
    self.frame_description = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_description.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)
    #Description Label
    self.lbl_description = tk.Label(self.frame_description,text='Protein Description', width=22, font=config.font_subtitle)  
    self.lbl_description.grid(row=0, column=0, columnspan=2, padx=6, pady=6)
    #Radio button frame
    self.rbd_frame = Frame(self.frame_description, bg="red", width=20, height=20)
    self.rbd_frame.grid(row=1, column=0, columnspan=2)
    #Radio button
    self.rdb_var = StringVar(value='and')
    self.rdb_and = tk.Radiobutton(self.rbd_frame, text="And", width=10, variable=self.rdb_var, value='and')
    self.rdb_and.grid(row=0, column=0, padx=(0,0), pady=0)#, sticky="W")
    self.rdb_and.config( font = config.font_checkbox )
    self.rdb_or = tk.Radiobutton(self.rbd_frame, text="Or", width=10, variable=self.rdb_var, value='or')
    self.rdb_or.grid(row=0, column=1, padx=(0,0), pady=0)#, sticky="E")
    self.rdb_or.config( font = config.font_checkbox )
    #Description Entry
    self.ntr_description = tk.Entry(self.frame_description, width=36)
    self.ntr_description.grid(row=2,column=0, padx=5, pady=5)
    #Description Add button
    self.btn_add = tk.Button(self.frame_description, text='Add', font=config.font_button, width=3, command=self.add_description_element)
    self.btn_add.grid(row=2, column=1, padx=5, pady=5)
    #Create frame and scrollbar
    self.dsc_frame = Frame(self.frame_description)#, bg='red')
    self.dsc_frame.grid(row=4, column=0, rowspan=4, columnspan=2)
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
    self.btn_remove.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

  def make_makeAs(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #MakedAs frame
    self.frame_marker = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_marker.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)
    #MakedAs label
    self.lbl_marker = tk.Label(self.frame_marker,text='Marker', width=20, font=config.font_subtitle)  
    self.lbl_marker.grid(row=0, column=0, padx=6, pady=6)
    #MakedAs scroll
    self.scl_check_marker = MyUtility.CheckboxList(self.frame_marker, bg="grey", padx=1, pady=1)
    self.scl_check_marker.grid(row=1,column=0, rowspan=4)

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


  ### Functions to create Options in window ###
  def make_fill_zero(self, p_row=0, p_column=0):
    #Fill with 0 in abundances
    self.var_chc_fill_zero = IntVar(value=0)
    self.chc_fill_zero = tk.Checkbutton(self.frame_right, text='Replace missing values with 0', width=32, anchor="w", variable=self.var_chc_fill_zero, onvalue=1, offvalue=0)
    self.chc_fill_zero.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_fill_zero.config( font = config.font_checkbox )

  def make_master(self, p_row=0, p_column=0):
    #Master checkbox
    self.var_chc_master = IntVar(value=0)
    self.chc_master = tk.Checkbutton(self.frame_right, text='Master proteins only', width=32, anchor="w", variable=self.var_chc_master, onvalue=1, offvalue=0)
    self.chc_master.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_master.config( font = config.font_checkbox )

  def make_ptrAccessions(self, p_row=0, p_column=0):
    #Protein Accessions checkbox
    self.var_chc_ptrAccessions = IntVar(value=0)
    self.chc_ptrAccessions = tk.Checkbutton(self.frame_right, text='Show Protein Accessions', width=32, anchor="w", variable=self.var_chc_ptrAccessions, onvalue=1, offvalue=0)
    self.chc_ptrAccessions.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_ptrAccessions.config( font = config.font_checkbox )

  def make_normalized(self, p_row=0, p_column=0):
    #Normalized checkbox
    self.var_chc_normalized = IntVar(value=0)
    self.chc_normalized = tk.Checkbutton(self.frame_right, text='Select normalized abundances', width=32, anchor="w", variable=self.var_chc_normalized, onvalue=1, offvalue=0, command=self.normalized_control )
    self.chc_normalized.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_normalized.config( font = config.font_checkbox )

  def make_re_normalized(self, p_row=0, p_column=0, p_text='Re Normalized'):
    #Re-Normalized checkbox
    self.var_chc_re_normalized = IntVar(value=0)
    self.chc_re_normalized = tk.Checkbutton(self.frame_right, text=p_text, width=32, anchor="w", variable=self.var_chc_re_normalized, onvalue=1, offvalue=0, command=self.normalized_control )
    self.chc_re_normalized.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_re_normalized.config( font = config.font_checkbox )

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
          #take the df
          self.df = thread.df
          #read it to create some button in the window and mark if the file is load
          self.isFileLoad = self.manage_the_upload()
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

  def manage_the_upload(self):
    #controlli per selezionare le colonne indispensabili per il coretto funzionamento delle diverse tipologie di file
    if(MyUtility.workDict['input_type'] == 'proteome'):
      #find all abundances columns
      abundances_columns = list(self.df.filter(regex = 'Abundance:')) + list(self.df.filter(regex = '(Normalized)'))

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

      #create a valid list of columns and add abundaces columns
      valid_columns = valid_columns + abundances_columns

      #in the df keep only the useful columns
      self.df = self.df.filter(items=valid_columns)

    #check if the df_columns cointains all valid columns, otherwise return an error message and exit from method
    check = all(item in self.df.columns for item in valid_columns)
    if(not check):
      self.isFileLoad = False
      self.lbl_loadedFile['text'] = "No file"
      tk.messagebox.showerror(parent=self, title="Error", message="Incompatible columns in uploaded file")
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
        #remove all previous checkbox
        self.scl_check_quantInfo.removeAllCheckbox()
        #mostro il frame
        self.frame_quanInfo.grid()

        #get quant as value and put in a list
        quanList = self.df['Quan Info'].dropna().unique()
        quanList = quanList.tolist()

        #reorder marker
        quanList.sort()
        #if need put empty element in top
        if(np.nan in quanList):
          #move empty value on top of the list
          quanList.insert(0, quanList.pop(quanList.index("Empty")))

        #pass list to create checkbox
        self.scl_check_quantInfo.insertCheckbox(quanList)

        #scroll to top
        self.scl_check_quantInfo.scroll_to_top()

        #deselect all check
        self.scl_check_quantInfo.deselectAllCheckbox()
    #Description
    if( hasattr(self, 'frame_description') ):
      column_name = ''
      if(MyUtility.workDict['mode'] == 'Proteins'):
        column_name = 'Description'
      else:
        column_name = 'Master Protein Descriptions'
      if(column_name not in self.df.columns):
        self.frame_description.grid_remove()
      else:
        self.frame_description.grid()
    #Marker
    if( hasattr(self, 'frame_marker') ):
      if('Marked as' not in self.df.columns):
        self.frame_marker.grid_remove()
      else:  
        #remove previous checkbox
        self.scl_check_marker.removeAllCheckbox()
        #show elements
        self.frame_marker.grid()

        #get MarkedAs as value and put in a list
        markedList = self.df['Marked as'].unique()
        markedList = markedList.tolist()

        # find the index of Rahul
        if(np.nan in markedList):
          #get nan index
          nan_index = markedList.index(np.nan)
          #replace nan with another significative string
          markedList[nan_index] = "Empty"
        #reorder marker
        markedList.sort()
        #if need put empty element in top
        if(np.nan in markedList):
          #move empty value on top of the list
          markedList.insert(0, markedList.pop(markedList.index("Empty")))

        #pass list to create checkbox
        self.scl_check_marker.insertCheckbox(markedList)

        #scroll to top
        self.scl_check_marker.scroll_to_top()
    #Valid values (for number of elements)
    if( hasattr(self, 'frame_validValues') ):
      if(MyUtility.workDict['input_type'] == 'proteome' ):
        num_abundance = sum(['Abundance:' in col for col in self.df.columns])
        num_normalized = sum(['(Normalized):' in col for col in self.df.columns])
        if(num_abundance > 0) and (num_normalized > 0):
          abundances_divisor = 2
        else:
          abundances_divisor = 1
      else:
        abundances_divisor = 1

      #add number of aboundance columns
      self.num_abundance_tot = int((len(list(self.df.filter(regex=r'F\d+'))))/abundances_divisor)
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

    return True

  def upload_file(self):
    #ask file name
    if(MyUtility.workDict['input_type'] == 'proteome'):
      filepath = filedialog.askopenfilename(parent=self, title="Open",filetypes=config.file_types)
    else:
      filepath = filedialog.askopenfilename(parent=self, title="Open", filetypes=[("mzTab", "*.mzTab")])

    #check if a file has been chosen
    if filepath:
      #load the name of file in label (if name is too long then resize it)
      tmp_path = os.path.basename(filepath)
      if(len(tmp_path)>25):
        tmp_path = tmp_path[:25] + "..."
      self.lbl_loadedFile['text'] = tmp_path
      #self.lbl_loadedFile['text'] = os.path.basename(filepath)

      #show loading windows
      self.winLoad = wLd.LoadingWindow("Uploading file...")

      #create thread to load file
      if(MyUtility.workDict["input_type"]=='proteome'):
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
      file_path = filedialog.asksaveasfilename(parent=self, filetypes=config.file_types, defaultextension=".xlsx")

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
    MyUtility.workDict["fill0"] = self.var_chc_fill_zero.get()

    #hide this window
    self.withdraw()
    #create new window
    self.windowTaxonomicMenu = wTxMn.TaxonomicMenuWindow(self.wn_root, self, self.df_tmp)

'''
if __name__ == "__main__":
  app = ProteinsWindow()
  app.mainloop()
'''