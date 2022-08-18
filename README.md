Hello dear python dev!

This repository is supposed to act as a playground for your submission.

Before getting started, please make sure use this repository as a **template** and create your own **public** repository, on which you will commit and push your code regularly. 
Once you are ready, please mail us back the link to your repository. 

Below, you will find the **Task** definition.

Happy Hacking :computer:

# Task

Write a python script that connects to a remote API, downloads a certain set of resources, merges them with local resources, and converts them to a formatted excel file.
In particular, the script should:

- Take an input parameter `-k/--keys` that can receive an arbitrary amount of string arguments
- Take an input parameter `-c/--colored` that receives a boolean flag and defaults to `True`
- Request the resources located at `https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active`
- Additionally, read and parse the locally provided [vehicles.csv](vehicles.csv)
- Store both of them in an appropriate data structure and make sure the result is distinct
- Filter out any resources that do not have a value set for `hu` field
- For each `labelId` in the vehicle's JSON array `labelIds` resolve its `colorCode` using `https://api.baubuddy.de/dev/index.php/v1/labels/{labelId}`
- Generate an `.xlsx` file that contains all resources and make sure that:
   - Rows are sorted by response field `gruppe`
   - Columns always contain `rnr` field
   - Only keys that match the input arguments are considered as additional columns (i.e. when the script is invoked with `kurzname` and `info`, print two extra columns)
   - If `labelIds` are given and at least one `colorCode` could be resolved, use the first `colorCode` to tint the cell's text (if `labelIds` is given in `-k`)
   - If the `-c` flag is `True`, color each row depending on the following logic:
     - If `hu` is not older than 3 months --> green (`#007500`)
     - If `hu` is not older than 12 months --> orange (`#FFA500`)
     - If `hu` is older than 12 months --> red (`#b30000`)
   - The file should be named `vehicles_{current_date_iso_formatted}.xlsx`


# Description
## Installation
We need to install few packages to be able to performe the tast. First of all we will install pandas. Write to your terminal this:
```bash
pip install pandas
```
this will give us the desired format of our data. It is very easy to work with DataFrame type.
Second we will install requests packages. With that we can make a request to the given urls and get the data from them
```bash
pip install requests
```
These two packages are needed to start the task. Right down i will put the other packages i use to complete the task
```bash
pip install Jinja2
```

```bash
pip install openpyxl
```

### Usage
In our project we will create data.py file where we will create our Data class. This class will be responsible for our task. In it we will implement whole logic. For this class we will need few methods and i will go through all of them one by one:
- We are creating our class atributes, REQUEST_DATA_URL, LOCAL_DATA, LABELS_IDS_URL. From there we will collect all the needed information for our task.
- We are creating get_url_data method. This method is private because it is not needed to know how we do that outsite our class, but in the same time we can check it directly in out class. Most of our methods will be private. In this method we just make a request to REQUEST_DATA_URL and store the data into variable ant return it.
- We are creating get_local_data method. It is private method. Here we are just getting the data from our vehicle.csv file, which is given to us by the task.
- merge_data method. Everything here is clear. We are just merging our two dataframes, which we created above. In this method we make all the needed manipulation for our dataframe, before we start to export and color it. These two dataframes are the same, but in vehicle.csv file, there is one more item. Also after merging the datas, we are creating one big dataframe with the all info from the two dataframes. When we do that, we performe some manipulations to check is the info from the first is the same in the second, if not to make it the same.
- We are crating get_data method, which will bring us to the final version of our dataframe. This will be the format with whom we will performe export method(which is not created yet). In this method we check for colorIds. If we find colorIds we place it in our dataframe, if not we give None.Also we performe some mathematical operations, here we need to find date difference between to columns with datetime objects and make that values to months.
- We are creating two static method for our coloring in our dataframe. These methods will give us the flexibility to performe all kind of formation we want. But for out task we have only two conditions, so thats why we have two static methods. We called them format_df and format_text.
- Finally we are creating our export method, which will be responsible for exporting the data and for its formating. In this method we implement almost all conditions from our task. Here is the while class Data:

```python
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
```
## Finaly
we are creating our main file, where we will give some input information for our data (what kind of columns we need to print). Here everything is pretty straight forward

```python
import pandas as pd
from data import Data


pd.set_option('display.expand_frame_repr', False)

df = Data()
keys = input(f"Possible columns {str(df.my_df.columns)}. What columns do you want: ").split(", ")
print(df.export_data(*keys))

```



