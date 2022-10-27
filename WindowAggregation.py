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
#import my multi threading function to upload and download file
from MyMultiThreading import *

#import loading window
import WindowLoading as wLd
#import next window
import WindowTemplate as wTm

class AggregationWindow(tk.Toplevel): #tk.Tk):
  def __init__(self, wn_root, wn_previous, previousDf, previousDict):
    super().__init__()

    #change icon
    self.iconbitmap("MetaPAnnA_icon.ico")

    #take the root window
    self.wn_root = wn_root
    #take the previous window
    self.wn_previous = wn_previous

    #take the old df
    self.df = previousDf;
    #take the old dict
    self.workDict = previousDict

    '''
    self.workDict = {}
    self.workDict["taxonomic"] = True
    self.workDict["functional"] = True
    '''

    # configure the root window
    self.title('Data aggregation')
    self.geometry('1060x580')

    #fixed list to use
    self.list_taxonomic = ["superkingdom", "phylum", "class", "order", "family", "genus", "species"]
    self.list_functional = ["COG_category", "GOs", "EC", "KEGG_ko", "KEGG_Pathway", "KEGG_Module", "KEGG_Reaction", "CAZy"]

    if(len(self.list_taxonomic) > len(self.list_functional)):
      self.max_row = len(self.list_taxonomic)
    else:
      self.max_row = len(self.list_functional)
      
    #fonts
    self.font_title=('Calibri', 16, 'bold')
    self.font_subtitle=('Calibri', 10)
    self.font_kegg_title=('Calibri', 15, 'bold')
    self.font_up_base = ('Calibri', 12, 'bold')
    self.font_base = ('Calibri', 12)
    self.font_button = ('Calibri', 10)
    self.font_checkbox = ('Calibri', 10)

    #Choose Taxonomic label
    self.lbl_chooseTaxonomic = tk.Label(self, text='Taxonomic levels', width=20, font=self.font_title)  
    self.lbl_chooseTaxonomic.grid(row=0, column=0, padx=6, pady=6)
    if(self.workDict["taxonomic"]):
      i = 0
      self.chcs_taxonomic = []
      self.var_chcs_taxonomic = []
      for x in self.list_taxonomic:
        c = i
        self.var_chcs_taxonomic.append(IntVar(value=0))
        self.chcs_taxonomic.append( tk.Checkbutton(self, text=x, width=20, anchor="w", variable=self.var_chcs_taxonomic[c], onvalue=1, offvalue=0) )
        self.chcs_taxonomic[i].grid(row=(i+2), column=0, padx=(50,0), pady=5)
        self.chcs_taxonomic[i].config( font = self.font_checkbox )
        #self.chcs_taxonomic[i].select()
        i = i+1
    else:
      self.lbl_noTaxonomic = tk.Label(self, text='No annotations', width=20, font=self.font_up_base)  
      self.lbl_noTaxonomic.grid(row=1, column=0, padx=5, pady=5)

    #Choose Functional label
    self.lbl_chooseFunctional = tk.Label(self, text='Functional levels', font=self.font_title)  
    self.lbl_chooseFunctional.grid(row=0, column=1, padx=6, pady=6)
    if(self.workDict["functional"]):
      i = 0
      self.chcs_functional = []
      self.var_chcs_functional = []
      for x in self.list_functional:
        c = i
        self.var_chcs_functional.append(IntVar(value=0))
        self.chcs_functional.append( tk.Checkbutton(self, text=x, width=20, anchor="w", variable=self.var_chcs_functional[c], onvalue=1, offvalue=0) )
        self.chcs_functional[i].grid(row=(i+2), column=1, padx=(50,0), pady=5)
        self.chcs_functional[i].config( font = self.font_checkbox )
        #self.chcs_functional[i].select()
        i = i+1

      #control for online reserch of kegg code
      i=i+3
      #label title
      self.lbl_keggOnline = tk.Label(self, text='Retrieve KEGG name', width=20, font=self.font_kegg_title)  
      self.lbl_keggOnline.grid(row=i, column=1, padx=6, pady=6)
      #label description
      self.lbl_keggOnline_info = tk.Label(self, text='(working internet connection needed)', width=30, font=self.font_subtitle)  
      self.lbl_keggOnline_info.grid(row=(i+1), column=1, padx=6, pady=0)
      #checkbox
      self.var_chcs_kegg = IntVar(value=1)
      self.chcs_kegg = tk.Checkbutton(self, text="yes", width=20, anchor="w", variable=self.var_chcs_kegg, onvalue=1, offvalue=0)
      self.chcs_kegg.grid(row=(i+2), column=1, padx=(50,0), pady=5)
      self.chcs_kegg.select()
      self.chcs_kegg.config( font = self.font_checkbox )
    else:
      self.lbl_noFunctional = tk.Label(self, text='No annotations', width=20, font=self.font_up_base)  
      self.lbl_noFunctional.grid(row=1, column=1, padx=5, pady=5)
  
    #Choose Union label
    self.lbl_chooseUnion = tk.Label(self, text='Taxon-specific function', width=40, font=self.font_title)  
    self.lbl_chooseUnion.grid(row=0, column=2, columnspan=3, sticky='EW', padx=6, pady=6 )

    #check if there are both the annotaion 
    if(self.workDict["taxonomic"] and self.workDict["functional"]):
      #option to taxonomic
      self.opt_taxonomic_var = StringVar(value=self.list_taxonomic[0]) # dafault value
      self.opt_taxonomic = tk.OptionMenu(self, self.opt_taxonomic_var, *self.list_taxonomic)
      self.opt_taxonomic.grid(row=1, column=2, padx=10, pady=6)
      self.opt_taxonomic.config(width=18)
      self.opt_taxonomic.config( font = self.font_checkbox )

      #option to functional
      self.opt_functional_var = StringVar(value=self.list_functional[0]) # dafault value
      self.opt_functional = tk.OptionMenu(self, self.opt_functional_var, *self.list_functional)
      self.opt_functional.grid(row=1, column=3, padx=10, pady=6)
      self.opt_functional.config(width=18)
      self.opt_functional.config( font = self.font_checkbox )

      #Add button
      self.btn_add = tk.Button(self, text='Add', font=self.font_button, width=18, command=self.add_element)
      self.btn_add.grid(row=1, column=4, padx=10, pady=6)

      #Create frame and scrollbar
      self.my_frame = Frame(self, bg='red',)
      self.my_frame.grid(row=2, column=2, rowspan=self.max_row, columnspan=2)
      #scrollbar
      self.my_scrollbar = Scrollbar(self.my_frame,  orient=VERTICAL)

      #Listbox
      #SINGLE, BROWSE, MULTIPLE, EXTENDED
      self.my_listbox = Listbox(self.my_frame, yscrollcommand=self.my_scrollbar.set, selectmode=EXTENDED) #background="Blue", fg="white", selectbackground="Red",highlightcolor="Red",
      self.my_listbox.grid(row=0, column=0)
      self.my_listbox.config(width=50, height=12)
      
      #configure scrollvar
      self.my_scrollbar.config(command=self.my_listbox.yview)
      self.my_scrollbar.grid(row=0, column=1, sticky="NS")
      
      #Remove button
      self.btn_remove = tk.Button(self, text='Remove', font=self.font_button, width=18, command=self.remove_element)
      self.btn_remove.grid(row=2, column=4, rowspan=2, padx=10, pady=6)

      #Remove All button
      self.btn_remove_all = tk.Button(self, text='Remove all', font=self.font_button, width=18, command=self.remove_all_alement)
      self.btn_remove_all.grid(row=3, column=4, rowspan=2, padx=10, pady=6)
    else:
      #Choose Union label
      self.lbl_noAnnotation = tk.Label(self, text='Not enough annotations', width=36, font=self.font_up_base)  
      self.lbl_noAnnotation.grid(row=1, column=2, columnspan=3, sticky='EW', padx=6, pady=6 )

    #chek if there are at least one annotation file
    if(self.workDict["taxonomic"] or self.workDict["functional"]):
      #Download button
      self.btn_remove_all = tk.Button(self, text='Download tables', font=self.font_button, width=18, command=self.download)
      self.btn_remove_all.grid(row=6, column=4, rowspan=2, padx=10, pady=6)

      #option to extra table download
      self.lbl_sup_tab = tk.Label(self, text='Supplementary tables',width=25,font=self.font_title)
      #checkbox text according to start choose
      box_text = "Feature-related peptide counts"
      if(self.workDict["mode"] == 'proteins'):
        box_text = "Feature-related protein counts"
      #checkbox
      self.var_chcs_sup = IntVar(value=0)
      self.chcs_sup = tk.Checkbutton(self, text=box_text, width=25, variable=self.var_chcs_sup, onvalue=1, offvalue=0)
      self.chcs_sup.config( font = self.font_checkbox )
      #self.chcs_sup.select()
      #control to put in the right way the label and checbox, according to kegg
      if( hasattr(self, 'lbl_keggOnline') ):
        #get info from kegg online lbl
        info = self.lbl_keggOnline.grid_info()
        need_row = info["row"]
        self.lbl_sup_tab.grid(row=need_row, column=2, columnspan=2, padx=6, pady=6)
        self.chcs_sup.grid(row=need_row+2, column=2, columnspan=2, padx=5, pady=5)
      else:
        self.lbl_sup_tab.grid(row=self.max_row+1, column=2, columnspan=2, padx=6, pady=6)
        self.chcs_sup.grid(row=self.max_row+2, column=2, columnspan=2, padx=5, pady=5)

    if( (not self.workDict["taxonomic"]) and (not self.workDict["functional"]) ):
      #Only for space
      self.lbl_space = tk.Label(self, text='',width=18,font=self.font_up_base)
      self.lbl_space.grid(row=2, column=0, padx=5, pady=5)

    last_kegg_row = 3
    if(self.workDict["functional"]):
      #get position of last chechbox from functional coloums
      info = self.chcs_kegg.grid_info()
      last_kegg_row = info["row"] + 1 #add one to not overwrite label
    elif(self.workDict["taxonomic"]):
      #get position of last chechbox from taxonomic coloums
      info = self.chcs_taxonomic[-1].grid_info()
      last_kegg_row = info["row"] + 1 #add one to not overwrite label
      #Only for space
      self.lbl_space_1 = tk.Label(self, text='',width=18,font=self.font_up_base)
      self.lbl_space_1.grid(row=last_kegg_row, column=0, columnspan=2, padx=5, pady=5)
      last_kegg_row = last_kegg_row + 1
      
    #Previous Step button
    self.btn_previous_step = tk.Button(self, text='🡸 Previous step', font=self.font_button, width=18, command=self.previous_window)
    self.btn_previous_step.grid(row=last_kegg_row, column=0, rowspan=1, padx=10, pady=6)
    #Next Step button
    self.btn_next_step = tk.Button(self, text='Next step 🡺', font=self.font_button, width=18, command=self.next_window)
    self.btn_next_step.grid(row=last_kegg_row, column=4, rowspan=1, padx=10, pady=6)

    #put this window up
    self.lift()

    #when I close window
    self.protocol("WM_DELETE_WINDOW", self.on_closing)
    

  def on_closing(self):
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        self.wn_root.destroy()

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

  def remove_element(self):
    #delete all select elment from list
    #self.my_listbox.delete(ANCHOR)
    for item in reversed(self.my_listbox.curselection()):
      self.my_listbox.delete(item)

  def remove_all_alement(self):
    #delete all element from list
    self.my_listbox.delete(0, END)

  def create_list(self):
    #create empty list
    my_list = []
    #Fill list to taxonomic
    if(self.workDict["taxonomic"]):
      for i in range(0, len(self.list_taxonomic)):
        if(self.var_chcs_taxonomic[i].get()):
          #create list
          inside_list = []
          #get column name and insert inside the "inside_list"
          inside_list.append(self.list_taxonomic[i])
          #insert "inside_list" inside "my_list"
          my_list.append(inside_list)

    #Fill list to functional
    if(self.workDict["functional"]):
      for i in range(0, len(self.list_functional)):
        if(self.var_chcs_functional[i].get()):
          #create list
          inside_list = []
          #get column name and insert inside the "inside_list"
          inside_list.append(self.list_functional[i])
          #insert "inside_list" inside "my_list"
          my_list.append(inside_list)

    #Fill list to Union
    if((self.workDict["taxonomic"]) and (self.workDict["functional"])):
      #get all element from listbox
      get_content = self.my_listbox.get(0, END)
      #read and elaborate all elments in listbox
      for con_item in get_content:
        #create list
        inside_list = []
        #split and pass to 2 different position of inside_list
        col_1, col_2 = con_item.split('+')
        inside_list.extend([col_1, col_2])
        #insert "inside_list" inside "my_list"
        my_list.append(inside_list)

    return my_list

  def download(self):
    #ask position to save all file
    file_direcotory = filedialog.askdirectory(parent=self)

    #check if a file has been chosen
    if file_direcotory:
      #invoke function to manage data before export
      my_list = self.create_list()

      #show loading windows
      self.winLoad = wLd.LoadingWindow("Downloading file(s)...")

      #create thread to download file
      #get kegg online checkbox value
      keggOnline = False
      if(self.workDict["functional"]):
        keggOnline = self.var_chcs_kegg.get()
      #get Supplementary tables online checkbox value
      sup_tab = False
      if(self.workDict["taxonomic"] or self.workDict["functional"]):
        sup_tab = self.var_chcs_sup.get()
      #create a dictionary to pass
      params = {
        "keggOnline": keggOnline,
        "sup_tab": sup_tab,
        "mode": self.workDict["mode"],
        "fill0": self.workDict["fill0"]
      }

      #create thread and start it
      download_thread = AsyncDownload_Aggregation(self.df, my_list, params, file_direcotory)
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
    
    #create new window
    self.windowTemplate = wTm.TemplateWindow(self.wn_root, self)



'''
if __name__ == "__main__":
  app = AggregationWindow()
  app.mainloop()
'''