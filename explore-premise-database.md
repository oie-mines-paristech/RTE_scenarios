---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: lca_alg_11
    language: python
    name: lca_alg_11
---

```python editable=true slideshow={"slide_type": ""}
#importation of usefull packages
import bw2data
import bw2io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
```

```python
import lca_algebraic as agb
```

# Intitialisation
## `🔧` Project name and ecoinvent names *2

```python
NAME_BW_PROJECT="HySPI_premise_FE2050_14"
```

```python
#Set in the right project and print the databases
bw2data.projects.set_current(NAME_BW_PROJECT)
list(bw2data.databases)
#agb.list_databases() #equivalent lca_algebraic function
```

```python
ecoinvent_db_name='ecoinvent-3.9.1-cutoff'
biosphere_db_name='ecoinvent-3.9.1-biosphere'
```

```python
#If you need to delete a database
#del bw2data.databases['ei_cutoff_3.9_tiam-ucl_SSP2-RCP45_2020_Reference - N1 2025-05-22 - update electricity']
```

## Export excel 

```python
#Fonction to export several dataframes in several excel sheets
def export_data_to_excel(list_df_to_export, xlsx_file_name):
    """Export dataframe to excel files in several excel sheet"""
    # list_df_to_export is a list that looks like ["name", df1, df2, df3...]
    # "name" is the name of the sheet in the excel file where df1, df2, df3 will be exporter
    # df1, df2, df3 are the dataframe to be exported in the same excel sheet. 
    # xlsx_file_name is the name of the excel file. It shall end with .xlsx
    with pd.ExcelWriter(xlsx_file_name,engine="xlsxwriter") as writer:
        for list_name_tables in list_df_to_export:
            if len(list_name_tables)==2:
                list_name_tables[1].to_excel(writer,sheet_name=list_name_tables[0])
                #list_name_tables[1] = df, list_name_tables[0]=sheet_name
            elif len(list_name_tables)>2:
                a=0
                for i in range((len(list_name_tables)-1)):
                    list_name_tables[i+1].to_excel(writer,sheet_name=list_name_tables[0],startcol=0,startrow=a,header=True,index=True)
                    a=a+len(list_name_tables[i+1].index)+2

```

# Impact assessment methods

```python
EF = 'EF v3.1'
climate = (EF, 'climate change', 'global warming potential (GWP100)')
acidification = (EF,'acidification','accumulated exceedance (AE)')
land=(EF, 'land use', 'soil quality index')
ionising_rad=(EF,'ionising radiation: human health','human exposure efficiency relative to u235')
metals_minerals=(EF,  'material resources: metals/minerals',  'abiotic depletion potential (ADP): elements (ultimate reserves)')
non_renew_energy=(EF,'energy resources: non-renewable','abiotic depletion potential (ADP): fossil fuels')

impacts=[climate, acidification, land, ionising_rad,metals_minerals,non_renew_energy]

for impact in impacts:
    print(impact, bw2data.Method(impact).metadata['unit'])
```

```python
#If you want you can import climate change impact method that is updated by premise
from premise_gwp import add_premise_gwp
add_premise_gwp()
climate_premise=('IPCC 2021', 'climate change', 'GWP 100a, incl. H and bio CO2')
```

```python
#To see all the categories associated with EF3.1
#agb.findMethods("",'EF v3.1')
[m for m in bw2data.methods if EF == m[0]]
```

# Manipulating multiple databases


## Filters the database

```python
#generate a list of names of generated databases by premise
premise_db_name_list=[]
for db_name in bw2data.databases.keys():
    if "ei_cutoff" in db_name:
        premise_db_name_list.append(db_name)
premise_db_name_list
```

```python editable=true slideshow={"slide_type": ""}
#generate a list of generated databases by premise
premise_db_list=[]
for db_name in premise_db_name_list:
    premise_db_list.append(bw2data.Database(db_name))
```

```python editable=true slideshow={"slide_type": ""}
#Options for model / SSP / IAM / FR scenarios
model_list=['image','tiam-ucl','remind']
year_list=['2020','2050']
SSP_list=['SSP1','SSP2','SSP3','SSP4','SSP5']
RCP_list=['Base','RCP26','RCP45','Npi']
FR_scenario_list=['M0','M1','M23','N1','N2','N03']
```

```python
#tag the database with corresponding year, model, SSP, RCP and FR scenario
for db in premise_db_list:
    for year in year_list:
        if year in db.name:
            db.year=int(year)
    for model in model_list:
        if model in db.name:
            db.model=model
    for SSP in SSP_list:
        if SSP in db.name:
            db.SSP=SSP
    for RCP in RCP_list:
        if RCP in db.name:
            db.RCP=RCP      
    db.FR_scenario='None'
    for FR_scenario in FR_scenario_list:
        if FR_scenario in db.name:
            db.FR_scenario=FR_scenario    
    #Warning
    db.warning=' '
    if '2025-05-16' in db.name:
        db.warning='in 2019: 2050 ratios (except efficencies) with premise year 2019'
    if 'elec' in db.name:
        db.warning='update electricity only'
    if db.name=="ei_cutoff_3.9_tiam-ucl_SSP2-RCP45_2020_Reference - N1 2025-05-22 - elec":
        db.year=2050
        db.warning='update electricity only+wrong year in db.name'
    if '2025-05-22' in db.name and 'elec' not in db.name:
        db.warning='in 2050: 2019 ratios (except efficencies) with premise year 2050'
```

```python
#Each database can be sorted with these tags
df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning'])
for db in premise_db_list:
    df.loc[len(df.index)] = [db.name,db.model,db.SSP,db.RCP,db.FR_scenario,db.year, db.warning]
df
```

## `🔧` Select databases with filters

```python editable=true slideshow={"slide_type": ""}
#If you want to run the tests on all premise databases
selected_db_list=premise_db_list
```

```python
#To generate a list of databases based on filters on the year / SSP / RCP/ FR_Scenario
#Example
selected_db_list=[db for db in premise_db_list if '2025-05-15' in db.name and db.FR_scenario=='N1'and db.RCP=='RCP45' and db.year==2020]+[db for db in premise_db_list if '2025-05-15' in db.name and db.RCP=='RCP45' and db.year==2050]+[db for db in premise_db_list if '2025-05-15' in db.name and db.FR_scenario=='N1'and db.RCP=='Base' and db.year==2020]+[db for db in premise_db_list if '2025-05-15' in db.name and db.RCP=='Base' and db.year==2050]
#selected_db_list=[db for db in premise_db_list if '2025-05-22' in db.name and 'update' not in db.name]+[db for db in premise_db_list if db.name=='ei_cutoff_3.9_tiam-ucl_SSP2-RCP45_2050_Reference - N1 2025-05-15']+[db for db in premise_db_list if db.name=='ei_cutoff_3.9_tiam-ucl_SSP2-Base_2050_Reference - N1 2025-05-15']
#selected_db_list=[db for db in premise_db_list if db.warning==' ']
#selected_db_list=[db for db in premise_db_list if 'update' not in db.name]
#selected_db_list=[bw2data.Database('ei_cutoff_3.9_tiam-ucl_SSP2-RCP45_2050_Reference - N03 2025-05-15')]+[bw2data.Database('ei_cutoff_3.9_tiam-ucl_SSP2-RCP45_2020_Reference - N1 2025-05-15')]+[bw2data.Database('ei_cutoff_3.9_tiam-ucl_SSP2-RCP45_2020_Reference - M03 2025-05-15')]
selected_db_list
#selected_db_list=[selected_db_list[2]]
#database'2025-05-16' = scenario_data_2050 ratios with premise year 2019_except efficencies_column
```

# List of activities in market for electricity high voltage

```python
#list of activities in each subcategory

direct_elec_prod_act_names=[
    "electricity production, nuclear, pressure water reactor",
    "electricity production, Evolutionary Power Reactor (EPR)",
    "electricity production, Small Modular Reactor (SMR)",
    
    "electricity production, hydro, run-of-river",
    "electricity production, hydro, reservoir, alpine region",
    "electricity production, photovoltaic",
    "electricity production, wind, 1-3MW turbine, onshore",
    "electricity production, wind, 1-3MW turbine, offshore",
    "heat and power co-generation, wood chips, 6667 kW",
    "treatment of municipal solid waste, incineration",
    "electricity production, wave energy converter",
    
    "electricity production, natural gas, combined cycle power plant",
    "electricity production, oil",
    "electricity production, hard coal",
    ]

flexibilities_act_names=[
    "electricity production, hydro, pumped storage, FE2050",
    "electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050",
    "electricity production, from vehicle-to-grid, FE2050",
    "electricity supply, high voltage, from vanadium-redox flow battery system, FE2050",
    ]

import_act_name=["market group for electricity, high voltage"]

losses_act_names=["market for electricity, high voltage, FE2050"]

tranmission_act_names=[
    "transmission network construction, electricity, high voltage direct current aerial line",
    "transmission network construction, electricity, high voltage direct current land cable",
    "transmission network construction, electricity, high voltage direct current subsea cable",
]

#Labels of each subcategory
dict_act_subcategories = {
    'direct electricity production in France':direct_elec_prod_act_names,
    'electricity production from flexibilities': flexibilities_act_names,
    'imports':import_act_name,
    'losses':losses_act_names,
    'network':tranmission_act_names
}
```

```python
dict_color={
    "electricity production, nuclear, pressure water reactor":['gold','nuclear'],
    "electricity production, Evolutionary Power Reactor (EPR)":['gold','nuclear'],
    "electricity production, Small Modular Reactor (SMR)":['goldenrod','nuclear'],
    "electricity production, hydro, run-of-river":['dodgerblue','hydro'],
    "electricity production, hydro, reservoir, alpine region":['dodgerblue','hydro'],
    "electricity production, photovoltaic":['coral','photovoltaic'],
    "electricity production, wind, 1-3MW turbine, onshore":['aquamarine','onshore wind'],
    "electricity production, wind, 1-3MW turbine, offshore":['mediumaquamarine','offshore wind'],
    "heat and power co-generation, wood chips, 6667 kW":['chartreuse','biomass and waste'],
    "treatment of municipal solid waste, incineration":['chartreuse','biomass and waste'],
        
    "electricity production, natural gas, combined cycle power plant":['slategrey','gas'],
    "electricity production, oil":['black','oil and coal'],
    "electricity production, hard coal":['black','oil and coal'],
    
    "electricity production, wave energy converter":['blue','wave'],    
    
    "electricity production, hydro, pumped storage, FE2050":['rebeccapurple','storage'],
    "electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050":['rebeccapurple','storage'],
    "electricity production, from vehicle-to-grid, FE2050":['rebeccapurple','storage'],
    "electricity supply, high voltage, from vanadium-redox flow battery system, FE2050":['rebeccapurple','storage'],
    
    "market group for electricity, high voltage":['magenta','imports'],
     }  
```

```python
list_dict_storage=[
    {
    'act_storage_name':'electricity production, hydro, pumped storage, FE2050',
    'act_where_elec_is_stored_name':'electricity production, hydro, pumped storage, FE2050',
    'act_elec_stored_name':"market for electricity, high voltage, FE2050"
     },
    {
    'act_storage_name':'electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050',
    'act_where_elec_is_stored_name':'hydrogen production, gaseous, 30 bar, from PEM electrolysis, from grid electricity, domestic, FE2050',
    'act_elec_stored_name':"market for electricity, low voltage, FE2050"
    },    
    {
    'act_storage_name':'electricity production, from vehicle-to-grid, FE2050',
    'act_where_elec_is_stored_name':'electricity production, from vehicle-to-grid, FE2050',
    'act_elec_stored_name':"market for electricity, low voltage, FE2050"
     },
    {
    'act_storage_name':'electricity supply, high voltage, from vanadium-redox flow battery system, FE2050',
    'act_where_elec_is_stored_name':'electricity supply, high voltage, from vanadium-redox flow battery system, FE2050',
    'act_elec_stored_name':"market for electricity, high voltage, FE2050"
     }
]

```

# Dev en cours


## To do : 
* resortir les graphes évolutions N1 et comparaison

* Problème : High/medium/low voltage = des sources différentes pour les différentes sources de stockage, des impacts différents pour chaque source.
  > faire un seul marché, 8% de pertes RTE + accumuler tous les réseau.
  > Est ce qu'on distingue les réseaux high en fonction des scénarios ? 
* Problème : on retire le marché de conso français et pas le marché de prod directe alors qu'on veut fusionner les 2. 
 > Enlever le market for elec, from direct production plutôt ? mais attention, pour le calcul d'efficacité, garder le marché conso. 


## Pertes high medium low 

```python
for db in [selected_db_list[0]]:  
    elec_high=db.search("market for electricity, high voltage, FE2050")[0]
    elec_med=db.search("market for electricity, medium voltage, FE2050")[0]
    elec_low=db.search("market for electricity, low voltage, FE2050")[0]
```

```python
1.0312427*1.0042*1.0307
#0.0312427 	0.0042 0.0307 pertes high/medium/low
#8% RTE

```

# Impact 1 kWh of electricity


## `🔧` activity, impact category

```python
act_name_list=[
    "market for electricity, high voltage, FE2050",
    #"market for electricity, from direct French production, FE2050",
    #"market for electricity, from storage, FE2050",
    #"market for electricity, from import, FE2050",
]
    
impact_cat=climate
#impact_cat=climate_premise
```

## Run

```python
df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','act','impact','unit'])

for db in selected_db_list:    
    for act_name in act_name_list:
        #act=agb.findActivity(elec_act_name, db_name=db.name)
        act=db.search(act_name)[0]
        lca = act.lca(method=impact_cat, amount=1)
        score = lca.score
        unit_impact = bw2data.Method(impact_cat).metadata["unit"]
        if unit_impact == "kg CO2-Eq":
            score=1000*score
            unit_impact="g CO2-Eq"
        df.loc[len(df.index)] = [db.name,db.model, db.SSP, db.RCP,db.FR_scenario,db.year,db.warning,act["name"],score,unit_impact]
```

```python editable=true slideshow={"slide_type": ""}
#df_elec = df.style.map(style_red, props='background-color:red;')\
#             .map(style_orange, props='background-color:orange;')\
#             .map(style_green, props='background-color:green;')
df_elec_1=df.style.background_gradient(cmap='Reds',subset='impact')
df_elec_1
```

# Aggregated contribution analysis


## `🔧` activity, impact category

```python
act_name_list=[
    "market for electricity, high voltage, FE2050",
    "market for electricity, from direct French production, FE2050",
    "market for electricity, from storage, FE2050",
    "market for electricity, from import, FE2050",
    #"market for electricity, from direct production and import, FE2050",
    #"market for electricity production, direct production, high voltage, FE2050",
    #"market for electricity production, storage production, FE2050",
    #"market for electricity production, import, FE2050"
]
    
impact_cat=climate
#impact_cat=climate_premise
```

## Run

```python
list_df_ca_aggreg=[]

for db in selected_db_list:  
    df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','act','amount (kWh)','contribution to impact','unit'])    
    #Amount of direct electricity / storage / imports
    act=db.search("market for electricity, high voltage, FE2050")[0]
    excs=[exc for exc in act.exchanges()]
    amount_direct_elec=0
    amount_storage=0
    amount_import=0
    for exc in excs:
        if exc["name"] in direct_elec_prod_act_names:
            amount_direct_elec = exc["amount"]+amount_direct_elec
        if exc["name"] in flexibilities_act_names:
            amount_storage = exc["amount"]+amount_storage
        if exc["name"] in import_act_name:
            amount_import = exc["amount"]+amount_import

    #Impact of each mix
    for act_name in act_name_list:
        #act=agb.findActivity(elec_act_name, db_name=db.name)
        act=db.search(act_name)[0]
        #Amount
        if act["name"]=="market for electricity, high voltage, FE2050":
            amount=1
        if act["name"]=="market for electricity, from direct French production, FE2050":
            amount=amount_direct_elec
        if act["name"]=="market for electricity, from storage, FE2050":
            amount=amount_storage
        if act["name"]=="market for electricity, from import, FE2050":
            amount=amount_import
        #Impact
        lca = act.lca(method=impact_cat, amount=amount)
        score = lca.score            
        unit_impact = bw2data.Method(impact_cat).metadata["unit"]
        #change of unit for climate change
        if unit_impact == "kg CO2-Eq":
            score=1000*score
            unit_impact="g CO2-Eq"
        #export
        df.loc[len(df.index)] = [db.name,db.model, db.SSP,db.RCP,db.FR_scenario,db.year,db.warning,act["name"],amount,score,unit_impact]
    #For each db in the selected list add the dataframe to the list of dataframes
    list_df_ca_aggreg.append(df)

#list_df_ca_aggreg[0]
```

```python
for df in list_df_ca_aggreg: 
    #Add columns to calculate the contribution to impacts (percentage)
    total = df['contribution to impact'].iloc[1:].sum()
    df['percentage contribution']=df['contribution to impact']/total*100
    # Absolute impact/kWh
    df["impact/kWh (absolute)"]=df["contribution to impact"]/df["amount (kWh)"]
    #add label and color for plots
    df['label']=['consumption mix','from direct electricity production','from storage','from imports']
    df['color']=['orange','deepskyblue','royalblue','midnightblue']
    
    #ajust decimals
    #for column in ['impact', 'contribution to impact']:
    #    df[column] = df[column].apply(lambda x: '{:.1f}'.format(x))
    #df['amount (kWh)'] = df['amount (kWh)'].apply(lambda x: '{:.2f}'.format(x))
    #df['percentage contribution'] = df['percentage contribution'].apply(lambda x: '{:.0f}'.format(x))
    
    #color the table
    #df=df.style.background_gradient(cmap='Reds',subset=["impact", "contribution to impact"])


```

```python
for df in selected_db_list: 

    act_market_elec= act_storage=db.search("market for electricity, high voltage, FE2050")[0]
    excs_market_elec=[exc for exc in act_market_elec.exchanges()]
    
    for diki in list_dict_storage:
        act_storage_name=diki['act_storage_name']
        act_where_elec_is_stored_name=diki['act_where_elec_is_stored_name']
        act_elec_stored_name=diki['act_elec_stored_name']
    
        #Storage amount
        exc_amount=0
        for exc in excs_market_elec:
            if exc.input["name"]==act_storage_name:
                exc_amount=exc["amount"]

        #Store scores in a dataframe
        df.loc[len(df.index)] = [db.name,db.model, db.SSP, db.RCP,db.FR_scenario,db.year,db.warning,act_storage_name,exc_amount]
    #For each db in the selected list add the dataframe to the list of dataframes
    list_df_storage_2.append(df)           

```

```python
list_df_storage_2[7]
```

```python
unit_impact = bw2data.Method(impact_cat).metadata["unit"]

list_df_storage=[]

for db in selected_db_list: 
    df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','act','elec from storage (1kWh)','storage infrastructure','input elec losses','input elec 1kWh','unit','% storage infrastructure','% input elec losses','% input elec 1kWh','% efficency',"amount in elec market"])    

    act_market_elec= act_storage=db.search("market for electricity, high voltage, FE2050")[0]
    excs_market_elec=[exc for exc in act_market_elec.exchanges()]
    
    for diki in list_dict_storage:
        act_storage_name=diki['act_storage_name']
        act_where_elec_is_stored_name=diki['act_where_elec_is_stored_name']
        act_elec_stored_name=diki['act_elec_stored_name']
    
        #storage activity to study
        act_storage=db.search(act_storage_name)[0]
        #activity that countains the electricity flow to be stored
        act_where_elec_is_stored=db.search(act_where_elec_is_stored_name)[0]
        #Elec flow stored
        act_elec_stored=db.search(act_elec_stored_name)[0]

        #Elec stored 
        lca = act_elec_stored.lca(method=impact_cat, amount=1)
        score_elec=lca.score #Total : Electricity from storage score
    
        #Total : Electricity from storage score
        lca = act_storage.lca(method=impact_cat, amount=1)
        total=lca.score #Total : Electricity from storage score

        #Modification of the activity that countains the electricity flow to be stored
        #This flow is turned to zero to model only LCI of infrastructure
        excs=[exc for exc in act_where_elec_is_stored.exchanges()]
        for exc in excs:
            if exc.input["name"]==act_elec_stored_name:
                amount=exc["amount"]
                exc["amount"]=0
                exc.save()
        #act_where_elec_is_stored.updateExchanges({ act_elec_stored: None})
        lca = act_storage.lca(method=impact_cat, amount=1)
        infra=lca.score #Storage infrastructure score
        
        #Delete modification
        for exc in excs:
            if exc.input["name"]==act_elec_stored_name:
                exc["amount"]=amount
                exc.save()
        lca = act_storage.lca(method=impact_cat, amount=1)
        test=lca.score #test
        #Test that the database was nos modified
        if total!=test:
            print('there is an issue')

        #elec_losses
        losses=total-infra-score_elec

        #Contrib
        score_elec_contrib=score_elec/total*100
        infra_contrib=infra/total*100
        losses_contrib =losses/total*100

        #Efficency
        efficency=score_elec/(losses+score_elec)*100

        #Conversion for climate change impact
        if unit_impact == "kg CO2-Eq":
            total =1000*total
            infra=1000*infra
            score_elec=1000*score_elec
            losses=1000*losses
            unit_impact="g CO2-Eq"

        #Storage amount
        exc_amount=0
        for exc in excs_market_elec:
            if exc.input["name"]==act_storage_name:
                exc_amount=exc["amount"]
                
        #Store scores in a dataframe
        df.loc[len(df.index)] = [db.name,db.model, db.SSP, db.RCP, db.FR_scenario,db.year,db.warning,act_storage_name,total,infra,losses,score_elec,unit_impact,infra_contrib,losses_contrib,score_elec_contrib,efficency,exc_amount]
    #For each db in the selected list add the dataframe to the list of dataframes
    list_df_storage.append(df)           

```

```python
for df in list_df_storage:
 #Average % of input elec
    df['Helper'] = df["amount in elec market"] * df['% input elec 1kWh']
    df.loc[0,'Weighted average % input elec 1kWh'] = df['Helper'].sum() / df["amount in elec market"].sum()
 #Average efficency
    df['Helper'] = df["amount in elec market"] * df['% efficency']
    df.loc[0,'Weighted average efficency'] = df['Helper'].sum() / df["amount in elec market"].sum()
 #Average contrib of storage infra
    df['Helper'] = df["amount in elec market"] * df['storage infrastructure']
    df.loc[0,'Weighted average storage infrastructure impact'] = df['Helper'].sum() / df["amount in elec market"].sum()
```

```python
#for each database
for n in range (len(list_df_ca_aggreg)):
    #Reallocation factor taken from list_df_storage
    #print(list_df_storage[n].loc[0,['Weighted mean % input elec 1kWh']])
    realloc=(list_df_storage[n].loc[0,['Weighted mean % input elec 1kWh']]).to_list()[0]/100 #to_list()[0] to convert the serie into a float
    df=list_df_ca_aggreg[n]
    #df.loc[1,"realloc contribution to impact"]=df.loc[2,"contribution to impact"]*realloc
    
    #df.loc[1,"realloc contribution to impact"]=df.loc[1,"contribution to impact"]+realloc*df.loc[2,"contribution to impact"]
    #The share of contribution related to direct production is increased
    #The share of contribution related to storage is decreased
    df.loc[0,"realloc contribution to impact"]=df.loc[0,"contribution to impact"]
    df.loc[1,"realloc contribution to impact"]=df.loc[1,"contribution to impact"]+realloc*df.loc[2,"contribution to impact"]
    df.loc[2,"realloc contribution to impact"]=df.loc[2,"contribution to impact"]*(1-realloc)
    df.loc[3,"realloc contribution to impact"]=df.loc[3,"contribution to impact"]
```

```python
list_df_ca_aggreg[0].head(4)
```

```python
list_df_storage[2]
```

# Graphs

```python
#Recap : list of databases
list_df = pd.DataFrame(columns=list_df_ca_aggreg[0].columns)
for df in list_df_ca_aggreg:
    list_df=pd.concat([list_df,df.head(1)],ignore_index=True)
list_df
```

## `🔧` Choose databases to compare and order

```python
#Choose what you want to plot in which order on the graphs
#rows_to_plot=[5,1,4]
#rows_to_plot=[0,15,1]+[0,8,1]
plot_order=[3,2,7,6] #

#Generate the list to plot
list_df_to_plot= []
for order in plot_order:
    list_df_to_plot.append(list_df_ca_aggreg[order])

#To plot all graphs
#list_df_to_plot=list_df_ca_aggreg
```

## Compare production mix vs consumption mix

```python
list_df_to_plot[0]
```

```python
column='impact/kWh (absolute)'
title='Impact per kWh'
```

```python
#Plot consumption mix
a=0
label_bar_number=[]
label_bar=[]

fig,ax = plt.subplots()

for df in list_df_to_plot:
    a=a+0.2
    #plot consumption mix (bar)
    ax.bar(a,df[column].iloc[0],width=0.1,color=df['color'].iloc[0], label=df['label'].iloc[0])
    #plot production mix (point)
    #add labels
    ax.annotate(
        text = f'{round(df[column].iloc[0],1)}',
        xy=(a, df[column].iloc[0] + 0.1),
        ha='center',
    )

    label_bar_number.append(a)
    #list of bar label
    label_bar.append(df['model'].iloc[0]+', '+ df['SSP']+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))


# add labels with bar_label

#Add information on the graph
plt.xlabel('  ')  
plt.ylabel(impact_cat[2]+ ', '+  list_df_ca_aggreg[0]['unit'].iloc[0])  
plt.title(title)
plt.xticks(label_bar_number,label_bar)  
plt.xticks(rotation=45, ha='right')
# Add legend without redundant labels
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
fig.legend(by_label.values(), by_label.keys(), loc='lower center',bbox_to_anchor=(0.5, -0.1))
plt.tight_layout()
#plt.show()
plt.savefig('image2-consumption.png')
```

```python
#Plot Production vs consumption mix

a=0
label_bar_number=[]
label_bar=[]

fig,ax = plt.subplots()

for df in list_df_to_plot:
    a=a+0.2
    #plot consumption mix (bar)
    ax.bar(a,df[column].iloc[0],width=0.1,color=df['color'].iloc[0], label=df['label'].iloc[0])
    #plot production mix (point)
    ax.plot(a, df[column].iloc[1], color=df['color'].iloc[1], label=df['label'].iloc[1], marker = 'o')


    #relative difference production mix >> consumption mix 
    diff=(df[column].iloc[0]-df[column].iloc[1])/df[column].iloc[1]*100 
    
    
    #add labels
    ax.annotate(
        text = f'{round(df[column].iloc[0],1)} | +{round(diff)}%',
        xy=(a, df[column].iloc[0] + 0.1),
        ha='center',
    )


    #ax.annotate(
    #    text = f'+{round(diff)}%',
    #    xy=(a, df[column].iloc[0]/2),
    #    ha='center',
    #)    
    #Number of the bar
    #list of bar number
    label_bar_number.append(a)
    #list of bar label
    label_bar.append(df['model'].iloc[0]+', '+ df['SSP']+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))


# add labels with bar_label

#Add information on the graph
plt.xlabel('  ')  
plt.ylabel(impact_cat[2]+ ', '+  list_df_ca_aggreg[0]['unit'].iloc[0])  
plt.title(title)
plt.xticks(label_bar_number,label_bar)  
plt.xticks(rotation=45, ha='right')
# Add legend without redundant labels
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
fig.legend(by_label.values(), by_label.keys(), loc='lower center',bbox_to_anchor=(0.5, -0.1))
plt.tight_layout()
#plt.show()
plt.savefig('image2-prod vs consumption.png')
```

## Origin of electricity
* export pie chart to be changed


```python
column="amount (kWh)"
a=0

for df in list_df_to_plot:
    df=df[df["act"]!="market for electricity, high voltage, FE2050"].head()
    fig, ax = plt.subplots()
    patches, texts, autotexts  = ax.pie(df[column], autopct='%1.1f%%',colors=df["color"]) #labels=df["label"]
    [autotext.set_color('white') for autotext in autotexts]
    a=a+1
    plt.savefig('image-origin of electricity.png')
```

```python
#Fonction to plot aggregated amount
def plot_bar_graph_amount(list_df_to_plot, column, rows=[1,2,3], figsize=(5, 5)):
    """Plot amount"""
    # comment
    title='Origin of electricity'
    
    a=0
    label_bar_number=[]
    label_bar=[]
    fig,ax = plt.subplots(figsize=figsize)

    for df in list_df_to_plot:
        #bar graph number
        a=a+1
        #list of bar number
        label_bar_number.append(a)
        #list of bar label
        label_bar.append(df['model'].iloc[0]+', '+ df['SSP']+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))
        base=0
        for row in rows:
            ax.bar(a, df[column].iloc[row], bottom=base, color=df['color'].iloc[row], label=df['label'].iloc[row])
            base=base+df[column].iloc[row]
            
    #Add information on the graph
    plt.xlabel(' ')  
    plt.ylabel('kWh')  
    plt.title(title)
    plt.xticks(label_bar_number,label_bar)  
    plt.xticks(rotation=45, ha='right')
    # Add legend without redundant labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='lower right')
    plt.tight_layout()
    #plt.show()    
    plt.savefig('image-origin of electricity.png')
```

```python
plot_bar_graph_amount(list_df_to_plot=list_df_to_plot, column='amount (kWh)') #title, figsize
```

```python
#Fonction to plot aggregated contribution
def plot_bar_graph_contrib(list_df_to_plot, column, rows=[1,2,3], figsize=(10, 6)):
    """Plot contribution"""
    # comment
    title=impact_cat[2]
    
    a=0
    label_bar_number=[]
    label_bar=[]
    fig,ax = plt.subplots(figsize=figsize)
    
    for df in list_df_to_plot:
        #bar graph number
        a=a+1
        #list of bar number
        label_bar_number.append(a)
        #list of bar label
        label_bar.append(df['model'].iloc[0]+', '+ df['SSP']+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))
        #Plot contributions
        base=0
        for row in rows:
            ax.bar(a, df[column].iloc[row], bottom=base, color=df['color'].iloc[row], label=df['label'].iloc[row])
            base=base+df[column].iloc[row]
        #Plot production mix
        ax.plot(a, df['impact/kWh (absolute)'].iloc[1], color='coral', label='1kWh - production mix', marker = 'o')
        #Add value
        ax.annotate(
            text = f'{round(df[column].iloc[0])}',
            xy=(a, df[column].iloc[0] + 0.1),
            ha='center',
        )        
            
    #Add information on the graph
    plt.xlabel(' ')  
    plt.ylabel(list_df_to_plot[0]['unit'].iloc[0]+ '/kWh')  
    plt.title(title)
    plt.xticks(label_bar_number,label_bar)  
    plt.xticks(rotation=45, ha='right')
    # Add legend without redundant labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=(1.5, 0.8), loc='right')
    plt.tight_layout()
    #plt.show()    
    plt.savefig('image2-contrib to impact.png')
```

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot, column='contribution to impact') #title, figsize
```

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot, column='realloc contribution to impact') #title, figsize
```

```python
column='impact/kWh (absolute)'
title='Impact per kWh'
rows=[1,2,3]

a=0
label_bar_number=[]
label_bar=[]

fig,ax = plt.subplots()

for df in list_df_to_plot:
    a=a+0.2
    #plot consumption mix (bar)
    ax.bar(a,df[column].iloc[0],width=0.1,color=df['color'].iloc[0], label=df['label'].iloc[0])
    #plot production mix (point)
    for row in rows:
        ax.plot(a, df[column].iloc[row], color=df['color'].iloc[row], label=df['label'].iloc[row], marker = 'o')
    #add labels
        ax.annotate(
            text = f'{round(df[column].iloc[0],1)}',
            xy=(a, df[column].iloc[0] + 0.5),
            ha='center',
        )
    
    #Number of the bar
    #list of bar number
    label_bar_number.append(a)
    #list of bar label
    label_bar.append(df['model'].iloc[0]+', '+ df['SSP']+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))


# add labels with bar_label

#Add information on the graph
plt.xlabel('  ')  
plt.ylabel(impact_cat[2]+ ', '+  list_df_ca_aggreg[0]['unit'].iloc[0])  
plt.title(title)
plt.xticks(label_bar_number,label_bar)  
plt.xticks(rotation=45, ha='right')
# Add legend without redundant labels
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
fig.legend(by_label.values(), by_label.keys(), loc='lower center')#,bbox_to_anchor=(0.5, -0.1))
plt.tight_layout()
#plt.show()
plt.savefig('image-mixes comparison.png')
```

<!-- #region editable=true slideshow={"slide_type": ""} -->
# Detailed contribution analysis
<!-- #endregion -->

```python
elec_act_name="market for electricity, high voltage, FE2050"
elec_act_unit='kilowatt hour'
impact_cat=climate
selected_db_list=selected_db_list #premise_db_list
```

```python
list_df_ca=[]

#For each db in the selected list
for db in selected_db_list:
    #initialisation of the dataframe
    df=pd.DataFrame([],columns=[
        'db_name',
        'model',
        'SSP',
        'RCP',
        'FR scenario',
        'year',
        'warning',
        'act',
        'amount',
        'unit amount',
        'contribution to impact before reallocation',
        'unit',
        #'% impact',
        #'impact/kWh (absolute)',
        #'absolute impact/impact elec'
        ])
    
    #Calculate the impact of the chosen activity
    act=db.search(elec_act_name)[0]
    #acts=db.search(elec_act_name)
    #act=[act for act in acts if act["location"]=="WEU"][0]
    lca = act.lca(method=impact_cat, amount=1)
    score_ref = lca.score
    
    #Select the exchanges that compose the activity
    excs=[exc for exc in act.exchanges()]

    for exc in excs:
        if exc["type"]=='technosphere' and "transmission" not in exc['name']:
            #Score act ref
            lca = exc.input.lca(method=impact_cat, amount=exc.amount) #exc.amount
            score = lca.score
            unit_impact= bw2data.Method(impact_cat).metadata["unit"]
            #change unit if climate change
            if unit_impact == "kg CO2-Eq":
                score_ref =1000*score_ref
                score=1000*score
                unit_impact="g CO2-Eq"
            
            score_abs=score/exc["amount"]
            
            df.loc[len(df.index)] = [
                db.name,
                db.model,
                db.SSP,
                db.RCP,
                db.FR_scenario,
                db.year,
                db.warning,
                exc["name"],
                exc["amount"],
                exc.unit,
                score,
                unit_impact,
                #score/score_ref,
                #score_abs,
                #score_abs/score_ref,
            ]
       
    list_df_ca.append(df)

    lca = act.lca(method=impact_cat, amount=1)
    score_ref = lca.score
```

```python
for df in list_df_ca:
    #Total = sum of the impacts including losses excluding direct emissions & grid infra
    total = df['contribution to impact before reallocation'].sum()
    # impact of Losses  
    impact_losses=df.loc[df['act'] == elec_act_name, 'contribution to impact before reallocation'].iloc[0]
    #1kWh total
    score_ref=df.loc[df['act'] == elec_act_name, 'contribution to impact before reallocation'].iloc[0]/df.loc[df['act'] == elec_act_name, 'amount'].iloc[0]
    #reallocation of losses proportionnaly to the absolute impacts, reallocation of grid proportionally to the amount of electricity
    df['contribution to impact']=df['contribution to impact before reallocation']*(1+impact_losses/(total-impact_losses)) +df["amount"]*(score_ref-total)
    df.loc[df['act'] == elec_act_name, 'contribution to impact']=0
    #test = 0
    if df['contribution to impact'].sum()-df.loc[df['act'] == elec_act_name, 'contribution to impact'].iloc[0]-score_ref>1e-10:
        print("issues to be fixed",df['contribution to impact'].sum()-score_ref)
    # % impact
    df['% impact']=df['contribution to impact']/score_ref*100
    df.loc[df['act'] == elec_act_name, '% impact']=0
    df['impact/kWh (absolute)']=df['contribution to impact']/df["amount"]
    df.loc[df['impact/kWh (absolute)'] == elec_act_name, 'impact/kWh (absolute)']=score_ref

    df['contribution of losses/kWh (absolute)']=df['contribution to impact before reallocation']*impact_losses/(total-impact_losses)/df["amount"]
    df.loc[df['act'] == elec_act_name, 'contribution of losses/kWh (absolute)']=0

    df['contribution of grid/kWh (absolute)']=(score_ref-total)
    df.loc[df['act'] == elec_act_name, 'contribution of grid/kWh (absolute)']=0
    
    df['% contribution of grid/kWh (absolute)']=df['contribution of grid/kWh (absolute)']/df['impact/kWh (absolute)']*100
    df.loc[df['act'] == elec_act_name, '% contribution of grid/kWh (absolute)']=0

        #ajust decimals
    #for column in ['contribution to impact',,]:
    #    df[column] = df[column].apply(lambda x: '{:.1f}'.format(x))
    #df['amount (kWh)'] = df['amount (kWh)'].apply(lambda x: '{:.2f}'.format(x))
    #df['% impact] = df['percentage contribution'].apply(lambda x: '{:.0f}'.format(x))
    
    #color the table
    #df=df.style.background_gradient(cmap='Reds',subset=["amount", "% impact","impact/kWh (absolute)",'% contribution of grid/kWh (absolute)'])

    for prod,colorlabel in dict_color.items():
        df.loc[(df['act']==prod), 'color']=colorlabel[0]
        df.loc[(df['act']==prod), 'label']=colorlabel[1]
```

```python
list_df_ca[3]
    
```

```python
#Fonction to plot aggregated contribution
def plot_bar_graph_disagreg_contrib(list_df_to_plot, column, figsize=(10, 6)):
    """Plot contribution"""
    # comment
    title=impact_cat[2]
    
    a=0
    label_bar_number=[]
    label_bar=[]
    fig,ax = plt.subplots(figsize=figsize)
    
    for df in list_df_to_plot:
        rows=list(range(len(df)-1))
        #bar graph number
        a=a+1
        #list of bar number
        label_bar_number.append(a)
        #list of bar label
        label_bar.append(df['model'].iloc[0]+', '+ df['SSP']+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))
        #Plot contributions
        base=0
        for row in rows:
            ax.bar(a, df[column].iloc[row], bottom=base, color=df['color'].iloc[row], label=df['label'].iloc[row])
            base=base+df[column].iloc[row]
        #Plot production mix
        #ax.plot(a, df['contribution to impact'].iloc[1], color='black', label='1kWh - production mix', marker = 'o')
        #Add value
        #ax.annotate(
        #    text = f'{round(df[column].iloc[0])}',
        #    xy=(a, df[column].iloc[0] + 0.1),
        #    ha='center',
        #)        
            
    #Add information on the graph
    plt.xlabel(' ')  
    plt.ylabel(list_df_to_plot[0]['unit'].iloc[0]+ '/kWh')  
    plt.title(title)
    plt.xticks(label_bar_number,label_bar)  
    plt.xticks(rotation=45, ha='right')
    # Add legend without redundant labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=(1.5, 0.8), loc='right')
    plt.tight_layout()
    #plt.show()    
    plt.savefig('image-contrib to impact disaggreg.png')
```

```python
plot_bar_graph_disagreg_contrib(   
    list_df_ca, 'contribution to impact') #
```

```python

```

# Compare standard GWP and premise GWP

```python
premise_db_list

```

```python
selected_db_list=

act_name_list=[
    "market for electricity, high voltage, FE2050",
    #"market for electricity, from direct French production, FE2050",
    #"market for electricity, from storage, FE2050",
    #"market for electricity, from import, FE2050",
]
    
impacts=[climate,climate_premise]
list_df_premisegwp=[]
```

```python

for impact_cat in impacts:
    df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','act','impact','unit'])
    for db in selected_db_list:    
        for act_name in act_name_list:
            #act=agb.findActivity(elec_act_name, db_name=db.name)
            act=db.search(act_name)[0]
            lca = act.lca(method=impact_cat, amount=1)
            score = lca.score
            unit_impact = bw2data.Method(impact_cat).metadata["unit"]
            df.loc[len(df.index)] = [db.name,db.model, db.SSP,db.RCP,db.FR_scenario,db.year,db.warning,act["name"],score,unit_impact]
    list_df_premisegwp.append(df)
```

```python
xlsx_file_name="export-comparison GWP and presimeGWP-01.xlsx"

list_df_to_export=[
    ["GWP"] + list_df_premisegwp,
]

export_data_to_excel(list_df_to_export,xlsx_file_name)
```

```python

```

```python

```

```python

```

```python

```

<!-- #region editable=true slideshow={"slide_type": ""} -->
# OLD
<!-- #endregion -->

## old Detailed contribution analysis


### `🔧` activity, impact category, db to explore

```python
elec_act_name="market for electricity, high voltage, FE2050"
elec_act_unit='kilowatt hour'
impact_cat=climate
selected_db_list=selected_db_list #premise_db_list

```

```python
#unit of the studied impact category
unit_impact= bw2data.Method(impact_cat).metadata["unit"]
```

### Run

```python
list_df_ca=[]

#For each db in the selected list
for db in selected_db_list:
    #initialisation of the dataframe
    df=pd.DataFrame([],columns=[
        'db_name',
        'model',
        'SSP',
        'RCP',
        'FR scenario',
        'year',
        'warning',
        'act',
        'amount',
        'unit amount',
        'impact',
        'unit impact',
        '% impact',
        'absolute impact',
        'absolute impact/impact elec'
        ])
    
    #Calculate the impact of the chosen activity
    act=db.search(elec_act_name)[0]
    #acts=db.search(elec_act_name)
    #act=[act for act in acts if act["location"]=="WEU"][0]
    lca = act.lca(method=impact_cat, amount=1)
    score_ref = lca.score
    #Select the exchanges that compose the activity
    excs=[exc for exc in act.exchanges()]

    for exc in excs:
        if exc["type"]=='technosphere' : #and "transmission" not in exc['name']:
            lca = exc.input.lca(method=impact_cat, amount=exc.amount)
            score = lca.score
            score_abs=score/exc["amount"]
            df.loc[len(df.index)] = [
                db.name,
                db.model,
                db.SSP,
                db.RCP,
                db.FR_scenario,
                db.year,
                db.warning,
                exc["name"],
                exc["amount"],
                exc.unit,
                score,
                unit_impact,
                score/score_ref,
                score_abs,
                score_abs/score_ref,
            ]
       
        if exc["type"]=='biosphere' :
                df.loc[len(df.index)] = [
                db.name,
                db.model,
                db.SSP,
                db.RCP,
                db.FR_scenario,
                db.year,
                db.warning,
                str(exc["name"])+str(exc["categories"]),
                exc["amount"],
                exc["unit"],
                np.nan,
                None,
                np.nan,
                np.nan,
                np.nan,
                ]
    list_df_ca.append(df)
```

## Old Aggregated contribution analysis into 6 subcategories for electricity source
* 1/ direct production
* 2/ flexibilités
* 3/ imports 
* 4/ losses
* 5/ Transmission network
* 6/ Biosphere flows

```python editable=true slideshow={"slide_type": ""}
#list of activities in each subcategory

direct_elec_prod_act_names=[
    "electricity production, nuclear, pressure water reactor",
    "electricity production, Evolutionary Power Reactor (EPR)",
    "electricity production, Small Modular Reactor (SMR)",
    
    "electricity production, hydro, run-of-river",
    "electricity production, hydro, reservoir, alpine region",
    "electricity production, photovoltaic",
    "electricity production, wind, 1-3MW turbine, onshore",
    "electricity production, wind, 1-3MW turbine, offshore",
    "heat and power co-generation, wood chips, 6667 kW",
    "treatment of municipal solid waste, incineration",
    "electricity production, wave energy converter",
    
    "electricity production, natural gas, combined cycle power plant",
    "electricity production, oil",
    "electricity production, hard coal",
    ]

flexibilities_act_names=[
    "electricity production, hydro, pumped storage, FE2050",
    "electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050",
    "electricity production, from vehicle-to-grid, FE2050",
    "electricity supply, high voltage, from vanadium-redox flow battery system, FE2050",
    ]

import_act_name=["market group for electricity, high voltage"]

losses_act_names=["market for electricity, high voltage, FE2050"]

tranmission_act_names=[
    "transmission network construction, electricity, high voltage direct current aerial line",
    "transmission network construction, electricity, high voltage direct current land cable",
    "transmission network construction, electricity, high voltage direct current subsea cable",
]

#Labels of each subcategory
dict_act_subcategories = {
    'direct electricity production in France':direct_elec_prod_act_names,
    'electricity production from flexibilities': flexibilities_act_names,
    'imports':import_act_name,
    'losses':losses_act_names,
    'network':tranmission_act_names
}
```

```python editable=true slideshow={"slide_type": ""}
list_df_ca_aggregated=[]

#For each db in the selected list
for df in list_df_ca:
    #Impact of the market activity
    score_ref = df.loc[df['act'] == elec_act_name, 'absolute impact'].values[0]
    
    #initialisation of the dataframe
    df_ca_aggregated = pd.DataFrame(columns=df.columns)
    
    #For each subcategory we generate a row with the aggregated results
    for label,list_act_names in dict_act_subcategories.items():
        #Filter the rows based on the list of activity names that will be aggregated in this category
        condition = False
        for act_name in list_act_names:
            condition = condition | (df['act'] == act_name)
        filtered_df = df.loc[condition]
        #Aggregate the rows in one row
        result_df = pd.DataFrame(columns=df.columns)
        result_df['db_name']=filtered_df['db_name'].iloc[0],
        result_df['model']=filtered_df['model'].iloc[0],
        result_df['RCP']=filtered_df['RCP'].iloc[0],
        result_df['FR scenario']=filtered_df['FR scenario'].iloc[0],
        result_df['year']=filtered_df['year'].iloc[0],
        result_df['warning']=filtered_df['warning'].iloc[0],
        result_df["act"]=label
        result_df['amount']= filtered_df['amount'].sum(),
        result_df['unit amount']= filtered_df['unit amount'].iloc[0],
        result_df['impact']= filtered_df['impact'].sum(),
        result_df['unit impact']= filtered_df['unit impact'].iloc[0],
        result_df['% impact']= filtered_df['% impact'].sum(),
        #Absolute impact is not the sum of absolute impact but the ratio of sum of impact / sum of amount
        result_df["absolute impact"]=result_df["impact"]/result_df["amount"]
        result_df["absolute impact/impact elec"]=result_df["absolute impact"]/score_ref
        #Add this row to a dataframe
        df_ca_aggregated.loc[len(df_ca_aggregated)] =  result_df.iloc[0]
    
    #We add a row for biosphere flows    
    df_ca_aggregated.loc[len(df_ca_aggregated.index)] = [
            df_ca_aggregated.iloc[0,0],
            df_ca_aggregated.iloc[0,1],
            df_ca_aggregated.iloc[0,2],
            df_ca_aggregated.iloc[0,3],
            df_ca_aggregated.iloc[0,4],
            df_ca_aggregated.iloc[0,5],
            "others : biosphere flows",
            np.nan,
            None,
            score_ref-df_ca_aggregated["impact"].sum(),
            unit_impact,
            1-df_ca_aggregated["% impact"].sum(),
            np.nan,
            np.nan
        ]

    #We add a row for the total impacts
    df_ca_aggregated.loc[len(df_ca_aggregated.index)] = [
            df_ca_aggregated.iloc[0,0],
            df_ca_aggregated.iloc[0,1],
            df_ca_aggregated.iloc[0,2],
            df_ca_aggregated.iloc[0,3],
            df_ca_aggregated.iloc[0,4],
            df_ca_aggregated.iloc[0,5],
            elec_act_name,
            1,
            elec_act_unit,
            score_ref,
            unit_impact,
            score_ref/score_ref,
            score_ref,
            score_ref/score_ref
        ]
    #For each db in the selected list add the dataframe to the list of dataframes
    list_df_ca_aggregated.append(df_ca_aggregated)
```

```python
list_df_ca_aggregated[0]
```

## Old Test contrib analysis storage avec axis 

```python
USER_DB='user_database'
agb.resetDb(USER_DB)

```

### Test axis sur la database

```python
selected_db_list[0].name
```

```python
for db in [selected_db_list[0]]: 
    pumped_storage=db.search('electricity production, hydro, pumped storage, FE2050')[0]
    elec=db.search("market for electricity, high voltage, FE2050")[0]
```

```python
elec["contrib"]="electricity"
elec.save()
pumped_storage.save()
```

```python
agb.compute_impacts(
    pumped_storage,
    climate,
    axis="contrib")
```

```python
agb.compute_impacts(
    pumped_storage,
    climate
    )
```

```python
agb.printAct(pumped_storage)
```

### test axis sur des activités copiées dans USER_DB
Axis fonctionne mais lorsque je copie l'élec sans la modifier "market for electricity, high voltage, FE2050" je n'obtiens pas le même impact pour l'act copiée et pour l'activité originale ???

```python
#db_name=selected_db_list[0].name
for db in [selected_db_list[0]]:  
    pumped_storage_1=db.search('electricity production, hydro, pumped storage, FE2050')[0]
    elec_1=db.search("market for electricity, high voltage, FE2050")[0]
```

```python
pumped_storage_2=agb.copyActivity(USER_DB,pumped_storage_1,"pumped_storage_2")
elec_2=agb.copyActivity(USER_DB,elec_1,"elec_2")
elec_2["contrib"]="electricity"
elec.save()
pumped_storage_2.updateExchanges({ 
    'market for electricity, high voltage, FE2050' : elec_2}) 
```

```python
pumped_storage_2=agb.copyActivity(USER_DB,pumped_storage_1,"pumped_storage_2")
pumped_storage_2.updateExchanges({ 
    'market for electricity, high voltage, FE2050' : None}) 
```

```python
pumped_storage_3=agb.copyActivity(USER_DB,pumped_storage_1,"pumped_storage_3")
elec_3=agb.copyActivity(USER_DB,elec_1,"elec_3")

```

```python
agb.printAct(pumped_storage_1,pumped_storage_2)
```

```python
agb.compute_impacts(
    pumped_storage_2,
    climate,
    axis="contrib"
)
```

```python
agb.compute_impacts(
    [pumped_storage_1,pumped_storage_2,pumped_storage_3],
    climate,
)
```

```python
agb.compute_impacts(
    [elec_1,elec_2,elec_3],
    climate,
)
```

## oLD Ajouter un échange

```python
new_exc=act_storage.new_exchange(
    input=act_elec_stored,
    amount=1.243177, # Example amount
    type='technosphere'
)
new_exc.save()
```

```python

```

# Excel Export

```python editable=true slideshow={"slide_type": ""}
xlsx_file_name="export-test-07.xlsx"

list_df_to_export=[
    ["elec 1 kWh", df_elec_1],
    ["contrib an. aggreg"] + list_df_ca_aggreg,
    ["contrib an. detail"] + list_df_ca,
]

export_data_to_excel(list_df_to_export,xlsx_file_name)
```

```python
xlsx_file_name="export-full-250711.xlsx"

list_df_to_export=[
    ["contrib an. aggreg"] + list_df_ca_aggreg,
    ["storage"]+ list_df_storage #, df_elec_2, df_elec_3, df_elec_4, df_elec_5, df_elec_6],
]

export_data_to_excel(list_df_to_export,xlsx_file_name)
```

```python
xlsx_file_name="export-influence background_2.xlsx"

list_df_to_export=[
    ["background", df_elec_1],
]

export_data_to_excel(list_df_to_export,xlsx_file_name)
```

```python

```
