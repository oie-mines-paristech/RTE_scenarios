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

The following coupling is done between IAM and EP2050+ scenarios:

| IAM scenario           | EP2050+ scenario     |
|------------------------|----------------------|
| IMAGE SSP2-Base        | Business As Usual    |
| IMAGE SSP2-RCP26       | ZERO Basis (default) |
| IMAGE SSP2-RCP26       | ZERO A               |
| IMAGE SSP2-RCP26       | ZERO B               |
| IMAGE SSP2-RCP26       | ZERO C               |
| IMAGE SSP2-RCP19       | ZERO Basis (default) |
| IMAGE SSP2-RCP19       | ZERO A               |
| IMAGE SSP2-RCP19       | ZERO B               |
| IMAGE SSP2-RCP19       | ZERO C               |
| REMIND SSP2-Base       | Business As Usual    |
| REMIND SSP2-PkBudg1150 | ZERO Basis (default) |
| REMIND SSP2-PkBudg1150 | ZERO A               |
| REMIND SSP2-PkBudg1150 | ZERO B               |
| REMIND SSP2-PkBudg1150 | ZERO C               |
| REMIND SSP2-PkBudg500  | ZERO Basis           |
| REMIND SSP2-PkBudg500  | ZERO A               |
| REMIND SSP2-PkBudg500  | ZERO B               |
| REMIND SSP2-PkBudg500  | ZERO C               |

What does this do?
------------------

![map electricity markets](assets/map.png)

This external scenario creates markets for France listed below, according
to the projections from the RTE's Energy Future 2050 2050+ (yellow boundaries in map above).

Electricity
***********

* `market for electricity, high voltage, EF2050` (CH)
* `market for electricity, medium voltage, EF2050` (CH)
* `market for electricity, medium voltage, EF2050` (CH)

These markets are relinked to activities that consume electricity in France.

Additionally, the Swiss markets rely to a varying extent on imports from
neighboring countries (FR + DE + IT + AT), for which a market is also created 
(orange boundaries in map above):

* `import from neighboring countries electricity, high voltage` (CH)

That market itself relies on imports from the rest of Europe, which is
provided by the regional IAM market for European electricity (blue boundaries in map above).

How are technologies mapped?
---------------------------
The tables below show how the mapping between reported technologies
and LCI datasets is done. Unless specified otherwise, ecoinvent
LCI datasets are used.

Electricity
***********

| Technologies in EP2050+            | LCI datasets used                                               | Remarks                                                                                                                   |
| ---------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Hydro, run-of-river                | electricity production, hydro, run-of-river                     |
| Hydro, alpine reservoir            | electricity production, hydro, reservoir, alpine region         |
| Nuclear, Boiling water reactor     | electricity production, nuclear, boiling water reactor          | The split between boiling water and pressure water is not provided. We use the current split, based on production volume. |
| Nuclear, Pressure water reactor    | electricity production, nuclear, pressure water reactor         |
| Conventional, Waste-to-Energy      | treatment of municipal solid waste, incineration                |
| Conventional, Other                | electricity production, natural gas, combined cycle power plant | The report does not specify what "Other" is. Assumed to be natural gas.                                                   |
| Conventional, Coal                 | electricity production, hard coal                               |
| Conventional, Natural gas          | electricity production, natural gas, combined cycle power plant |
| Renewable, Photovoltaic            | electricity production, photovoltaic                            | Datasets from 10.13140/RG.2.2.17977.19041.                                                                                |
| Renewable, Wind turbines, Onshore  | electricity production, wind, 1-3MW turbine, onshore            |
| Renewable, Wind turbines, Offshore | electricity production, wind, 1-3MW turbine, offshore           |
| Renewable, Geothermal              | electricity production, deep geothermal                         | Dataset provided by premise, based on the geothermal heat dataset of ecoinvent.                                           |
| Renewable, Biomass                 | heat and power co-generation, wood chips, 6667 kW               |
| Renewable, Biogas                  | heat and power co-generation, biogas, gas engine                |



Flow diagram
------------


How to use it?
--------------

```python

    import brightway2 as bw
    from premise import NewDatabase
    from datapackage import Package
    
    
    fp = r"https://raw.githubusercontent.com/romainsacchi/RTE_scenarios/main/datapackage.json"
    ep2050 = Package(fp)
    
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
                ep2050, # <-- list datapackages here
            ] 
        )
```

