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
    'treatment of municipal solid waste, municipal incineration',
    "electricity production, wave energy converter",
    
    "electricity production, natural gas, combined cycle power plant",
    "electricity production, oil",
    "electricity production, hard coal",
    ]

storage_act_names=[
    "electricity production, hydro, pumped storage, FE2050",
    "electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050",
    "electricity production, from vehicle-to-grid, FE2050",
    "electricity supply, high voltage, from vanadium-redox flow battery system, FE2050",
    ]

import_act_name=["market group for electricity, high voltage"]

losses_act_names=["market for electricity, high voltage, FE2050"]

fluctuating_renew={
    "electricity production, photovoltaic",
    "electricity production, wind, 1-3MW turbine, onshore",
    "electricity production, wind, 1-3MW turbine, offshore",
    }

transmission_act_names=[
    "transmission network construction, electricity, high voltage direct current aerial line",
    "transmission network construction, electricity, high voltage direct current land cable",
    "transmission network construction, electricity, high voltage direct current subsea cable",
]

#Labels of each subcategory
dict_act_subcategories = {
    'direct electricity production in France':direct_elec_prod_act_names,
    'electricity production from flexibilities': storage_act_names,
    'imports':import_act_name,
    'losses':losses_act_names,
    'network':transmission_act_names
}


list_dict_storage=[
    {
    'act_storage_name':'electricity production, hydro, pumped storage, FE2050',
    'act_where_elec_is_stored_name':'electricity production, hydro, pumped storage, FE2050',
    #'act_elec_stored_name':"market for electricity, high voltage, FE2050"
     },
    {
    'act_storage_name':'electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050',
    'act_where_elec_is_stored_name':'hydrogen production, gaseous, 30 bar, from PEM electrolysis, from grid electricity, domestic, FE2050',
    #'act_elec_stored_name':"market for electricity, high voltage, FE2050"
    },    
    {
    'act_storage_name':'electricity production, from vehicle-to-grid, FE2050',
    'act_where_elec_is_stored_name':'electricity production, from vehicle-to-grid, FE2050',
    #'act_elec_stored_name':"market for electricity, high voltage, FE2050"
     },
    {
    'act_storage_name':'electricity supply, high voltage, from vanadium-redox flow battery system, FE2050',
    'act_where_elec_is_stored_name':'electricity supply, high voltage, from vanadium-redox flow battery system, FE2050',
    #'act_elec_stored_name':"market for electricity, high voltage, FE2050"
     }
]


#Colors for graphs

dict_color={
    "electricity production, nuclear, pressure water reactor":['gold','nuclear'],
    "electricity production, Evolutionary Power Reactor (EPR)":['gold','nuclear'],
    "electricity production, Small Modular Reactor (SMR)":['gold','nuclear'],
    "electricity production, hydro, run-of-river":['dodgerblue','hydro'],
    "electricity production, hydro, reservoir, alpine region":['dodgerblue','hydro'],
    "electricity production, photovoltaic":['coral','photovoltaic'],
    "electricity production, wind, 1-3MW turbine, onshore":['aquamarine','onshore wind'],
    "electricity production, wind, 1-3MW turbine, offshore":['mediumaquamarine','offshore wind'],
    "heat and power co-generation, wood chips, 6667 kW":['chartreuse','biomass and waste'],
    "treatment of municipal solid waste, municipal incineration":['chartreuse','biomass and waste'],
        
    "electricity production, natural gas, combined cycle power plant":['darkslategrey','gas'],
    "electricity production, oil":['black','oil and coal'],
    "electricity production, hard coal":['black','oil and coal'],
    
    "electricity production, wave energy converter":['blue','wave'],    
    
    "electricity production, hydro, pumped storage, FE2050":['royalblue','electricity from storage'], #'rebeccapurple'
    "electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050":['royalblue','electricity from storage'],
    "electricity production, from vehicle-to-grid, FE2050":['royalblue','electricity from storage'],
    "electricity supply, high voltage, from vanadium-redox flow battery system, FE2050":['royalblue','electricity from storage'],
    
    "market group for electricity, high voltage":['midnightblue','imports'], #magenta
    "market for electricity production, direct production, high voltage, FE2050":['midnightblue','imports'],

    "market for electricity, high voltage, FE2050":['rebeccapurple','losses'],
    "transmission network construction, electricity, high voltage direct current aerial line":['purple','grid infrastructure'],
    "transmission network construction, electricity, high voltage direct current land cable":['purple','grid infrastructure'],
    "transmission network construction, electricity, high voltage direct current subsea cable":['purple','grid infrastructure'],
    "Dinitrogen monoxide('air',)": 	['violet','grid direct emissions'],
    "Ozone('air',)":['violet','grid direct emissions'],
     }  


dict_color_mix={
    "electricity production, nuclear, pressure water reactor":['gold','nuclear'],
    "electricity production, Evolutionary Power Reactor (EPR)":['gold','nuclear'],
    "electricity production, Small Modular Reactor (SMR)":['gold','nuclear'],
    "electricity production, hydro, run-of-river":['dodgerblue','hydro'],
    "electricity production, hydro, reservoir, alpine region":['dodgerblue','hydro'],
    "electricity production, photovoltaic":['coral','photovoltaic'],
    "electricity production, wind, 1-3MW turbine, onshore":['aquamarine','wind'],
    "electricity production, wind, 1-3MW turbine, offshore":['aquamarine','wind'],
    "heat and power co-generation, wood chips, 6667 kW":['grey','others'],
    "treatment of municipal solid waste, municipal incineration":['grey','others'],
        
    "electricity production, natural gas, combined cycle power plant":['darkslategrey','gas'],
    "electricity production, oil":['black','oil and coal'],
    "electricity production, hard coal":['black','oil and coal'],
    
    "electricity production, wave energy converter":['grey','others'],    
    
    "electricity production, hydro, pumped storage, FE2050":['pink','hydro pumped'], #'rebeccapurple'
    "electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050":['magenta','P-to-hydrogen-to-P'],
    "electricity production, from vehicle-to-grid, FE2050":['deeppink','electric vehicles'],
    "electricity supply, high voltage, from vanadium-redox flow battery system, FE2050":['purple','stationnary batteries'],
    
    "market group for electricity, high voltage":['midnightblue','imports'], #magenta
    "market for electricity production, direct production, high voltage, FE2050":['midnightblue','imports'],

    "market for electricity, high voltage, FE2050":['rebeccapurple','losses'],
    "transmission network construction, electricity, high voltage direct current aerial line":['purple','grid infrastructure'],
    "transmission network construction, electricity, high voltage direct current land cable":['purple','grid infrastructure'],
    "transmission network construction, electricity, high voltage direct current subsea cable":['purple','grid infrastructure'],
    "Dinitrogen monoxide('air',)": 	['violet','grid direct emissions'],
    "Ozone('air',)":['violet','grid direct emissions'],
     }  

dict_color_storage={
    'impact elec from storage mix':['tot','tot',None],
    'impact original elec in storage mix':['royalblue','1kWh of electricity if there was no storage','///'],
    'impact grid in storage mix':['maroon','additional transport in the electricity grid',None],
    'impact storage infra in storage mix':['red', 'storage infrastructure',None],
    'impact storage losses in storage mix':['lightsalmon','storage electricity losses',None],
    }