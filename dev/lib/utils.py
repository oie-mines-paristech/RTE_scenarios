from premise import *
from datapackage import Package
import bw2data
import os as os
import pandas as pd
from .static_database_generation import *
from .static_transversal import *

#import bw2io
#import lca_algebraic as agb

def init():
    for FOLDER in FOLDERS: 
        if not os.path.exists(FOLDER):
            os.makedirs(FOLDER)

    bw2data.projects.set_current(NAME_BW_PROJECT)


def save_xls(xls_path,list_dfs):
    """Export a list of dataframes in an excel file with multiple excel sheets"""
    with pd.ExcelWriter(xls_path) as writer:
        for n, df in enumerate(list_dfs):
            #df.to_excel(writer,'sheet%s' % n)
            df.to_excel(writer,sheet_name=str(n))


def import_xls_list_df(xls_path):
    """Export excel file with multiple excel sheets in a list of dataframe"""
    #xl = pd.ExcelFile(xls_path)
    #n=len(xl.sheet_names)
    dict_df= pd.read_excel(xls_path, sheet_name=None,index_col=0)
    list_df=list(dict_df.values())
    return list_df

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


def generate_premise_dbs(list_scenarios):
    """Generate a series of databases with year x IAM scenario x FR scenario """
    fp = "../datapackage.json"
    rte = Package(fp)
    for scenarios in list_scenarios:
        ndb = NewDatabase(
                        scenarios = scenarios,        
                        source_db=ecoinvent_db_name,
                        source_version=eco_version,
                        key='tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo=',
                        biosphere_name=ecoinvent_bio_db_name,
                        #use_multiprocessing=True
                        )
        ndb.update()
        ndb.write_db_to_brightway()



def generate_premise_db_list():
    """ Generate a list of databases generated with premise"""
    #generate a list of names of generated databases by premise
    premise_db_name_list=[]
    for db_name in list(bw2data.databases): #bw2data.databases.keys():
        if "ei_cutoff" in db_name:
            premise_db_name_list.append(db_name)
    #generate a list of generated databases by premise
    premise_db_list=[]
    for db_name in premise_db_name_list:
        premise_db_list.append(bw2data.Database(db_name))

    if len(list(bw2data.databases))-len(premise_db_list)!=2:
       print('error when generating list of premise database')
       print(len(list(bw2data.databases)),list(bw2data.databases))
       print(len(premise_db_list))
    
    return premise_db_list

def tag_premise_dbs(premise_db_list, folder):
    """tag the database with corresponding year, model, SSP, RCP and FR scenario"""
    for db in premise_db_list:
        for year in year_list:
            if year in db.name:
                db.year=int(year)
        for model in model_list:
            if model in db.name:
                db.model=model
        for SSP in SSP_list:
            if SSP in db.name:
                db.SSP=SSP
        for RCP in RCP_list:
            if RCP in db.name:
                db.RCP=RCP
        db.FR_scenario='None'
        for FR_scenario in FR_scenario_list:
            if FR_scenario in db.name:
                db.FR_scenario=FR_scenario    
        #Warning
        db.warning=' '
        #Correction of RCP
        if db.RCP=='-M_':
            db.RCP='M'
        if db.RCP=='-L':
            db.RCP='L'
        if db.RCP=='-H':
            db.RCP='H'

    #Each database can be sorted with these tags
    df=pd.DataFrame([],columns=['db_name','model','SSP','RCP','FR scenario','year','warning'])
    for db in premise_db_list:
        df.loc[len(df.index)] = [db.name,db.model,db.SSP,db.RCP,db.FR_scenario,db.year, db.warning]
    save_xls(folder+'/'+'premise_db_list.xlsx',[df])

    return(df)


def create_empty_act(selected_db_list):
    for db in selected_db_list:
        empty_act=agb.newActivity(
            db.name,
            "empty activity",
            "unit",
        )

storage_input_mix_name="input electricity mix for storage, FE2050"

def change_input_storage_mix(selected_db_list,new_input_name):
    for db in selected_db_list:
        input_storage_mix=db.search(storage_input_mix_name)[0]
        new_input_storage_mix=db.search(new_input_name)[0]
        excs=[exc for exc in input_storage_mix.exchanges()]
        for exc in excs:
            if exc["type"]=="technosphere":
                exc.input=new_input_storage_mix
                exc.save()