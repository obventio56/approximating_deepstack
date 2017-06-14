def merge_lists(list1, list2):
    list_len = max(len(list1), len(list2))
    
    final_list = []
    
    for element in range(0, list_len):
        if len(list1) > element: final_list.append(list1[element])
        if len(list2) > element: final_list.append(list2[element])
            
    return final_list

