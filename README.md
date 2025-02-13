# Premise + French prospective scenarios : Futurs énergétiques 2050 / RTE
Implementation of French prospective scenarios from RTE study "Futurs énergétiques 2050" into ecoinvent database with premise


What does this repository do ?
-----------

This is a repository containing the implementation of prospective scenarios for France into ecoinvent. 
The prospective scenarios are provided in the "Futurs énergétiques 2050" (also called "Energy pathways to 2050") study by the French Transmission System Operator - RTE.   
The scope of RTE prospective study is metropolitan France, from now to 2050, and covers in details the electricity mix sector and with less details the fuel & gas, and hydrogen sectors.
This repository creates market-specific activities in the LCA database ecoinvent for the following sectors in France:
* electricity
* hydrogen
* fuel & gas

The evolution at the world regional scale are modeled by coupling the French scenarios with a global scenario provided by an Integrated Assessment Model (IAM).

**Warning:**
* The modeled markets for hydrogen do not cover all uses of hydrogen, only material uses of hydrogen for the following industrial sectors : ammonia, steel, chemistry, diverse sectors, refinery). This model does not cover energetic, grid balancing and synthetic fuel uses of hydrogen.
* The proxy used to generate imports and exports electricity datasets probably artificially overestimates the imports in 2060. The electricity datasets for 2060 shall be used with caution. 



RTE prospective study 
------------------------

Prospective scenarios are extracted from the study : Futurs énergétiques 2050, RTE, 2021-2022\
[`Website`](https://www.rte-france.com/analyses-tendances-et-prospectives/bilan-previsionnel-2050-futurs-energetiques) \
[`Reports`](https://www.rte-france.com/analyses-tendances-et-prospectives/bilan-previsionnel-2050-futurs-energetiques#Lesdocuments) \
[`Data repository`](https://www.rte-france.com/analyses-tendances-et-prospectives/bilan-previsionnel-2050-futurs-energetiques#Lesdonnees)


RTE provides 3 demand scenarios : 
* reference
* extensive reindustrialisation (higher demand compared to reference scenario)
* sobriety (lower demand compared to reference scenario).

For each demand scenario, RTE provides 6 electricity production scenarios 
* M0, M1, M23 : that rely mostly on renewables development
* N1, N2, N03 : that rely both on renewables and nuclear development

It makes a total of 3 * 6 = 18 scenarios. 


How is the repository organized ?
-----------

This repository is meant to be used with the open-source python library [`premise`](https://github.com/polca/premise), using the [`user-defined scenario functionnality`](https://premise.readthedocs.io/en/latest/user_scenarios.html).
The data relating to the annual production volumes of different energy carriers 
(e.g. electricity, hydrogen) for each scenario 
have been formatted and organised in a data package defined by the Frictionless standards 
(Walsh and Pollock, 2022). This data package is read and interpreted by `premise`. 
We therefore store a number of scenarios in a single data package.

This datapackage contains four files necessary to the scenarios implementation into the ecoinvent LCA database: 

* A **datapackage.json** file, which provides the metadata for the data package (e.g. authors, scenario descriptions, list and locations of resources, etc.). 
* A **config.yaml** file which provides the correspondence between the scenario variables and the LCA datasets in the ecoinvent DB, as well as the additional "LCA datasets" when they are not available in the ecoinvent database. 
* A tabular data **scenario_data.csv** file containing the time series for each variable in the set of scenarios. 
* An optional Excel file **LCI-FE2050.xlsx** containing the LCA inventories of the additional "LCA datasets" for any technology not initially present in the ecoinvent database. 

Additionally, a pdf document called "supplementary information" presents the methodological choices that where made to build this model.


How to use this notebook ?
------------------
* 0. Prerequisites: ecoinvent licence
* 1. Install the environment as explained [`here`](https://github.com/polca/premise?tab=readme-ov-file#how-to-install-this-package).
  Use premise version => 2.2.6
* 2. Create a brightway project and load ecoinvent database in the project. It can be done using [`ecoinvent_interface`](https://github.com/brightway-lca/ecoinvent_interface).
* 3. Run the script for a chosen combination of Year x IAM model x IAM scenario x French scenario. Here is an example for two French scenarios combined with the same IAM scenario.

  ```python

    import brightway2 as bw
    from premise import *
    import bw2data
    import bw2io
    from datapackage import Package

    fp = r"datapackage.json"
    rte = Package(fp)

    #Choose the IAM model
    model_1="tiam-ucl"
    #Choose the world scenario
    world_scenario_1=SSP2-RCP45"
    #choose the Year
    year=2050
    #Choose the French scenario 
    fr_scenario_1="Reference - M0"
    fr_scenario_4="Reference - N03"
    
    scenarios = [
        {"model": model_1, "pathway":world_scenario_1, "year": year, "external scenarios": [{"scenario": fr_scenario_1, "data": rte}]},
        {"model": model_1, "pathway":world_scenario_1, "year": year, "external scenarios": [{"scenario": fr_scenario_4, "data": rte}]},
        ]
  
    ndb = NewDatabase(
        scenarios = scenarios,        
        source_db=ecoinvent_3_9_db_name,
        source_version="3.9.1",
        key= , #ask the key to Romain Sacchi
        )
  
    ndb.update()
  
    ndb.write_db_to_brightway()
  
    list(bw2data.databases)

  ```
  
A prospective version of ecoinvent is generated for each combination of : Year x IAM model x IAM scenario x French scenario.
The newly created market datasets are tagged with 'FE2050', for example : `market for electricity, high voltage, FE2050` (FR)


Ecoinvent database compatibility
--------------------------------
* ecoinvent 3.9.1 cut-off (main branch)
* ecoinvent 3.10 cut-off (ei310 branch)


IAM scenario compatibility
---------------------------
The user can couple each French scenario with a global scenario (IAM) provided by premise.\
The available IAM scenarios provided by premise can be explored [`here`](https://premisedash-6f5a0259c487.herokuapp.com/)\
The choice of IAM scenario is under the responsability of the user of this repository. However, the authors highlight the fact that the impact results highly depends on the IAM scenario chosen. The authors advice to couple the scenarios with RCP 4.5 scenarios or with scenarios whose temperature increase are similar to RCP 4.5 scenarios, as it is mentioned in RTE study that the scenarios are compatible with RCP4.5 scenarios.

List of French scenarios
--------------------------------
| FE2050 scenario                        |
|----------------------------------------|
| Extensive reindustrialization - M0     |
| Extensive reindustrialization - M1     |
| Extensive reindustrialization - M23    |
| Extensive reindustrialization - N03    |
| Extensive reindustrialization - N1     |
| Extensive reindustrialization - N2     |
| Reference - M0                         |
| Reference - M1                         |
| Reference - M23                        |
| Reference - N03                        |
| Reference - N1                         |
| Reference - N2                         |
| Sobriety - M0                          |
| Sobriety - M1                          |
| Sobriety - M23                         |
| Sobriety - N03                         |
| Sobriety - N1                          |
| Sobriety - N2                          |


Authors of this data package
----------------------------

* Joanna Schlesinger
* Romain Sacchi 
* Juliana Steinbach 
* Thomas Beaussier 
* Paula Perez-Lopez


Acknowledgements
----------------------------
We would like to thank RTE experts for providing datasets and explanations to understand scenarios and datasets.
We also would like to thank Guillaume Batot from IFPEN for fruitfull discussions regarding the modeling choices.


Funding
-------
This work is supported by the ADEME agency, in the context of
the [`HYSPI project`](https://www.psi.ch/en/ta/projects/hyspi). 









