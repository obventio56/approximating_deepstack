from holdem import Poker
import sys, random
import hand_ranker

def compare(hand1, hand2):
    if (hand1 == hand2):
        return 0
    try:
        rank1 = hand_ranker.rank(hand1)
    except:
        print("bad Hand")
        badHands.append(hand1)
        rank1 = [0, '']
    try: 
        rank2 = hand_ranker.rank(hand2)
    except:
        badHands.append(hand2)
        print("bad Hand")
        rank2 = [0, '']
        
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
 

def print_cards(cards):
    for card in cards:
        print(card)

class Game(object):
    
    def __init__(self, number_of_players, game_type):
        self.game_type = game_type
        self.number_of_players = number_of_players
        self.dealer = self.initiate_dealer(number_of_players)
        self.agents = self.initiate_agents(number_of_players)
        
    def initiate_agents(self, number_of_players):
        cards = self.dealer.distribute()
        agents = []
        for player in range(0, number_of_players):
            if (self.game_type == 'random'):
                agents.append(RandomAgent(random.randint(1,100)*100, cards[player]))
        
    def initiate_dealer(self, number_of_players):
        dealer = Poker(number_of_players, False)
        dealer.shuffle()
        dealer.cut(random.randint(1,51))
        return dealer
    
class RandomAgent(object):
    
    actions = ["fold", "check", "raise"]
    
    def __init__(self, starting_chips, cards):
        self.chips = starting_chips
        self.cards = cards
        print(self.chips)
        print_cards(self.cards)
        self.pot = 0
        self.in_play = True
        self.play_data = []
        
    def make_move(self, amount_to_call, can_raise):
        
        action = actions[random.randint(0,2)] if can_raise else actions[random.randint(0,1)]
        
        amount_spent = 0   
        if action == 'fold':
            self.in_play = False
        elif action == 'check':
            amount_spent = amount_to_call
        elif action == 'raise':
            amount_spent = random.randint(1,self.chips)
        self.chips = self.chips - amount_spent
        agressiveness = 0
        if self.pot != 0:
            agressivness = float(amount_spent)/self.pot
        else:
            agressivness = amount_spent
        self.play_data.append(agressivness)
        return amount_spent
    
    
game = Game(6, 'random')
    
    

    
            