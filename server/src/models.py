import os
import json
from syslog import syslog
import pandas as pd
import json

PATH_DATA_FOLDER = '../data/'
PATH_DATA_FILE_EXAMPLE_CSV = 'example.csv'
PATH_DATA_FILE_EXAMPLE_JSON = 'example.json'


class Model:
    def __init__(self):
        self.DATA_FOLDER = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), PATH_DATA_FOLDER)

        # load the CSV dataset
        try:
            self.csv_data = pd.read_csv(os.path.join(
                self.DATA_FOLDER, PATH_DATA_FILE_EXAMPLE_CSV))
        except:
            print(f'could not open: {PATH_DATA_FILE_EXAMPLE_CSV}')

        # load the JSON dataset
        try:
            with open(os.path.join(self.DATA_FOLDER, PATH_DATA_FILE_EXAMPLE_JSON), 'r') as file:
                self.json_data = json.load(file)
        except Exception as e:
            print(f'could not open: {PATH_DATA_FILE_EXAMPLE_JSON} because {e}')

    """
    to_json is frequently used in outputing pandas DataFrame
    The 'records' and 'index' orients are typically helpful in rendering front-end components.
    force_ascii is set to False to support diverse character sets.
    """
    # The following methods all target netflix dataset

    def get_example_data(self):
      return json.dumps(self.json_data, ensure_ascii=False)
        # return self.json_data.to_json(orient='records', force_ascii=False)

    def modify_example_data(self, value):
      # modify the data
      self.json_data = value
      return json.dumps(self.json_data, ensure_ascii=False)
