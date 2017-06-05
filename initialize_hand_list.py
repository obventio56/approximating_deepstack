import hand_ranker
import itertools
import time

def compareCards(card1, card2):
    index1 = cards.index(card1)
    index2 = cards.index(card2)
    
    if (index1 < index2):
        return -1
    elif (index1 > index2):
        return 1
    return 0


def compareHands(hand1, hand2):
    rank1 = hand_ranker.rank(hand1)
    rank2 = hand_ranker.rank(hand2)
    if (rank1[0] == rank2[0]):
        tieBreakerLen = len(rank1[1]) if len(rank1[1]) < len(rank2[1]) else len(rank2[1])
        for tieLevel in range(0,tieBreakerLen):
            tie1 = int(rank1[1][tieLevel])
            tie2 = int(rank2[1][tieLevel])
            if (tie1 > tie2):
                return 1
            elif (tie1 < tie2):
                return -1
        if (len(rank1[1]) > len(rank2[1])):
            return 1
        elif (len(rank1[1]) < len(rank2[1])):
            return -1
        else:
            return 0
        
    elif (rank1[0] > rank2[0]):
        return 1
    
    return -1


def generateOrderedCombos(combos, filename):
    hands = []
    for combo in combos:
        combo_list = map(str,combo)
        combo_list.sort(cmp=compareCards)
        hands.append(' '.join(combo_list))
        
    hands.sort(cmp=compareHands)  
    
    with open(filename, 'w') as outfile:
        for item in hands:
            outfile.write("%s," % item)
            
            
faces = ['s','c','d','h']
card_values = ['2', '3', '4', '5', '6', '7','8', '9', '10', '11', '12', '13', '14']  
cards = []

for index, value in enumerate(card_values):
    for face in range(0, len(faces)):
        cards.append(value + faces[face])
        
def main():

    hand_combos = itertools.combinations(cards, 2)
    generateOrderedCombos(hand_combos, 'hands.txt')

    print("hands complete")

    flop_combos = itertools.combinations(cards, 5)
    generateOrderedCombos(flop_combos, 'flops.txt')
    

if __name__ == "__main__":
    main()




        


    

