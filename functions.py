import csv
import os
import logging
from rsLogger.logger import Logger
import pandas as pd


# Starts logger for file
current_path = os.getcwd()
folder_name = os.path.basename(current_path)
my_log = Logger().get_logger(__name__)
my_file_logger = Logger()
if os.environ.get('DEBUG') == 'True':
    logging.root.setLevel(logging.DEBUG)
else:
    logging.root.setLevel(logging.INFO)



def load_csv(path_to_csv: str) -> list:
    """
    Load a csv file into a a pandas dataframe
    :param path_to_csv: str
    :return: list
    """
    try:
        data = pd.read_csv(path_to_csv)
        return data
    except Exception as e:
        my_log.error(f'Error loading csv file: {e}')
        return None
    
def array_to_csv(array_data: list, save_path: str) -> None:
    """
    Save a list of dictionaries into a csv file
    :param array_data: list
    :param save_path: str
    :return: None
    """
    with open(save_path, 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=array_data[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(array_data)
        
def sort_by_id(data: list) -> list:
    """
    Sort data by id
    :param data: list
    :return: list
    """

    