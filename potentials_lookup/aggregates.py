 
import os 
import json

potentials = {}
    
for fn in os.listdir('hands'):
    print (fn)   

    with open ("hands/" + fn) as strengths_file:
        strengths = [int(val) for val in strengths_file.read().split(",") if val != '']
        print(len(strengths))
        probability = 1/float(19600)

        mean = sum(strengths)*probability


        standard_deviation = 0
        for x in strengths:
            standard_deviation += x**2 
        standard_deviation *= probability
        standard_deviation -=  mean**2

        potentials[fn.replace(".txt", "")] = [mean, standard_deviation]
    
with open ("../potentials.txt", "w") as potentials_file:
    potentials = json.dump(potentials, potentials_file)