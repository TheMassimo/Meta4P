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
#import next window (if there is aggregation)
import WindowSummaryMetricsPost as wSMpst
#import next window (if there is not aggregation)
import WindowRenameColumns as wRC

#import prefix and sufix window
import WindowNameExtension as wNE

class AggregationWindow(tk.Toplevel): #tk.Tk):
  def __init__(self, wn_root, wn_previous, previousDf):
    super().__init__()

    #change icon
    img = PhotoImage(file=resource_path(config.icon))
    self.iconphoto(False, img)

    #take the root window
    self.wn_root = wn_root
    #take the previous window
    self.wn_previous = wn_previous

    #take the old df
    self.df = previousDf;

    # configure the root window
    self.title('Data aggregation')

    #for Entry widget
    self.vcmd = (self.register(self.onValidate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

    #fixed list to use with proteome
    #if(MyUtility.workDict['taxonomic_mode'] == 'dynamic'):
    if 'taxonomic_table' in MyUtility.workDict:
      self.list_taxonomic = MyUtility.workDict['taxonomic_table']
    else:
      self.list_taxonomic = []

    if 'functional_table' in MyUtility.workDict:
      if(MyUtility.workDict['functional_mode'] == 'dynamic'):
        self.list_functional             = MyUtility.workDict['functional_table']
        self.list_functional_to_display = []
        for item in self.list_functional:
          if item.startswith('KEGG'):
            # sostituisci '_' con uno spazio e converti la parola successiva in minuscolo
            new_item = ' '.join([s.lower() if i == 1 else s for i, s in enumerate(item.split('_'))])
          else:
            new_item = item
          self.list_functional_to_display.append(new_item)
      else:
        self.list_functional            = MyUtility.workDict['functional_table'] 
        self.list_functional_to_display = MyUtility.workDict['functional_to_display']
    else:
      self.list_functional            = []
      self.list_functional_to_display = []
    
    ### left area ###
    #Load/download frame
    self.frame_left = tk.Frame(self, borderwidth=2, relief='flat')
    self.frame_left.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

    #Choose Taxonomic label
    self.lbl_chooseTaxonomic = tk.Label(self.frame_left, text='Taxonomic levels', width=20, font=config.font_title)  
    self.lbl_chooseTaxonomic.grid(row=0, column=0, padx=6, pady=6)
    if(MyUtility.workDict["taxonomic"]):
      #Load/download frame
      self.frame_taxonomic_buttons = tk.Frame(self.frame_left, borderwidth=0, relief='flat')
      self.frame_taxonomic_buttons.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")
      #select all checkbox
      self.btn_taxonomic_all = tk.Button(self.frame_taxonomic_buttons, text='Select all', font=config.font_button, width=11)
      self.btn_taxonomic_all.grid(row=0, column=0, padx=20, pady=5)
      #select none checkbox
      self.btn_taxonomic_none = tk.Button(self.frame_taxonomic_buttons, text='Deselect all', font=config.font_button, width=11)
      self.btn_taxonomic_none.grid(row=0, column=1, padx=0, pady=5)

      #taxonomic scroll
      self.scl_check_taxonomic = MyUtility.CheckboxList(self.frame_left, bg="grey", padx=1, pady=1, height=360)
      self.scl_check_taxonomic.grid(row=2,column=0, rowspan=4)
      #pass list to create checkbox
      self.scl_check_taxonomic.insertCheckbox(self.list_taxonomic)

      #add function to select all or deselect all
      self.btn_taxonomic_all.config(command=self.scl_check_taxonomic.selectAllCheckbox)
      self.btn_taxonomic_none.config(command=self.scl_check_taxonomic.deselectAllCheckbox)
    else:
      self.lbl_noTaxonomic = tk.Label(self.frame_left, text='No annotations', width=20, font=config.font_up_base)  
      self.lbl_noTaxonomic.grid(row=1, column=0, padx=5, pady=5)

    #Choose Functional label
    self.lbl_chooseFunctional = tk.Label(self.frame_left, text='Functional levels', font=config.font_title)  
    self.lbl_chooseFunctional.grid(row=0, column=1, padx=6, pady=6)
    if(MyUtility.workDict["functional"]):
      #Load/download frame
      self.frame_functional_buttons = tk.Frame(self.frame_left, borderwidth=0, relief='flat')
      self.frame_functional_buttons.grid(row=1, column=1, padx=2, pady=2, sticky="nsew")
      #select all checkbox
      self.btn_functional_all = tk.Button(self.frame_functional_buttons, text='Select all', font=config.font_button, width=11)
      self.btn_functional_all.grid(row=0, column=0, padx=12, pady=5)
      #select none checkbox
      self.btn_functional_none = tk.Button(self.frame_functional_buttons, text='Deselect all', font=config.font_button, width=11)
      self.btn_functional_none.grid(row=0, column=1, padx=0, pady=5)

      #functional scroll
      self.scl_check_functional = MyUtility.CheckboxList(self.frame_left, bg="grey", padx=1, pady=1, height=360)
      self.scl_check_functional.grid(row=2,column=1, rowspan=4)
      #pass list to create checkbox
      self.scl_check_functional.insertCheckbox(self.list_functional_to_display)

      #add function to select all or deselect all
      self.btn_functional_all.config(command=self.scl_check_functional.selectAllCheckbox)
      self.btn_functional_none.config(command=self.scl_check_functional.deselectAllCheckbox)

      #control for online reserch of kegg code
      #label title
      self.lbl_keggOnline = tk.Label(self.frame_left, text='Retrieve KEGG name', width=20, font=config.font_kegg_title)  
      self.lbl_keggOnline.grid(row=6, column=1, padx=6, pady=6)
      #label description
      self.lbl_keggOnline_info = tk.Label(self.frame_left, text='(working internet connection needed)', width=30, font=config.font_info)  
      self.lbl_keggOnline_info.grid(row=7, column=1, padx=6, pady=0)
      #checkbox
      self.var_chcs_kegg = IntVar(value=1)
      self.chcs_kegg = tk.Checkbutton(self.frame_left, text="yes", width=20, anchor="w", variable=self.var_chcs_kegg, onvalue=1, offvalue=0)
      self.chcs_kegg.grid(row=8, column=1, padx=(50,0), pady=5)
      self.chcs_kegg.select()
      self.chcs_kegg.config( font = config.font_checkbox )
    else:
      self.lbl_noFunctional = tk.Label(self.frame_left, text='No annotations', width=20, font=config.font_up_base)  
      self.lbl_noFunctional.grid(row=1, column=1, padx=5, pady=5)
    

    ### centre area ###
    #title frame    
    self.frame_centre = tk.Frame(self, borderwidth=2, relief='flat')
    self.frame_centre.grid(row=0, column=1, padx=2, pady=2,sticky="nsew")

    #Choose Union label
    self.lbl_chooseUnion = tk.Label(self.frame_centre, text='Taxon-specific function', width=40, font=config.font_title)  
    self.lbl_chooseUnion.grid(row=0, column=0, columnspan=3, sticky='EW', padx=6, pady=6 )
    #check if there are both the annotaion 
    if(MyUtility.workDict["taxonomic"] and MyUtility.workDict["functional"]):
      #option to taxonomic
      self.opt_taxonomic_var = StringVar(value=self.list_taxonomic[0]) # dafault value
      self.opt_taxonomic = tk.OptionMenu(self.frame_centre, self.opt_taxonomic_var, *self.list_taxonomic)
      self.opt_taxonomic.grid(row=1, column=0, padx=10, pady=6, sticky='n')
      self.opt_taxonomic.config(width=18)
      self.opt_taxonomic.config(font = config.font_checkbox )

      #option to functional
      self.opt_functional_var = StringVar(value=self.list_functional_to_display[0]) # dafault value
      self.opt_functional = tk.OptionMenu(self.frame_centre, self.opt_functional_var, *self.list_functional_to_display)
      self.opt_functional.grid(row=1, column=1, padx=10, pady=6, sticky='n')
      self.opt_functional.config(width=18)
      self.opt_functional.config( font = config.font_checkbox )

      #Create frame and scrollbar
      self.my_frame = Frame(self.frame_centre, bg='red',)
      self.my_frame.grid(row=2, column=0, rowspan=4, columnspan=2, sticky='n')
      #scrollbar
      self.my_scrollbar = Scrollbar(self.my_frame,  orient=VERTICAL)
      #Listbox
      #SINGLE, BROWSE, MULTIPLE, EXTENDED
      self.my_listbox = Listbox(self.my_frame, yscrollcommand=self.my_scrollbar.set, selectmode=EXTENDED) #background="Blue", fg="white", selectbackground="Red",highlightcolor="Red",
      self.my_listbox.grid(row=0, column=0)
      self.my_listbox.config(width=55, height=12)
      #configure scrollvar
      self.my_scrollbar.config(command=self.my_listbox.yview)
      self.my_scrollbar.grid(row=0, column=1, sticky="NS")

      #Add button
      self.btn_add = tk.Button(self.frame_centre, text='Add', font=config.font_button, width=18, command=self.add_element)
      self.btn_add.grid(row=2, column=2, padx=10, pady=6, sticky='n')

      #Add All button
      self.btn_add_all = tk.Button(self.frame_centre, text='Add All', font=config.font_button, width=18, command=self.add_all_elements)
      self.btn_add_all.grid(row=3, column=2, padx=10, pady=6, sticky='n')
      
      #Remove button
      self.btn_remove = tk.Button(self.frame_centre, text='Remove', font=config.font_button, width=18, command=self.remove_element)
      self.btn_remove.grid(row=4, column=2, padx=10, pady=6, sticky='n')

      #Remove All button
      self.btn_remove_all = tk.Button(self.frame_centre, text='Remove all', font=config.font_button, width=18, command=self.remove_all_alement)
      self.btn_remove_all.grid(row=5, column=2, padx=10, pady=6, sticky='n')
    else:
      #Choose Union label
      self.lbl_noAnnotation = tk.Label(self.frame_centre, text='Not enough annotations', width=36, font=config.font_up_base)  
      self.lbl_noAnnotation.grid(row=1, column=0, columnspan=3, sticky='EW', padx=6, pady=6 )


    ### right area ###
    #Options frame
    self.frame_right = tk.Frame(self, borderwidth=2, relief='flat')
    self.frame_right.grid(row=0, column=2, padx=2, pady=2, sticky="nsew")

    #chek if there are at least one annotation file
    if(MyUtility.workDict["taxonomic"] or MyUtility.workDict["functional"]):
      #option to extra table download
      self.lbl_sup_tab = tk.Label(self.frame_right, text='Feature-related peptide counts',width=25,font=config.font_title)
      self.lbl_sup_tab.grid(row=0, column=0, padx=6, pady=6)

      #checkbox text according to start choose
      box_text = "Export separate tables\n(with single sample and total peptide counts)"
      if(MyUtility.workDict["mode"] == 'Proteins'):
        box_text = "Export separate tables\n(with single sample and total protein counts)"
      #checkbox for choose if download extra tables
      self.var_chcs_sup = IntVar(value=0)
      self.chcs_sup = tk.Checkbutton(self.frame_right, text=box_text, width=25, wraplength=200, anchor="w", variable=self.var_chcs_sup, onvalue=1, offvalue=0)
      self.chcs_sup.config(font = config.font_checkbox )
      self.chcs_sup.grid(row=1, column=0, padx=5, pady=5)

      #checkbox for extra column in results
      #checkbox text according to start choose
      box_text = "Insert a supplementary column\nin all tables\n(with total peptide counts)"
      if(MyUtility.workDict["mode"] == 'Proteins'):
        box_text = "Insert a supplementary column\nin all tables\n(with total protein counts)"
      self.var_chcs_counts_col = IntVar(value=0)
      self.chcs_counts_col = tk.Checkbutton(self.frame_right, text=box_text, width=25, wraplength=200, anchor="w", variable=self.var_chcs_counts_col, onvalue=1, offvalue=0, command=self.change_extra_counts_col)
      self.chcs_counts_col.config(font = config.font_checkbox )
      self.chcs_counts_col.grid(row=2, column=0, padx=5, pady=5)
      #save start status
      MyUtility.workDict["extra_counts_col"] = self.var_chcs_counts_col.get()      

      #checkbox for choose if filter the counts
      #checkbox text according to start choose
      box_text = "Filter features (rows) based\non the related peptide counts"
      if(MyUtility.workDict["mode"] == 'Proteins'):
        box_text = "Filter features (rows) based\non the related protein counts"
      self.var_chcs_filter_count = IntVar(value=0)
      self.chcs_filter_count = tk.Checkbutton(self.frame_right, text=box_text, width=25, wraplength=200, anchor="w", variable=self.var_chcs_filter_count, onvalue=1, offvalue=0, command=self.counts_filter_control)
      self.chcs_filter_count.config(font = config.font_checkbox )
      self.chcs_filter_count.grid(row=3, column=0, padx=5, pady=5)
      #save start status
      MyUtility.workDict["counts_col"] = self.var_chcs_filter_count.get()

      #Entry for quantity of filter
      self.ntr_filter_counts = tk.Entry(self.frame_right, width=20, validate="key", validatecommand=self.vcmd)
      self.ntr_filter_counts.insert(0, "0")
      self.ntr_filter_counts.grid(row=4, column=0, padx=5, pady=5)
      self.ntr_filter_counts.configure(state='disabled')

      #quantity filter info
      #checkbox text according to start choose
      box_text = "(min. number of peptides)"
      if(MyUtility.workDict["mode"] == 'Proteins'):
        box_text = "(min. number of protein)"
      self.lbl_abundanceTot = tk.Label(self.frame_right, text=box_text, width=20, font=config.font_description)
      self.lbl_abundanceTot.grid(row=5, column=0, padx=5, pady=(0,5))

      #Download button
      self.btn_remove_all = tk.Button(self.frame_right, text='Download table(s)', font=config.font_button, width=18, command=self.pre_download)
      self.btn_remove_all.grid(row=6, column=0, rowspan=2, padx=10, pady=(40,6))

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

    #create variable for prefix and sufix of futere download
    self.prefix = ""
    self.suffix = ""

    #put this window up
    self.lift()

    #when I close window
    self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
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

  def monitor_download(self, thread):
    if thread.is_alive():
      #check the thread every 100ms
      self.after(100, lambda: self.monitor_download(thread))
    else:
      if(not thread.internetWork):
        tk.messagebox.showerror(parent=self, title="Error", message="Internet problems")
      #delete load window
      self.winLoad.destroy()
      #put window in front
      self.lift()
      #a questo punto avrò anche metrics_df
      if(not thread.fileSaved):
        tk.messagebox.showerror(parent=self, title="Error", message="One or more files not saved\nThey are probably in use by another program")

  def add_element(self):
    #string to insert
    my_string = self.opt_taxonomic_var.get() +"+"+ self.opt_functional_var.get()
    #check if alredy insert
    iscontain = my_string in self.my_listbox.get(0, "end")
    if(iscontain):
      tk.messagebox.showerror(parent=self, title="Error", message="These values have already been entered")
    else:
      self.my_listbox.insert(END, my_string)

  def add_all_elements(self):
    #loop for insert all combination
    for tmp_tax in self.list_taxonomic:
      for tmp_fun in self.list_functional_to_display:
        #string to insert
        my_string = tmp_tax+"+"+tmp_fun
        #check if alredy insert
        iscontain = my_string in self.my_listbox.get(0, "end")
        if(not iscontain):
          self.my_listbox.insert(END, my_string)

  def remove_element(self):
    #delete all select elment from list
    #self.my_listbox.delete(ANCHOR)
    for item in reversed(self.my_listbox.curselection()):
      self.my_listbox.delete(item)

  def remove_all_alement(self):
    #delete all element from list
    self.my_listbox.delete(0, END)

  def counts_filter_control(self):
    # Change value according to checkbox
    MyUtility.workDict["counts_col"] = self.var_chcs_filter_count.get()
    # Change entry status
    if(self.var_chcs_filter_count.get() == 1):
      self.ntr_filter_counts.configure(state='normal')
    else:
      self.ntr_filter_counts.configure(state='disabled')

  def change_extra_counts_col(self):
    #change value according to checkbox
    MyUtility.workDict["extra_counts_col"] = self.var_chcs_counts_col.get()

  def create_list(self):
    #create empty list
    my_list = []
    #Fill list to taxonomic
    if(MyUtility.workDict["taxonomic"]):
      for i in range(0, len(self.list_taxonomic)):
        if(self.scl_check_taxonomic.var_chcs[i].get()):
          #create list
          inside_list = []
          #get column name and insert inside the "inside_list"
          inside_list.append(self.list_taxonomic[i])
          #insert "inside_list" inside "my_list"
          my_list.append(inside_list)

    #Fill list to functional
    if(MyUtility.workDict["functional"]):
      for i in range(0, len(self.list_functional)):
        if(self.scl_check_functional.var_chcs[i].get()):
          #create list
          inside_list = []
          #get column name and insert inside the "inside_list"
          inside_list.append(self.list_functional[i])
          #insert "inside_list" inside "my_list"
          my_list.append(inside_list)

    #Fill list to Union
    if((MyUtility.workDict["taxonomic"]) and (MyUtility.workDict["functional"])):
      #get all element from listbox
      get_content = self.my_listbox.get(0, END)
      #read and elaborate all elments in listbox
      for con_item in get_content:
        #create list
        inside_list = []
        #split and pass to 2 different position of inside_list
        col_1, col_2 = con_item.split('+')

        #get the right name of coloumn
        name_index = self.list_functional_to_display.index(col_2)
        col_2 = self.list_functional[name_index]

        #add this elements to list
        inside_list.extend([col_1, col_2])
        #insert "inside_list" inside "my_list"
        my_list.append(inside_list)


    return my_list

  def pre_download(self):
    #reset prefix and suffix value
    self.prefix = ""
    self.suffix = ""
    #create windows to show extra information for prefix and sufix of files_name
    self.winNameExt = wNE.NameExtensionWindow(self)

  def download(self):
    #ask position to save all file
    file_path = filedialog.asksaveasfilename(parent=self,
                                             filetypes=config.file_types,
                                             defaultextension=".xlsx",
                                             initialfile="Filenames will be generated automatically, just choose the folder and file extension")

    #check if a file has been chosen
    if file_path:
      #invoke function to manage data before export
      my_list = self.create_list()

      #show loading windows
      self.winLoad = wLd.LoadingWindow("Downloading file(s)...")

      #create thread to download file
      #get kegg online checkbox value
      keggOnline = False
      if(MyUtility.workDict["functional"]):
        keggOnline = self.var_chcs_kegg.get()
      #get Supplementary tables online checkbox value
      sup_tab = False
      if(MyUtility.workDict["taxonomic"] or MyUtility.workDict["functional"]):
        sup_tab = self.var_chcs_sup.get()

      #check if entry for minimu peptides or proteins count is valid
      if(not self.ntr_filter_counts.get().isdigit()):
        self.ntr_filter_counts.insert(0, "0")

      #create a dictionary to pass
      params = {
        "keggOnline": keggOnline,
        "sup_tab": sup_tab,
        "mode": MyUtility.workDict["mode"],
        "fill0": MyUtility.workDict["fill0"],
        "extra_counts_col": MyUtility.workDict["extra_counts_col"],
        "counts_col": MyUtility.workDict["counts_col"],
        "min_counts": int(self.ntr_filter_counts.get()),
        "prefix": self.prefix,
        "suffix": self.suffix
      }

      #create thread and start it
      download_thread = AsyncDownload_Aggregation(self, self.df, my_list, params, file_path)
      download_thread.start()
      self.monitor_download(download_thread)
    else:
      tk.messagebox.showerror(parent=self, title="Error", message="No directory selected")

  def previous_window(self):
    #hide this window
    #self.withdraw()
    #Destroy this window
    self.destroy()

    #show last window
    self.wn_previous.deiconify()
    self.wn_previous.lift()

  def next_window(self):
    #hide this window
    self.withdraw()

    if( hasattr(self, 'metrics_df') and (len(self.create_list()) > 0) ):
      #create new window for renaming
      self.windowSummaryMetricsPost = wSMpst.SummaryMetricsPostWindow(self.wn_root, self, self.metrics_df)
    else:
      #create new window for renaming
      self.windowRC = wRC.RenameColumnsWindow(self.wn_root, self)



'''
if __name__ == "__main__":
  app = AggregationWindow()
  app.mainloop()
'''