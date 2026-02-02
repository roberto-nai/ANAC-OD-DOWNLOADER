# 01_anac_opendata.py

"""
Script name: 01_anac_od_download.py
Author: R. Nai
Creation date: 10/01/2024
Last modified: 01/03/2024 (added class SSLAdapter)
Description: application to download public notices from the ANAC website
https://dati.anticorruzione.it/opendata/download/dataset/cig-AAAA/filesystem/cig_csv_YYYY_MM.zip
(ex. https://dati.anticorruzione.it/opendata/download/dataset/cig-2021/filesystem/cig_csv_2021_01.zip)

[2025-06-12]: updated with logging functionalities.
"""

### IMPORT ###
import logging
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
anac_other_dataset_names = yaml_config.get("ANAC_OTHER_DATASET_NAMES", [])

MERGE_DO = False  # whether to merge the CSV files after download and unzip or not

# OUTPUT
merge_file = f"bando_cig_{year_start}-{year_end}.csv" # final file with all the tenders following years
anac_download_dir = str(yaml_config["ANAC_DOWNLOAD_DIR"]) 
data_dir = str(yaml_config["OD_ANAC_DIR"])

### FUNCTIONS ###

def url_generate(year_start: int, year_end: int, list_months: list, url_base: list, key: str, day: str = "01") -> list:
    """
    Generates a list of URLs based on a range of years, a list of months, and a base URL.

    Parameters:
        year_start (int): the starting year of the range (inclusive).
        year_end (int): the ending year of the range (inclusive). It assumes `year_end` >= `year_start`.
        list_months (list): a list of strings representing months, where each month is expected to be in a format that matches the expected URL pattern (e.g., '01' for January).
        url_base (str): The base URL to which the year and month will be appended. The base URL should not end with a slash.
        key (str): the dataset name key to be used in URL construction (e.g., "cig" or other dataset names).
        day (str): the day to be used in URL construction (default: "01").
        
    Returns:
    - list: a list of strings, where each string is a fully constructed URL according to the described pattern.
    """

    list_url = []
    for year in range(year_start, year_end + 1):  # year_end+1 to keep year_end inclusive
        year_str = f"{year:04}"
        for month in list_months:
            month_str = f"{int(month):02}"
            day_str = f"{int(day):02}"
            for pattern in url_base:
                url = (
                    pattern
                    .replace("{YYYY}", year_str)
                    .replace("{MM}", month_str)
                    .replace("{DD}", day_str)
                )
                if "{dataset-name}" in url:
                    url = url.replace("{dataset-name}", key)
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
        return 0

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

def print_list_urls(list_urls: list) -> None:
    """
    Prints each URL in the provided list of URLs.

    Parameters:
        list_urls (list): A list of URLs to be printed.
    Returns:
        None
    """
    print("List of URLs:")
    for i, url in enumerate(list_urls, start=1):
        print(f"{i}) {url}")

### MAIN ###

def main() -> None:
    """
    Main script function.
    Parameters: None
    Returns: None
    """

    # Logging setup
    log_file = f"{Path(__file__).stem}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    print()
    print("*** PROGRAM START ***")
    print()
    
    logger.info("PROGRAM START")

    start_time = datetime.now().replace(microsecond=0)
    print("Start process: " + str(start_time))
    logger.info(f"Start process: {start_time}")
    print()

    print(">> Generating output directories")
    check_and_create_directory(anac_download_dir)
    check_and_create_directory(data_dir)
    print()
    
    print(">> Generating dynamic URLs")
    url_base = read_urls_from_json(url_dynamic_file, "cig")
    list_urls_din = url_generate(year_start, year_end, list_months, url_base, "cig")
    list_urls_din_len = len(list_urls_din)
    print("URLs generated (num):", list_urls_din_len)
    print_list_urls(list_urls_din) # debug
    print()

    print(">> Generating dynamic URLs (others)")
    url_base_others = read_urls_from_json(url_dynamic_file, "others")
    list_urls_others_din = []
    for dataset_name in anac_other_dataset_names:
        list_urls_others_din.extend(
            url_generate(year_start, year_end, list_months, url_base_others, dataset_name)
        )
    list_urls_others_din_len = len(list_urls_others_din)
    print("URLs generated (num):", list_urls_others_din_len)
    print_list_urls(list_urls_others_din) # debug
    print()

    print(">> Generating static URLs")
    list_urls_sta = read_urls_from_json(url_statics_file, "others")
    list_urls_sta_len = len(list_urls_sta)
    print("URLs generated (num):", list_urls_sta_len)
    print_list_urls(list_urls_sta) # debug
    print()

    print(">> Merging dynamic and static URLs lists")
    list_urls_all = list_urls_din + list_urls_others_din + list_urls_sta
    list_urls_all_len = len(list_urls_all)
    print("URLs generated (all):", list_urls_all_len)
    # print(list_urls_all) # debug
    print()

    print(">> Downloading from URLs")
    print("Download directory:", anac_download_dir)
    logger.info(f"Starting download from {list_urls_all_len} URLs")
    dic_result = url_download(list_urls_all, anac_download_dir)
    print("Download results")
    print(dic_result)
    logger.info(f"Download completed - Results: {dic_result}")
    print()

    print(">> Unzipping files")
    unzipped_files = url_unzip(anac_download_dir)
    print("Unzipped files:", len(unzipped_files))
    print()

    if MERGE_DO == False:
        print(">> Merging skipped as per configuration (MERGE_DO = False).")
    else:
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
    logger.info(f"End process: {end_time}")
    logger.info(f"Time to finish: {delta_time}")
    print()

    print()
    print("*** PROGRAM END ***")
    logger.info("PROGRAM END")
    print()

if __name__ == "__main__":
    main()