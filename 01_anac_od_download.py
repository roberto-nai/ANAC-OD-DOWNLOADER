# 01_anac_opendata.py

"""
Script name: 01_anac_od_download.py
Author: R. Nai
Creation date: 10/01/2024
Last modified: 01/03/2024 (added class SSLAdapter)
Description: application to download public notices from the ANAC website
https://dati.anticorruzione.it/opendata/download/dataset/cig-AAAA/filesystem/cig_csv_YYYY_MM.zip
(ex. https://dati.anticorruzione.it/opendata/download/dataset/cig-2021/filesystem/cig_csv_2021_01.zip)
"""

### IMPORT ###
from datetime import datetime
from pathlib import Path

### LOCAL IMPORT ###
from config import config_reader
from utility_manager.utilities import check_and_create_directory, url_download, url_unzip, read_urls_from_json

### GLOBALS ###
yaml_config = config_reader.config_read_yaml("config.yml", "config")
list_months = [f"{i:02}" for i in range(1, 13)]
# url_base = str(yaml_config["DOWNLOAD_URL"])
year_start = int(yaml_config["YEAR_START_DOWNLOAD"])
year_end = int(yaml_config["YEAR_END_DOWNLOAD"]) 
url_statics_file = str(yaml_config["ANAC_STATIC_URLS_JSON"])
url_dynamic_file = str(yaml_config["ANAC_DYNAMIC_URLS_JSON"])
cig_prefix = str(yaml_config["CIG_PREFIX"])

# OUTPUT
merge_file = f"bando_cig_{year_start}-{year_end}.csv" # final file with all the tenders following years
anac_download_dir = str(yaml_config["ANAC_DOWNLOAD_DIR"]) 
data_dir = str(yaml_config["OD_ANAC_DIR"])

### FUNCTIONS ###

def url_generate(year_start:int, year_end:int, list_months:list, url_base:str) -> list:
    """
    Generates a list of URLs based on a range of years, a list of months, and a base URL.

    Parameters:
        year_start (int): the starting year of the range (inclusive).
        year_end (int): the ending year of the range (inclusive). It assumes `year_end` >= `year_start`.
        list_months (list): a list of strings representing months, where each month is expected to be in a format that matches the expected URL pattern (e.g., '01' for January).
        url_base (str): The base URL to which the year and month will be appended. The base URL should not end with a slash.

    Returns:
    - list: a list of strings, where each string is a fully constructed URL according to the described pattern.
    """

    list_url = []
    for year in range(year_start, year_end+1): # year_end+1 to keep year_end inclusive
        for month in list_months:
            url = f"{url_base[0]}{year}/filesystem/cig_csv_{year}_{month}.zip"
            # print(url)
            list_url.append(url)
    return list_url

def merge_csv_files(source_dir: str, output_dir:str, prefix_name:str, output_file: str) -> int:
    """
    Merges all CSV files with a specific prefix name in the specified directory into a single CSV file (useful for "bando CIG" table).
    
    Parameters:
        source_dir (str): the path to the directory containing the CSV files to be merged.
        output_dir (str): the path to the output CSV directory where the merged content will be stored.
        prefix_name (str): the prefix of files to be merged.
        output_file (str): the path to the output CSV file where the merged content will be stored.

    Returns:
        int: number of lines in the merged CSV file
    """

    source_path = Path(source_dir)
    output_path = Path(output_dir) / output_file

    # Ensure the source directory exists
    if not source_path.is_dir():
        print(f"WARNING! Source directory {source_dir} does not exist.")
        return

    # Open the output file in write mode
    with output_path.open(mode='w') as outfile:
        for csv_file in source_path.glob(f'{prefix_name}*.csv'):
            with csv_file.open(mode='r') as infile:
                # Read the content of the current CSV file and write it to the output file
                outfile.write(infile.read())
            print(f"Merged: {csv_file}")

    print(f"All CSV files in '{source_dir}' with file name prefix '{prefix_name}' have been merged into file '{output_file}' in '{output_path}'.\n")

    # Count the lines in the merged CSV file

    with open(output_path, 'r') as file:
        lines = sum(1 for line in file)

    return lines

### MAIN ###

def main() -> None:
    """
    Main script function.
    Parameters: None
    Returns: None
    """

    print()
    print("*** PROGRAM START ***")
    print()

    start_time = datetime.now().replace(microsecond=0)
    print("Start process: " + str(start_time))
    print()

    print(">> Generating output directories")
    check_and_create_directory(anac_download_dir)
    check_and_create_directory(data_dir)
    print()
    
    print(">> Generating dinamic URLs")
    url_base = read_urls_from_json(url_dynamic_file)
    list_urls_din = url_generate(year_start, year_end, list_months, url_base)
    list_urls_len = len(list_urls_din)
    print("URLs generated (num):", list_urls_len)
    # print(list_urls_din) # debug
    print()

    print(">> Generating static URLs")
    list_urls_sta = read_urls_from_json(url_statics_file)
    list_urls_sta_len = len(list_urls_sta)
    print("URLs generated (num):", list_urls_sta_len)
    # print(list_urls_sta) # debug
    print()

    print(">> Merging dynamic and static URLs lists")
    list_urls_all = list_urls_din + list_urls_sta
    list_urls_all_len = len(list_urls_all)
    print("URLs generated:", list_urls_all_len)
    # print(list_urls_all) # debug
    print()

    print(">> Downloading from URLs")
    print("Download directory:", anac_download_dir)
    dic_result = url_download(list_urls_all, anac_download_dir)
    print("Download results")
    print(dic_result)
    print()

    print(">> Unzipping files")
    unzipped_files = url_unzip(anac_download_dir)
    print("Unzipped files:", len(unzipped_files))
    print()

    print(">> Merging files")
    print("Prefix for merging:", cig_prefix)
    lines_csv = merge_csv_files(anac_download_dir, data_dir, cig_prefix, merge_file)
    print(f"Lines in the merged CSV file '{merge_file}' (with duplicates): {lines_csv}")
    print()

    # end
    end_time = datetime.now().replace(microsecond=0)
    delta_time = end_time - start_time

    print()
    print("End process:", end_time)
    print("Time to finish:", delta_time)
    print()

    print()
    print("*** PROGRAM END ***")
    print()

if __name__ == "__main__":
    main()