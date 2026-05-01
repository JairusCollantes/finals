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
        vals = sorted([HAND_RANKS[c[0]] for c in cards], reverse=True)
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

class PokerGame:
    def __init__(self, player_chips=1000, ai_chips=1000):
        self.player_chips = player_chips
        self.ai_chips = ai_chips
        self.deck = []
        self.player_hand = []
        self.ai_hand = []
        self.community = []
        self.pot = 0
        self.current_bet = 0
        self.player_bet_this_round = 0
        self.ai_bet_this_round = 0
        self.street = 0 
        self.hand_over = True

    def new_hand(self):
        if self.player_chips <= 0 or self.ai_chips <= 0:
            return False
        self.deck = FULL_DECK[:]
        random.shuffle(self.deck)
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.ai_hand = [self.deck.pop(), self.deck.pop()]
        self.community = []
        self.pot = 0
        self.current_bet = 10         
        self.player_bet_this_round = 5
        self.ai_bet_this_round = 10
        self.player_chips -= 5
        self.ai_chips -= 10
        self.pot = 15
        self.street = 0
        self.hand_over = False
        return True

    def deal_community(self):
        if self.street == 0:
            self.deck.pop()
            self.community += [self.deck.pop() for _ in range(3)]  # flop
            self.street = 1
        elif self.street == 1:
            self.deck.pop()
            self.community.append(self.deck.pop())  # turn
            self.street = 2
        elif self.street == 2:
            self.deck.pop()
            self.community.append(self.deck.pop())  # river
            self.street = 3
        self.player_bet_this_round = 0
        self.ai_bet_this_round = 0
        self.current_bet = 0

    def player_fold(self):
        self.ai_chips += self.pot
        self.hand_over = True
        return 'fold'

    def player_call(self):
        diff = self.current_bet - self.player_bet_this_round
        self.player_chips -= diff
        self.pot += diff
        self.player_bet_this_round = self.current_bet
        return 'call'

    def player_raise(self, amount=20):
        self.current_bet = amount
        diff = amount - self.player_bet_this_round
        self.player_chips -= diff
        self.pot += diff
        self.player_bet_this_round = amount
        return 'raise'

    def ai_decision(self):
        if len(self.community) >= 3:
            rank, _ = HandEvaluator.evaluate(self.ai_hand + self.community)
        else:
            rank = 0
        if random.random() < rank / 15: 
            self.ai_raise(20)
            return 'raise'
        else:
            self.ai_call()
            return 'call'

    def ai_call(self):
        diff = self.current_bet - self.ai_bet_this_round
        self.ai_chips -= diff
        self.pot += diff
        self.ai_bet_this_round = self.current_bet

    def ai_raise(self, amount=20):
        self.current_bet = amount
        diff = amount - self.ai_bet_this_round
        self.ai_chips -= diff
        self.pot += diff
        self.ai_bet_this_round = amount

    def showdown(self):
        player_rank, player_high = HandEvaluator.evaluate(self.player_hand + self.community)
        ai_rank, ai_high = HandEvaluator.evaluate(self.ai_hand + self.community)
        if player_rank > ai_rank or (player_rank == ai_rank and player_high > ai_high):
            self.player_chips += self.pot
            result = 'win'
        elif player_rank < ai_rank or (player_rank == ai_rank and player_high < ai_high):
            self.ai_chips += self.pot
            result = 'loss'
        else:
            self.player_chips += self.pot // 2
            self.ai_chips += self.pot - self.pot // 2
            result = 'tie'
        self.hand_over = True
        return result
    def get_state(self):
        return {
            "player_hand": self.player_hand,
            "ai_hand": self.ai_hand,
            "community": self.community,
            "pot": self.pot,
            "player_chips": self.player_chips,
            "ai_chips": self.ai_chips
        }