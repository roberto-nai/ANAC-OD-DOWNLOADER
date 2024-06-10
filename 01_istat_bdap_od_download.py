# 01_istat_od_download.py

"""
Script name: 01_istat_od_download.py
Author: R. Nai
Creation date: 10/01/2024
Last modified: 01/03/2024 (added class SSLAdapter)
Description: application to download data from ISTAT website
"""

### IMPORT ###
from datetime import datetime

### LOCAL IMPORT ###
from config import config_reader
from utility_manager.utilities import check_and_create_directory, read_urls_from_json, url_download, url_unzip, move_files

### GLOBALS ###
yaml_config = config_reader.config_read_yaml("config.yml", "config")

# INPUT
istat_url_statics_file = str(yaml_config["ISTAT_STATIC_URLS_JSON"]) 
bdap_url_statics_file = str(yaml_config["BDAP_STATIC_URLS_JSON"]) 

# OUTPUT
istat_download_dir = str(yaml_config["ISTAT_DOWNLOAD_DIR"]) 
bdap_download_dir = str(yaml_config["BDAP_DOWNLOAD_DIR"]) 
istat_dir = str(yaml_config["OD_ISTAT_DIR"])
bdap_dir = str(yaml_config["OD_BDAP_DIR"])

### FUNCTIONS ###


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
    check_and_create_directory(istat_download_dir)
    check_and_create_directory(bdap_download_dir)
    check_and_create_directory(istat_dir)
    check_and_create_directory(bdap_dir)
    print()

    print(">> Generating static URLs - ISTAT")
    istat_list_urls_sta = read_urls_from_json(istat_url_statics_file)
    istat_list_urls_sta_len = len(istat_list_urls_sta)
    print("URLs generated (num):", istat_list_urls_sta_len)
    print(istat_list_urls_sta) # debug
    print()

    print(">> Generating static URLs - BDAP")
    bdap_list_urls_sta = read_urls_from_json(bdap_url_statics_file)
    bdap_list_urls_sta_len = len(bdap_list_urls_sta)
    print("URLs generated (num):", bdap_list_urls_sta_len)
    print(bdap_list_urls_sta) # debug
    print()

    print(">> Downloading from URLs - ISTAT")
    print("Download directory:", istat_download_dir)
    dic_result = url_download(istat_list_urls_sta, istat_download_dir)
    print("Download results")
    print(dic_result)
    print()

    print(">> Downloading from URLs - BDAP")
    print("Download directory:", bdap_download_dir)
    dic_result = url_download(bdap_list_urls_sta, bdap_download_dir)
    print("Download results")
    print(dic_result)
    print()

    print(">> Unzipping files")
    print("Directory:", istat_download_dir)
    unzipped_files = url_unzip(istat_download_dir)
    print(f"Unzipped files in '{istat_download_dir}': {len(unzipped_files)}")
    print("Directory:", bdap_download_dir)
    unzipped_files = url_unzip(bdap_download_dir)
    print(f"Unzipped files in '{bdap_download_dir}': {len(unzipped_files)}")
    # print(unzipped_files) # debug
    print()

    print(">> Moving files")
    filetype = "csv"
    num_files = move_files(istat_download_dir, filetype, istat_dir)
    print(f"Files with type '{filetype}' moved from {istat_download_dir} to {istat_dir}: {num_files}")
    num_files = move_files(bdap_download_dir, filetype, bdap_dir)
    print(f"Files with type '{filetype}' moved from {bdap_download_dir} to {bdap_dir}: {num_files}")
    filetype = "xlsx"
    num_files = move_files(istat_download_dir, filetype, istat_dir)
    print(f"Files with type '{filetype}' moved from {istat_download_dir} to {istat_dir}: {num_files}")
    num_files = move_files(bdap_download_dir, filetype, bdap_dir)
    print(f"Files with type '{filetype}' moved from {bdap_download_dir} to {bdap_dir}: {num_files}")
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