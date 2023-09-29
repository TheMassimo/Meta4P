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
from tkinter.messagebox import showinfo

#import loading window
import WindowLoading as wLd
#import next window
import WindowAggregation as wAg

class SummaryMetricsPreWindow(tk.Toplevel): #tk.Tk):
    def __init__(self, wn_root, wn_previous, previousDf):
        super().__init__()

        #take the root window (in this case is the same that previous)
        self.wn_root = wn_root
        #take the previous windows
        self.wn_previous = wn_previous
        #take the old df
        self.df = previousDf;

        #change icon
        img = PhotoImage(file=resource_path(config.icon))
        self.iconphoto(False, img)

        # configure the root window
        self.title('Summary metrics') #Meta Protein Annotation Aggregation

        #Create button name
        button_name = ""
        if(MyUtility.workDict["mode"] == "Proteins"):
            button_name = "Download protein metrics"
            self.defaultDwName = "protein metrics.xlsx"
        elif(MyUtility.workDict["mode"] == "Peptides"):
            button_name = "Download peptide metrics"
            self.defaultDwName = "peptide metrics.xlsx"
        else:
            button_name = "Download PSM metrics"
            self.defaultDwName = "PSM metrics.xlsx"

        #Download button
        self.btn_download_metrics = tk.Button(self, text=button_name, font=config.font_button, width=30,command=self.download)
        self.btn_download_metrics.grid(row=0, column=0, columnspan=2, padx=5, pady=(30,10))

        #Previous Step
        self.btn_previous_step = tk.Button(self, text='← Previous step', font=config.font_button, width=20, command=self.previous_window)
        self.btn_previous_step.grid(row=1, column=0, padx=5, pady=(5,10))
        #Next Step
        self.btn_next_step = tk.Button(self, text='Next step →', font=config.font_button, width=20,  command=self.next_window)
        self.btn_next_step.grid(row=1, column=1, padx=5, pady=(5,10))

        #put this window up
        self.lift()

        #when i close window
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

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


    def download(self):
        #ask directory to save file
        file_path = filedialog.asksaveasfilename(parent=self, filetypes=config.file_types, initialfile=self.defaultDwName, defaultextension=".xlsx")

        #check if a file has been chosen
        if file_path:
            #save file temporaneous
            self.file_path = file_path

            #show loading windows
            self.winLoad = wLd.LoadingWindow("Managing file...")

            #create thread to manage the file
            manage_file_thread = ManageSummaryMetricsPre(self)
            manage_file_thread.start()
            self.monitor_manage_file(manage_file_thread, "download")
        else:
            tk.messagebox.showerror(parent=self, title="Error", message="No directory selected")


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
        #hide this window
        self.withdraw()
        #create new window
        self.windowAggregation = wAg.AggregationWindow(self.wn_root, self, self.df)