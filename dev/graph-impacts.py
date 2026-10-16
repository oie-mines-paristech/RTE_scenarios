# INITIALISATION

#Import usefull packages
import pandas as pd
import numpy as np
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import os as os

#import static data for database generation
from lib.static_transversal import *
from lib.static_impact import *

#import specific functions
from lib.utils import import_xls_list_df
from lib.utils_graph import (
    change_plot_order,
    plot_bar_graph_contrib,
    plot_impact_category_overview,
)

#Choose if you want to compare FR scenarios or same FR scenario with different IAM scenarios
scenarios='FR'
# scenarios='IAM'

#Define the analyses to be performed
analyses=[
    {
    "analysis_type":"aggregated", 
    "column":'contribution to impact', #column name in list_df_ca_aggreg_ter to be used for plotting
    "rows":[1,2,7,10], #rows number in list_df_ca_aggreg_ter to be used for plotting
    "impact_cat":[ #selected impact categories to be plotted in the overview graph
        "acidification",
        "climate change adapted",
        "material resources:metals minerals",
        "particulate matter formation",
        "water use",
        "ionising radiation:human health"
        ],
    "title_graph":"Domestic generation and supply mix impacts per kWh",#title of the overview graph
    "contrib_anal":False,
    "ncols":3,
    },
    {
    "analysis_type":"incremental",
    "column":'contribution to difference',
    "rows":[5,6,10,9],
    "impact_cat":[
        "acidification",
        "climate change adapted",
        "material resources:metals minerals",
        "water use"
        ],
    "title_graph":"Incremental effect analysis",
    "contrib_anal":True,
    "ncols":2,
    }
]


#Set-up for FR and IAM scenatrios
if scenarios=='FR':
    mainfolders=[ #name of the folders in DATA_OUT_FOLDER that contain the data to be plotted
        'image-SSP2-M',
        #'tiam-SSP2-RCP45'
    ]

    graph_param=[  #Order of the scenarios to be plotted in the graphs. The order is defined by the index of the scenarios in the list_df_ca_aggreg_ter
        {'order':[6,4,1]},
        #{'order':[3,2,1]},
        #{'order':[6,5,4,3,2,1]}
        ]
    
    subplot_size=(1,4) 

if scenarios=='IAM':
    mainfolders=['scenarios-RCP45-M0']
    order=[4,0,2,3,1,5,6]
    graph_param=[
        {'order':order},
        ]
    subplot_size=(2,9)



plot_options = {
    'add_number_percentage': 'number',
    'add_prod_mix': 1,
    'add_conso_mix': 1,
    'add_percentage': 1,
    'add_PVwind': True,
    'subplot_size': subplot_size,
    'sharey': False,
    'pos_legend': (0.5, -2),
    'size_title': 17,
    'size_subplot_title': 15,
    'size_xaxis': 15,
    'size_yaxis': 15,
    'size_absolute_value': 14,
    'size_percentage': 13,
    'size_legend': 15,
}

for mainfolder in mainfolders:
    datapath=DATA_OUT_FOLDER+'/'+mainfolder
    mainpath=GRAPH_FOLDER+'/'+mainfolder

    for g in graph_param:
        for analysis in analyses:
            for folder in [
                GRAPH_FOLDER,
                mainpath,
                mainpath+'/'+analysis["analysis_type"],
                mainpath+'/'+analysis["analysis_type"]+'/'+str(g['order']),
            ]:
                if not os.path.exists(folder):
                    os.makedirs(folder)

    #Load data
    impact_data_by_category = {}
    for impact in os.listdir(datapath):
        #load data
        full_datapath=datapath+'/'+impact
        list_df_ca_aggreg=import_xls_list_df(full_datapath+'/'+'list_df_ca_aggreg.xlsx')
        list_df_ca_aggreg_bis=import_xls_list_df(full_datapath+'/'+'list_df_ca_aggreg_bis.xlsx')
        list_df_ca_aggreg_ter=import_xls_list_df(full_datapath+'/'+'list_df_ca_aggregg_ter.xlsx')

        #modify data 
        for df in list_df_ca_aggreg:
            df['hatch']=None
            df['year']=df['year'].astype('Int64')
        for df in list_df_ca_aggreg_bis:
            df['hatch']=None
            df.loc[(df['label']=="electricity from storage replaced by production mix"),'hatch']="///"
            df.loc[(df['label']=="storage losses and infrastructure"),'hatch']='++'
            df.loc[(df['label']=="electricity from imports replaced by production mix"),'hatch']="///"
            df.loc[(df['label']=='differential impacts due to imports'),'hatch']='++'
            df['year']=df['year'].astype('Int64')
        for df in list_df_ca_aggreg_ter:
            df['hatch']=None
            df['contribution to difference % 100']=100*df['contribution to difference %']
            df.loc[(df['label']=="electricity from storage replaced by production mix"),'hatch']="///"
            df.loc[(df['label']=="electricity from imports replaced by production mix"),'hatch']="///"
            df.loc[df['label'] == 'storage losses','hatch']='--'
            df.loc[df['label'] == 'storage infrastructure','hatch']='|'
            df.loc[(df['label']=="storage losses and infrastructure"),'hatch']='+'
            df.loc[(df['label']=='differential impacts due to imports'),'hatch']='+'
            df['year']=df['year'].astype('Int64')

        impact_data_by_category[impact] = list_df_ca_aggreg_ter

        #plot individual graphs per impact categor
        for analysis in analyses:
            for g in graph_param:
                    list_df_to_plot=change_plot_order(list_df_ca_aggreg_ter,g['order'])
                    list_dict_to_plot=[]
                    dict_to_plot={
                            "list_df_to_plot":list_df_to_plot,
                            "rows":analysis["rows"],
                            "column":analysis["column"]
                        }
                    list_dict_to_plot.append(dict_to_plot)

                    plot_bar_graph_contrib(
                        list_dict_to_plot=list_dict_to_plot,
                        #ax_titles=["Contribution analysis","Differential analysis"],
                        scenarios=scenarios,
                        fig_path=mainpath+'/'+analysis["analysis_type"]+'/'+str(str(g['order']))+'/'+impact+'_'+mainfolder+'.png',
                        legend_path=mainpath+'/'+analysis["analysis_type"]+'/',
                        contrib_anal=analysis['contrib_anal'],
                        **plot_options,
                    )

    #plot overview graph for each analysis type
    for analysis in analyses:
        for g in graph_param:
            order_path = mainpath+'/'+analysis["analysis_type"]+'/'+str(g['order'])
            plot_impact_category_overview(
                impact_categories=analysis["impact_cat"],
                impact_data=impact_data_by_category,
                order=g['order'],
                rows=analysis["rows"],
                column=analysis["column"],
                output_path=order_path+'/0_'+analysis["analysis_type"]+'_'+mainfolder+'.png',
                title=analysis["title_graph"],
                scenarios=scenarios,
                subplot_size=subplot_size,
                contrib_anal=analysis['contrib_anal'],
                ncols=analysis['ncols'],
                plot_options=plot_options,
            )


