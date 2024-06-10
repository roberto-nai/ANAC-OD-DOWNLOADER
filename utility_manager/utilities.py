import json
from pathlib import Path
import requests
import zipfile
from ssl_adapter import SSLAdapter

def json_to_list_dict(json_file: str) -> list:
    """
    Extracts and sorts key-value pairs from a JSON file alphabetically by the keys.

    Args:
        json_file (str): The path to the JSON file.

    Returns:
        list: A list of dictionary containing key-value pairs extracted and sorted from the JSON file.
    """
    # Load JSON data from file
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # Extract key-value pairs into a list, sort alphabetically by keys and convert each tuple to a dictionary
    sorted_key_value_pairs = sorted(data.items(), key=lambda x: x[0])
    sorted_dictionaries = [{key: value} for key, value in sorted_key_value_pairs]
    
    return sorted_dictionaries

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

    # print(list_url) # debug

    return list_url

def check_and_create_directory(dir_name:str, dir_parent:str="") -> None:
    """
    Create a directory in its parent directory (optional)

    Parameters
    -----------------------
    dir_name: str,
        directory to be created
    dir_parent: str,
        parent directory in which to create the directory
    """

    path_directory = ""
    if dir_parent != "":
        path_directory = Path(dir_parent) / dir_name
    else:
        path_directory = Path(dir_name)
    if path_directory.exists() and path_directory.is_dir():
        print(f"The directory '{path_directory}' already exists")
    else:
        path_directory.mkdir(parents=True, exist_ok=True)
        print(f"The directory '{path_directory}' has been created successfully")

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
    list_file = [] # List of unzipped files

    for file_path in download_path.glob("*.zip"):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(download_path)
        list_file.append(file_path)
        print(f"Unzipped: {file_path}")
        unzipped_files+=1

    return list_file

def move_files(source_folder: str, file_extension: str, destination_folder: str) -> int:
    """
    Moves all files with a specified extension from a source folder and its subfolders to a destination folder.

    Parameters:
        source_folder (str): The folder from which to move the files.
        file_extension (str): The extension of the files to be moved (e.g., "csv").
        destination_folder (str): The folder to which the files will be moved.

    Returns:
        int: The number of files moved.
    """
    # Create Path objects for the source and destination folders
    source_path = Path(source_folder)
    destination_path = Path(destination_folder)
    
    # Initialise a counter for the number of files moved
    files_moved = 0

    # Iterate over all files in the source folder and its subfolders with the desired extension
    for file_path in source_path.rglob(f'*.{file_extension}'):
        # Construct the destination file path
        destination_file_path = destination_path / file_path.name
        # Move the file
        file_path.rename(destination_file_path)
        print(f"Moved {file_path.name} from {file_path.parent} to {destination_folder}")
        files_moved += 1

    return files_moved