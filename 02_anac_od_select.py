# 02_anac_od_select.py

"""
Script name: 01_istat_bdap_od_download.py
Author: R. Nai
Creation date: 10/01/2024
Last modified: 01/03/2024 (added class SSLAdapter)
Description: selects data from the general dataset by filtering them on the basis of ANAC_OD_SELECT and ANAC_OD_REGION. It then applies a join to the PA data obtained from ANAC and Open BDAP.
"""

### IMPORT ###
import pandas as pd
import csv
from datetime import datetime
from pathlib import Path

### LOCAL IMPORT ###
from config import config_reader
from utility_manager.utilities import json_to_list_dict, check_and_create_directory

### GLOBALS ###
yaml_config = config_reader.config_read_yaml("config.yml", "config")
csv_sep = str(yaml_config["CSV_SEP"])
anac_odfilter_json = str(yaml_config["ANAC_OD_SELECT"]) # filter configuration
anac_regions_json = str(yaml_config["ANAC_OD_REGION"]) # filter configuration
year_start = int(yaml_config["YEAR_START_DOWNLOAD"])
year_end = int(yaml_config["YEAR_END_DOWNLOAD"]) 

# Registry
pa_reg_dir = str(yaml_config["OD_BDAP_DIR"])
pa_reg_file = str(yaml_config["OD_BDAP_FILE"])
pa_reg_columns = list(yaml_config["PA_REG_SCHEMA"])
pa_reg_dict = dict(yaml_config["PA_REG_SCHEMA"])

# INPUT
data_file = f"bando_cig_{year_start}-{year_end}.csv" # starting file with all the tenders following years
data_dir = str(yaml_config["OD_ANAC_DIR"])

# OUTPUT
anac_stats_dir = str(yaml_config["ANAC_STATS_DIR"])
anac_stats_file = str(yaml_config["ANAC_STATS_FILE"])
list_stats = []

### FUNCTIONS ###
def read_anac_data(path: str, col_list: list, col_type:dict, csv_sep: str = ";") -> pd.DataFrame:
    """
    Reads data from a CSV file into a pandas DataFrame with specified columns and data types.

    Parameters:
        path (str): the file path to the CSV file to be read.
        columns (list): a list of column names to be read from the CSV file.
        sep (str): the delimiter string used in the CSV file. Defaults to ';'.

    Returns:
        pd.DataFrame: a pandas DataFrame containing the data read from the CSV file.
    """

    df = pd.read_csv(path, usecols=col_list, dtype=col_type, sep=csv_sep, low_memory=False)
    df = df.drop_duplicates()
    return df

def read_pa_data(path: str, col_list: list, col_type: dict):
    """
    Reads an XLSX file and converts specific columns to 'object' type.

    Parameters:    
        path (str): the file path to the XLSX file to be read.
        col_list (list): a list of column names to be read from the CSV file.
        col_type (dict): a dictionary mapping column names to their respective data types.    

    Returns:
        pandas.DataFrame: The DataFrame with specified columns converted to 'object' type.
    """

    df = pd.read_excel(path, usecols=col_list, dtype=col_type)
    df = df.drop_duplicates()
    print_details(df, "Initial PA registry")

    # Return the DataFrame with specified columns converted to 'object' type
    return df

def print_details(df: pd.DataFrame, title: str) -> None:
    """
    Prints details of a pandas DataFrame, including its size and a preview of its contents,
    along with any available information on publication years and regions if present in the DataFrame.

    Parameters:
        df (pd.DataFrame): the DataFrame whose details are to be printed.
        title (str): a title for the printed output to describe the context of the DataFrame.

    Returns:
        None
    """

    print(f">> {title}")
    print(f"Dataframe size: {df.shape}\n")
    # ANAC
    if "anno_pubblicazione" in df.columns:
        print(f"anno_pubblicazione distinct values: {df['anno_pubblicazione'].unique()}\n")
    if "sezione_regionale" in df.columns:
        print(f"sezione_regionale distinct values: {df['sezione_regionale'].unique()}\n")
    if "oggetto_principale_contratto" in df.columns:
        print(f"oggetto_principale_contratto distinct values: {df['oggetto_principale_contratto'].unique()}\n")
    if "settore" in df.columns:
        print(f"settore distinct values: {df['settore'].unique()}\n")
    print(f"{title} dataframe preview:")
    print(df.head(), "\n\n")
    print(df.columns, "\n\n")
    print(df.dtypes, "\n\n")

def filter_data(df: pd.DataFrame, filter_list: list) -> pd.DataFrame:
    """
    Filters a pandas DataFrame based on a list of years and a specific region, and performs
    some specific cleaning tasks on the 'sezione_regionale', 'settore', and 'cod_cpv' columns.

    Parameters:
        df (pd.DataFrame): the DataFrame to be filtered.
        filter_list (lit[dict]): a list filters.

    Returns:
        pd.DataFrame: A filtered and cleaned pandas DataFrame.
    """

    # Filter

    for filter_data in filter_list:
        for key, key_value_list in filter_data.items():
            print(f"Key: {key}")
            print(f"Value: {key_value_list}")
            print()
            if key in df.columns:
                if len(key_value_list) > 0:
                    df = df[df[key].isin(key_value_list)]
    
    # filtered_df = df.copy()
    return df

def clean_data(df: pd.DataFrame,) -> pd.DataFrame:
    # Clean
    df['sezione_regionale'] = df['sezione_regionale'].str.replace("SEZIONE REGIONALE ", "", regex=False)
    df['settore'] = df['settore'].str.replace("SETTORI ", "", regex=False)
    # CPV division
    df['cpv_division'] = df['cod_cpv'].apply(lambda x: x[:2] if pd.notnull(x) and x != '' else '')
    # Order
    df = df.sort_values(by=['anno_pubblicazione', 'cig'])
    return df

def save_data(df: pd.DataFrame, path: str, sep: str = ",") -> None:
    """
    Saves a pandas DataFrame to a CSV file at the specified path, using the specified delimiter.

    Parameters:
        df (pd.DataFrame): the DataFrame to be saved.
        path (str): the file path where the CSV file will be saved.
        sep (str, optional): the delimiter string to be used in the CSV file. Defaults to ','.

    Returns:
        None
    """

    df.to_csv(path, sep=sep, index=False, quoting=csv.QUOTE_ALL)
    print(f"Data saved to: {path}\n\n")

def merge_dataframes(df1, df2, common_field_df1, common_field_df2, columns_to_drop=None):
    """
    Merge two dataframes based on common fields, rename the common field, and create a new column 'pa_type'.
    Then drops specified columns.

    Args:
        df1 (pandas.DataFrame): First DataFrame.
        df2 (pandas.DataFrame): Second DataFrame.
        common_field_df1 (str): Common field in the first DataFrame.
        common_field_df2 (str): Common field in the second DataFrame.
        columns_to_drop (list): List of column names to drop.

    Returns:
        pandas.DataFrame: Merged DataFrame with the new column 'pa_type' and specified columns dropped.
    """
    # Merge the dataframes based on the common fields
    merged_df = pd.merge(df1, df2, left_on=common_field_df1, right_on=common_field_df2, how='inner')

    # Rename the common field to 'cf_pa'
    merged_df.rename(columns={common_field_df1: 'cf_pa'}, inplace=True)

    # Create new column 'pa_type' based on 'Descr_Tipologia_SIOPE' or 'Descr_Tipologia_MIUR'
    merged_df['pa_type'] = merged_df['Descr_Tipologia_SIOPE'].fillna(merged_df['Descr_Tipologia_MIUR'])

    # Drop specified columns if provided
    if columns_to_drop:
        merged_df.drop(columns=columns_to_drop, inplace=True)

    return merged_df

def convert_columns_to_lowercase(df: pd.DataFrame, columns_to_modify:list) -> pd.DataFrame:
    """
    Converts the text of specified columns in a DataFrame to lowercase.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to operate on.
        columns_to_modify (list of str): List of the names of the columns to be converted to lowercase.

    Returns:
        pd.Dataframe
    """

    for col in columns_to_modify:
        if col in df.columns:  # Checks if the column exists in the DataFrame
            if columns_to_modify == 'sezione_regionale':
                df[col] = df[col].str.capitalize()
            else:
                df[col] = df[col].str.lower()
        else:
            print(f"The column '{col}' does not exist in the DataFrame.")

    return df

### MAIN ###

def main():
    print()
    print("*** PROGRAM START ***")
    print()

    start_time = datetime.now().replace(microsecond=0)
    print("Start process: " + str(start_time))
    print()
    print()

    print(">> Generating output directories")
    check_and_create_directory(data_dir)
    check_and_create_directory(anac_stats_dir)
    print()

    print(">> Reading ANAC filter JSON")
    print("File:", anac_odfilter_json)
    filter_list = json_to_list_dict(anac_odfilter_json)
    filter_list_len = len(filter_list)
    print("Filters found in JSON:", filter_list_len)
    print(filter_list)
    print()

    print(">> Reading ANAC regions JSON")
    print("File:", anac_regions_json)
    regions_list = json_to_list_dict(anac_regions_json)
    regions_list_len = len(regions_list)
    print("Regions found in JSON:", regions_list_len)
    print(regions_list)
    print()

    print(">> Reading initial ANAC Open Data")
    path_anac_od = Path(data_dir) / data_file
    schema_cols = ["cig","cig_accordo_quadro","numero_gara","oggetto_gara","importo_complessivo_gara","n_lotti_componenti","oggetto_lotto","importo_lotto","oggetto_principale_contratto","stato","settore","luogo_istat","provincia","data_pubblicazione","data_scadenza_offerta","cod_tipo_scelta_contraente","tipo_scelta_contraente","cod_modalita_realizzazione","modalita_realizzazione","codice_ausa","cf_amministrazione_appaltante","denominazione_amministrazione_appaltante","sezione_regionale","id_centro_costo","denominazione_centro_costo","anno_pubblicazione","mese_pubblicazione","cod_cpv","descrizione_cpv","flag_prevalente"]
    schema_type = {"cig":object,"cig_accordo_quadro":object, "anno_pubblicazione":object}
    df_anac = read_anac_data(path_anac_od, schema_cols, schema_type, csv_sep)
    print_details(df_anac, "Initial ANAC Open Data")
    print()
    
    print(">> Filtering (1 - generic)")
    df_filtered_1 = filter_data(df_anac, filter_list)
    print()
    # Print
    print_details(df_filtered_1, "Filtered ANAC Open Data (1 - generic)")
    # Save
    print(">> Saving data filtered (1 - generic) without BDAP")
    data_file_out = f"bando_cig_{year_start}-{year_end}_filtered.csv"
    path_out = Path(data_dir) / data_file_out
    print("Path:", path_out)
    save_data(df_filtered_1, path_out, csv_sep)
    print()

    # Loading BDAP
    print(">> Reading BDAP")
    path_pa_registry = Path(pa_reg_dir) / pa_reg_file
    df_pa_registry = read_pa_data(path_pa_registry, pa_reg_columns, pa_reg_dict)
    print()
    
    # Merge with BDAP
    print(">> Merging ANAC Open Data and BDAP")
    columns_to_drop = ['Codice_Tipologia_MIUR', 'Codice_Tipologia_SIOPE', 'Denominazione', 'Descr_Tipologia_MIUR', 'Descr_Tipologia_SIOPE', 'CF']
    merged_data = merge_dataframes(df_filtered_1, df_pa_registry, 'cf_amministrazione_appaltante', 'CF', columns_to_drop)
    merged_data = merged_data.drop_duplicates()
    merged_data_len = len(merged_data)
    print("done!")
    print()

    # Clean
    df_filtered_1_clean = clean_data(merged_data)
    # Print
    print_details(df_filtered_1, "Filtered ANAC Open Data with BDAP (1 - generic)")

    # Stats on dataframe
    dic_stat = {"region":"all", "size":len(df_filtered_1_clean)}
    list_stats.append(dic_stat)

    # Save
    print(">> Saving data filtered with BDAP (1 - generic)")
    data_file_out = f"bando_cig_{year_start}-{year_end}_filtered_bdap.csv"
    path_out = Path(data_dir) / data_file_out
    print("Path:", path_out)
    save_data(df_filtered_1_clean, path_out, csv_sep)
    print()

    print(">> Filtering (2 - by region)")

    i = 0

    for region_dic in regions_list:
        
        i+=1
        
        print(f"[{i} / {regions_list_len}]\n")

        print("Region dict:", region_dic)
        print()

        # Get region for file name and ANAC filter
        region_key = next(iter(region_dic))
        region_filter = region_dic[region_key]
        region_output = region_key
        region_filter_list = [{"sezione_regionale": [region_filter]}] # the filter is a list of dict
    

        print(">> Filtering data from ANAC Open Data")
        print("Region (filter):", region_filter)
        print("Region (output):", region_output)
        df_filtered = filter_data(df_anac, region_filter_list)
        print()


        # Merge df_filtered with df_pa_registry and drop columns not needed
        print(">> Merging ANAC Open Data and PA Registry")
        columns_to_drop = ['Codice_Tipologia_MIUR', 'Codice_Tipologia_SIOPE', 'Denominazione', 'Descr_Tipologia_MIUR', 'Descr_Tipologia_SIOPE', 'CF']
        merged_data = merge_dataframes(df_filtered, df_pa_registry, 'cf_amministrazione_appaltante', 'CF', columns_to_drop)
        merged_data = merged_data.drop_duplicates()
        merged_data_len = len(merged_data)
        print()

        print(">> Cecking NaN columns")
        df_nan = merged_data.isna().sum()
        print(df_nan)
        print()

        print(">> Columns to lowercase")
        col_low = ['oggetto_principale_contratto', 'settore', 'sezione_regionale', 'pa_type']
        merged_data = convert_columns_to_lowercase(merged_data,col_low)
        print()

        # Clean
        df_filtered_2_clean = clean_data(merged_data)

        print(">> Saving data filtered (2 - by region)")
        data_file_out = f"bando_cig_{year_start}-{year_end}_{region_output}.csv"
        print_details(df_filtered_2_clean, "Final dataframe")
        path_out = Path(data_dir) / data_file_out
        save_data(df_filtered_2_clean, path_out, csv_sep)
        print()

        # Stats on dataframe by region
        dic_stat = {"region":region_output, "size":merged_data_len}
        list_stats.append(dic_stat)

    print(">> Saving data stats")
    df_stats = pd.DataFrame.from_records(list_stats)
    path_stats = Path(anac_stats_dir) / anac_stats_file
    df_stats.to_csv(path_stats, sep=csv_sep, index=False)
    print("Stats path:", path_stats)
    print()

    end_time = datetime.now().replace(microsecond=0)
    delta_time = end_time - start_time

    print("End process:", end_time)
    print("Time to finish:", delta_time)
    print()

    print()
    print("*** PROGRAM END ***")
    print()

if __name__ == "__main__":
    main()