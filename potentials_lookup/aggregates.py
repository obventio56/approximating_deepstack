        probability = 1
        for depth in range(len(hand_cards), length):
            probability *= 1/(float(52 - depth))
            
        mean = sum(strengths)*probability
        
        
        standard_deviation = 0
        for x in strengths:
            standard_deviation += x**2  
        standard_deviation *= probability
        standard_deviation -=  mean**2
        
        print("pre-return complete")
        difference = time.time() - pre_return.pop()
        print("Time: " + str(difference))
        print("End: " + Card.print_pretty_cards(hand_cards))

        return (hand_cards, mean, standard_deviation)