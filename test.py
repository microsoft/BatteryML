import pickle
# import pandas as pd

import scipy.io

data = scipy.io.loadmat('./data/raw/MATR/MATR_batch_20170512.mat')

print(data.keys())
# Access data using variable names from the MAT file
# my_array = data['array_name']



# with open(f"./data/raw/HUST/hust_data/our_data/1-1.pkl", "rb") as f:  # Open in binary reading mode
#     data_dict = pickle.load(f)


# print(data_dict.keys())
# # print(data_dict['1-1']['data'][12]['Cycle number'][1])


# with open(f"./data/raw/HUST_FINAL_TEST/omg/our_data_new_5_12/1-1.pkl", "rb") as f:  # Open in binary reading mode
#     data_dict = pickle.load(f)

# print(data_dict['1-1']['data'].keys())
# # # print(data_dict['1-1']['data'][1])
# print(data_dict['1-1']['data'][4]['Cycle number'][5])

# with open(f'./data/processed/HUST/final_10_12/HUST_2-8.pkl','rb') as f:
#     data_dict=pickle.load(f)

# print(data_dict.keys())
# print(data_dict['cycle_data'][0].keys())
# print(data_dict['cycle_data'][0]['time_in_s'])