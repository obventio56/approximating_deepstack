import re
import numpy as np
import helpers

class Game(object):
    
    def __init__(self, line, small_blind, big_blind):
        
        self.id = 0
        self.flop = []
        self.turn = []
        self.river = []
        self.small_blind = small_blind
        self.big_blind = big_blind
        
        self.parse_acpc(line)

        
    def parse_acpc(self, line):
        lineMatch = re.match( r'STATE:(.*) # (.*)', line)
        data = lineMatch.group(1).split(":")
        self.id = int(data[0])
        
        player2, player1 = re.split('\|', data[4])
        
        moves1, moves2 = self.parse_moves(data[1])
        
        cards1, cards2, self.flop, self.turn, self.river = return_value = self.parse_cards(data[2], 5)
        
        self.player1 = Agent(cards1, moves1, 0, self)
        self.player2 = Agent(cards2, moves2, 1, self)
        
        if (player1 == 'DeepStack'):
            self.deepstack = self.player1
            self.other_player = self.player2
        else:
            self.deepstack = self.player2
            self.other_player = self.player1

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
            
        moves1.insert(0, ['r' + str(self.small_blind)])
        moves2.insert(0, ['r' + str(self.big_blind)])

        return moves1, moves2

        
    
class Agent(object):
    
    def __init__(self, cards, moves, position, game):
        self.starting_chips = 20000
        self.cards = cards
        self.moves = moves
        self.position = position
        self.game = game
        
    def pertinant_moves(self, end_betting_round, end_subround):
        
        print(self.moves)
        if end_betting_round  >= len(self.moves): raise ValueError("Betting round out of range")
        if end_subround >= len(self.moves[end_betting_round]): raise ValueError("Subround out of range")
        
        game = self.game
          
        #initiate players in the order of turns (i.e. player1 and player2)
        player1 = game.player1
        player2 = game.player2
        
                        
        pertinent_moves = []
        
        for betting_round in range(0, end_betting_round):
            pertinent_moves += helpers.merge_lists(player1.moves[betting_round], player2.moves[betting_round])
          
        player1_end_range = end_subround
        player2_end_range = end_subround + 1
        
        if self.position == 0:
            player2_end_range -= 1
            
        print(player1_end_range, player2_end_range)
                       
        player1_last_round = player1.moves[end_betting_round][0:player1_end_range]
        player2_last_round = player2.moves[end_betting_round][0:player2_end_range]
        
        pertinent_moves += helpers.merge_lists(player1_last_round, player2_last_round)
        
        return pertinent_moves
        
    def current_standing(self, end_betting_round, end_subround):

        game = self.game
        
        other_player = game.player1
        if self.position == 0:
            other_player = game.player2
        
        self.chips, other_player.chips = self.starting_chips, other_player.starting_chips #set starting chip amounts
        
        pot = 0
        self_pot = 0
        other_pot = 0
        
        pertinent_moves = self.pertinant_moves(end_betting_round, end_subround)
        
        just_raises = [bet_raise for bet_raise in pertinent_moves if bet_raise[0] == "r"]
        print(pertinent_moves)
        last_raise = just_raises.pop()
        second_raise = just_raises.pop()
        
        other_pot = int(last_raise[1:len(last_raise)])
        self_pot = other_pot
        if (pertinent_moves[-1][0] == "r"):
            self_pot = int(second_raise[1:len(second_raise)])
        
            
        pot += self_pot + other_pot
        self.chips -= self_pot
        other_player.chips -= other_pot
        
        return (self.chips, other_player.chips, pot)

                