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
import WindowFunctionalMenu as wFnMn

class StandardTaxonomicWindow(tk.Toplevel): #tk.Tk):
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
    self.df = previousDf
    #check if file is load
    self.isFileLoad = False

    #preapre df
    self.df_annotation = pd.DataFrame()

    # configure the root window
    self.title('Taxonomic annotation')

    #Only for space
    self.lbl_space_1 = tk.Label(self, text='',width=30,font=config.font_up_base)
    self.lbl_space_1.grid(row=0, column=0, padx=5, pady=5)

    #Load annotation button
    self.btn_loadFile = tk.Button(self, text='Upload annotation', font=config.font_button, width=22, command=self.upload_annotation_file)
    self.btn_loadFile.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    #label annotation loaded
    self.lbl_loadedFile = tk.Label(self, text='No file',width=30,font=config.font_up_base)
    self.lbl_loadedFile.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    #label annotation info
    self.lbl_annotationInfo = tk.Label(self, text='Meta4P automatically retrieves taxonomic annotations for 8 main levels provided by the Unipept output: lca, domain/superkingdom, phylum, class, order, family, genus, and species.\nTo retrieve information at other levels, please choose "Other/custom taxonomic annotation" instead of "Unipept output" in the previous step, then manually select the columns for your desired levels.', 
                                        wraplength=500, width=100, font=config.font_info)
    self.lbl_annotationInfo.grid(row=3, column=0, columnspan=2, padx=0, pady=0)

    #Download button
    self.btn_download = tk.Button(self, text='Download annotated table', font=config.font_button, width=22,command=self.download)
    self.btn_download.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    #Only for space
    self.lbl_space_2 = tk.Label(self, text='',width=30,font=config.font_up_base)
    self.lbl_space_2.grid(row=5, column=0, padx=5, pady=5)

    #Previous Step
    self.btn_previous_step = tk.Button(self, text='← Previous step', font=config.font_button, width=22,command=self.previous_window)
    self.btn_previous_step.grid(row=6, column=0, padx=20, pady=5)
    #Next Step
    self.btn_next_step = tk.Button(self, text='Next step →', font=config.font_button, width=22,command=self.next_window)
    self.btn_next_step.grid(row=6, column=2, padx=20, pady=5)

    ### right area ###
    #Options
    self.lbl_options = tk.Label(self,text='Options', width=22, font=config.font_title)  
    self.lbl_options.grid(row=0, column=2, padx=6, pady=6)

    #Equate I and L
    if( (MyUtility.workDict["mode"] != 'Proteins') and (MyUtility.workDict['taxonomic_match'] == 'peptide')):
      self.var_chc_IandL = IntVar(value=0)
      self.chc_IandL = tk.Checkbutton(self, text='I (isoleucine) has been replaced by L (leucine) in all peptide sequences listed in the annotation input',
                                           wraplength=400, width=60, anchor="w", variable=self.var_chc_IandL, onvalue=1, offvalue=0)
      self.chc_IandL.grid(row=2, column=2, padx=5, pady=(10,20))
      self.chc_IandL.config(font = config.font_checkbox )

    #Fill with unassigned
    self.var_chc_unassigned = IntVar(value=0)
    self.chc_unassigned = tk.Checkbutton(self, text='Replace missing values with \'unassigned\'',
                                           wraplength=400, width=60, anchor="w", variable=self.var_chc_unassigned, onvalue=1, offvalue=0)
    self.chc_unassigned.grid(row=3, column=2, columnspan=2, padx=5, pady=5)
    self.chc_unassigned.config(font = config.font_checkbox )

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
        self.df_annotation = thread.df.drop_duplicates()
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
    #old methd
    #remove unused coloum
    #self.df_annotation = self.df_annotation.loc[:, :'EC']
    #self.df_annotation.drop(['EC'], inplace=True, axis=1, errors='ignore')

    #create a valid list of columns and add abundaces columns for domain and superkingdom export
    valid_columns_domain = ["lca", "domain", "phylum", "class", "order", "family", "genus", "species"]
    valid_columns_superkingdom = ["lca", "superkingdom", "phylum", "class", "order", "family", "genus", "species"]

    #insert in first position the first elment according to the type of the file for domain and superkingdom export
    if(MyUtility.workDict["mode"] == 'Proteins'):
      valid_columns_domain.insert(0, "Accession No.")
      valid_columns_superkingdom.insert(0, "Accession No.")
    else:
      valid_columns_domain.insert(0, "peptide")
      valid_columns_superkingdom.insert(0, "peptide")

    #in the df keep only the useful columns for domain and superkingdom export
    df_domain = self.df_annotation.filter(items=valid_columns_domain)
    df_superkingdom = self.df_annotation.filter(items=valid_columns_superkingdom)

    #check if the df_columns cointains all valid columns, otherwise return an error message and exit from method for domain and superkingdom export
    check_domain = all(item in self.df_annotation.columns for item in valid_columns_domain)
    check_superkingdom = all(item in self.df_annotation.columns for item in valid_columns_superkingdom)

    #if we have error for both exports return error message
    if(not check_domain and not check_superkingdom):
      self.isFileLoad = False
      self.lbl_loadedFile['text'] = "No file"
      tk.messagebox.showerror(parent=self, title="Error", message="Incompatible columns in uploaded file")
      return False

    #if it is a new export, set the domain output
    if(check_domain):
      self.df_annotation = df_domain.rename(columns={"domain": "superkingdom"})

    #if it is a old export, set the superkingdom output
    if(check_superkingdom):
      self.df_annotation = df_superkingdom #.rename(columns={"superkingdom": "domain"})

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
      upload_thread = AsyncUpload(filepath)
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
        manage_file_thread = ManageTaxonomic(self)
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
      manage_file_thread = ManageTaxonomic(self)
      manage_file_thread.start()
      self.monitor_manage_file(manage_file_thread, "next_window")
    else:
      tk.messagebox.showerror(parent=self, title="Error", message="No files uploaded")

  def ultimate_next_window(self):
    #Edit the previous dict
    MyUtility.workDict["taxonomic"] = True

    #hide this window
    self.withdraw()
    #create new window
    self.windowFunctionalMenu = wFnMn.FunctionalMenuWindow(self.wn_root, self, self.df_tmp)

  def skip_window(self):
    #Edit the previous dict
    MyUtility.workDict["taxonomic"] = False

    #hide this window
    self.withdraw()
    #create new window
    self.windowFunctionalMenu = wFnMn.FunctionalMenuWindow(self.wn_root, self, self.df)


'''
if __name__ == "__main__":
  app = TaxonomicWindow()
  app.mainloop()
'''