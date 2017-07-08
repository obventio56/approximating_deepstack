import json

def main():
    target_data = []
    input_data = []
    with open('../input_data.json') as data_file:    
        input_data = json.load(data_file)
    with open('../target.json') as data_file:    
        target_data = json.load(data_file)
        
    for data_point in input_data:
    
    
if __name__ == "__main__":
    main()