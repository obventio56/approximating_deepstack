import sys
sys.path.insert(0,'..')
import pickle
import game

games = pickle.load( open( "../games.p", "rb" ) )


print(games[0].deepstack.moves)