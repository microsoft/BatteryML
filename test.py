import pickle
import pandas as pd

with open("./data/processed/HUST_FINAL/HUST_1-1.pkl", "rb") as f:  # Open in binary reading mode
    data_dict = pickle.load(f)

with open("./data/processed/HUST/final/HUST_1-1.pkl", "rb") as f:  # Open in binary reading mode
    data_dict = pickle.load(f)


print(len(data_dict['cycle_data']))
print(len(data_dict['1-1']['data'][10]['Time (s)']))

# with open(f"./data/raw/HUST_FINAL_TEST/1-1.pkl", "rb") as f:  # Open in binary reading mode
#     data_dict = pickle.load(f)

# print(data_dict['1-1']['data'].keys())
# print(len(data_dict['1-1']['data'][1]['Time (s)']))

# # -------------------------------------------------------------------------------------------------
# with open(f"./data/raw/HUST/hust_data/our_data/1-1.pkl", "rb") as f:  # Open in binary reading mode
#     data_dict = pickle.load(f)

# with open(f"./data/raw/HUST_FINAL_TEST/omg/1-1.pkl", "rb") as f:  # Open in binary reading mode
#     new_data_dict = pickle.load(f)

# print(len(data_dict['1-1']['data']))
# print(len(new_data_dict['1-1']['data']))

# print(data_dict['1-1']['data'][100])
# print(new_data_dict['1-1']['data'][100])

# # ------------------------------------------------------------------------------------
# print(data_dict['1-1']['data'].keys())
# print(new_data_dict['1-1']['data'].keys())

# print(data_dict['1-1']['data'][153].keys())
# print(new_data_dict['1-1']['data'][0].keys())

# print(data_dict['1-1'].keys())
# print(new_data_dict['1-1'].keys())

# print(data_dict['1-1']['data'][1]==new_data_dict['1-1']['data'][1])


# print(data_dict['1-1']['data'].keys())
# print(len(data_dict['1-1']['data'][1]['Time (s)']))
# print("ok")
# print(len(data_dict['1-1']['data']))

print()
