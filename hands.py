import hand_ranker
import bisect
import itertools
import time
import multiprocessing
from deuces import Card, Evaluator
import json

cards = ['2s', '2c', '2d', '2h', '3s', '3c', '3d', '3h', '4s', '4c', '4d', '4h', '5s', '5c', '5d', '5h', '6s', '6c', '6d', '6h', '7s', '7c', '7d', '7h', '8s', '8c', '8d', '8h', '9s', '9c', '9d', '9h', 'Ts', 'Tc', 'Td', 'Th', 'Js', 'Jc', 'Jd', 'Jh', 'Qs', 'Qc', 'Qd', 'Qh', 'Ks', 'Kc', 'Kd', 'Kh', 'As', 'Ac', 'Ad', 'Ah']

cards = [Card.new(card) for card in cards]

evaluator = Evaluator()

print(cards)

"""      
def init_lookup(file_name):
    lookup = {}
    with open (file_name, "r") as f:
        hands = f.read().split(",")
        for index, hand in enumerate(hands):
            lookup[hand] = index
    return lookup


    
def compareCards(card1, card2):
    index1 = cards.index(card1)
    index2 = cards.index(card2)

    if (index1 < index2):
        return -1
    elif (index1 > index2):
        return 1
    return 0

def order_cards(hand_cards, cards):
    hand_cards = list(hand_cards)
    hand_cards.sort(cmp=compareCards)
    return " ".join(hand_cards)
"""
    
start = 0
end = 0

def evaluate(hand_cards, length, original_length):
    
    probability = 0
    
    if length > len(hand_cards):
        
        if len(hand_cards) == 4:
            start = time.time()
        #if len(hand_cards) == 4:
            #print(Card.print_pretty_cards(hand_cards))
                
        for card in cards:  
            if card not in hand_cards:
                probability += (1/float(52 - len(hand_cards)))*evaluate(hand_cards + [card], length, original_length)
                
        if len(hand_cards) == 4:
            end = time.time()
            print(end - start)
            

    if length == len(hand_cards):
        probability = evaluator.evaluate(hand_cards[0:2], hand_cards[2:len(hand_cards)])    
    
    if len(hand_cards) == original_length:
        return (hand_cards, probability)
    else:
        return probability


#hands_lookup = init_lookup("hands.txt")
#flops_lookup = init_lookup("flops.txt")
pool = multiprocessing.Pool(processes=2)
results = []

with open ("test_hands.txt", "r") as f:
    hands = f.read().split(",")
    for hand in hands:
        deuces_hand = [Card.new(card) for card in hand.split(" ")]
        results.append(pool.apply_async(evaluate, args=(deuces_hand, 7, 2)))
        
output = [p.get() for p in results]

potentials = {}

for result in output:
    print(result)
    potentials[Card.print_pretty_cards(result[0])] = result[1]

with open('potentials.txt', 'w') as outfile:
    json.dump(potentials, outfile)
    
print(output)

#print(evaluate([Card.new("Ts"), Card.new("9h")], 7, 2))
    


