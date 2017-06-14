import sys
sys.path.insert(0,'..')
import hand_ranker
import bisect
import itertools
import time
import numpy as np
import multiprocessing
from deuces import Card, Evaluator
import json

core_count = 2

cards = ['2s', '2c', '2d', '2h', '3s', '3c', '3d', '3h', '4s', '4c', '4d', '4h', '5s', '5c', '5d', '5h', '6s', '6c', '6d', '6h', '7s', '7c', '7d', '7h', '8s', '8c', '8d', '8h', '9s', '9c', '9d', '9h', 'Ts', 'Tc', 'Td', 'Th', 'Js', 'Jc', 'Jd', 'Jh', 'Qs', 'Qc', 'Qd', 'Qh', 'Ks', 'Kc', 'Kd', 'Kh', 'As', 'Ac', 'Ad', 'Ah']

cards = [Card.new(card) for card in cards]
evaluator = Evaluator()

potential_times = []
pre_return = []

def evaluate(hand_cards, length, original_length):
    
    if len(hand_cards) == original_length:
        print("Start: " + Card.print_pretty_cards(hand_cards))
        potential_times.append(time.time())
        
    strengths = []
    
    if length > len(hand_cards):
        
        for card in cards:  
            if card not in hand_cards:
                strengths += evaluate(hand_cards + [card], length, original_length)

    if length == len(hand_cards):
        strengths.append(evaluator.evaluate(hand_cards[0:2], hand_cards[2:len(hand_cards)])) 
    
    if len(hand_cards) == original_length:
        print("potential calc complete")
        difference = time.time() - potential_times.pop()
        print("Time: " + str(difference))          
        print("pre-return calculations")
        pre_return.append(time.time())
        
        probability = 1
        for depth in range(len(hand_cards), length):
            probability *= 1/(float(52 - depth))
            
        mean = sum(strengths)*probability
        
        
        standard_deviation = 0
        for x in strengths:
            standard_deviation += x**2  
        standard_deviation *= probability
        standard_deviation -=  mean**2
        
        print("pre-return complete")
        difference = time.time() - pre_return.pop()
        print("Time: " + str(difference))
        print("End: " + Card.print_pretty_cards(hand_cards))

        return (hand_cards, mean, standard_deviation)
    else:
        return strengths



with open ("../hands.txt", "r") as f:
    hands = f.read().split(",")
    number_of_hand_sets = len(hands)//core_count
    for hand_set in range(0, number_of_hand_sets):
        
        potentials = {}
        with open('../potentials.txt', 'r') as infile:
            potentials = json.load(infile)
            infile.close()
            
        pool = multiprocessing.Pool(processes=core_count)
        results = []
        for hand in range(hand_set*core_count, (hand_set + 1)*core_count):
            print(hands[hand])
            deuces_hand = [Card.new(card) for card in hands[hand].split(" ")]
            results.append(pool.apply_async(evaluate, args=(deuces_hand, 6, 2)))
        
        output = [p.get() for p in results]
        print(output)
        for result in output:
            print(result)
            potentials[Card.print_pretty_cards(result[0])] = [result[1], result[2]]

        with open('../potentials.txt', 'w') as outfile:
            json.dump(potentials, outfile)
            outfile.close()

#print(evaluate([Card.new("Ts"), Card.new("9h")], 7, 2))
    
    


