#highest 2 card hand: ["As", "Ac", "2s", "3s", "4s"], score: 3545
#highest 3 card hand: ["As", "Ac", "Ah", "2s", "3s"], score: 1675
#highest 4 card hand: ["As", "Ac", "Ah", "Ad", "2s"], score: 22

import json

with open('../input_data.json') as data_file:    
    X = json.load(data_file)
    
for data_point in X:
        #data_point[11] = (270724 - data_point[11])*0.02748186345 + 22
    print(data_point[14])

#with open('../input_data.json', 'w') as data_file:    
    #json.dump(X, data_file)
        