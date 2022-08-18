import pandas as pd
from numpy import nan, timedelta64
import requests
from datetime import date


class Data:
    REQUEST_DATA_URL = "https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active"
    LOCAL_DATA = "vehicles.csv"
    LABELS_IDS_URL = "https://api.baubuddy.de/dev/index.php/v1/labels/"

    def __init__(self):
        self.__get_data()

    def __get_url_data(self):
        print("Start getting url data...")
        requested_data = requests.get(self.REQUEST_DATA_URL)
        json_data = requested_data.json()
        url_data = pd.DataFrame.from_dict(json_data)
        url_data.drop_duplicates()
        print("Url data is collected.")
        return url_data

    def __get_local_data(self):
        print("Start getting local data...")
        local_data = pd.read_csv(self.LOCAL_DATA, delimiter=";")
        local_data.drop_duplicates()
        print("Local data is collected.")
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
        print("Data is ready.")

        return data

    def __get_data(self):
        data = self.__merge_data()
        print("Start finding colorCodes by labelId...")
        data['colorCode'] = None

        for row in range(len(data.index)):
            label_id = data.labelIds[row]

            if label_id is not None:
                label_id_response = requests.get(f"https://api.baubuddy.de/dev/index.php/v1/labels/{label_id}")
                label_id_json = label_id_response.json()
                label_id = pd.DataFrame.from_dict(label_id_json)
                data.colorCode[row] = label_id.colorCode
        print("End finding colorCodes by labelId.")
        data = data.sort_values('gruppe')
        data = data.reset_index(drop=True)

        data['hu'] = pd.to_datetime(data['hu']).dt.date

        current_date = date.today()
        data.insert(12, 'currDate', current_date)
        data.insert(13, 'dateDiff', (data.currDate - data.hu) / timedelta64(1, 'M'))

        print(data)
        return data



