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

class LoadingWindow(tk.Toplevel):

  def __init__(self, loading_text="Loading..."):
    super().__init__()

    #change icon
    img = PhotoImage(file=resource_path(config.icon))
    self.iconphoto(False, img)

    # configure the root window
    self.title('Loading')

    # move window center
    winWidth = self.winfo_reqwidth()
    winwHeight = self.winfo_reqheight()
    posRight = int(self.winfo_screenwidth() / 2 - winWidth / 2)
    posDown = int(self.winfo_screenheight() / 2 - winwHeight / 2)
    self.geometry("+{}+{}".format(posRight, posDown))


    #title label
    self.lbl_loadFile = tk.Label(self, text=loading_text, width=30,font=config.font_title)  
    self.lbl_loadFile.grid(row=0, column=0, padx=10, pady=10)

    #create a progressbar
    pb = ttk.Progressbar(
      self,
      orient='horizontal',
      mode='indeterminate',
      length=200
    )
    pb.grid(row=1, column=0, padx=10, pady=(10,30))
    pb.start(18) #value in ms (default is 50ms)

    #put window in front
    self.lift()
    #prevent touch in other windows
    self.grab_set()

    #Disable exit button and other
    #self.attributes("-disabled", True)


if __name__ == "__main__":
  app = LoadingWindow()
  app.mainloop()