import random
import itertools
from collections import Counter

SUITS =["H", "D", "C", "S"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
HAND_RANKS = {r : i for i, r in enumerate(RANKS)}
FULL_DECK = [r + s for r in RANKS for s in SUITS]

def card_name(card):
    return ' '.join(card)

def card(s):
    if not s: return []
    return [s[i:i+2] for i in range(0, len(s), 2)]

class HandEvaluator:
    @staticmethod
    def evaluate_hand(hole_cards, community_cards):
        all_cards = hole_cards + community_cards
        best_rank = 0
        for combo in itertools.combinations(all_cards, 5):
            rank = HandEvaluator.rank_hand(combo)
            best_rank = max(best_rank, rank)
        return best_rank

    @staticmethod
    def rank_hand(cards):
        ranks = sorted([HAND_RANKS[c[:-1]] for c in cards], reverse=True)
        suits = [c[-1] for c in cards]
        is_flush = len(set(suits)) == 1
        is_straight = ranks == list(range(ranks[0], ranks[0] - 5, -1))
        rank_counts = Counter(ranks).values()

        if is_straight and is_flush and ranks[0] == HAND_RANKS['A']:
            return 10  # Royal Flush
        if is_straight and is_flush:
            return 9   # Straight Flush
        if 4 in rank_counts:
            return 8   # Four of a Kind
        if 3 in rank_counts and 2 in rank_counts:
            return 7   # Full House
        if is_flush:
            return 6   # Flush
        if is_straight:
            return 5   # Straight
        if 3 in rank_counts:
            return 4   # Three of a Kind
        if list(rank_counts).count(2) == 2:
            return 3   # Two Pair
        if 2 in rank_counts:
            return 2   # One Pair
        return 1       # High Card