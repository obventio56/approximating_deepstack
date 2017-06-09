import re
import numpy as np

class Game(object):
    
    def __init__(self, line):
        
        self.id = 0
        self.flop = []
        self.turn = []
        self.river = []
        self.parse_acpc(line)
        
    def parse_acpc(self, line):
        lineMatch = re.match( r'STATE:(.*) # (.*)', line)
        data = lineMatch.group(1).split(":")
        self.id = int(data[0])
        
        player1, player2 = re.split('\|', data[4])
        
        moves2, moves1 = self.parse_moves(data[1])
        
        cards1, cards2, self.flop, self.turn, self.river = return_value = self.parse_cards(data[2], 5)
        
        agent1 = Agent(cards1, moves1, 0)
        agent2 = Agent(cards2, moves2, 1)
        
        if (player1 == 'DeepStack'):
            self.deepstack = agent1
            self.other_player = agent2
        else:
            self.deepstack = agent2
            self.other_player = agent1

    def parse_cards(self, card_string, expected_groups):
        
        card_groups = []
        groups = re.split(r'\||\/', card_string)
        for group in groups:
            cards_in_group = re.findall('(?:[QKJA]|[2-9]|10)[hdsc]', group)
            card_groups.append(cards_in_group)
            
        card_groups += [list()]*(expected_groups - len(card_groups))
        return tuple(card_groups)
    
    def parse_moves(self, moves_string):
        
        moves1, moves2 = [], []
        
        move_groups = re.split('\/', moves_string)
        for group in move_groups:
            moves = re.findall('[cf]|r[\d]+', group)
            moves1.append(moves[0::2] if moves[0::2] != [] else ['s'])
            moves2.append(moves[1::2] if moves[0::2] != [] else ['s'])
        
        return moves1, moves2
    
    def current_standing(self, betting_round, subround):
        pot = 0 #start pot at 0
          
        #initiate players in the order of turns (i.e. player1 and player2)
        players = {}
        player1 = self.other_player
        players["other_player"] = player1
        player2 = self.deepstack
        players["deepstack"] = player2
      
        if self.deepstack.position == 0:
            player1 = self.deepstack
            players["deepstack"] = player1
            player2 = self.other_player
            players["other_player"] = player2
            
        player1.chips, player2.chips = player1.starting_chips, player2.starting_chips #set starting chip amounts

        #Determine the round of betting. Make sure both players have moves in that round to avoid range errors. 
        #A raise will never be the last move so this works
        if betting_round + 1 > len(player1.moves) or betting_round + 1 > len(player2.moves): subround = 5
        betting_round = min(betting_round + 1, len(player1.moves), len(player2.moves)) - 1
        
        subround = min(subround + 1, len(player1.moves[betting_round]), len(player2.moves[betting_round])) - 1

        print(subround)
        
        player1_difference = min(subround - len(player1.moves[betting_round]) + 1, 0) #find the number of sub rounds in the round to leave out 
        player2_difference = min(subround - len(player2.moves[betting_round]) + 1, 0)
        
        print(player1_difference)
        print(player2_difference)
        
        flat_player1 = [move for move_round in player1.moves for move in move_round] #get rid of the round distinctions
        flat_player2 = [move for move_round in player2.moves for move in move_round] 
        
        flat_player1 = flat_player1[0:len(flat_player1) + player1_difference] #trim the unwanted subrounds
        flat_player2 = flat_player2[0:len(flat_player2) + player2_difference]
        
        print(player1.moves)
        print(flat_player1)
        print(player2.moves)
        print(flat_player2)
        
        larger_list = max(len(flat_player1), len(flat_player2))
        
        last_raiser, raises, following_action = 0, [50.0,100.00], 'f' #set raise values to default, blind might change this
        for index in range(0, larger_list):
            if (len(flat_player1) > index):
                if flat_player1[index][0] == 'r': #if player 1 raised
                    raises.append(float(flat_player1[index][1:len(flat_player1[index])])) #add to raise list
                    if (len(flat_player2) > index):
                        following_action = flat_player2[index] #find player2's next action (check or fold)
                    else:
                        following_action = 'f' #because we don't know
                    last_raiser = 1 #remember who made this raise
            if (len(flat_player2) > index):
                if flat_player2[index][0] == 'r':
                    raises.append(float(flat_player2[index][1:len(flat_player2[index])]))
                    if (len(flat_player1) > index + 1):
                        following_action = flat_player1[index + 1] #check player1's next move (check or fold)
                    else:
                        following_action = 'f'
                    last_raiser = 2
         
        #determine how much each player bet
        if last_raiser == 1: 
            player1.chips -= raises[-1]
            if following_action == 'c': player2.chips -= raises[-1]
            if following_action == 'f': player2.chips -= raises[-2]
        else:
            player2.chips -= raises[-1]
            if following_action == 'c': player1.chips -= raises[-1]
            if following_action == 'f': player1.chips -= raises[-2]

        #pot from sum of differences of start and end
        pot = (player1.starting_chips - player1.chips) + (player2.starting_chips - player2.chips) 
        
        #return consistant order based on dict created when assigning players to turns
        return (pot, players["deepstack"].chips, players["other_player"].chips) 
        
    
class Agent(object):
    
    def __init__(self, cards, moves, position):
        self.starting_chips = 20000
        self.cards = cards
        self.moves = moves
        self.position = position