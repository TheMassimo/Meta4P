#tkinter import
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from tkinter.messagebox import showinfo
from tkinter.ttk import Separator, Style
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

class TemplateWindow(tk.Toplevel): #tk.Tk):
  def __init__(self, wn_root, wn_previous):
    super().__init__()

    #take the root window
    self.wn_root = wn_root
    #take the previous window
    self.wn_previous = wn_previous

    #preapre dfs
    self.df_tm = pd.DataFrame()
    self.df_gn = pd.DataFrame()
    #check for file loaded
    self.isLoad_df = False
    self.isLoad_df_tm = False
    self.isLoad_df_gn = False
    
    # configure the root window
    self.title('Rename/reorder sample columns')
    self.geometry('1180x460')

    #fonts
    self.font_title=('Calibri', 16, 'bold')
    self.font_up_base = ('Calibri', 12, 'bold')
    self.font_base = ('Calibri', 12)
    self.font_subtitle=('Calibri', 10)
    self.font_button = ('Calibri', 10)
    self.font_checkbox = ('Calibri', 10)

    #Big title
    self.lbl_bigTitle = tk.Label(self, text='Rename/reorder sample columns',width=50,font=self.font_title)  
    self.lbl_bigTitle.grid(row=0, column=0, columnspan=7, padx=6, pady=(20,30))


    #title label
    self.lbl_loadGenerator = tk.Label(self, text='Create conversion file',width=25,font=self.font_title)  
    self.lbl_loadGenerator.grid(row=1, column=0, padx=6, pady=(6,0))
    #decription title label
    self.lbl_descLoadGenerator = tk.Label(self, text='(skip if already available)',width=25,font=self.font_subtitle)  
    self.lbl_descLoadGenerator.grid(row=2, column=0, padx=0, pady=(0,20))
    #decription button loadGenerator
    self.lbl_descLoadGenerator = tk.Label(self, text='A MetaPAnnA output file is required\nto retrieve sample column headers',width=30,font=self.font_subtitle)  
    self.lbl_descLoadGenerator.grid(row=3, column=0, padx=0, pady=(20,0))
    #Load button
    self.btn_loadGenerator = tk.Button(self, text='Upload File', width=25, command=self.upload_general_file)
    self.btn_loadGenerator.grid(row=4, column=0, padx=5, pady=5)
    #label generate
    self.lbl_generatorFile = tk.Label(self, text='No file',width=30,font=self.font_base)
    self.lbl_generatorFile.grid(row=5, column=0, padx=5, pady=5)
    #Done button
    self.btn_downloadTemplate = tk.Button(self, text='Download conversion file', font=self.font_button, width=25, command=self.download_template)
    self.btn_downloadTemplate.grid(row=6, column=0, padx=5, pady=5)

    #Only for space
    self.lbl_space = tk.Label(self, text='',width=25,font=self.font_up_base)
    self.lbl_space.grid(row=7, column=0, padx=5, pady=5)
    #Previous Step button
    self.btn_previous_step = tk.Button(self, text='🡸 Previous step', width=30, font=self.font_button, command=self.previous_window)
    self.btn_previous_step.grid(row=8, column=0, padx=5, pady=5)

    #separator    
    sp_1 = Separator(self, orient="vertical")
    sp_1.grid(column=1, row=1, rowspan=6, pady=(25,0), sticky='ns')

    #Load Template title label
    self.lbl_loadTemplate = tk.Label(self, text='Load conversion file',width=25,font=self.font_title)  
    self.lbl_loadTemplate.grid(row=1, column=2, padx=6, pady=6)
    #decription button loadTemplate
    self.lbl_descLoadTemplate = tk.Label(self, text='Modified conversion file with\nnew sample column headers\nand/or sample order',width=30,font=self.font_subtitle)  
    self.lbl_descLoadTemplate.grid(row=3, column=2, padx=0, pady=(20,0))
    #Load Template
    self.btn_loadTemplate = tk.Button(self, text='Upload File', width=25, font=self.font_button, command=self.upload_template_file)
    self.btn_loadTemplate.grid(row=4, column=2, padx=5, pady=5)
    #label template
    self.lbl_templateFile = tk.Label(self, text='No file',width=30,font=self.font_base)
    self.lbl_templateFile.grid(row=5, column=2, padx=5, pady=5)

    #separator    
    sp_2 = Separator(self, orient="vertical")
    sp_2.grid(column=3, row=1, rowspan=6, pady=(25,0), sticky='ns')

    #Load File to edit title label
    self.lbl_loadEditable = tk.Label(self, text='Select file(s) to edit',width=25,font=self.font_title)  
    self.lbl_loadEditable.grid(row=1, column=4, padx=6, pady=6)
    #decription button loadEditable
    self.lbl_descLoadEditable = tk.Label(self, text='MetaPAnnA outputs with sample\ncolumns to rename/reorder',width=30,font=self.font_subtitle)  
    self.lbl_descLoadEditable.grid(row=3, column=4, padx=0, pady=(20,0))
    #Button for Load File to edit
    self.btn_loadEditable = tk.Button(self, text='Upload file(s)', font=self.font_button, width=25, command=self.upload_editable_file)
    self.btn_loadEditable.grid(row=4, column=4, padx=5, pady=5)
    #label template
    self.lbl_editableFile = tk.Label(self, text='No file',width=30,font=self.font_base)
    self.lbl_editableFile.grid(row=5, column=4, padx=5, pady=5)

    #separator    
    sp_3 = Separator(self, orient="vertical")
    sp_3.grid(column=5, row=1, rowspan=6, pady=(25,0), sticky='ns')


    #Rename file(s) title label
    self.lbl_loadEditable = tk.Label(self, text='Rename/reorder',width=25,font=self.font_title)  
    self.lbl_loadEditable.grid(row=1, column=6, padx=6, pady=6)
    #Final Done button
    self.btn_rename = tk.Button(self, text='Rename/reorder', font=self.font_button, width=25, command=self.download_final)
    self.btn_rename.grid(row=4, column=6, padx=5, pady=5)



    #put this window up
    self.lift()

    #when I close window
    self.protocol("WM_DELETE_WINDOW", self.on_closing)
    

  def on_closing(self):
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        self.wn_root.destroy()

  def monitor_upload_template(self, thread):
    if thread.is_alive():
      # check the thread every 100ms
      self.after(100, lambda: self.monitor_upload_template(thread))
    else:
      self.winLoad.destroy()
      #put window in front
      self.lift()
      if(thread.fileOpen):
        #take the df
        self.df_tm = thread.df
        #read it to create some button in the window and mark if the file is load
        self.isLoad_df_tm = True
      else:
        tk.messagebox.showerror(parent=self, title="Error", message="File not upload\nIt is probably in use by another program")

  def monitor_upload_generator(self, thread):
    if thread.is_alive():
      # check the thread every 100ms
      self.after(100, lambda: self.monitor_upload_generator(thread))
    else:
      #delete load window
      self.winLoad.destroy()
      #put window in front
      self.lift()
      if(thread.fileOpen):
        #take the df
        self.df_gn = thread.df
        #read df and do some things
        self.manage_the_upload_generator()
        #read it to create some button in the window and mark if the file is load
        self.isLoad_df_gn = True
      else:
        tk.messagebox.showerror(parent=self, title="Error", message="File not upload\nIt is probably in use by another program")

  def monitor_download_template(self, thread):
    if thread.is_alive():
      #check the thread every 100ms
      self.after(100, lambda: self.monitor_download_template(thread))
    else:
      #delete load window
      self.winLoad.destroy()
      #put window in front
      self.lift()
      if(not thread.fileSaved):
        tk.messagebox.showerror(parent=self, title="Error", message="File not saved\nIt is probably in use by another program")

  def monitor_download_file(self, thread):
    if thread.is_alive():
      #check the thread every 100ms
      self.after(100, lambda: self.monitor_download_file(thread))
    else:
      #delete load window
      self.winLoad.destroy()
      #put window in front
      self.lift()
      if(not thread.correctLen):
        tk.messagebox.showerror(parent=self, title="Error", message="One or more files not renamed\nNumber of columns does not match")
      if(not thread.fileSaved):
        tk.messagebox.showerror(parent=self, title="Error", message="One or more files not saved\nThey are probably in use by another program")

  def manage_the_upload_generator(self):
    #remove unused coloum
    self.df_gn = self.df_gn.filter(like=': Sample')
    #get list of columns
    allColumns = list(self.df_gn.columns)
    #make one row for every column
    self.df_gn = pd.DataFrame(allColumns)
    #extrat only F* word
    self.df_gn = self.df_gn[0].str.extract(pat = '([F][\w]+)')
    #remove all dupliate
    self.df_gn = self.df_gn.drop_duplicates()
    #rename columns
    self.df_gn.rename(columns={0:'Old Name'}, inplace=True)
    #Add empty column
    self.df_gn.insert(loc=1, column='New Name', value=['' for i in range(self.df_gn.shape[0])])

  def upload_editable_file(self):
    #ask file name
    filepath = filedialog.askopenfilename(parent=self, title="Open", multiple=True)#,filetypes=(("text files","*.txt"),("All files","*.*")))

    #check if a file has been chosen
    if filepath:
      #get list from filepath tuple
      self.editable_paths = list(filepath)

      #check if ther is only one file or more
      if(len(self.editable_paths)==1):
        #load the name of file in label (if name is too long then resize it)
        tmp_path = os.path.basename(self.editable_paths[0])
        if(len(tmp_path)>25):
          tmp_path = tmp_path[:25] + "..."
        self.lbl_editableFile['text'] = tmp_path
        #self.lbl_editableFile['text'] = os.path.basename(self.editable_paths[0])
      else:
        self.lbl_editableFile['text'] = "Multiple files"

      #the file is load
      self.isLoad_df = True

    else:
      tk.messagebox.showwarning(parent=self, title="Warning", message="No file selected")
  
  def upload_template_file(self):
    #ask file name
    filepath = filedialog.askopenfilename(parent=self, title="Open")#,filetypes=(("text files","*.txt"),("All files","*.*")))

    #check if a file has been chosen
    if filepath:
      #load the name of file in label (if name is too long then resize it)
      tmp_path = os.path.basename(filepath)
      if(len(tmp_path)>25):
        tmp_path = tmp_path[:25] + "..."
      self.lbl_templateFile['text'] = tmp_path
      #self.lbl_templateFile['text'] = os.path.basename(filepath)

      #show loading windows
      self.winLoad = wLd.LoadingWindow()

      #create thread to load file
      upload_thread = AsyncUpload(filepath)
      upload_thread.start()
      self.monitor_upload_template(upload_thread)
    else:
      tk.messagebox.showwarning(parent=self, title="Warning", message="No file selected")

  def upload_general_file(self):
    #ask file name
    filepath = filedialog.askopenfilename(parent=self, title="Open")#,filetypes=(("text files","*.txt"),("All files","*.*")))

    #check if a file has been chosen
    if filepath:
      #load the name of file in label (if name is too long then resize it)
      tmp_path = os.path.basename(filepath)
      if(len(tmp_path)>25):
        tmp_path = tmp_path[:25] + "..."
      self.lbl_generatorFile['text'] = tmp_path
      #self.lbl_generatorFile['text'] = os.path.basename(filepath)

      #show loading windows
      self.winLoad = wLd.LoadingWindow()

      #create thread to load file
      upload_thread = AsyncUpload(filepath)
      upload_thread.start()
      self.monitor_upload_generator(upload_thread)
    else:
      tk.messagebox.showwarning(parent=self, title="Warning", message="No file selected")

  def download_template(self):
    #check if file is loadid
    if(self.isLoad_df_gn):
      #ask directory to save file
      file = filedialog.asksaveasfile(parent=self, filetypes=[('EXCEL','.xlsx')], mode='w', defaultextension=".xlsx")

      #check if a file has been chosen
      if file:
        #show loading windows
        self.winLoad = wLd.LoadingWindow()

        #create thread to download file
        download_thread = AsyncDownload(self.df_gn, file)
        download_thread.start()
        self.monitor_download_template(download_thread)
      else:
        tk.messagebox.showerror(parent=self, title="Error", message="No directory selected")
    else:
      tk.messagebox.showerror(parent=self, title="Error", message="No files uploaded")

  def download_final(self):
    #check if file is loadid
    if(not self.isLoad_df):
      tk.messagebox.showerror(parent=self, title="Error", message="No rename files uploaded")
    elif(not self.isLoad_df_tm):
      tk.messagebox.showerror(parent=self, title="Error", message="No template file uploaded")
    else:

      #show loading windows
      self.winLoad = wLd.LoadingWindow()

      #create thread to download file
      download_thread = AsyncRenameFile(self.editable_paths, self.df_tm)
      download_thread.start()
      self.monitor_download_file(download_thread)

  def previous_window(self):
    #hide this window
    #self.withdraw()
    #Destroy this window
    self.destroy()

    #show last window
    self.wn_previous.deiconify()
    self.wn_previous.lift()

'''
if __name__ == "__main__":
  app = TemplateWindow()
  app.mainloop()
'''