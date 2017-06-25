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

core_count = 2

cards = ['2s', '2c', '2d', '2h', '3s', '3c', '3d', '3h', '4s', '4c', '4d', '4h', '5s', '5c', '5d', '5h', '6s', '6c', '6d', '6h', '7s', '7c', '7d', '7h', '8s', '8c', '8d', '8h', '9s', '9c', '9d', '9h', 'Ts', 'Tc', 'Td', 'Th', 'Js', 'Jc', 'Jd', 'Jh', 'Qs', 'Qc', 'Qd', 'Qh', 'Ks', 'Kc', 'Kd', 'Kh', 'As', 'Ac', 'Ad', 'Ah']

cards = [Card.new(card) for card in cards]
evaluator = Evaluator()

potential_times = []
pre_return = []

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
        


with open ("../hands.txt", "r") as f:
    hands = f.read().split(",")
    q = queue.Queue()
    for hand in hands:
        deuces_hand = [Card.new(card) for card in hand.split(" ")]
        q.put(deuces_hand)
        
    cpus=multiprocessing.cpu_count() #detect number of cores
    print("Creating %d threads" % cpus)
    for i in range(cpus - 3):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
            
            
q.join()



    
    


