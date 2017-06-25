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

core_count = 2

cards = ['2s', '2c', '2d', '2h', '3s', '3c', '3d', '3h', '4s', '4c', '4d', '4h', '5s', '5c', '5d', '5h', '6s', '6c', '6d', '6h', '7s', '7c', '7d', '7h', '8s', '8c', '8d', '8h', '9s', '9c', '9d', '9h', 'Ts', 'Tc', 'Td', 'Th', 'Js', 'Jc', 'Jd', 'Jh', 'Qs', 'Qc', 'Qd', 'Qh', 'Ks', 'Kc', 'Kd', 'Kh', 'As', 'Ac', 'Ad', 'Ah']

cards = [Card.new(card) for card in cards]
evaluator = Evaluator()

potential_times = []
pre_return = []

def evaluate(output_file, hand_cards, length, original_length):
    
    if len(hand_cards) == original_length:
        print("Start: " + Card.print_pretty_cards(hand_cards))
        potential_times.append(time.time())
        
    strengths = []
    
    if length > len(hand_cards):
        
        for card in cards:  
            if card not in hand_cards:
                strengths += evaluate(output_file, hand_cards + [card], length, original_length)

    if length == len(hand_cards):
        output_file.write(str(evaluator.evaluate(hand_cards[0:2], hand_cards[2:len(hand_cards)])) + ",")
    
    if len(hand_cards) == original_length:
        print("potential calc complete")
        difference = time.time() - potential_times.pop()
        print("Time: " + str(difference))          
        print("pre-return calculations")
        pre_return.append(time.time())
        
        
        return

    else:
        return strengths


    
def worker():
    while True:
        this_hand = q.get()
        with open ("hands/" + Card.print_pretty_cards(this_hand).replace(" ", "_") + ".txt", "w") as output_file:
            result = evaluate(output_file, this_hand, 7, 2)
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
    for i in range(cpus):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
            
            
q.join()



    
    


