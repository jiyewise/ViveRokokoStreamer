import pickle

with open('test_output_json.pickle', 'rb') as f:
    data = pickle.load(f)

    print(data)