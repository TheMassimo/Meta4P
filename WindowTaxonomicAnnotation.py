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
#import my multi threading function to upload and download file
from MyMultiThreading import *

#import loading window
import WindowLoading as wLd
#import next window
import WindowFunctionalAnnotation as wFnAn

class TaxonomicWindow(tk.Toplevel): #tk.Tk):
  def __init__(self, wn_root, wn_previous, previousDf, previousDict):
    super().__init__()

    #take the root window
    self.wn_root = wn_root
    #take the previous window
    self.wn_previous = wn_previous

    #take the old df
    self.df = previousDf;
    #take the old dict
    self.workDict = previousDict
    #check if file is load
    self.isFileLoad = False

    #preapre df
    self.df_annotation = pd.DataFrame()

    # configure the root window
    self.title('Taxonomic annotation')
    self.geometry('420x280')

    #fonts
    self.font_title=('Calibri', 16, 'bold')
    self.font_up_base = ('Calibri', 12, 'bold')
    self.font_base = ('Calibri', 12)
    self.font_button = ('Calibri', 10)
    self.font_checkbox = ('Calibri', 10)


    #Skip Step
    self.btn_skip_step = tk.Button(self, text='Skip step', font=self.font_button, width=22,command=self.skip_window)
    self.btn_skip_step.grid(row=0, column=0, padx=20, pady=5)
    #Only for space
    self.lbl_space_1 = tk.Label(self, text='',width=30,font=self.font_up_base)
    self.lbl_space_1.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
    #Load annotation button
    self.btn_loadFile = tk.Button(self, text='Upload annotation', font=self.font_button, width=22, command=self.upload_annotation_file)
    self.btn_loadFile.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
    #label annotation loaded
    self.lbl_loadedFile = tk.Label(self, text='No file',width=30,font=self.font_up_base)
    self.lbl_loadedFile.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
    #Download button
    self.btn_download = tk.Button(self, text='Download annotated table', font=self.font_button, width=22,command=self.download)
    self.btn_download.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
    #Only for space
    self.lbl_space_2 = tk.Label(self, text='',width=30,font=self.font_up_base)
    self.lbl_space_2.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
    #Previous Step
    self.btn_previous_step = tk.Button(self, text='🡸 Previous step', font=self.font_button, width=22,command=self.previous_window)
    self.btn_previous_step.grid(row=6, column=0, padx=20, pady=5)
    #Next Step
    self.btn_next_step = tk.Button(self, text='Next step 🡺', font=self.font_button, width=22,command=self.next_window)
    self.btn_next_step.grid(row=6, column=1, padx=20, pady=5)

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
        tk.messagebox.showerror(parent=self, title="Error", message="File not upload\nIt is probably in use by another program")

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

    #create a valid list of columns and add abundaces columns
    valid_columns = ['lca', 'superkingdom', 'kingdom', 'phylum',
                     'class', 'order', 'family', 'genus', 'species']
    #insert in first position the first elment according to the type of the file
    if(self.workDict["mode"] == 'proteins'):
      valid_columns.insert(0, 'Accession No.')
    else:
      valid_columns.insert(0, 'peptide')
    #in the df keep only the useful columns
    self.df_annotation = self.df_annotation.filter(items=valid_columns)

    #check if the df_columns cointains all valid columns, otherwise return an error message and exit from method
    check = all(item in self.df_annotation.columns for item in valid_columns)
    if(not check):
      self.isFileLoad = False
      self.lbl_loadedFile['text'] = "No file"
      tk.messagebox.showerror(parent=self, title="Error", message="Incompatible columns in uploaded file")
      return False

    return True

  def upload_annotation_file(self):
    #ask file name
    filepath = filedialog.askopenfilename(parent=self, title="Open") #,filetypes=(("text files","*.txt"),("All files","*.*")))

    #check if a file has been chosen
    if filepath:
      #load the name of file in label (if name is too long then resize it)
      tmp_path = os.path.basename(filepath)
      if(len(tmp_path)>25):
        tmp_path = tmp_path[:25] + "..."
      self.lbl_loadedFile['text'] = tmp_path
      #self.lbl_loadedFile['text'] = os.path.basename(filepath)

      #show loading windows
      self.winLoad = wLd.LoadingWindow("Upload file...")

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
      file = filedialog.asksaveasfile(parent=self, filetypes=[('EXCEL','.xlsx')], mode='w', defaultextension=".xlsx")

      #check if a file has been chosen
      if file:
        #save file temporaneous
        self.file = file

        #show loading windows
        self.winLoad = wLd.LoadingWindow("Manage file...")
        
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
    self.winLoad = wLd.LoadingWindow("Download file...")

    #create thread to download file
    download_thread = AsyncDownload(self.df_tmp, self.file)
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
      self.winLoad = wLd.LoadingWindow("Manage file...")
      
      #create thread to manage the file
      manage_file_thread = ManageTaxonomic(self)
      manage_file_thread.start()
      self.monitor_manage_file(manage_file_thread, "next_window")
    else:
      tk.messagebox.showerror(parent=self, title="Error", message="No files uploaded")

  def ultimate_next_window(self):
    #Edit the previous dict
    self.workDict["taxonomic"] = True

    #hide this window
    self.withdraw()
    #create new window
    self.windowFunctional = wFnAn.FunctionalWindow(self.wn_root, self, self.df_tmp, self.workDict) 

  def skip_window(self):
    #Edit the previous dict
    self.workDict["taxonomic"] = False

    #hide this window
    self.withdraw()
    #create new window
    self.windowFunctional = wFnAn.FunctionalWindow(self.wn_root, self, self.df, self.workDict)


'''
if __name__ == "__main__":
  app = TaxonomicWindow()
  app.mainloop()
'''