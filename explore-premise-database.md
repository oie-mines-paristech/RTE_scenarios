---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: lca_alg_12
    language: python
    name: lca_alg_12
---

```python
#If you want you can import climate change impact method that is updated by premise
from premise_gwp import add_premise_gwp
add_premise_gwp()

```

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
NAME_BW_PROJECT="HySPI_premise_FE2050_19"
```

```python
#Set in the right project and print the databases
bw2data.projects.set_current(NAME_BW_PROJECT)
list(bw2data.databases)
#agb.list_databases() #equivalent lca_algebraic function
```

```python
ecoinvent_db_name='ecoinvent-3.10.1-cutoff'
ecoinvent_db=bw2data.Database(ecoinvent_db_name)
biosphere_db_name='ecoinvent-3.10.1-biosphere'
```

```python
#If you need to delete a database
#del bw2data.databases['ei_cutoff_3.10_remind_SSP1-NDC_2050 2025-07-30']
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

for impact_cat in impacts:
    print(impact_cat, bw2data.Method(impact_cat).metadata['unit'])
```

```python
climate_premise=('IPCC 2013', 'climate change', 'GWP 20a, incl. H and bio CO2')

```

```python
#To see all the categories associated with EF3.1
#agb.findMethods("",'EF v3.1')
#[m for m in bw2data.methods if EF == m[0]]
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
    if '2025-07-31' in db.name:
        db.warning='premise v2.3.0dev1'
    if '2025-07-29' in db.name:
        db.warning='premise v2.2.7'
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
#selected_db_list=[db for db in premise_db_list if '2025-05-22' in db.name and 'update' not in db.name]+[db for db in premise_db_list if db.name=='ei_cutoff_3.9_tiam-ucl_SSP2-RCP45_2050_Reference - N1 2025-05-15']+[db for db in premise_db_list if db.name=='ei_cutoff_3.9_tiam-ucl_SSP2-Base_2050_Reference - N1 2025-05-15']
selected_db_list
#selected_db_list=[selected_db_list[2]]
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
    'treatment of municipal solid waste, municipal incineration',
    "electricity production, wave energy converter",
    
    "electricity production, natural gas, combined cycle power plant",
    "electricity production, oil",
    "electricity production, hard coal",
    ]

storage_act_names=[
    "electricity production, hydro, pumped storage, FE2050",
    "electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050",
    "electricity production, from vehicle-to-grid, FE2050",
    "electricity supply, high voltage, from vanadium-redox flow battery system, FE2050",
    ]

import_act_name=["market for electricity production, direct production, high voltage, FE2050"]

losses_act_names=["market for electricity, high voltage, FE2050"]

transmission_act_names=[
    "transmission network construction, electricity, high voltage direct current aerial line",
    "transmission network construction, electricity, high voltage direct current land cable",
    "transmission network construction, electricity, high voltage direct current subsea cable",
]

#Labels of each subcategory
dict_act_subcategories = {
    'direct electricity production in France':direct_elec_prod_act_names,
    'electricity production from flexibilities': storage_act_names,
    'imports':import_act_name,
    'losses':losses_act_names,
    'network':transmission_act_names
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
    "treatment of municipal solid waste, municipal incineration":['chartreuse','biomass and waste'],
        
    "electricity production, natural gas, combined cycle power plant":['slategrey','gas'],
    "electricity production, oil":['black','oil and coal'],
    "electricity production, hard coal":['black','oil and coal'],
    
    "electricity production, wave energy converter":['blue','wave'],    
    
    "electricity production, hydro, pumped storage, FE2050":['royalblue','electricity from storage'], #'rebeccapurple'
    "electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050":['royalblue','electricity from storage'],
    "electricity production, from vehicle-to-grid, FE2050":['royalblue','electricity from storage'],
    "electricity supply, high voltage, from vanadium-redox flow battery system, FE2050":['royalblue','electricity from storage'],
    
    "market group for electricity, high voltage":['midnightblue','imports'], #magenta
    "market for electricity production, direct production, high voltage, FE2050":['midnightblue','imports'],
     }  
```

```python
list_dict_storage=[
    {
    'act_storage_name':'electricity production, hydro, pumped storage, FE2050',
    'act_where_elec_is_stored_name':'electricity production, hydro, pumped storage, FE2050',
    #'act_elec_stored_name':"market for electricity, high voltage, FE2050"
     },
    {
    'act_storage_name':'electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050',
    'act_where_elec_is_stored_name':'hydrogen production, gaseous, 30 bar, from PEM electrolysis, from grid electricity, domestic, FE2050',
    #'act_elec_stored_name':"market for electricity, high voltage, FE2050"
    },    
    {
    'act_storage_name':'electricity production, from vehicle-to-grid, FE2050',
    'act_where_elec_is_stored_name':'electricity production, from vehicle-to-grid, FE2050',
    #'act_elec_stored_name':"market for electricity, high voltage, FE2050"
     },
    {
    'act_storage_name':'electricity supply, high voltage, from vanadium-redox flow battery system, FE2050',
    'act_where_elec_is_stored_name':'electricity supply, high voltage, from vanadium-redox flow battery system, FE2050',
    #'act_elec_stored_name':"market for electricity, high voltage, FE2050"
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
1.0312427*1.0042*1.0307
#0.0312427 	0.0042 0.0307 pertes high/medium/low
#8% RTE

```

# Database modification : Run only once


## Create new French electricity activity with European mix as import mix 

```python
selected_db_list
```

```python
#Db list where you want to change the imports
selected_db_list=premise_db_list
#if I just want to create a market with imports from european mix generated with the same IAM
with_EUR_imports_severals="no" 
#if I want to create french markets with imports from european mix taken from other IAM
with_EUR_imports_severals="no" 
#db_import_list is the list from where imports come from with_EUR_imports_severals="yes"
db_import_list_severals=[premise_db_list[0]]+[premise_db_list[1]]+[premise_db_list[2]] 
```

Ignore the warnings in the next cell

```python
for db in selected_db_list:
    db_import_list=[db] #if I just want to create a market with imports from european mix generated with the same IAM
    if with_EUR_imports_severals=="yes": #with imports from european mix taken from other IAM
        db_import_list=db_import_list_severals 
    for db_import in db_import_list:
        #To add to activity names
        add_to_act_name=", with European market "+db_import.model+'-'+db_import.SSP+'-'+db_import.RCP+" as import mix"
        
        #Copy the french electricity mix
        french_mix=db.search("market for electricity, high voltage, FE2050")[0]
        french_mix_copy = agb.copyActivity(
            db_name=db.name,                   # Database where the new activity is copied
            activity = french_mix,             # initial activity
            code="market for electricity, high voltage, FE2050"+add_to_act_name #
        )
        
        excs_elec=[exc for exc in french_mix_copy.exchanges()]
    
        #Safety check : check that original and copied activity have the same impacts
        #lca1 = french_mix.lca(method=impact_cat, amount=1)
        #score1 = lca1.score
        #lca2 = french_mix_copy.lca(method=impact_cat, amount=1)
        #score2 = lca2.score
        #if (score1-score2)>1e-08:
        #    print("error original activity and copied activity do not have the same impact")
        #print("{:.5f}".format(score1))
        #print("{:.5f}".format(score2))
    
    
        #Copy storage elec activities with elec input at level 1
        for act_storage_name in ["electricity production, from vehicle-to-grid, FE2050",'electricity production, hydro, pumped storage, FE2050',"electricity supply, high voltage, from vanadium-redox flow battery system, FE2050"]:
            act_storage=db.search(act_storage_name)[0]
            act_storage_copy = agb.copyActivity(
                db_name=db.name,                   # Database where the new activity is copied
                activity = act_storage,             # initial activity
                code=(act_storage["name"]+", with European market "+add_to_act_name)
            )
        #Replace input elec mix in copied storage activities
            excs=[exc for exc in act_storage_copy.exchanges()]
            for exc in excs:
                if exc.input["name"]==french_mix["name"]:
                    exc.input=french_mix_copy
                    exc.save()
        #Replace by copied storage activities in French mix                
            for exc in excs_elec:
                if exc.input["name"]==act_storage_name:
                    exc.input=act_storage_copy
                    exc.save()
                    
        #Specific case  for hydrogen storage as elec input is not at level 1
        for act_storage_name in ["electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050"]:
    
            #Replace elec input in copied activity at level1
            act1=db.search("hydrogen production, gaseous, 30 bar, from PEM electrolysis, from grid electricity, domestic, FE2050")[0]
            act1_copy = agb.copyActivity(
                db_name=db.name,                   # Database where the new activity is copied
                activity = act1,             # initial activity
                code=(act1["name"]+", with European market "+add_to_act_name)
            )
    
            excs=[exc for exc in act1_copy.exchanges()]
            for exc in excs:
                if exc.input["name"]==french_mix["name"]:
                    exc.input=french_mix_copy
                    exc.save()
    
            #Replace by copied activity in intermediate activity at level 2
            act2=db.search("hydrogen storage, for grid-balancing, FE2050")[0]
            act2_copy = agb.copyActivity(
                db_name=db.name,                   # Database where the new activity is copied
                activity = act2,             # initial activity
                code=(act2["name"]+", with European market "+add_to_act_name)
            )
    
            excs=[exc for exc in act2_copy.exchanges()]
            for exc in excs:
                if exc.input["name"]==act1["name"]:
                    exc.input=act1_copy
                    exc.save()
    
            #Replace by copied activity from level 2 in storage activity
            act_storage=db.search(act_storage_name)[0]
            act_storage_copy = agb.copyActivity(
                db_name=db.name,                   # Database where the new activity is copied
                activity = act_storage,             # initial activity
                code=(act_storage["name"]+", with European market "+add_to_act_name)
            )
    
            excs=[exc for exc in act_storage_copy.exchanges()]
            for exc in excs:
                if exc.input["name"]==act2["name"]:
                    exc.input=act2_copy
                    exc.save()
    
            #Replace by copied storage activity in French mix                
            for exc in excs_elec:
                if exc.input["name"]==act_storage_name:
                    exc.input=act_storage_copy
                    exc.save()
    
                
            #Replace the import activity by the French production mix from direct elec (without : grid,losses,imports,storage)
            #Save the import amount as act["import"]
        
        import_prod=[act for act in db_import if act["name"]=='market group for electricity, high voltage' and act["location"]=="RER"][0]
    
        for exc in excs_elec:
            if exc.input["name"]=="market for electricity production, direct production, high voltage, FE2050":
                #french_mix_copy["import"]=exc["amount"]
                #french_mix_copy.save()
                exc.input=import_prod
                exc.save()


                #create import market (with losses and grid)
        import_mix=db.search("market for electricity, from import, FE2050")[0]
        import_mix_copy = agb.copyActivity(
            db_name=db.name,                   # Database where the new activity is copied
            activity = import_mix,             # initial activity
            code="market for electricity, from import, FE2050"+add_to_act_name
        )
        excs_import=[exc for exc in import_mix_copy.exchanges()]
        #Change the input elec
        for exc in excs_import:
            if exc.input["name"]=="market for electricity production, direct production, high voltage, FE2050":
                exc.input=import_prod
                exc.save()

```

# Impact 1 kWh of electricity


## `🔧` database, impact category, activities

```python
premise_db_list
```

```python
#selected_db_list=premise_db_list
selected_db_list=[db for db in premise_db_list if 'N03' in db.name and 'SSP2-RCP45' in db.name]+[db for db in premise_db_list if 'N1' in db.name and 'SSP2-RCP45' in db.name]+[db for db in premise_db_list if 'M0' in db.name and 'SSP2-RCP45' in db.name]

impact_cat_list=[climate]#,metals_minerals,land,ionising_rad]
#impact_cat=climate

act_name_list=[
    "market for electricity, high voltage, FE2050",
    #"market for electricity, high voltage, FE2050"+", with European market "+db_import.model+'-'+db_import.SSP+'-'+db_import.RCP+" as import mix",
    "market for electricity, from direct French production, FE2050",
    #market for electricity production, direct production, high voltage, FE2050",
    #"market for electricity, from storage, FE2050",
    #"market for electricity, from import, FE2050",
    #"market for electricity production, high voltage, with French market as import mix, FE2050"
]
selected_db_list
```

## Run

```python
    #Generate a list of impact and 'unit' and a list of impacts
    impact_unit_list=[]
    impact_list=[]
    for tuple1 in impact_cat_list:
        impact_unit_list.append(tuple1[1])
        impact_unit_list.append('unit')
        impact_list.append(tuple1[1])

    #initialise the dataframe
    df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','act']+impact_unit_list )
    #df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','act','score','unit'])#+impact_unit_list )
    
    for db in selected_db_list:    
        for act_name in act_name_list:
            #act=db.search(act_name)[0]
            act=[act for act in db if act["name"]==act_name and act["location"]=="FR"][0]
            score_unit_list=[]
            
            for impact_cat in impact_cat_list:
                unit_impact = bw2data.Method(impact_cat).metadata["unit"]
                unit=unit_impact
                lca = act.lca(method=impact_cat, amount=1)
                score = lca.score
                #print(score,unit)

            #Rescale in gCO2 instead of kgCO2 for climate change
                if unit_impact == "kg CO2-Eq":
                    score=1000*score
                    unit="g CO2-Eq"
                #print(score,unit)
                score_unit_list.append(score)
                score_unit_list.append(unit)
            #Store data
            df.loc[len(df.index)] = [db.name,db.model, db.SSP, db.RCP,db.FR_scenario,db.year,db.warning,act["name"]]+score_unit_list
            #df.loc[len(df.index)] = [db.name,db.model, db.SSP, db.RCP,db.FR_scenario,db.year,db.warning,act["name"],score,unit]#+score_unit_list
```

```python
df
```

```python editable=true slideshow={"slide_type": ""}
df_elec_1=df.style.background_gradient(cmap='Reds',subset=impact_list)
df_elec_1
```

# Aggregated contribution analysis


## `🔧` databases, impact category

```python
impact_cat=climate
#impact_cat=climate_premise

#if I want to calculate in addition, impacts of markets with imports from european mix generated with the same IAM
with_EUR_imports="no"
##if I want to calculate in addition, impacts markets with imports from sev european mix taken from other IAM
with_EUR_imports_severals="no" 
#db_import_list is the list from where imports come from with_EUR_imports_severals="yes"
db_import_list_severals=[premise_db_list[0]]+[premise_db_list[1]]+[premise_db_list[2]] 
```

## Run

```python
list_df_ca_aggreg=[]
unit_impact = bw2data.Method(impact_cat).metadata["unit"]
unit=unit_impact

act_name_list=[
    "market for electricity, high voltage, FE2050",
    "market for electricity, from direct French production, FE2050",
    "market for electricity, from storage, FE2050",
    "market for electricity, from import, FE2050",
]

for db in selected_db_list:  
    df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','act','amount (kWh)','contribution to impact','unit'])    
    
    #Amount of direct electricity / storage / imports
    act=db.search("market for electricity, high voltage, FE2050")[0]
    excs=[exc for exc in act.exchanges()]
    amount_direct_elec=0
    amount_storage=0
    amount_import=0
    for exc in excs:
        if exc.input["name"] in direct_elec_prod_act_names:
            amount_direct_elec = exc["amount"]+amount_direct_elec
        if exc.input["name"] in storage_act_names:
            amount_storage = exc["amount"]+amount_storage
        if exc.input["name"] in import_act_name:
            amount_import = exc["amount"]+amount_import
    
    # Safety Check 
        if exc.input["name"] not in direct_elec_prod_act_names + storage_act_names+import_act_name+[act["name"]]:
            if "transmission" not in exc.input["name"] and "Ozone" not in exc.input["name"] and "Dinitrogen"not in exc.input["name"]:
                print("warning: exchange", exc.input["name"], "forgotten")
            
    #Impact of each mix (total, from direct production, from storage, from import)
    for act_name in act_name_list:
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

            #change of unit for climate change
        if unit_impact == "kg CO2-Eq":
            score=1000*score
            unit="g CO2-Eq"       
            
        #export to dataframe
        df.loc[len(df.index)] = [db.name,db.model, db.SSP,db.RCP,db.FR_scenario,db.year,db.warning,act["name"],amount,score,unit]

    #Calculation for mix with French imports
    total = df['contribution to impact'].iloc[1:].sum()            
    #Add columns to calculate the contribution to impacts (percentage)
    df['percentage contribution']=df['contribution to impact']/total*100
    #Absolute impact/kWh
    df["impact/kWh (absolute)"]=df["contribution to impact"]/df["amount (kWh)"]
    #add label and color for plots
    df['label']=['consumption mix','from direct electricity production','from storage','from imports']
    df['color']=['orange','deepskyblue','royalblue','midnightblue']

    #Safety check
    if (df["amount (kWh)"].iloc[1:].sum()-1)>1e-4:
        print("error in amount")
        print(df["amount (kWh)"].iloc[1:].sum())
    if (total-df['contribution to impact'].iloc[0])>1e-4:
        print("error in impact")
        print(total,df['contribution to impact'].iloc[0])

    #Redo the calculation when imports from other EUR market
    if with_EUR_imports=="yes":
        db_import_list=[db] #if I just want to create a database with self eur import 
        if with_EUR_imports_severals=="yes":
            db_import_list=db_import_list_severals
        for db_import in db_import_list:
            add_to_act_name=", with European market "+db_import.model+'-'+db_import.SSP+'-'+db_import.RCP+" as import mix"
            
            #score consumption mix 
            act_elec=db.search("market for electricity, high voltage, FE2050"+add_to_act_name)[0]
            lca = act_elec.lca(method=impact_cat, amount=1)
            score_0 = lca.score
            if unit_impact == "kg CO2-Eq":
                score_0=1000*score_0
            
            #score direct production mix is the same as with French imports
            score_1=df['contribution to impact'].iloc[1]
            
            #score imports
            import_mix=db.search("market for electricity, from import, FE2050"+add_to_act_name)[0]
            lca = import_mix.lca(method=impact_cat, amount=amount_import)
            score_3 = lca.score
            if unit_impact == "kg CO2-Eq":
                score_3=1000*score_3
        
            #score storage is the rest
            score_2=score_0-score_1-score_3
    
            #Add to dataframe
            add_to_column_name=" with EUR imports "+db_import.model+'-'+db_import.SSP+'-'+db_import.RCP
            df["contribution to impact"+add_to_column_name]=[score_0,score_1,score_2,score_3]

            total = df['contribution to impact'+add_to_column_name].iloc[1:].sum()            
            #Add columns to calculate the contribution to impacts (percentage)
            df['percentage contribution'+add_to_column_name]=df['contribution to impact'+add_to_column_name]/total*100
            #Absolute impact/kWh
            df["impact/kWh (absolute)"+add_to_column_name]=df["contribution to impact"+add_to_column_name]/df["amount (kWh)"]        
    
    #For each db in the selected list add the dataframe to the list of dataframes
    list_df_ca_aggreg.append(df)
```

```python
#change decimals
    #for column in ['impact', 'contribution to impact']:
    #    df[column] = df[column].apply(lambda x: '{:.1f}'.format(x))
    #df['amount (kWh)'] = df['amount (kWh)'].apply(lambda x: '{:.2f}'.format(x))
    #df['percentage contribution'] = df['percentage contribution'].apply(lambda x: '{:.0f}'.format(x))
    
#Color the table
    #df=df.style.background_gradient(cmap='Reds',subset=["impact", "contribution to impact"])

```

```python
list_df_ca_aggreg[1]
```

# Dissagregate contribution storage


## `🔧` databases for efficency
## `🔧` databases, losses

```python
#For efficency : choose a database from same year as all databases from same year have same efficencies
db=selected_db_list[1]

#For disaggregation
selected_db_list=selected_db_list
grid_losses=0.03109
```

## Storage efficencies 

```python
        df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','act','% efficency','storage losses (kWh)'])

        #french electricity mix
        french_mix=db.search("market for electricity, high voltage, FE2050")[0]        
        excs_elec=[exc for exc in french_mix.exchanges()]
    
        #Storage elec activities with elec input at level 1
        for act_storage_name in ["electricity production, from vehicle-to-grid, FE2050",'electricity production, hydro, pumped storage, FE2050',"electricity supply, high voltage, from vanadium-redox flow battery system, FE2050"]:
            act_storage=db.search(act_storage_name)[0]
  
            #calculate efficency with input elec mix
            excs=[exc for exc in act_storage.exchanges()]
            for exc in excs:
                if exc.input["name"]=="market for electricity, high voltage, FE2050":
                    #print(act_storage_name)
                    #print("{:.2f}".format(exc.amount))
                    #print("{:.1f}".format(1/exc.amount*100))
                    df.loc[len(df.index)] = [db.name,db.model, db.SSP, db.RCP, db.FR_scenario,db.year,db.warning,act_storage_name,(1/exc.amount*100),(exc.amount-1)]

        #Specific case h2 storage
        for act_storage_name in ["electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050"]:
            #calculate efficency by multiplying flows at different levels
            #level 1
            act1=db.search("hydrogen production, gaseous, 30 bar, from PEM electrolysis, from grid electricity, domestic, FE2050")[0] 
            excs=[exc for exc in act1.exchanges()]
            for exc in excs:
                if exc.input["name"]==french_mix["name"]:
                    a=exc.amount
                    #print("{:.2f}".format(exc.amount))
            #Level 2
            act2=db.search("hydrogen storage, for grid-balancing, FE2050")[0]    
            excs=[exc for exc in act2.exchanges()]
            for exc in excs:
                if exc.input["name"]==act1["name"]:
                    b=exc.amount
                    #print("{:.2f}".format(exc.amount))
            #Level 3
            act_storage=db.search(act_storage_name)[0]    
            excs=[exc for exc in act_storage.exchanges()]
            for exc in excs:
                if exc.input["name"]==act2["name"]:
                    c=exc.amount
                    #print("{:.2f}".format(exc.amount))
                    #print(act_storage_name)
                    #print("{:.1f}".format(1/(a*b*c)*100))
                    df.loc[len(df.index)] = [db.name,db.model, db.SSP, db.RCP, db.FR_scenario,db.year,db.warning,act_storage_name,1/(a*b*c)*100,a*b*c-1]

df_storage_efficency=df
df_storage_efficency
```

## Disaggregation of storage

```python
list_df_storage=[]
unit_impact = bw2data.Method(impact_cat).metadata["unit"]
unit=unit_impact

efficency='NA'
storage_losses='NA'

for db in selected_db_list: 
    df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','act','amount in elec market (kWh)','% efficency','storage losses (kWh)','impact 1kWh prod elec from storage','impact storage infra','impact 1 kWh elec consumption mix','impact 1 kWh elec mix from prod and import','impact grid per kWh','unit'])    

    #French electricity market
    act_market_elec= db.search("market for electricity, high voltage, FE2050")[0]
    act_market_elec_name=act_market_elec["name"]
    lca = act_market_elec.lca(method=impact_cat, amount=1)
    score_elec=lca.score #Total : Electricity from storage score
    excs_market_elec=[exc for exc in act_market_elec.exchanges()]

    #French electricity market
    act_prod_import_elec= db.search('market for electricity, from direct production and import, FE2050')[0]
    lca = act_prod_import_elec.lca(method=impact_cat, amount=1)
    score_prod_import_elec=lca.score #Total : Electricity from storage score

    #French electricity market
    act_prod_import_elec= db.search('market for electricity, from direct production and import, FE2050')[0]
    lca = act_prod_import_elec.lca(method=impact_cat, amount=1)
    score_prod_import_elec=lca.score #Total : Electricity from storage score
    print(score_prod_import_elec*1000)
    
    #Electricity has 2 times grid (input elec for storage + output elec when released)
    act_grid= db.search("high voltage grid, per kWh, FE2050")[0]
    lca = act_grid.lca(method=impact_cat, amount=1)
    score_grid=lca.score #Total : Electricity from storage score    
    score_elec_with_grid=score_elec+score_grid

    if unit_impact == "kg CO2-Eq":
            score_elec=1000*score_elec
            score_grid=1000*score_grid
            unit="g CO2-Eq"

    score_elec_with_grid=score_elec+score_grid

    for diki in list_dict_storage:

        #storage activity to study
        act_storage_name=diki['act_storage_name']
        act_storage=[act for act in db if act["name"]==act_storage_name][0]
        
        #Calculate impact
        lca = act_storage.lca(method=impact_cat, amount=1)
        total_elec_from_storage=lca.score
        
        #activity that countains the electricity flow to be stored
        act_where_elec_is_stored_name=diki['act_where_elec_is_stored_name']
        act_where_elec_is_stored=[act for act in db if act["name"]==act_where_elec_is_stored_name][0]
        
        #Elec flow stored 
        #act_elec_stored=db.search(act_elec_stored_name)[0]       
        #act_elec_stored_name=diki['act_elec_stored_name']
        #lca = act_elec_stored.lca(method=impact_cat, amount=1)
        #score_elec=lca.score #Total : Electricity from storage score
    
        #Modification of the activity that countains the electricity flow to be stored
        #This flow is turned to zero to model only LCI of infrastructure
        excs=[exc for exc in act_where_elec_is_stored.exchanges()]
        for exc in excs:
            amount=0
            if exc.input["name"]==act_market_elec_name:
                amount=exc["amount"]
                exc["amount"]=0
                exc.save()
        lca = act_storage.lca(method=impact_cat, amount=1)
        infra=lca.score #Storage infrastructure score
        
        #Delete modification
        for exc in excs:
            if exc.input["name"]==act_market_elec_name:
                exc["amount"]=amount
                exc.save()
        #lca = act_storage.lca(method=impact_cat, amount=1)
        #test=lca.score #test
        
        #Test that the database was nos modified
        #if total_elec_from_storage!=test:
        #    print('warning you modified your database')

        #Conversion for climate change impact
        if unit_impact == "kg CO2-Eq":
            total_elec_from_storage =1000*total_elec_from_storage
            infra=1000*infra

        #Storage amount in electricity mix
        exc_amount=0
        for exc in excs_market_elec:
            if exc.input["name"]==act_storage_name:
                exc_amount=exc["amount"]

        #Store scores in a dataframe
        df.loc[len(df.index)] = [db.name,db.model, db.SSP, db.RCP, db.FR_scenario,db.year,db.warning,act_storage_name,exc_amount,efficency,storage_losses,total_elec_from_storage,infra,score_elec,score_prod_import_elec,score_grid,unit] 
    #For each db in the selected list add the dataframe to the list of dataframes
    list_df_storage.append(df)           

```

```python
for df in list_df_storage:
    for diki in list_dict_storage:
        act_storage_name=diki['act_storage_name']
        df.loc[df['act'] == act_storage_name, '% efficency']=df_storage_efficency.loc[df_storage_efficency['act'] == act_storage_name, '% efficency'].values
        df.loc[df['act'] == act_storage_name, 'storage losses (kWh)']=df_storage_efficency.loc[df_storage_efficency['act'] == act_storage_name, 'storage losses (kWh)'].values
```

### with grid infra allocated to electicity production > ok it works but overestimates impacts from original production

```python
grid_losses_factor=1/(1-grid_losses)

#Calculations
for df in list_df_storage:
    #Impact
    df['impact grid final'] =  grid_losses_factor*df['impact grid per kWh'] 
    # Reallocate grid to electricity proportionnaly to the amount of electricity
    df['impact storage infra final'] =  grid_losses_factor*df['impact storage infra']/(1-df['amount in elec market (kWh)'])
    df['impact storage losses final'] = grid_losses_factor*(df['storage losses (kWh)']*df['impact 1 kWh elec consumption mix'])/(1-df['amount in elec market (kWh)']*df['storage losses (kWh)'])    + df['impact grid final']*df['storage losses (kWh)']/(1+df['storage losses (kWh)'])
    df['impact original elec final'] = grid_losses_factor*df['impact 1kWh prod elec from storage'] - df['impact storage infra final']  - df['impact storage losses final']          + df['impact grid final']*1
    df['impact 1kWh elec from storage'] = df['impact storage infra final']+df['impact storage losses final']+df['impact original elec final'] #+ df['impact grid final']+
    df['unit bis']=df['unit']

    #contribution
    df['contrib grid']=df['impact grid final']/df['impact 1kWh elec from storage']*100    
    df['contrib storage infra']=df['impact storage infra final']/df['impact 1kWh elec from storage']*100
    df['contrib storage losses']=df['impact storage losses final']/df['impact 1kWh elec from storage']*100
    df['contrib original elec']=df['impact original elec final']/df['impact 1kWh elec from storage']*100

    #Repartition of storage technology in electricity mix
    df['% amount in elec market'] = df['amount in elec market (kWh)'] / df['amount in elec market (kWh)'].sum()
```

### with grid infra not allocated > ok but it still overestimates impacts from original elec as electricity losses (due to double ) are accounted for original elec

```python
grid_losses_factor=1/(1-grid_losses)

#Calculations
for df in list_df_storage:
    #Impact
    df['impact storage infra final'] =  grid_losses_factor*df['impact storage infra']/(1-df['amount in elec market (kWh)'])
    df['impact storage losses final'] = grid_losses_factor*(df['storage losses (kWh)']*df['impact 1 kWh elec consumption mix'])/(1-df['amount in elec market (kWh)']*df['storage losses (kWh)'])
    df['impact original elec final'] = grid_losses_factor*df['impact 1kWh prod elec from storage'] - df['impact storage infra final']  - df['impact storage losses final']
    df['impact grid final'] =  grid_losses_factor*df['impact grid per kWh']
    df['impact 1kWh elec from storage final'] = df['impact grid final']+df['impact storage infra final']+df['impact storage losses final']+df['impact original elec final']
    df['unit bis']=df['unit']

    #contribution
    #df['contrib grid']=df['impact grid final']/df['impact 1kWh elec from storage']*100    
    #df['contrib storage infra']=df['impact storage infra final']/df['impact 1kWh elec from storage']*100
    #df['contrib storage losses']=df['impact storage losses final']/df['impact 1kWh elec from storage']*100
    #df['contrib original elec']=df['impact original elec final']/df['impact 1kWh elec from storage']*100

    #Repartition of storage technology in electricity mix
    df['% amount in elec market'] = df['amount in elec market (kWh)'] / df['amount in elec market (kWh)'].sum()
```

### Ok : grid contribution is recalculated by forcing impact of original electricity

```python
#Calculations
for df in list_df_storage:

    #Repartition of storage technology in electricity mix
    df['% amount in elec market'] = df['amount in elec market (kWh)'] / df['amount in elec market (kWh)'].sum()
    
    #Impact    
    df['impact storage infra final'] =  grid_losses_factor*df['impact storage infra']/(1-df['amount in elec market (kWh)'])
    df['impact storage losses final'] = grid_losses_factor*(df['storage losses (kWh)']*df['impact 1 kWh elec consumption mix'])/(1-df['amount in elec market (kWh)']*df['storage losses (kWh)'])
    df['impact original elec inter'] = grid_losses_factor*df['impact 1kWh prod elec from storage'] - df['impact storage infra final']  - df['impact storage losses final']
    df['impact grid inter'] =  grid_losses_factor*df['impact grid per kWh']
    df['impact 1kWh elec from storage inter'] = df['impact grid inter']+df['impact storage infra final']+df['impact storage losses final']+df['impact original elec inter']

    #Recalculation of original elec impacts > reallocation of the difference to the grid
    df['impact original elec final']= 1*df['impact 1 kWh elec mix from prod and import']
    df['impact grid final']=df['impact grid inter']+df['impact original elec inter']-df['impact original elec final']
    df['impact 1kWh elec from storage final'] = df['impact grid final']+df['impact storage infra final']+df['impact storage losses final']+df['impact original elec final']
    
    #df['impact original elec final']= 1*df['impact 1 kWh elec mix from prod and import'] 
    #df['impact grid final']=df['impact grid final']+

    #contribution
    #df['contrib grid']=df['impact grid final']/df['impact 1kWh elec from storage']*100    
    #df['contrib storage infra']=df['impact storage infra final']/df['impact 1kWh elec from storage']*100
    #df['contrib storage losses']=df['impact storage losses final']/df['impact 1kWh elec from storage']*100
    #df['contrib original elec']=df['impact original elec final']/df['impact 1kWh elec from storage']*100


```

### Run

```python
for df in list_df_storage:
    #weight the imacts based on the repartition in the electricity market
    df['Helper'] = df["% amount in elec market"] * df['% efficency']    
    df.loc[0,'efficency storage mix'] = df['Helper'].sum()    
    df['Helper'] = df["% amount in elec market"] * df['storage losses (kWh)']    
    df.loc[0,'storage losses in storage mix'] = df['Helper'].sum()    
    df['Helper'] = df["% amount in elec market"] * df['impact 1kWh elec from storage final']    
    df.loc[0,'impact elec from storage mix'] = df['Helper'].sum() #to be compared with storage with from aggregated contribution
    
    df['Helper'] = df["% amount in elec market"] * df['impact grid final']       
    df.loc[0,'impact grid in storage mix'] = df['Helper'].sum()
    df['Helper'] = df["% amount in elec market"] * df['impact storage infra final']   
    df.loc[0,'impact storage infra in storage mix'] = df['Helper'].sum()
    df['Helper'] = df["% amount in elec market"] * df['impact storage losses final']   
    df.loc[0,'impact storage losses in storage mix'] = df['Helper'].sum()
    df['Helper'] = df["% amount in elec market"] * df['impact original elec final']   
    df.loc[0,'impact original elec in storage mix'] = df['Helper'].sum()
    del df["Helper"]
```

```python
list_df_disaggreg_storage=[]
for df in list_df_storage:
    df2=pd.concat([df.iloc[0:1, 0:7],df.iloc[0:1, -12::] ], axis=1) #reajuster les :: pour faire apparaitre les colonnes intéressantes. 
    list_df_disaggreg_storage.append(df2)           
df_disaggreg_storage=pd.concat(list_df_disaggreg_storage,axis=0)
df_disaggreg_storage
```

```python

```

```python
list_df_storage==========list_df_clean

#for df in list_df_storage:
#    del(df['contrib original elec'])

#for df in list_df_storage:
#    df=df.rename(columns={"impact 1 kWh input elec without grid" : 'impact 1 kWh elec consumption mix'})
#list_df_storage[2]=list_df_storage[2].rename(columns={"impact 1 kWh input elec without grid" : 'impact 1 kWh elec consumption mix'})
#list_df_storage=list_df_storage_2
```

```python
dict_color_storage={
    'impact elec from storage mix':['tot','tot'],
    'impact original elec in storage mix':['green','impact of 1kWh of electricity if there was no storage'],
    'impact grid in storage mix':['blue','additional transport in the electricity grid'],
    'impact storage infra in storage mix':['yellow', 'storage infrastructure'],
    'impact storage losses in storage mix':['red','storage & release electricity losses'],
    }

        
```

```python
list_df_storage_to_print=[]
for df in list_df_storage:
    df2=pd.concat([df.iloc[0:1, 0:7] ], axis=1) #+ unit
    n=0
    for i in range (len(dict_color_storage)):
        df2.loc[i]=df2.iloc[0]
    for contribution,colorlabel in dict_color_storage.items():
        df2.loc[n,'what contributes'] = contribution
        df2.loc[n,'impact'] = df.loc[0,contribution]
        df2.loc[n,'unit'] = df.loc[0,'unit']
        df2.loc[n,'color'] = colorlabel[0]
        df2.loc[n,'label'] = colorlabel[1]
        n=n+1
    list_df_storage_to_print.append(df2)
list_df_storage_to_print[0]
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
plot_order=[0,1,2] #

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
    label_bar.append(df['model'].iloc[0]+', '+ df['SSP'].iloc[0]+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))


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
    label_bar.append(df['model'].iloc[0]+', '+ df['SSP'].iloc[0]+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))


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
        label_bar.append(df['model'].iloc[0]+', '+ df['SSP'].iloc[0]+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))
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
        label_bar.append(df['model'].iloc[0]+', '+ df['SSP'].iloc[0]+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))
        #Plot contributions
        base=0
        for row in rows:
            ax.bar(a, df[column].iloc[row], bottom=base, color=df['color'].iloc[row], label=df['label'].iloc[row])
            base=base+df[column].iloc[row]
        #Plot production mix
        #ax.plot(a, df['impact/kWh (absolute)'].iloc[1], color='coral', label='1kWh - production mix', marker = 'o')
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
list_df_storage_to_print[2]
```

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_storage_to_print, rows=[1,2,3,4],column='impact') #title, figsize
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
    label_bar.append(df['model'].iloc[0]+', '+ df['SSP'].iloc[0]+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))


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
selected_db_list=premise_db_list #premise_db_list
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
        label_bar.append(df['model'].iloc[0]+', '+ df['SSP'].iloc[0]+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))
        
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

# Compare standard GWP and premise GWP

```python
premise_db_list
selected_db_list=

```

```python

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

storage_act_names=[
    "electricity production, hydro, pumped storage, FE2050",
    "electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050",
    "electricity production, from vehicle-to-grid, FE2050",
    "electricity supply, high voltage, from vanadium-redox flow battery system, FE2050",
    ]

import_act_name=["market group for electricity, high voltage"]

losses_act_names=["market for electricity, high voltage, FE2050"]

transmission_act_names=[
    "transmission network construction, electricity, high voltage direct current aerial line",
    "transmission network construction, electricity, high voltage direct current land cable",
    "transmission network construction, electricity, high voltage direct current subsea cable",
]

#Labels of each subcategory
dict_act_subcategories = {
    'direct electricity production in France':direct_elec_prod_act_names,
    'electricity production from flexibilities': storage_act_names,
    'imports':import_act_name,
    'losses':losses_act_names,
    'network':transmission_act_names
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

## Old test imports with lca_algebraic parameter

```python
USER_DB='user_database'
agb.resetDb(USER_DB)
#code = "french mix with french imports" +'-'+ db.model+'-'+db.SSP+'-'+db.RCP+'-'+db.FR_scenario+'-'+str(db.year)
```

```python
elec_mix_imports_origin=agb.newEnumParam( 
    "elec_mix_imports_origin",             # Short name
    label="origin of import mix",             # label
    description="switch the origin of electricity mix chosen for imports", # Long description  
    #group="xxx",                   # (optional) to class your parameters in group
    values =[                       # Statistic weight of each option that fits with the market
        "european",
        "french",
    ],
    default="european")             # the default value is a string
```

```python
elec_mix_imports = agb.newSwitchAct(
                    USER_DB, # Database where the new activity is created
                    "import electricity mix",                                      
                    elec_mix_imports_origin, #enum parameter that is used to switch the activity
                            {
                                "european":european_mix,
                                "french": french_mix_copy,
                            })
```

```python
french_mix_copy.updateExchanges({ 
    'market group for electricity, high voltage' : elec_mix_imports})  
```

```python
agb.printAct(french_mix,french_mix_copy)
```

## Old Create a French production mix (without losses, without grid, with french imports)


```python
    french_prod_mix_copy = agb.copyActivity(
        db_name=db.name,                   # Database where the new activity is copied
        activity = french_mix_copy,             # initial activity
        code="market for electricity production, high voltage, with French market as import mix, FE2050"
        )
    excs=[exc for exc in french_prod_mix_copy.exchanges()]
        
    for exc in excs:
        if "transmission" in exc.input["name"]: 
            exc.delete()
            exc.save()
        if "Ozone" in exc.input["name"]: 
            exc.delete()
            exc.save()
        if "Dinitrogen" in exc.input["name"]: 
            exc.delete()
            exc.save()
        if exc.input["name"]=='market group for electricity, high voltage':
            exc.input=french_prod_mix_copy
            exc.save()    
```

```python

```

# Excel Export

```python editable=true slideshow={"slide_type": ""}
xlsx_file_name="export-elec-several impact cat-2.xlsx"

list_df_to_export=[
    ["elec 1 kWh", df],
    #["contrib an. aggreg"] + list_df_ca_aggreg,
    #["contrib an. detail"] + list_df_ca,
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
xlsx_file_name="export-storage.xlsx"

list_df_to_export=[
    ["storage",df_disaggreg_storage] #, df_elec_2, df_elec_3, df_elec_4, df_elec_5, df_elec_6],
]

export_data_to_excel(list_df_to_export,xlsx_file_name)
```

```python

```
