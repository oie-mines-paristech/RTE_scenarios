import os as os
import pandas as pd
import numpy as np
import matplotlib as matplotlib
import matplotlib.pyplot as plt
from .static_transversal import *
from .static_impact import *


def change_plot_order(list_df_disorded,plot_order):
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_disorded[order])
    return(list_df_to_plot)

def plot_bar_graph_french_scenarios(
    title,
    
    list_df_to_plot,
    column,
    fig_path='test-fig.png',

    starting_row=0,
    figsize=(2.2, 3),
    color_percentage='black',
    add_percentage=1,
    percentage_column=0,
    xlabel='',
    ylabel='',
    size_label=8,
    size_title=12,
    size_percentage=8,
    pos_legend=(0.5, -0.5),
    addlinev=0,
    addlineh=0,
    addlegend=1,
    change_topbottom=0,
    addPVwind=0,
    ):
    """Plot amount"""
    title=title

    a=0
    ecart=0.5
    b=ecart
    width=0.4

    label_bar_number=[]
    label_bar=[]

    fig,ax = plt.subplots(figsize=figsize)

    for df in list_df_to_plot:
        #plt.subplots(100+len(list_df_to_plot)+x)
        #bar graph number
        
        a=a+ecart 
        base=0

        #list of bar number
        label_bar_number.append(a)
        #list of bar label
        if df['year'].iloc[0]==2020:
            label_bar.append('2019'+'|')
        else:
            label_bar.append(df['FR scenario'].iloc[0]) #+','+ str(df['year'].iloc[0]))

        #which rows you want to print
        rows=[]
        for i in range(starting_row, len(df)):
            rows.append(i)

        for row in rows:
                value=df[column].iloc[row]
                    
                ax.bar(a, value, bottom=base, color=df['color'].iloc[row],label=df['label'].iloc[row], width=width) 
                percentage=df[percentage_column].iloc[row]
                #if row==1:
                if percentage>0.0001:
                        if add_percentage == 1:
                            if percentage<0.01:
                                printed_percentage= f'{round(percentage*100,1)}%'
                            else:
                                printed_percentage=f'{round(percentage*100)}%'
                            if df['color'].iloc[row]=='deepskyblue':
                                printed_color_percentage='white'
                                position_percentage=82
                            else:
                                printed_color_percentage=color_percentage
                                position_percentage=base+df[column].iloc[row]*0.3
                            ax.text(
                                a,
                                position_percentage,
                                printed_percentage,
                                ha = 'center', color = printed_color_percentage, size = size_percentage, weight = 'bold')
                base=base+value
        if addPVwind==1:
            #calculate the rate of fluctuating renewable
            amount_PVwind=0
            amount_tot=0
            for act in fluctuating_renew:
                amount_PVwind=amount_PVwind+df[df["act"]==act]["amount"].values.tolist()[0]
            for act in direct_elec_prod_act_names:
                if act in df['act'].tolist():
                    amount_tot=amount_tot+df[df["act"]==act]["amount"].values.tolist()[0]
            PVwind_rate=amount_PVwind/amount_tot*100     

            ax.text(
                a,
                100.5,
                f'{round(PVwind_rate)}%',
                ha = 'center', color = 'black', size = size_percentage, )#weight = 'bold')
 
    #Add information on the graph
    plt.xlabel(xlabel,size=size_label)  
    plt.ylabel(ylabel,size=size_label)  
    plt.title(title,size=size_title)
    #plt.xticks(rotation=0, ha='right')
    plt.xticks(label_bar_number,label_bar)
    #plt.ylim(80,105) 


    if addlinev==1:
        plt.axvline(ecart+ecart/2,color='red', linewidth=1)
    if addlineh==1:
        plt.axhline(100,color='black',linestyle='dashed', linewidth=1)
        
    # Add legend without redundant labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    if addlegend==1:
        plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_label*0.8))
    if change_topbottom==1:
        bottom, top = plt.ylim()
        plt.ylim(bottom=80)
        plt.ylim(top=103.5)
    
    plt.tight_layout()
    plt.savefig(fig_path)
    plt.show()    


    #Fonction to plot aggregated amount
def plot_bar_graph_french_scenarios_double(
    title,
    list_df_to_plot,
    list_df_to_plot2,

    column,
    column2,
    fig_path='test-fig.png',
    starting_row=2,
    ending_row=2,
    starting_row2=0,
    figsize=(3, 6),
    color_percentage='black',
    color_percentage2='black',
    add_percentage=1,
    percentage_column=0,
    percentage_column2=0,
    xlabel='',
    ylabel='',
    size_label=8,
    size_title=12,
    size_percentage=8,
    pos_legend=(0.5, -0.5),
    addlegend=1,
    addlinev=0
):
    """Plot amount"""
    title=title
    width=0.3
    
    a=0
    ecart=0.8
    b=ecart

    label_bar_number=[]
    label_bar=[]

    fig,ax = plt.subplots(figsize=figsize)

    for df in list_df_to_plot:
        #plt.subplots(100+len(list_df_to_plot)+x)
        #bar graph number
        
        a=a+ecart 
        base=0

        #list of bar number
        label_bar_number.append(a)
        #list of bar label
        if df['year'].iloc[0]==2020:
            label_bar.append('          '+ '2019')
        else:
            label_bar.append('          '+df['FR scenario'].iloc[0]) #+','+ str(df['year'].iloc[0]))


        #which rows you want to print
        rows=[]
        for i in range(starting_row, ending_row):
            rows.append(i)

        for row in rows:
            ax.bar(a, df[column].iloc[row], bottom=base, color=df['color'].iloc[row], label=df['label'].iloc[row], width=width)
            percentage=df[percentage_column].iloc[row]
            if percentage>0.0001:
                if add_percentage == 1:
                    if percentage<0.01:
                        printed_percentage= f'{round(percentage*100,1)}%'
                    else:
                        printed_percentage=f'{round(percentage*100)}%'
                    ax.text(a,
                        base+df[column].iloc[row]*0.3,
                        printed_percentage,
                        ha = 'center', color = color_percentage, size = size_percentage, weight = 'bold')
            base=base+df[column].iloc[row]



    a=0.4
    ecart=0.8
    b=ecart
    width=0.3
    
    for df in list_df_to_plot2:
        #plt.subplots(100+len(list_df_to_plot)+x)
        #bar graph number
        
        a=a+ecart 
        base=0

        #list of bar number
        label_bar_number.append(a)
        #list of bar label
        label_bar.append('')
        
        #which rows you want to print
        rows=[]
        for i in range(starting_row2, len(df)):
            rows.append(i)

        for row in rows:
            ax.bar(a, df[column2].iloc[row], bottom=base, color=df['color'].iloc[row], label=df['label'].iloc[row], width=width)
            percentage=df[percentage_column2].iloc[row]
            if percentage>0.0001:
                if add_percentage == 1:
                    if percentage<0.01:
                        printed_percentage= f'{round(percentage*100,1)}%'
                    else:
                        printed_percentage=f'{round(percentage*100)}%'
                    ax.text(a,
                        base+df[column2].iloc[row]*0.3,
                        printed_percentage,
                        ha = 'center', color = color_percentage2, size = size_percentage, weight = 'bold')
            base=base+df[column2].iloc[row]

    #Add information on the graph
    plt.xlabel(xlabel,size=size_label)  
    plt.ylabel(ylabel,size=size_label)  
    plt.title(title,size=size_title)
    plt.xticks(label_bar_number,label_bar)
    #plt.xticks(rotation=45, ha='right')
    
    #Add vertical lines
    if addlinev==1:
        plt.axvline(0.4+ecart*1.25,color='red', linewidth=1)
        for n in range(len(list_df_to_plot)-2):
            plt.axvline(0.4+ecart*(2.25+n), color='black', linestyle='dashed', linewidth=1)

    # Add legend without redundant labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    if addlegend==1:
        plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_label*0.8))

    plt.tight_layout()
    plt.savefig(fig_path)
    #plt.show() 


    #Fonction to plot aggregated contribution
def plot_bar_graph_contrib(
    list_dict_to_plot,

    fig_path='test-fig.png',
    legend_path='',
    ax_titles=["",""],
    scenarios='FR',

    add_number_percentage="number", #"number" or "percentage"
    add_prod_mix=0,
    add_conso_mix=0,
    add_percentage=0,
    percentage_column='contribution to difference %',
    addlineh=1,
    
    subplot_size=(4, 3),
    width=0.7,
    sharey=False,
    pos_legend=(0.5, -0.5),

    size_title=17,
    size_subplot_title=15,
    size_xaxis=13,
    size_yaxis=13,
    size_absolute_value=14,
    size_percentage=12,
    size_legend=10,
    
):
    """Plot contribution"""    
    nb_subplot=len(list_dict_to_plot)
    nb_scenarios=len(list_dict_to_plot[0]["list_df_to_plot"])

    #create fig
    #fig,ax = plt.subplots(figsize=subplot_size)
    fig, axs = plt.subplots(1,nb_subplot, figsize=(nb_scenarios*subplot_size[0],subplot_size[1]),sharey=sharey, constrained_layout=True)
    if nb_subplot==1:
        axs=[axs]

    #For each subplot
    for i, (ax, dict_to_plot) in enumerate(zip(axs,list_dict_to_plot)):
        list_df_to_plot=dict_to_plot["list_df_to_plot"]
        rows=dict_to_plot["rows"]
        column=dict_to_plot["column"]

        label_bar_number=[]
        label_bar=[]

        #add a horizontal line = 0
        if addlineh==1:
            plt.axhline(0,color='black',linestyle='dashed', linewidth=1)
        #For each bar 
        for j, df in enumerate(list_df_to_plot): #j = bar graph number  
            #Extract static values
            col='impact/kWh (absolute)'
            elec_conso_impact=df.loc[df['act']=='market for electricity, high voltage, FE2050',col].tolist()[0]
            elec_prod_impact=df.loc[df['act']=='market for electricity, from direct French production, FE2050',col].tolist()[0]
            
            #list of bar number
            label_bar_number.append(j)
            #list of bar label
            if scenarios=='IAM':
                label_bar.append(df['model'].iloc[0]+' | '+ df['SSP'].iloc[0]+'-'+ df['RCP'].iloc[0])#+','+ str(df['year'].iloc[0]))
            if scenarios=='FR':
                label_bar.append(df['FR scenario'].iloc[0])

            #Plot contributions
            base1=0
            base2=0
    
            for row in rows:
                value=df[column].iloc[row]
    
                #Change base depending if value positive or negative
                if value>=0:
                        base=base1
                if value<0:
                        base=base2
                #plot bar
                ax.bar(j, value, width=width, bottom=base, color=df['color'].iloc[row], label=df['label'].iloc[row],hatch=df['hatch'].iloc[row], edgecolor="lightgrey")

                #Add percentage
                if 'contribution to difference' in column:
                    if add_percentage==1:
                        percentage=df[percentage_column].iloc[row]
                        if percentage>=0:
                            sign="+"
                        if percentage<0:
                            sign=""
                        color_percentage='lightgrey'
                        if df['color'].iloc[row]=='royalblue':
                            color_percentage='black'
                        if abs(percentage)>=0.01:
                            printed_percentage= f'{sign}{round(percentage*100)}%'
                            position_percentage=base+df[column].iloc[row]*0.3
                            ax.text(
                                j,
                                position_percentage,
                                printed_percentage,
                                ha = 'center', color = color_percentage, size = size_percentage, weight = 'bold',
                            )
                #Recalulate base
                base=base+value
                if value>=0:
                    base1=base1+value
                if value<0:
                    base2=base2+value
                
            #if 1 in row, print absolute value, else print differential value
            test_row=1
            if test_row in rows:
                prod_point=elec_prod_impact
                conso_point=elec_conso_impact
            else:
                prod_point=0
                conso_point=elec_conso_impact-elec_prod_impact
            #if rows!=[9,5,6,10]:
            if add_prod_mix==1:
                ax.plot(j, prod_point, color='darkorange', label='1 kWh, production mix', marker ="D",markersize=8)    
            
            if add_conso_mix==1:
                ax.plot(j, conso_point, color='forestgreen', label='1 kWh, consumption mix', marker ="o",markersize=6)    
            
                
            #Plot production mix, consumption mix, relative difference
            #relative difference production mix and consumption mix
            diff=(elec_conso_impact-elec_prod_impact)/elec_prod_impact*100 
            if diff>=0:
                sign="+"
            if diff<0:
                sign=""

            #Add consumption mix impact and difference in %
            if column=='contribution to impact': 
                if add_number_percentage=="number": 
                    if elec_conso_impact>1 and elec_conso_impact<100:
                        elec_conso_impact_to_print=f'{round(elec_conso_impact,1)}'
                    else: 
                       elec_conso_impact_to_print=f"{elec_conso_impact:.1e}"
                    add_text=elec_conso_impact_to_print
                elif add_number_percentage=="percentage":   
                    add_text=f'{round(elec_conso_impact,1)} | {sign} {round(diff)}%'
                else:
                    add_text=''            
            else:
                    add_text=''
            if elec_conso_impact>elec_prod_impact:
                color_text='black'
            else:
                color_text='lightgrey'
            ax.annotate(
                    text = add_text,
                    xy=(j, elec_conso_impact*1.015),
                    ha='center',
                    color=color_text,
                    fontsize=size_absolute_value,
                    weight="bold",
                )
            if 'climate' not in df['impact'].iloc[0]:
                ax.ticklabel_format(style='sci', scilimits=(0,0))
        
        #Add information on the graph and format axis 
        # Add labels and title for each subplot
        #ax.set_title(list_df_to_plot[0]['impact'].iloc[0], size=size_subplot_title)
        ax.set_title(ax_titles[i], size=size_subplot_title)
        #ax.set_xlabel('C')
        if sharey==False:
            if i==0:
                ax.set_ylabel(list_df_to_plot[0]['unit'].iloc[0]+ '/kWh', size=size_yaxis)
        if sharey==True:
            if i==0:
                ax.set_ylabel(list_df_to_plot[0]['unit'].iloc[0]+ '/kWh', size=size_yaxis)

        #Bar label
        if scenarios=='IAM':
            ax.set_xticks(label_bar_number,label_bar, size=size_xaxis, rotation=45, ha='right')  
        if scenarios=='FR':
            ax.set_xticks(label_bar_number,label_bar, size=size_xaxis) #rotation=45, ha='right')  
        #ax.set_xticks(rotation=45, ha='right')


    
    # Add legend without redundant labels
        #if i in range(len(axs)): #[0,2]:
            #ax.legend(bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_label*0.9))
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        #ax.legend(by_label.values(), by_label.keys(),fontsize=int(size_legend))
        #ax.legend(by_label.values(), by_label.keys(),bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_legend))
        #ax.legend(bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_label*0.9))

            # 3. Create a separate figure just for the legend
        fig_leg = plt.figure(figsize=(3, 2))
        # Add the legend to the empty figure
        legend = fig_leg.legend(by_label.values(), by_label.keys(), loc='center')
        # 4. Save the legend file, cropping out extra whitespace
        fig_leg.savefig(legend_path+str(i+1)+'_'+'legend.png', bbox_inches='tight')
        plt.close(fig_leg)


    #handles, labels = plt.gca().get_legend_handles_labels()
    #by_label = dict(zip(labels, handles))
    #plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_legend))
    
    #fig.suptitle(fig_title)
    df=list_df_to_plot[0]
    fig.suptitle((df['impact'].iloc[0]), size=size_title)
    #fig.suptitle((df['model'].iloc[0]+'-'+ df['SSP'].iloc[0]+'-'+ df['RCP'].iloc[0] +' | '+ str(df['year'].iloc[0])), size=size_title)
    #plt.tight_layout()
    #plt.show()    
    fig.savefig(fig_path)
    # Close the legend figure to free memory
    plt.close('all')


    