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
#random import
import random
#importo os
import os

# importing the threading module
from threading import Thread

#import loading window
import WindowLoading as wLd
#import next window
import WindowSummaryMetricsPre as wSMpr

class StandardFunctionalWindow(tk.Toplevel): #tk.Tk):
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
    #check if file is load
    self.isFileLoad = False

    #preapre df
    self.df_annotation = pd.DataFrame()

    # configure the root window
    self.title('Functional annotation')

    #Only for space
    self.lbl_space_1 = tk.Label(self, text='',width=30,font=config.font_up_base)
    self.lbl_space_1.grid(row=0, column=0, padx=5, pady=5)
    #Load annotation button
    self.btn_loadFile = tk.Button(self, text='Upload annotation file', font=config.font_button, width=22, command=self.upload_annotation_file)
    self.btn_loadFile.grid(row=1, column=0, padx=5, pady=5)
    #label annotation loaded
    self.lbl_loadedFile = tk.Label(self, text='No file',width=30,font=config.font_up_base)
    self.lbl_loadedFile.grid(row=2, column=0, padx=5, pady=5)
    #Download button
    self.btn_download = tk.Button(self, text='Download annotated table', font=config.font_button, width=22,command=self.download)
    self.btn_download.grid(row=3, column=0, padx=5, pady=5)
    #Only for space
    self.lbl_space_2 = tk.Label(self, text='',width=30,font=config.font_up_base)
    self.lbl_space_2.grid(row=4, column=0, padx=5, pady=5)
    #Previous Step
    self.btn_previous_step = tk.Button(self, text='← Previous step', font=config.font_button, width=22,command=self.previous_window)
    self.btn_previous_step.grid(row=5, column=0, padx=20, pady=5)
    #Next Step
    self.btn_next_step = tk.Button(self, text='Next step →', font=config.font_button, width=22,command=self.next_window)
    self.btn_next_step.grid(row=5, column=2, padx=20, pady=5)


    ### right area ###
    #Options
    self.lbl_options = tk.Label(self,text='Options', width=22, font=config.font_title)  
    self.lbl_options.grid(row=0, column=2, padx=6, pady=6)

    #Kegg description checkbox
    self.var_chc_kegg_description = IntVar(value=0)
    self.chc_kegg_description = tk.Checkbutton(self, text='Retrieve KEGG name', width=32,  anchor="w", variable=self.var_chc_kegg_description, onvalue=1, offvalue=0)
    self.chc_kegg_description.grid(row=1, column=2, padx=5, pady=(5,0))
    self.chc_kegg_description.config( font = config.font_checkbox )
    #label description
    self.lbl_keggOnline = tk.Label(self, text='(working internet connection needed)', width=30, font=config.font_info)  
    self.lbl_keggOnline.grid(row=2, column=2, padx=5, pady=(0,20))

    #Fill with unassigned
    self.var_chc_unassigned = IntVar(value=0)
    self.chc_unassigned = tk.Checkbutton(self, text='Replace missing values with \'unassigned\'',
                                         width=34, anchor="w", variable=self.var_chc_unassigned, onvalue=1, offvalue=0)
    self.chc_unassigned.grid(row=3, column=2, padx=5, pady=5)
    self.chc_unassigned.config(font = config.font_checkbox )

    #Equate I and L
    if( (MyUtility.workDict["mode"] != 'Proteins') and (MyUtility.workDict['functional_match'] == 'peptide')):
      self.var_chc_IandL = IntVar(value=0)
      self.chc_IandL = tk.Checkbutton(self, text='I and L treated as equivalent for annotation',
                                           width=34, anchor="w", variable=self.var_chc_IandL, onvalue=1, offvalue=0)
      self.chc_IandL.grid(row=4, column=2, padx=(5,10), pady=(10,20))
      self.chc_IandL.config(font = config.font_checkbox )

    #put this window up
    self.lift()

    #when I close window
    self.protocol("WM_DELETE_WINDOW", self.on_closing)
    

  def on_closing(self):
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
      self.wn_root.destroy()

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
        #take the df_annotation
        self.df_annotation = thread.df
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

  def starting_with_map(self, lst):
    map_words = [word for word in lst if word.startswith('map')]
    return ','.join(map_words) if map_words else ''

  def choose_element(self, lst):
    if len(lst) == 1:
      return lst[0]
    else:
      return lst[1]

  def manage_the_upload(self):
    #edit name for solve name conflict
    if "COG Functional cat." in self.df_annotation.columns:
      self.df_annotation = self.df_annotation.rename(columns={"COG Functional cat.": "COG_category"})

    #remove unused coloum
    #new method
    #create a valid list of columns and add abundaces columns
    valid_columns = ['query', 'COG_category', 'GOs', 'EC', 'KEGG_ko', 'KEGG_Pathway', 'KEGG_Module',
                     'KEGG_Reaction', 'CAZy']

    #in the df_annotation keep only the useful columns
    self.df_annotation = self.df_annotation.filter(items=valid_columns)

    #check if the df_columns cointains all valid columns, otherwise return an error message and exit from method
    check = all(item in self.df_annotation.columns for item in valid_columns)
    if(not check):
      self.isFileLoad = False
      self.lbl_loadedFile['text'] = "No file"
      tk.messagebox.showerror(parent=self, title="Error", message="Incompatible columns in uploaded file")
      return False

    #I keep only the second element of the "query" column (if there is more than one element) separate by |
    lists_query = self.df_annotation['query'].str.split('|')
    self.df_annotation['query'] = lists_query.apply(self.choose_element)
    #I keep only the second element of the "query" column (if there is more than one element) that start with UniRed+number+_
    lists_query = self.df_annotation['query'].str.split(r'UniRef\d+_')
    self.df_annotation['query'] = lists_query.apply(self.choose_element)
    #another way but more problematic
    #self.df_annotation['query'] = self.df_annotation['query'].str.split('|').str[1]

    #From the "KEGG_Pathway" column we remove all the ko and keep only map
    lists_map = self.df_annotation['KEGG_Pathway'].str.split(',')
    self.df_annotation['KEGG_Pathway'] = lists_map.apply(self.starting_with_map)

    return True

  def upload_annotation_file(self):
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
      upload_thread = AsyncUpload_2(filepath)
      upload_thread.start()
      self.monitor_upload(upload_thread)
    else:
      tk.messagebox.showwarning(parent=self, title="Warning", message="No file selected")

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
      #ask directory to save file
      file_path = filedialog.asksaveasfilename(parent=self, filetypes=config.file_types, defaultextension=".xlsx")

      #check if a file has been chosen
      if file_path:
        #save file temporaneous
        self.file_path = file_path

        #show loading windows
        self.winLoad = wLd.LoadingWindow("Managing file...")
        
        #create thread to manage the file
        manage_file_thread = ManageFunctional(self)
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
      #show loading windows
      self.winLoad = wLd.LoadingWindow("Managing file...")
      
      #create thread to manage the file
      manage_file_thread = ManageFunctional(self)
      manage_file_thread.start()
      self.monitor_manage_file(manage_file_thread, "next_window")
    else:
      tk.messagebox.showerror(parent=self, title="Error", message="No files uploaded")

  def ultimate_next_window(self):
    #Edit the previous dict
    MyUtility.workDict["functional"] = True

    #hide this window
    self.withdraw()
    #create new window
    self.windowSummaryMetricsPre = wSMpr.SummaryMetricsPreWindow(self.wn_root, self, self.df_tmp)



'''
if __name__ == "__main__":
  app = FunctionalWindow()
  app.mainloop()
'''