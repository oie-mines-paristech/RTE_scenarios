#Check the calculation set up in lib.static_transversal

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
import numpy as np
#import lca_algebraic as agb

#import custom functions
from lib.utils import init,generate_list_scenarios, generate_premise_dbs,generate_premise_db_list,tag_premise_dbs,extract_scenario_data
from lib.utils import save_xls, import_xls_list_df
from lib.utils import change_input_storage_mix
from lib.utils_impact import ca_aggreg, ca_disaggreg_storage, ca_disaggreg_ter

#import climate change impact method that is updated by premise
from premise_gwp import add_premise_gwp

#import static data for database generation
from lib.static_transversal import *
from lib.static_database_generation import *
from lib.static_impact import *


#0. initialisation
init()
print ('INFO : ignore the warning')

#1. Generate databases

if generate_db:
        #Generate the list of scenarios
        fp = "../datapackage.json"
        rte = Package(fp)
        list_scenarios=generate_list_scenarios(rte)
        #for scenario in list_scenarios:
        #        print(scenario)

        # Generate databases
        generate_premise_dbs(list_scenarios)
        #Add climate change premise (incl.H2 and biogenic CO2)
        add_premise_gwp()

# Generate a list and table of databases
premise_db_list=generate_premise_db_list()
df_premise_db_list=tag_premise_dbs(premise_db_list, DATA_OUT_FOLDER)
print('INFO: ',len(df_premise_db_list),'premise databases were generated and tagged')

#Extract RTE Data only for database generated with image_SSP2-M
if extract_RTE_data:
       extract_scenario_data(generate_premise_db_list(filter='image_SSP2-M'))

#2. Impacts
#Check that impacts are bw2 methods
for impact_cat in impacts:
    print(impact_cat, bw2data.Method(impact_cat).metadata['unit'])


# Choose configuration

configurations=[
        {
        "selected_db_list":[db for db in premise_db_list if db.model=='image' and db.SSP=='SSP2' and db.RCP=='M' and '2026-10-16' not in db.name],
        "mainfolder":'test',
        "selected_impacts": [climate],
        "curtailment_included":True,
        },

        # {
        # "selected_db_list":[db for db in premise_db_list if db.model=='image' and db.SSP=='SSP2' and db.RCP=='M'],
        # "mainfolder":'image-SSP2-M',
        # "selected_impacts": impacts,
        # "curtailment_included":True,
        # },
        # {
        # "selected_db_list":[db for db in premise_db_list if db.model=='tiam-ucl' and db.SSP=='SSP2' and db.RCP=='RCP45'],
        # "mainfolder":'tiam-SSP2-RCP45',
        # "selected_impacts":impacts,
        # "curtailment_included":True,
        # },
        # {
        # "selected_db_list":[db for db in premise_db_list if db.FR_scenario=='M0'],
        # "mainfolder":'scenarios-RCP45-M0',
        # "selected_impacts":impacts,
        # "curtailment_included":True,
        # }
]


if run_calc:
        for config in configurations:
                for db in config["selected_db_list"]:
                        print(db.name)
                for impact_cat in config["selected_impacts"]:
                        print(impact_cat[1])

                #aggregated contribution analysis
                df_curtailment=import_xls_list_df('lib/curtailed_electricity.xlsx')[0]
                results=ca_aggreg(config["mainfolder"],config["selected_db_list"],config["selected_impacts"],config["curtailment_included"],df_curtailment)
                ca_aggreg=results[0]
                ca_aggreg_bis=results[1]

                #disaggregation of storage
                results=ca_disaggreg_storage(config["mainfolder"],config["selected_db_list"],config["selected_impacts"])
                ca_storage=results[0]
                list_df_storage_efficiency=results[1]

                #ca_disaggreg_ter
                ca_aggreg_ter=ca_disaggreg_ter(config["mainfolder"],config["selected_db_list"],config["selected_impacts"],ca_aggreg_bis,ca_storage)
