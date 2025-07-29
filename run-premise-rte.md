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

# Initialisation

```python
from premise import *
import bw2data
import bw2io
from datapackage import Package
```

# Open brightway project

```python
#Put the name of your brightway project
# ecoinvent + biosphere shall be already loaded as databases of the project
list(bw2data.projects)
# It should be ecoinvent 3.9 or more recent version
NAME_BW_PROJECT="HySPI_premise_FE2050_15"
```

```python
#Open the brightway project
bw2data.projects.set_current(NAME_BW_PROJECT)
#bw2data.projects.current

#Print the databases that are in your project
list(bw2data.databases)
```

```python
ecoinvent_3_9_db_name='ecoinvent-3.9.1-cutoff'
ecoinvent_3_9_bio_db_name="ecoinvent-3.9.1-biosphere"

ecoinvent_3_10_db_name='ecoinvent-3.10-cutoff'
ecoinvent_3_10_bio_db_name="ecoinvent-3.10-biosphere"

```

```python
#if needed to delete a database
#del bw2data.databases['tiam-SSP2-Base-N1']
```

# Generate a new version of ecoinvent according to scenarios

```python
fp = r"datapackage.json"
rte = Package(fp)
```

```python
# Choose the scenario to generate
#IAM model
model_1="image"
model_2="tiam-ucl"
model_3="remind"

#world scenario

world_scenario_1="SSP2-Base"
world_scenario_2="SSP2-RCP45"
world_scenario_3="SSP2-RCP26"
world_scenario_4="SSP2-RCP19"
world_scenario_5="SSP2-NPi"

#Year
year=2050

#French scenario référence
fr_scenario_1="Reference - M0"
fr_scenario_2="Reference - M1"
fr_scenario_3="Reference - M23"
fr_scenario_4="Reference - N1"
fr_scenario_5="Reference - N2"
fr_scenario_6="Reference - N03"

#French scenario sob
fr_scenario_1_sob="Sobriety - M0"
fr_scenario_2_sob="Sobriety - M1"
fr_scenario_3_sob="Sobriety - M23"
fr_scenario_4_sob="Sobriety - N03"
fr_scenario_5_sob="Sobriety - N1"
fr_scenario_6_sob="Sobriety - N2"

#French scenario reindus
fr_scenario_1_ind="Extensive reindustrialization - M0"
fr_scenario_2_ind="Extensive reindustrialization - M1"
fr_scenario_3_ind="Extensive reindustrialization - M23"
fr_scenario_4_ind="Extensive reindustrialization - N03"
fr_scenario_5_ind="Extensive reindustrialization - N1"
fr_scenario_6_ind="Extensive reindustrialization - N2"

```

```python
#Run premise without French scenario
scenarios = [
        {"model": model_3, "pathway":"SSP1-NDC", "year": 2050},
        {"model": model_2, "pathway":world_scenario_1, "year": year}      
        ]
```

```python
#to delete
scenarios = [
        {"model": model_2, "pathway":world_scenario_1, "year": 2050, "external scenarios": [{"scenario": fr_scenario_1, "data": rte}]},
  ]
```

```python editable=true slideshow={"slide_type": ""}
#Run premise with a combination of global and French scenarios
scenarios = [
        {"model": model_2, "pathway":world_scenario_2, "year": 2020, "external scenarios": [{"scenario": fr_scenario_4, "data": rte}]},
        {"model": model_2, "pathway":world_scenario_1, "year": 2050, "external scenarios": [{"scenario": fr_scenario_4, "data": rte}]},
        {"model": model_2, "pathway":world_scenario_2, "year": 2050, "external scenarios": [{"scenario": fr_scenario_4, "data": rte}]},
        {"model": model_2, "pathway":world_scenario_3, "year": 2050, "external scenarios": [{"scenario": fr_scenario_4, "data": rte}]},
  ]
```

```python
scenarios = [
    {"model": model_2, "pathway":world_scenario_2, "year": 2050, "external scenarios": [{"scenario": fr_scenario_4, "data": rte}]},
]
```

```python editable=true slideshow={"slide_type": ""}
ndb = NewDatabase(
        scenarios = scenarios,        
        source_db=ecoinvent_3_10_db_name,
        source_version="3.10",
        key='tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo=',
        biosphere_name=ecoinvent_3_10_bio_db_name,
        #use_multiprocessing=True
)
```

```python
ndb.update()
#ndb.update("biomass")
#ndb.update(["electricity","external"])
```

```python editable=true slideshow={"slide_type": ""}
#Write the database to brightway
ndb.write_db_to_brightway()
#ndb.write_db_to_brightway()

#or write a superstructure database to brightway to compare scenarios in Activity Browser
#ndb.write_superstructure_db_to_brightway(name="tiam-SSP2-Base-M0")
```

```python editable=true slideshow={"slide_type": ""}
list(bw2data.databases)
```

```python
#if needed to delete a database
#del bw2data.databases['ei_cutoff_3.10_remind_SSP1-NDC_2050 2025-07-29']
```

## Extraction to be done 

```python
#Run premise with a combination of global and French scenarios
scenarios = [
        {"model": model_2, "pathway":world_scenario_1, "year": 2050, "external scenarios": [{"scenario": fr_scenario_1, "data": rte}]},
        {"model": model_2, "pathway":world_scenario_2, "year": 2050, "external scenarios": [{"scenario": fr_scenario_1, "data": rte}]},
        {"model": model_2, "pathway":world_scenario_3, "year": 2050, "external scenarios": [{"scenario": fr_scenario_1, "data": rte}]},
  ]

ndb = NewDatabase(
        scenarios = scenarios,        
        source_db=ecoinvent_3_9_db_name,
        source_version="3.9.1",
        key='tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo=',
        biosphere_name=ecoinvent_3_9_bio_db_name,
        #use_multiprocessing=True
)

ndb.update()

ndb.write_db_to_brightway()

list(bw2data.databases)

```

```python
#Run premise with a combination of global and French scenarios
scenarios = [
        {"model": model_2, "pathway":world_scenario_1, "year": 2050, "external scenarios": [{"scenario": fr_scenario_6, "data": rte}]},
        {"model": model_2, "pathway":world_scenario_2, "year": 2050, "external scenarios": [{"scenario": fr_scenario_6, "data": rte}]},
        {"model": model_2, "pathway":world_scenario_3, "year": 2050, "external scenarios": [{"scenario": fr_scenario_6, "data": rte}]},
  ]

ndb = NewDatabase(
        scenarios = scenarios,        
        source_db=ecoinvent_3_9_db_name,
        source_version="3.9.1",
        key='tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo=',
        biosphere_name=ecoinvent_3_9_bio_db_name,
        #use_multiprocessing=True
)

ndb.update()

ndb.write_db_to_brightway()

list(bw2data.databases)
```

```python
#Run premise with a combination of global and French scenarios

#changeeeeer le fichier de scenario data
#changer le nom des databases ou le faire à J+1 sinon cela va écraser les autres database

scenarios = [
        {"model": model_2, "pathway":world_scenario_2, "year": 2020, "external scenarios": [{"scenario": fr_scenario_4, "data": rte}]},
       {"model": model_2, "pathway":world_scenario_2, "year": 2050, "external scenarios": [{"scenario": fr_scenario_4, "data": rte}]},
       {"model": model_2, "pathway":world_scenario_1, "year": 2020, "external scenarios": [{"scenario": fr_scenario_4, "data": rte}]},
       {"model": model_2, "pathway":world_scenario_1, "year": 2050, "external scenarios": [{"scenario": fr_scenario_4, "data": rte}]},
  ]
```

# Incremental

```python
inc = IncrementalDatabase(
        scenarios = scenarios,        
        source_db=ecoinvent_3_9_db_name,
        source_version="3.9.1",
        key='tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo=',
        biosphere_name=ecoinvent_3_9_bio_db_name,
)
```

```python editable=true slideshow={"slide_type": ""}
sectors = {
    "FR":"external",
    "electricity": "electricity",
}

```

```python editable=true slideshow={"slide_type": ""}
inc.update(sectors=sectors)
```

```python
inc.write_increment_db_to_brightway(name="test increment 7", file_format="csv")
```

```python
sectors = {
    "FR scenarios":"external",
    "electricity": "electricity",
    "others": ["steel","dac","fuels","heat","biomass","cement","emissions","cars","trucks","two_wheelers","buses"]
   
}

sectors = {
    "electricity": "electricity",
    "steel": "steel",
    "others": [
        "cement",
        "cars",
        "fuels"
    ]
}
```

# Explore the new database


## Explore the activities and exchanges

```python
list(bw2data.databases)
```

```python
#name of the db you want to explore
db_name='ei_cutoff_3.10_tiam-ucl_SSP2-Base_2050_Reference - M0 2025-02-25'
db = bw2data.Database(db_name)
```

```python
acts=[act for act in db if "FE2050" in act["name"]]
acts
```

```python
act=[act for act in db if "hydrogen production, gaseous, 30 bar, " in act["name"]]# and act["location"]=="FR"][0]
act
```

```python
exc = [exc for exc in act.exchanges()]
exc
#exc = [exc for exc in act.exchanges() if "wind" in e.input["name"]][0]  # ¡¡¡Nota: e.input et torna l'activitat!!!!
```

## Compute impacts

```python
act=[act for act in db if "market for electricity, high voltage, FE2050" in act["name"] and act["location"]=="FR"][0]
act
```

```python
#Climate change with EF3.1
climate = ('EF v3.1', 'climate change', 'global warming potential (GWP100)')
#impact calculation
lca = act.lca(method=climate, amount=1)
score = lca.score
unit = bw2data.Method(climate).metadata["unit"]
score
```

## Compare premise gwp with EF gwp

```python
#If you want you can import climate change impact method that is updated by premise
from premise_gwp import add_premise_gwp
add_premise_gwp()
climate_premise=('IPCC 2021', 'climate change', 'GWP 100a, incl. H and bio CO2')
```

```python
#name of the db you want to explore
db_name_1='ei_cutoff_3.9_tiam-ucl_SSP2-Base_2050_Reference - M0 2025-02-19'
db_name_2='ei_cutoff_3.9_tiam-ucl_SSP2-RCP45_2050_Reference - M0 2025-02-19'
```

```python
db1 = bw2data.Database(db_name_1)
db2 = bw2data.Database(db_name_2)

act1=[act for act in db1 if "market for electricity, high voltage, FE2050" in act["name"] and act["location"]=="FR"][0]
act2=[act for act in db2 if "market for electricity, high voltage, FE2050" in act["name"] and act["location"]=="FR"][0]
```

```python
#SSP2base
lca = act1.lca(method=climate, amount=1)
score1 = lca.score

lca = act1.lca(method=climate_premise, amount=1)
score1p = lca.score

print("{:.2f}".format(score1*1000))
print("{:.2f}".format(score1p*1000))
```

```python
#SSP2 RCP45
lca = act2.lca(method=climate, amount=1)
score2 = lca.score

lca = act2.lca(method=climate_premise, amount=1)
score2p = lca.score

print("{:.2f}".format(score2*1000))
print("{:.2f}".format(score2p*1000))
```
