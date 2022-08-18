import pandas as pd
from data import Data


pd.set_option('display.expand_frame_repr', False)

df = Data()
keys = input(f"Possible columns {str(df.my_df.columns)}. What columns do you want: ").split(", ")

print(df.export_data(*keys, colored=False))



