from importlib import resources 
import pandas as pd 
from bourbon.get_bourbon import get_all_bourbons

# get values of dataframe 
with resources.path("my_data","bourbons.csv") as f: 
    bourbon_names = pd.read_csv(f).loc[:,'name'].to_list()


if __name__ == "__main__": 
    
    all_bourbons = [get_all_bourbons(bourbon) for bourbon in bourbon_names]
    full_df = pd.concat(all_bourbons).reset_index(drop=True)

    print(full_df)
