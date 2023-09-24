# Futurs énergétiques 2050 (Energy future 2050)


Description
-----------

This is a repository containing a scenario that implements the projections of the 
French electricity operator (RTE) for:

* electricity

It is meant to be used in `premise` in addition to a global IAM scenario, to provide 
refined projections at the country level.

This data package contains all the files necessary for `premise` to implement
this scenario and create market-specific composition for electricity (including imports from
neighboring countries), liquid and gaseous fuels (including hydrogen).

Sourced from publication
------------------------

Futurs énergétiques 2050\
Réseau de Transport d'Electricité\
https://assets.rte-france.com/prod/public/2021-12/Futurs-Energetiques-2050-principaux-resultats.pdf

Data validation 
---------------

[![goodtables.io](https://goodtables.io/badge/github/romainsacchi/RTE_scenarios.svg)](https://goodtables.io/github/romainsacchi/RTE_scenarios)

Test 
----

![example workflow](https://github.com/romainsacchi/RTE_scenarios/actions/workflows/main.yml/badge.svg?branch=main)

Ecoinvent database compatibility
--------------------------------

ecoinvent 3.8 cut-off

IAM scenario compatibility
---------------------------

The following coupling is done between IAM and FE2050+ scenarios:

| IAM scenario           | FE2050+ scenario                    |
|------------------------|-------------------------------------|
| IMAGE SSP2-Base        | Extensive reindustrialization - M0  |
| IMAGE SSP2-RCP26       | Extensive reindustrialization - M1  |
| IMAGE SSP2-RCP45       | Extensive reindustrialization - M23 |
| IMAGE SSP2-RCP60       | Extensive reindustrialization - N03 |
| IMAGE SSP2-RCP85       | Extensive reindustrialization - N1  |
| IMAGE SSP2-Base        | Extensive reindustrialization - N2  |
| IMAGE SSP2-RCP26       | Reference - M0                      |
| IMAGE SSP2-RCP45       | Reference - M1                      |
| IMAGE SSP2-RCP60       | Reference - M23                     |
| IMAGE SSP2-RCP85       | Reference - N03                     |
| IMAGE SSP2-Base        | Reference - N1                      |
| IMAGE SSP2-RCP26       | Reference - N2                      |
| IMAGE SSP2-RCP45       | Sobriety - M0                       |
| IMAGE SSP2-RCP60       | Sobriety - M1                       |
| IMAGE SSP2-RCP85       | Sobriety - M23                      |
| IMAGE SSP2-Base        | Sobriety - N03                      |
| IMAGE SSP2-RCP26       | Sobriety - N1                       |
| IMAGE SSP2-RCP45       | Sobriety - N2                       |


What does this do?
------------------

![map electricity markets](assets/map.png)

This external scenario creates markets for France listed below, according
to the projections from the RTE's Energy Future 2050 (yellow boundaries in map above).

Electricity
***********

* `market for electricity, high voltage, EF2050` (CH)
* `market for electricity, medium voltage, EF2050` (CH)
* `market for electricity, medium voltage, EF2050` (CH)

These markets are relinked to activities that consume electricity in France.

Additionally, the French market relies to a varying extent on imports from
neighboring countries. These imports are sourced from the rest of Europe, which is
provided by the regional IAM market for European electricity (blue boundaries in map above).

How are technologies mapped?
---------------------------
The tables below show how the mapping between reported technologies
and LCI datasets is done. Unless specified otherwise, ecoinvent
LCI datasets are used.

Electricity
***********

| Technologies in FE2050+             | LCI datasets used                                               | Remarks                                                                                                                   |
|-------------------------------------|-----------------------------------------------------------------| ------------------------------------------------------------------------------------------------------------------------- |
| Hydro, run-of-river                 | electricity production, hydro, run-of-river                     |
| Hydro, alpine reservoir             | electricity production, hydro, reservoir, alpine region         |
| Nuclear, Evolutionary Power Reactor | electricity production, Evolutionary Power Reactor (EPR)        | 
| Nuclear, Small Modular Reactor      | electricity production, Small Modular Reactor (SMR)             |
| Nuclear, Pressure water reactor     | electricity production, nuclear, pressure water reactor         |
| Conventional, Waste-to-Energy       | treatment of municipal solid waste, incineration                |
| Conventional, Other                 | electricity production, natural gas, combined cycle power plant |                                                  |
| Conventional, Coal                  | electricity production, hard coal                               |
| Conventional, Natural gas           | electricity production, natural gas, combined cycle power plant |
| Conventional, Oil                   | electricity production, oil                                     |
| Renewable, Photovoltaic             | electricity production, photovoltaic                            | Datasets from 10.13140/RG.2.2.17977.19041.                                                                                |
| Renewable, Wind turbines, Onshore   | electricity production, wind, 1-3MW turbine, onshore            |
| Renewable, Wind turbines, Offshore  | electricity production, wind, 1-3MW turbine, offshore           |
| Renewable, Geothermal               | electricity production, deep geothermal                         | Dataset provided by premise, based on the geothermal heat dataset of ecoinvent.                                           |
| Renewable, Biomass                  | heat and power co-generation, wood chips, 6667 kW               |
| Renewable, Biogas                   | heat and power co-generation, biogas, gas engine                |
| Renewable, Wave                     | electricity production, wave energy converter                   |
| Storage, Hydrogen                   | electricity production, from hydrogen                           |
| Storage, Vehicle-to-grid            | electricity production, from vehicle-to-grid                    |
| Storage, Battery                    | electricity production, from stationary battery                 |
| Storage, Pumped hydro               | electricity production, hydro, pumped storage                   |

Fuels
*****

Markets for diesel, gasoline and gas are created:

* `market for diesel, EF2050` (FR)
* `market for gasoline, EF2050` (FR)
* `market for compressed gas, high pressure, FE2050` (FR)
* `market for compressed gas, low pressure, FE2050` (FR)

These markets are relinked to activities that consume liquid and gaseous fuels in France.

| Technologies in FE2050+ | LCI datasets used                                 | Remarks |
|-------------------------|---------------------------------------------------|---------|
| Fossil, diesel          | market for diesel, low-sulfur                     |   
| Fossil, gasoline        | market for gasoline, low-sulfur                   |
| Biofuel, biodiesel      | diodiesel, from rapeseed oil, at fuelling station |
| Biofuel, bioethanol     | ethanol production from sugar beet                |
| CNG                     | market for natural gas, high pressure             |
| LNG                     | market for natural gas, liquefied                 |
| Biomethane              | market for biomethane, high pressure              |         |


Hydrogen
********

Markets for hydrogen are created:

* `market for hydrogen, gaseous, for refinery use, FE2050` (FR)
* `market for hydrogen, gaseous, for ammonia use, FE2050` (FR)
* `market for hydrogen, gaseous, for chemicals use, FE2050` (FR)
* `market for hydrogen, gaseous, for steel use, FE2050` (FR)
* `market for hydrogen, gaseous, for various use, FE2050` (FR)

These markets are relinked to activities that consume hydrogen in France, according to their area
of application.

| Technologies in FE2050+       | LCI datasets used                                                       | Remarks |
|-------------------------------|-------------------------------------------------------------------------|---------|
| Hydrogen, electrolysis        | hydrogen production, electrolysis, 25 bar, domestic                     |
| Hydrogen, from coke gas + CCS | hydrogen, recovered from coke oven gas, with carbon capture and storage |
| Hydrogen, refinery            | hydrogen production, gaseous, petroleum refinery operation              |
| Hydrogen, from chlore-alkali  | chlor-alkali electrolysis, diaphragm cell                               |
| Hydrogen, APME cracking       | hydrogen cracking, APME                                                 |
| Hydrogen, from SMR of NG      | hydrogen production, steam reforming                                    |
| Hydrogen, from ammonia        | hydrogen production, steam reforming                                    |


Flow diagram
------------


How to use it?
--------------

```python

    import brightway2 as bw
    from premise import NewDatabase
    from datapackage import Package
    
    
    fp = r"https://raw.githubusercontent.com/romainsacchi/RTE_scenarios/main/datapackage.json"
    FE2050 = Package(fp)
    
    bw.projects.set_current("your_bw_project")
    
    ndb = NewDatabase(
            scenarios = [
                {"model":"image", "pathway":"SSP2-Base", "year":2050,},
                {"model":"image", "pathway":"SSP2-RCP26", "year":2030,},
            ],        
            source_db="ecoinvent 3.8 cutoff",
            source_version="3.8",
            key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            external_scenarios=[
                FE2050, # <-- list datapackages here
            ] 
        )
```

