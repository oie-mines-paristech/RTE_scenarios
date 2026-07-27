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
#import matplotlib as matplotlib
#import matplotlib.pyplot as plt
import os as os
#import lca_algebraic as agb

#import custom functions
from utils import save_xls, import_xls_list_df, create_empty_act, change_input_storage_mix, storage_input_mix_name
from activities_type_label import *

#import climate change impact method that is updated by premise
from premise_gwp import add_premise_gwp
```

# Intitialisation: `🔧` Project name and ecoinvent names

```python
eco_version="3.12"
```

```python
#Name ecoinvent databases
if eco_version=="3.10": 
    ecoinvent_db_name='ecoinvent-3.10.1-cutoff'
    ecoinvent_db_name="ecoinvent-3.10.1-biosphere"
    NAME_BW_PROJECT="premise_France_RTE_310" 

if eco_version=="3.11": 
    ecoinvent_db_name='ecoinvent-3.11-cutoff'
    ecoinvent_bio_db_name="ecoinvent-3.11-biosphere"
    NAME_BW_PROJECT="premise_France_RTE_311"
    NAME_BW_PROJECT="ecoinvent_3_11"

if eco_version=="3.12": 
    ecoinvent_db_name='ecoinvent-3.12-cutoff'
    ecoinvent_bio_db_name="ecoinvent-3.12-biosphere"
    NAME_BW_PROJECT="premise_France_RTE_312"
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
add_premise_gwp()
```

```python
EF = 'EF v3.1'
climate = (EF, 'climate change', 'global warming potential (GWP100)')
climate_premise=('IPCC 2021', 'climate change', 'GWP 100a, incl. H and bio CO2')
acidification = (EF,'acidification','accumulated exceedance (AE)')
land=(EF, 'land use', 'soil quality index')
ionising_rad=(EF,'ionising radiation: human health','human exposure efficiency relative to u235')
metals_minerals=(EF,  'material resources: metals/minerals',  'abiotic depletion potential (ADP): elements (ultimate reserves)')
non_renew_energy=(EF,'energy resources: non-renewable','abiotic depletion potential (ADP): fossil fuels')

impacts=[climate, climate_premise, acidification, land, ionising_rad,metals_minerals,non_renew_energy]

for impact_cat in impacts:
    print(impact_cat, bw2data.Method(impact_cat).metadata['unit'])
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
#Options for model / SSP / IAM / FR scenarios
model_list=['image','tiam-ucl','remind','remind-eu',"message"]
year_list=['2020','2050']
SSP_list=['SSP1','SSP2','SSP3','SSP4','SSP5']
RCP_list=['Base','RCP19','RCP26','RCP45','Npi','NDC','-M_','-L','-H','PkBudg1000','NDC','NPi','ML','VLHO','rollBack','PkBudg650']
FR_scenario_list=['M0','M1','M23','N1','N2','N03']
```

```python
#generate a list of names of generated databases by premise
premise_db_name_list=[]
for db_name in bw2data.databases.keys():
    if "ei_cutoff" in db_name:
        premise_db_name_list.append(db_name)
```

```python editable=true slideshow={"slide_type": ""}
#generate a list of generated databases by premise
premise_db_list=[]
for db_name in premise_db_name_list:
    premise_db_list.append(bw2data.Database(db_name))
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
df_premise_db_list=df
df_premise_db_list
```

## Select databases with filters

```python editable=true slideshow={"slide_type": ""}
#If you want to run the tests on all premise databases
selected_db_list=premise_db_list
```

```python
#To generate a list of databases based on filters on the year / SSP / RCP/ FR_Scenario
#Example
selected_db_list=[db for db in premise_db_list if 'M0' in db.name and 'Base' not in db.name and 'RCP26' not in db.name]# and 'update' not in db.name]+[db for db in premise_db_list if db.name=='ei_cutoff_3.9_tiam-ucl_SSP2-RCP45_2050_Reference - N1 2025-05-15']
selected_db_list_1=[db for db in premise_db_list if 'M0' in db.name]
selected_db_list_2=[db for db in premise_db_list if 'remind' in db.name and db.SSP=='SSP2' and db.RCP in ['PkBudg1000','NDC','NPi'] and 'M1' not in db.name and 'M23' not in db.name and 'N2' not in db.name]
selected_db_list_3=[db for db in premise_db_list if 'remind' in db.name and db.SSP=='SSP2' and db.RCP=='NDC']
selected_db_list_4=selected_db_list_3+[db for db in premise_db_list if db.year==2020]

#selected_db_list=[selected_db_list[-3]]
selected_db_list_1
```

# `🔧` Choose configuration for analysis

```python
#selected_impacts=[impacts[0]]+[impacts[3]]
selected_impacts=impacts
for impact_cat in selected_impacts:
    print(impact_cat[1])
```

```python
selected_db_list=selected_db_list_1
#[selected_db_list_4[0]]+[selected_db_list_4[5]]
selected_db_list
```

```python
mainfolder='M0/'
```

## `🔧` optional features : curtailed energy

```python
curtailment_included="yes"
```

```python
if curtailment_included=="yes":
    df_curtailment=import_xls_list_df('curtailed_electricity.xlsx')[0]
```

# Database modification (run only once)

```python
new_input_name="market for electricity production, direct production, high voltage, FE2050"
create_empty_act(selected_db_list)
change_input_storage_mix(selected_db_list,new_input_name)
```

# Aggregated contribution analysis
Contribution analysis between :
* electricity from direct production
* electricity from storage
* electricity from imports
* optionnaly : electricity from curtailement

```python
ca_aggreg=[]
ca_aggreg_bis=[]

for impact_cat in selected_impacts:

# A. Disaggregate electricity into 4 (dorect prod, storage, import, curtailment)

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

        #Absolute impact/kWh
        df["impact/kWh (absolute)"]=df["contribution to impact"]/df["amount (kWh)"]
        
        #Add curtailment
        if curtailment_included=="yes":
            act=db.search("market for electricity production, direct production, high voltage, FE2050")[0]
            amount=df_curtailment[df_curtailment['FR_scenario']==db.FR_scenario][db.year].squeeze()
            lca = act.lca(method=impact_cat, amount=1)
            direct_elec_score=lca.score
            curtailment_score=direct_elec_score*amount
            if unit_impact == "kg CO2-Eq":
                direct_elec_score=1000*direct_elec_score
                curtailment_score=1000*curtailment_score
            df.loc[len(df.index)] = [db.name,db.model, db.SSP,db.RCP,db.FR_scenario,db.year,db.warning,impact_cat[1],'curtailment',amount,curtailment_score,unit,direct_elec_score]
            #add curtailment score to market score
            market_score=df.loc[df['act']=='market for electricity, high voltage, FE2050','contribution to impact']    
            df.loc[df['act']=='market for electricity, high voltage, FE2050','contribution to impact']=market_score+curtailment_score
            df.loc[df['act']=='market for electricity, high voltage, FE2050','impact/kWh (absolute)']=market_score+curtailment_score
            
        
        #Calculation for mix
        total = df['contribution to impact'].iloc[1:].sum()       
    
        #Add columns to calculate the contribution to impacts (percentage)
        df['percentage contribution']=df['contribution to impact']/total*100

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

    list_df_ca_aggreg_bis=[]

# B. Disaggregate electricity from storage and imports into 2
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
        df2['unit']=df2.loc[0,'unit']
        
        #Add df2 to the list
        list_df_ca_aggreg_bis.append(df2)

    #Save the list for each impact category   
    ca_aggreg.append(list_df_ca_aggreg)
    ca_aggreg_bis.append(list_df_ca_aggreg_bis)
    
    #Save a file / a list for each impact category
    newpath=mainfolder+impact_cat[1].replace(":","").replace("/"," ")
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    save_xls(newpath+'/'+'list_df_ca_aggreg.xlsx',list_df_ca_aggreg)
    save_xls(newpath+'/'+'list_df_ca_aggreg_bis.xlsx',list_df_ca_aggreg_bis)
        
```

```python
len(list_df_ca_aggreg)
```

```python
ca_aggreg[0][0]
```

```python
ca_aggreg_bis[0][0]
```

# Dissagregate contribution storage btw losses and infrastructure

```python
#grid_losses
grid_losses=0.03109
grid_losses_factor=1/(1-grid_losses)
grid_losses_factor
```

```python
ca_storage=[]

for impact_cat in selected_impacts:  
    list_df_storage_efficiency= []
    list_df_storage=[]
    unit_impact = bw2data.Method(impact_cat).metadata["unit"]
    unit=unit_impact
    
    zero=0.0
    columns = ['db_name','model','SSP','RCP','FR scenario','year','warning','act',
               'amount in elec market (kWh)','% efficiency','storage losses (kWh)',
               'impact 1kWh prod elec from storage','impact storage losses','impact storage infra',
               'impact 1 kWh elec consumption market','impact 1 kWh elec market from prod','impact 1 kWh pure production','impact 1 kWh elec market from storage','unit']
    
    for db in selected_db_list:

#A. Storage efficiencies
        
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
        list_df_storage_efficiency.append(df_storage_efficiency)

#B. Impact storage
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
        act_pure_prod_elec= db.search('market for electricity production, direct production, high voltage, FE2050')[0]
        lca = act_pure_prod_elec.lca(method=impact_cat, amount=1)
        score_prod_pure=lca.score
    
        #Consumption mix from storage
        act_market_stor_elec= db.search('market for electricity, from storage, FE2050')[0]
        lca = act_market_stor_elec.lca(method=impact_cat, amount=1)
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
    
    
        #transversal calculations
        for diki in list_dict_storage:
            act_storage_name=diki['act_storage_name']
            df.loc[df['act'] == act_storage_name, '% efficiency']=df_storage_efficiency.loc[df_storage_efficiency['act'] == act_storage_name, '% efficiency'].values
            df.loc[df['act'] == act_storage_name, 'storage losses (kWh)']=df_storage_efficiency.loc[df_storage_efficiency['act'] == act_storage_name, 'storage losses (kWh)'].values
        df['impact storage losses']=df['storage losses (kWh)']*df['impact 1 kWh pure production']
        df['impact storage infra']=df['impact 1kWh prod elec from storage']-(1+df['storage losses (kWh)'])*df['impact 1 kWh pure production']
    
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
            #For each db in the selected list add the dataframe to the list of dataframes
        
        list_df_storage.append(df)        
    #save    
    ca_storage.append(list_df_storage)
    newpath=mainfolder+impact_cat[1].replace(":","").replace("/"," ")
    save_xls(newpath+'/'+'impact_storage.xlsx',list_df_storage)
    


```

```python
list_df_storage_efficiency[0]
```

```python
ca_storage[0][0]
```

## Disaggregation of storage

```python
len(ca_aggreg_bis)
```

```python
ca_aggreg_ter=[]
n_impact=0

#For each impact cat
for list_df_ca_aggreg_bis in ca_aggreg_bis:
    list_df_storage=ca_storage[n_impact]
    n_impact=n_impact+1

    n_scenario=0
    list_df_ca_aggreg_ter=[]

    #For each scenario
    for df in list_df_ca_aggreg_bis:
        #Extract storage related data from df and df_sto
        df_sto=list_df_storage[n_scenario]
        impact_mix_prod=df_sto.loc[0,'impact 1 kWh elec market from prod']
        losses_sto=df_sto.loc[0,'impact storage losses in consumption mix']
        infra_sto= df_sto.loc[0,'impact storage infra in consumption mix']
        amount_sto=df.loc[(df['act']=="market for electricity, from storage, FE2050"),'amount (kWh)'].values.tolist()[0]
        n_scenario=n_scenario+1
        #losses_sto*amount_sto
        #infra_sto*amount_sto
    
        #insert empty lines
        df2=df.copy()
        for newrow in [5,6]:
            df2 = pd.DataFrame(np.insert(df2.values, newrow, values =len(df.columns)*[np.NaN],axis=0))
        df2.columns = df.columns
    
        #Label and act of new lines
        df2.loc[5,'label']='storage losses'
        df2.loc[5,'act']='storage losses' 
        df2.loc[5,'color']='royalblue'
    
        df2.loc[6,'label']='storage infrastructure'
        df2.loc[6,'act']='storage infrastructure'
        df2.loc[6,'color']='royalblue'
    
        
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
            print('warning total does not equal consumption mix for')
            print(df2['impact'].tolist()[0])
            print(df2['FR scenario'].tolist()[0])
            print(test)
    
        #recalculate percentage contribution
        df2['percentage contribution']=df2['contribution to impact']/df2.loc[0,'contribution to impact']
    
        #Put unit on all lines
        df2['unit']=df2.loc[0,'unit']
    
        list_df_ca_aggreg_ter.append(df2)
    
    ca_aggreg_ter.append(list_df_ca_aggreg_ter)
    impact_name=list_df_ca_aggreg_bis[0]['impact'].tolist()[0]
    newpath=mainfolder+impact_name.replace(":","").replace("/"," ")
    save_xls(newpath+'/'+'list_df_ca_aggregg_ter.xlsx',list_df_ca_aggreg_ter)
```

```python
ca_aggreg_ter[0][0]
```

# EXTRACT RTE data

```python
RTE_folder='RTE data/'
if not os.path.exists(RTE_folder):
        os.makedirs(RTE_folder)
```

```python
selected_db_list_to_plot=[db for db in premise_db_list if 'remind' in db.name and db.SSP=='SSP2' and db.RCP=='NDC']+[db for db in premise_db_list if '2020' in db.name]
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

save_xls(RTE_folder+'list_df_mix.xlsx',list_df_mix)
```

```python
column="amount"
list_df_prod_mix=[]

for df in list_df_mix:

    #calculate the rate of fluctuating renewable
    a=0
    b=0
    
    #print only production activities
    df=df[df["act"]!="market for electricity, high voltage, FE2050"]
    df=df[df["act"]!="market group for electricity, high voltage"]
    for act_name in storage_act_names:
        df=df[df["act"]!=act_name]
    #
    df["percentage production technology"]=df["amount"]/df["amount"].sum()

    for act in fluctuating_renew:
        a=a+df[df["act"]==act]["amount"].values.tolist()[0]
        percentage_fluctuating_renew=a/df["amount"].sum()
    print(percentage_fluctuating_renew)
    list_df_prod_mix.append(df)
    
save_xls(RTE_folder+'list_df_prod_mix.xlsx',list_df_prod_mix)
```

```python
list_df_to_plot_storage_mix=[]

for df in list_df_mix:
    df=df[df["act"]!="market for electricity, high voltage, FE2050"]
    df=df[df["act"]!="market for electricity production, direct production, high voltage, FE2050"]
    df=df[df["act"]!="market group for electricity, high voltage"]
    for act_name in direct_elec_prod_act_names :
        df=df[df["act"]!=act_name]
    df['percentage storage technology']=df['amount']/df['amount'].sum()
    list_df_to_plot_storage_mix.append(df)

save_xls(RTE_folder+'list_df_to_plot_storage_mix.xlsx',list_df_to_plot_storage_mix)
```

# Graphs

```python
for impact_cat in impacts:
    print(mainfolder+impact_cat[1].replace(":","").replace("/"," "))
```

```python
newpaths=[
    'remind_SSP2-NDC/climate change',
    'remind_SSP2-NDC/acidification',
    'remind_SSP2-NDC/land use',
    'remind_SSP2-NDC/ionising radiation human health',
    'remind_SSP2-NDC/material resources metals minerals',
    'remind_SSP2-NDC/energy resources non-renewable',
    ]
```

```python
mainfolder='remind_SSP2-NDC/'
```

```python
newpath=mainfolder+'climate change'
#newpath=mainfolder+'acidification'
#newpath=mainfolder+'land use'
#newpath=mainfolder+'ionising radiation human health'
#newpath=mainfolder+'material resources metals minerals'
#newpath=mainfolder+'energy resources non-renewable'
```

```python
list_df_ca_aggreg=import_xls_list_df(newpath+'/'+'list_df_ca_aggreg.xlsx')
list_df_ca_aggreg_bis=import_xls_list_df(newpath+'/'+'list_df_ca_aggreg_bis.xlsx')
list_df_ca_aggreg_ter=import_xls_list_df(newpath+'/'+'list_df_ca_aggregg_ter.xlsx')
list_df_mix=import_xls_list_df(RTE_folder+'list_df_mix.xlsx')
list_df_prod_mix=import_xls_list_df(RTE_folder+'list_df_prod_mix.xlsx')
list_df_to_plot_storage_mix=import_xls_list_df(RTE_folder+'list_df_to_plot_storage_mix.xlsx')
list_df_to_plot_storage_mix_empty=import_xls_list_df(RTE_folder+'list_df_to_plot_storage_mix_empty.xlsx')
```

```python
for df in list_df_prod_mix:
    df["percentage production technology 100"]=df["percentage production technology"]*100
for df in list_df_ca_aggreg:
    df['amount (kWh) 100']=100*df['amount (kWh)']
for df in list_df_to_plot_storage_mix:
    df['amount 100']=100*df['amount']
    df['percentage storage technology 100']=100* df['percentage storage technology']
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
    df['contribution to difference % 100']=100*df['contribution to difference %']
    df.loc[(df['label']=="electricity from storage replaced by production mix"),'hatch']="///"
    df.loc[(df['label']=="electricity from imports replaced by production mix"),'hatch']="///"
    df.loc[df['label'] == 'storage losses','hatch']='---'
    df.loc[df['label'] == 'storage infrastructure','hatch']='||'
    df.loc[(df['label']=="storage losses and infrastructure"),'hatch']='++'
    df.loc[(df['label']=='differential impacts due to imports'),'hatch']='++'
    df['year']=df['year'].astype('Int64')
```

```python
#Recap : list of databases covered by list_df_ca_aggreg
list_df = pd.DataFrame(columns=list_df_ca_aggreg[0].columns)
for df in list_df_ca_aggreg_ter:
    list_df=pd.concat([list_df,df.head(1)],ignore_index=True)
list_df
```

## `🔧` Optional : choose specific change databases to compare and order

```python
#Choose what you want to plot in which order on the graphs
change_plot_order=1
plot_order=[6,0,2,5]
plot_order=[6,0,1,2,3,4,5]
```

# Origin of electricity


## Definition of function

```python
#Fonction to plot aggregated amount
def plot_bar_graph_french_scenarios(
    title,
    
    list_df_to_plot,
    column,
    fig_name='test-fig.png',

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
                    
                ax.bar(a, value, bottom=base, color=df['color'].iloc[row], label=df['label'].iloc[row], width=width)
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
    plt.savefig(fig_name)
    plt.show()    
```

```python
#Fonction to plot aggregated amount
def plot_bar_graph_french_scenarios_double(
    title,
    list_df_to_plot,
    list_df_to_plot2,
    column,
    column2,
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
    
    if addlinev==1:
        plt.axvline(0.4+ecart*1.25,color='red', linewidth=1)
        plt.axvline(0.4+ecart*2.25, color='black', linestyle='dashed', linewidth=1)
        plt.axvline(0.4+ecart*3.25, color='black', linestyle='dashed', linewidth=1)
    # Add legend without redundant labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    if addlegend==1:
        plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_label*0.8))

    plt.tight_layout()
    plt.savefig('image-origin of electricity.png')
    plt.show() 
```

## Origin of electricity


## Aggregated origin : Bar graph

```python
list_df_to_plot=list_df_ca_aggreg
if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg[order])
```

```python
plot_bar_graph_french_scenarios(
    list_df_to_plot=list_df_to_plot, 
    column='amount (kWh) 100', 
    starting_row=1,
    add_percentage=1,
    percentage_column='amount (kWh)',
    color_percentage='darkgrey',
    
    #title='Electricity origin\nper kWh consumed\n in 2020 and 2050', 
    title='Consumption mix',
    size_title=10,
    ylabel='%',
    size_label=8,
    size_percentage=8,
    addlineh=1,
    addlinev=1,
    pos_legend=(0.4, -0.3),
    figsize=(2.2, 3),
    addlegend=0,
    change_topbottom=1,
)

    
```

```python
plot_bar_graph_french_scenarios(
    list_df_to_plot=list_df_to_plot, 
    column='amount (kWh) 100', 
    starting_row=2,
    add_percentage=1,
    percentage_column='amount (kWh)',
    color_percentage='darkgrey',
    
    #title='Electricity origin\nper kWh consumed\n in 2020 and 2050', 
    title='Consumption mix',
    size_title=10,
    ylabel='%',
    size_label=8,
    size_percentage=8,
    #addlineh=1,
    addlinev=1,
    pos_legend=(0.4, -0.3),
    figsize=(2.2, 3),
    addlegend=0
)

```

```python
plot_bar_graph_french_scenarios(
    list_df_to_plot=list_df_to_plot, 
    column='amount (kWh) 100', 
    starting_row=2,
    add_percentage=1,
    percentage_column='amount (kWh)',
    
    title='Origin of electricity \nper kWh consumed', 
    size_title=12,
    ylabel='kWh/kWh',
    size_label=10,
    size_percentage=11,
    color_percentage='darkgrey',
    pos_legend=(0.4, -0.3),
    figsize=(2.5, 5),

    addlinev=1,

)
```

## Production mix ; bar chart

```python
list_df_to_plot=list_df_prod_mix
if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_prod_mix[order])
```

```python
plot_bar_graph_french_scenarios(
    list_df_to_plot=list_df_to_plot, 
    column='percentage production technology 100', 
    starting_row=0,
    add_percentage=0,
    percentage_column='amount',
    title='Production technology mix',
    size_title=10,
    ylabel='%',
    size_label=8,
    size_percentage=8,
    pos_legend=(0.4, -0.3),
    figsize=(2.2, 3),
    addlegend=0,
    addlinev=1,
    addPVwind=1,
)
  
```

```python
   for df in list_df_to_plot:
        #plt.subplots(100+len(list_df_to_plot)+x)
        #bar graph number
        

        #list of bar label
        #if addPVwind==1:
            #calculate the rate of fluctuating renewable
            amount_PVwind=0
            amount_tot=0
            for act in fluctuating_renew:
                amount_PVwind=amount_PVwind+df[df["act"]==act]["amount"].values.tolist()[0]
            for act in direct_elec_prod_act_names:
                if act in df['act'].tolist():
                    amount_tot=amount_tot+df[df["act"]==act]["amount"].values.tolist()[0]
            PVwind_rate=amount_PVwind/b*100
```

```python
plot_bar_graph_french_scenarios(
    list_df_to_plot=list_df_to_plot, 
    column='percentage production technology 100', 
    starting_row=0,
    add_percentage=0,
    percentage_column='amount',
    title='Production mix',
    size_title=10,
    ylabel='',
    size_label=12,
    size_percentage=8,
    pos_legend=(0.4, -0.3),
    figsize=(4, 8),
    addlegend=1,
    addlinev=1,
)

```

## Storage mix: Bar chart

```python
list_df_to_plot=list_df_to_plot_storage_mix
if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_to_plot_storage_mix[order])
```

```python
plot_bar_graph_french_scenarios(
    list_df_to_plot=list_df_to_plot, 
    column='percentage storage technology 100', 
    starting_row=0,
    add_percentage=1,
    percentage_column='percentage storage technology',
    title='Storage mix',
    size_title=10,
    ylabel='%',
    size_label=8,
    size_percentage=8,
    pos_legend=(0.4, -0.3),
    figsize=(2.2, 3),
    addlegend=0,
    addlinev=1,
)

```

```python
plot_bar_graph_french_scenarios(
    list_df_to_plot=list_df_to_plot, 
    column='amount', 
    title='Origin of electricity per kWh consumed, for electricity from storage', 
    starting_row=0,
    figsize=(3, 6),
    add_percentage=1,
    percentage_column='percentage storage technology')
```

```python
list_df_to_plot=list_df_ca_aggreg
if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg[order])
```

```python
list_df_to_plot2=list_df_to_plot_storage_mix
if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot2= []
    for order in plot_order:
        list_df_to_plot2.append(list_df_to_plot_storage_mix[order])
```

```python
plot_bar_graph_french_scenarios_double(
    list_df_to_plot=list_df_to_plot, 
    column='amount (kWh) 100', 
    starting_row=2,
    ending_row=2+1,
    add_percentage=1,
    percentage_column='amount (kWh)',
    
    list_df_to_plot2=list_df_to_plot2, 
    column2='amount 100', 
    starting_row2=0,
    percentage_column2='percentage storage technology',
    
    title='Electricity released from storage in the consumption mix\nand storage technology mix', 
    size_title=10,
    ylabel='',
    size_label=8,
    size_percentage=8,
    addlinev=1,

    color_percentage='darkgrey',
    #color_percentage2

    pos_legend=(0.4, -0.3),
    figsize=(4.4, 3),
    addlegend=0
)

```

```python
list_df_to_plot2=list_df_to_plot_storage_mix_empty
if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot2= []
    for order in plot_order:
        list_df_to_plot2.append(list_df_to_plot_storage_mix_empty[order])
```

```python
plot_bar_graph_french_scenarios_double(
    list_df_to_plot=list_df_to_plot, 
    column='amount (kWh) 100', 
    starting_row=2,
    ending_row=2+1,
    add_percentage=1,
    percentage_column='amount (kWh)',
    
    list_df_to_plot2=list_df_to_plot2, 
    column2='amount 100', 
    starting_row2=0,
    percentage_column2='percentage storage technology',
    
    title='Electricity released from storage in the consumption mix\nand storage technology mix', 
    size_title=10,
    ylabel='',
    size_label=8,
    size_percentage=8,
    addlinev=1,

    color_percentage='darkgrey',
    #color_percentage2

    pos_legend=(0.4, -0.3),
    figsize=(4.4, 3),
    addlegend=0
)

```

# Impact Analysis : Contribution analysis


## Definition of function

```python
#Fonction to plot aggregated contribution
def plot_bar_graph_contrib(
    list_dict_to_plot,

    fig_title='test',
    fig_name='test-fig.png',

    add_number_percentage="number", #"number" or "percentage"
    add_prod_mix=0,
    add_conso_mix=0,
    add_percentage=0,
    percentage_column='contribution to difference %',
    addlineh=1,
    
    subplot_size=(3, 3),
    width=0.7,
    sharey=False,
    pos_legend=(0.5, -0.5),
    
    size_subplot_title=10,
    size_label=8,
    
):
    """Plot contribution"""    
    nb_subplot=len(list_dict_to_plot)

    #create fig
    #fig,ax = plt.subplots(figsize=subplot_size)
    fig, axs = plt.subplots(1,nb_subplot, figsize=(nb_subplot*subplot_size[0],subplot_size[1]),sharey=sharey)
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
            label_bar.append(df['model'].iloc[0]+', '+ df['SSP'].iloc[0]+'-'+ df['RCP'].iloc[0] +', '+ df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]))
            
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
                            printed_percentage= f'{sign} {round(percentage*100)}%'
                            position_percentage=base+df[column].iloc[row]*0.3
                            ax.text(
                                j,
                                position_percentage,
                                printed_percentage,
                                ha = 'center', color = color_percentage, size = size_label*1.4, weight = 'bold',
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

            if column=='contribution to impact': 
                if add_number_percentage=="number": 
                    add_text=f'{round(elec_conso_impact,1)}'
                elif add_number_percentage=="percentage":   
                    add_text=f'{round(elec_conso_impact,1)} | {sign} {round(diff)}%'
                else:
                    add_text=''            
            else:
                    add_text=''
            #Add consumption mix impact and difference in %
            ax.annotate(
                    text = add_text,
                    xy=(j, max(elec_conso_impact,elec_prod_impact)),
                    ha='center',
                    fontsize=size_label+1,
                    weight="bold",
                )

        
        #Add information on the graph
        # Add labels and title for each subplot
        ax.set_title(list_df_to_plot[0]['impact'].iloc[0], size=size_subplot_title)
        #ax.set_xlabel('C')
        if sharey==False:
            ax.set_ylabel(list_df_to_plot[0]['unit'].iloc[0]+ '/kWh')
        if sharey==True:
            if i==0:
                ax.set_ylabel(list_df_to_plot[0]['unit'].iloc[0]+ '/kWh')

        ax.set_xticks(label_bar_number,label_bar,rotation=45, ha='right')  
        #ax.set_xticks(rotation=45, ha='right')


    
    # Add legend without redundant labels
        if i in range(len(axs)): #[0,2]:
            #ax.legend(bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_label*0.9))
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(),bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_label*0.9))
            #ax.legend(bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_label*0.9))

    #handles, labels = plt.gca().get_legend_handles_labels()
    #by_label = dict(zip(labels, handles))
    #plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=pos_legend, loc='center', fontsize=int(size_label*0.8))
    
    fig.suptitle(fig_title)
    plt.tight_layout()
    plt.show()    
    fig.savefig(fig_name)
```

## Plot absolute and differential impacts

```python
#Choose what you want to plot in which order on the graphs
change_plot_order=1
plot_order=[0,2,5]
```

```python
list_df_to_plot=list_df_ca_aggreg_ter

if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg_ter[order])
```

### Absolute

```python
list_dict_to_plot=[]
```

```python
list_dict_to_plot=[]
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[1,2,7,10],
    "column":'contribution to impact'
    }
list_dict_to_plot.append(dict_to_plot)
```

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    #"rows":[9,5,6,10],
    "rows":[5,6,10],
    "column":'contribution to difference'
    }

list_dict_to_plot.append(dict_to_plot)


```

```python
plot_bar_graph_contrib(
    list_dict_to_plot=list_dict_to_plot,
    
    fig_title='',
    fig_name='test-fig.png',

    add_number_percentage="number",
    add_prod_mix=0,
    add_conso_mix=1,
    add_percentage=1,
    
    subplot_size=(5,15),
    #width=0.7,
    sharey=False,
    pos_legend=(0.5, -1),
    
    size_subplot_title=15,
    size_label=13,

) #title, figsize
```

```python

```

```python

```

## Explain the absolute and differential analysis


### without electricity from storage disaggregated

```python
#Choose what you want to plot in which order on the graphs
change_plot_order=1
plot_order=[0,2,5]
```

```python
list_df_to_plot=list_df_ca_aggreg_ter

if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg_ter[order])
```

```python
list_dict_to_plot=[]
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[1,2,7,10],
    "column":'contribution to impact'
    }
list_dict_to_plot.append(dict_to_plot)
```

### with electricity from storage disaggregated into 2

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[1,3,4,8,9,10],
    "column":'contribution to impact'
    }
list_dict_to_plot.append(dict_to_plot)
```

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[1,3,8,4,9,10],
    "column":'contribution to impact'
    }
list_dict_to_plot.append(dict_to_plot)
```

### with differential impacts

```python
list_df_ca_aggreg_ter2=[]
for df in list_df_ca_aggreg_ter:
    df2=df.copy()
    df2.loc[df['act']=='market for electricity, high voltage, FE2050','difference with production mix']=df.loc[df['act']=='market for electricity, high voltage, FE2050','impact/kWh (absolute)'].values.tolist()[0]
    df2.loc[df['act']=='market for electricity, from direct French production, FE2050','difference with production mix']=df.loc[df['act']=='market for electricity, from direct French production, FE2050','impact/kWh (absolute)'].values.tolist()[0]
    df2.loc[df['act']=='market for electricity, from direct French production, FE2050','color']='grey'
    df2.loc[df['act']=='market for electricity, from direct French production, FE2050','label']='1 kWh from direct production'
    for act in ['storage losses and infrastructure','differential impacts due to imports','curtailment']:
        df2.loc[df['act']==act,'difference with production mix']=df.loc[df['act']==act,'contribution to impact'].values.tolist()[0]
    list_df_ca_aggreg_ter2.append(df2)
```

```python
list_df_to_plot=[list_df_ca_aggreg_ter2]
```

```python
if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg_ter2[order])
else:
    list_df_to_plot=list_df_ca_aggreg_ter2
```

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[1,4,9,10],
    "column":'difference with production mix'
    }
list_dict_to_plot.append(dict_to_plot)
```

### with storage infra and losses disagregated

```python
list_df_to_plot=list_df_ca_aggreg_ter
```

```python
if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg_ter[order])
```

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[9,5,6,10],
    "column":'contribution to difference'
    }
```

### plot

```python
plot_bar_graph_contrib(
    list_dict_to_plot=list_dict_to_plot,
    
    fig_title='Absolute versus differential contribution analysis',
    fig_name='test-fig.png',

    add_number_percentage="percentage",
    add_prod_mix=1,
    add_conso_mix=1,
    
    subplot_size=(2, 3.5),
    #width=0.7,
    sharey=True,
    pos_legend=(0.5, -1),
    
    size_subplot_title=10,
    size_label=8,

) #title, figsize
```

```python
plot_bar_graph_contrib(
    list_dict_to_plot=[dict_to_plot],
    
    fig_title='Differential contribution analysis',
    fig_name='test-fig.png',

    add_number_percentage=0,
    add_prod_mix=1,
    add_conso_mix=1,
    add_percentage=1,
    
    subplot_size=(8, 20),
    #width=0.7,
    sharey=False,
    pos_legend=(0.5, -1),
    
    size_subplot_title=10,
    size_label=8,

) #title, figsize
```

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    #"rows":[9,5,6,10],
    "rows":[5,6,10],
    "column":'contribution to difference'
    }

list_dict_to_plot.append(dict_to_plot)

plot_bar_graph_contrib(
    list_dict_to_plot=[dict_to_plot],
    
    fig_title='',
    fig_name='test-fig.png',

    add_number_percentage=0,
    add_prod_mix=0,
    add_conso_mix=0,
    add_percentage=1,
    
    subplot_size=(8,20),
    #width=0.7,
    sharey=False,
    pos_legend=(0.5, -1),
    
    size_subplot_title=10,
    size_label=8,

) #title, figsize
```

## xxxxxxxxxxx


### without electricity from storage disaggregated

```python
#Choose what you want to plot in which order on the graphs
change_plot_order=1

plot_order=[10,0,1,2,3,11,7,8,4,9,5,6,12,13,14,15] #  M0+ all IAM
plot_order=[10,0,1,2,3,11] #M0 + remind
plot_order=[1,3,4,14,5,6] #M0 + SSP2
```

```python
list_df_to_plot=list_df_ca_aggreg_ter

if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg_ter[order])
```

```python
list_dict_to_plot=[]
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[1,2,7,10],
    "column":'contribution to impact'
    }
list_dict_to_plot.append(dict_to_plot)
```

### with storage infra and losses disagregated

```python
list_df_to_plot=list_df_ca_aggreg_ter
```

```python
if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg_ter[order])
```

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[9,5,6,10],
    "column":'contribution to difference'
    }
list_dict_to_plot.append(dict_to_plot)
```

```python
plot_bar_graph_contrib(
    list_dict_to_plot=list_dict_to_plot,
    
    fig_title='',
    fig_name='test-fig.png',

    add_number_percentage="percentage",
    add_prod_mix=1,
    add_conso_mix=1,
    add_percentage=1,
    
    subplot_size=(8, 10),
    #width=0.7,
    sharey=False,
    pos_legend=(0.5, -0.5),
    
    size_subplot_title=10,
    size_label=8,

) #title, figsize
```

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[9],
    "column":'contribution to difference'
    }
list_dict_to_plot.append(dict_to_plot)
```

```python
plot_bar_graph_contrib(
    list_dict_to_plot=[dict_to_plot],
    fig_title='',
    add_number_percentage="",#"percentage",
    add_prod_mix=0,
    add_conso_mix=0,
    subplot_size=(8, 10),

) #title, figsize
```

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[9],
    "column":'contribution to difference % 100'
    }
list_dict_to_plot.append(dict_to_plot)
```

```python
plot_bar_graph_contrib(
    list_dict_to_plot=[dict_to_plot],
    fig_title='',
    add_number_percentage="",#"percentage",
    add_prod_mix=0,
    add_conso_mix=0,
    subplot_size=(8, 10),

) #title, figsize
```

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[5,6,10],
    "column":'contribution to difference'
    }
list_dict_to_plot.append(dict_to_plot)
```

```python
plot_bar_graph_contrib(
    list_dict_to_plot=[dict_to_plot],
    fig_title='',
    add_number_percentage="",#"percentage",
    add_prod_mix=0,
    add_conso_mix=0,
    subplot_size=(8, 10),

) #title, figsize
```

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[5,6,10],
    "column":'contribution to difference % 100'
    }
list_dict_to_plot.append(dict_to_plot)
```

```python
plot_bar_graph_contrib(
    list_dict_to_plot=[dict_to_plot],
    fig_title='',
    add_number_percentage="",#"percentage",
    add_prod_mix=0,
    add_conso_mix=0,
    subplot_size=(8, 10),

) #title, figsize
```

### with electricity from storage disaggregated into 2

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[1,3,4,8,9,10],
    "column":'contribution to impact'
    }
list_dict_to_plot.append(dict_to_plot)
```

```python
plot_bar_graph_contrib(
    list_dict_to_plot=[dict_to_plot],
    fig_title='',
    add_number_percentage="percentage",
    add_prod_mix=1,
    add_conso_mix=1
) #title, figsize
```

```python
list_df_ca_aggreg_ter2=[]
for df in list_df_ca_aggreg_ter:
    df2=df.copy()
    df2.loc[df['act']=='market for electricity, high voltage, FE2050','difference with production mix']=df.loc[df['act']=='market for electricity, high voltage, FE2050','impact/kWh (absolute)'].values.tolist()[0]
    df2.loc[df['act']=='market for electricity, from direct French production, FE2050','difference with production mix']=df.loc[df['act']=='market for electricity, from direct French production, FE2050','impact/kWh (absolute)'].values.tolist()[0]
    df2.loc[df['act']=='market for electricity, from direct French production, FE2050','color']='grey'
    df2.loc[df['act']=='market for electricity, from direct French production, FE2050','label']='1 kWh from direct production'
    for act in ['storage losses and infrastructure','differential impacts due to imports','curtailment']:
        df2.loc[df['act']==act,'difference with production mix']=df.loc[df['act']==act,'contribution to impact'].values.tolist()[0]
    list_df_ca_aggreg_ter2.append(df2)
```

```python
list_df_to_plot=[list_df_ca_aggreg_ter2]
```

```python
if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg_ter2[order])
else:
    list_df_to_plot=list_df_ca_aggreg_ter2
```

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[1,4,9,10],
    "column":'difference with production mix'
    }
list_dict_to_plot.append(dict_to_plot)
```

```python
plot_bar_graph_contrib(
    list_dict_to_plot=[dict_to_plot],
    fig_title='',
    add_number_percentage="percentage",
    add_prod_mix=1,
    add_conso_mix=1
) #title, figsize
```

```python
plot_bar_graph_contrib(
    list_dict_to_plot=list_dict_to_plot,
    fig_title='',
    add_number_percentage="percentage",
    add_prod_mix=1,
    add_conso_mix=1
) #title, figsize
```

### with storage infra and losses disagregated

```python
list_df_to_plot=list_df_ca_aggreg_ter
```

```python
if change_plot_order==1: 
    #Generate the list to plot
    list_df_to_plot= []
    for order in plot_order:
        list_df_to_plot.append(list_df_ca_aggreg_ter[order])
```

```python
dict_to_plot={
    "list_df_to_plot":list_df_to_plot,
    "rows":[9,5,6,10],
    "column":'contribution to difference'
    }
list_dict_to_plot.append(dict_to_plot)
```

```python
plot_bar_graph_contrib(
    list_dict_to_plot=[dict_to_plot],
    
    fig_title='Differential contribution analysis',
    fig_name='test-fig.png',

    add_number_percentage=0,
    add_prod_mix=0,
    add_conso_mix=0,
    
    subplot_size=(2, 3.5),
    #width=0.7,
    sharey=False,
    pos_legend=(0.5, -1),
    
    size_subplot_title=10,
    size_label=8,

) #title, figsize
```

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot,
                       rows=[9,5,6,10],
                       column='contribution to difference',
                       add_number_percentage="NO",
                       add_prod_mix='no',
                       #figsize=(8, 6)
                      ) #title, figsize
```

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot,
                       rows=[9,5,6,10],
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

### Pertes high medium low 

```python
1.0312427*1.0042*1.0307
#0.0312427 	0.0042 0.0307 pertes high/medium/low
#8% RTE

```

## Impact 1 kWh of electricity
Calculate the impact of a chosen activity per several scenarios / years


### `🔧` database, impact category, activities

```python
#premise_db_list
```

```python
#selected_db_list=[premise_db_list[0]]#,premise_db_list[1],premise_db_list[4],]
selected_db_list=selected_db_list[0]
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

### Run

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

```python

```

### Production mix : Pie chart

```python
column="amount"
list_df_prod_mix=[]


for df in list_df_mix:

    #calculate the rate of fluctuating renewable
    amount_PVwind=0
    amount_tot=0
    for act in fluctuating_renew:
        amount_PVwind=amount_PVwind+df[df["act"]==act]["amount"].values.tolist()[0]
    for act in direct_elec_prod_act_names:
        if act in df['act'].tolist():
            amount_tot=amount_tot+df[df["act"]==act]["amount"].values.tolist()[0]
    PV_wind_rate=amount_PVwind/b*100
    
    #print only production activities
    df=df[df["act"]!="market for electricity, high voltage, FE2050"]
    df=df[df["act"]!="market group for electricity, high voltage"]
    for act_name in storage_act_names:
        df=df[df["act"]!=act_name]
    df["percentage production technology"]=df["amount"]/df["amount"].sum()
    list_df_prod_mix.append(df)
    
    fig, ax = plt.subplots()
    ax.pie(
        df[column],
        labels=df['label'],#autopct='%1.1f%%',
        colors=df["color"],
        radius=0.9,
        labeldistance=None,
        startangle=90,
    )
    plt.title(df['FR scenario'].iloc[0]+','+ str(df['year'].iloc[0]) + ", ""{:.0f}".format(PV_wind_rate) + "% of PV+Wind")
    
    # Add legend without redundant labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=(0.5, 1.3), loc='center')
    plt.savefig('image-production mix.png')
```

```python

```

<!-- #region jp-MarkdownHeadingCollapsed=true -->
## old Detailed contribution analysis with grid reallocation
<!-- #endregion -->

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

## Excel Export

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
