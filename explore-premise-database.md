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

```python
#importation of usefull packages
import bw2data
import bw2io
import pandas as pd
import numpy as np
```

# Intitialisation
## `🔧` Project name and ecoinvent names *2

```python
PROJECT_NAME="HySPI_premise_FE2050_13"
```

```python
#Set in the right project and print the databases
bw2data.projects.set_current(PROJECT_NAME)
list(bw2data.databases)
#agb.list_databases() #equivalent lca_algebraic function
```

```python
ecoinvent_db_name='ecoinvent-3.9.1-cutoff'
biosphere_db_name='ecoinvent-3.9.1-biosphere'
```

```python
#If you need to delete a database
#del bw2data.databases['ei_cutoff_3.9_tiam-ucl_SSP2-RCP45_2050_Reference - N2 2025-01-23']
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
#from premise_gwp import add_premise_gwp
#add_premise_gwp()
#climate_premise=('IPCC 2021', 'climate change', 'GWP 100a, incl. H and bio CO2')
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
SSP_list=['SSP1','SSP2']
IAM_scenario_list=['Base','RCP26','RCP45','Npi']
FR_scenario_list=['M0','M1','M23','N1','N2','N03']
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

## `🔧` Select databases with filters

```python
#To generate a list of databases based on filters on the year / IAM scenario / FR_Scenario
#Example
selected_db_list=[db for db in premise_db_list if db.FR_scenario=='M0' and db.year==2050]
```

```python editable=true slideshow={"slide_type": ""}
#If you want to run the tests on all premise databases
selected_db_list=premise_db_list
```

# Impact 1 kWh of electricity


## `🔧` activity, impact category, db to explore

```python
elec_act_name="market for electricity, high voltage, FE2050"
impact_cat=climate
selected_db_list=selected_db_list #premise_db_list
```

## Run

```python
df=pd.DataFrame([],columns=['db_name','model','IAM scenario','FR scenario','year','act','impact','unit'])
#list_act=[]

for db in selected_db_list:    
    #act=agb.findActivity(elec_act_name, db_name=db.name)
    act=db.search(elec_act_name)[0]
    lca = act.lca(method=impact_cat, amount=1)
    score = lca.score
    unit = bw2data.Method(impact_cat).metadata["unit"]
    df.loc[len(df.index)] = [db.name,db.model, db.IAM_scenario,db.FR_scenario,db.year,act["name"],score,unit]
```

```python editable=true slideshow={"slide_type": ""}
#df_elec = df.style.map(style_red, props='background-color:red;')\
#             .map(style_orange, props='background-color:orange;')\
#             .map(style_green, props='background-color:green;')
df_elec=df#.style.background_gradient(cmap='Reds')
df_elec
```

```python
elec_act_name="market for electricity, direct production only, high voltage, FE2050"
df=pd.DataFrame([],columns=['db_name','model','IAM scenario','FR scenario','year','act','impact','unit'])
#list_act=[]

for db in selected_db_list:    
    #act=agb.findActivity(elec_act_name, db_name=db.name)
    act=db.search(elec_act_name)[0]
    lca = act.lca(method=impact_cat, amount=1)
    score = lca.score
    unit = bw2data.Method(impact_cat).metadata["unit"]
    df.loc[len(df.index)] = [db.name,db.model, db.IAM_scenario,db.FR_scenario,db.year,act["name"],score,unit]

df_elec_2=df#.style.background_gradient(cmap='Reds')
df_elec_2
```

<!-- #region editable=true slideshow={"slide_type": ""} -->
# Contribution analysis
<!-- #endregion -->

## `🔧` activity, impact category, db to explore

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

## Contribution analysis (ca)

```python
list_df_ca=[]

#For each db in the selected list
for db in selected_db_list:
    #initialisation of the dataframe
    df=pd.DataFrame([],columns=[
        'db_name',
        'model',
        'IAM scenario',
        'FR scenario',
        'year',
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
                db.IAM_scenario,
                db.FR_scenario,
                db.year,
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
                db.IAM_scenario,
                db.FR_scenario,
                db.year,
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

## Aggregated contribution analysis into 6 subcategories for electricity source
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
        result_df['IAM scenario']=filtered_df['IAM scenario'].iloc[0],
        result_df['FR scenario']=filtered_df['FR scenario'].iloc[0],
        result_df['year']=filtered_df['year'].iloc[0],
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

# Excel Export

```python editable=true slideshow={"slide_type": ""}
xlsx_file_name="export-test-01.xlsx"

list_df_to_export=[
    ["elec 1 kWh", df_elec, df_elec_2],
    ["contrib an. detail"] + list_df_ca,
    ["contrib an. aggreg"] + list_df_ca_aggregated,
]

export_data_to_excel(list_df_to_export,xlsx_file_name)
```

```python
elec_act_name="market for electricity, high voltage, FE2050"
impact_cat=climate
```

```python
df=pd.DataFrame([],columns=[
    'db_name',
    'model',
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
    #act_elec_1kWh=agb.findActivity(elec_act_name, db_name=db.name)
    act_elec_1kWh=db.search(elec_act_name)[0]

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
    #act_elec_without_import=agb.copyActivity(db.name,act_elec_1kWh,"market for electricity without imports, high voltage, FE2050 - warning the ref flow is no more 1 kWh")
    act_elec_without_import = act_elec_1kWh.copy()
    act_elec_without_import.name="market for electricity without imports, high voltage, FE2050 - warning the ref flow is no more 1 kWh"
    act_elec_without_import.save()
    act_elec_without_import.as_dict()
    #act_elec_without_import.deleteExchanges('market group for electricity, high voltage')
    import_kWh_bis=[exc for exc in act_elec_without_import.exchanges() if exc["name"]=='market group for electricity, high voltage'][0]
    import_kWh_bis.delete
    act_elec_without_import.save()
    act_elec_without_import.as_dict()

    
#WARNING #If you redo the calcultation, comment the two last lines and run only the line below
    #act_elec_without_import=agb.findActivity("market for electricity without imports, high voltage, FE2050 - warning the ref flow is no more 1 kWh",db_name=db.name)
    db.search("market for electricity without imports, high voltage, FE2050 - warning the ref flow is no more 1 kWh")
    
    #Impacts of production elec mix (redimensioning the impacts to consider a 1 kWh ref flow)
    lca = act_elec_without_import.lca(method=impact_cat, amount=1)
    impact_elec_without_import_1kWh = lca.score/(1-import_kWh["amount"])

    #'impacts(1 kWh imports)/impact(1 kWh production elec mix)'
    ratio_impacts_imports_on_productionmix=impact_import_1kWh/impact_elec_without_import_1kWh
    
    #Unit of the impact considered
    unit = bw2data.Method(climate).metadata["unit"]

    df.loc[len(df.index)] = [
        db.name,
        db.model,
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

<!-- #region editable=true slideshow={"slide_type": ""} -->
# Old / to delete
<!-- #endregion -->

## Tests à compléter sur les autres marchés

```python
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

```python
for df in list_df_ca_aggregated:
    df=df.style.format({
                    'amount': '{:,.3f}'.format,
                    'impact': '{:,.1e}'.format,
                    '% impact': '{:,.2%}'.format,
                    'absolute impact': '{:,.1e}'.format,
                    'absolute impact/impact elec':'{:,.2f}'.format,
                })\
             .background_gradient(cmap='Reds')
```
