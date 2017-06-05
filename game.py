import re

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
        
        moves1, moves2 = self.parse_moves(data[1])
        
        cards1, cards2, self.flop, self.turn, self.river = return_value = self.parse_cards(data[2], 5)
        
        agent1 = Agent(cards1, moves1)
        agent2 = Agent(cards2, moves2)
        
        if (player1 == 'DeepStack'):
            self.deepstack = agent1
            self.other_player = agent2
        else:
            self.deepstack = agent2
            self.deepstack = agent1

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
                                
        
    
class Agent(object):
    
    def __init__(self, cards, moves):
        self.starting_chips = 20000
        self.cards = cards
        self.moves = moves