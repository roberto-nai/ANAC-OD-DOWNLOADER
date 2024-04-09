import json
from pathlib import Path

def json_to_list_dict(json_file: str) -> list:
    """
    Extracts and sorts key-value pairs from a JSON file alphabetically by the keys.

    Args:
        json_file (str): The path to the JSON file.

    Returns:
        list: A list of tuples containing tuples of key-value pairs extracted and sorted from the JSON file.
    """
    # Load JSON data from file
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # Extract key-value pairs into a list and sort alphabetically by keys
    sorted_key_value_pairs = sorted(data.items(), key=lambda x: x[0])

    return sorted_key_value_pairs


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
        print("The directory '{}' already exists: {}".format(dir_name, path_directory))
    else:
        path_directory.mkdir(parents=True, exist_ok=True)
        print("The directory '{}' has been created successfully: {}".format(dir_name, path_directory))
        
    print()