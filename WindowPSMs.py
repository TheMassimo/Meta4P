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
#import numpy
import numpy as np

# importing the threading module
from threading import Thread
#import my multi threading function to upload and download file
from MyMultiThreading import *

#import loading window
import WindowLoading as wLd
#import next window
import WindowTaxonomicAnnotation as wTxAn

class PSMsWindow(tk.Toplevel): #tk.Tk):
  def __init__(self, wn_previous):
    super().__init__()

    #change icon
    img = PhotoImage(file=resource_path("MP_icon.png"))
    self.iconphoto(False, img)

    #take the root window (in this case is the same that previous)
    self.wn_root = wn_previous
    #take the previous window
    self.wn_previous = wn_previous

    #preapre df
    self.df = pd.DataFrame()
    #check if file is load
    self.isFileLoad = False

    # configure the root window
    self.title('PSMs')
    self.geometry('1400x600')

    #fonts
    self.font_title=('Calibri', 16, 'bold')
    self.font_up_base = ('Calibri', 12, 'bold')
    self.font_base = ('Calibri', 11)
    self.font_button = ('Calibri', 10)
    self.font_checkbox = ('Calibri', 10)

    
    ### left area ###
    #Load button
    self.btn_loadFile = tk.Button(self, text='Upload input file', font=self.font_button, width=20, command=self.upload_psms_file)
    self.btn_loadFile.grid(row=0, column=0, padx=5, pady=5)
    #label template
    self.lbl_loadedFile = tk.Label(self, text='No file',width=30,font=self.font_up_base)
    self.lbl_loadedFile.grid(row=1, column=0, padx=5, pady=5)
    #Download button
    self.btn_download = tk.Button(self, text='Download filtered table', font=self.font_button, width=20,command=self.download)
    self.btn_download.grid(row=2, column=0, padx=5, pady=5)
    #Previous Step
    self.btn_previous_step = tk.Button(self, text='🡸 Previous step', font=self.font_button, width=20,command=self.previous_window)
    self.btn_previous_step.grid(row=15, column=0, padx=5, pady=5)
    #Next Step
    self.btn_next_step = tk.Button(self, text='Next step 🡺', font=self.font_button, width=20,  command=self.next_window)
    self.btn_next_step.grid(row=15, column=5, padx=5, pady=5)

    ### centre area ###
    #Fileter
    self.lbl_fileter = tk.Label(self,text='Filter PSMs based on',width=20,font=self.font_title)  
    self.lbl_fileter.grid(row=0, column=1, columnspan=4, padx=6, pady=6)
    #separator    
    self.sp = Separator(self, orient="horizontal")
    self.sp.grid(row=1, column=1, columnspan=4, padx=6, sticky='ew')
    
    #Protein FDR label (Confidence)
    self.lbl_confidence = tk.Label(self,text='Confidence',width=20, font=self.font_title)  
    self.lbl_confidence.grid(row=2, column=1, padx=6, pady=6)
    #Protein FDR checkboxes (Confidence)
    self.var_chc_low = IntVar(value=1)
    self.var_chc_medium = IntVar(value=1)
    self.var_chc_high = IntVar(value=1)
    self.chc_low = tk.Checkbutton(self, text='Low', width=20, anchor="w", variable=self.var_chc_low, onvalue=1, offvalue=0)
    self.chc_low.grid(row=3, column=1, padx=(50,5), pady=5)
    self.chc_low.select()
    self.chc_low.config( font = self.font_checkbox )
    self.chc_medium = tk.Checkbutton(self, text='Medium', width=20, anchor="w", variable=self.var_chc_medium, onvalue=1, offvalue=0)
    self.chc_medium.grid(row=4, column=1, padx=(50,5), pady=5)
    self.chc_medium.select()
    self.chc_medium.config( font = self.font_checkbox )
    self.chc_high = tk.Checkbutton(self, text='High', width=20, anchor="w", variable=self.var_chc_high, onvalue=1, offvalue=0)
    self.chc_high.grid(row=5, column=1, padx=(50,5), pady=5)
    self.chc_high.select()
    self.chc_high.config( font = self.font_checkbox )
    
    #Description Label
    self.lbl_description = tk.Label(self,text='Master Protein Description', width=22, font=self.font_title)  
    self.lbl_description.grid(row=2, column=2, columnspan=2, padx=6, pady=6)
    #Radio button frame
    self.rbd_frame = Frame(self, bg="red", width=20, height=20)
    self.rbd_frame.grid(row=3, column=2, columnspan=2)
    #Radio button
    self.rdb_var = StringVar(value='and')
    self.rdb_and = tk.Radiobutton(self.rbd_frame, text="And", width=10, variable=self.rdb_var, value='and')
    self.rdb_and.grid(row=0, column=0, padx=(0,0), pady=0)#, sticky="W")
    self.rdb_and.config( font = self.font_checkbox )
    self.rdb_or = tk.Radiobutton(self.rbd_frame, text="Or", width=10, variable=self.rdb_var, value='or')
    self.rdb_or.grid(row=0, column=1, padx=(0,0), pady=0)#, sticky="E")
    self.rdb_or.config( font = self.font_checkbox )
    #Description Entry
    self.ntr_description = tk.Entry(self, width=36)
    self.ntr_description.grid(row=4,column=2)
    #Description Add button
    self.btn_add = tk.Button(self, text='Add', font=self.font_button, width=3, command=self.add_description_element)
    self.btn_add.grid(row=4, column=3)
    #List for label and button
    self.lbls_description = []
    self.btns_remove = []
    self.descriptionIndex = 0
    #Create frame and scrollbar
    self.dsc_frame = Frame(self)#, bg='red')
    self.dsc_frame.grid(row=5, column=2, rowspan=4, columnspan=2)
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
    self.btn_remove = tk.Button(self, text='Remove', font=self.font_button, width=23, command=self.remove_description_element)
    self.btn_remove.grid(row=9, column=2, padx=5, pady=5)

    #MakedAs label
    self.lbl_marked = tk.Label(self,text='Marker', width=20, font=self.font_title)  
    self.lbl_marked.grid(row=2, column=4, padx=6, pady=6)
    #Only for space
    self.lbl_space_1 = tk.Label(self, text='',width=20,font=self.font_up_base)
    self.lbl_space_1.grid(row=6, column=4, padx=5, pady=5)


    ### right area ###
    #Options
    self.lbl_options = tk.Label(self,text='Options',width=32,font=self.font_title)  
    self.lbl_options.grid(row=0, column=5, padx=6, pady=6)

    #Fill with 0 in abundances
    self.var_chc_fill_zero = IntVar(value=0)
    self.chc_fill_zero = tk.Checkbutton(self, text='Replace missing values with 0', width=32, anchor="w", variable=self.var_chc_fill_zero, onvalue=1, offvalue=0)
    self.chc_fill_zero.grid(row=2, column=5, padx=5, pady=5)
    self.chc_fill_zero.config( font = self.font_checkbox )


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
        #take the df
        self.df = thread.df
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
    #remove unused coloum
    '''
    #old method
    self.df.drop(['Checked', 'Identifying Node Type','Identifying Node','Search ID','Identifying Node No',
                  'PSM Ambiguity','Annotated Sequence','Modifications','# Proteins''Protein Descriptions',
                  '# Missed Cleavages','Charge','Original Precursor Charge','DeltaScore','DeltaCn',
                  'Search Engine Rank','Concatenated Rank','m/z [Da]','Aligned m/z [Da]','MH+ [Da]',
                  'Theo. MH+ [Da]','DeltaM [ppm]','Deltam/z [Da]','Ions Matched','Matched Ions','Total Ions',
                  'Intensity','Activation Type','MS Order','Isolation Interference [%]',
                  'Ion Inject Time [ms]','RT [min]','First Scan','Last Scan','Master Scan(s)','Spectrum File',
                  'Quan Info','Peptides Matched','XCorr','# Protein Groups','Percolator q-Value',
                  'Percolator PEP','Percolator SVMScore','Precursor Abundance',
                  'Apex RT [min]'], inplace=True, axis=1, errors='ignore')
    '''
    #new method
    #create a valid list of columns and add abundaces columns
    valid_columns = ['Confidence', 'Sequence', 'Master Protein Accessions', 'Master Protein Descriptions',
                     'Protein Accessions', 'File ID', 'Marked as']
    #in the df keep only the useful columns
    self.df = self.df.filter(items=valid_columns)

    #check if the df_columns cointains all valid columns, otherwise return an error message and exit from method
    check = all(item in self.df.columns for item in valid_columns)
    if(not check):
      self.isFileLoad = False
      self.lbl_loadedFile['text'] = "No file"
      tk.messagebox.showerror(parent=self, title="Error", message="Incompatible columns in uploaded file")
      return False

    #to be sure, any old lists and checkboxes are removed
    if( hasattr(self, 'chcs_marked') ):
      #destroy all chechbox widget
      for i in self.chcs_marked:
        i.destroy()
      #clear the lists
      self.chcs_marked.clear()
      self.var_chcs_marked.clear()

    #get MarkedAs as value and put in a list
    markedList = self.df['Marked as'].unique()
    markedList = markedList.tolist()
    #get position of markedAs label
    info = self.lbl_marked.grid_info()
    actual_marked_row = info["row"] + 1 #add one to not overwrite label
    actual_marked_column = info["column"]
    #iterate for all element
    i = 0
    self.chcs_marked = []
    self.var_chcs_marked = []
    for x in markedList:
      self.var_chcs_marked.append(IntVar(value=1))
      self.chcs_marked.append( tk.Checkbutton(self, text=x, width=20, anchor="w", variable=self.var_chcs_marked[i], onvalue=1, offvalue=0) )
      self.chcs_marked[i].grid(row=(i+actual_marked_row), column=actual_marked_column, padx=(50,0), pady=5)
      self.chcs_marked[i].select()
      self.chcs_marked[i].config( font = self.font_checkbox )
      i = i+1

    return True

  def upload_psms_file(self):
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
      self.winLoad = wLd.LoadingWindow("Uploading file...")

      #create thread to load file
      upload_thread = AsyncUpload(filepath)
      upload_thread.start()
      self.monitor_upload(upload_thread)
    else:
      tk.messagebox.showwarning(parent=self, title="Warning", message="No file selected")

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
        self.winLoad = wLd.LoadingWindow("Managing file...")
        
        #create thread to manage the file
        manage_file_thread = ManagePSMs(self)
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
      self.winLoad = wLd.LoadingWindow("Managing file...")
      
      #create thread to manage the file
      manage_file_thread = ManagePSMs(self)
      manage_file_thread.start()
      self.monitor_manage_file(manage_file_thread, "next_window")
    else:
      tk.messagebox.showerror(parent=self, title="Error", message="No files uploaded")

  def ultimate_next_window(self):
    #Preapre a dict
    myDict = {}
    myDict["mode"] = 'psms'
    myDict["fill0"] = self.var_chc_fill_zero.get()

    #hide this window
    self.withdraw()
    #create new window
    self.windowTaxonomic = wTxAn.TaxonomicWindow(self.wn_root, self, self.df_tmp, myDict)




'''
if __name__ == "__main__":
  app = PSMsWindow()
  app.mainloop()
'''