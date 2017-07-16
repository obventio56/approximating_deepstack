import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

key_array = [ "betting_round", "subround", "my_chips", "opp_chips", "pot", "amt_to_call", "self_hand_agg", "opp_hand_agg", "self_last_agg", "opp_last_agg", "hand_strength", "hand_potential", "hand_std", "community_strength", "community_potential", "community_std"]
#0, 1, 0, 19950, 19900, 150, 50, 0, 0, 0, 0, 1201, 424821.2909183674, 178503124595.53516, -1, -1, -1

pandas_data = {}
df = False

def main():
    X = []
    Y = []
    
    
    
    with open('../input_data.json') as data_file:    
        X = json.load(data_file)
    with open('../target.json') as data_file:    
        Y = json.load(data_file)
        
    X = [x[2:len(x)] for x in X]
        
    for dimension in range(0, len(X[0])):
        pandas_data[key_array[dimension]] = pd.Series([x[dimension] for x in X])   
        
        
        fig = plt.figure()
        x_values, y_values = [], []
        for point_index, data_point in enumerate(X):
            x_values.append(data_point[dimension])
            y_values.append(Y[point_index])
            
        plt.plot(x_values, y_values, "o")
        plt.savefig("plots/" + str(dimension) + "_" + key_array[dimension] + ".png")
        pandas_data["target"] = pd.Series(Y)   
        df = pd.DataFrame(pandas_data)
        

if __name__ == "__main__":
    main()