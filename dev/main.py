# INITIALISATION

#Import usefull packages
from premise import *
from datapackage import Package
import bw2data
import bw2io
import pandas as pd
import numpy as np
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import os as os
#import lca_algebraic as agb

#import custom functions
from lib.utils import init, generate_premise_dbs,generate_premise_db_list,tag_premise_dbs
from lib.utils import save_xls, import_xls_list_df
from lib.utils import create_empty_act, change_input_storage_mix, storage_input_mix_name
from activities_type_label import *

#import climate change impact method that is updated by premise
from premise_gwp import add_premise_gwp

#import static data for database generation
from lib.static_transversal import *
from lib.static_database_generation import *

#0. initialisation
init()

#1. Generate databases
#Generate databases
if generate_db:
        generate_premise_db(list_scenarios)

#generate a list and table of databases
premise_db_list=generate_premise_db_list()
df_premise_db_list=tag_premise_dbs(premise_db_list, DATA_OUT_FOLDER)
print(len(df_premise_db_list),'premise databases were generated and tagged')

#2. Modify databases
