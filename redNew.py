import pandas as pd
import pickle
import os
import re
import sys

script_name = sys.argv[0]
arguments = sys.argv[1:]

if len(arguments)==2:
    NUM_OF_AVOIDING_CYCLES=int(sys.argv[1])
    NUM_OF_AVOIDING_SEC=int(sys.argv[2])
else:
    NUM_OF_AVOIDING_CYCLES=10
    NUM_OF_AVOIDING_SEC=12

print(NUM_OF_AVOIDING_CYCLES)
print(NUM_OF_AVOIDING_SEC)

FOLDER_PATH="./data/raw/HUST/hust_data/our_data"

file_list=os.listdir(FOLDER_PATH)
count=0
for filename in file_list:
    # if count==1:
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
        if i % NUM_OF_AVOIDING_CYCLES != 0:
            del data_dict[cell_id]['data'][i]
            continue
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

    # print(data_dict['1-1']['data'].keys())
    # print(data_dict['1-1']['data'][10])
    pd.options.mode.chained_assignment = None
    # import copy
    new_dict={}
    new_dict[cell_id] = {'data': {}}
    for index,current_index in enumerate(data_dict[cell_id]['data'].keys()):
        new_index=index+1
        # print(index+1,current_index)
        new_dict[cell_id]['dq']=data_dict[cell_id]['dq']
        new_dict[cell_id]['rul']=data_dict[cell_id]['rul']
        new_dict[cell_id]['data'][new_index] = {
        'Status': data_dict[cell_id]['data'][current_index]['Status'],
        'Cycle number': data_dict[cell_id]['data'][current_index]['Cycle number'],
        'Current (mA)': data_dict[cell_id]['data'][current_index]['Current (mA)'],
        'Voltage (V)': data_dict[cell_id]['data'][current_index]['Voltage (V)'],
        'Capacity (mAh)': data_dict[cell_id]['data'][current_index]['Capacity (mAh)'],
        'Time (s)': data_dict[cell_id]['data'][current_index]['Time (s)']
    }
        for cycle_index,now_value in enumerate(new_dict[cell_id]['data'][i]['Cycle number']):
            # print(cycle_index,now_value,new_index)
            new_dict[cell_id]['data'][new_index]['Cycle number'][cycle_index]=new_index #TODO
            # print("::::::::::::::::::::::::",new_dict[cell_id]['data'][i]['Cycle number'][cycle_index])
            # new_dict[cell_id]['data'][new_index]['Cycle number'][j]=j+1
            # data_dict[cell_id]['data'][i]['Cycle number'][]=
    data_dict[cell_id]['data']=new_dict[cell_id]['data']
    # print(data_dict[cell_id]['data'][10])
    # print(new_dict.keys(),data_dict.keys())
    # print(new_dict[cell_id].keys(),data_dict[cell_id].keys())
    # print(new_dict[cell_id]['data'].keys(),data_dict[cell_id]['data'].keys())
    # print(new_dict[cell_id]['data'][1]['Cycle number'][1])

    print("New Number of cycles in the cell: ",len(data_dict[cell_id]['data']))
    print("New Number of data in the cycle: ",len(data_dict[cell_id]['data'][10]))
    # print("New Number of cycles in the cell: ",len(new_dict[cell_id]['data']))
    # print("New Number of data in the cycle: ",len(new_dict[cell_id]['data'][10]))

    with open(f"./data/raw/HUST_FINAL_TEST/omg/our_data_new_5_12/{cell_id}.pkl", 'wb') as f:
            # Write the data to the file using pickle.dump()
            pickle.dump(data_dict, f)