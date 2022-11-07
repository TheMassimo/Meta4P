#import threading
from threading import Thread
#pandas import
import pandas as pd
#numpy import
import numpy as np

#tkinter import
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from tkinter.messagebox import showinfo
from tkinter.ttk import Separator, Style

# Standard library packages
import io
import os
import sys

# Import Biopython modules to interact with KEGG
#from Bio import SeqIO
#from Bio.KEGG import REST
#from Bio.KEGG.KGML import KGML_parser
#from Bio.Graphics.KGML_vis import KGMLCanvas

#Import module to request
from urllib.request import urlopen
import ssl

#utility for load image
def resource_path(relative_path):
  try:
    base_path = sys._MEIPASS
  except Exception:
    base_path = os.path.abspath(".")

  return os.path.join(base_path, relative_path)

def resource_path_2(relative_path):
  base_path = getattr(
    sys,
    '_MEIPASS',
    os.path.dirname(os.path.abspath(__file__)) )
  
  return os.path.join(base_path, relative_path)

#Request for KEGG data
def _q(op, arg1, arg2=None, arg3=None):
  URL = "https://rest.kegg.jp/%s"
  if arg2 and arg3:
    args = f"{op}/{arg1}/{arg2}/{arg3}"
  elif arg2:
    args = f"{op}/{arg1}/{arg2}"
  else:
    args = f"{op}/{arg1}"

  #original request
  #resp = urlopen(URL % (args))
  
  #edit request to avoid certificate request      
  ctx = ssl.create_default_context()
  ctx.check_hostname = False
  ctx.verify_mode = ssl.CERT_NONE
  resp=urlopen(URL % (args), context=ctx)

  if "image" == arg2:
      return resp

  handle = io.TextIOWrapper(resp, encoding="UTF-8")
  handle.url = resp.url
  return handle

#query for KEGG list   
def kegg_list(database, org=None):
  """KEGG list - Entry list for database, or specified database entries.
  db - database or organism (string)
  org - optional organism (string), see below.
  For the pathway and module databases the optional organism can be
  used to restrict the results.
  """
  # TODO - split into two functions (dbentries seems separate)?
  #
  #  https://rest.kegg.jp/list/<database>/<org>
  #
  #  <database> = pathway | module
  #  <org> = KEGG organism code
  if database in ("pathway", "module") and org:
    resp = _q("list", database, org)
  elif isinstance(database, str) and database and org:
    raise ValueError("Invalid database arg for kegg list request.")

  # https://rest.kegg.jp/list/<database>
  #
  # <database> = pathway | brite | module | disease | drug | environ |
  #              ko | genome | <org> | compound | glycan | reaction |
  #              rpair | rclass | enzyme | organism
  # <org> = KEGG organism code or T number
  #
  #
  # https://rest.kegg.jp/list/<dbentries>
  #
  # <dbentries> = KEGG database entries involving the following <database>
  # <database> = pathway | brite | module | disease | drug | environ |
  #              ko | genome | <org> | compound | glycan | reaction |
  #              rpair | rclass | enzyme
  # <org> = KEGG organism code or T number
  else:
    if isinstance(database, list):
      if len(database) > 100:
        raise ValueError(
          "Maximum number of databases is 100 for kegg list query"
        )
      database = ("+").join(database)
    resp = _q("list", database)

  return resp

#Some code to return a Pandas dataframe, given tabular text
def to_df(result):
  #
  return pd.read_table(io.StringIO(result), header=None)

#Manage KEGG data
def manage_kegg_query(self):
  if( hasattr(self, 'query_ko') ): #category_to_search['KEGG_ko']):
    #preapre df
    self.df_ko = pd.DataFrame()
    #get online information from kegg.com and convert into dataframe
    self.df_ko = to_df(self.query_ko)
    #take information about ko codes from originale df
    need_df = (self.df.assign(KEGG_ko=self.df['KEGG_ko'].str.split('[,;]')).explode('KEGG_ko'))
    tmp_list = need_df['KEGG_ko'].dropna().unique().tolist()
    #delete everything is not on the list
    self.df_ko = self.df_ko[self.df_ko[0].isin(tmp_list)]
    #delete everything except what is on the list
    #self.df_ko = self.df_ko[~self.df_ko[0].isin(tmp_list)]
    #mangage description text
    #split elment by ";" and take only the element in position 1
    self.df_ko[1] = self.df_ko[1].str.split('; ').str[1]
    #split elment by "[" and take only the element in position 0
    self.df_ko[1] = self.df_ko[1].str.split(' \[EC').str[0]
  if( hasattr(self, 'query_pathway') ): #category_to_search['KEGG_Pathway']):
    #preapre df
    self.df_pathway = pd.DataFrame()
    #get online information from kegg.com and convert into dataframe
    self.df_pathway = to_df(self.query_pathway)
    #take information about pathway codes from originale df
    need_df = (self.df.assign(KEGG_Pathway=self.df['KEGG_Pathway'].str.split('[,;]')).explode('KEGG_Pathway'))
    tmp_list = need_df['KEGG_Pathway'].dropna().unique().tolist()
    #split elment by ":" and take only the element in position 1
    self.df_pathway[0] = self.df_pathway[0].str.split(':').str[1]
    #delete everything is not on the list
    self.df_pathway = self.df_pathway[self.df_pathway[0].isin(tmp_list)]
    #delete everything except what is on the list
    #self.df_pathway = self.df_pathway[~self.df_pathway[0].isin(tmp_list)]
    #mangage code column to future matching with original df data
  if( hasattr(self, 'query_module') ): #category_to_search['KEGG_Module']):
    #preapre df
    self.df_module = pd.DataFrame()
    #get online information from kegg.com and convert into dataframe
    self.df_module = to_df(self.query_module)
    #take information about module codes from originale df
    need_df = (self.df.assign(KEGG_Module=self.df['KEGG_Module'].str.split('[,;]')).explode('KEGG_Module'))
    tmp_list = need_df['KEGG_Module'].dropna().unique().tolist()
    #split elment by ":" and take only the element in position 1
    self.df_module[0] = self.df_module[0].str.split(':').str[1]
    #delete everything is not on the list
    self.df_module = self.df_module[self.df_module[0].isin(tmp_list)]
    #delete everything except what is on the list
    #self.df_module = self.df_module[~self.df_module[0].isin(tmp_list)]
    #mangage code column to future matching with original df data
  if( hasattr(self, 'query_reaction') ): #category_to_search['KEGG_Reaction']):
    #preapre df
    self.df_reaction = pd.DataFrame()
    #get online information from kegg.com and convert into dataframe
    self.df_reaction = to_df(self.query_reaction)
    #take information about reactions codes from originale df
    need_df = (self.df.assign(KEGG_Reaction=self.df['KEGG_Reaction'].str.split('[,;]')).explode('KEGG_Reaction'))
    tmp_list = need_df['KEGG_Reaction'].dropna().unique().tolist()
    #split elment by ":" and take only the element in position 1
    self.df_reaction[0] = self.df_reaction[0].str.split(':').str[1]
    #delete everything is not on the list
    self.df_reaction = self.df_reaction[self.df_reaction[0].isin(tmp_list)]
    #delete everything except what is on the list
    #self.df_reaction = self.df_reaction[~self.df_reaction[0].isin(tmp_list)]
    #mangage code column to future matching with original df data

#class to upload file
class AsyncUpload(Thread):
  def __init__(self, filepath):
    super().__init__()

    self.filepath = filepath

  def run(self):
    #variable to check if file will be open
    self.fileOpen = True
    #open file with pandas
    try:
      self.df = pd.read_excel(self.filepath)
    except Exception as e:
      #print("===>>" + str(e))
      self.fileOpen = False

#class to upload file exluding some start and end line
class AsyncUpload_2(Thread):
  def __init__(self, filepath):
    super().__init__()

    self.filepath = filepath

  def run(self):
    #variable to check if file will be open
    self.fileOpen = True
    #open file with pandas
    try:
      #remove first 2 and last3 row because are not used
      self.df = pd.read_excel(self.filepath, skiprows=2, skipfooter = 3)
    except Exception as e:
      #print("===>>" + str(e))
      self.fileOpen = False

#class to download file
class AsyncDownload(Thread):
  def __init__(self, df_tmp, file):
    super().__init__()

    self.df_tmp = df_tmp
    self.file = file

  def run(self):
    #variable to check if file will be saved
    self.fileSaved = True
    #open file with pandas
    try:
      #save file with pandas
      self.df_tmp.to_excel(self.file.name, index=False)
    except Exception as e:
      #print("===>>" + str(e))
      self.fileSaved = False

#class to download aggregation files
class AsyncDownload_Aggregation(Thread):
  def __init__(self, df, my_list, params, file_direcotory):
    super().__init__()

    #save the df recived
    self.df = df
    #save the list recived
    self.my_list = my_list
    #params to work
    self.params = params
    #save file_direcotory
    self.file_direcotory = file_direcotory

  def run(self):
    #variable to check if file will be saved
    self.fileSaved = True

    #dictionary to kegg values
    category_to_search = {'KEGG_ko':False, 'KEGG_Pathway':False, 'KEGG_Module':False, 'KEGG_Reaction':False}

    #variable to check connection    
    self.internetWork = True

    #only if online search is request
    if(self.params["keggOnline"]):
      #first of all check for what kegg value is need to search
      for element in self.my_list:
        #by default i put the first element 
        value = element[0]
        #if the element is a aggregation kegg can be only in the second so i put it
        if(len(element) == 2):
          value = element[1]

        #check if the value in the list are one of this to search
        if(value == 'KEGG_ko'):
          category_to_search['KEGG_ko'] = True
        elif(value == 'KEGG_Pathway'):
          category_to_search['KEGG_Pathway'] = True
        elif(value == 'KEGG_Module'):
          category_to_search['KEGG_Module'] = True
        elif(value == 'KEGG_Reaction'):
          category_to_search['KEGG_Reaction'] = True

      #check if is possible get online value of kegg value
      try:
        #try all download here
        if(category_to_search['KEGG_ko']):
          #get online value of KEGG_ko
          self.query_ko = kegg_list("orthology").read()
        if(category_to_search['KEGG_Pathway']):
          #get online value of KEGG_pathway
          self.query_pathway = kegg_list("pathway").read()
        if(category_to_search['KEGG_Module']):
          #get online value of KEGG_module
          self.query_module = kegg_list("module").read()
        if(category_to_search['KEGG_Reaction']):
          #get online value of KEGG_reaction
          self.query_reaction = kegg_list("reaction").read()
      except Exception as e:
        #print("===>>" + str(e))
        self.internetWork = False
        return

      #Manage the online results
      manage_kegg_query(self)

    #for every list element create a file
    for element in self.my_list:
      #get all F cols
      cols = list(self.df.filter(regex=r'F\d+'))
      #add in first place the col_name of column that i want aggragate
      cols.extend(element)
      #create a tmp df
      df_tmp = self.df[cols]

      #First replace empty strings in all columns to mising values:
      df_tmp = df_tmp.replace('', np.nan)

      #prepare filename to save file
      file_path = self.file_direcotory+"/"

      #create a tmp df for supplementary tables
      df_tmp_sup = df_tmp.copy()
      #prepare filename to save supplementary tables
      file_path_sup = self.file_direcotory+"/"

      #check if there are 1 or 2 name
      if(len(element) == 1):
        #take col name
        col_name = element[0]

        #get abundace colums
        aboundance_cols = list(df_tmp.filter(regex=r'F\d+'))

        #re put nan in empty cells
        df_tmp[aboundance_cols] = df_tmp[aboundance_cols].replace({0:np.nan})

        #controls for supplementary tables
        if(self.params["sup_tab"]):
          #re put nan in empty cells
          df_tmp_sup[aboundance_cols] = df_tmp_sup[aboundance_cols].replace({0:np.nan})

          #drop unuseless row
          df_tmp_sup = df_tmp_sup.dropna(subset=[col_name])
          #For the safe I convert this column to a string before split
          df_tmp_sup = df_tmp_sup.astype({col_name: 'str'})

          df_tmp_sup = (df_tmp_sup.assign(new_col=df_tmp_sup[col_name].str.split('[,;]'))
            .explode('new_col')
            .drop_duplicates()
            .groupby('new_col', as_index=False)
            .count())

          #edit file_path_sup
          exstension = ""
          col_count = ""
          if(self.params["mode"] == "proteins"):
            exstension = "-proteins"
            col_count = "Total protein count"
          elif( (self.params["mode"] == 'peptide') or (self.params["mode"] == 'psms') ):
            exstension = "-peptides"
            col_count = "Total peptide count"
          else:
            exstension = "-count"
            col_count = "Total count"

          #raname previus column name to tot
          df_tmp_sup.rename(columns = {col_name:col_count}, inplace = True)
          #rename the tmp col use to explode
          df_tmp_sup.rename(columns = {'new_col':col_name}, inplace = True)
          #remove the new empty values
          df_tmp_sup = df_tmp_sup.replace('', np.nan)
          df_tmp_sup = df_tmp_sup.dropna(subset=[col_name])

          #edit file_path_sup
          file_path_sup = file_path_sup + col_name + exstension + ".xlsx"

        #drop unuseless row
        df_tmp = df_tmp.dropna(subset=[col_name])
        #For the safe I convert this column to a string before split
        df_tmp = df_tmp.astype({col_name: 'str'})

        #create the new file with the sum of aboundances
        df_tmp = (df_tmp.assign(new_col=df_tmp[col_name].str.split('[,;]'))
          .explode('new_col')
          .drop_duplicates()
          .groupby('new_col', as_index=False)
          .sum(min_count=1))

        #rename the tmp col use to explode
        df_tmp.rename(columns = {'new_col':col_name}, inplace = True)

        #remove the new empty values
        df_tmp = df_tmp.replace('', np.nan)
        df_tmp = df_tmp.dropna(subset=[col_name])

        #edit file_path
        file_path = file_path + col_name + ".xlsx"

        ## for df_tmp and df_tmp_sup ##
        #add extra column with description of kegg name
        if( (col_name == "KEGG_ko") and (category_to_search['KEGG_ko']) ):
          #get position for new column
          position_to_insert = df_tmp.columns.get_loc("KEGG_ko")+1
          #crearte a new empty column
          df_tmp.insert(loc=position_to_insert, column="KO name", value=['' for i in range(df_tmp.shape[0])])

          #it looks for all the values of kegg and associates them with the correct description
          for i, row in self.df_ko.iterrows():
            df_tmp["KO name"].where(df_tmp["KEGG_ko"] != row[0], row[1], inplace=True)

          #check for add description also in df_tmp_sup
          if(self.params["sup_tab"]):
            df_tmp_sup.insert(loc=position_to_insert, column="KO name", value=df_tmp["KO name"])

        elif( (col_name == "KEGG_Pathway") and (category_to_search['KEGG_Pathway']) ):
          #get position for new column
          position_to_insert = df_tmp.columns.get_loc("KEGG_Pathway")+1
          #crearte a new empty column
          df_tmp.insert(loc=position_to_insert, column="Pathway name", value=['' for i in range(df_tmp.shape[0])])

          #it looks for all the values of kegg and associates them with the correct description
          for i, row in self.df_pathway.iterrows():
            df_tmp["Pathway name"].where(df_tmp["KEGG_Pathway"] != row[0], row[1], inplace=True)

          #check for add description also in df_tmp_sup
          if(self.params["sup_tab"]):
            df_tmp_sup.insert(loc=position_to_insert, column="Pathway name", value=df_tmp["Pathway name"])

        elif( (col_name == "KEGG_Module") and (category_to_search['KEGG_Module']) ):
          #get position for new column
          position_to_insert = df_tmp.columns.get_loc("KEGG_Module")+1
          #crearte a new empty column
          df_tmp.insert(loc=position_to_insert, column="Module name", value=['' for i in range(df_tmp.shape[0])])

          #it looks for all the values of kegg and associates them with the correct description
          for i, row in self.df_module.iterrows():
            df_tmp["Module name"].where(df_tmp["KEGG_Module"] != row[0], row[1], inplace=True)

          #check for add description also in df_tmp_sup
          if(self.params["sup_tab"]):
            df_tmp_sup.insert(loc=position_to_insert, column="Module name", value=df_tmp["Module name"])

        elif( (col_name == "KEGG_Reaction") and (category_to_search['KEGG_Reaction']) ):
          #get position for new column
          position_to_insert = df_tmp.columns.get_loc("KEGG_Reaction")+1
          #crearte a new empty column
          df_tmp.insert(loc=position_to_insert, column="Reaction name", value=['' for i in range(df_tmp.shape[0])])

          #it looks for all the values of kegg and associates them with the correct description
          for i, row in self.df_reaction.iterrows():
            df_tmp["Reaction name"].where(df_tmp["KEGG_Reaction"] != row[0], row[1], inplace=True)

          #check for add description also in df_tmp_sup
          if(self.params["sup_tab"]):
            df_tmp_sup.insert(loc=position_to_insert, column="Reaction name", value=df_tmp["Reaction name"])

      else:
        #take cols name
        col_name_1 = element[0]
        col_name_2 = element[1]

        #get abundace colums
        aboundance_cols = list(df_tmp.filter(regex=r'F\d+'))

        #re put nan in empty cells
        df_tmp[aboundance_cols] = df_tmp[aboundance_cols].replace({0:np.nan})

        #controls for supplementary tables
        if(self.params["sup_tab"]):
          #re put nan in empty cells
          df_tmp_sup[aboundance_cols] = df_tmp_sup[aboundance_cols].replace({0:np.nan})

          #drop unuseless row
          df_tmp_sup = df_tmp_sup.dropna(subset=[col_name_1, col_name_2])
          #For the safe I convert this column to a string before split
          df_tmp_sup = df_tmp_sup.astype({col_name_2: 'str'})

          df_tmp_sup = (df_tmp_sup.assign(new_col=df_tmp_sup[col_name_2].str.split('[,;]'))
            .explode('new_col')
            .drop_duplicates()
            .groupby([col_name_1, 'new_col'], as_index=False)
            .count())

          #edit file_path_sup
          exstension = ""
          col_count = ""
          if(self.params["mode"] == "proteins"):
            exstension = "-proteins"
            col_count = "Total protein count"
          elif( (self.params["mode"] == 'peptide') or (self.params["mode"] == 'psms') ):
            exstension = "-peptides"
            col_count = "Total peptide count"
          else:
            exstension = "-count"
            col_count = "Total count"

          #raname previus column name to tot
          df_tmp_sup.rename(columns = {col_name_2:col_count}, inplace = True)
          #rename the tmp col use to explode
          df_tmp_sup.rename(columns = {'new_col':col_name_2}, inplace = True)
          #remove the new empty value
          df_tmp_sup = df_tmp_sup.replace('', np.nan)
          df_tmp_sup = df_tmp_sup.dropna(subset=[col_name_1, col_name_2])

          #edit file_path_sup
          file_path_sup = file_path_sup + col_name_1 + "+" + col_name_2 + exstension + ".xlsx"
    
        #drop unuseless row
        df_tmp = df_tmp.dropna(subset=[col_name_1, col_name_2])
        #For the safe I convert this column to a string before split
        df_tmp = df_tmp.astype({col_name_2: 'str'})
 
        #create the new file with the sum of aboundaces
        df_tmp = (df_tmp.assign(new_col=df_tmp[col_name_2].str.split('[,;]'))
              .explode('new_col')
              .drop_duplicates()
              .groupby([col_name_1, 'new_col'], as_index=False)
              .sum(min_count=1))

        #rename the tmp col use to explode
        df_tmp.rename(columns = {'new_col':col_name_2}, inplace = True)

        #remove the new empty value
        df_tmp = df_tmp.replace('', np.nan)
        df_tmp = df_tmp.dropna(subset=[col_name_1, col_name_2])

        #add extra column with description of kegg name
        if( (col_name_2 == "KEGG_ko") and (category_to_search['KEGG_ko']) ):
          #get position for new column
          position_to_insert = df_tmp.columns.get_loc("KEGG_ko")+1
          #crearte a new wmpty column
          df_tmp.insert(loc=position_to_insert, column="KO name", value=['' for i in range(df_tmp.shape[0])])

          #it looks for all the values of kegg and associates them with the correct description
          for i, row in self.df_ko.iterrows():
            df_tmp["KO name"].where(df_tmp["KEGG_ko"] != row[0], row[1], inplace=True)

          #check for add description also in df_tmp_sup
          if(self.params["sup_tab"]):
            df_tmp_sup.insert(loc=position_to_insert, column="KO name", value=df_tmp["KO name"])

        elif( (col_name_2 == "KEGG_Pathway") and (category_to_search['KEGG_Pathway']) ):
          #get position for new column
          position_to_insert = df_tmp.columns.get_loc("KEGG_Pathway")+1
          #crearte a new wmpty column
          df_tmp.insert(loc=position_to_insert, column="Pathway name", value=['' for i in range(df_tmp.shape[0])])

          #it looks for all the values of kegg and associates them with the correct description
          for i, row in self.df_pathway.iterrows():
            df_tmp["Pathway name"].where(df_tmp["KEGG_Pathway"] != row[0], row[1], inplace=True)

          #check for add description also in df_tmp_sup
          if(self.params["sup_tab"]):
            df_tmp_sup.insert(loc=position_to_insert, column="Pathway name", value=df_tmp["Pathway name"])

        elif( (col_name_2 == "KEGG_Module") and (category_to_search['KEGG_Module']) ):
          #get position for new column
          position_to_insert = df_tmp.columns.get_loc("KEGG_Module")+1
          #crearte a new wmpty column
          df_tmp.insert(loc=position_to_insert, column="Module name", value=['' for i in range(df_tmp.shape[0])])

          #it looks for all the values of kegg and associates them with the correct description
          for i, row in self.df_module.iterrows():
            df_tmp["Module name"].where(df_tmp["KEGG_Module"] != row[0], row[1], inplace=True)

          #check for add description also in df_tmp_sup
          if(self.params["sup_tab"]):
            df_tmp_sup.insert(loc=position_to_insert, column="Module name", value=df_tmp["Module name"])

        elif( (col_name_2 == "KEGG_Reaction") and (category_to_search['KEGG_Reaction']) ):
          #get position for new column
          position_to_insert = df_tmp.columns.get_loc("KEGG_Reaction")+1
          #crearte a new wmpty column
          df_tmp.insert(loc=position_to_insert, column="Reaction name", value=['' for i in range(df_tmp.shape[0])])

          #it looks for all the values of kegg and associates them with the correct description
          for i, row in self.df_reaction.iterrows():
            df_tmp["Reaction name"].where(df_tmp["KEGG_Reaction"] != row[0], row[1], inplace=True)

          #check for add description also in df_tmp_sup
          if(self.params["sup_tab"]):
            df_tmp_sup.insert(loc=position_to_insert, column="Reaction name", value=df_tmp["Reaction name"])

        #edit file_path
        file_path = file_path + col_name_1 + "+" + col_name_2 + ".xlsx"

      #control to put zero in empty cells 
      if(self.params['fill0'] == 1):
        #get abundace colums
        sub_set = list(df_tmp.filter(regex=r'F\d+'))
        df_tmp[sub_set] = df_tmp[sub_set].fillna(0)
        if(self.params["sup_tab"]):
          df_tmp_sup[sub_set] = df_tmp_sup[sub_set].fillna(0)

      try:
        #save the file
        df_tmp.to_excel(file_path, index=False)
        if(self.params["sup_tab"]):
          df_tmp_sup.to_excel(file_path_sup, index=False)
      except Exception as e:
        #print("===>>" + str(e))
        self.fileSaved = False

#class to rename files
class AsyncRenameFile(Thread):
  def __init__(self, list_file, df_tm):
    super().__init__()

    #save list of file to edit
    self.list_file = list_file
    #save df template
    self.df_tm = df_tm

  def run(self):
    #variable to check if file will be saved
    self.fileSaved = True

    #variable to check correct lenght of all files
    self.correctLen = True
    len_template = self.df_tm[self.df_tm.columns[0]].count()

    #Take the name from template
    col_one_list = self.df_tm['Old Name'].tolist()
    col_two_list = self.df_tm['New Name'].tolist()
    #iterate for every path
    for filepath in self.list_file:
      #open file
      df = pd.read_excel(filepath)

      #take the old list of "F*" value in order
      cols_len = len(list(df.filter(regex=r'F\d+')))

      #check lenght
      if( cols_len == len_template ):

        #Change all name to take only "F+number" for every intressed colums
        df.columns = df.columns.str.replace(r'.*\b(F\d+)\b.*', r'\1', regex=True)

        #the columns are sorted according to the template
        #take the old list of "F*" value in order
        old_cols = list(df.filter(regex=r'F\d+'))
        #calculate name before and after the "f*" coloums
        before_cols = [col for col in df.columns if df.columns.get_loc(col) < df.columns.get_loc(old_cols[0])]
        after_cols = [col for col in df.columns if df.columns.get_loc(col) > df.columns.get_loc(old_cols[-1])]
        #reorder df according to the new order
        df = df[before_cols+col_one_list+after_cols]      

        for i in range(len(col_one_list)):
          df.rename(columns = {col_one_list[i]:col_two_list[i]}, inplace = True)

        #check to save file  
        try:
          #save new file in the same start place
          df.to_excel(filepath, index=False)
        except Exception as e:
          #print("===>>" + str(e))
          self.fileSaved = False
      else:
        self.correctLen = False
      
#class to manage file on protein window
class ManageProtein(Thread):
  def __init__(self, window):
    super().__init__()

    #take window data
    self.window = window

  def run(self):
    #take a copy of window to do controls
    window = self.window
    #create a copy for finale edits
    df_final = window.df.copy()

    #control for Protein FDR
    if(window.var_chc_low.get() == 0 ):
      df_final.drop(df_final.index[df_final['Protein FDR Confidence: Combined'] == 'Low'], inplace=True)
    if(window.var_chc_medium.get() == 0 ):
      df_final.drop(df_final.index[df_final['Protein FDR Confidence: Combined'] == 'Medium'], inplace=True)
    if(window.var_chc_high.get() == 0 ):
      df_final.drop(df_final.index[df_final['Protein FDR Confidence: Combined'] == 'High'], inplace=True)

    #For description
    #get content of description listbox
    get_content = window.dsc_listbox.get(0, END)
    #make list for remove row
    toSearch = []
    for con_item in get_content:
      toSearch.append(con_item)
    #delete rows that do not contain any words in the column
    if(window.rdb_var.get()=='or'):
      df_final = df_final[df_final["Description"].str.contains('|'.join(toSearch)) == True]
    elif(window.rdb_var.get()=='and'):
      base = r'^{}'
      expr = '(?=.*{})'
      toSearch = base.format(''.join(expr.format(w) for w in toSearch))
      df_final = df_final[df_final["Description"].str.contains(toSearch) == True]
    #finally edit the cells for remove "newline"(\n) and put ";"
    df_final['Description'] = df_final['Description'].str.replace("\n","; ")
    
    #control for marked as
    i = 0
    for marked in window.chcs_marked:
      if(window.var_chcs_marked[i].get() == 0):
        #print(marked.cget("text"))
        df_final.drop(df_final.index[df_final['Marked as'] == marked.cget("text")], inplace=True)
      i = i+1

    #control for master protein
    if(window.var_chc_master.get() == 1):
      df_final.drop(df_final.index[df_final['Master'] != 'Master Protein'], inplace=True)

    #get abundace colums
    sub_set = list(df_final.filter(regex=r'F\d+'))

    #control for abundance
    num_abundance = 0
    if(window.opt_abundance_var.get() == 'Absolute'):
      num_abundance = int(window.ntr_abundance.get())
    elif(window.opt_abundance_var.get() == 'Percentage'):
      #get number of columns
      num_cols = len(sub_set)
      #calcolate num
      num_abundance = window.proper_round((int(window.ntr_abundance.get()) * num_cols)/100)
    #delete all row width 'num_cols' empty in Aboundance(F1,F2..) columns
    df_final = df_final.dropna(subset=sub_set, thresh=num_abundance)

    #control for normalized
    if(window.var_chc_normalized.get() == 1):
      df_final.drop(list(df_final.filter(regex = 'Abundance:')), axis = 1, inplace = True)
    else:
      df_final.drop(list(df_final.filter(regex = 'Normalized')), axis = 1, inplace = True)

    #recreate abundace colums after drop some
    sub_set = list(df_final.filter(regex=r'F\d+'))

    #control for Re-Normalized
    if(window.var_chc_re_normalized.get() == 1):
      #RE-Normalize all colums
      for col_name in sub_set:
        df_final[col_name] = ( df_final[col_name]/df_final[col_name].sum() ) * 10000000000

    #control to put zero in empty cells
    if(window.var_chc_fill_zero.get() == 1):
      df_final[sub_set] = df_final[sub_set].fillna(0)

    #save edit df in tmp variable
    window.df_tmp = df_final

#class to manage file on peptide window
class ManagePeptide(Thread):
  def __init__(self, window):
    super().__init__()

    #take window data
    self.window = window

  def run(self):
    #take a copy of window to do controls
    window = self.window
    #create a copy for finale edits
    df_final = window.df.copy()

    #control for Protein FDR
    if(window.var_chc_low.get()==0 ):
      df_final.drop(df_final.index[df_final['Confidence'] == 'Low'], inplace=True)   
    if(window.var_chc_medium.get() == 0 ):
      df_final.drop(df_final.index[df_final['Confidence'] == 'Medium'], inplace=True)    
    if(window.var_chc_high.get() == 0 ):
      df_final.drop(df_final.index[df_final['Confidence'] == 'High'], inplace=True)

    #control for normalized
    if(window.var_chc_normalized.get() == 1):
      df_final.drop(list(df_final.filter(regex = 'Abundance:')), axis = 1, inplace = True)
    else:
      df_final.drop(list(df_final.filter(regex = 'Normalized')), axis = 1, inplace = True)

    #For Master Proterin Descriptions
    #make list for remove row
    toSearch = []
    for label in window.lbls_description:
      toSearch.append(label.cget("text"))
    #delete rows that do not contain any words in the column
    if(window.rdb_var.get()=='or'):
      df_final = df_final[df_final["Master Protein Descriptions"].str.contains('|'.join(toSearch)) == True]
    elif(window.rdb_var.get()=='and'):
      base = r'^{}'
      expr = '(?=.*{})'
      toSearch = base.format(''.join(expr.format(w) for w in toSearch))
      df_final = df_final[df_final["Master Protein Descriptions"].str.contains(toSearch) == True]
    #finally edit the cells for remove "newline"(\n) and put ";"
    df_final['Master Protein Descriptions'] = df_final['Master Protein Descriptions'].str.replace("\n","; ")

    #control for Protein Accessions
    if(window.var_chc_ptrAccessions.get() == 0):
      df_final.drop(['Protein Accessions'], inplace=True, axis=1, errors='ignore')

    #control for marked as
    i = 0
    for marked in window.chcs_marked:
      if(window.var_chcs_marked[i].get() == 0):
        df_final.drop(df_final.index[df_final['Marked as'] == marked.cget("text")], inplace=True)
      i = i+1

    #control for Quan Info
    i = 0
    for quan in window.chcs_quant:
      if(window.var_chcs_quant[i].get() == 0):
        df_final.drop(df_final.index[df_final['Quan Info'] == quan.cget("text")], inplace=True)
      i = i+1

    #get abundace colums
    sub_set = list(df_final.filter(regex=r'F\d+'))

    #recreate abundace colums after drop some
    sub_set = list(df_final.filter(regex=r'F\d+'))

    #control for Re-Normalized
    if(window.var_chc_re_normalized.get() == 1):
      #RE-Normalize all colums
      for col_name in sub_set:
        df_final[col_name] = ( df_final[col_name]/df_final[col_name].sum() ) * 10000000000

    #remove duplicate Sequence (cause of Protoeme Discovery bug)
    #create a list for Abundance cols
    abn_list = list(df_final.filter(regex=r'F\d+'))
    #create a list for all cols
    c_list = list(df_final.columns)
    #remove Sequence (because used for groupby)
    c_list.remove('Sequence')
    #remove all Abundance (because used for sum)
    c_list = [i for i in c_list if i not in abn_list]
    #aggregate by sequence and sum Abundance
    df_final = df_final.groupby('Sequence').agg({**dict.fromkeys(c_list, 'first'), **dict.fromkeys(abn_list, 'sum') }).reset_index()
    #re-swap "Sequence"(first columns) and "Confidence"(second columns)
    # get a list of the columns
    col_list = list(df_final)
    # use this handy way to swap the elements
    col_list[0], col_list[1] = col_list[1], col_list[0]
    # assign back, the order will now be swapped
    df_final = df_final[col_list]
    #re put nan in empty cells
    df_final[abn_list] = df_final[abn_list].replace({0:np.nan})

    #control for abundance (valid values)
    num_abundance = 0
    if(window.opt_abundance_var.get() == 'Absolute'):
      num_abundance = int(window.ntr_abundance.get())
    elif(window.opt_abundance_var.get() == 'Percentage'):
      #get abundace colums
      sub_set = list(df_final.filter(regex=r'F\d+'))
      #get number of columns
      num_cols = len(sub_set)
      #calcolate num
      num_abundance = window.proper_round((int(window.ntr_abundance.get()) * num_cols)/100)
    #delete all row width 'num_cols' empty in Aboundance(F1,F2..) columns
    df_final = df_final.dropna(subset=sub_set, thresh=num_abundance)

    #control to put zero in empty cells
    if(window.var_chc_fill_zero.get() == 1):
      df_final[sub_set] = df_final[sub_set].fillna(0)

    #save edit df in tmp variable
    window.df_tmp = df_final

#class to manage file on PSMs window
class ManagePSMs(Thread):
  def __init__(self, window):
    super().__init__()

    #take window data
    self.window = window

  def run(self):
    #take a copy of window to do controls
    window = self.window
    #create a copy for finale edits
    df_final = window.df.copy()

    #control for Protein FDR
    if(window.var_chc_low.get()==0 ):
      df_final.drop(df_final.index[df_final['Confidence'] == 'Low'], inplace=True)   
    if(window.var_chc_medium.get() == 0 ):
      df_final.drop(df_final.index[df_final['Confidence'] == 'Medium'], inplace=True)    
    if(window.var_chc_high.get() == 0 ):
      df_final.drop(df_final.index[df_final['Confidence'] == 'High'], inplace=True)

    #For Master Proterin Descriptions
    #make list for remove row
    toSearch = []
    for label in window.lbls_description:
      toSearch.append(label.cget("text"))
    #delete rows that do not contain any words in the column
    if(window.rdb_var.get()=='or'):
      df_final = df_final[df_final["Master Protein Descriptions"].str.contains('|'.join(toSearch)) == True]
    elif(window.rdb_var.get()=='and'):
      base = r'^{}'
      expr = '(?=.*{})'
      toSearch = base.format(''.join(expr.format(w) for w in toSearch))
      df_final = df_final[df_final["Master Protein Descriptions"].str.contains(toSearch) == True]
    #finally edit the cells for remove "newline"(\n) and put ";"
    df_final['Master Protein Descriptions'] = df_final['Master Protein Descriptions'].str.replace("\n","; ")

    #control for marked as
    i = 0
    for marked in window.chcs_marked:
      if(window.var_chcs_marked[i].get() == 0):
        df_final.drop(df_final.index[df_final['Marked as'] == marked.cget("text")], inplace=True)
      i = i+1

    #prepare pivot table
    table = pd.pivot_table(data=df_final,
                           index=['Sequence'],
                           columns=['File ID'],
                           aggfunc='size')
                           #fill_value=0) if I want fill Nan with 0
    
    #table.columns = table.columns.droplevel(0) #remove first line
    table.columns.name = None               #File id
    table = table.reset_index()                #index to columns

    #marge original file with table
    df_final = df_final.merge(table, left_on='Sequence', right_on='Sequence', how='left')

    #remove duplicate
    df_final = df_final.drop_duplicates(subset='Sequence', keep="last")

    #remove "File ID" column
    df_final.drop(['File ID'], inplace=True, axis=1, errors='ignore')

    #reorder F columns
    num = df_final.columns.str.extract('F(\d+)', expand=False).astype(float)
    cols = df_final.columns.to_numpy(copy=True)
    m = num.notna()
    order = np.argsort(num[m])
    cols[m] = cols[m][order]
    df_final = df_final[cols]


    #df.loc[df['temp']==0, 'temp'] = np.nan
    #control to put zero in empty cells 
    if(window.var_chc_fill_zero.get() == 1):
      #get abundace colums
      sub_set = list(df_final.filter(regex=r'F\d+'))
      df_final[sub_set] = df_final[sub_set].fillna(0)

    #save edit df in tmp variable
    window.df_tmp = df_final

#class to manage file on Taxonomic window
class ManageTaxonomic(Thread):
  def __init__(self, window):
    super().__init__()

    #take window data
    self.window = window

  def run(self):
    #take a copy of window to do controls
    window = self.window
    #create a copy for finale edits
    df_final = window.df.copy()
    df_final_annotation = window.df_annotation.copy()

    #if mode is not proteins we need to add one columns
    if(window.workDict["mode"] != 'proteins'):
      #add duplicate of sequence column
      #make copy of Sequence column
      column_to_duplicate = df_final['Sequence']
      #get the position of the original sequence column 
      position_to_insert = df_final.columns.get_loc("Sequence")+1
      #put new duplicate column next to original sequence
      df_final.insert(position_to_insert, "Sequence(I=L)", column_to_duplicate)
      #change all I with L
      df_final['Sequence(I=L)'] = df_final['Sequence(I=L)'].replace('I','L', regex=True)

    #merge files
    if(window.workDict["mode"] == 'proteins'):
      colname = df_final_annotation.columns[0]
      df_final = df_final.merge(df_final_annotation, left_on='Accession', right_on=colname, how='left')
      df_final.drop(['Accession No.'], inplace=True, axis=1, errors='ignore')
    else:
      df_final = df_final.merge(df_final_annotation, left_on='Sequence(I=L)', right_on='peptide', how='left')
      df_final.drop(['peptide'], inplace=True, axis=1, errors='ignore')

    #control to put zero in empty cells 
    if(window.workDict['fill0'] == 1):
      #get abundace colums
      sub_set = list(df_final.filter(regex=r'F\d+'))
      df_final[sub_set] = df_final[sub_set].fillna(0)

    #save edit df in tmp variable
    window.df_tmp = df_final

#class to manage file on Functional window
class ManageFunctional(Thread):
  def __init__(self, window):
    super().__init__()

    #take window data
    self.window = window

  def run(self):
    #take a copy of window to do controls
    window = self.window
    #create a copy for finale edits
    df_final = window.df.copy()
    df_final_annotation = window.df_annotation.copy()

    #remove all "-" in the cells
    df_final.replace("-","",inplace=True)
    df_final_annotation.replace("-","",inplace=True)

    #Check if i need to take information starting from protein file or another
    if(window.workDict["mode"] != 'proteins'):
      df_final = (df_final.assign(query = df_final['Master Protein Accessions'].str.split('; '))
               .explode('query')
               .reset_index()
               .merge(df_final_annotation, how='left', on='query')
               .fillna('')
               .astype(dict.fromkeys(df_final_annotation, str))
               .groupby('index')
               .agg({**dict.fromkeys(df_final, 'first'), **dict.fromkeys(df_final_annotation, ';'.join)})
               .rename_axis(None))
    else:
      df_final = (df_final.assign(query = df_final['Accession'].str.split('; '))
         .explode('query')
         .reset_index()
         .merge(df_final_annotation, how='left', on='query')
         .fillna('')
         .astype(dict.fromkeys(df_final_annotation, str))
         .groupby('index')
         .agg({**dict.fromkeys(df_final, 'first'), **dict.fromkeys(df_final_annotation, ';'.join)})
         .rename_axis(None))

    #remove a unused coloum
    df_final.drop(['query'], inplace=True, axis=1, errors='ignore')

    #Replace column values if it repeats the same ";" character
    df_final = df_final.mask(df_final.applymap(lambda x: isinstance(x, str) and set(x) == {';'}), '')
    #other method
    #cols = ['col_1','col_2']
    #df[cols] = df[cols].replace(r'^;{1,}$','', regex=True)

    #control to put zero in empty cells 
    if(window.workDict['fill0'] == 1):
      #get abundace colums
      sub_set = list(df_final.filter(regex=r'F\d+'))
      df_final[sub_set] = df_final[sub_set].fillna(0)

    #Control to get KEGG data
    if(window.var_chc_kegg_description.get() == 1):
      #Variable to monitorize internet work
      self.internetWork = True
      #check if is possible get online value of kegg value
      try:
        #try all download here
        #get online value of KEGG_ko
        self.query_ko = kegg_list("orthology").read()
        #get online value of KEGG_pathway
        self.query_pathway = kegg_list("pathway").read()
        #get online value of KEGG_module
        self.query_module = kegg_list("module").read()
        #get online value of KEGG_reaction
        self.query_reaction = kegg_list("reaction").read()
      except Exception as e:
        #print("===>>" + str(e))
        self.internetWork = False
        return

      #save local df copy
      self.df = df_final
      #Manage the online results
      manage_kegg_query(self)

      #add extra column with description of kegg name
      ### KEGG KO ###
      position_to_insert = df_final.columns.get_loc("KEGG_ko")+1
      #crearte a new empty column
      df_final.insert(loc=position_to_insert, column="KO name", value=['' for i in range(df_final.shape[0])])
      #rename to use
      self.df_ko.rename(columns={0:'Name', 1:'Description'}, inplace=True)
      #mapper
      mapper = self.df_ko.set_index('Name')['Description'].to_dict()
      regex = '|'.join(self.df_ko['Name'])
      # 'ko:123|ko:111|ko:222|ko:333|ko:444|ko:555'
      df_final['KO name'] = df_final['KEGG_ko'].str.replace(regex, lambda m: mapper.get(m.group()), regex=True)

      ### KEGG Pathway ###
      #get position for new column
      position_to_insert = df_final.columns.get_loc("KEGG_Pathway")+1
      #crearte a new empty column
      df_final.insert(loc=position_to_insert, column="Pathway name", value=['' for i in range(df_final.shape[0])])
      #rename to use
      self.df_pathway.rename(columns={0:'Name', 1:'Description'}, inplace=True)
      #mapper
      mapper = self.df_pathway.set_index('Name')['Description'].to_dict()
      regex = '|'.join(self.df_pathway['Name'])
      # 'ko:123|ko:111|ko:222|ko:333|ko:444|ko:555'
      df_final['Pathway name'] = df_final['KEGG_Pathway'].str.replace(regex, lambda m: mapper.get(m.group()), regex=True)

      ### KEGG Module ###
      #get position for new column
      position_to_insert = df_final.columns.get_loc("KEGG_Module")+1
      #crearte a new empty column
      df_final.insert(loc=position_to_insert, column="Module name", value=['' for i in range(df_final.shape[0])])
      #rename to use
      self.df_module.rename(columns={0:'Name', 1:'Description'}, inplace=True)
      #mapper
      mapper = self.df_module.set_index('Name')['Description'].to_dict()
      regex = '|'.join(self.df_module['Name'])
      # 'ko:123|ko:111|ko:222|ko:333|ko:444|ko:555'
      #df_final['Module name'] = df_final['KEGG_Module'].str.replace(regex, lambda m: mapper.get(m.group()), regex=True)
      df_final['Module name'] = df_final['KEGG_Module'].str.replace(',', '|', regex=False).str.replace(regex, lambda m: mapper.get(m.group()), regex=True)

      ### KEGG Reaction ###
      #get position for new column
      position_to_insert = df_final.columns.get_loc("KEGG_Reaction")+1
      #crearte a new empty column
      df_final.insert(loc=position_to_insert, column="Reaction name", value=['' for i in range(df_final.shape[0])])
      #rename to use
      self.df_reaction.rename(columns={0:'Name', 1:'Description'}, inplace=True)
      #mapper
      mapper = self.df_reaction.set_index('Name')['Description'].to_dict()
      regex = '|'.join(self.df_reaction['Name'])
      # 'ko:123|ko:111|ko:222|ko:333|ko:444|ko:555'
      #df_final['Reaction name'] = df_final['KEGG_Reaction'].str.replace(regex, lambda m: mapper.get(m.group()), regex=True)
      df_final['Reaction name'] = df_final['KEGG_Reaction'].str.replace(';', '|', regex=False).str.replace(regex, lambda m: mapper.get(m.group()), regex=True)

    #save edit df in tmp variable
    window.df_tmp = df_final



### Old code ###
'''
df_tmp_2 = (df_tmp.assign(new_col=df_tmp[col_name].str.split('[,;]'))
.explode('new_col')
.groupby('new_col', as_index=False)
.count())
#edit file_path
df_tmp_2.to_excel(file_path + "NUM_" + col_name + ".xlsx", index=False) 

#rename col by position not by name
df_tmp_sup.rename(columns = {df_tmp_sup.columns[0]:col_name, df_tmp_sup.columns[1]:col_count}, inplace = True)
#kepp only the firt two coloumns
df_tmp_sup = df_tmp_sup.iloc[:, :2]
'''

'''
#old rename
#change every columns name according to template (i need to start from the higest value and go to the smallest)
for i in range(len(col_one_list)-1, -1, -1 ):
  #using the previously ordered columns I start from the last one and go towards the first "F"
  index_to_do = col_one_list.index(old_cols[i])
  df.columns = df.columns.str.replace(col_one_list[index_to_do], col_two_list[index_to_do])
'''