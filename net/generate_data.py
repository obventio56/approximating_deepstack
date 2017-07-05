import sys
sys.path.insert(0,'..')
import pickle
import game
import time
import json

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


games = pickle.load( open( "../games.p", "rb" ) )

input_data = []
target_data = []
print(len(games))
for game_index, game in enumerate(games):
    start_time = time.time()
    print(game_index)
    for betting_round in range(1, len(game.deepstack.moves)):
        for subround, _ in enumerate(game.deepstack.moves[betting_round]):
            this_x = game.deepstack.generate_data(betting_round, subround)
            this_target = game.deepstack.generate_target(betting_round, subround)
            input_data.append(this_x)
            target_data.append(this_target)
            
    print(time.time() - start_time)
          
with open('../target.json', 'w') as outfile:
    json.dump(target_data, outfile)

with open('../input_data.json', 'w') as outfile:
    json.dump(input_data, outfile)

