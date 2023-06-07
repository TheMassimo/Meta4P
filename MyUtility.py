#import config module for environmental variability
import config
#import my utility class and function
import MyUtility


#tkinter import
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from tkinter.messagebox import showinfo
from tkinter.ttk import Separator, Style


#common variable
'''
input_type       -> proteome/mzTab/other
mode             -> Proteins/Peptides/PSMs
fill0            -> 0/1
extra_counts_col -> 0/1
counts_col       -> 0/1
taxonomic_mode   -> standard/dynamic
taxonomic        -> True/False
taxonomic_table  -> [] #that contains the name of taxonomic columns  
functional_mode  -> standard/dynamic
functional       -> True/False
functional_table -> [] #that contains the name of functional columns
functional_match -> protein/peptide
'''
workDict = {}


#common class
class CheckboxList(tk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        #save master windows
        self.master = master

        self.canvas = tk.Canvas(self, width=kw.get('width', 180), height=kw.get('height', 140), bd=0, highlightthickness=0) #bg='white', 
        #self.canvas = tk.Canvas(self, bg='white', bd=0,width=115, highlightthickness=0)
        self.yscroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.yscroll.set)
        self.canvas.grid(row=0,column=0, sticky='nsew')
        self.yscroll.grid(row=0, column=1, sticky='nse')
        self.frame.bind("<Configure>", lambda e: self.canvas.config(width=e.width, scrollregion=self.canvas.bbox("all")))

        #add listener for mouse
        #self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
     
    def _on_mousewheel(self, event):
        bbox = self.frame.bbox("all")
        if event.x >= bbox[0] and event.x <= bbox[2] and event.y >= bbox[1] and event.y <= bbox[3]:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def scroll_to_top(self):
        self.canvas.yview_moveto(0)

    def removeAllCheckbox(self):
        #se esiste le elimino
        if( hasattr(self, 'chcs') ):
            #destroy all chechbox widget
            for i in self.chcs:
                i.destroy()
            #clear the lists
            self.chcs.clear()
            self.var_chcs.clear()

    def selectAllCheckbox(self):
        for chc in self.chcs:
            chc.select()

    def deselectAllCheckbox(self):
        for chc in self.chcs:
            chc.deselect()

    def insertCheckbox(self, myList):
        #iterate for all element
        i = 0
        self.chcs = []
        self.var_chcs = []

        for x in myList:
            c = i
            self.var_chcs.append(IntVar(value=1))
            self.chcs.append( tk.Checkbutton(self.frame, text=x, width=20, anchor="w", variable=self.var_chcs[c], onvalue=1, offvalue=0) )
            self.chcs[i].grid(row=i, column=0, sticky='w', padx=5, pady=5)
            self.chcs[i].select()
            self.chcs[i].config( font = config.font_checkbox )
            i = i+1
        self.frame.update_idletasks()

    def destroy(self):
        #remove mousewheel listener before destroying the canvas
        self.canvas.unbind_all("<MouseWheel>")
        super().destroy()



class Separator(tk.Frame):
    def __init__(self, master=None, orient='horizontal', **kwargs):
        super().__init__(master, **kwargs)
        if orient == 'horizontal':
            self.columnconfigure(0, weight=1)
            self.rowconfigure(0, weight=0)
            self.config(height=2, relief='sunken', bd=1)
        else:
            self.columnconfigure(0, weight=0)
            self.rowconfigure(0, weight=1)
            self.config(width=2, relief='sunken', bd=1)

#prova