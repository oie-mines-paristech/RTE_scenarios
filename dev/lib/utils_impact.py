from premise import *
from datapackage import Package
import bw2data
import os as os
import pandas as pd
import numpy as np
from .static_database_generation import *
from .static_transversal import *
from .static_impact import *
from lib.utils import save_xls



def ca_aggreg(mainfolder,selected_db_list,selected_impacts,curtailment_included,df_curtailment):
    """Aggregated contribution analysis"""

    ca_aggreg=[]
    ca_aggreg_bis=[]

    for impact_cat in selected_impacts:
        #change climate change premise name not to confuse with standard climate change
        if 'incl. H and bio CO2' in impact_cat[2]:
            impact_cat_name='climate change premise'
        else:
            impact_cat_name=impact_cat[1]

    # A. Disaggregate electricity into 4 (direct prod, storage, import, curtailment)
        list_df_ca_aggreg=[]
        unit_impact = bw2data.Method(impact_cat).metadata["unit"]
        unit=unit_impact
        
        act_name_list=[
            "market for electricity, high voltage, FE2050",
            "market for electricity, from direct French production, FE2050",
            "market for electricity, from storage, FE2050",
            "market for electricity, from import, FE2050",
        ]
        
        for db in selected_db_list:  
            df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','impact','act','amount (kWh)','contribution to impact','unit'])    
            
            #Amount of direct electricity / storage / imports
            act=db.search("market for electricity, high voltage, FE2050")[0]
            excs=[exc for exc in act.exchanges()]
            amount_direct_elec=0
            amount_storage=0
            amount_import=0
            for exc in excs:
                if exc.input["name"] in direct_elec_prod_act_names:
                    amount_direct_elec = exc["amount"]+amount_direct_elec
                if exc.input["name"] in storage_act_names:
                    amount_storage = exc["amount"]+amount_storage
                if exc.input["name"] in import_act_name:
                    amount_import = exc["amount"]+amount_import
            
            # Safety Check that direct_elec_prod_act_names + storage_act_names+import_act_name covers al the activities
                if exc.input["name"] not in direct_elec_prod_act_names + storage_act_names+import_act_name+[act["name"]]:
                    if "transmission" not in exc.input["name"] and "Ozone" not in exc.input["name"] and "Dinitrogen"not in exc.input["name"]:
                        print("warning: exchange", exc.input["name"], "forgotten")
                    
            #Impact of each mix (total, from direct production, from storage, from import)
            for act_name in act_name_list:
                act=db.search(act_name)[0]
                #Amount
                if act["name"]=="market for electricity, high voltage, FE2050":
                    amount=1
                if act["name"]=="market for electricity, from direct French production, FE2050":
                    amount=amount_direct_elec
                if act["name"]=="market for electricity, from storage, FE2050":
                    amount=amount_storage
                if act["name"]=="market for electricity, from import, FE2050":
                    amount=amount_import
                    
                #Impact
                lca = act.lca(method=impact_cat, amount=amount)
                score = lca.score            
        
                    #change of unit for climate change
                if unit_impact == "kg CO2-Eq":
                    score=1000*score
                    unit="g CO2-Eq"       
                    
                #export to dataframe
                df.loc[len(df.index)] = [db.name,db.model, db.SSP,db.RCP,db.FR_scenario,db.year,db.warning,impact_cat_name,act["name"],amount,score,unit]

            #Absolute impact/kWh
            df["impact/kWh (absolute)"]=df["contribution to impact"]/df["amount (kWh)"]
            
            #Add curtailment
            if curtailment_included:
                act=db.search("market for electricity production, direct production, high voltage, FE2050")[0]
                amount=df_curtailment[df_curtailment['FR_scenario']==db.FR_scenario][db.year].squeeze()
                lca = act.lca(method=impact_cat, amount=1)
                direct_elec_score=lca.score
                curtailment_score=direct_elec_score*amount
                if unit_impact == "kg CO2-Eq":
                    direct_elec_score=1000*direct_elec_score
                    curtailment_score=1000*curtailment_score
                df.loc[len(df.index)] = [db.name,db.model, db.SSP,db.RCP,db.FR_scenario,db.year,db.warning,impact_cat_name,'curtailment',amount,curtailment_score,unit,direct_elec_score]
                #add curtailment score to market score
                market_score=df.loc[df['act']=='market for electricity, high voltage, FE2050','contribution to impact']    
                df.loc[df['act']=='market for electricity, high voltage, FE2050','contribution to impact']=market_score+curtailment_score
                df.loc[df['act']=='market for electricity, high voltage, FE2050','impact/kWh (absolute)']=market_score+curtailment_score
                
            
            #Calculation for mix
            total = df['contribution to impact'].iloc[1:].sum()       
        
            #Add columns to calculate the contribution to impacts (percentage)
            df['percentage contribution']=df['contribution to impact']/total*100

            #add label and color for plots
            if curtailment_included:
                df['label']=['supply mix','directly supplied from domestic generation','released from storage','from imports','curtailment']
                df['color']=['grey','deepskyblue','royalblue','midnightblue','black']
            else: 
                df['label']=['supply mix','directly supplied from domestic generation','released from storage','supplied from imports','curtailment']
                df['color']=['grey','deepskyblue','royalblue','midnightblue']                
            #Safety check
            if (df["amount (kWh)"].iloc[1:3].sum()-1)>1e-4:
                print("error in amount")
                print(df["amount (kWh)"].iloc[1:3].sum())
            if (total-df['contribution to impact'].iloc[0])>1e-4:
                print("error in impact")
                print(total,df['contribution to impact'].iloc[0])
        
            list_df_ca_aggreg.append(df)

        list_df_ca_aggreg_bis=[]

    # B. Disaggregate electricity from storage and imports into 2
        for df in list_df_ca_aggreg:
        
            #insert empty lines
            df2=df.copy()
            for n in [3,4,6,7]:
                df2 = pd.DataFrame(np.insert(df2.values, n, values =len(df.columns)*[np.NaN],axis=0))
            df2.columns = df.columns
        
            #add information on the empty lines
            df2.loc[3,'act']="electricity from storage replaced by production mix"
            df2.loc[3,'label']="electricity from storage replaced by production mix"
            df2.loc[3,'color']="royalblue"
        
            df2.loc[4,'act']='storage losses and infrastructure'
            df2.loc[4,'label']='storage losses and infrastructure'
            df2.loc[4,'color']="royalblue"
        
            df2.loc[6,'act']="electricity from imports replaced by production mix"
            df2.loc[6,'label']="electricity from imports replaced by production mix"
            df2.loc[6,'color']="midnightblue"
        
            df2.loc[7,'act']='differential impacts due to imports'
            df2.loc[7,'label']='differential impacts due to imports'
            df2.loc[7,'color']="midnightblue"
            
            #Impact of production mix
            impact_mix_prod=df2.loc[(df2['act']=="market for electricity, from direct French production, FE2050"),'impact/kWh (absolute)'].values.tolist()[0]
            
            #divide in 2 the impact of electricity from storage
            amount_sto=df2.loc[(df2['act']=="market for electricity, from storage, FE2050"),'amount (kWh)'].values.tolist()[0]
            impact_sto=df2.loc[(df2['act']=="market for electricity, from storage, FE2050"),'contribution to impact'].values.tolist()[0]
            #"electricity from storage replaced by production mix" = amount storage * impact mix direct prod and import (in our case mix prod and import = mix direct prod)
            df2.loc[(df2['act']=="electricity from storage replaced by production mix"),'contribution to impact']=impact_mix_prod*amount_sto
            #storage infra and losses impact is the rest
            df2.loc[(df2['act']=='storage losses and infrastructure'),'contribution to impact']=impact_sto-impact_mix_prod*amount_sto
        
            #divide in 2 the impacts of imports
            b1=df2.loc[(df2['act']=="market for electricity, from import, FE2050"),'amount (kWh)'].values.tolist()[0]
            c1=df2.loc[(df2['act']=="market for electricity, from import, FE2050"),'contribution to impact'].values.tolist()[0]
            #imports
            df2.loc[(df2['act']=="electricity from imports replaced by production mix"),'contribution to impact']=impact_mix_prod*b1
            #differential impact is the rest
            df2.loc[(df2['act']=='differential impacts due to imports'),'contribution to impact']=c1-impact_mix_prod*b1
        
            #recalculate percentage contribution
            df2['percentage contribution']=df2['contribution to impact']/df2.loc[0,'contribution to impact']
        
            #Calculate contributuion to difference 
            df2['contribution to difference']=df2['amount (kWh)']*(df2['impact/kWh (absolute)']-impact_mix_prod)
            for act in ['storage losses and infrastructure','differential impacts due to imports','curtailment']:
                df2.loc[(df2['act']==act),'contribution to difference']=df2.loc[(df2['act']==act),'contribution to impact']
            
            df2['contribution to difference %']=df2['contribution to difference']/impact_mix_prod*100
        
            #Safety check
            test=df2['contribution to difference'].iloc[3]+df2['contribution to difference'].iloc[4]-df2['contribution to difference'].iloc[0]
            if test > 1e-5:
                write('warning total does not equal supply mix')
        
            #Put unit on all lines
            df2['unit']=df2.loc[0,'unit']
            
            #Add df2 to the list
            list_df_ca_aggreg_bis.append(df2)

        #Save the list for each impact category   
        ca_aggreg.append(list_df_ca_aggreg)
        ca_aggreg_bis.append(list_df_ca_aggreg_bis)
        
        #Save a file / a list for each impact category
        newpath= DATA_OUT_FOLDER+'/'+mainfolder+'/'+impact_cat_name.replace(":","").replace("/"," ")
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        save_xls(newpath+'/'+'list_df_ca_aggreg.xlsx',list_df_ca_aggreg)
        save_xls(newpath+'/'+'list_df_ca_aggreg_bis.xlsx',list_df_ca_aggreg_bis)
    return[ca_aggreg,ca_aggreg_bis]


def ca_disaggreg_storage(mainfolder,selected_db_list,selected_impacts):

    #grid_losses
    grid_losses=0.03109
    grid_losses_factor=1/(1-grid_losses)
    grid_losses_factor

    ca_storage=[]

    for impact_cat in selected_impacts:  
        #change climate change premise name not to confuse with standard climate change
        if 'incl. H and bio CO2' in impact_cat[2]:
            impact_cat_name='climate change premise'
        else:
            impact_cat_name=impact_cat[1]

        list_df_storage_efficiency= []
        list_df_storage=[]
        unit_impact = bw2data.Method(impact_cat).metadata["unit"]
        unit=unit_impact
        
        zero=0.0
        columns = ['db_name','model','SSP','RCP','FR scenario','year','warning','act',
                'amount in elec market (kWh)','efficiency (%)','storage losses (kWh)',
                'impact 1kWh prod elec from storage','impact storage losses','impact storage infra',
                'impact 1 kWh elec consumption market','impact 1 kWh elec market from prod','impact 1 kWh pure production','impact 1 kWh elec market from storage','unit']
        
        for db in selected_db_list:

    #A. Storage efficiencies
            
            df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning','act','efficiency (%)','storage losses (kWh)'])

            #french electricity mix
            french_mix=db.search("market for electricity, high voltage, FE2050")[0]        
            excs_elec=[exc for exc in french_mix.exchanges()]
        
            #Storage elec activities with elec input at level 1
            for act_storage_name in ["electricity production, from vehicle-to-grid, FE2050",'electricity production, hydro, pumped storage, FE2050',"electricity supply, high voltage, from vanadium-redox flow battery system, FE2050"]:
                act_storage=db.search(act_storage_name)[0]
    
                #calculate efficiency with input elec mix
                excs=[exc for exc in act_storage.exchanges()]
                for exc in excs:
                    if exc.input["name"]==storage_input_mix_name:
                        #print(act_storage_name)
                        #print("{:.2f}".format(exc.amount))
                        #print("{:.1f}".format(1/exc.amount*100))
                        df.loc[len(df.index)] = [db.name,db.model, db.SSP, db.RCP, db.FR_scenario,db.year,db.warning,act_storage_name,(1/exc.amount*100),(exc.amount-1)]
            #Specific case h2 storage
            for act_storage_name in ["electricity production, from hydrogen, with gas turbine, for grid-balancing, FE2050"]:
                #calculate efficiency by multiplying flows at different levels
                #level 1
                act1=db.search("hydrogen production, gaseous, 30 bar, from PEM electrolysis, from grid electricity, domestic, FE2050")[0] 
                excs=[exc for exc in act1.exchanges()]
                for exc in excs:
                    if exc.input["name"]==storage_input_mix_name:
                        a=exc.amount
                        #print("{:.2f}".format(exc.amount))
                #Level 2
                act2=db.search("hydrogen storage, for grid-balancing, FE2050")[0]    
                excs=[exc for exc in act2.exchanges()]
                for exc in excs:
                    if exc.input["name"]==act1["name"]:
                        b=exc.amount
                        #print("{:.2f}".format(exc.amount))
                #Level 3
                act_storage=db.search(act_storage_name)[0]    
                excs=[exc for exc in act_storage.exchanges()]
                for exc in excs:
                    if exc.input["name"]==act2["name"]:
                        c=exc.amount
                        #print("{:.2f}".format(exc.amount))
                        #print(act_storage_name)
                        #print("{:.1f}".format(1/(a*b*c)*100))
                        df.loc[len(df.index)] = [db.name,db.model, db.SSP, db.RCP, db.FR_scenario,db.year,db.warning,act_storage_name,1/(a*b*c)*100,a*b*c-1]

            df_storage_efficiency=df
            list_df_storage_efficiency.append(df_storage_efficiency)

    #B. Impact storage
            df=pd.DataFrame([],columns=columns)    
        
            #French electricity market
            act_market_elec_name="market for electricity, high voltage, FE2050"
            act_market_elec= db.search(act_market_elec_name)[0]
            lca = act_market_elec.lca(method=impact_cat, amount=1)
            score_elec=lca.score #Total : Electricity from storage score
            excs_market_elec=[exc for exc in act_market_elec.exchanges()]
        
            #Consumption mix from direct production
            act_market_prod_elec= db.search('market for electricity, from direct French production, FE2050')[0]
            lca = act_market_prod_elec.lca(method=impact_cat, amount=1)
            score_prod_market=lca.score 
        
            #Production mix from direct production
            act_pure_prod_elec= db.search('market for electricity production, direct production, high voltage, FE2050')[0]
            lca = act_pure_prod_elec.lca(method=impact_cat, amount=1)
            score_prod_pure=lca.score
        
            #Consumption mix from storage
            act_market_stor_elec= db.search('market for electricity, from storage, FE2050')[0]
            lca = act_market_stor_elec.lca(method=impact_cat, amount=1)
            score_storage_market=lca.score 
            
            #Infra grid impact
            #act_grid_infra= db.search("high voltage grid, per kWh, FE2050")[0]
            #lca = act_grid_infra.lca(method=impact_cat, amount=1)
            #score_grid_infra=lca.score #Total : Electricity from storage score 
        
            if unit_impact == "kg CO2-Eq":
                    score_elec=1000*score_elec
                    score_prod_market=1000*score_prod_market
                    score_prod_pure=1000*score_prod_pure    
                    #score_grid_infra=1000*score_grid_infra
                    unit="g CO2-Eq"
        
            for diki in list_dict_storage:
                #storage activity to study
                act_storage_name=diki['act_storage_name']
                act_storage=[act for act in db if act["name"]==act_storage_name][0]
                #Calculate impact
                lca = act_storage.lca(method=impact_cat, amount=1)
                total_elec_from_storage=lca.score
        
                if unit_impact == "kg CO2-Eq":
                    total_elec_from_storage =1000*total_elec_from_storage
                    
                #Infra > input elec=0
                #change_input_storage_mix([db],"empty activity")
                #lca = act_storage.lca(method=impact_cat, amount=1)
                #storage_infra=lca.score
        
                #Back
                #change_input_storage_mix([db],new_input_name)
        
                #Conversion for climate change impact
                #if unit_impact == "kg CO2-Eq":
                    #total_elec_from_storage =1000*total_elec_from_storage
                    #storage_infra=1000*storage_infra
        
                #Storage amount in electricity mix
                exc_amount=0
                for exc in excs_market_elec:
                    if exc.input["name"]==act_storage_name:
                        exc_amount=exc["amount"]
        
        
                #Store scores in a dataframe
                df.loc[len(df.index)] = [db.name,db.model, db.SSP, db.RCP, db.FR_scenario,db.year,db.warning,act_storage_name,
                                        exc_amount,zero,zero,
                                        total_elec_from_storage,zero,zero,
                                        score_elec,score_prod_market,score_prod_pure, score_storage_market,unit] 
        
        
            #transversal calculations
            for diki in list_dict_storage:
                act_storage_name=diki['act_storage_name']
                df.loc[df['act'] == act_storage_name, 'efficiency (%)']=df_storage_efficiency.loc[df_storage_efficiency['act'] == act_storage_name, 'efficiency (%)'].values
                df.loc[df['act'] == act_storage_name, 'storage losses (kWh)']=df_storage_efficiency.loc[df_storage_efficiency['act'] == act_storage_name, 'storage losses (kWh)'].values
            df['impact storage losses']=df['storage losses (kWh)']*df['impact 1 kWh pure production']
            df['impact storage infra']=df['impact 1kWh prod elec from storage']-(1+df['storage losses (kWh)'])*df['impact 1 kWh pure production']
        
            #Repartition of storage technology in electricity mix
            df['% amount in elec market'] = df['amount in elec market (kWh)'] / df['amount in elec market (kWh)'].sum()
            #weight the imacts based on the repartition in the electricity market
            df['Helper'] = df["% amount in elec market"] * df['efficiency (%)']    
            df.loc[0,'efficiency storage mix'] = df['Helper'].sum()    
            df['Helper'] = df["% amount in elec market"] * df['storage losses (kWh)']    
            df.loc[0,'storage losses in storage mix'] = df['Helper'].sum()    
        
            #Impact in consumption mix. Correction by grid losses factor
            df['Helper'] = df["% amount in elec market"] * df['impact storage losses']*grid_losses_factor
            df.loc[0,'impact storage losses in supply mix'] = df['Helper'].sum()    
            
            df['Helper'] = df["% amount in elec market"] * df['impact storage infra']*grid_losses_factor 
            df.loc[0,'impact storage infra in supply mix'] = df['Helper'].sum()    
                #For each db in the selected list add the dataframe to the list of dataframes
            
            list_df_storage.append(df)        
        #save    
        ca_storage.append(list_df_storage)
        newpath= DATA_OUT_FOLDER+'/'+mainfolder+'/'+impact_cat_name.replace(":","").replace("/"," ")
        save_xls(newpath+'/'+'impact_storage.xlsx',list_df_storage)

    return([ca_storage,list_df_storage_efficiency])
    

def ca_disaggreg_ter(mainfolder,selected_db_list,selected_impacts,ca_aggreg_bis,ca_storage):
    ca_aggreg_ter=[]
    n_impact=0

    #For each impact cat
    for list_df_ca_aggreg_bis in ca_aggreg_bis:
        list_df_storage=ca_storage[n_impact]
        n_impact=n_impact+1

        n_scenario=0
        list_df_ca_aggreg_ter=[]

        #For each scenario
        for df in list_df_ca_aggreg_bis:
            #Extract storage related data from df and df_sto
            df_sto=list_df_storage[n_scenario]
            impact_mix_prod=df_sto.loc[0,'impact 1 kWh elec market from prod']
            losses_sto=df_sto.loc[0,'impact storage losses in supply mix']
            infra_sto= df_sto.loc[0,'impact storage infra in supply mix']
            amount_sto=df.loc[(df['act']=="market for electricity, from storage, FE2050"),'amount (kWh)'].values.tolist()[0]
            n_scenario=n_scenario+1
            #losses_sto*amount_sto
            #infra_sto*amount_sto
        
            #insert empty lines
            df2=df.copy()
            for newrow in [5,6]:
                df2 = pd.DataFrame(np.insert(df2.values, newrow, values =len(df.columns)*[np.NaN],axis=0))
            df2.columns = df.columns
        
            #Label and act of new lines
            df2.loc[5,'label']='storage losses'
            df2.loc[5,'act']='storage losses' 
            df2.loc[5,'color']='royalblue'
        
            df2.loc[6,'label']='storage infrastructure'
            df2.loc[6,'act']='storage infrastructure'
            df2.loc[6,'color']='royalblue'
        
            
            #Calculate contribution to difference
            df2.loc[df2['label'] == 'storage losses','contribution to difference']=losses_sto*amount_sto
            df2.loc[df2['label'] == 'storage losses','contribution to impact']=losses_sto*amount_sto
        
            df2.loc[df2['label'] == 'storage infrastructure','contribution to difference']=infra_sto*amount_sto
            df2.loc[df2['label'] == 'storage infrastructure','contribution to impact']=infra_sto*amount_sto
        
            impact_mix_prod=df2.loc[(df2['act']=="market for electricity, from direct French production, FE2050"),'impact/kWh (absolute)'].values.tolist()[0]
            df2['contribution to difference %']=df2['contribution to difference']/impact_mix_prod
        
            #safety check
            test=df2['contribution to difference'].iloc[5]+df2['contribution to difference'].iloc[6]-df2['contribution to difference'].iloc[4]
            if test > 1e-5:
                print('warning total does not equal supply mix for')
                print(df2['impact'].tolist()[0])
                print(df2['FR scenario'].tolist()[0])
                print(test)
        
            #recalculate percentage contribution
            df2['percentage contribution']=df2['contribution to impact']/df2.loc[0,'contribution to impact']
        
            #Put unit on all lines
            df2['unit']=df2.loc[0,'unit']
        
            list_df_ca_aggreg_ter.append(df2)
        
        ca_aggreg_ter.append(list_df_ca_aggreg_ter)
        impact_name=list_df_ca_aggreg_bis[0]['impact'].tolist()[0]
        newpath=DATA_OUT_FOLDER+'/'+mainfolder+'/'+impact_name.replace(":","").replace("/"," ")
        save_xls(newpath+'/'+'list_df_ca_aggregg_ter.xlsx',list_df_ca_aggreg_ter)

    return(ca_aggreg_ter)
    
