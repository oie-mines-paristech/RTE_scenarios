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
import os as os
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
selected_db_list_2=[db for db in premise_db_list if 'M0' in db.name and'remind' in db.name and db.SSP=='SSP2' and db.RCP in ['PkBudg1000','NDC','NPi']]
selected_db_list_3=[db for db in premise_db_list if 'remind' in db.name and db.SSP=='SSP2' and db.RCP=='NDC']
selected_db_list_4=selected_db_list_3+[db for db in premise_db_list if db.year==2020]

#selected_db_list=[selected_db_list[-3]]
selected_db_list=selected_db_list_4
selected_db_list
```

# `🔧` Choose configuration for analysis

```python
#selected_impacts=[impacts[0]]+[impacts[3]]
selected_impacts=impacts
for impact_cat in selected_impacts:
    print(impact_cat[1])
```

```python
selected_db_list=selected_db_list_4
#[selected_db_list_4[0]]+[selected_db_list_4[5]]
selected_db_list
```

```python
mainfolder='remind_SSP2-NDC/'
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
#new_input_name="market for electricity production, direct production, high voltage, FE2050"
#create_empty_act(selected_db_list)
#change_input_storage_mix(selected_db_list,new_input_name)
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
newpath='remind_SSP2-NDC/climate change'
#newpath='remind_SSP2-NDC/acidification'
#newpath='remind_SSP2-NDC/land use'
#newpath='remind_SSP2-NDC/ionising radiation human health'
#newpath='remind_SSP2-NDC/material resources metals minerals'
#newpath='remind_SSP2-NDC/energy resources non-renewable'
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
for df in list_df_ca_aggreg:
    list_df=pd.concat([list_df,df.head(1)],ignore_index=True)
list_df
```

## `🔧` Optional : choose specific change databases to compare and order

```python
#Choose what you want to plot in which order on the graphs
change_plot_order=1
plot_order=[6,0,2,5]
```

# Definition of functions

```python
#Fonction to plot aggregated amount
def plot_bar_graph_french_scenarios(
    title,
    list_df_to_plot,
    column,
    starting_row=0,
    figsize=(3, 6),
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
    plt.savefig('image-origin of electricity.png')
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


### Aggregated origin : Bar graph

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

### Production mix ; bar chart

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

### Storage mix: Bar chart

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

## Impact: Aggregated contribution analysis

```python
#Fonction to plot aggregated contribution
def plot_bar_graph_contrib(
    list_df_to_plot, 
    column, rows=[1,2,3],
    add_number_percentage="number",
    add_prod_mix='no',
    add_conso_mix='no'):
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
        base1=0
        base2=0

        for row in rows:
            value=df[column].iloc[row]
            if value>=0:
                    base=base1
            if value<0:
                    base=base2
        
            ax.bar(a, value, width=0.3, bottom=base, color=df['color'].iloc[row], label=df['label'].iloc[row],hatch=df['hatch'].iloc[row], edgecolor="lightgrey")
            base=base+value
            
            if value>=0:
                base1=base1+value
            if value<0:
                base2=base2+value


        col='impact/kWh (absolute)'
        elec_conso_impact=df.loc[df['act']=='market for electricity, high voltage, FE2050',col].tolist()[0]
        elec_prod_impact=df.loc[df['act']=='market for electricity, from direct French production, FE2050',col].tolist()[0]

        if add_number_percentage=="percentage":

            #plot storage mix (point)
            #ax.plot(a, df.loc[df['act']=='market for electricity, from storage, FE2050','impact/kWh (absolute)'].values, color='magenta', label='1 kWh - from storage', marker = 'o')    
            
            #relative difference production mix >> consumption mix
            diff=(elec_conso_impact-elec_prod_impact)/elec_prod_impact*100 
            if diff>=0:
                sign="+"
            if diff<0:
                sign=""
            
            #add labels
            ax.annotate(
                text = f'{round(elec_conso_impact,1)} | {sign} {round(diff)}%',
                #text = f'{round(df[column].iloc[0],1)} | + {round(df[col].iloc[1],1)}| +{round(diff)}%',
                xy=(a, max(elec_conso_impact,elec_prod_impact)*1.05),
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
            ax.plot(a, elec_prod_impact, color='darkorange', label='1 kWh, production mix', marker ="D",markersize=10)    
        
        if add_conso_mix=='yes':
            ax.plot(a, elec_conso_impact, color='forestgreen', label='1 kWh, consumption mix', marker ="o",markersize=6)    
    
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

```python
def plot_contributions(list_of_list_df_to_plot, 
                        columns_list, 
                        rows_list,
                        add_number_percentage_list,
                        add_prod_mix_list,
                        add_conso_mix_list,
                        save_fig=False,
                        fig_name='contrib_to_impact.png'):
    """
    Plot contribution of different datasets
    """

    fig, axs = plt.subplots(len(list_of_list_df_to_plot), 1, figsize=(10, 6*len(list_of_list_df_to_plot)))

    for i, (list_df_to_plot, columns, rows, add_number_percentage, add_prod_mix, add_conso_mix) in enumerate(zip(list_of_list_df_to_plot, columns_list, rows_list, add_number_percentage_list, add_prod_mix_list, add_conso_mix_list)):
        ax = axs[i]
        for j, df in enumerate(list_df_to_plot):
            # Plot bar chart
            ax.bar(j, df[columns])

        # Add labels and title
        ax.set_title(f'Contribution of {list_df_to_plot[0].columns[0]}')
        ax.set_xlabel('Category')
        ax.set_ylabel('Value')

    # Layout so plots do not overlap
    plt.tight_layout()

    # Save figure
    if save_fig:
        plt.savefig(fig_name)

    # Show plot
    plt.show()

```

### without electricity from storage disaggregated

```python
#Choose what you want to plot in which order on the graphs
change_plot_order=1
plot_order=[5]
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
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot,
                       rows=[1,2,7,10],
                       column='contribution to impact',
                       add_number_percentage="percentage",
                       add_prod_mix='yes',
                       add_conso_mix='yes'
                       #figsize=(8, 6)
                      ) #title, figsize
```

### with electricity from storage disaggregated into 2

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot,
                       rows=[1,3,4,8,9,10],
                       column='contribution to impact',
                       add_number_percentage="percentage",
                       add_prod_mix='yes',
                       #figsize=(8, 6)
                      ) #title, figsdata:image/png;base64,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ize
```

```python
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot,
                       rows=[1,3,8,4,9,10],
                       column='contribution to impact',
                       add_number_percentage="percentage",
                       add_prod_mix='yes',
                       add_conso_mix="yes"
                       #figsize=(8, 6)
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
plot_bar_graph_contrib(list_df_to_plot=list_df_to_plot,
                       rows=[1,4,9,10],
                       column='difference with production mix',
                       add_number_percentage="percentage",
                       add_prod_mix='yes',
                       #figsize=(8, 6)
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
