#tkinter import
import tkinter as tk
from tkinter import *
from tkinter import ttk

class LoadingWindow(tk.Toplevel):

  def __init__(self, loading_text="Loading..."):
    super().__init__()

    #change icon
    img=PhotoImage(file="C:\\Users\\maxim\\Desktop\\MetaPAnnA\\MP_icon.png")
    self.iconphoto(False,img)

    # configure the root window
    self.title('Loading')
    self.geometry('417x130')
    # move window center
    winWidth = self.winfo_reqwidth()
    winwHeight = self.winfo_reqheight()
    posRight = int(self.winfo_screenwidth() / 2 - winWidth / 2)
    posDown = int(self.winfo_screenheight() / 2 - winwHeight / 2)
    self.geometry("+{}+{}".format(posRight, posDown))

    #fonts
    self.font_title=('Calibri', 18, 'bold')

    #title label
    self.lbl_loadFile = tk.Label(self, text=loading_text, width=30,font=self.font_title)  
    self.lbl_loadFile.grid(row=0, column=0, padx=10, pady=10)

    #create a progressbar
    pb = ttk.Progressbar(
      self,
      orient='horizontal',
      mode='indeterminate',
      length=200
    )
    pb.grid(row=1, column=0, padx=10, pady=10)
    pb.start(18) #value in ms (default is 50ms)

    #put window in front
    self.lift()
    #prevent touch in other windows
    self.grab_set()

    #Disable exit button
    #self.protocol("WM_DELETE_WINDOW", disable_event)


if __name__ == "__main__":
  app = LoadingWindow()
  app.mainloop()