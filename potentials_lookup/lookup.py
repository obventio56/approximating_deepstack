import sys
sys.path.insert(0,'..')
import hand_ranker
import bisect
import itertools
import time
import numpy as np
import queue
import threading
import multiprocessing
from deuces import Card, Evaluator
import json
import copy 
import operator as op
from functools import reduce

core_count = 2

cards = ['2s', '2c', '2d', '2h', '3s', '3c', '3d', '3h', '4s', '4c', '4d', '4h', '5s', '5c', '5d', '5h', '6s', '6c', '6d', '6h', '7s', '7c', '7d', '7h', '8s', '8c', '8d', '8h', '9s', '9c', '9d', '9h', 'Ts', 'Tc', 'Td', 'Th', 'Js', 'Jc', 'Jd', 'Jh', 'Qs', 'Qc', 'Qd', 'Qh', 'Ks', 'Kc', 'Kd', 'Kh', 'As', 'Ac', 'Ad', 'Ah']

cards = [Card.new(card) for card in cards]
evaluator = Evaluator()

potential_times = []
pre_return = []

two_card_lookup = {}

with open('../two_card_lookup.json') as data_file:    
    two_card_lookup = json.load(data_file)
    
three_card_lookup = {}

with open('../flops.json') as data_file:    
    three_card_lookup = json.load(data_file)
    
four_card_lookup = {}

with open('../turns.json') as data_file:    
    four_card_lookup = json.load(data_file)
    
    
two_card_potentials = {}

with open('../potentials.json') as data_file:    
    two_card_potentials = json.load(data_file)
    


def evaluate(output_file, hand_cards, length, original_length, count):
    
    print("Start: " + Card.print_pretty_cards(hand_cards))
    potential_times.append(time.time())
        
    
    remaining_cards = copy.deepcopy(cards)
    for card in hand_cards:
        remaining_cards.remove(card)   
        
    for card_combo in itertools.combinations(remaining_cards, length - original_length):  
        possible_hand = hand_cards + list(card_combo)
        
        output_file.write(str(evaluator.evaluate(possible_hand[0:2], possible_hand[2:len(possible_hand)])) + ",")
    
    if len(hand_cards) == original_length:
        print("potential calc complete")
        difference = time.time() - potential_times.pop()
        print("Time: " + str(difference))          
        print("pre-return calculations")
        pre_return.append(time.time())
        print(count)
       
        
    return

    
def worker():
    while True:
        this_hand = q.get()
        with open ("hands/" + Card.print_pretty_cards(this_hand).replace(" ", "_") + ".txt", "w") as output_file:
            result = evaluate(output_file, this_hand, 5, 2, 0)
            output_file.close()
        q.task_done()
        

def main():
    with open ("../hands.txt", "r") as f:
        hands = f.read().split(",")
        q = queue.Queue()
        for hand in hands:
            deuces_hand = [Card.new(card) for card in hand.split(" ")]
            q.put(deuces_hand)

        cpus=multiprocessing.cpu_count() #detect number of cores
        print("Creating %d threads" % cpus)
        for i in range(cpus):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()


    q.join()


if __name__ == "__main__":
    main()
    
def transform_for_lookup(card_string):
    card_string = card_string.replace("T", "10")
    card_string = card_string.replace("J", "11")
    card_string = card_string.replace("Q", "12")
    card_string = card_string.replace("K", "13")
    card_string = card_string.replace("A", "14")
    return card_string

    
def order_cards(card):
    return cards.index(Card.new(card))
 
def hand_strength(hand_cards, community):
    if len(community) == 0:
        hand_cards.sort(key=order_cards)
        raw_score = two_card_lookup[" ".join(hand_cards)]
        scaled_score = (1325 - raw_score)*2.9562264151 + 3545
        return scaled_score
    
    elif len(community) == 3 and len(hand_cards) == 0:

        community.sort(key=order_cards)
        community = " ".join(community)
        community = transform_for_lookup(community)
        raw_score = three_card_lookup[community]
        scaled_score = (22100 - raw_score)*0.2618552036 + 1675
        
        return scaled_score
    elif len(community) == 4 and len(hand_cards) == 0:

        community.sort(key=order_cards)
        community = " ".join(community)
        community = transform_for_lookup(community)
        raw_score = four_card_lookup[community] 
        scaled_score = (270725 - raw_score)*0.02756526525 + 22
        return four_card_lookup[community]      
    else: 
        deuces_cards = [Card.new(card) for card in hand_cards]
        deuces_community = [Card.new(card) for card in community]
        return evaluator.evaluate(deuces_cards, deuces_community)
    
def hand_potential(hand_cards, community):
    if len(community) == 0:
        hand_cards.sort(key=order_cards)
        mean, std = tuple(two_card_potentials["_".join(hand_cards)])
        return mean, std
    
    elif len(community) != 5:
        strengths = []
        
        all_cards = hand_cards + community
        all_cards = [Card.new(card) for card in all_cards]
        
        remaining_cards = copy.deepcopy(cards)
        for card in all_cards:
            remaining_cards.remove(card) 
            
        for card_combo in itertools.combinations(remaining_cards, 7 - len(all_cards)): 
            possible_hand = all_cards + list(card_combo) 
            strengths.append(evaluator.evaluate(possible_hand[0:2], possible_hand[2:len(possible_hand)]))

        probability = 1.0/len(strengths)
    
        mean = sum(strengths)*probability

        standard_deviation = 0.0
        for x in strengths:
            standard_deviation += x**2 
        standard_deviation *= probability
        standard_deviation -=  mean**2
        
        return mean, standard_deviation
    else:
        return hand_strength(hand_cards, community), 0
    
def ncr(n, r):
    r = min(r, n-r)
    if r == 0: return 1
    numer = reduce(op.mul, range(n, n-r, -1))
    denom = reduce(op.mul, range(1, r+1))
    return numer//denom

def evaluate_hand(cards):
    deuces_cards = [Card.new(card) for card in cards]
    return evaluator.evaluate(deuces_cards[0:2], deuces_cards[2:len(deuces_cards)])
    
        

        
    
    


