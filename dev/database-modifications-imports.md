```python
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
NAME_BW_PROJECT="HySPI_premise_FE2050_23"
```

```python
#Set in the right project and print the databases
bw2data.projects.set_current(NAME_BW_PROJECT)
list(bw2data.databases)
#agb.list_databases() #equivalent lca_algebraic function
```

```python
ecoinvent_db_name='ecoinvent-3.10.1-cutoff'
biosphere_db_name='ecoinvent-3.10.1-biosphere'
ecoinvent_db=bw2data.Database(ecoinvent_db_name)
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

```python
#generate a list of generated databases by premise
premise_db_list=[]
for db_name in premise_db_name_list:
    premise_db_list.append(bw2data.Database(db_name))
```

```python
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

```python
#If you want to run the tests on all premise databases
selected_db_list=premise_db_list
```

```python
#To generate a list of databases based on filters on the year / SSP / RCP/ FR_Scenario
#Example
selected_db_list=[db for db in premise_db_list if 'RCP45' in db.name]# and 'update' not in db.name]+[db for db in premise_db_list if db.name=='ei_cutoff_3.9_tiam-ucl_SSP2-RCP45_2050_Reference - N1 2025-05-15']
selected_db_list
#selected_db_list=[selected_db_list[2]]
```

# Database modification : Run only once


## Create new French electricity activity with European mix as import mix 
* WARNING !! Do not cross databases // Ideally we should create these new activity in user_db
* track the interaction btw databases
    * M0, RCP45 > ecoinvent 3.10, M0 RCP26, M0 Base
    * NO3, RCP45 > ecoinvent 3.10, NO3 RCP26, NO3 Base

```python
#Db list where you want to change the imports
selected_db_list=[premise_db_list[1]] #selectioooooon
selected_db_list
```

```python
#if I just want to create a market with imports from european mix generated with the same IAM
with_EUR_imports="yes" 
#if I want to create french markets with imports from european mix taken from other IAM
#!!!!!!!!!!!!! If several imports EUR, only one database !!
with_EUR_imports_severals="yes" 
#db_import_list is the list from where imports come from with_EUR_imports_severals="yes"
db_import_list_severals=[premise_db_list[0]]+[premise_db_list[1]]+[premise_db_list[2]]
db_import_list_severals
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
                code=(act_storage["name"]+add_to_act_name)
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
                code=(act1["name"]+add_to_act_name)
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
                code=(act2["name"]+add_to_act_name)
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
                code=(act_storage["name"]+add_to_act_name)
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

## Create a new activity with imports by hand 

```python
premise_db_list
```

```python
db=premise_db_list[1]
db
```

```python
#imports from EUR current (ecoinvent)
add_to_act_name=", with European mix from ecoinvent 3.10.1 as import mix"
db_of_new_import_act=bw2data.Database('ecoinvent-3.10.1-cutoff')
new_import_name='market group for electricity, high voltage'
new_import_loc='RER'
import_prod=[act for act in db_of_new_import_act if act["name"]==new_import_name and act["location"]==new_import_loc][0]
agb.printAct(import_prod)

```

```python
#imports from wind mix
add_to_act_name=", with onshore wind mix as import mix"
new_import_name="electricity production, wind, 1-3MW turbine, onshore"
new_import_loc='FR'
import_prod=[act for act in db_of_new_import_act if act["name"]==new_import_name and act["location"]==new_import_loc][0]
agb.printAct(import_prod)
```

```python
#imports with no impacts
empty_act=agb.newActivity(
    db.name,
    "empty activity",
    "unit",
)
import_prod=empty_act
add_to_act_name=", with empty activity as import mix"
```

```python
# avec empty, changer la fin de la cellule pour mettre empty dans le import mix et ne pas garder le grid
import_mix_copy = agb.copyActivity(
            db_name=db.name,                   # Database where the new activity is copied
            activity = empty_act,             # initial activity
            code="market for electricity, from import, FE2050"+add_to_act_name
        )
```

#Does not work, I do not know why
#Imports with renew scenario
solar=[act for act in db if act["name"]=="electricity production, photovoltaic" and act["location"]=="FR"][0]
onshore=[act for act in db if act["name"]=="electricity production, wind, 1-3MW turbine, onshore" and act["location"]=="FR"][0]
offshore=[act for act in db if act["name"]=="electricity production, wind, 1-3MW turbine, offshore" and act["location"]=="FR"][0]
solar_wind_mix=agb.newActivity(
    db.name,
    "miiix 50% solar, 50% wind - 25% onshore, 25% offshore",
    "kilowatt hour",
    exchanges={
        onshore : 0.25, #add flows and amount 
        offshore:0.25,
        solar:0.5
    }
)
#import_prod=solar_wind_mix
#agb.printAct(import_prod)
add_to_act_name=", with solar + wind mix as import mix"

```python
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
                code=(act_storage["name"]+add_to_act_name)
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
                code=(act1["name"]+add_to_act_name)
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
                code=(act2["name"]+add_to_act_name)
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
                code=(act_storage["name"]+add_to_act_name)
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
        
        for exc in excs_elec:
            if exc.input["name"]=="market for electricity production, direct production, high voltage, FE2050":
                #french_mix_copy["import"]=exc["amount"]
                #french_mix_copy.save()
                exc.input=import_prod
                exc.save()

        #copy import market (with losses and grid)
        import_mix=db.search("market for electricity, from import, FE2050")[0]
        import_mix_copy = agb.copyActivity(
            db_name=db.name,                   # Database where the new activity is copied
            activity = import_mix,             # initial activity
            code="market for electricity, from import, FE2050"+add_to_act_name
        )
        
        #Change the input elec in copied import market
        excs_import=[exc for exc in import_mix_copy.exchanges()]
        for exc in excs_import:
            if exc.input["name"]=="market for electricity production, direct production, high voltage, FE2050":
                exc.input=import_prod
                exc.save()


```
