import sys
sys.path.insert(0,'..')
import pickle
import game


### Input data:
###    Position (0 or 1)
###    Round (pre-flop, post-flop etc)
###    Pot
###    Minimum bet to call
###    Deepstack chips
###    Deepstack aggresivness prior move -> amount bet/pot
###    Deepstack aggresivness cumulative -> amount bet/pot
###    Hand strength
###    Hand potential
###    Opponent chips
###    Opponent aggressivness prior move
###    Opponent aggressivness cumulative for the game


### Target data:
###    Action probabilites
###    Agressivness


games = pickle.load( open( "../games.p", "rb" ) )

for game in games:
    print(game.current_standing(1,1))

