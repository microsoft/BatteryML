import pickle

with open('./workspace/test/predictions_seed_0_20240302185650.pkl', 'rb') as f:
    data = pickle.load(f)

# Check the data type
print(type(data))
print(data.keys())

# # Example: If it's a dictionary, access values by key
if isinstance(data, dict):
  print(data["scores"])  # Print the value for key "key"