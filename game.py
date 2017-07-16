import re
import numpy as np
import helpers
from agent import *

class Game(object):
    
    def __init__(self, line, small_blind, big_blind):
        
        self.id = 0
        self.flop = []
        self.turn = []
        self.river = []
        self.all_cards = [self.flop, self.turn, self.river]
        self.small_blind = small_blind
        self.big_blind = big_blind
        
        self.parse_acpc(line)

        
    def parse_acpc(self, line):
        lineMatch = re.match( r'STATE:(.*) # (.*)', line)
        data = lineMatch.group(1).split(":")
        self.id = int(data[0])
        
        
        player1, player2 = re.split('\|', data[4])
        
        moves1, moves2 = self.parse_moves(data[1])
        
        print(data[2])
        cards1, cards2, self.flop, self.turn, self.river = return_value = self.parse_cards(data[2], 5)
        print(cards1, cards2)
        
        self.player1 = Agent(cards1, moves1, 0, self)
        self.player2 = Agent(cards2, moves2, 1, self)
        
        if (player1 == 'DeepStack'):
            self.deepstack = self.player1
            self.other_player = self.player2
            self.other_player_name = player2
        else:
            self.deepstack = self.player2
            self.other_player = self.player1
            self.other_player_name = player1

    def parse_cards(self, card_string, expected_groups):
        
        card_groups = []
        groups = re.split(r'\||\/', card_string)
        for group in groups:
            cards_in_group = re.findall('(?:[QKTJA]|[2-9]|10)[hdsc]', group)
            card_groups.append(cards_in_group)
            
        card_groups += [list()]*(expected_groups - len(card_groups))
        return tuple(card_groups)
    
    def parse_moves(self, moves_string):
        
        moves1, moves2 = [], []
        
        move_groups = re.split('\/', moves_string)
        for index, group in enumerate(move_groups):
            moves = re.findall('[cf]|r[\d]+', group)
            if index == 0:
                moves2.append(moves[0::2] if moves[0::2] != [] else ['s'])
                moves1.append(moves[1::2] if moves[1::2] != [] else ['s'])
            else:
                moves1.append(moves[0::2] if moves[0::2] != [] else ['s'])
                moves2.append(moves[1::2] if moves[1::2] != [] else ['s'])

        moves1.insert(0, ['r' + str(self.big_blind)])  
        moves2.insert(0, ['r' + str(self.small_blind)])

        return moves1, moves2
    
    def all_moves(self):
        all_moves = []
        
        all_moves.append([[self.player2.moves[0][0], 1], 
                          [self.player1.moves[0][0], 0]]) #small blind and big blind
        
        #pre-flop the small blind moves first
        all_moves.append(helpers.combine_moves(self.player2.moves[1], self.player1.moves[1], 1, 0)) 
        
        for remaining_round in range(2, len(self.player1.moves)):
            all_moves.append(helpers.combine_moves(self.player1.moves[remaining_round], self.player2.moves[remaining_round], 0, 1))
            
        return all_moves
        
    def get_all_cards(self):
        return [self.flop, self.turn, self.river]
        

        
    

                