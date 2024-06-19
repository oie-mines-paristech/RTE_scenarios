---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.2
  kernelspec:
    display_name: lca_alg_11
    language: python
    name: lca_alg_11
---

Impacts market for electricity, high voltage, Tr2050 > see sheet elec 1 kWh
* Impacts elec 1kWh FR : Base (17 to 50 kgCo2eq) > RCP26 (10 to 40 kgCo2eq) > RCP19 (-10 to 30 kgCo2eq)
  
Imports > See sheet imports contributions 
* Impacts elec 1kWh FR without import : Base (17 to 50 kgCo2eq) > RCP26 (10 to 40 kgCo2eq) > RCP19 (neg to 30 kgCo2eq)  kgCo2eq 
* Impacts imports Base > RCP26  > RCP19  == 400 / 100 / 8 kgCo2eq
* Imports S1 =18% > S2 > S3 > S4 =28%
  
Background activities used as input for "market for electricity, high voltage, Tr2050"
* Strange impact results for these activities (a lot of neg values)
* Surprising that same IAM model and different French scenarios, the results are slightly different 


```python
#importation of usefull packages
from init import *
import bw2data
import bw2io
```

# To do `🔧` 

```python
PROJECT_NAME="HySPI_premise_FE2050_9"
```

```python
#Set in the right project and print the databases
bw2data.projects.set_current(PROJECT_NAME)
list(bw2data.databases)
#agb.list_databases() #equivalent lca_algebraic function
```

# Fonctions
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

```python
for db in premise_db_list:
    if '2050' in db.name:
        db.year=2050
    if 'Base' in db.name:
        db.IAM_scenario='Base'
    if 'RCP26' in db.name:
        db.IAM_scenario='RCP26'
    if 'RCP19' in db.name:
        db.IAM_scenario='RCP19'
    if 'M0' in db.name:
        db.FR_scenario='M0'
    if 'M1' in db.name:
        db.FR_scenario='M1'
    if 'M23' in db.name:
        db.FR_scenario='M23'
    if 'N1' in db.name:
        db.FR_scenario='N1'
    if 'N2' in db.name:
        db.FR_scenario='N2'
    if 'N03' in db.name:
        db.FR_scenario='N03'

```

```python
df=pd.DataFrame([],columns=['db_name','IAM scenario','FR scenario','year'])
for db in premise_db_list:
    df.loc[len(df.index)] = [db.name,db.IAM_scenario,db.FR_scenario,db.year]
df
```

```python
def db_name_list(*args):
    """ Generate a list of database's name containing given keywords (one or several)"""
    list_db_name=[]
    for db_name in bw2data.databases.keys():
        a=0
        for arg in args:
            if arg in db_name:
                a=a+1
        if a==len(args):
            list_db_name.append(db_name)
    return list_db_name
```

```python
#Example 
db_name_list('Base')
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
EF = 'EF v3.0 no LT'
climate = (EF, 'climate change no LT', 'global warming potential (GWP100) no LT')
impacts=[climate]
```

```python
list_LCIA_methods = [m[0] for m in bw.methods if "EF"  in str(m) and not "no LT" in str(m) and not'obsolete' in str(m)]
list_LCIA_methods = [*set(list_LCIA_methods)]  #this line automatically delete the duplicates
list_LCIA_methods
```

```python
LCIA_method = 'EF v3.0'

ecosystem_quality_acid = (LCIA_method,'acidification','accumulated exceedance (AE)')
impacts=[ecosystem_quality_acid]
```

# Impact of electricity


## To do `🔧` 

```python
elec_act_name="market for electricity, high voltage, FE2050"
```

## Impact 1 kWh of electricity

```python
#To do : generate a list of databases to exploe
#list_db_name=db_name_list('S1')
list_db_name=premise_db_name_list
list_db_name
```

```python
df=pd.DataFrame([],columns=['scenario','act','impact','unit'])
list_act=[]

for dbtoexplore_name in list_db_name:
    act_elec_1kWh=agb.findActivity(elec_act_name, db_name=dbtoexplore_name)
    list_act.append(act_elec_1kWh)

for act in list_act:
   lca = act.lca(method=climate, amount=1)
   score = lca.score
   unit = bw2data.Method(climate).metadata["unit"]
   df.loc[len(df.index)] = [act["database"],act["name"],score,unit]
```

```python
df
```

```python
df_colour=df.style.background_gradient(cmap='Blues')
df_colour
```

```python
df=pd.DataFrame([],columns=['db_name','IAM scenario','FR scenario','year','act','impact','unit'])
list_act=[]

for db in premise_db_list:
#for dbtoexplore_name in list_db_name:
    act=agb.findActivity(elec_act_name, db_name=db.name)
    #list_act.append(act_elec_1kWh)
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

## Imports contribution 
## `🔧` Comment/uncomment + Change name of act without imports

```python
list_db_name=premise_db_name_list
```

```python
df=pd.DataFrame([],columns=['scenario','% import','% impact of imports','impact 1 kWh elec','impact 1 kWh import','impact 1kWh without import','unit'])
list_act=[]

for dbtoexplore_name in list_db_name:
    act_elec_1kWh=agb.findActivity(elec_act_name, db_name=dbtoexplore_name)
    list_act.append(act_elec_1kWh)

for act_elec_1kWh in list_act:
    lca = act_elec_1kWh.lca(method=climate, amount=1)
    impact_elec_1kWh = lca.score

    import_kWh=[exc for exc in act_elec_1kWh.exchanges() if exc["name"]=='market group for electricity, high voltage'][0]
    act_import=import_kWh.input
    
    lca = act_import.lca(method=climate, amount=1)
    impact_import_1kWh = lca.score
    ratio_impact=impact_import_1kWh*import_kWh["amount"]/impact_elec_1kWh 
    #act_elec_without_import=agb.findActivity("market for electricity without imports, high voltage, FE2050",db_name=act_elec_1kWh["database"])
    #act_elec_without_import=agb.copyActivity(act_elec_1kWh["database"],act_elec_1kWh,"market for electricity without imports, high voltage, FE2050")
    #act_elec_without_import.deleteExchanges('market group for electricity, high voltage')
    lca = act_elec_without_import.lca(method=climate, amount=1)
    impact_elec_without_import_1kWh = lca.score/(1-import_kWh["amount"])
    
    unit = bw2data.Method(climate).metadata["unit"]
    
    df.loc[len(df.index)] = [act_elec_1kWh["database"],import_kWh["amount"],ratio_impact,impact_elec_1kWh,impact_import_1kWh,impact_elec_without_import_1kWh,unit]

df_import=df.style.map(style_neg, props='background-color:red;',subset='impact 1kWh without import')
df_import
```

## Impact of background activities used to model FR electricity market (depends on IAM model)


## To do `🔧` : choose IAM scenario

```python
#list_db_name=db_name_list('Base')
#list_db_name=db_name_list('RCP26')
list_db_name=db_name_list('RCP19')

list_db_name
```

### Print All

```python
df=pd.DataFrame([],columns=['scenario','act','impact','unit'])
list_exc=[]
list_act=[]

for dbtoexplore_name in list_db_name:
    act_elec_1kWh=agb.findActivity(elec_act_name, db_name=dbtoexplore_name)
    list_act.append(act_elec_1kWh)

for act in list_act:
    excs=[exc.input for exc in act.exchanges() if exc["type"]=='technosphere' and exc["name"]!=elec_act_name]
    for exc in excs:
#        if exc["name"] not in str(list_exc):
            list_exc.append(exc)

for exc in list_exc:
    lca = exc.lca(method=climate, amount=1)
    score = lca.score
    unit = bw2data.Method(climate).metadata["unit"]
    df.loc[len(df.index)] = [exc["database"],exc["name"],score,unit]

#df_Base_all = df.style.map(style_neg, props='background-color:red;')
#df_Base_all
#df_RCP26_al = df.style.map(style_neg, props='background-color:red;')
#df_RCP26_all
df_RCP19_all = df.style.map(style_neg, props='background-color:red;')
df_RCP19_all
```

## Print only neg values

```python
df=pd.DataFrame([],columns=['scenario','act','impact','unit'])
list_exc=[]
list_act=[]

for dbtoexplore_name in list_db_name:
    act_elec_1kWh=agb.findActivity(elec_act_name, db_name=dbtoexplore_name)
    list_act.append(act_elec_1kWh)

for act in list_act:
    excs=[exc.input for exc in act.exchanges() if exc["type"]=='technosphere' and exc["name"]!=elec_act_name]
    for exc in excs:
#        if exc["name"] not in str(list_exc):
            list_exc.append(exc)

for exc in list_exc:
    lca = exc.lca(method=climate, amount=1)
    score = lca.score
    unit = bw2data.Method(climate).metadata["unit"]
    if score < 0 :
        df.loc[len(df.index)] = [exc["database"],exc["name"],score,unit]

df_RCP19_neg = df.style.map(style_neg, props='background-color:red;')
df_RCP19_neg
```

### Print for one act

```python
#list_db_name=db_name_list('Base')
#list_db_name=db_name_list('RCP26')
list_db_name=db_name_list('RCP19')
list_db_name

line_0=2
```

```python
df=pd.DataFrame([],columns=['scenario','act','impact','unit'])
list_exc=[]
list_act=[]

for dbtoexplore_name in list_db_name:
    act_elec_1kWh=agb.findActivity(elec_act_name, db_name=dbtoexplore_name)
    list_act.append(act_elec_1kWh)

for act in list_act:
    excs=[exc.input for exc in act.exchanges() if exc["type"]=='technosphere' and exc["name"]!=elec_act_name]
    for exc in excs:
#        if exc["name"] not in str(list_exc):
            list_exc.append(exc)

for n in range(5):
    exc=list_exc[n*15+line_0]
    lca = exc.lca(method=climate, amount=1)
    score = lca.score
    unit = bw2data.Method(climate).metadata["unit"]
    df.loc[len(df.index)] = [exc["database"],exc["name"],score,unit]

df_comparison = df.style.map(style_neg, props='background-color:red;')
df_comparison
```

# Heat > can not print some results ??

```python
#    act_heat=agb.findActivity('market for heat, district or industrial, natural gas', loc='WEU', db_name=dbtoexplore_name)
```

# Export to excel

```python
xlsx_file_name="export_data_FE2050.xlsx"
list_df_to_export=[
    ["elec 1 kWh",df_elec],     
    ["imports contribution",df_import],
    ["background act", df_RCP19_all]  
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
dbtoexplore=db_name_list('2024')[0]
#dbtoexplore='M0_2050_SSP2Base'
dbtoexplore	
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

# Draft

```python
bw2data.methods
```

```python
list_LCIA_methods = [m[0] for m in bw.methods if "EF v3.0"  in str(m) and not "no LT" in str(m) and not'EN15804' in str(m)]
list_LCIA_methods = [*set(list_LCIA_methods)]  #this line automatically delete the duplicates
list_LCIA_methods[0].keys()
```

```python
bw.methods
```

```python
method_key = ('EF v3.0 no LT', 'climate change no LT', 'global warming potential (GWP100) no LT')
method_key
```

```python
method_data = bw.Method(method_key).load()
print("Number of CFs:", len(method_data))
method_data[:60]
```

```python

```
