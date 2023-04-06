#import config module for environmental variability
import config
#import my utility class and function
import MyUtility
#import my multi threading function to upload and download file
from MyMultiThreading import *

#tkinter import
import tkinter as tk
from tkinter import *
from tkinter import ttk

#import my multi threading function to upload and download file
from MyMultiThreading import *

class NameExtensionWindow(tk.Toplevel):

  def __init__(self, master):
    super().__init__(master)

    #save master window
    self.master = master

    #change icon
    img = PhotoImage(file=resource_path(config.icon))
    self.iconphoto(False, img)

    # configure the root window
    self.title('Add prefix/suffix')

    # move window center
    winWidth = self.winfo_reqwidth()
    winwHeight = self.winfo_reqheight()
    posRight = int(self.winfo_screenwidth() / 2 - winWidth / 2)
    posDown = int(self.winfo_screenheight() / 2 - winwHeight / 2)
    self.geometry("+{}+{}".format(posRight, posDown))

    #title label
    self.lbl_loadFile = tk.Label(self, text="Add a prefix and/or a suffix to the\noutput table names (optional)", width=30,font=config.font_title)  
    self.lbl_loadFile.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    #Prefix Entry
    self.ntr_prefix = tk.Entry(self, width=28)
    self.ntr_prefix.grid(row=1,column=0)
    #Prefix Label
    self.lbl_prefix = tk.Label(self,text='Prefix',width=20,font=config.font_base)  
    self.lbl_prefix.grid(row=1, column=1, padx=5, pady=5)

    #Suffix Entry
    self.ntr_suffix = tk.Entry(self, width=28)
    self.ntr_suffix.grid(row=2,column=0)
    #Suffix Label
    self.lbl_suffix = tk.Label(self,text='Suffix',width=20,font=config.font_base)  
    self.lbl_suffix.grid(row=2, column=1, padx=5, pady=5)

    #ok button
    self.btn_ok = tk.Button(self, text='Ok', font=config.font_button, width=20,command=self.confirm_text)
    self.btn_ok.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    #when I close window
    self.protocol("WM_DELETE_WINDOW", self.on_closing)

    #put window in front
    self.lift()
    #prevent touch in other windows
    self.grab_set()


  def on_closing(self):
    #delete itself
    self.destroy()

  def confirm_text(self):
    #get value
    if( (len(self.ntr_prefix.get().strip()) > 0) and (not self.ntr_prefix.get().isspace()) ):
      self.master.prefix = self.ntr_prefix.get() + "_"
    if( (len(self.ntr_suffix.get().strip()) > 0) and (not self.ntr_suffix.get().isspace()) ):
      self.master.suffix = "_" + self.ntr_suffix.get()
    #delete itself
    self.destroy()
    #call method for download files from master window
    self.master.download()


if __name__ == "__main__":
  app = NameExtensionWindow()
  app.mainloop()