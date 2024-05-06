import json
from pathlib import Path

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