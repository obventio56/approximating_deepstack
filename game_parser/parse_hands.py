import sys
sys.path.insert(0,'..')
import os
import pickle
import game
        
def main():
    games = []
    for fn in os.listdir('../ACPC'):
        if os.path.isfile('../ACPC/' + fn) and fn != '.DS_Store':
            print(fn)
            with open('../ACPC/' + fn) as f:
                counter = 0
                for line in f:
                    print(counter)
                    counter += 1
                    print(line)
                    this_game = game.Game(line, 50, 100)
                    print(this_game.deepstack.moves)
                    games.append(this_game)
                
    pickle.dump( games, open( "../games.p", "wb" ) )
    
    
if __name__ == "__main__":
    main()
    