import pandas as pd
from numpy import nan, timedelta64
import requests
from datetime import date, datetime
from collections import deque


class Data:
    REQUEST_DATA_URL = "https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active"
    LOCAL_DATA = "vehicles.csv"
    LABELS_IDS_URL = "https://api.baubuddy.de/dev/index.php/v1/labels/"

    def __init__(self):
        self.my_df = self.__get_data()

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
        df = pd.merge(self.__get_url_data(), self.__get_local_data(), how="outer", on="kurzname")
        print("Start merging url data and local data and make data manupulations...")
        df = df.replace(r'^\s*$', None, regex=True)
        df = df.replace({nan: None})

        for row in range(len(df.index)):
            if df.gruppe_x[row] is None:
                if df.gruppe_y[row] is not None:
                    df.gruppe_x[row] = df.gruppe_y[row]
            if df.langtext_x[row] is None:
                if df.langtext_y[row] is not None:
                    df.langtext_x[row] = df.langtext_y[row]
            if df.info_x[row] is None:
                if df.info_y[row] is not None:
                    df.info_x[row] = df.info_y[row]
            if df.lagerort_x[row] is None:
                if df.lagerort_y[row] is not None:
                    df.lagerort_x[row] = df.lagerort_y[row]

            if df.labelIds_x[row] is None:
                if df.labelIds_y[row] is not None:
                    df.labelIds_x[row] = df.labelIds_y[row]

        df.drop(['gruppe_y', 'langtext_y', 'info_y', 'lagerort_y', 'labelIds_y'], inplace=True, axis=1)
        df.rename(columns={'gruppe_x': 'gruppe',
                           'langtext_x': 'langtext',
                           'info_x': 'info',
                           'lagerort_x': 'lagerort',
                           'labelIds_x': 'labelIds'}, inplace=True)

        df = df[df['hu'].notnull()]
        df = df.reset_index(drop=True)
        print("Data is ready.")

        return df

    def __get_data(self):
        df = self.__merge_data()
        print("Start finding colorCodes by labelId...")
        df['colorCode'] = None

        for row in range(len(df.index)):
            label_id = df.labelIds[row]

            if label_id is not None:
                label_id_response = requests.get(f"https://api.baubuddy.de/dev/index.php/v1/labels/{label_id}")
                label_id_json = label_id_response.json()
                label_id = pd.DataFrame.from_dict(label_id_json)
                df.colorCode[row] = label_id.colorCode
        print("End finding colorCodes by labelId.")
        df = df.sort_values('gruppe')
        df = df.reset_index(drop=True)

        df['hu'] = pd.to_datetime(df['hu']).dt.date

        current_date = date.today()
        df.insert(12, 'currDate', current_date)
        df.insert(13, 'dateDiff', (df.currDate - df.hu) / timedelta64(1, 'M'))

        print(df)
        return df

    @staticmethod
    def format_df(data):
        if data.dateDiff < 3:
            return ['background-color: green'] * len(data)
        if data.dateDiff < 12:
            return ['background-color: orange'] * len(data)
        return ['background-color: red'] * len(data)

    @staticmethod
    def format_text(data, color):
        return [f'color: {color}'] * len(data)

    def export_data(self, *args, colored: bool = True):
        df = self.my_df
        args = deque(args)
        curr_date_iso = datetime.now().isoformat()
        curr_date_iso = curr_date_iso.replace(":", "-")
        file_name = "vehicles_"

        if "labelIds" in args:
            if any(df.colorCode):
                temp_df = df[df.colorCode.notnull()]
                color_code = temp_df.iloc[0]['colorCode']
                df.style.apply(lambda df: self.format_text(df, color_code), axis=1).to_excel(
                    f"{file_name}{curr_date_iso}.xlsx", index=False)

        if colored:
            df.style.apply(lambda df: self.format_df(df), axis=1).to_excel(f"{file_name}{curr_date_iso}.xlsx",
                                                                           index=False)
        else:
            df.to_excel(f"{file_name}{curr_date_iso}.xlsx", index=False)

        if args[0] == "":
            return df

        default = "rnr"
        args.appendleft(default)
        temp_df = df[args]
        return temp_df
