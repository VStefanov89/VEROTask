import pandas as pd
from numpy import nan
import requests


class Data:
    REQUEST_DATA_URL = "https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active"
    LOCAL_DATA = "vehicles.csv"

    def __init__(self):
        self.__merge_data()

    def __get_url_data(self):
        print("Start getting url data...")
        requested_data = requests.get(self.REQUEST_DATA_URL)
        json_data = requested_data.json()
        url_data = pd.DataFrame.from_dict(json_data)
        url_data.drop_duplicates()
        print("Url data is collected")
        return url_data

    def __get_local_data(self):
        print("Start getting local data...")
        local_data = pd.read_csv(self.LOCAL_DATA, delimiter=";")
        local_data.drop_duplicates()
        print("Local data is collected")
        return local_data

    def __merge_data(self):
        data = pd.merge(self.__get_url_data(), self.__get_local_data(), how="outer", on="kurzname")
        print("Start merging url data and local data and make data manupulations...")
        data = data.replace(r'^\s*$', None, regex=True)
        data = data.replace({nan: None})

        for row in range(len(data.index)):
            if data.gruppe_x[row] is None:
                if data.gruppe_y[row] is not None:
                    data.gruppe_x[row] = data.gruppe_y[row]

            if data.langtext_x[row] is None:
                if data.langtext_y[row] is not None:
                    data.langtext_x[row] = data.langtext_y[row]

            if data.info_x[row] is None:
                if data.info_y[row] is not None:
                    data.info_x[row] = data.info_y[row]

            if data.lagerort_x[row] is None:
                if data.lagerort_y[row] is not None:
                    data.lagerort_x[row] = data.lagerort_y[row]

            if data.labelIds_x[row] is None:
                if data.labelIds_y[row] is not None:
                    data.labelIds_x[row] = data.labelIds_y[row]

        data.drop(['gruppe_y', 'langtext_y', 'info_y', 'lagerort_y', 'labelIds_y'], inplace=True, axis=1)
        data.rename(columns={'gruppe_x': 'gruppe',
                              'langtext_x': 'langtext',
                              'info_x': 'info',
                              'lagerort_x': 'lagerort',
                              'labelIds_x': 'labelIds'}, inplace=True)

        data = data[data['hu'].notnull()]
        data = data.reset_index(drop=True)
        print("Data is ready")
        print(data)
        return data



