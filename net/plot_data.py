import json
import numpy as np
import matplotlib.pyplot as plt

#0, 1, 0, 19950, 19900, 150, 50, 0, 0, 0, 0, 1201, 424821.2909183674, 178503124595.53516, -1, -1, -1

def main():
    X = []
    Y = []
    
    
    
    with open('../input_data.json') as data_file:    
        X = json.load(data_file)
    with open('../target.json') as data_file:    
        Y = json.load(data_file)
     
    #all_data = []
    
    #for point_index, data_point in enumerate(X):
    #    all_data.append([data_point, Y[point_index]])  
        
    #for dimension in range(0, len(X[0])):
    #dimension = 11
    #fig = plt.figure()
    #x_values = [point[0][dimension] for point in all_data if point[0][1] == 1]
    #y_values = [point[1] for point in all_data if point[0][1] == 1]
    #plt.plot(x_values, y_values, "o")
    #plt.savefig(str(dimension) + ".png")
    print(X[Y.index(max(Y))])
    plt.xlim([0,10])
    plt.hist(Y,normed=True, bins=5, range=range(0,10))
    plt.savefig("hist.png")
        

if __name__ == "__main__":
    main()