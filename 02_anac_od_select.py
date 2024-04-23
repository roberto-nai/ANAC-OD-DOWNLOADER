# 02_anac_od_select.py

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
data_dir = str(yaml_config["DATA_DIR"])
data_file_schema = dict(yaml_config["ANAC_OD_SCHEMA"])
data_file_cols = list(yaml_config["ANAC_OD_SCHEMA"])
csv_sep = str(yaml_config["CSV_SEP"])
pa_reg_dir = str(yaml_config["PA_REG_DIR"])
pa_reg_file = str(yaml_config["PA_REG_FILE"])
pa_reg_columns = list(yaml_config["PA_REG_SCHEMA"])
pa_reg_dict = dict(yaml_config["PA_REG_SCHEMA"])
anac_regions_json = str(yaml_config["ANAC_REGIONS_JSON"])

# INPUT
data_file = str(yaml_config["ANAC_OD_FILE"])
year_start = int(yaml_config["YEAR_START_FILTER"])
year_end = int(yaml_config["YEAR_END_FILTER"]) 
year_list_filter = list(range(year_start, year_end+1)) # year_end+1 to keep year_end inclusive

# OUTPUT
anac_stats_dir = str(yaml_config["ANAC_STATS_DIR"])
anac_stats_file = str(yaml_config["ANAC_STATS_FILE"])

### FUNCTIONS ###
def read_anac_data(path: str, col_list: list[str], col_type: dict[str, str], csv_sep: str = ",") -> pd.DataFrame:
    """
    Reads data from a CSV file into a pandas DataFrame with specified columns and data types.

    Parameters:
        path (str): the file path to the CSV file to be read.
        columns (list[str]): a list of column names to be read from the CSV file.
        dtype (dict[str, str]): a dictionary mapping column names to their respective data types.
        sep (str, optional): the delimiter string used in the CSV file. Defaults to ','.

    Returns:
        pd.DataFrame: a pandas DataFrame containing the data read from the CSV file.
    """

    df = pd.read_csv(path, usecols=col_list, dtype=col_type, sep=csv_sep)
    df = df.drop_duplicates()
    print_details(df, "Initial ANAC Open Data")
    return df

def read_pa_data(path: str, col_list: list[str], col_type: dict[str, str]):
    """
    Reads an XLSX file and converts specific columns to 'object' type.

    Parameters:    
        path (str): the file path to the XLSX file to be read.
        col_list (list[str]): a list of column names to be read from the CSV file.
        col_type (dict[str, str]): a dictionary mapping column names to their respective data types.    

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
        print(f"Years available: {df['anno_pubblicazione'].unique()}\n")
    if "sezione_regionale" in df.columns:
        print(f"Regions available: {df['sezione_regionale'].unique()}\n")
    # PA
    if "Descr_Tipologia_SIOPE" in df.columns:
        print(f"PA types in Registry: {df['Descr_Tipologia_SIOPE'].unique()}\n")
    if "pa_type" in df.columns:
        print(f"PA types (final): {df['pa_type'].unique()}\n")
    print(f"{title} dataframe preview:")
    print(df.head(), "\n\n")
    print(df.columns, "\n\n")

def filter_data(df: pd.DataFrame, year_list: list[int], region: str) -> pd.DataFrame:
    """
    Filters a pandas DataFrame based on a list of years and a specific region, and performs
    some specific cleaning tasks on the 'sezione_regionale', 'settore', and 'cod_cpv' columns.

    Parameters:
        df (pd.DataFrame): the DataFrame to be filtered.
        year_list (List[int]): a list of years to filter the DataFrame by.
        region (str): the region to filter the DataFrame by.

    Returns:
        pd.DataFrame: A filtered and cleaned pandas DataFrame.
    """

    # Filter
    filtered_df = df[(df["anno_pubblicazione"].isin(year_list)) & (df["sezione_regionale"] == region)].copy()
    # Clean
    filtered_df['sezione_regionale'] = filtered_df['sezione_regionale'].str.replace("SEZIONE REGIONALE ", "", regex=False)
    filtered_df['settore'] = filtered_df['settore'].str.replace("SETTORI ", "", regex=False)
    # CPV division
    filtered_df['cpv_division'] = filtered_df['cod_cpv'].apply(lambda x: x[:2] if pd.notnull(x) and x != '' else '')
    # Order
    filtered_df = filtered_df.sort_values(by=['anno_pubblicazione', 'cig'])
    # Print
    print_details(filtered_df, "Selected ANAC Open Data")
    return filtered_df

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
    print()

    print(">> Reading ANAC regions JSON")
    print()
    print("File:", anac_regions_json)
    regions_list = json_to_list_dict(anac_regions_json)
    regions_list_len = len(regions_list)
    print("Regions found in JSON:", regions_list_len)
    print(regions_list)
    print()

    print(">> Reading initial ANAC Open Data")
    print()
    path_anac_od = Path(data_dir) / data_file
    df_anac = read_anac_data(path_anac_od, data_file_cols, data_file_schema, csv_sep)
    print()

    print(">> Preparing output directories")
    check_and_create_directory(anac_stats_dir)

    i = 0
    
    list_stats = []

    for region in regions_list:
        
        i+=1
        
        print(f"[{i} / {regions_list_len}]\n")

        print("Region tuple:", region)
        print()

        # Get region for file name and ANAC filter
        region_output = region[0]
        region_filter = region[1]

        print(">> Filtering data from ANAC Open Data")
        print("Region:", region_filter)
        df_filtered = filter_data(df_anac, year_list_filter, region_filter)
        print()

        print(">> Reading PA Registry")
        print()
        path_pa_registry = Path(pa_reg_dir) / pa_reg_file
        df_pa_registry = read_pa_data(path_pa_registry, pa_reg_columns, pa_reg_dict)
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

        print(">> Saving data filtered")
        data_file_out = str(yaml_config["ANAC_FILE_FILTERED"]).replace("YS",str(year_start)).replace("YE", str(year_end)).replace("R",region_output)
        print_details(merged_data, "Final dataframe")
        path_out = Path(data_dir) / data_file_out
        save_data(merged_data, path_out, csv_sep)
        print()

        # Stats onf dataframe by region
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