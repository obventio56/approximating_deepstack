import json


with open ("../turns.txt", "r") as f:
    hands = f.read().split(",")
    hand_ranks = {}
    
    
    number_of_hands = float(len(hands))
    for hand_index, hand in enumerate(hands):
        hand_ranks[hand] = hand_index
        
    with open('../turns.json', 'w') as outfile:
        json.dump(hand_ranks, outfile)