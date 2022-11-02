#tkinter import
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo

#Import all windows class
import WindowProteins as wPr
import WindowPeptide as wPe
import WindowPSMs as wPS
import WindowTemplate as wTm
#import my multi threading function to upload and download file
from MyMultiThreading import *



class MenuWindow(tk.Tk): #tk.Toplevel):
    def __init__(self):
        super().__init__()

        #change icon
        img = PhotoImage(file=resource_path("MP_icon.png"))
        self.iconphoto(False, img)

        # configure the root window
        self.title('MetaPAnnA') #Meta Protein Annotation Aggregation
        self.geometry('405x270')

        #font
        font_title = ('Calibri', 18, 'bold')
        font_subtitle = ('Calibri', 14, 'bold')
        font_button = ('Calibri', 10)

        #title label
        self.lbl_title = tk.Label(self, text='Input type',width=30, font=font_title)  
        self.lbl_title.grid(row=0, column=0, padx=6, pady=6)
        #Proteins button
        self.btn_proteins = tk.Button(self, text='Proteins', width=26, font=font_button, command=self.create_proteins)
        self.btn_proteins.grid(row=1, column=0, padx=5, pady=5)
        #Peptide button
        self.btn_peptide = tk.Button(self, text='Peptides', width=26, font=font_button, command=self.create_peptide)
        self.btn_peptide.grid(row=2, column=0, padx=5, pady=5)
        #PSMs button
        self.btn_psms = tk.Button(self, text='PSMs', width=26, font=font_button, command=self.create_psms)
        self.btn_psms.grid(row=3, column=0, padx=5, pady=5)
        #Template button
        self.btn_template = tk.Button(self, text='Rename/reorder sample columns', width=26, font=font_button, command=self.create_template)
        self.btn_template.grid(row=4, column=0, padx=5, pady=(45,5))

        #put this window up
        self.lift()

        #when i close window
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def create_proteins(self):
        #hide menu window
        self.withdraw()
        #create new window
        self.windowPr = wPr.ProteinsWindow(self)

    def create_peptide(self):
        #hide menu window
        self.withdraw()
        #create new window
        self.windowPe = wPe.PeptideWindow(self)

    def create_psms(self):
        #hide menu window
        self.withdraw()
        #create new window
        self.windowPS = wPS.PSMsWindow(self)

    def create_template(self):
        #hide menu window
        self.withdraw()
        #create new window
        self.windowTm = wTm.TemplateWindow(self, self)


'''
#create new window or show it if alredy exists
if( hasattr(self, 'windowPr') ):
    self.windowPr.deiconify()
    #put this window up
    self.windowPr.lift()
else:
    self.windowPr = wPr.ProteinsWindow(self)
'''
    

"""
window.configure(bg='lightgray')

# move window center
winWidth = window.winfo_reqwidth()
winwHeight = window.winfo_reqheight()
posRight = int(window.winfo_screenwidth() / 2 - winWidth / 2)
posDown = int(window.winfo_screenheight() / 2 - winwHeight / 2)
window.geometry("+{}+{}".format(posRight, posDown))

window.mainloop()
"""


'''
#import os
import os

#get the current path
dir_path = os.path.dirname(os.path.realpath(__file__))
#add folder dir
dir_path = dir_path + '/temp'
# Check whether the specified path exists or not
isExist = os.path.exists(dir_path)
if not isExist:
  # Create a new directory because it does not exist 
  os.makedirs(dir_path)
  print("The new directory is created!")
'''