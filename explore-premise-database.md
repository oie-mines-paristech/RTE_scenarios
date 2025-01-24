---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: premise5
    language: python
    name: premise5
---

## `🔧` To switch from FE2050 to Tr2050


```python
#importation of usefull packages
from init import *
import bw2data
import bw2io
```

# Intitialisation
## `🔧` Project name 

```python
PROJECT_NAME="HySPI_premise_FE2050_11"
```

```python
#Set in the right project and print the databases
bw2data.projects.set_current(PROJECT_NAME)
list(bw2data.databases)
#agb.list_databases() #equivalent lca_algebraic function
```

# Utils
## Manipulating databases

```python
ecoinvent_3_9_db= bw2data.Database('ecoinvent-3.9.1-cutoff')
ecoinvent_3_9_db_name='ecoinvent-3.9.1-cutoff'
```

```python
ecoinvent_3_9_db.name
```

```python
#generate a list of names of generated databases by premise
premise_db_name_list=list(bw2data.databases.keys())
for db_name in bw2data.databases.keys():
    if "biosphere" in db_name:
        premise_db_name_list.remove(db_name)
    elif "ecoinvent" in db_name:
        premise_db_name_list.remove(db_name)
premise_db_name_list
```

```python
#generate a list of generated databases by premise
premise_db_list=[]
for db_name in premise_db_name_list:
    premise_db_list.append(bw2data.Database(db_name))
premise_db_list
```

## `🔧` filters the database

```python
model_list=['image','tiam-ucl','remind']
SSP_list=['SSP1','SSP2']
IAM_scenario_list=['Base','RCP26','RCP45','Npi']
FR_scenario_list=['M0','M1','M23','N1','N2','NO3']
```

```python
#tag the database with corresponding year, model, IAM scenario and FR scenario
for db in premise_db_list:
    if '2050' in db.name:
        db.year=2050
    for model in model_list:
        if model in db.name:
            db.model=model    
    for IAM_scenario in IAM_scenario_list:
        if IAM_scenario in db.name:
            db.IAM_scenario=IAM_scenario      
    db.FR_scenario='None'
    for FR_scenario in FR_scenario_list:
        if FR_scenario in db.name:
            db.FR_scenario=FR_scenario    

```

```python
#Each database can be sorted with these tags
df=pd.DataFrame([],columns=['db_name','model','IAM scenario','FR scenario','year'])
for db in premise_db_list:
    df.loc[len(df.index)] = [db.name,db.model,db.IAM_scenario,db.FR_scenario,db.year]
df
```

```python
#To generate a list of databases based on filters on the year / IAM scenario / FR_Scenario
selected_db=[db for db in premise_db_list if db.model=='tiam-ucl' and db.IAM_scenario=='Base' and db.FR_scenario=='M0'] #and db.year==2050]
```

## Export excel 

```python
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

## Dataframe printing

```python
high_value=0.050
low_value=0.015

def style_red(v, props=''):
    return props if type(v)==float and v > high_value else None
def style_orange(v, props=''):
    return props if type(v)==float and v < high_value and v >low_value else None
def style_green(v, props=''):
    return props if type(v)==float and v < low_value else None
```

```python
def style_neg(v, props=''):
    return props if type(v)==float and v < 0 else None
```

# Methods

```python
EF = 'EF v3.1'
climate = (EF, 'climate change no LT', 'global warming potential (GWP100)')
acidification = (EF,'acidification','accumulated exceedance (AE)')
land=('EF v3.1', 'land use', 'soil quality index')
ionising_rad=('EF v3.1','ionising radiation: human health','human exposure efficiency relative to u235')
metals_minerals= ('EF v3.1','material resources: metals/minerals','abiotic depletion potential (ADP): elements (ultimate reserves)'),
non_renew_energy=('EF v3.1','energy resources: non-renewable','abiotic depletion potential (ADP): fossil fuels')
impacts=[climate, acidification, land, ionising_rad,metals_minerals,non_renew_energy]
```

```python
#To see all the categories associated with EF3.1
#agb.findMethods("",EF)
```

```python
list_LCIA_methods = [m[0] for m in bw.methods if "EF"  in str(m) and not "no LT" in str(m) and not'obsolete' in str(m)]
list_LCIA_methods = [*set(list_LCIA_methods)]  #this line automatically delete the duplicates
list_LCIA_methods
```

# Impact 1 kWh of electricity


## `🔧` elec_act_name

```python
elec_act_name="market for electricity, high voltage, FE2050"
```

## Run

```python
df=pd.DataFrame([],columns=['db_name','IAM scenario','FR scenario','year','act','impact','unit'])
list_act=[]

for db in premise_db_list:
    act=agb.findActivity(elec_act_name, db_name=db.name)
    lca = act.lca(method=climate, amount=1)
    score = lca.score
    unit = bw2data.Method(climate).metadata["unit"]
    df.loc[len(df.index)] = [db.name,db.IAM_scenario,db.FR_scenario,db.year,act["name"],score,unit]
```

```python
#df_elec = df.style.map(style_red, props='background-color:red;')\
#             .map(style_orange, props='background-color:orange;')\
#             .map(style_green, props='background-color:green;')
df_elec=df.style.background_gradient(cmap='Reds')
df_elec
```

# Electricity imports contribution 
## `🔧` elec_act_name + impact category
## WARNING : Comment/uncomment the line starting with #Warning and change name of the "activity without imports" if needed

```python
elec_act_name="market for electricity, high voltage, FE2050"
impact_cat=climate
```

```python
df=pd.DataFrame([],columns=[
    'db_name',
    'IAM scenario',
    'FR scenario',
    'year',
    'Contribution of import to consumption elec mix (1 kWh)',
    'Contribution of imports to impacts of 1 kWh of consumption elec mix',
    'impacts(1 kWh imports)/impact(1 kWh production elec mix)',
    'impact 1 kWh elec',
    'impact 1 kWh import',
    'impact 1kWh without import',
    'unit'])

for db in premise_db_list:
    #Activity 1 kWh elec mix
    act_elec_1kWh=agb.findActivity(elec_act_name, db_name=db.name)

    #Impact of 1 kWh of consumption elec mix
    lca = act_elec_1kWh.lca(method=climate, amount=1)
    impact_elec_1kWh = lca.score

    #Activity that models import
    import_kWh=[exc for exc in act_elec_1kWh.exchanges() if exc["name"]=='market group for electricity, high voltage'][0]
    act_import=import_kWh.input

    #Contribution of import to consumption elec mix (1 kWh)
    #import_kWh["amount"]
    
    #Impact of 1 kWh of import
    lca = act_import.lca(method=climate, amount=1)
    impact_import_1kWh = lca.score

    #Contribution of imports to impacts of 1 kWh of consumption elec mix
    contribution_imports_impact_consumptionmix=impact_import_1kWh*import_kWh["amount"]/impact_elec_1kWh 

    #Generating activity that models production elec mix (just deleting imports)
    act_elec_without_import=agb.copyActivity(db.name,act_elec_1kWh,"market for electricity without imports, high voltage, FE2050 - warning the ref flow is no more 1 kWh")
    act_elec_without_import.deleteExchanges('market group for electricity, high voltage')

#WARNING #If you redo the calcultation, comment the two last lines and run only the line below
    act_elec_without_import=agb.findActivity("market for electricity without imports, high voltage, FE2050 - warning the ref flow is no more 1 kWh",db_name=db.name)
    
    #Impacts of production elec mix (redimensioning the impacts to consider a 1 kWh ref flow)
    lca = act_elec_without_import.lca(method=impact_cat, amount=1)
    impact_elec_without_import_1kWh = lca.score/(1-import_kWh["amount"])

    #'impacts(1 kWh imports)/impact(1 kWh production elec mix)'
    ratio_impacts_imports_on_productionmix=impact_import_1kWh/impact_elec_without_import_1kWh
    
    #Unit of the impact considered
    unit = bw2data.Method(climate).metadata["unit"]

    df.loc[len(df.index)] = [
        db.name,
        db.IAM_scenario,
        db.FR_scenario,
        db.year,
        import_kWh["amount"],
        contribution_imports_impact_consumptionmix,
        ratio_impacts_imports_on_productionmix,
        impact_elec_1kWh,
        impact_import_1kWh,
        impact_elec_without_import_1kWh,
        unit]

#df_import=df.style.map(style_neg, props='background-color:red;',subset='impact 1kWh without import')
df_import=df
df_import
```

# Impact of background activities used to model FR electricity market

```python
df=pd.DataFrame([],columns=[
    'db_name',
    'IAM scenario',
    'FR scenario',
    'year',
    'act',
    'impact',
    'unit'
    ])

for db in premise_db_list:
    act=agb.findActivity(elec_act_name, db_name=db.name)
    excs=[exc.input for exc in act.exchanges() if exc["type"]=='technosphere'] #and exc["name"]!=elec_act_name]
    for exc in excs:
        lca = exc.lca(method=climate, amount=1)
        score = lca.score
        unit = bw2data.Method(climate).metadata["unit"]
        df.loc[len(df.index)] = [
            db.name,
            db.IAM_scenario,
            db.FR_scenario,
            db.year,
            exc["name"],
            score,
            unit]

```

```python
df_elec_all=df.style.background_gradient(cmap='Reds')
df_elec_all
```

```python
#Same done for 'market for electricity, high voltage, FR' from original ecoinvent database

df=pd.DataFrame([],columns=[
    'db_name',
    'IAM scenario',
    'FR scenario',
    'year',
    'act',
    'impact',
    'unit'
    ])


act=agb.findActivity('market for electricity, high voltage', loc='FR', db_name='ecoinvent-3.9.1-cutoff')
excs=[exc.input for exc in act.exchanges() if exc["type"]=='technosphere'] #and exc["name"]!=elec_act_name]
for exc in excs:
    lca = exc.lca(method=climate, amount=1)
    score = lca.score
    unit = bw2data.Method(climate).metadata["unit"]
    df.loc[len(df.index)] = [
            'ecoinvent-3.9.1-cutoff',
            "None",
            "None",
            "None",
            exc["name"],
            score,
            unit]
```

```python
df_elec_ecoinvent=df.style.background_gradient(cmap='Reds')
df_elec_ecoinvent
```

## Tests à compléter sur les autres marchés


**Comparaison ecoinvent / premise / premise + external scenarios**

* market group for gas, high pressure - WEU
* market for compressed gas, high pressure, FE2050
replaces market for natural gas, high pressure - FR (ei)
* market for compressed gas, low pressure, FE2050
replaces market for natural gas, low pressure - FR (ei)

* pas de market for petrol centralisé dans ei
* market for diesel, FE2050
replaces market for petrol - WEU + market for petrol, low sulfur - WEU

* market for hydrogen créés > ce sont les mêmes ratios pour les marchés donc diff viennent de market for compressed gas, low pressure, FE2050 pour SMR et market elec pour électrolysis > comparer juste l'hydrogène produit par électrolyse et l'hydrogène par SMR en FR


# Heat > to be deleted. Peu de différence entre les différents scénarios RCP

```python
heat_act_name='market for heat, district or industrial, natural gas'
```

```python
df=pd.DataFrame([],columns=['db_name','IAM scenario','FR scenario','year','act','impact','unit'])
list_act=[]

for db in premise_db_list:
    act=agb.findActivity(heat_act_name, loc='WEU',db_name=db.name)
    lca = act.lca(method=climate, amount=1)
    score = lca.score
    unit = bw2data.Method(climate).metadata["unit"]
    df.loc[len(df.index)] = [db.name,db.IAM_scenario,db.FR_scenario,db.year,act["name"],score,unit]
```

```python
#df_elec = df.style.map(style_red, props='background-color:red;')\
#             .map(style_orange, props='background-color:orange;')\
#             .map(style_green, props='background-color:green;')
df_heat=df.style.background_gradient(cmap='Reds')
df_heat
```

# Export to excel

```python
xlsx_file_name="export_data_FE2050_9.xlsx"
list_df_to_export=[
    ["elec 1 kWh",df_elec],
    ["elec background act premise", df_elec_all],
    ["elec background act ecoinvent", df_elec_ecoinvent],
    ["heat WEU act", df_heat],    
    ["imports contribution",df_import],
]
export_data_to_excel(list_df_to_export,xlsx_file_name)
```

# Basic test


## Test ecoinvent

```python
elec_ecoinvent=agb.findActivity("market for electricity, high voltage", loc='FR', db_name=ecoinvent_3_9_db_name)
elec_ecoinvent
```

```python
agb.printAct(elec_ecoinvent)
```

```python
agb.compute_impacts(elec_ecoinvent,impacts)
```

## Test premise database

```python
dbtoexplore='ei_cutoff_3.9_image_SSP2-Base_2050_Reference - M0 2024-06-17'
elec_act_name="market for electricity, high voltage, FE2050"
```

```python
elec_2050=agb.findActivity(elec_act_name, db_name=dbtoexplore)
```

```python
agb.printAct(elec_2050)
```

```python
excs=[exc for exc in elec_2050.exchanges() if 'Ozone' in exc["name"]][0]
excs.input["database"]
```

```python
agb.compute_impacts(elec_2050,impacts)
```

```python
pv=agb.findActivity("electricity production, photovoltaic", loc='FR', db_name=dbtoexplore)
```

```python
agb.compute_impacts(pv,impacts)
```

```python

```
