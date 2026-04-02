---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: lca_alg_132
    language: python
    name: lca_alg_132
---

```python editable=true slideshow={"slide_type": ""}
#importation of usefull packages
import bw2data
import bw2io
import pandas as pd
import numpy as np
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import lca_algebraic as agb

#import custom functions
from utils import save_xls, import_xls_list_df, create_empty_act, change_input_storage_mix, storage_input_mix_name
from activities_type_label import *
```

```python
#If you want you can import climate change impact method that is updated by premise
from premise_gwp import add_premise_gwp
add_premise_gwp()
```

# Intitialisation: `🔧` Project name and ecoinvent names

```python
NAME_BW_PROJECT="HySPI_premise_FE2050_26"
ecoinvent_db_name='ecoinvent-3.10.1-cutoff'
biosphere_db_name='ecoinvent-3.10.1-biosphere'
```

```python
#Set in the right project and print the databases
bw2data.projects.set_current(NAME_BW_PROJECT)
ecoinvent_db=bw2data.Database(ecoinvent_db_name)
list(bw2data.databases)
```

```python
#If you need to delete a database
#del bw2data.databases['ei_cutoff_3.10_image_SSP2-M_2050_Reference - M1 2026-03-17']
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
climate_premise=('IPCC 2021', 'climate change', 'GWP 100a, incl. H and bio CO2')
```

```python
#To see all the categories associated with EF3.1
#agb.findMethods("",'EF v3.1')
[m for m in bw2data.methods if 'incl. H and bio CO2' in m[2]]
#[m for m in bw2data.methods if 'Copper' in m[2]]
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
model_list=['image','tiam-ucl','remind','remind-eu',"message"]
year_list=['2020','2050']
SSP_list=['SSP1','SSP2','SSP3','SSP4','SSP5']
RCP_list=['Base','RCP19','RCP26','RCP45','Npi','NDC','-M_','-L','-H','PkBudg1000','NDC','NPi','ML','VLHO','rollBack','PkBudg650']
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
    #Correction of RCP
    if db.RCP=='-M_':
        db.RCP='M'
    if db.RCP=='-L':
        db.RCP='L'
    if db.RCP=='-H':
        db.RCP='H'
```

```python
#Each database can be sorted with these tags
df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning'])
for db in premise_db_list:
    df.loc[len(df.index)] = [db.name,db.model,db.SSP,db.RCP,db.FR_scenario,db.year, db.warning]
    print(db.name)
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
selected_db_list=[db for db in premise_db_list if 'M0' in db.name and 'Base' not in db.name and 'RCP26' not in db.name]# and 'update' not in db.name]+[db for db in premise_db_list if db.name=='ei_cutoff_3.9_tiam-ucl_SSP2-RCP45_2050_Reference - N1 2025-05-15']
selected_db_list_1=[db for db in premise_db_list if 'image_SSP2-M_2050' in db.name and 'M0' in db.name]
#selected_db_list=[selected_db_list[-3]]
selected_db_list=selected_db_list_1
```

# Dev en cours


## Database modification

```python
new_input_name="market for electricity production, direct production, high voltage, FE2050"
```

```python
#create_empty_act(selected_db_list)
#change_input_storage_mix(selected_db_list,new_input_name)
```

## Pertes high medium low 

```python
1.0312427*1.0042*1.0307
#0.0312427 	0.0042 0.0307 pertes high/medium/low
#8% RTE

```

# Impact 1 kWh of electricity
Calculate the impact of a chosen activity per several scenarios / years


## `🔧` database, impact category, activities

```python
#premise_db_list
```

```python
#selected_db_list=[premise_db_list[0]]#,premise_db_list[1],premise_db_list[4],]
selected_db_list
```

```python
impact_cat_list=[climate] #,climate_premise]#,acidification]##,metals_minerals,land,ionising_rad]
#impact_cat=climate

act_name_list=[    
    "market for electricity, high voltage, FE2050",
    #"market for electricity, from direct French production, FE2050",
    #"market for electricity, from storage, FE2050",
    #"market for electricity, from import, FE2050",
    #"market for electricity production, direct production, high voltage, FE2050",
    #"market group for electricity, high voltage",
]
```

```python
#Helper to delete
    #"market group for electricity, high voltage",
    #"market for electricity, high voltage, FE2050, with European mix Ecoinvent 3.10.1 as import mix",
    #"market for electricity, high voltage, FE2050, with European market tiam-ucl-SSP2-Base as import mix", 
    #'market for electricity, high voltage, FE2050, with European market tiam-ucl-SSP2-RCP45 as import mix',
    #"market for electricity, high voltage, FE2050, with European market tiam-ucl-SSP2-RCP26 as import mix",  
    #"market for electricity, high voltage, FE2050, with onshore wind mix as import mix"
    #"market for electricity, high voltage, FE2050, with empty activity as import mix",
    
    #"market for electricity, from direct French production, FE2050",
    #market for electricity production, direct production, high voltage, FE2050",
    #"market for electricity, from storage, FE2050",
    #"market for electricity, from import, FE2050",

    #electricity production, nuclear, pressure water reactor",
    #"electricity production, Evolutionary Power Reactor (EPR)",
    #"electricity production, Small Modular Reactor (SMR)",
    
    #"electricity production, hydro, run-of-river",
    #"electricity production, hydro, reservoir, alpine region",
    #"electricity production, photovoltaic",
    #"electricity production, wind, 1-3MW turbine, onshore",
    #"electricity production, wind, 1-3MW turbine, offshore",

```

## Run

```python
    #Generate a list of impact and 'unit' and a list of impacts
    impact_unit_list=[]
    for tuple1 in impact_cat_list:
        if 'incl. H and bio CO2' in tuple1[2]:
            impact_unit_list.append(tuple1[1]+' premise')
        else:
            impact_unit_list.append(tuple1[1])
        impact_unit_list.append('unit')

    #initialise the dataframe
    #df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','act','impact/kWh (absolute)','unit' ]) #+impact_unit_list )
    df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','act'] + impact_unit_list )
    
    for db in selected_db_list:  
        #act_name_list.append("market for electricity, high voltage, FE2050, with European market "+db.model+'-'+db.SSP+'-'+db.RCP+" as import mix")
        for act_name in act_name_list:
            #act=db.search(act_name)[0]
            if act_name=="electricity production, Small Modular Reactor (SMR)":
                loc="CH"
            if act_name=="market group for electricity, high voltage":
                loc="RER"
            if act_name=="market for copper, cathode":
                loc="GLO"
            else:
                loc="FR"
            act=[act for act in db if act["name"]==act_name and act["location"]==loc][0]
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
        #del act_name_list[-1]
    df
```

```python editable=true slideshow={"slide_type": ""}
#Helper to delete or fixme
#if len(impact_cat_list)==1:
#    df_elec_1=df.style.background_gradient(cmap='Reds',subset=[impact_unit_list[0]])#impact_unit_list[0])
#else:
#    df_elec_1=df
```

```python
df.to_excel('impact_act_1.xlsx')
```

# Aggregated contribution analysis
Contribution analysis between :
* electricity from direct production
* electricity from storage
* electricity from imports
* optionnaly : electricity from curtailement


## `🔧` databases, impact category

```python
#selected_db_list=[db for db in premise_db_list if 'N03' in db.name and 'SSP2-RCP45' in db.name]+[db for db in premise_db_list if 'N1' in db.name and 'SSP2-RCP45' in db.name] +[db for db in premise_db_list if 'M0' in db.name and 'SSP2-RCP45' in db.name]
selected_db_list
```

```python
impact_cat=climate
#impact_cat=climate_premise
```

## `🔧` optional features : curtailed energy

```python
curtailment_included="yes"
```

```python
if curtailment_included=="yes":
    df_curtailment=import_xls_list_df('curtailed_electricity.xlsx')[0]
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
    df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','impact','act','amount (kWh)','contribution to impact','unit'])    
    
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
    
    # Safety Check that direct_elec_prod_act_names + storage_act_names+import_act_name covers al the activities
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
        df.loc[len(df.index)] = [db.name,db.model, db.SSP,db.RCP,db.FR_scenario,db.year,db.warning,impact_cat[1],act["name"],amount,score,unit]

    #Add curtailment
    if curtailment_included=="yes":
        act=db.search("market for electricity production, direct production, high voltage, FE2050")[0]
        amount=df_curtailment[df_curtailment['FR_scenario']==db.FR_scenario][db.year].squeeze()
        lca = act.lca(method=impact_cat, amount=amount)
        curtailment_score=lca.score
        if unit_impact == "kg CO2-Eq":
            curtailment_score=1000*curtailment_score
        df.loc[len(df.index)] = [db.name,db.model, db.SSP,db.RCP,db.FR_scenario,db.year,db.warning,impact_cat[1],'curtailment',amount,curtailment_score,unit]
        #add curtailment score to market score
        market_score=df.loc[df['act']=='market for electricity, high voltage, FE2050','contribution to impact']    
        df.loc[df['act']=='market for electricity, high voltage, FE2050','contribution to impact']=market_score+curtailment_score
        df.loc[df['act']=='market for electricity, high voltage, FE2050','impact/kWh (absolute)']=market_score+curtailment_score

    
    #Calculation for mix
    total = df['contribution to impact'].iloc[1:].sum()       

    #Add columns to calculate the contribution to impacts (percentage)
    df['percentage contribution']=df['contribution to impact']/total*100
    #Absolute impact/kWh
    df["impact/kWh (absolute)"]=df["contribution to impact"]/df["amount (kWh)"]
    #add label and color for plots
    df['label']=['consumption mix','from direct electricity production','from storage','from imports','curtailment']
    df['color']=['grey','deepskyblue','royalblue','midnightblue','black']

    #Safety check
    if (df["amount (kWh)"].iloc[1:3].sum()-1)>1e-4:
        print("error in amount")
        print(df["amount (kWh)"].iloc[1:3].sum())
    if (total-df['contribution to impact'].iloc[0])>1e-4:
        print("error in impact")
        print(total,df['contribution to impact'].iloc[0])

    list_df_ca_aggreg.append(df)

```

```python
list_df_ca_aggreg[0]
```

```python
save_xls('list_df_ca_aggreg_1.xlsx',list_df_ca_aggreg)
```

### old : with different exports

```python
#if I want to calculate in addition, impacts of markets with imports from european mix generated with the same IAM
with_EUR_imports="no" #"yes"
##if I want to calculate in addition, impacts markets with imports from sev european mix taken from other IAM
with_EUR_imports_severals="no" #"yes"
#db_import_list is the list from where imports come from with_EUR_imports_severals="yes"
db_import_list_severals=[premise_db_list[0]]+[premise_db_list[1]]+[premise_db_list[2]] 
#If I want to calculate a list from one database
with_add_to_act_names="no" #"yes"

add_to_act_names_list=[
    ", with European mix Ecoinvent 3.10.1 as import mix",
    ", with European market tiam-ucl-SSP2-Base as import mix", 
    ', with European market tiam-ucl-SSP2-RCP45 as import mix',
    ", with European market tiam-ucl-SSP2-RCP26 as import mix",  
    #", with onshore wind mix as import mix",
    ", with empty activity as import mix",
]
```

```python
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
    list_df_ca_aggreg.append(df)

    #Redo the calculation when imports from other EUR market
           
    if with_add_to_act_names=="yes":
        df['config']='with French production mix as import'
        for add_to_act_name in add_to_act_names_list:
            #Copy df and delete impact results
            df2=df.copy()
            df2['contribution to impact']=None
            df2['percentage contribution']=None
            df2["impact/kWh (absolute)"]=None

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
            df2["contribution to impact"]=[score_0,score_1,score_2,score_3]

            total = df2['contribution to impact'].iloc[1:].sum()            
            #Add columns to calculate the contribution to impacts (percentage)
            df2['percentage contribution']=df2['contribution to impact']/total*100
            #Absolute impact/kWh
            df2["impact/kWh (absolute)"]=df2["contribution to impact"]/df2["amount (kWh)"]
            df2['config']=add_to_act_name

            #For each add_to_act_names, add the list to the score
            list_df_ca_aggreg.append(df2)


#Add a column for hatches
#for df in list_df_ca_aggreg:
#    df['hatch']=None
```

```python
#To be deleted if not useful
#df_elec_1['color']='grey'
#df_elec_1['label']='consumption mix'

#for df in list_df_ca_aggreg:
#    df['color']=['grey','deepskyblue','royalblue','midnightblue']

#list_df_ca_aggreg_2=[df_elec_1]+list_df_ca_aggreg
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

# Disaggregate electricity from storage and imports into 2

```python
list_df_ca_aggreg_bis=[]

for df in list_df_ca_aggreg:

    #insert empty lines
    df2=df.copy()
    for n in [3,4,6,7]:
        df2 = pd.DataFrame(np.insert(df2.values, n, values =len(df.columns)*[np.NaN],axis=0))
    df2.columns = df.columns

    #add information on the empty lines
    df2.loc[3,'act']="electricity from storage replaced by production mix"
    df2.loc[3,'label']="electricity from storage replaced by production mix"
    df2.loc[3,'color']="royalblue"

    df2.loc[4,'act']='storage losses and infrastructure'
    df2.loc[4,'label']='storage losses and infrastructure'
    df2.loc[4,'color']="royalblue"

    df2.loc[6,'act']="electricity from imports replaced by production mix"
    df2.loc[6,'label']="electricity from imports replaced by production mix"
    df2.loc[6,'color']="midnightblue"

    df2.loc[7,'act']='differential impacts due to imports'
    df2.loc[7,'label']='differential impacts due to imports'
    df2.loc[7,'color']="midnightblue"
    
    #Impact of production mix
    impact_mix_prod=df2.loc[(df2['act']=="market for electricity, from direct French production, FE2050"),'impact/kWh (absolute)'].values.tolist()[0]
    
    #divide in 2 the impact of electricity from storage
    amount_sto=df2.loc[(df2['act']=="market for electricity, from storage, FE2050"),'amount (kWh)'].values.tolist()[0]
    impact_sto=df2.loc[(df2['act']=="market for electricity, from storage, FE2050"),'contribution to impact'].values.tolist()[0]
    #"electricity from storage replaced by production mix" = amount storage * impact mix direct prod and import (in our case mix prod and import = mix direct prod)
    df2.loc[(df2['act']=="electricity from storage replaced by production mix"),'contribution to impact']=impact_mix_prod*amount_sto
    #storage infra and losses impact is the rest
    df2.loc[(df2['act']=='storage losses and infrastructure'),'contribution to impact']=impact_sto-impact_mix_prod*amount_sto

    #divide in 2 the impacts of imports
    b1=df2.loc[(df2['act']=="market for electricity, from import, FE2050"),'amount (kWh)'].values.tolist()[0]
    c1=df2.loc[(df2['act']=="market for electricity, from import, FE2050"),'contribution to impact'].values.tolist()[0]
    #imports
    df2.loc[(df2['act']=="electricity from imports replaced by production mix"),'contribution to impact']=impact_mix_prod*b1
    #differential impact is the rest
    df2.loc[(df2['act']=='differential impacts due to imports'),'contribution to impact']=c1-impact_mix_prod*b1
    df2.loc[5,'label']='differential impacts due to imports'
  
    #recalculate percentage contribution
    df2['percentage contribution']=df2['contribution to impact']/df2.loc[0,'contribution to impact']

    #Calculate contributuion to difference 
    df2['contribution to difference']=df2['amount (kWh)']*(df2['impact/kWh (absolute)']-impact_mix_prod)
    for act in ['storage losses and infrastructure','differential impacts due to imports','curtailment']:
        df2.loc[(df2['act']==act),'contribution to difference']=df2.loc[(df2['act']==act),'contribution to impact']
    
    df2['contribution to difference %']=df2['contribution to difference']/impact_mix_prod*100

    #Safety check
    test=df2['contribution to difference'].iloc[3]+df2['contribution to difference'].iloc[4]-df2['contribution to difference'].iloc[0]
    if test > 1e-5:
        write('warning total does not equal consumption mix')

    #Put unit on all lines
    df['unit']=df.loc[0,'unit']
    
    #Add df2 to the list
    list_df_ca_aggreg_bis.append(df2)
list_df_ca_aggreg_bis[0]
```

```python
save_xls('list_df_ca_aggreg_bis_1.xlsx',list_df_ca_aggreg_bis)
```

# Dissagregate contribution storage btw losses and infrastructure


## `🔧` databases for efficiency calculation !!!! same year 
## `🔧` databases, losses, impact categories

```python
#For efficiency : choose a database from same year as all databases from same year have same efficencies
db=selected_db_list[0]

#For disaggregation
selected_db_list=selected_db_list

#grid_losses
grid_losses=0.03109
grid_losses_factor=1/(1-grid_losses)

impact_cat=climate
```

## Storage efficencies 

```python
        df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','act','% efficiency','storage losses (kWh)'])

        #french electricity mix
        french_mix=db.search("market for electricity, high voltage, FE2050")[0]        
        excs_elec=[exc for exc in french_mix.exchanges()]
    
        #Storage elec activities with elec input at level 1
        for act_storage_name in ["electricity production, from vehicle-to-grid, FE2050",'electricity production, hydro, pumped storage, FE2050',"electricity supply, high voltage, from vanadium-redox flow battery system, FE2050"]:
            act_storage=db.search(act_storage_name)[0]
  
            #calculate efficiency with input elec mix
            excs=[exc for exc in act_storage.exchanges()]
            for exc in excs:
                if exc.input["name"]==storage_input_mix_name:
                    #print(act_storage_name)
                    #print("{:.2f}".format(exc.amount))
                    #print("{:.1f}".format(1/exc.amount*100))
                    df.loc[len(df.index)] = [db.name,db.model, db.SSP, db.RCP, db.FR_scenario,db.year,db.warning,act_storage_name,(1/exc.amount*100),(exc.amount-1)]

        #Specific case h2 storage
        for act_storage_name in ["electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050"]:
            #calculate efficiency by multiplying flows at different levels
            #level 1
            act1=db.search("hydrogen production, gaseous, 30 bar, from PEM electrolysis, from grid electricity, domestic, FE2050")[0] 
            excs=[exc for exc in act1.exchanges()]
            for exc in excs:
                if exc.input["name"]==storage_input_mix_name:
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

        df_storage_efficiency=df
        df_storage_efficiency
```

## Disaggregation of storage

```python
list_df_storage=[]
unit_impact = bw2data.Method(impact_cat).metadata["unit"]
unit=unit_impact

zero=0.0
columns = ['db_name','model','SSP','RCP','FR scenario','year','warning','act',
           'amount in elec market (kWh)','% efficiency','storage losses (kWh)',
           'impact 1kWh prod elec from storage','impact storage losses','impact storage infra',
           'impact 1 kWh elec consumption market','impact 1 kWh elec market from prod','impact 1 kWh pure production','impact 1 kWh elec market from storage','unit']

for db in selected_db_list: 
    df=pd.DataFrame([],columns=columns)    

    #French electricity market
    act_market_elec_name="market for electricity, high voltage, FE2050"
    act_market_elec= db.search(act_market_elec_name)[0]
    lca = act_market_elec.lca(method=impact_cat, amount=1)
    score_elec=lca.score #Total : Electricity from storage score
    excs_market_elec=[exc for exc in act_market_elec.exchanges()]

    #Consumption mix from direct production
    act_market_prod_elec= db.search('market for electricity, from direct French production, FE2050')[0]
    lca = act_market_prod_elec.lca(method=impact_cat, amount=1)
    score_prod_market=lca.score 

    #Production mix from direct production
    act_market_prod_elec= db.search('market for electricity production, direct production, high voltage, FE2050')[0]
    lca = act_market_prod_elec.lca(method=impact_cat, amount=1)
    score_prod_pure=lca.score

    #Consumption mix from storage
    act_market_prod_elec= db.search('market for electricity, from storage, FE2050')[0]
    lca = act_market_prod_elec.lca(method=impact_cat, amount=1)
    score_storage_market=lca.score 
    
    #Infra grid impact
    #act_grid_infra= db.search("high voltage grid, per kWh, FE2050")[0]
    #lca = act_grid_infra.lca(method=impact_cat, amount=1)
    #score_grid_infra=lca.score #Total : Electricity from storage score 

    if unit_impact == "kg CO2-Eq":
            score_elec=1000*score_elec
            score_prod_market=1000*score_prod_market
            score_prod_pure=1000*score_prod_pure    
            #score_grid_infra=1000*score_grid_infra
            unit="g CO2-Eq"

    for diki in list_dict_storage:
        #storage activity to study
        act_storage_name=diki['act_storage_name']
        act_storage=[act for act in db if act["name"]==act_storage_name][0]
        #Calculate impact
        lca = act_storage.lca(method=impact_cat, amount=1)
        total_elec_from_storage=lca.score

        if unit_impact == "kg CO2-Eq":
            total_elec_from_storage =1000*total_elec_from_storage
            
        #Infra > input elec=0
        #change_input_storage_mix([db],"empty activity")
        #lca = act_storage.lca(method=impact_cat, amount=1)
        #storage_infra=lca.score

        #Back
        #change_input_storage_mix([db],new_input_name)

        #Conversion for climate change impact
        #if unit_impact == "kg CO2-Eq":
            #total_elec_from_storage =1000*total_elec_from_storage
            #storage_infra=1000*storage_infra

        #Storage amount in electricity mix
        exc_amount=0
        for exc in excs_market_elec:
            if exc.input["name"]==act_storage_name:
                exc_amount=exc["amount"]


        #Store scores in a dataframe
        df.loc[len(df.index)] = [db.name,db.model, db.SSP, db.RCP, db.FR_scenario,db.year,db.warning,act_storage_name,
                                 exc_amount,zero,zero,
                                 total_elec_from_storage,zero,zero,
                                 score_elec,score_prod_market,score_prod_pure, score_storage_market,unit] 
        #For each db in the selected list add the dataframe to the list of dataframes
    list_df_storage.append(df)           

```

```python
for df in list_df_storage:
    for diki in list_dict_storage:
        act_storage_name=diki['act_storage_name']
        df.loc[df['act'] == act_storage_name, '% efficiency']=df_storage_efficiency.loc[df_storage_efficiency['act'] == act_storage_name, '% efficiency'].values
        df.loc[df['act'] == act_storage_name, 'storage losses (kWh)']=df_storage_efficiency.loc[df_storage_efficiency['act'] == act_storage_name, 'storage losses (kWh)'].values
    df['impact storage losses']=df['storage losses (kWh)']*df['impact 1 kWh pure production']
    df['impact storage infra']=df['impact 1kWh prod elec from storage']-(1+df['storage losses (kWh)'])*df['impact 1 kWh pure production']
```

```python
#Calculations
for df in list_df_storage:
    #Repartition of storage technology in electricity mix
    df['% amount in elec market'] = df['amount in elec market (kWh)'] / df['amount in elec market (kWh)'].sum()
    #weight the imacts based on the repartition in the electricity market
    df['Helper'] = df["% amount in elec market"] * df['% efficiency']    
    df.loc[0,'efficiency storage mix'] = df['Helper'].sum()    
    df['Helper'] = df["% amount in elec market"] * df['storage losses (kWh)']    
    df.loc[0,'storage losses in storage mix'] = df['Helper'].sum()    

    #Impact in consumption mix. Correction by grid losses factor
    df['Helper'] = df["% amount in elec market"] * df['impact storage losses']*grid_losses_factor
    df.loc[0,'impact storage losses in consumption mix'] = df['Helper'].sum()    
    
    df['Helper'] = df["% amount in elec market"] * df['impact storage infra']*grid_losses_factor 
    df.loc[0,'impact storage infra in consumption mix'] = df['Helper'].sum()    

```

```python
save_xls('impact_storage_1.xlsx',list_df_storage)
```

```python
list_df_ca_aggreg_bis[0]
```

```python
n=0
list_df_ca_aggreg_ter=[]
for df in list_df_ca_aggreg_bis:
    #Extract storage related data from df and df_sto
    df_sto=list_df_storage[n]
    impact_mix_prod=df_sto.loc[0,'impact 1 kWh elec market from prod']
    losses_sto=df_sto.loc[0,'impact storage losses in consumption mix']
    infra_sto= df_sto.loc[0,'impact storage infra in consumption mix']
    amount_sto=df.loc[(df['act']=="market for electricity, from storage, FE2050"),'amount (kWh)'].values.tolist()[0]
    #losses_sto*amount_sto
    #infra_sto*amount_sto

    #insert empty lines
    df2=df.copy()
    for n in [5,6]:
        df2 = pd.DataFrame(np.insert(df2.values, n, values =len(df.columns)*[np.NaN],axis=0))
    df2.columns = df.columns

    #Label and act of new lines
    df2.loc[5,'label']='storage losses'
    df2.loc[5,'act']='storage losses' 
    df2.loc[6,'label']='storage infrastructure'
    df2.loc[6,'act']='storage infrastructure'

    #Calculate contribution to difference
    df2.loc[df2['label'] == 'storage losses','contribution to difference']=losses_sto*amount_sto
    df2.loc[df2['label'] == 'storage losses','contribution to impact']=losses_sto*amount_sto

    df2.loc[df2['label'] == 'storage infrastructure','contribution to difference']=infra_sto*amount_sto
    df2.loc[df2['label'] == 'storage infrastructure','contribution to impact']=infra_sto*amount_sto

    impact_mix_prod=df2.loc[(df2['act']=="market for electricity, from direct French production, FE2050"),'impact/kWh (absolute)'].values.tolist()[0]
    df2['contribution to difference %']=df2['contribution to difference']/impact_mix_prod

    #safety check
    test=df2['contribution to difference'].iloc[5]+df2['contribution to difference'].iloc[6]-df2['contribution to difference'].iloc[4]
    if test > 1e-5:
        print('warning total does not equal consumption mix')

    #recalculate percentage contribution
    df2['percentage contribution']=df2['contribution to impact']/df2.loc[0,'contribution to impact']

    #Put unit on all lines
    df['unit']=df.loc[0,'unit']

    list_df_ca_aggreg_ter.append(df2)

list_df_ca_aggreg_ter[0]
```

```python
save_xls('list_df_ca_aggreg_ter_1.xlsx',list_df_ca_aggreg_ter)
```

# Graphs

```python
list_df_ca_aggreg=import_xls_list_df('list_df_ca_aggreg_1.xlsx')
list_df_ca_aggreg_bis=import_xls_list_df('list_df_ca_aggreg_bis_1.xlsx')
list_df_ca_aggreg_ter=import_xls_list_df('list_df_ca_aggreg_ter_1.xlsx')

```

```python
for df in list_df_ca_aggreg:
    df['hatch']=None
    df['year']=df['year'].astype('Int64')
```

```python
for df in list_df_ca_aggreg_bis:
    df['hatch']=None
    df.loc[(df['label']=="electricity from storage replaced by production mix"),'hatch']="///"
    df.loc[(df['label']=="storage losses and infrastructure"),'hatch']='++'
    df.loc[(df['label']=="electricity from imports replaced by production mix"),'hatch']="///"
    df.loc[(df['label']=='differential impacts due to imports'),'hatch']='++'
    df['year']=df['year'].astype('Int64')
```

```python
for df in list_df_ca_aggreg_ter:
    df['hatch']=None
    df.loc[df['label'] == 'storage losses','hatch']='---'
    df.loc[df['label'] == 'storage infrastructure','hatch']='||'
    df.loc[(df['label']=='differential impacts due to imports'),'hatch']='++'
    df['year']=df['year'].astype('Int64')
```

```python
#Recap : list of databases covered by list_df_ca_aggreg
list_df = pd.DataFrame(columns=list_df_ca_aggreg[0].columns)
for df in list_df_ca_aggreg:
    list_df=pd.concat([list_df,df.head(1)],ignore_index=True)
list_df
```

```python
list_df_to_plot=list_df_ca_aggreg

```

```python
change_plot_order="no" #yes"

```

## `🔧` Optional : choose specific change databases to compare and order

```python
change_plot_order="yes" #yes"
#Choose what you want to plot in which order on the graphs
plot_order=[1,4,7]
```

```python
if change_plot_order=="yes": 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg[order])
```

## Origin of electricity


### Aggregated origin : pie chart

```python
#to select only one graph
#index_pie_chart=1
```

```python
column="amount (kWh)"
for df in list_df_to_plot:
#for df in [list_df_to_plot[index_pie_chart]]: #to select only one graph
    df=df[df["act"]!="market for electricity, high voltage, FE2050"]
    fig, ax = plt.subplots()
    patches, texts, autotexts  = ax.pie(
        df[column],
        autopct='%1.1f%%',
        colors=df["color"],
        textprops = {"fontsize":30,"weight":"bold"},
        pctdistance=1.55,
        radius=0.9,
        explode = [0,0,0.15],
        startangle=5,

    )
        
        #explode = [0,0.2,0.2],
        #labeldistance=.6
        #labels=df["label"]
    plt.title(df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))
    [autotext.set_color('black') for autotext in autotexts]
    plt.savefig('image-origin of electricity.png')
```

### Aggregated origin : Bar graph

```python
#Fonction to plot aggregated amount
def plot_bar_graph_french_scenarios(list_df_to_plot, column, title, starting_row=0, add_percentage='yes', figsize=(3, 6),color_percentage='black'):
    """Plot amount"""
    title=title
    
    a=0
    b=0.4
    
    label_bar_number=[]
    label_bar=[]
    base_list=[]

    fig,ax = plt.subplots(figsize=figsize)

    for df in list_df_to_plot:
        #bar graph number
        a=a+b
        #list of bar number
        label_bar_number.append(a)
        #list of bar label
        label_bar.append(df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))
        base=0

        #which rows you want to print
        rows=[]
        for i in range(starting_row, len(df)):
            rows.append(i)

        for row in rows:
            ax.bar(a, df[column].iloc[row], bottom=base, color=df['color'].iloc[row], label=df['label'].iloc[row], width=0.2)
            base=base+df[column].iloc[row]
        base_list.append(base)

    n=-1
    if add_percentage == 'yes':
            for bar in ax.patches:
                if bar.get_x()!=b:
                    b=bar.get_x()
                    n=n+1
                    base=base_list[n]
                
                if bar.get_height()!=0:
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2 + bar.get_y(),
                    f'{round(bar.get_height()/base*100)}%', 
                    ha = 'center', color = color_percentage, size = 10, weight = 'bold')        
    
    #Add information on the graph
    plt.xlabel(' ')  
    plt.ylabel('kWh')  
    plt.title(title)
    plt.xticks(label_bar_number,label_bar)  
    plt.xticks(rotation=45, ha='right')
    # Add legend without redundant labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=(0.5, 1.08), loc='center')

    plt.tight_layout()
    #plt.show()    
    plt.savefig('image-origin of electricity.png')
```

```python
plot_bar_graph_french_scenarios(list_df_to_plot=list_df_to_plot, column='amount (kWh)', title='Origin of electricity per kWh consumed', starting_row=1,figsize=(8, 16),color_percentage='white')
```

```python
#plot_bar_graph_french_scenarios(list_df_to_plot=[list_df_to_plot_storage_mix[0],list_df_to_plot_storage_mix[2]], column='amount', title='Electricity from storage', starting_row=0)
```

### Production mix : Pie chart

```python
selected_db_list_to_plot=selected_db_list
```

```python
if change_plot_order=="yes": 
    #Generate the list of databases to plot
    selected_db_list_to_plot= []
    for order in plot_order:
        selected_db_list_to_plot.append(selected_db_list[order])

```

```python
#selected_db_list_to_plot=[premise_db_list[7],premise_db_list[4]]
selected_db_list_to_plot
```

```python
list_df_mix=[]

elec_act_name="market for electricity, high voltage, FE2050"

#For each db in the selected list
for db in selected_db_list_to_plot:
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
        #'% impact',
        #'impact/kWh (absolute)',
        #'absolute impact/impact elec'
        ])
    
    #Calculate the impact of the chosen activity
    act=db.search(elec_act_name)[0]
    
    #Select the exchanges that compose the activity
    excs=[exc for exc in act.exchanges()]

    for exc in excs:
        if exc["type"]=='technosphere' and "transmission" not in exc['name']:            
            df.loc[len(df.index)] = [
                db.name,
                db.model,
                db.SSP,
                db.RCP,
                db.FR_scenario,
                db.year,
                db.warning,
                exc.input["name"],
                exc.amount,
                exc.unit,
            ]
       
    list_df_mix.append(df)

#Add color, labels
for df in list_df_mix:
    for prod,colorlabel in dict_color_mix.items():
        df.loc[(df['act']==prod), 'color']=colorlabel[0]
        df.loc[(df['act']==prod), 'label']=colorlabel[1]
```

```python
column="amount"

for df in list_df_mix:

    #calculate the rate of fluctuating renewable
    a=0
    b=0
    for act in fluctuating_renew:
        a=a+df[df["act"]==act]["amount"].values.tolist()[0]
    for act in direct_elec_prod_act_names:
        if act in df['act'].tolist():
            b=b+df[df["act"]==act]["amount"].values.tolist()[0]
    
    #print only production activities
    df=df[df["act"]!="market for electricity, high voltage, FE2050"]
    df=df[df["act"]!="market for electricity production, direct production, high voltage, FE2050"]
    for act_name in storage_act_names:
        df=df[df["act"]!=act_name]

    fig, ax = plt.subplots()
    ax.pie(
        df[column],
        labels=df['label'],#autopct='%1.1f%%',
        colors=df["color"],
        radius=0.9,
        labeldistance=None,
        startangle=90,
    )
    plt.title(df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]) + ", ""{:.0f}".format(a/b*100) + "% of PV+Wind")
    
    # Add legend without redundant labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=(0.5, 1.3), loc='center')
    plt.savefig('image-production mix.png')
```

```python

```

### Storage mix : Pie Chart

```python
list_df_to_plot_storage_mix=[]

for df in list_df_mix:
    df=df[df["act"]!="market for electricity, high voltage, FE2050"]
    df=df[df["act"]!="market for electricity production, direct production, high voltage, FE2050"]
    df=df[df["act"]!="market group for electricity, high voltage"]
    for act_name in direct_elec_prod_act_names :
        df=df[df["act"]!=act_name]
    list_df_to_plot_storage_mix.append(df)
    
```

```python
column="amount"

for df in list_df_to_plot_storage_mix:
#for df in [list_df_to_plot_storage_mix[0]]: #if I want to plot only one graph
    fig, ax = plt.subplots()
    ax.pie(
        df[column],
        labels=df['label'],#autopct='%1.1f%%',
        colors=df["color"],
        radius=0.9,
        labeldistance=None,
        startangle=90,
    )
    plt.title(df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))
    
    # Add legend without redundant labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=(0.5, 1.3), loc='center')
    plt.savefig('image-storage mix.png')
```

### Storage mix: Bar chart

```python
plot_bar_graph_french_scenarios(list_df_to_plot=list_df_to_plot_storage_mix, column='amount', title='Storage technology mix, per kWh of electricity consumed', starting_row=0,figsize=(8, 12))
```

## Impact Consumption & production mix : Bar graph

Plot production and consumption mix

```python
title='Impact per kWh'
label_consumption='1 kWh, from consumption mix'
label_prod='1 kWh, from direct production mix'
```

```python
#Add production mix on the graph (not only consumption)
add_prod="yes"
#Add percentage comparision prod vs consumption mix on the graph
add_percentage="yes"
```

```python
act_consumption='market for electricity, high voltage, FE2050'
act_prod='market for electricity, from direct French production, FE2050'
column='impact/kWh (absolute)'

a=0
label_bar_number=[]
label_bar=[]

fig,ax = plt.subplots()

for df in list_df_to_plot:
     
    a=a+0.2

#consumption mix 
    #Identify row consumption mix 
    index_consumption=df.loc[df['act']==act_consumption].index[0]
    #plot consumption mix (bar)
    ax.bar(a,df[column].iloc[index_consumption],width=0.1,color=df['color'].iloc[index_consumption], label=label_consumption)
    #plot production mix (point)
    #add labels

#Production mix
    if add_prod=="yes":
        #plot production mix (point)
        ax.plot(a,
                df.loc[df['act']==act_prod,column].values,
                color='darkorange',
                label=label_prod,
                marker = 'o'
               )    
        if add_percentage=="yes":
            #relative difference production mix >> consumption mix 
            diff=(df[column].iloc[index_consumption]-df[column].iloc[1])/df[column].iloc[1]*100     
            #annotate axe with relative difference 
            ax.annotate(
                text = f'{round(df[column].iloc[index_consumption],1)} | +{round(diff)}%',
                #text = f'{round(df[column].iloc[index_consumption],1)}',
                xy=(a, df[column].iloc[index_consumption] + 0.1),
                ha='center',
            )
        else:
            #annotate axe only with consumption mix         
            ax.annotate(
                text = f'{round(df[column].iloc[index_consumption],1)}',
                xy=(a, df[column].iloc[index_consumption] + 0.1),
                ha='center',
            )

    else:
        #annotate axe only with consumption mix         
        ax.annotate(
            text = f'{round(df[column].iloc[index_consumption],1)}',
            xy=(a, df[column].iloc[index_consumption] + 0.1),
            ha='center',
        )

    #For axis x labelling
    #Bar number
    label_bar_number.append(a)
    #list of bar label
    label_bar.append(df['model'].iloc[index_consumption]+', '+ df['SSP'].iloc[index_consumption]+'-'+ df['RCP'].iloc[index_consumption] +', '+ df['FR scenario'].iloc[index_consumption]+','+ str(df['year'].iloc[index_consumption]))


#Add information on the graph
plt.xlabel('  ')  
plt.ylabel(impact_cat[1]+ ', '+  list_df_ca_aggreg[0]['unit'].iloc[index_consumption])  
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

## Impact: Aggregated contribution analysis

```python
#Fonction to plot aggregated contribution
def plot_bar_graph_contrib(list_df_to_plot, column, rows=[1,2,3], add_number_percentage="number", add_prod_mix='no'):
    """Plot contribution"""    
    a=0
    label_bar_number=[]
    label_bar=[]
    fig,ax = plt.subplots() #
    
    for df in list_df_to_plot:
        #bar graph number
        a=a+0.5
        #list of bar number
        label_bar_number.append(a)
        #list of bar label
        label_bar.append(df['model'].iloc[0]+', '+ df['SSP'].iloc[0]+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))
        #Plot contributions
        base=0
        for row in rows:
            ax.bar(a, df[column].iloc[row], width=0.3, bottom=base, color=df['color'].iloc[row], label=df['label'].iloc[row],hatch=df['hatch'].iloc[row], edgecolor="grey")
            base=base+df[column].iloc[row]

        if add_number_percentage=="percentage":

            #plot storage mix (point)
            #ax.plot(a, df.loc[df['act']=='market for electricity, from storage, FE2050','impact/kWh (absolute)'].values, color='magenta', label='1 kWh - from storage', marker = 'o')    
        
            
            #relative difference production mix >> consumption mix
            col='impact/kWh (absolute)'
            diff=(df[col].iloc[0]-df[col].iloc[1])/df[col].iloc[1]*100 
    
            #add labels
            ax.annotate(
                text = f'{round(df[column].iloc[0],1)} | +{round(diff)}%',
                #text = f'{round(df[column].iloc[0],1)} | + {round(df[col].iloc[1],1)}| +{round(diff)}%',
                xy=(a, df[column].iloc[0] + 0.1),
                ha='center',
                fontsize=10,
                weight="bold",
            )

        if add_number_percentage=="number": 
                       #add labels
            ax.annotate(
                text = f'{round(df[column].iloc[0],1)}',
                xy=(a, df[column].iloc[0] + 0.1),
                ha='center',
                fontsize=18,
                weight="bold",
            )
        if add_prod_mix=='yes':
            #plot production mix (point)
            ax.plot(a, df.loc[df['act']=='market for electricity, from direct French production, FE2050','impact/kWh (absolute)'].values, color='darkorange', label='1 kWh - from direct production', marker ="D",markersize=10)    


    
    #Add information on the graph
    plt.xlabel(' ')  
    plt.ylabel(list_df_to_plot[0]['unit'].iloc[0]+ '/kWh')  
    plt.title(list_df_to_plot[0]['impact'].iloc[0])
    plt.xticks(label_bar_number,label_bar)  
    plt.xticks(rotation=45, ha='right')
    # Add legend without redundant labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=(0.8, 1.5), loc='best')
    #plt.tight_layout()
    #plt.show()    
    plt.savefig('image2-contrib to impact.png')
```

### without electricity from storage disaggregated

```python
list_df_to_plot=list_df_ca_aggreg

if change_plot_order=="yes": 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg[order])
```

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot, rows=[1,2,3], column='contribution to impact', add_prod_mix='yes',add_number_percentage="percentage") #title, figsize
```

### with electricity from storage disaggregated into 2

```python
list_df_ca_aggreg_bis[0]
```

```python
list_df_to_plot=list_df_ca_aggreg_bis
```

```python
if change_plot_order=="yes": 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg_bis[order])
    else:
        list_df_to_plot=list_df_ca_aggreg_bis
```

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot,
                       rows=[1,2,3,4,5],
                       column='contribution to impact',
                       add_number_percentage="percentage",
                       add_prod_mix='yes',
                       #figsize=(8, 6)
                      ) #title, figsize
```

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot,
                       rows=[1,2,4,3,5],
                       column='contribution to impact',
                       add_number_percentage="percentage",
                       add_prod_mix='yes',
                       #figsize=(8, 6)
                      ) #title, figsize
```

```python
list_df_ca_aggreg_bis2=[]
for df in list_df_ca_aggreg_bis:
    df2=df.copy()
    df2.loc[df['act']=='market for electricity, from direct French production, FE2050','difference with production mix']=df.loc[df['act']=='market for electricity, from direct French production, FE2050','impact/kWh (absolute)'].values.tolist()[0]
    df2.loc[df['act']=='market for electricity, from direct French production, FE2050','color']='grey'
    df2.loc[df['act']=='market for electricity, from direct French production, FE2050','label']='1 kWh   from direct production'
    df2.loc[df['act']=='market for electricity, from storage, FE2050','difference with production mix']=df.loc[df['act']=='market for electricity, from storage, FE2050','contribution to impact'].values.tolist()[0]
    df2.loc[df['act']=='market for electricity, from import, FE2050','difference with production mix']=df.loc[df['act']=='market for electricity, from import, FE2050','contribution to impact'].values.tolist()[0]
    list_df_ca_aggreg_bis2.append(df2)
```

```python
list_df_to_plot=list_df_ca_aggreg_bis2
```

```python
if change_plot_order=="yes": 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg_bis2[order])
    else:
        list_df_to_plot=list_df_ca_aggreg_bis2
```

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot,
                       rows=[1,3,5],
                       column='difference with production mix',
                       add_number_percentage="yes",
                       add_prod_mix='yes',
                       #figsize=(8, 6)
                      ) #title, figsize
```

### with storage infra and losses disagregated

```python
list_df_to_plot=list_df_ca_aggreg_ter
```

```python
if change_plot_order=="yes": 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg_ter[order])
```

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot,
                       rows=[5,2,3],
                       column='contribution to difference',
                       add_number_percentage="NO",
                       add_prod_mix='no',
                       #figsize=(8, 6)
                      ) #title, figsize
```

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot,
                       rows=[5,2,3],
                       column='contribution to difference %',
                       add_number_percentage="NO",
                       add_prod_mix='no',
                       #figsize=(8, 6)
                      ) #title, figsize
```

## Impact : Dissagregated storage mix

```python
list_df_storage_to_print[2]
```

```python
plot_bar_graph_french_scenarios(list_df_to_plot=list_df_storage_to_print, column='impact', title='title', starting_row=3, add_percentage='no', figsize=(8, 12),color_percentage='black')
```

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_storage_to_print, rows=[1,2,3,4],add_number_percentage="number",column='impact') #title, figsize
```

<!-- #region editable=true slideshow={"slide_type": ""} -->
## Impacts: Detailed contribution analysis
<!-- #endregion -->

```python
elec_act_name="market for electricity, high voltage, FE2050"
elec_act_unit='kilowatt hour'
impact_cat=climate
selected_db_list=[selected_db_list[0]] #premise_db_list
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

```python
list_df_ca[0]
```

#### WARNING : if the biosphere flows are modified, we have to modify this section

```python
ozone=agb.findActivity(db_name=biosphere_db_name,name="Ozone",categories=('air',))
no2=agb.findActivity(db_name=biosphere_db_name,name="Dinitrogen monoxide",categories=('air',))
```

```python
df=list_df_ca[0]
```

```python
grid_direct_emissions_no2=agb.newActivity(
    USER_DB_NAME,
    "NO2 direct emissions, high voltage grid, FE2050",
    unit="kWh",
    exchanges={
                    no2:df[df["act"]=="Dinitrogen monoxide('air',)"]["amount"].values.tolist()[0]
        }
    )

lca = grid_direct_emissions_no2.lca(method=impact_cat, amount=1)
no2_score = lca.score

unit_impact= bw2data.Method(impact_cat).metadata["unit"]
if unit_impact == "kg CO2-Eq":
    no2_score =1000*no2_score
```

```python
grid_direct_emissions_ozone=agb.newActivity(
    USER_DB_NAME,
    "NO2 direct emissions, high voltage grid, FE2050",
    unit="kWh",
    exchanges={
                    ozone:df[df["act"]=="Ozone('air',)"]["amount"].values.tolist()[0]
        }
    )

lca = grid_direct_emissions_ozone.lca(method=impact_cat, amount=1)
ozone_score = lca.score

unit_impact= bw2data.Method(impact_cat).metadata["unit"]
if unit_impact == "kg CO2-Eq":
    ozone_score =1000*ozone_score
```

```python
for df in list_df_ca:
   df.iloc[df.index[df["act"]=="Dinitrogen monoxide('air',)"].tolist()[0],df.columns.get_loc("impact")]=no2_score
   df.iloc[df.index[df["act"]=="Ozone('air',)"].tolist()[0],df.columns.get_loc("impact")]=ozone_score
```

```python
for df in list_df_ca:
        for prod,colorlabel in dict_color.items():
            df.loc[(df['act']==prod), 'color']=colorlabel[0]
            df.loc[(df['act']==prod), 'label']=colorlabel[1]
list_df_ca[0]    
```

```python
for n in range(len(selected_db_list)):
    if (list_df_ca[n]['impact'].sum()-list_df_ca_aggreg[n]['contribution to impact'].iloc[0])>10-5:
        print("error database number", n)
```

```python
#Fonction to plot aggregated contribution
def plot_bar_graph_disagreg_contrib(list_df_to_plot, column, figsize=(10, 15)):
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
    plt.ylabel(list_df_to_plot[0]['unit impact'].iloc[0]+ '/kWh')  
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
    list_df_ca, column='impact') #
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

## old Detailed contribution analysis with grid reallocation

```python
selected_db_list_to_plot=[selected_db_list[0]]
selected_db_list_to_plot
```

```python
elec_act_name="market for electricity, high voltage, FE2050"
elec_act_unit='kilowatt hour'
impact_cat=climate
```

```python
list_df_ca=[]

#For each db in the selected list
for db in selected_db_list_to_plot:
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
list_df_ca=[]

#For each db in the selected list
for db in selected_db_list_to_plot:
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
        'absolute impact 1 kWh',
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

## OLD : Consumption / Production / Import / storage mix comparison

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
xlsx_file_name="export-elec prod2.xlsx"

list_df_to_export=[
    ["elec 1 kWh", df],
    #["contrib an. aggreg"] + list_df_ca_aggreg,
    #["contrib an. detail"] + list_df_ca,
]

export_data_to_excel(list_df_to_export,xlsx_file_name)
```

```python
xlsx_file_name="export-full-251110.xlsx"

list_df_to_export=[
    ["contrib an. aggreg"] + list_df_ca_aggreg,
    #["storage"]+ list_df_storage #, df_elec_2, df_elec_3, df_elec_4, df_elec_5, df_elec_6],
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
