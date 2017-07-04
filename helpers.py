def merge_lists(list1, list2):
    list_len = max(len(list1), len(list2))
    
    final_list = []
    
    for element in range(0, list_len):
        if len(list1) > element: final_list.append(list1[element])
        if len(list2) > element: final_list.append(list2[element])
            
    return final_list

def sorted_raises(player1_moves, player2_moves):
    player1_raises = [int(betting_raise[1:len(betting_raise)]) for betting_raise in player1_moves if betting_raise[0] == "r"]
    player2_raises = [int(betting_raise[1:len(betting_raise)]) for betting_raise in player2_moves if betting_raise[0] == "r"]
    
    all_raises = player1_raises + player2_raises
    
    all_raises.sort()
    
    return all_raises
    
def get_2_d_index(moves, player):
    end_betting_round = 0
    for betting_round, _ in enumerate(player.moves):
        if moves >= len(player.moves[betting_round]):
            moves -= len(player.moves[betting_round])
            end_betting_round += 1
        else: break
    return end_betting_round, moves
