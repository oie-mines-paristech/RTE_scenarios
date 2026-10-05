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
from lib.utils import import_xls_list_df
from lib.utils_graph import change_plot_order,plot_bar_graph_contrib


analyses=[
    {
    "analysis_type":"contrib",
    "rows":[1,2,7,10],
    "column":'contribution to impact'
    },
    {
    "analysis_type":"incremental",
    "rows":[5,6,10,9],
    "column":'contribution to difference',
    }
]

mainfolder='image-SSP2-M'
#mainfolder='tiam-SSP2-RCP45'

graph_param=[
    {'order':[6,4,1]},
    {'order':[3,2,1]},
    {'order':[6,5,4,3,2,1]}
    ]
scenarios='FR'
subplot_size=(1,4)

# mainfolder='scenarios-RCP45-M0'
# order=[4,0,2,3,1,5,6]
# graph_param=[
#     {'order':order},
#     ]
# scenarios='IAM'
# subplot_size=(2,9)


#0. initialisation
datapath=DATA_OUT_FOLDER+'/'+mainfolder
mainpath=GRAPH_FOLDER+'/'+mainfolder

for g in graph_param:
    for analysis in analyses:
        for folder in [
                    GRAPH_FOLDER,
                    mainpath,
                    mainpath+'/'+analysis["analysis_type"],
                    mainpath+'/'+analysis["analysis_type"]+'/'+str(str(g['order']))
                    ]:
            if not os.path.exists(folder):
                os.makedirs(folder)

#1. Load data
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


    #plot
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
                    add_number_percentage="number",
                    add_prod_mix=1,
                    add_conso_mix=1,
                    add_percentage=1,
                    add_PVwind=True,

                    subplot_size=subplot_size,
                    #width=
                    sharey=False,
                    pos_legend=(0.5, -2),
                    
                    size_title=17,
                    size_subplot_title=15,
                    size_xaxis=15,
                    size_yaxis=15,
                    size_absolute_value=14,
                    size_percentage=13,
                    size_legend=10,

)


