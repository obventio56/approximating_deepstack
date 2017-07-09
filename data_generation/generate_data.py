import sys
sys.path.insert(0,'..')
import pickle
import game
import time
import json
import queue
import threading
import multiprocessing

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
input_data = []
target_data = []

def worker():
    while True:
        start_time = time.time()
        game, betting_round, subround = q.get()
        this_x = game.deepstack.generate_data(betting_round, subround)
        this_target = game.deepstack.generate_target(betting_round, subround)
        print(this_x)
        input_data.append(this_x)
        target_data.append(this_target)
        print("End Time: " + str(time.time() - start_time))
        q.task_done()
    
def main():
    games = pickle.load( open( "../games.p", "rb" ) )

    for game_index, game in enumerate(games[0:10]):
        for betting_round in range(1, len(game.deepstack.moves)):
            for subround, _ in enumerate(game.deepstack.moves[betting_round]):
                q.put((game, betting_round, subround)) 
                
    cpus=multiprocessing.cpu_count() #detect number of cores
    print("Creating %d threads" % cpus)
    for i in range(cpus):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        
    q.join()

    with open('../target.json', 'w') as outfile:
        json.dump(target_data, outfile)

    with open('../input_data.json', 'w') as outfile:
        json.dump(input_data, outfile)
        
if __name__ == "__main__":
    main()

