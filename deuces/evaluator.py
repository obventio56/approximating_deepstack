import itertools
from .card import Card
from .deck import Deck
from .lookup import LookupTable

class Evaluator(object):
    """
    Evaluates hand strengths using a variant of Cactus Kev's algorithm:
    http://www.suffecool.net/poker/evaluator.html

    I make considerable optimizations in terms of speed and memory usage, 
    in fact the lookup table generation can be done in under a second and 
    consequent evaluations are very fast. Won't beat C, but very fast as 
    all calculations are done with bit arithmetic and table lookups. 
    """

    def __init__(self):

        self.table = LookupTable()
        
        self.hand_size_map = {
            2 : self._two,
            5 : self._five,
            6 : self._six,
            7 : self._seven
        }

    def evaluate(self, cards, *board):
        """
        This is the function that the user calls to get a hand rank. 

        Supports empty board, etc very flexible. No input validation 
        because that's cycles!
        """
        if len(board)>0 and len(board[0])>0 :
            all_cards = cards+board[0]
        else:
            all_cards = cards
        #print('cards=',cards)
        #print('board=',board)
        #print('all_cards=',all_cards)
        ncards=len(all_cards)
        if(not ncards in [2,5,6,7]):
            print("error:cards number=",ncards," is wrong")
            exit()
        return self.hand_size_map[len(all_cards)](all_cards)[0]

    def bestcards(self, cards, *board):
        """
        This is the function that the user calls to get a hand rank. 

        Supports empty board, etc very flexible. No input validation 
        because that's cycles!
        """
        if len(board)>0 and len(board[0])>0 :
            all_cards = cards+board[0]
        else:
            all_cards = cards
        #print('cards=',cards)
        #print('board=',board)
        #print('all_cards=',all_cards)
        ncards=len(all_cards)
        if(not ncards in [2,5,6,7]):
            print("error:cards number=",ncards," is wrong")
            exit()
        
        bestcds=self.hand_size_map[len(all_cards)](all_cards)[1]
        plaincard=Card.get_plain_cards(bestcds)
        return plaincard

    def _two(self, cards):
        """
        两张牌只有两种情况，对子和高牌
        对子比高排大，对子都不能是同色的
        对子数量为13种，6种配色是相同的
        高牌数量为13*12种，4种同色大于6种非同色的
        因此如果牌的大小按数字从1到最大来排序的话，共有13+C_13^2*2种等于169
        最大的同色的双A为1，最小的不同色23为169
        """
        #print("rank=",Card.get_rank_int(cards[0]),Card.get_rank_int(cards[1]))
        #print("suit=",Card.get_suit_int(cards[0]),Card.get_suit_int(cards[1]))
        rank0=Card.get_rank_int(cards[0])
        rank1=Card.get_rank_int(cards[1])
        suit0=Card.get_suit_int(cards[0])
        suit1=Card.get_suit_int(cards[1])
        tabidx=0
        if(rank0==rank1) :
            tabidx=13-rank0  #2的rank为0，A的rank为12，那么13-rank正好是A排序为1，2排序为13
        else:
            a=12-max(rank0,rank1)   #表示大数是第几个，等于12，那么a=0
            b=12-a-min(rank0,rank1) #表示小数是第几个
            c=0
            for i in range(a):
                c=c+(12-i)*2
            c=c+b*2
            if(suit0==suit1) :
                tabidx=13+c-1
            else:
                tabidx=13+c
        return [tabidx,cards]



    def _five(self, cards):
        """
        Performs an evalution given cards in integer form, mapping them to
        a rank in the range [1, 7462], with lower ranks being more powerful.

        Variant of Cactus Kev's 5 card evaluator, though I saved a lot of memory
        space using a hash table and condensing some of the calculations. 
        """
        # if flush
        if cards[0] & cards[1] & cards[2] & cards[3] & cards[4] & 0xF000:
            handOR = (cards[0] | cards[1] | cards[2] | cards[3] | cards[4]) >> 16
            prime = Card.prime_product_from_rankbits(handOR)
            return [self.table.flush_lookup[prime],cards]

        # otherwise
        else:
            prime = Card.prime_product_from_hand(cards)
            return [self.table.unsuited_lookup[prime],cards]

    def _six(self, cards):
        """
        Performs five_card_eval() on all (6 choose 5) = 6 subsets
        of 5 cards in the set of 6 to determine the best ranking, 
        and returns this ranking.
        """
        minimum = LookupTable.MAX_HIGH_CARD

        all5cardcombobs = itertools.combinations(cards, 5)
        for combo in all5cardcombobs:

            [score,bcards] = self._five(combo)
            if score < minimum:
                minimum = score
                bestcards = bcards

        return [minimum,bestcards]

    def _seven(self, cards):
        """
        Performs five_card_eval() on all (7 choose 5) = 21 subsets
        of 5 cards in the set of 7 to determine the best ranking, 
        and returns this ranking.
        """
        minimum = LookupTable.MAX_HIGH_CARD

        all5cardcombobs = itertools.combinations(cards, 5)
        for combo in all5cardcombobs:
            
            [score,bcards] = self._five(combo)
            if score < minimum:
                minimum = score
                bestcards = bcards

        return [minimum,bestcards]

    def get_rank_class(self, hr):
        """
        Returns the class of hand given the hand hand_rank
        returned from evaluate. 
        注意：分类只适用于5张以上的牌
        """
        if hr >= 0 and hr <= LookupTable.MAX_STRAIGHT_FLUSH:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_STRAIGHT_FLUSH]
        elif hr <= LookupTable.MAX_FOUR_OF_A_KIND:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_FOUR_OF_A_KIND]
        elif hr <= LookupTable.MAX_FULL_HOUSE:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_FULL_HOUSE]
        elif hr <= LookupTable.MAX_FLUSH:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_FLUSH]
        elif hr <= LookupTable.MAX_STRAIGHT:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_STRAIGHT]
        elif hr <= LookupTable.MAX_THREE_OF_A_KIND:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_THREE_OF_A_KIND]
        elif hr <= LookupTable.MAX_TWO_PAIR:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_TWO_PAIR]
        elif hr <= LookupTable.MAX_PAIR:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_PAIR]
        elif hr <= LookupTable.MAX_HIGH_CARD:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_HIGH_CARD]
        else:
            raise Exception("Inavlid hand rank, cannot return rank class")

    def class_to_string(self, class_int):
        """
        Converts the integer class hand score into a human-readable string.
        """
        return LookupTable.RANK_CLASS_TO_STRING[class_int]

    def get_five_card_rank_percentage(self, hand_rank):
        """
        Scales the hand rank score to the [0.0, 1.0] range.
        """
        return float(hand_rank) / float(LookupTable.MAX_HIGH_CARD)

    def get_two_card_rank_percentage(self, hand_rank):
        """
        Scales the hand rank score to the [0.0, 1.0] range.
        """
        return float(hand_rank) / float(169)

    #输出全局的统计
    def summarymulti(self, hands1, *board1 ):
        """
        Gives a sumamry of the hand with ranks as time proceeds. 

        Requires that the board is in chronological order for the 
        analysis to make sense.
        """
        hands=hands1
        board=board1[0]
        for player, hand in enumerate(hands):
            print("player:",player,"hand cards:",Card.get_pretty_cards(hand))
        if (len(board1)>0):
            print("board cards:",Card.get_pretty_cards(board))

        line_length = 10
        street=0
        if(len(board)>4):
            street=4
        elif(len(board)>3):
            street=3
        elif(len(board)>2):
            street=2
        else:
            street=1
        stages = ["PreFLOP","FLOP", "TURN", "RIVER"]

        for i in range(street):
            line = ("=" * line_length) + " %s " + ("=" * line_length) 
            print(line % stages[i])
            
            best_rank = 7463  # rank one worse than worst hand
            winners = []
            for player, hand in enumerate(hands):

                if(i>0) :
                    # evaluate current board position
                    rank = self.evaluate(hand, board[:(i + 2)])
                    rank_class = self.get_rank_class(rank)
                    class_string = self.class_to_string(rank_class)
                    percentage = 1.0 - self.get_five_card_rank_percentage(rank)  # higher better here
                    cards= self.bestcards(hand, board[:(i + 2)])
                    print("Player %d cards %s handrk = %s, percent in 7463 = %f" % (
                        player + 1,cards, str(rank)+"("+class_string+")", percentage))
                else:
                    rank = self.evaluate(hand)
                    cards= self.bestcards(hand)
                    percentage = 1.0 - self.get_two_card_rank_percentage(rank)  # higher better here
                    print("Player %d cards %s handrk = %s, percent in 169 = %f" % (
                        player + 1,cards, str(rank) , percentage))

                # detect winner
                if rank == best_rank:
                    winners.append(player)
                    best_rank = rank
                elif rank < best_rank:
                    winners = [player]
                    best_rank = rank

            # if we're not on the river
            if i != stages.index("RIVER"):
                if len(winners) == 1:
                    print( "Player %d hand is currently winning.\n" % (winners[0] + 1,))
                else:
                    print( "Players %s are tied for the lead.\n" % [x + 1 for x in winners])

            # otherwise on all other streets
            else:
                print()
                print( ("=" * line_length) + " HAND OVER " + ("=" * line_length) )
                if len(winners) == 1:
                    print( "Player %d is the winner with a %s\n" % (winners[0] + 1, 
                        self.class_to_string(self.get_rank_class(self.evaluate(hands[winners[0]], board)))))
                else:
                    print( "Players %s tied for the win with a %s\n" % (winners, 
                        self.class_to_string(self.get_rank_class(self.evaluate(hands[winners[0]], board)))))


    def hand_summary(self, board, hands):
        """
        Gives a sumamry of the hand with ranks as time proceeds. 

        Requires that the board is in chronological order for the 
        analysis to make sense.
        """

        assert len(board) == 5, "Invalid board length"
        for hand in hands:
            assert len(hand) == 2, "Inavlid hand length"

        line_length = 10
        stages = ["FLOP", "TURN", "RIVER"]

        for i in range(len(stages)):
            line = ("=" * line_length) + " %s " + ("=" * line_length) 
            print(line % stages[i])
            
            best_rank = 7463  # rank one worse than worst hand
            winners = []
            for player, hand in enumerate(hands):

                # evaluate current board position
                rank = self.evaluate(hand, board[:(i + 3)])
                rank_class = self.get_rank_class(rank)
                class_string = self.class_to_string(rank_class)
                percentage = 1.0 - self.get_five_card_rank_percentage(rank)  # higher better here
                print("Player %d hand = %s, percentage rank among all hands = %f" % (
                    player + 1, class_string, percentage))

                # detect winner
                if rank == best_rank:
                    winners.append(player)
                    best_rank = rank
                elif rank < best_rank:
                    winners = [player]
                    best_rank = rank

            # if we're not on the river
            if i != stages.index("RIVER"):
                if len(winners) == 1:
                    print( "Player %d hand is currently winning.\n" % (winners[0] + 1,))
                else:
                    print( "Players %s are tied for the lead.\n" % [x + 1 for x in winners])

            # otherwise on all other streets
            else:
                print()
                print( ("=" * line_length) + " HAND OVER " + ("=" * line_length) )
                if len(winners) == 1:
                    print( "Player %d is the winner with a %s\n" % (winners[0] + 1, 
                        self.class_to_string(self.get_rank_class(self.evaluate(hands[winners[0]], board)))))
                else:
                    print( "Players %s tied for the win with a %s\n" % (winners, 
                        self.class_to_string(self.get_rank_class(self.evaluate(hands[winners[0]], board)))))



