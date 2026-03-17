import pandas as pd

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
