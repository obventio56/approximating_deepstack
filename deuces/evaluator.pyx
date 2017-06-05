# cython: profile=True
import itertools
from .card import Card
from .deck import Deck
from .lookup import LookupTable
from magic_numbers cimport *
cimport cython
cimport libc.stdlib as stdlib

cdef int * _PRIMES_13

cdef int prime_product_from_hand_cython(int *cards, int n):
    cdef int product, c, i
    i = 0
    product = 1
    while i < n:
        c = cards[i]
        product *= (c & 0xFF)
        i += 1
    return product

cdef void _init_primes():
    global _PRIMES_13
    _PRIMES_13 = <int *> stdlib.malloc(13 * cython.sizeof(int) )
    for i in range(13):
        _PRIMES_13[i] = Card.PRIMES[i]

cdef int prime_product_from_rankbits_cython(int rankbits):
    cdef int product, i
    product = 1
    i = 0
    global _PRIMES_13
    if(<long>_PRIMES_13 == 0):
        _init_primes()
    while i < 13:
        if rankbits & (1 << i):
            product *= _PRIMES_13[i]
        i += 1

    return product

cdef class Evaluator(object):
    """
    Evaluates hand strengths using a variant of Cactus Kev's algorithm:
    http://suffe.cool/poker/evaluator.html

    I make considerable optimizations in terms of speed and memory usage, 
    in fact the lookup table generation can be done in under a second and 
    consequent evaluations are very fast. Won't beat C, but very fast as 
    all calculations are done with bit arithmetic and table lookups. 
    """
    cdef object table
    cdef dict hand_size_map

    def __init__(self):

        self.table = LookupTable()
        
        self.hand_size_map = {
            5 : self._five,
            6 : self._six,
            7 : self._seven
        }

    def evaluate(self, cards, board):
        """
        This is the function that the user calls to get a hand rank. 

        Supports empty board, etc very flexible. No input validation 
        because that's cycles!
        """
        all_cards = cards + board
        return self.hand_size_map[len(all_cards)](all_cards)

    def _five(self, py_cards):
        """
        Performs an evalution given cards in integer form, mapping them to
        a rank in the range [1, 7462], with lower ranks being more powerful.

        Variant of Cactus Kev's 5 card evaluator, though I saved a lot of memory
        space using a hash table and condensing some of the calculations. 
        """
        cdef int *cards
        cdef int i, prime, handOR

        cards = <int *>stdlib.malloc(5 * cython.sizeof(int))
        i = 0
        while i < 5:
            cards[i] = py_cards[i]
            i = i + 1
        # if flush
        if cards[0] & cards[1] & cards[2] & cards[3] & cards[4] & 0xF000:
            handOR = (cards[0] | cards[1] | cards[2] | cards[3] | cards[4]) >> 16
            prime = prime_product_from_rankbits_cython(handOR)
            stdlib.free(cards)
            return self.table.flush_lookup[prime]

        # otherwise
        else:
            prime = prime_product_from_hand_cython(cards, 5)
            stdlib.free(cards)
            return self.table.unsuited_lookup[prime]

    def _six(self, cards):
        """
        Performs five_card_eval() on all (6 choose 5) = 6 subsets
        of 5 cards in the set of 6 to determine the best ranking, 
        and returns this ranking.
        """
        minimum = MAX_VALUE.MAX_HIGH_CARD

        all5cardcombobs = itertools.combinations(cards, 5)
        for combo in all5cardcombobs:

            score = self._five(combo)
            if score < minimum:
                minimum = score

        return minimum

    cpdef int _five_cython(self, long p_cards):
        #FIXME: Can't pass int*  Don't know the reason
        cdef int *cards
        cdef int prime, handOR

        cards = <int *>p_cards
        # if flush
        if cards[0] & cards[1] & cards[2] & cards[3] & cards[4] & 0xF000:
            handOR = (cards[0] | cards[1] | cards[2] | cards[3] | cards[4]) >> 16
            prime = prime_product_from_rankbits_cython(handOR)
            return self.table.flush_lookup[prime]
        # otherwise
        else:
            prime = prime_product_from_hand_cython(cards, 5)
            return self.table.unsuited_lookup[prime]

    def _seven(self, cards):
        """
        Performs five_card_eval() on all (7 choose 5) = 21 subsets
        of 5 cards in the set of 7 to determine the best ranking, 
        and returns this ranking.
        """
        cdef int minimum
        cdef int score
        minimum = MAX_VALUE.MAX_HIGH_CARD

        cdef int * p_cards
        cdef int i
        p_cards = <int *>stdlib.malloc(5 * cython.sizeof(int))

        cdef tuple all5cardcombobs
        cdef tuple combo

        all5cardcombobs = tuple(itertools.combinations(cards, 5))
        for combo in all5cardcombobs:
            i = 0
            while i < 5:
                p_cards[i] = combo[i]
                i = i + 1
            score = self._five_cython(<long>p_cards)
            if score < minimum:
                minimum = score
        stdlib.free(p_cards)

        return minimum

    def get_rank_class(self, int hr):
        """
        Returns the class of hand given the hand hand_rank
        returned from evaluate. 
        """
        if hr >= 0 and hr <= MAX_VALUE.MAX_STRAIGHT_FLUSH:
            return self.table.MAX_TO_RANK_CLASS[MAX_VALUE.MAX_STRAIGHT_FLUSH]
        elif hr <= MAX_VALUE.MAX_FOUR_OF_A_KIND:
            return self.table.MAX_TO_RANK_CLASS[MAX_VALUE.MAX_FOUR_OF_A_KIND]
        elif hr <= MAX_VALUE.MAX_FULL_HOUSE:
            return self.table.MAX_TO_RANK_CLASS[MAX_VALUE.MAX_FULL_HOUSE]
        elif hr <= MAX_VALUE.MAX_FLUSH:
            return self.table.MAX_TO_RANK_CLASS[MAX_VALUE.MAX_FLUSH]
        elif hr <= MAX_VALUE.MAX_STRAIGHT:
            return self.table.MAX_TO_RANK_CLASS[MAX_VALUE.MAX_STRAIGHT]
        elif hr <= MAX_VALUE.MAX_THREE_OF_A_KIND:
            return self.table.MAX_TO_RANK_CLASS[MAX_VALUE.MAX_THREE_OF_A_KIND]
        elif hr <= MAX_VALUE.MAX_TWO_PAIR:
            return self.table.MAX_TO_RANK_CLASS[MAX_VALUE.MAX_TWO_PAIR]
        elif hr <= MAX_VALUE.MAX_PAIR:
            return self.table.MAX_TO_RANK_CLASS[MAX_VALUE.MAX_PAIR]
        elif hr <= MAX_VALUE.MAX_HIGH_CARD:
            return self.table.MAX_TO_RANK_CLASS[MAX_VALUE.MAX_HIGH_CARD]
        else:
            raise Exception("Inavlid hand rank, cannot return rank class")

    def class_to_string(self, class_int):
        """
        Converts the integer class hand score into a human-readable string.
        """
        return self.table.RANK_CLASS_TO_STRING[class_int]

    def get_five_card_rank_percentage(self, hand_rank):
        """
        Scales the hand rank score to the [0.0, 1.0] range.
        """
        return float(hand_rank) / float(MAX_VALUE.MAX_HIGH_CARD)

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
            print((line % stages[i]))
            
            best_rank = 7463  # rank one worse than worst hand
            winners = []
            for player, hand in enumerate(hands):

                # evaluate current board position
                rank = self.evaluate(hand, board[:(i + 3)])
                rank_class = self.get_rank_class(rank)
                class_string = self.class_to_string(rank_class)
                percentage = 1.0 - self.get_five_card_rank_percentage(rank)  # higher better here
                print(("Player %d hand = %s, percentage rank among all hands = %f" % (
                    player + 1, class_string, percentage)))

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
                    print(("Player %d hand is currently winning.\n" % (winners[0] + 1,)))
                else:
                    print(("Players %s are tied for the lead.\n" % [x + 1 for x in winners]))

            # otherwise on all other streets
            else:
                print()
                print((("=" * line_length) + " HAND OVER " + ("=" * line_length))) 
                if len(winners) == 1:
                    print(("Player %d is the winner with a %s\n" % (winners[0] + 1, 
                        self.class_to_string(self.get_rank_class(self.evaluate(hands[winners[0]], board))))))
                else:
                    print(("Players %s tied for the win with a %s\n" % (winners, 
                        self.class_to_string(self.get_rank_class(self.evaluate(hands[winners[0]], board))))))



