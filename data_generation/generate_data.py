import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../potentials_lookup')
import pickle
import game
import agent
import time
import json
import queue
import threading
import multiprocessing
import lookup
import numpy as np

# Input data:
#    Position (0 or 1) +
#    Round (pre-flop, post-flop etc) +
#    Pot+
#    Minimum bet to call + 
#    Deepstack chips +
#    Deepstack aggresivness prior move -> amount bet/pot
#    Deepstack aggresivness cumulative -> amount bet/pot
#    Hand strength
#    Hand potential
#    Opponent chips + 
#    Opponent aggressivness prior move
#    Opponent aggressivness cumulative for the game
#    Community card strength
#    Community card potential



# Target data:
#    Action probabilites
#    Agressivness

q = queue.Queue()
x_data = []
y_data = []

def generate_data(game):
    input_data = []
    target_data = []
    
    deepstack_position = game.deepstack.position
    
    deepstack_subround_index = 0
    other_player_subround_index = 0
        
    deepstack_last_bet = float(game.deepstack.moves[0][0][1:len(game.deepstack.moves[0][0])])
    other_player_last_bet = float(game.other_player.moves[0][0][1:len(game.other_player.moves[0][0])])
    
    pot = deepstack_last_bet + other_player_last_bet
    
    deepstack_chips = game.deepstack.starting_chips - deepstack_last_bet
    other_player_chips = game.other_player.starting_chips - other_player_last_bet

    deepstack_hand_aggressivness = []
    other_player_hand_aggressivness = []
    
    community_cards = []
    
    all_moves = game.all_moves()
    all_cards = game.get_all_cards()
        
    for betting_round in range(1, len(all_moves)):
        deepstack_subround_index, other_player_subround_index = 0, 0
        
        if betting_round > 1:
            community_cards += all_cards[betting_round - 2]
        
        for move_index, move in enumerate(all_moves[betting_round]):
            
            if move[1] == deepstack_position:
                amount_bet = 0.0
                this_bet = 0.0
                if move[0][0] == 'r':
                    amount_bet = float(move[0][1:len(move[0])]) - deepstack_last_bet
                    this_bet = float(move[0][1:len(move[0])])
                elif move[0] == 'c':
                    amount_bet = other_player_last_bet - deepstack_last_bet
                    this_bet = other_player_last_bet
                    
                aggressivness = amount_bet/pot
                
                if move[0] == 'f': aggressivness = -1.0
                
                data_point = [game.id, game.other_player_name, betting_round, deepstack_subround_index]
                data_point += [deepstack_chips, other_player_chips, pot]
                data_point.append(other_player_last_bet - deepstack_last_bet)
                
                if (len(deepstack_hand_aggressivness) > 0):
                    data_point.append(np.mean(np.array(deepstack_hand_aggressivness)))
                    data_point.append(deepstack_hand_aggressivness[-1])
                else:
                    data_point += [0.0, 0.0]
                if (len(other_player_hand_aggressivness) > 0):
                    data_point.append(np.mean(np.array(other_player_hand_aggressivness)))
                    data_point.append(other_player_hand_aggressivness[-1])
                else:
                    data_point += [0.0, 0.0]
                    
                data_point.append(lookup.hand_strength(game.deepstack.cards, community_cards))
                data_point += list(lookup.hand_potential(game.deepstack.cards, community_cards)) 
                
                if len(community_cards) > 0:
                    data_point.append(lookup.hand_strength([], community_cards))
                    data_point += list(lookup.hand_potential([], community_cards))
                else:
                    data_point.append(-1)
                    data_point += [-1,-1]
                    
                print(data_point)
                print(aggressivness)
                input_data.append(data_point)
                target_data.append(aggressivness)
                    
                deepstack_hand_aggressivness.append(aggressivness)
                pot += amount_bet
                deepstack_chips -= amount_bet
                deepstack_last_bet = this_bet
                deepstack_subround_index += 1
                
            else:
                
                amount_bet = 0.0
                if move[0][0] == 'r':
                    amount_bet = float(move[0][1:len(move[0])]) - other_player_last_bet
                    other_player_last_bet = float(move[0][1:len(move[0])])
                elif move[0] == 'c':
                    amount_bet = deepstack_last_bet - other_player_last_bet
                    other_player_last_bet = deepstack_last_bet
                    
                other_player_hand_aggressivness.append(amount_bet/pot)
                pot += amount_bet
                other_player_chips -= amount_bet
                other_player_subround_index += 1
                
    return input_data, target_data

def worker():
    global x_data
    global y_data
    while True:
        start_time = time.time()
        game = q.get()
        this_x, this_target = generate_data(game)
        x_data += this_x
        y_data += this_target
        print("End Time: " + str(time.time() - start_time))
        q.task_done()
    
def main():
    games = pickle.load( open( "../games.p", "rb" ) )

    for game_index, game in enumerate(games[0:300]):
        q.put((game)) 
                
    cpus=multiprocessing.cpu_count() #detect number of cores
    print("Creating %d threads" % cpus)
    for i in range(cpus - 3):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        
    q.join()

    with open('../target.json', 'w') as outfile:
        json.dump(y_data, outfile)

    with open('../input_data.json', 'w') as outfile:
        json.dump(x_data, outfile)
        
if __name__ == "__main__":
    main()

