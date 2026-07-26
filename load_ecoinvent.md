---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

## To be completed by the user

```python
#Put you ecoinvent username and password
eco_username="xxx"
eco_password="xxx
# Choose the ecoinvent version. The cut-off system model will be chosen. 
eco_version="3.12"
```

# Initialisation

```python
import bw2data
import bw2io 
```

```python
#Name ecoinvent databases
if eco_version=="3.10": 
    ecoinvent_db_name='ecoinvent-3.10.1-cutoff'
    ecoinvent_db_name="ecoinvent-3.10.1-biosphere"
    NAME_BW_PROJECT="premise_France_RTE" 

if eco_version=="3.11": 
    ecoinvent_db_name='ecoinvent-3.11-cutoff'
    ecoinvent_db_name="ecoinvent-3.11-biosphere"
    NAME_BW_PROJECT="premise_France_RTE_311"
    NAME_BW_PROJECT="ecoinvent_3_11"

if eco_version=="3.12": 
    ecoinvent_db_name='ecoinvent-3.12-cutoff'
    ecoinvent_bio_db_name="ecoinvent-3.12-biosphere"
    NAME_BW_PROJECT="premise_France_RTE_312"
```

```python
eco_system_model='cutoff'
```

```python
#Give the password associated with your ecoinvent account
from ecoinvent_interface import Settings, permanent_setting
permanent_setting("username",eco_username )
permanent_setting("password", eco_password)
```

```python
from ecoinvent_interface import Settings, EcoinventRelease, ReleaseType
my_settings = Settings(username= eco_username, password=eco_password)
release = EcoinventRelease(my_settings)
#release.list_versions()
#release.list_system_models('3.10')
release.get_release(version=eco_version, system_model=eco_system_model, release_type=ReleaseType.ecospold)
```

```python
#open a brightway project
bw2data.projects.set_current(NAME_BW_PROJECT)
bw2data.projects.current, list(bw2data.databases)
```

```python
#load the chosen vesion of ecoinvent. Here an example with ecoinvent 3.9.1, cut off
bw2io.import_ecoinvent_release(eco_version, eco_system_model)
```

```python
#You should have two databases in your project : technosphere and biosphere database
list(bw2data.databases)
```
