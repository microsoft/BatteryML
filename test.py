import pickle
import pandas as pd

with open(f"./data/raw/HUST/hust_data/our_data/1-1.pkl", "rb") as f:  # Open in binary reading mode
    data_dict = pickle.load(f)

# print(data_dict['1-1']['data'][12]['Cycle number'][1])


with open(f"./data/raw/HUST_FINAL_TEST/omg/our_data_new/1-8.pkl", "rb") as f:  # Open in binary reading mode
    data_dict = pickle.load(f)

print(data_dict['1-8']['data'].keys())
# print(data_dict['1-1']['data'][1])
print(data_dict['1-8']['data'][1]['Cycle number'][5])