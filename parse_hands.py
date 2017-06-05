import os
import pickle
import game
        
def main():
    games = []
    for fn in os.listdir('ACPC'):
        if os.path.isfile('ACPC/' + fn) and fn != '.DS_Store':
            print(fn)
            with open('ACPC/' + fn) as f:
                for line in f:
                    print(line)
                    games.append(game.Game(line))
                
    pickle.dump( games, open( "games.p", "wb" ) )
    
    
if __name__ == "__main__":
    main()
    