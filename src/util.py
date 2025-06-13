import json
from src.logger import setup_logger

log = setup_logger(__name__)

def read_json_file(file_path):
    """
    Parse the JSON content of a file.
    Args:
        file_path (str): Path to file containing JSON content.
    Returns:
        Parsed JSON data.
    Raises:
        FileNotFoundError: An exception throw when a file does not exit in the provided file path
    """
    try:
        with open(file_path, encoding="utf-8") as json_file:
            json_data = json.load(json_file)
            return json_data
    except FileNotFoundError as fnfe:
        error_msg = f"File not found {fnfe}"
        log.error(error_msg)
        raise FileNotFoundError(error_msg) from fnfe

def get_str_from_teams(team_ids):
    """ This function is used to convert the team ids to a string
    Args:
        team_ids: list of team ids
    Returns: string representation of a list
    """
    if team_ids:
        return "[" + ", ".join([f'"{id}"' for id in team_ids]) + "]"
    return "[]"