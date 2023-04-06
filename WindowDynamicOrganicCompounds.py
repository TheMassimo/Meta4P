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

class DynamicOrganicCompoundsWindow(tk.Toplevel): #tk.Tk):
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

    #title of editing
    self.lbl_fileter = tk.Label(self.frame_centre,text='Column selection - '+MyUtility.workDict["mode"],width=20,font=config.font_title)  
    self.lbl_fileter.grid(row=0, column=0, columnspan=2, padx=6, pady=6, sticky='ew')

    #riquadro con le colonne da scegliere
    self.make_columnsHeaders(p_row=1, p_column=0, p_rowspan=1, p_sticky='n')

    if(MyUtility.workDict['mode'] == 'Proteins'):
      self.make_proteinAccession(p_row=1, p_column=1, p_sticky='n')
      self.make_abundanceValue(p_row=2, p_column=1, p_sticky='n')
      self.make_otherInfo(p_row=3, p_column=1, p_sticky='n')
      self.frame_columnsHeaders.grid(rowspan=3)
    elif(MyUtility.workDict['mode'] == 'Peptides'):
      self.make_peptideSequence(p_row=1, p_column=1, p_sticky='n')
      self.make_proteinAccession(p_row=2, p_column=1, p_sticky='n')
      self.make_abundanceValue(p_row=3, p_column=1, p_sticky='n')
      self.make_otherInfo(p_row=4, p_column=1, p_sticky='n')
      self.frame_columnsHeaders.grid(rowspan=4)
    elif(MyUtility.workDict['mode'] == 'PSMs'):
      self.make_peptideSequence(p_row=1, p_column=1, p_sticky='n')
      self.make_proteinAccession(p_row=2, p_column=1, p_sticky='n')
      self.make_sampleID(p_row=3, p_column=1, p_sticky='n')
      self.make_otherInfo(p_row=4, p_column=1, p_sticky='n')
      self.frame_columnsHeaders.grid(rowspan=4)

    ### right area ###
    #Fileter and Options frame
    self.frame_right = tk.Frame(self, borderwidth=2, relief='flat')
    self.frame_right.grid(row=0, column=2, padx=2, pady=2, sticky="nsew")

    #Fileter
    if( (MyUtility.workDict['mode'] == 'Proteins') or (MyUtility.workDict['mode'] == 'Peptides') ):
      fileter_text = MyUtility.workDict["mode"]
      if(fileter_text != "PSMs"):
        fileter_text = fileter_text.lower()
      self.lbl_fileter = tk.Label(self.frame_right,text='Filter '+fileter_text+' based on',width=20,font=config.font_title)  
      self.lbl_fileter.grid(row=0, column=0, columnspan=1, padx=6, pady=6, sticky='ew')

      #create frame for abundance values
      self.make_validValues(p_row=1, p_column=0, p_sticky='n')

    #Option label
    self.lbl_options = tk.Label(self.frame_right,text='Options',width=32,font=config.font_title)  
    self.lbl_options.grid(row=2, column=0, padx=6, pady=6)

    self.make_fill_zero(p_row=3)
    if(MyUtility.workDict['mode'] != 'PSMs'):
      self.make_re_normalized(p_row=5, p_text='Normalize abundances (after filtering)')


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

    #put this window up
    self.lift()

    #when I close window
    self.protocol("WM_DELETE_WINDOW", self.on_closing)

  ### Functions to create frame for choose columns ###
  def make_columnsHeaders(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #Columns Headers frame
    self.frame_columnsHeaders = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_columnsHeaders.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)

    #title of select column area
    self.lbl_columnHeaders = tk.Label(self.frame_columnsHeaders, text='Column headers', width=32, font=config.font_subtitle )  
    self.lbl_columnHeaders.grid(row=0, column=0, padx=6, pady=6)

    #Create frame and scrollbar
    self.all_columns_frame = Frame(self.frame_columnsHeaders)#, bg='red')
    self.all_columns_frame.grid(row=1, column=0, rowspan=1)
    #scrollbar
    self.all_columns_scrollbar = Scrollbar(self.all_columns_frame,  orient=VERTICAL)
    #Listbox
    #SINGLE, BROWSE, MULTIPLE, EXTENDED
    self.all_columns_listbox = Listbox(self.all_columns_frame, yscrollcommand=self.all_columns_scrollbar.set, selectmode=EXTENDED) #background="Blue", fg="white", selectbackground="Red",highlightcolor="Red",
    self.all_columns_listbox.grid(row=0, column=0)
    self.all_columns_listbox.config(width=40, height=30)
    #configure scrollvar
    self.all_columns_scrollbar.config(command=self.all_columns_listbox.yview)
    self.all_columns_scrollbar.grid(row=0, column=1, sticky="NS")

  def make_proteinAccession(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #protein Accession frame
    self.frame_proteinAccession = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_proteinAccession.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)

    #title of select column area
    self.lbl_proteinAccession = tk.Label(self.frame_proteinAccession, text='Protein accession', width=32, font=config.font_subtitle )  
    self.lbl_proteinAccession.grid(row=0, column=0, columnspan=2, padx=6, pady=6)

    #button select >
    self.btn_take_proteinAccession = tk.Button(self.frame_proteinAccession, text='>', font=config.font_button,
                                               width=2, command=lambda: self.take_column(self.proteinAccession_listbox))
    self.btn_take_proteinAccession.grid(row=1, column=0, padx=1, pady=1)
    #button unselect <
    self.btn_restore_proteinAccession = tk.Button(self.frame_proteinAccession, text='<', font=config.font_button,
                                                  width=2, command=lambda: self.restore_column(self.proteinAccession_listbox))
    self.btn_restore_proteinAccession.grid(row=2, column=0, padx=1, pady=1)

    #Create frame and scrollbar
    self.all_proteinAccession = Frame(self.frame_proteinAccession)#, bg='red')
    self.all_proteinAccession.grid(row=1, column=1, rowspan=2, padx=1, pady=1)
    #scrollbar
    self.proteinAccession_scrollbar = Scrollbar(self.all_proteinAccession,  orient=VERTICAL)
    #Listbox
    #SINGLE, BROWSE, MULTIPLE, EXTENDED
    self.proteinAccession_listbox = Listbox(self.all_proteinAccession, yscrollcommand=self.proteinAccession_scrollbar.set, selectmode=EXTENDED) #background="Blue", fg="white", selectbackground="Red",highlightcolor="Red",
    self.proteinAccession_listbox.grid(row=0, column=0)
    self.proteinAccession_listbox.config(width=40, height=5)
    #configure scrollvar
    self.proteinAccession_scrollbar.config(command=self.proteinAccession_listbox.yview)
    self.proteinAccession_scrollbar.grid(row=0, column=1, sticky="NS")

  def make_abundanceValue(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #protein Accession frame
    self.frame_abundanceValue = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_abundanceValue.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)

    #title of select column area
    self.lbl_abundanceValue = tk.Label(self.frame_abundanceValue, text='Abundance values', width=32, font=config.font_subtitle )  
    self.lbl_abundanceValue.grid(row=0, column=0, columnspan=2, padx=6, pady=(6,1))

    #label info
    self.lbl_abundanceValue_info = tk.Label(self.frame_abundanceValue, text='Abundance column headers will be sequentially\nrenamed according to the following nomenclature:\n"Abundance F1", "Abundance F2", etc. ',
                                            width=30, font=config.font_info)  
    self.lbl_abundanceValue_info.grid(row=1, column=0, columnspan=2, padx=1, pady=1, sticky='ew')

    #button select >
    self.btn_take_abundanceValue = tk.Button(self.frame_abundanceValue, text='>', font=config.font_button,
                                             width=2, command=lambda: self.take_column(self.abundanceValue_listbox))
    self.btn_take_abundanceValue.grid(row=2, column=0, padx=1, pady=1)
    #button unselect <
    self.btn_restore_abundanceValue = tk.Button(self.frame_abundanceValue, text='<', font=config.font_button,
                                                width=2, command=lambda: self.restore_column(self.abundanceValue_listbox))
    self.btn_restore_abundanceValue.grid(row=3, column=0, padx=1, pady=1)

    #Create frame and scrollbar
    self.all_abundanceValue = Frame(self.frame_abundanceValue)#, bg='red')
    self.all_abundanceValue.grid(row=2, column=1, rowspan=2, padx=1, pady=1)
    #scrollbar
    self.proteinAccession_scrollbar = Scrollbar(self.all_abundanceValue,  orient=VERTICAL)
    #Listbox
    #SINGLE, BROWSE, MULTIPLE, EXTENDED
    self.abundanceValue_listbox = Listbox(self.all_abundanceValue, yscrollcommand=self.proteinAccession_scrollbar.set, selectmode=EXTENDED) #background="Blue", fg="white", selectbackground="Red",highlightcolor="Red",
    self.abundanceValue_listbox.grid(row=0, column=0)
    self.abundanceValue_listbox.config(width=40, height=5)
    #configure scrollvar
    self.proteinAccession_scrollbar.config(command=self.abundanceValue_listbox.yview)
    self.proteinAccession_scrollbar.grid(row=0, column=1, sticky="NS")

  def make_otherInfo(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #protein Accession frame
    self.frame_otherInfo = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_otherInfo.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)

    #title of select column area
    self.lbl_otherInfo = tk.Label(self.frame_otherInfo, text='Other Info', width=32, font=config.font_subtitle )  
    self.lbl_otherInfo.grid(row=0, column=0, columnspan=2, padx=6, pady=6)

    #button select >
    self.btn_take_otherInfo = tk.Button(self.frame_otherInfo, text='>', font=config.font_button, width=2, command=lambda: self.take_column(self.otherInfo_listbox))
    self.btn_take_otherInfo.grid(row=1, column=0, padx=1, pady=1)
    #button unselect <
    self.btn_restore_otherInfo = tk.Button(self.frame_otherInfo, text='<', font=config.font_button, width=2, command=lambda: self.restore_column(self.otherInfo_listbox))
    self.btn_restore_otherInfo.grid(row=2, column=0, padx=1, pady=1)

    #Create frame and scrollbar
    self.all_otherInfo = Frame(self.frame_otherInfo)#, bg='red')
    self.all_otherInfo.grid(row=1, column=1, rowspan=2, padx=1, pady=1)
    #scrollbar
    self.otherInfo_scrollbar = Scrollbar(self.all_otherInfo,  orient=VERTICAL)
    #Listbox
    #SINGLE, BROWSE, MULTIPLE, EXTENDED
    self.otherInfo_listbox = Listbox(self.all_otherInfo, yscrollcommand=self.otherInfo_scrollbar.set, selectmode=EXTENDED) #background="Blue", fg="white", selectbackground="Red",highlightcolor="Red",
    self.otherInfo_listbox.grid(row=0, column=0)
    self.otherInfo_listbox.config(width=40, height=5)
    #configure scrollvar
    self.otherInfo_scrollbar.config(command=self.otherInfo_listbox.yview)
    self.otherInfo_scrollbar.grid(row=0, column=1, sticky="NS")
  
  def make_peptideSequence(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #protein Accession frame
    self.frame_peptideSequence = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_peptideSequence.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)

    #title of select column area
    self.lbl_peptideSequence = tk.Label(self.frame_peptideSequence, text='Peptide sequence', width=32, font=config.font_subtitle )  
    self.lbl_peptideSequence.grid(row=0, column=0, columnspan=2, padx=6, pady=6)

    #button select >
    self.btn_take_peptideSequence = tk.Button(self.frame_peptideSequence, text='>', font=config.font_button,
                                              width=2, command=lambda: self.take_column(self.peptideSequence_listbox))
    self.btn_take_peptideSequence.grid(row=1, column=0, padx=1, pady=1)
    #button unselect <
    self.btn_restore_peptideSequence = tk.Button(self.frame_peptideSequence, text='<', font=config.font_button,
                                                 width=2, command=lambda: self.restore_column(self.peptideSequence_listbox))
    self.btn_restore_peptideSequence.grid(row=2, column=0, padx=1, pady=1)

    #Create frame and scrollbar
    self.all_peptideSequence = Frame(self.frame_peptideSequence)#, bg='red')
    self.all_peptideSequence.grid(row=1, column=1, rowspan=2, padx=1, pady=1)
    #scrollbar
    self.peptideSequence_scrollbar = Scrollbar(self.all_peptideSequence,  orient=VERTICAL)
    #Listbox
    #SINGLE, BROWSE, MULTIPLE, EXTENDED
    self.peptideSequence_listbox = Listbox(self.all_peptideSequence, yscrollcommand=self.peptideSequence_scrollbar.set, selectmode=EXTENDED) #background="Blue", fg="white", selectbackground="Red",highlightcolor="Red",
    self.peptideSequence_listbox.grid(row=0, column=0)
    self.peptideSequence_listbox.config(width=40, height=5)
    #configure scrollvar
    self.peptideSequence_scrollbar.config(command=self.peptideSequence_listbox.yview)
    self.peptideSequence_scrollbar.grid(row=0, column=1, sticky="NS")

  def make_sampleID(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #protein Accession frame
    self.frame_sampleID = tk.Frame(self.frame_centre, borderwidth=2, relief='flat')
    self.frame_sampleID.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)

    #title of select column area
    self.lbl_sampleID = tk.Label(self.frame_sampleID, text='Sample ID', width=32, font=config.font_subtitle )  
    self.lbl_sampleID.grid(row=0, column=0, columnspan=2, padx=6, pady=6)

    #button select >
    self.btn_take_sampleID = tk.Button(self.frame_sampleID, text='>', font=config.font_button, width=2,
                                       command=lambda: self.take_column(self.sampleID_listbox))
    self.btn_take_sampleID.grid(row=1, column=0, padx=1, pady=1)
    #button unselect <
    self.btn_restore_sampleID = tk.Button(self.frame_sampleID, text='<', font=config.font_button, width=2,
                                          command=lambda: self.restore_column(self.sampleID_listbox))
    self.btn_restore_sampleID.grid(row=2, column=0, padx=1, pady=1)

    #Create frame and scrollbar
    self.all_sampleID = Frame(self.frame_sampleID)#, bg='red')
    self.all_sampleID.grid(row=1, column=1, rowspan=2, padx=1, pady=1)
    #scrollbar
    self.sampleID_scrollbar = Scrollbar(self.all_sampleID,  orient=VERTICAL)
    #Listbox
    #SINGLE, BROWSE, MULTIPLE, EXTENDED
    self.sampleID_listbox = Listbox(self.all_sampleID, yscrollcommand=self.sampleID_scrollbar.set, selectmode=EXTENDED) #background="Blue", fg="white", selectbackground="Red",highlightcolor="Red",
    self.sampleID_listbox.grid(row=0, column=0)
    self.sampleID_listbox.config(width=40, height=5)
    #configure scrollvar
    self.sampleID_scrollbar.config(command=self.sampleID_listbox.yview)
    self.sampleID_scrollbar.grid(row=0, column=1, sticky="NS")

  ### function to create frame for filter and option ###
  #Function
  def make_validValues(self, p_row=0, p_column=0, p_rowspan=1, p_columnspan=1, p_sticky='nsew'):
    #Valid values frame
    self.frame_validValues = tk.Frame(self.frame_right, borderwidth=2, relief='flat')
    self.frame_validValues.grid(row=p_row, column=p_column, rowspan=p_rowspan, columnspan=p_columnspan, padx=2, pady=2, sticky=p_sticky)
    #Valid values (Abundance label)
    self.lbl_abundance = tk.Label(self.frame_validValues,text='Valid values threshold', width=20, font=config.font_title)  
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

  #Options
  def make_fill_zero(self, p_row=0, p_column=0):
    #Fill with 0 in abundances
    self.var_chc_fill_zero = IntVar(value=0)
    self.chc_fill_zero = tk.Checkbutton(self.frame_right, text='Replace missing values with 0', width=32, anchor="w", variable=self.var_chc_fill_zero, onvalue=1, offvalue=0)
    self.chc_fill_zero.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_fill_zero.config( font = config.font_checkbox )

  def make_re_normalized(self, p_row=0, p_column=0, p_text='Re Normalized'):
    #Re-Normalized checkbox
    self.var_chc_re_normalized = IntVar(value=0)
    self.chc_re_normalized = tk.Checkbutton(self.frame_right, text=p_text, width=32, anchor="w", variable=self.var_chc_re_normalized, onvalue=1, offvalue=0, command=self.normalized_control )
    self.chc_re_normalized.grid(row=p_row, column=p_column, padx=5, pady=5)
    self.chc_re_normalized.config( font = config.font_checkbox )

  #function to choose column in area
  def take_column(self, recipient_listbox):
    #I prevent it from putting more than one element in the Protein Accession or Peptide Sequence or sampleID
    if( (hasattr(self, 'proteinAccession_listbox') and (recipient_listbox == self.proteinAccession_listbox)) or
        (hasattr(self, 'peptideSequence_listbox')  and (recipient_listbox == self.peptideSequence_listbox))  or
        (hasattr(self, 'sampleID_listbox')         and (recipient_listbox == self.sampleID_listbox)) ):
      if(len(self.all_columns_listbox.curselection()) > 1):
        tk.messagebox.showerror(parent=self, title="Error", message="Select only 1 item for this area")
        return
      elif(recipient_listbox.size() > 0):
        tk.messagebox.showerror(parent=self, title="Error", message="This area can only have 1 associated column")
        return

    #Move the elements to the various areas and remove them from the main one
    #remove the elements from the starting listbox
    items_to_move = []
    for index in reversed(self.all_columns_listbox.curselection()):
      #add elemnts to list for recipient listbox
      items_to_move.append(self.all_columns_listbox.get(index))
      #remove element to all columns listbox
      self.all_columns_listbox.delete(index)
    #add elements to recipient listbox
    for el in reversed(items_to_move):
      recipient_listbox.insert(END, el)

    #Update aboundance tot in necessari
    if(hasattr(self, 'abundanceValue_listbox')):
      if(recipient_listbox == self.abundanceValue_listbox):
        self.num_abundance_tot = recipient_listbox.size()
        self.lbl_abundanceTot["text"] = "(# of samples: " + str(self.num_abundance_tot) + " )"

  def restore_column(self, sender_listbox):
    #Move the elements to the various areas and remove them from the main one
    #remove the elements from the starting listbox
    items_to_move = []
    for index in reversed(sender_listbox.curselection()):
      #add elemnts to list for sender listbox
      items_to_move.append(sender_listbox.get(index))
      #remove element to all columns listbox
      sender_listbox.delete(index)
    #add elements to recipient listbox
    for el in reversed(items_to_move):
      self.all_columns_listbox.insert(END, el)

    #Update aboundance tot in necessari
    if(sender_listbox == self.abundanceValue_listbox):
      self.num_abundance_tot = sender_listbox.size()
      self.lbl_abundanceTot["text"] = "(# of samples: " + str(self.num_abundance_tot) + " )"

  def on_closing(self):
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
      self.wn_root.destroy()

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

  def normalized_control(self):
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
        #take the df
        self.df = thread.df
        #read it to create some button in the window and mark if the file is load
        self.isFileLoad = self.manage_the_upload()
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
    #if need clear previous listbox
    if( hasattr(self, 'proteinAccession_listbox') ):
      self.proteinAccession_listbox.delete(0, END)
    if( hasattr(self, 'abundanceValue_listbox') ):
      self.abundanceValue_listbox.delete(0, END)
    if( hasattr(self, 'otherInfo_listbox') ):
      self.otherInfo_listbox.delete(0, END)
    if( hasattr(self, 'peptideSequence_listbox') ):
      self.peptideSequence_listbox.delete(0, END)
    if( hasattr(self, 'sampleID_listbox') ):
      self.sampleID_listbox.delete(0, END)

    #if listbox is not empty then clear all
    if self.all_columns_listbox.size() > 0:
        # rimozione di tutti gli elementi dalla ListBox
        self.all_columns_listbox.delete(0, END)

    #fill_listbox with all columns
    columns = self.df.columns.tolist()
    for column in columns:
      self.all_columns_listbox.insert(END, column)

    return True

  def upload_file(self):
    #ask file name
    filepath = filedialog.askopenfilename(parent=self, title="Open",filetypes=config.file_types)

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
      upload_thread = AsyncUpload(filepath)
      upload_thread.start()
      self.monitor_upload(upload_thread)
    else:
      tk.messagebox.showwarning(parent=self, title="Warning", message="No file selected")

  def proper_round(self, num, dec=0):
    num = str(num)[:str(num).index('.')+dec+2]
    if num[-1]>='5':
        return float(num[:-2-(not dec)]+str(int(num[-2-(not dec)])+1))
    return float(num[:-1])

  def is_value_ok(self):
    #check for abundance
    if( hasattr(self, 'ntr_abundance') ):
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

  def final_checks(self):
    #cotrols to check if the choose columns are good enough
    if( hasattr(self, 'proteinAccession_listbox') ):
      if(self.proteinAccession_listbox.size() != 1):
        tk.messagebox.showerror(parent=self, title="Error", message="Protein Accession must have 1 attribute")
        return False
    if( hasattr(self, 'peptideSequence_listbox') ):
      if(self.peptideSequence_listbox.size() != 1):
        tk.messagebox.showerror(parent=self, title="Error", message="Peptide Sequence must have 1 attribute")
        return False
    if( hasattr(self, 'sampleID_listbox') ):
      if(self.sampleID_listbox.size() != 1):
        tk.messagebox.showerror(parent=self, title="Error", message="SampleID must have 1 attribute")
        return False
    if( hasattr(self, 'abundanceValue_listbox') ):
      if(self.abundanceValue_listbox.size() < 1):
        tk.messagebox.showerror(parent=self, title="Error", message="Abundance Value must have at least 1 attribute")
        return False

    #return true if also value_ok else false
    return self.is_value_ok()

  def download(self):
    #check if file is loadid
    if(self.isFileLoad):
      #Check if value are right
      if(not self.final_checks()):
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
        manage_file_thread = ManageDataDynamic(self)
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
      if(not self.final_checks()):
        return
        
      #show loading windows
      self.winLoad = wLd.LoadingWindow("Managing file...")
      
      #create thread to manage the file
      manage_file_thread = ManageDataDynamic(self)
      manage_file_thread.start()
      self.monitor_manage_file(manage_file_thread, "next_window")
    else:
      tk.messagebox.showerror(parent=self, title="Error", message="No files uploaded")

  def ultimate_next_window(self):
    #Preapre a dict
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