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
import requests
import zipfile
import json

### LOCAL IMPORT ###
from config import config_reader
from ssl_adapter import SSLAdapter
from utility_manager.utilities import check_and_create_directory

### GLOBALS ###
yaml_config = config_reader.config_read_yaml("config.yml", "config")
list_months = [f"{i:02}" for i in range(1, 13)]
# url_base = str(yaml_config["DOWNLOAD_URL"])
year_start = int(yaml_config["YEAR_START_DOWNLOAD"])
year_end = int(yaml_config["YEAR_END_DOWNLOAD"]) 
data_dir = str(yaml_config["DATA_DIR"])
url_statics_file = str(yaml_config["ANAC_STATIC_URLS_JSON"])
url_dynamic_file = str(yaml_config["ANAC_DYNAMIC_URLS_JSON"])
cig_prefix = str(yaml_config["CIG_PREFIX"])

# OUTPUT
merge_file = f"bando_cig_{year_start}-{year_end}.csv" # final file with all the tenders following years
download_dir = str(yaml_config["DOWNLOAD_DIR"])
data_dir = str(yaml_config["DATA_DIR"])

### FUNCTIONS ###

def read_urls_from_json(json_file:str) -> list:
    """
    Reads a JSON file containing a list of URLs and returns the list.

    Parameters:
        json_file (str): The path to the JSON file containing the list of URLs.

    Returns:
        list: A list of URLs read from the JSON file.
    """

    list_url = []

    try:
        with open(json_file, 'r') as fp:
            list_url = json.load(fp)
    except FileNotFoundError:
        print("Error: The file was not found.")
    except json.JSONDecodeError:
        print("Error: The file is not a valid JSON.")

    return list_url

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
            url = f"{url_base}{year}/filesystem/cig_csv_{year}_{month}.zip"
            # print(url)
            list_url.append(url)
    return list_url

def url_download(list_urls:list, path_download:str) -> dict:
    """
    Downloads files from a list of URLs if they do not already exist in the specified directory. This function uses the 'requests' library for downloading and saving files.
    
    Parameters:
        url_list (list): a list of URLs of the files to be downloaded.
        path_download (str): the directory path where the files should be downloaded.

    Returns: 
        dict: a dictionary with download results
    """

    dic_result = {"download_ok": 0, "download_not_necessary":0, "download_error":0}

    s = requests.Session()
    s.mount('https://', SSLAdapter())

    list_urls_len = len(list_urls)
    
    i = 0

    for url in list_urls:

        i+=1

        print(f"[{i} / {list_urls_len}]")

        print(f"URL to be downloaded: {url}")
        
        file_name_zip = Path(url).name
        print(f"File to be downloaded: {file_name_zip}")
        
        file_name_csv = file_name_zip.replace('.zip', '.csv')
        print(f"File to be checked: {file_name_csv}")
        
        path_check = Path(path_download) / file_name_zip
        if path_check.exists():
            print(f"WARNING! File '{file_name_zip}' already downloaded\n")
            dic_result["download_not_necessary"]+=1
            continue
        try:
            print("Downloading file...")
            response = s.get(url)
            response.raise_for_status()  # Raises an HTTPError if the response was an error
            with open(Path(path_download) / file_name_zip, 'wb') as file:
                file.write(response.content)
            # command = "wget -P " + "./" + path_download + " " + url
            # os.system(command)
            print("OK! Download successful\n")
            dic_result["download_ok"]+=1
        except requests.RequestException as e:
            print(f"ERROR! Error downloading {url}: {e}\n")
            dic_result["download_error"]+=1
    return dic_result

def url_unzip(download_dir: str) -> int:
    """
    Unzips all the .zip files located in the specified download path.
    This function searches for all .zip files within the given directory, extracts their contents to the same directory, and uses Python's built-in zipfile module for the extraction process, providing a more secure and cross-platform approach compared to calling external unzip commands.    

    Parameters:
        download_dir (str): the path to the directory containing the .zip files.

    Returns:
        int: number of unzippped files.
    """

    download_path = Path(download_dir)
    unzipped_files = 0

    for file_path in download_path.glob("*.zip"):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(download_path)
        print(f"Unzipped: {file_path}")
        unzipped_files+=1

    return unzipped_files

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

    print(f"All CSV files in {source_dir} have been merged into '{output_file}'.\n")

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
    check_and_create_directory(download_dir)
    check_and_create_directory(data_dir)
    print()
    
    print(">> Generating dinamic URLs")
    url_base = read_urls_from_json(url_dynamic_file)
    list_urls_din = url_generate(year_start, year_end, list_months, url_base)
    list_urls_len = len(list_urls_din)
    print("URLs generated:", list_urls_len)
    print()

    print(">> Generating static URLs")
    list_urls_sta = read_urls_from_json(url_statics_file)
    list_urls_sta_len = len(list_urls_sta)
    print("URLs generated:", list_urls_sta_len)
    print()

    print(">> Merging dynamic and static URLs")
    list_urls_all = list_urls_din + list_urls_sta
    list_urls_all_len = len(list_urls_all)
    print("URLs generated:", list_urls_all_len)
    print()

    print(">> Downloading from URLs")
    print("Download directory:", download_dir)
    dic_result = url_download(list_urls_all, download_dir)
    print("Download results")
    print(dic_result)
    print()

    print(">> Unzipping files")
    unzipped_files = url_unzip(download_dir)
    print("Unzipped files:", unzipped_files)
    print()

    print(">> Merging files")
    lines_csv = merge_csv_files(download_dir, download_dir, cig_prefix, merge_file)
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