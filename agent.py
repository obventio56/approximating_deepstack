import sys
sys.path.insert(0,'../potentials_lookup')
import re
import numpy as np
import helpers
import lookup

class Agent(object):
    
    def __init__(self, cards, moves, position, game):
        self.starting_chips = 20000
        self.cards = cards
        self.moves = moves
        self.position = position
        self.game = game
        
    def pertinant_moves(self, end_betting_round, end_subround):
        
        if end_betting_round  >= len(self.moves): raise ValueError("Betting round out of range")
        if end_subround >= len(self.moves[end_betting_round]): raise ValueError("Subround out of range")
        
        game = self.game
          
        #initiate players in the order of turns (i.e. player1 and player2)
        player1 = game.player1
        player2 = game.player2
                   
        player1_moves, player2_moves = [], []
        
        for betting_round in range(0, end_betting_round):
            player1_moves += player1.moves[betting_round]
            player2_moves += player2.moves[betting_round]
          
        player1_end_range = end_subround
        player2_end_range = end_subround
        
        if self.position == 1:
            player1_end_range += 1
            
        if player1_end_range > 0:
            player1_moves += player1.moves[end_betting_round][0:player1_end_range]
        if player2_end_range > 0:
            player2_moves += player2.moves[end_betting_round][0:player2_end_range]
            
        if self.position == 0:
            return player1_moves, player2_moves
        else:
            return player2_moves, player1_moves

        
    def current_standing(self, end_betting_round, end_subround, when=0):

        game = self.game
        
        other_player = game.player1
        if self.position == 0:
            other_player = game.player2
        
        self.chips, other_player.chips = self.starting_chips, other_player.starting_chips #set starting chip amounts
        
        pot = 0
        self_pot = 0
        other_pot = 0

        self.occurred_moves, other_player.occurred_moves = self.pertinant_moves(end_betting_round, end_subround)
        just_raises = helpers.sorted_raises(self.occurred_moves, other_player.occurred_moves)
        
        if len(other_player.occurred_moves) < 1:
            return (self.chips, other_player.chips, pot)
        else:
            last_move = other_player.occurred_moves.pop()  if len(other_player.occurred_moves) > 0 else 'r0'

            last_raise = just_raises.pop() if len(just_raises) > 0 else 0
            second_raise = just_raises.pop() if len(just_raises) > 0 else 0
            
            other_pot = last_raise
            self_pot = other_pot
            if (last_move[0] == "r"):
                self_pot = second_raise


            pot += self_pot + other_pot
            self.chips -= self_pot
            other_player.chips -= other_pot

            return (self.chips, other_player.chips, pot)
        
    def hand_aggressivness(self, end_betting_round, end_subround):
        if end_betting_round >= len(self.moves): raise ValueError("Betting round out of range")
        if end_subround >= len(self.moves[end_betting_round]): raise ValueError("Subround out of range")
            
        game = self.game
        
        other_player = game.player1
        if self.position == 0:
            other_player = game.player2
            
        self.relevant_moves, other_player.relevant_moves = self.pertinant_moves(end_betting_round, end_subround)
        self.relevant_moves = self.relevant_moves[1:len(self.relevant_moves)]
        other_player.relevant_moves = other_player.relevant_moves[1:len(other_player.relevant_moves)]

        self_aggressivness = []
        other_player_aggressivness = []
        
        for move_index, move in enumerate(self.relevant_moves):

            betting_round, subround = helpers.get_2_d_index(move_index + 1, self)
            
            self_chips, other_player_chips, pot = self.current_standing(betting_round, subround)
            
            amount_bet = 0
            last_raise = other_player.starting_chips - other_player_chips
            second_raise = self.starting_chips - self_chips
            
            if move[0] == "r":
                amount_bet = int(move[1:len(move)]) - last_raise
            elif move == "c":
                amount_bet = last_raise - second_raise
                
            self_aggressivness.append(amount_bet/float(pot) if pot > 0 else 0)
        
        
        for move_index, move in enumerate(other_player.relevant_moves):
            betting_round, subround = helpers.get_2_d_index(move_index + 1, other_player)
            self_chips, other_player_chips, pot = other_player.current_standing(betting_round, subround)
            amount_bet = 0
            last_raise = self.starting_chips - other_player_chips
            second_raise = other_player.starting_chips - self_chips
            
            if move[0] == "r":
                amount_bet = int(move[1:len(move)]) - last_raise
            elif move == "c":
                amount_bet = last_raise - second_raise
            other_player_aggressivness.append(amount_bet/float(pot) if pot > 0 else 0)
          
    
        self_avg_aggressivness = sum(self_aggressivness)/len(self_aggressivness) if len(self_aggressivness) else 0
        other_player_avg_aggressivness = sum(other_player_aggressivness)/len(other_player_aggressivness) if len(other_player_aggressivness) else 0
        
        return self_avg_aggressivness, other_player_avg_aggressivness

    def last_move_aggressivness(self, end_betting_round, end_subround):
        
        if end_betting_round >= len(self.moves): raise ValueError("Betting round out of range")
        if end_subround >= len(self.moves[end_betting_round]): raise ValueError("Subround out of range")
            
        game = self.game
        
        other_player = game.player1
        if self.position == 0:
            other_player = game.player2
            
        self_aggressivness, other_player_aggressivness = 0, 0
        
        self.relevant_moves, other_player.relevant_moves = self.pertinant_moves(end_betting_round, end_subround)
        
        if len(self.relevant_moves) > 1:
            
            self_betting_round, self_subround = helpers.get_2_d_index(len(self.relevant_moves) - 1, self)
            
            move = self.relevant_moves[-1]

            self_chips, other_player_chips, pot = self.current_standing(self_betting_round, self_subround)

            amount_bet = 0
            last_raise = other_player.starting_chips - other_player_chips
            second_raise = self.starting_chips - self_chips

            if move[0] == "r":
                amount_bet = int(move[1:len(move)]) - last_raise
            elif move == "c":
                amount_bet = last_raise - second_raise

            self_aggressivness = (amount_bet/float(pot) if pot > 0 else 0)
        
        if len(other_player.relevant_moves) > 1:
        
            other_player_betting_round, other_player_subround = helpers.get_2_d_index(len(other_player.relevant_moves) - 1, other_player) 
             
            move = other_player.relevant_moves[-1]

            self_chips, other_player_chips, pot = other_player.current_standing(other_player_betting_round, other_player_subround)
            amount_bet = 0
            last_raise = self.starting_chips - other_player_chips
            second_raise = other_player.starting_chips - self_chips

            if move[0] == "r":
                amount_bet = int(move[1:len(move)]) - last_raise
            elif move == "c":
                amount_bet = last_raise - second_raise
            
            other_player_aggressivness = (amount_bet/float(pot) if pot > 0 else 0)
            
        return self_aggressivness, other_player_aggressivness
    
    
    def generate_data(self, end_betting_round, end_subround):
        
        game = self.game
        
        data = []
        
        data += [self.position, end_betting_round, end_subround]
        self_chips, other_chips, pot = self.current_standing(end_betting_round, end_subround)
        data += [self_chips, other_chips, pot]
        data.append(self_chips - other_chips)
        data += list(self.hand_aggressivness(end_betting_round, end_subround))
        data += list(self.last_move_aggressivness(end_betting_round, end_subround))
        game.all_cards = [game.flop, game.turn, game.river]
        community_cards = sum(game.all_cards[0:end_betting_round - 1], [])
        data.append(lookup.hand_strength(self.cards, community_cards))
        data += list(lookup.hand_potential(self.cards, community_cards))
        print(community_cards, self.cards)
        if len(community_cards) > 0:
            data.append(lookup.hand_strength([], community_cards))
            data += list(lookup.hand_potential([], community_cards))
        else:
            data.append(-1)
            data += [-1,-1]
        return data

    

    def generate_target(self, end_betting_round, end_subround):
        
        game = self.game
        
        other_player = game.player1
        if self.position == 0:
            other_player = game.player2
        
        move = self.moves[end_betting_round][end_subround]
        
        self_chips, other_player_chips, pot = self.current_standing(end_betting_round, end_subround)

        amount_bet = 0
        last_raise = other_player.starting_chips - other_player_chips
        second_raise = self.starting_chips - self_chips

        if move[0] == "r":
            amount_bet = int(move[1:len(move)]) - last_raise
        elif move == "c":
            amount_bet = last_raise - second_raise

        return (amount_bet/float(pot) if pot > 0 else 0)
                
        
        
            