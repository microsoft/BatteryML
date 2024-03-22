import pickle
import pandas as pd
import os

NUM_OF_AVOIDING_CYCLES=10
NUM_OF_AVOIDING_SEC=12
FOLDER_PATH="./data/processed/HUST/"

file_list=os.listdir(FOLDER_PATH)
for filename in file_list:
    if filename.endswith(".pkl"):
        print("FILENAME: ",filename," is getting processed.")
        filepath = os.path.join(FOLDER_PATH, filename)
        with open(filepath, "rb") as f:
            data_dict = pickle.load(f)
        # print("DATA COLUMNS:\n",data_dict.keys())
        # print("CYCLE_DATA COLUMNS:\n",data_dict['cycle_data'][0].keys())
        # print("Cell id: ",data_dict['cell_id'])

        # # df=pd.DataFrame(data_dict['cycle_data'])
        # # print(df.head())

        # # CELL
        # print("Number of cycles in the cell: ",len(data_dict['cycle_data']))
        # # print(data_dict['cell_id'])
        # # CYCLE - in each cycle keep data per minute
        # print("Number of data in the cycle: ",len(data_dict['cycle_data'][0]['time_in_s']))
        df=pd.DataFrame(data_dict['cycle_data'][0])
        # print(df.head)

        cycle_data_copy = data_dict['cycle_data'][:]
        for i in range(len(cycle_data_copy) -1, -1, -1):  # Iterate in reverse order # len(cycle_data_copy) - 1
            # print('NEW CYCLE--------------------------------------------------------------------')
            if i % NUM_OF_AVOIDING_CYCLES != 0:
                del data_dict['cycle_data'][i]
                continue
            # print(data_dict['cycle_data'][i])
            df = pd.DataFrame(data_dict['cycle_data'][i])
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
                data_dict['cycle_data'][i] = pickle.load(f)
            # print(data_dict['cycle_data'][i])
        print("New Number of cycles in the cell: ",len(data_dict['cycle_data']))
        print("New Number of data in the cycle: ",len(data_dict['cycle_data'][1]['time_in_s']))
    with open(f"./data/processed/HUST_FINAL/{filename}", 'wb') as f:
        # Write the data to the file using pickle.dump()
        pickle.dump(data_dict, f)