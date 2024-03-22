import pandas as pd
import pickle
import os
import re

NUM_OF_AVOIDING_CYCLES=10
NUM_OF_AVOIDING_SEC=12
FOLDER_PATH="./data/raw/HUST/hust_data/our_data"



file_list=os.listdir(FOLDER_PATH)
count=0
for filename in file_list:
    # if count>=4:
    #     print('ok')
    #     break
    # count=count+1
    if filename.endswith(".pkl"):
        print("FILENAME: ",filename," is getting processed.")
        filepath = os.path.join(FOLDER_PATH, filename)
        with open(filepath, "rb") as f:
            data_dict = pickle.load(f)
        # from filename keep only the '1-1' part
        pattern = re.compile(r'\b\d+-\d+\b')
        matches = pattern.findall(filename)
        cell_id=matches[0]

    with open(f"./data/raw/HUST/hust_data/our_data/{cell_id}.pkl", "rb") as f:
            data_dict = pickle.load(f)
    # print(data_dict[cell_id]['data'][1].keys())

    cycle_data_copy = data_dict[cell_id]['data']
    # count=0
    for i in range(len(cycle_data_copy) -1, 0, -1):  # Iterate in reverse order # len(cycle_data_copy) - 1
        # print('NEW CYCLE--------------------------------------------------------------------',i)
        # if i % NUM_OF_AVOIDING_CYCLES != 0:
        #     del data_dict[cell_id]['data'][i]
        #     continue
        df = pd.DataFrame(data_dict[cell_id]['data'][i])
                # print(df.head())
                # print("old shape: ", df.shape[0])

        filtered_dfs = []
        # Iterate through each row index
        for j in range(df.shape[0]):
            if j % NUM_OF_AVOIDING_SEC == 0:
                # Append the row to the list of filtered DataFrames if the condition is met
                filtered_dfs.append(df.iloc[[j]])

        # Concatenate the list of filtered DataFrames along the row axis
        filtered_df = pd.concat(filtered_dfs, ignore_index=True)

        # print('new shape:', filtered_df.shape[0])
        filtered_df.to_pickle('./data/processed/HUST/reduceTest/other/cycle.pkl')
        with open("./data/processed/HUST/reduceTest/other/cycle.pkl", "rb") as f:  # Open in binary reading mode
            data_dict[cell_id]['data'][i] = pickle.load(f)

        # for j in range(len(cycle_data_copy[i])-1,-1,-1):
        #     if (cycle_data_copy[i]['Time (s)'][j]+1)%NUM_OF_AVOIDING_SEC==0 or cycle_data_copy[i]['Time (s)'][j]==0:
        #         print(cycle_data_copy[i]['Time (s)'][j])
        #         # del data_dict[cell_id]['data'][i]
        #         continue

    # import copy
    # # new_dict = data_dict
    # # new_dict={}
    # pd.options.mode.chained_assignment = None
    # new_dict = copy.deepcopy(data_dict)
    # # print(new_dict.keys())
    # # print(data_dict.keys())
    # for index, key in enumerate(data_dict[cell_id]['data'].keys()):
    #     # print(cell_id)
    #     if cell_id not in new_dict:  # Initialize new_dict[cell_id] if it doesn't exist
    #         new_dict[cell_id] = {'data': {}}
    #     new_dict[cell_id]['data'][index+1] = data_dict[cell_id]['data'][key]
    #     # for other_index, other_key in enumerate(new_dict[cell_id]['data'][index+1]):
    #     #     # new_dict[cell_id]['data'][index+1]['Cycle number'][other_index+1] = new_dict[cell_id]['data'][index+1]['Cycle number'][other_key]
    #     #     new_dict[cell_id]['data'][index+1]['Cycle number'][other_index] = other_index+1

    print("New Number of cycles in the cell: ",len(data_dict[cell_id]['data']))

    # print("New Number of cycles in the cell: ",data_dict[cell_id]['data'])
    print("New Number of data in the cycle: ",len(data_dict[cell_id]['data'][10]))

    with open(f"./data/raw/HUST_FINAL_TEST/omg/{cell_id}.pkl", 'wb') as f:
            # Write the data to the file using pickle.dump()
            pickle.dump(data_dict, f)