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
from lib.utils_graph import change_plot_order, plot_bar_graph_french_scenarios, plot_bar_graph_french_scenarios_double

mainfolder='image-SSP2-M'
order1=[0,6,4,1]
order2=[0,6,5,4,3,2,1]
plot1=True
plot2=True
plot3=True

#0. initialisation
datapath=DATA_OUT_FOLDER+'/'+RTE_FOLDER+'/'
mainpath=GRAPH_FOLDER+'/'+RTE_FOLDER+'/'
for folder in [GRAPH_FOLDER,mainpath]:
        if not os.path.exists(folder):
            os.makedirs(folder)

#1. Load data
list_df_mix=import_xls_list_df(datapath+'list_df_mix.xlsx')
list_df_prod_mix=import_xls_list_df(datapath+'list_df_prod_mix.xlsx')
list_df_to_plot_storage_mix=import_xls_list_df(datapath+'list_df_to_plot_storage_mix.xlsx')
list_df_to_plot_storage_mix_empty=import_xls_list_df(datapath+'list_df_to_plot_storage_mix_empty.xlsx')
list_df_ca_aggreg=import_xls_list_df(DATA_OUT_FOLDER+'/'+mainfolder+'/'+'climate change'+'/'+'list_df_ca_aggreg.xlsx')

#Modify data
for df in list_df_prod_mix:
    df["percentage production technology 100"]=df["percentage production technology"]*100
for df in list_df_to_plot_storage_mix:
    df['amount 100']=100*df['amount']
    df['percentage storage technology 100']=100* df['percentage storage technology']
for df in list_df_ca_aggreg:
    df['amount (kWh) 100']=100*df['amount (kWh)']


#Consumption mix
graphs_conso=[
    {'order':order1,'size':(2.2, 3)},
    {'order':order2,'size':(4.4,3)}
    ]

graphs_storage=[
    {'order':order1,'size':(4.4, 3)},
    {'order':order2,'size':(8.8,3)}
    ]

if plot1:
        for g in graphs_conso:
                list_df_to_plot=change_plot_order(list_df_ca_aggreg,g['order'])
                plot_bar_graph_french_scenarios(
                list_df_to_plot=list_df_to_plot, 
                column='amount (kWh) 100', 
                starting_row=1,
                add_percentage=1,
                percentage_column='amount (kWh)',
                color_percentage='darkgrey',
                
                #title='Electricity origin\nper kWh consumed\n in 2020 and 2050', 
                fig_path=mainpath+'consumption_mix_'+str(len(g['order']))+'.png',
                title='Consumption mix',
                size_title=10,
                ylabel='%',
                size_label=8,
                size_percentage=8,
                addlineh=1,
                addlinev=1,
                pos_legend=(0.4, -0.3),
                figsize=g['size'],
                addlegend=0,
                change_topbottom=1,
                )

if plot2:
    for g in graphs_conso:
            list_df_to_plot=change_plot_order(list_df_prod_mix,g['order'])
            plot_bar_graph_french_scenarios(
                    list_df_to_plot=list_df_to_plot, 
                    column='percentage production technology 100', 
                    starting_row=0,
                    add_percentage=0,
                    percentage_column='amount',

                    fig_path=mainpath+'production_mix_'+str(len(g['order']))+'.png',
                    title='Production technology mix',
                    size_title=10,
                    ylabel='%',
                    size_label=8,
                    size_percentage=8,
                    pos_legend=(0.4, -0.3),
                    figsize=g['size'],
                    addlegend=0,
                    addlinev=1,
                    addPVwind=1,
                    )
if plot3:
    for g in graphs_conso:
            list_df_to_plot=change_plot_order(list_df_to_plot_storage_mix,g['order'])
            plot_bar_graph_french_scenarios(
                list_df_to_plot=list_df_to_plot, 
                column='percentage storage technology 100', 
                starting_row=0,
                add_percentage=1,
                percentage_column='percentage storage technology',

                fig_path=mainpath+'storage_mix_absolute_'+str(len(g['order']))+'.png',
                title='Storage mix',
                size_title=10,
                ylabel='%',
                size_label=8,
                size_percentage=8,
                pos_legend=(0.4, -0.3),
                figsize=g['size'],
                addlegend=0,
                addlinev=1,
            )
    for g in graphs_storage:
            list_df_to_plot1=change_plot_order(list_df_ca_aggreg,g['order'])
            list_df_to_plot2=change_plot_order(list_df_to_plot_storage_mix,g['order'])

            plot_bar_graph_french_scenarios_double(
                list_df_to_plot=list_df_to_plot1, 
                column='amount (kWh) 100', 
                starting_row=2,
                ending_row=2+1,
                add_percentage=1,
                percentage_column='amount (kWh)',
                
                list_df_to_plot2=list_df_to_plot2, 
                column2='amount 100', 
                starting_row2=0,
                percentage_column2='percentage storage technology',

                fig_path=mainpath+'storage_mix_relative'+str(len(g['order']))+'.png',
                title='Electricity released from storage in the consumption mix\nand storage technology mix', 
                size_title=10,
                ylabel='',
                size_label=8,
                size_percentage=8,
                addlinev=1,

                color_percentage='darkgrey',
                #color_percentage2

                pos_legend=(0.4, -0.3),
                figsize=g['size'],
                addlegend=0
            )

# newpaths=[]
# for folder in os.listdir(DATA_OUT_FOLDER+'/'+mainfolder):
#     newpath=DATA_OUT_FOLDER+'/'+mainfolder+'/'+folder
