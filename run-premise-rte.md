---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: premise247
    language: python
    name: premise247
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
# ecoinvent + biosphere shall be already loaded in the the project
NAME_BW_PROJECT="premise_France_RTE" 
```

```python
#HELP To get all brightway projects
#list(bw2data.projects)
```

```python
#Open the brightway project
bw2data.projects.set_current(NAME_BW_PROJECT)

#Print the databases that are in your project
list(bw2data.databases)
```

```python
#Name ecoinvent databases
eco_version="3.10"
ecoinvent_3_10_db_name='ecoinvent-3.10.1-cutoff'
ecoinvent_3_10_bio_db_name="ecoinvent-3.10.1-biosphere"
```

```python
#HELP if needed to delete a database
#del bw2data.databases['tiam-SSP2-Base-N1']
```

# List of IAM and French scenarios

```python
#List of IAM scenarios

image="image"
SSP2_VLHO='SSP2-VLHO'
SSP2_L="SSP2-L" 
SSP2_M="SSP2-M"
SSP3_H="SSP3-H"

tiam="tiam-ucl"
SSP2_RCP19="SSP2-RCP19"
SSP2_RCP26="SSP2-RCP26"
SSP2_RCP45="SSP2-RCP45"
SSP2_Base="SSP2-Base"

remind="remind"
SSP2_650="SSP2-PkBudg650"
SSP2_1000="SSP2-PkBudg1000"
SSP2_NDC="SSP2-NDC"
SSP2_NPi="SSP2-NPi"
SSP2_rollBack="SSP2-rollBack"
SSP3_rollBack="SSP3-rollBack"


```

```python
#List of French scenario

#French scenario référence
M0="Reference - M0"
M1="Reference - M1"
M23="Reference - M23"
N1="Reference - N1"
N2="Reference - N2"
N03="Reference - N03"

#French scenario sob
M0_sob="Sobriety - M0"
M1_sob="Sobriety - M1"
M23_sob="Sobriety - M23"
N03_sob="Sobriety - N03"
N1_sob="Sobriety - N1"
N2_sob="Sobriety - N2"

#French scenario reindus
M0_ind="Extensive reindustrialization - M0"
M1_ind="Extensive reindustrialization - M1"
M23_ind="Extensive reindustrialization - M23"
N03_ind="Extensive reindustrialization - N03"
N1_ind="Extensive reindustrialization - N1"
N2_ind="Extensive reindustrialization - N2"
```

# Generate a new version of ecoinvent according to scenarios
List of scenarios provided by premise : https://premise.readthedocs.io/en/latest/introduction.html#choosing-the-right-iam

```python
fp = r"datapackage.json"
rte = Package(fp)
```

```python
#Choose the year 
year=2050
```

```python
#If you want to run premise without French scenario
scenarios = [
        {"model": image, "pathway":SSP2_L, "year": year},
        {"model": image, "pathway": SSP2_M, "year": year}      
        ]
```

```python
#If you want to Run premise with French scenario
# Choose the year, IAM and FR scenario combinations. 

scenarios = [
            {"model": image, "pathway":SSP2_M, "year": year, "external scenarios": [{"scenario": M0, "data": rte}]},
            #{"model": image, "pathway":SSP2_L, "year": year, "external scenarios": [{"scenario": M0, "data": rte}]},
]
```

```python editable=true slideshow={"slide_type": ""}
ndb = NewDatabase(
        scenarios = scenarios,        
        source_db=ecoinvent_3_10_db_name,
        source_version=eco_version,
        key='tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo=',
        biosphere_name=ecoinvent_3_10_bio_db_name,
        #use_multiprocessing=True
)
```

```python
#Update the newdatabase ndb
ndb.update()

#or update only chosen sectors
#ndb.update("biomass")
#ndb.update(["electricity","external"])
```

```python editable=true slideshow={"slide_type": ""}
#Write the database to brightway
ndb.write_db_to_brightway()

#or write a superstructure database to brightway to compare scenarios in Activity Browser
#ndb.write_superstructure_db_to_brightway(name="tiam-SSP2-Base-M0")
```

```python editable=true slideshow={"slide_type": ""}
#List of all databases
list(bw2data.databases)
```

```python
#if needed to delete a database
del bw2data.databases['ei_cutoff_3.10_image_SSP2-M_2050_Reference - M0 2026-07-24']
```

# Explore the new database


## Explore the activities and exchanges

```python
list(bw2data.databases)
```

```python
#name of the database you want to explore
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
#exc = [exc for exc in act.exchanges() if "wind" in e.input["name"]][0]  
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
