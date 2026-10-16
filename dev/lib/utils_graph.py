import os as os
import pandas as pd
import numpy as np
import matplotlib as matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
import textwrap


from .static_transversal import *
from .static_impact import *
from .utils import import_xls_list_df


#Calculate the share of PV+wind in the mix in 2019 and 2050 and store them in a dictionnary
share_PVwind={}
list_df_prod_mix=import_xls_list_df(Path.cwd()/ DATA_OUT_FOLDER / RTE_FOLDER / 'list_df_prod_mix.xlsx')
for df in list_df_prod_mix[1:]:
    #calculate the rate of fluctuating renewable
    amount_PVwind=0
    amount_tot=0
    for act in fluctuating_renew:
        amount_PVwind=amount_PVwind+df[df["act"]==act]["amount"].values.tolist()[0]
    for act in direct_elec_prod_act_names:
        if act in df['act'].tolist():
            amount_tot=amount_tot+df[df["act"]==act]["amount"].values.tolist()[0]
            PVwind_rate=amount_PVwind/amount_tot*100     
    share_PVwind[df['FR scenario'].iloc[0]]=PVwind_rate


def change_plot_order(list_df_disorded,plot_order):
    """Generate the list to plot in the order you want"""
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_disorded[order])
    return(list_df_to_plot)


def plot_impact_category_overview(
    impact_categories,
    impact_data,
    order,
    rows,
    column,
    output_path,
    scenarios,
    contrib_anal,
    title='',
    subplot_size=(1, 4),
    ncols=3,
    plot_options=None,
):
    """Plot selected impact categories as equal-sized live subplots."""
    if not impact_categories:
        raise ValueError('impact_categories must contain at least one category')

    def normalize_impact_name(name):
        return ' '.join(name.lower().replace(':', ' ').replace('/', ' ').split())

    available_impacts = {
        normalize_impact_name(name): name
        for name in impact_data
    }
    aliases = {'climate change adapted': 'climate change premise'}

    selected_impacts = []
    for category in impact_categories:
        normalized_category = normalize_impact_name(category)
        impact_name = available_impacts.get(normalized_category)
        if impact_name is None and normalized_category in aliases:
            impact_name = available_impacts.get(aliases[normalized_category])
        if impact_name is None:
            raise FileNotFoundError(
                f'No generated plot found for impact category {category!r} '
                f'in the supplied impact data'
            )
        selected_impacts.append((category, impact_name))

    nrows = (len(selected_impacts) + ncols - 1) // ncols
    n_scenarios = len(change_plot_order(next(iter(impact_data.values())), order))
    panel_width = n_scenarios * subplot_size[0]
    if ncols>=3:
        legend_height = 1.4
    else:
        legend_height = 2.0
    fig = plt.figure(
        figsize=(panel_width * ncols, subplot_size[1] * nrows + legend_height + 0.35)
    )
    grid = fig.add_gridspec(
        nrows + 1,
        ncols,
        height_ratios=[subplot_size[1]] * nrows + [legend_height],
        wspace=0.4,
        hspace=0.3,
    )

    axes = []
    plot_options = dict(plot_options or {})
    for index, (_, impact_name) in enumerate(selected_impacts):
        ax = fig.add_subplot(grid[index // ncols, index % ncols])
        axes.append(ax)
        dict_to_plot = {
            'list_df_to_plot': change_plot_order(impact_data[impact_name], order),
            'rows': rows,
            'column': column,
        }
        plot_bar_graph_contrib(
            [dict_to_plot],
            ax=ax,
            scenarios=scenarios,
            show_xlabels=index // ncols == nrows - 1,
            save_legend=False,
            contrib_anal=contrib_anal,
            **plot_options,
        )

    for index in range(len(selected_impacts), nrows * ncols):
        empty_ax = fig.add_subplot(grid[index // ncols, index % ncols])
        empty_ax.axis('off')

    legend_items = {}
    # Merge legend entries from every subplot, keeping one handle per label.
    for ax in axes:
        handles, labels = ax.get_legend_handles_labels()
        for handle, label in zip(handles, labels):
            legend_items.setdefault(label, handle)

    #Reorganize legend order if the legend has two columns
    if ncols>=3:
        reordered_handles=list(legend_items.values())[::2]+list(legend_items.values())[1::2]
        reordered_labels=list(legend_items.keys())[::2]+list(legend_items.keys())[1::2]
    else:
        reordered_handles=list(legend_items.values())
        reordered_labels=list(legend_items.keys())

    legend_ax = fig.add_subplot(grid[-1, :])
    legend_ax.axis('off')
    if legend_items:
        # Anchor the legend to the full-width bottom row and distribute it across three columns.
        legend_ax.legend(
            reordered_handles,
            reordered_labels,
            loc='center',
            bbox_to_anchor=(0, 0, 1, 1),
            mode='expand',
            ncols=ncols-1,
            fontsize=plot_options.get('size_legend', 10),
            frameon=False,
            borderaxespad=0,
        )

    if title:
        titre_formate = textwrap.fill(title, width=20*ncols)
        fig.suptitle(titre_formate, fontsize=18, y=0.99, weight='bold')
    fig.subplots_adjust(
        left=0.08,
        right=0.99,
        top=0.91 if title else 0.99,
        bottom=0.03,
    )
    fig.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)

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

    contrib_anal=True,
    add_number_percentage="number", #"number" or "percentage"
    add_prod_mix=0,
    add_conso_mix=0,
    add_percentage=0,
    percentage_column='contribution to difference %',
    addlineh=1,
    add_PVwind=True,
    
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
    ax=None,
    show_xlabels=True,
    save_legend=True,
    
    ):
    """Plot contribution"""    
    nb_subplot=len(list_dict_to_plot)
    nb_scenarios=len(list_dict_to_plot[0]["list_df_to_plot"])
    draw_on_supplied_axis = ax is not None

    if not draw_on_supplied_axis:
        fig, axs = plt.subplots(
            1, nb_subplot,
            figsize=(nb_scenarios * subplot_size[0], subplot_size[1]),
            sharey=sharey,
            constrained_layout=False,
        )
        if nb_subplot==1:
            axs=[axs]
    else:
        if nb_subplot != 1:
            raise ValueError('An externally supplied axis requires exactly one plot')
        fig = ax.figure
        axs = [ax]

    axis_value_annotations = {}
    axis_units = {}

    #For each subplot
    for i, (ax, dict_to_plot) in enumerate(zip(axs,list_dict_to_plot)):
        list_df_to_plot=dict_to_plot["list_df_to_plot"]
        rows=dict_to_plot["rows"]
        column=dict_to_plot["column"]
        axis_value_annotations[ax] = []
        axis_units[ax] = list_df_to_plot[0]['unit'].iloc[0]

        label_bar_number=[]
        label_bar=[]

        #add a horizontal line = 0
        if addlineh==1:
            ax.axhline(0,color='black',linestyle='dashed', linewidth=1)
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
                if add_PVwind==True: 
                    label_bar.append(df['FR scenario'].iloc[0]+'\n('+ str(round(share_PVwind[df['FR scenario'].iloc[0]])) +'%)')
                else: 
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

                #Correction label (to be deleted when new data export is made)
                if df['label'].iloc[row]=='from direct electricity production':
                    label='directly supplied from domestic generation'
                elif df['label'].iloc[row]=='from storage':
                    label='released from storage'
                elif df['label'].iloc[row]=='from imports':
                    label='supplied from imports'
                else: 
                    label=df['label'].iloc[row]

                #plot bar
                if contrib_anal==True:
                    ax.bar(j, value, width=width, bottom=base, color=df['color'].iloc[row], label=label,hatch=df['hatch'].iloc[row], edgecolor="lightgrey")
                else:
                    ax.bar(j, value, width=width, bottom=base, color="white", label=label,hatch=df['hatch'].iloc[row], edgecolor="white")

                #Add percentage
                if 'contribution to difference' in column:
                    if add_percentage==1:
                        percentage=df[percentage_column].iloc[row]
                        if percentage>=0:
                            sign="+"
                            position_percentage=base+df[column].iloc[row]*0.3
                        if percentage<0:
                            sign=""
                            position_percentage=base+df[column].iloc[row]*0.6
                        color_percentage='lightgrey'
                        if df['color'].iloc[row]=='royalblue':
                            color_percentage='black'
                        if abs(percentage)>=0.01:
                            printed_percentage= f'{sign}{round(percentage*100)}%'
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
                ax.plot(j, prod_point, color='darkorange', label='domestic generation reference mix', marker ="D",markersize=8)    
            
            if add_conso_mix==1:
                ax.plot(j, conso_point, color='forestgreen', label='supply mix', marker ="o",markersize=8)    
            
                
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
            #if elec_conso_impact>elec_prod_impact:
            color_text='black'
            #else:
            #    color_text='lightgrey'
            value_annotation = ax.annotate(
                    text = add_text,
                    xy=(j, elec_conso_impact),
                    xytext=(0, 6),
                    textcoords='offset points',
                    ha='center',
                    color=color_text,
                    fontsize=size_absolute_value,
                    weight="bold",
                    annotation_clip=False,
                )
            if column=='contribution to impact' and add_number_percentage=="number":
                axis_value_annotations[ax].append((value_annotation, elec_conso_impact))
            if 'climate' not in df['impact'].iloc[0]:
                ax.ticklabel_format(style='sci', scilimits=(0,0))
        
        #Add information on the graph and format axis 
        # Add labels and title for each subplot
        #ax.set_title(list_df_to_plot[0]['impact'].iloc[0], size=size_subplot_title)
        #ax.set_title(ax_titles[i], size=size_subplot_title)
        #ax.set_xlabel('C')
        if sharey==False:
            if i==0:
                ax.set_ylabel(list_df_to_plot[0]['unit'].iloc[0], size=size_yaxis)
        if sharey==True:
            if i==0:
                ax.set_ylabel(list_df_to_plot[0]['unit'].iloc[0], size=size_yaxis)

        #Bar label
        if scenarios=='IAM':
            ax.set_xticks(label_bar_number,label_bar, size=size_xaxis, rotation=45, ha='right')  
        if scenarios=='FR':
            ax.set_xticks(label_bar_number,label_bar, size=size_xaxis) #rotation=45, ha='right')  
        #ax.set_xticks(rotation=45, ha='right')
        ax.margins(y=0.15)
        if not show_xlabels:
            ax.tick_params(axis='x', labelbottom=False)


    
    # Add legend without redundant labels
        #if i in range(len(axs)): #[0,2]:
            #ax.legend(bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_label*0.9))
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        #ax.legend(by_label.values(), by_label.keys(),fontsize=int(size_legend))
        #ax.legend(by_label.values(), by_label.keys(),bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_legend))
        #ax.legend(bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_label*0.9))

            # 3. Create a separate figure just for the legend
        # Standalone plots save their legend separately; overview panels use one shared legend.
        if save_legend:
            fig_leg = plt.figure(figsize=(12, 3))
            fig_leg.legend(
                by_label.values(),
                by_label.keys(),
                loc='center',
                fontsize=size_legend,
                ncol=3,
            )
            fig_leg.savefig(legend_path+str(i+1)+'_'+'legend.png', dpi=300, bbox_inches='tight')
            plt.close(fig_leg)


    if add_number_percentage=="number":
        fig.canvas.draw()
        for ax in axs:
            formatter = ax.yaxis.get_major_formatter()
            exponent = getattr(formatter, 'orderOfMagnitude', 0)
            if exponent:
                scale = 10 ** exponent
                for annotation, value in axis_value_annotations[ax]:
                    annotation.set_text(f'{value / scale:.1f}')
                ax.yaxis.get_offset_text().set_visible(False)
                ax.set_ylabel(
                    f'{axis_units[ax]} ($\\times 10^{{{exponent}}}$)',
                    size=size_yaxis,
                )

    #handles, labels = plt.gca().get_legend_handles_labels()
    #by_label = dict(zip(labels, handles))
    #plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_legend))
    
    #fig.suptitle(fig_title)
    df=list_dict_to_plot[0]['list_df_to_plot'][0]
    titre_formate = textwrap.fill(df['impact'].iloc[0], width=25)
    if draw_on_supplied_axis:
        ax.set_title(titre_formate, size=size_subplot_title, pad=2, y=1.13, va='top')
    else:
        fig.suptitle(titre_formate, size=size_title, y=0.98)
        fig.subplots_adjust(top=0.82)
        fig.subplots_adjust(bottom=0.22)
        fig.savefig(fig_path, bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)

