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
    def evaluate(cards):
        if len(cards) < 5:
            return (0, ())
        best = (0, ())
        for combo in itertools.combinations(cards, 5):
            r, h = HandEvaluator._eval_5(combo)
            if r > best[0] or (r == best[0] and h > best[1]):
                best = (r, h)
        return best

    @staticmethod
    def _eval_5(cards):
        vals = sorted([RANK_VALUES[c[0]] for c in cards], reverse=True)
        suits = [c[1] for c in cards]
        is_flush = len(set(suits)) == 1
        unique = sorted(set(vals), reverse=True)
        is_straight = False
        straight_high = None
        if len(unique) == 5 and unique[0] - unique[-1] == 4:
            is_straight = True
            straight_high = unique[0]
        elif set(vals) == {12,0,1,2,3}:
            is_straight = True
            straight_high = 3

        cnt = Counter(vals)
        counts = sorted(cnt.values(), reverse=True)

        # Formal logic cascade
        if is_flush and is_straight:
            return (9, (straight_high,))
        elif counts == [4,1]:
            q = [k for k,v in cnt.items() if v==4][0]
            k = [k for k in cnt if cnt[k]==1][0]
            return (8, (q, k))
        elif counts == [3,2]:
            t = [k for k,v in cnt.items() if v==3][0]
            p = [k for k,v in cnt.items() if v==2][0]
            return (7, (t, p))
        elif is_flush:
            return (6, tuple(sorted(vals, reverse=True)))
        elif is_straight:
            return (5, (straight_high,))
        elif counts == [3,1,1]:
            t = [k for k,v in cnt.items() if v==3][0]
            kk = sorted([k for k in cnt if cnt[k]==1], reverse=True)
            return (4, (t, *kk))
        elif counts == [2,2,1]:
            pairs = sorted([k for k,v in cnt.items() if v==2], reverse=True)
            kk = [k for k in cnt if cnt[k]==1][0]
            return (3, (pairs[0], pairs[1], kk))
        elif counts == [2,1,1,1]:
            p = [k for k,v in cnt.items() if v==2][0]
            kk = sorted([k for k in cnt if cnt[k]==1], reverse=True)
            return (2, (p, *kk))
        else:
            return (1, tuple(sorted(vals, reverse=True)))

class RangeAnalyzer:
    def __init__(self, db):
        self.db = db

    def get_opponent_range(self, opponent_id, known_cards):
        used = set(known_cards)
        if self.db:
            hist = self.db.get_opponent_hands(opponent_id, 200)
            hands_set = set()
            for h in hist:
                c = card(h)
                if len(c) == 2:
                    hands_set.add(tuple(sorted(c)))
            if hands_set:
                return [c for c in hands_set if not set(c) & used]
        available = [c for c in FULL_DECK if c not in used]
        return list(itertools.combinations(available, 2))

def calc_win_probability(my_hand, community, opponent_range):
    my_rank, my_high = HandEvaluator.evaluate(my_hand + community)
    wins = 0
    total = 0
    for opp in opponent_range:
        opp_rank, opp_high = HandEvaluator.evaluate(list(opp) + community)
        if my_rank > opp_rank or (my_rank == opp_rank and my_high > opp_high):
            wins += 1
        total += 1
    return wins / total if total > 0 else 0.5

