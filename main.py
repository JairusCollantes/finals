import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt6 import uic
from PyQt6.QtCore import QTimer
from db import DB
from poker import PokerGame, calc_win_probability, RangeAnalyzer

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("ui/menu.ui", self)

        self.db = None

        self.setup_menu()

        QTimer.singleShot(0, self.init_db)

    def init_db(self):
        self.db = DB()
        
    def setup_menu(self):
        self.btn_start_game.clicked.connect(self.open_game)
        self.btn_history.clicked.connect(self.open_history)
        self.btn_reset.clicked.connect(self.clear_history)
        self.btn_exit.clicked.connect(self.close)
        
    def clear_history(self):
        self.db.clear_history()
        
    def log(self, message):
        if hasattr(self, 'log_output'):
            self.log_output.appendPlainText(message)
            self.log_output.verticalScrollBar().setValue(
                self.log_output.verticalScrollBar().maximum()
            )
    def open_game(self):
        uic.loadUi("ui/game.ui", self)
        self.setup_game()
    
    def setup_game(self):
        if not hasattr(self, "game"):
            self.game = PokerGame()
            self.range = RangeAnalyzer(self.db)

        self.game.new_hand()

        self.btn_new_hand.clicked.connect(self.new_hand)
        self.btn_call.clicked.connect(self.call)
        self.btn_fold.clicked.connect(self.fold)
        self.btn_raise.clicked.connect(self.raise_bet)
        self.btn_back.clicked.connect(self.back_to_menu)

        self.update_game_ui()
        
    def new_hand(self):
        self.game.new_hand()
        self.update_game_ui()
        self.log("--- New hand ---")
        self.log(f"Player: {self.game.player_hand[0]} {self.game.player_hand[1]}")
        self.log(f"Pot: {self.game.pot}")

    def call(self):
        self.game.player_call()
        self.log("Player calls")
        self.ai_turn()
        self.after_action()

    def fold(self):
        self.game.player_fold()
        self.log("Player folds")
        self.save_result("fold")
        self.after_action()          # <-- after_action already calls update_game_ui; we'll add auto-start there

    def raise_bet(self):
        self.game.player_raise(20)
        self.log("Player raises to 20")
        self.ai_turn()
        self.after_action()

    def ai_turn(self):
        decision = self.game.ai_decision()
        self.log(f"AI {decision}s")
        if self.game.street < 3:
            self.game.deal_community()
            if self.game.street == 1:
                self.log("Flop dealt: " + " ".join(self.game.community[0:3]))
            elif self.game.street == 2:
                self.log("Turn: " + self.game.community[3])
            elif self.game.street == 3:
                self.log("River: " + self.game.community[4])

    def after_action(self):
        if self.game.street >= 3:
            result = self.game.showdown()
            self.save_result(result)
            self.log(f"Showdown: Player {result} (Hand: {' '.join(self.game.player_hand)} vs AI: {' '.join(self.game.ai_hand)})")
            self.log(f"Pot: {self.game.pot} awarded")

        self.update_game_ui()
        self.update_probability()

        if self.game.hand_over:
            self.log("Hand finished. Next hand in 2 seconds...")
            self.btn_call.setEnabled(False)
            self.btn_fold.setEnabled(False)
            self.btn_raise.setEnabled(False)
            QTimer.singleShot(2000, self.auto_new_hand)

    def auto_new_hand(self):
        self.btn_call.setEnabled(True)
        self.btn_fold.setEnabled(True)
        self.btn_raise.setEnabled(True)
        self.new_hand()

    def update_game_ui(self):
        state = self.game.get_state()

        self.lbl_player_card1.setText(state["player_hand"][0])
        self.lbl_player_card2.setText(state["player_hand"][1])

        self.lbl_pot.setText(f"Pot: {state['pot']}")
        self.lbl_player_chips.setText(f"Chips: {state['player_chips']}")
        self.lbl_ai_chips.setText(f"Opponent chips: {state['ai_chips']}")

        community = state["community"]
        labels = [
            self.lbl_flop1,
            self.lbl_flop2,
            self.lbl_flop3,
            self.lbl_turn,
            self.lbl_river
        ]

        for i in range(len(labels)):
            labels[i].setText(community[i] if i < len(community) else "")
    
    def update_probability(self):
        if len(self.game.community) < 3:
            self.lbl_prob.setText("Probability: —")
            return

        opp_range = self.range.get_opponent_range(
            opponent_id=2,
            known_cards=self.game.player_hand + self.game.community
        )

        prob = calc_win_probability(
            self.game.player_hand,
            self.game.community,
            opp_range
        )

        self.lbl_prob.setText(f"Probability: {prob*100:.1f}%")
        
    def save_result(self, result):
        self.db.save_hand(
            player_id=1,
            opponent_id=2,
            player_cards="".join(self.game.player_hand),
            community_cards="".join(self.game.community),
            result=result,
            probability=calc_win_probability(
                self.game.player_hand,
                self.game.community,
                self.range.get_opponent_range(2, self.game.player_hand + self.game.community)),
            pot=self.game.pot
        )

    def back_to_menu(self):
        uic.loadUi("ui/menu.ui", self)
        self.setup_menu()

    def open_history(self):
        uic.loadUi("ui/history.ui", self)
        self.setup_history()

    def setup_history(self):
        self.btn_load.clicked.connect(self.load_history)
        self.btn_back.clicked.connect(self.back_to_menu)
    
    def load_history(self):
        data = self.db.get_player_history(1)

        self.table_history.setRowCount(len(data))

        for r, row in enumerate(data):
            for c, value in enumerate(row):
                self.table_history.setItem(
                    r, c, QTableWidgetItem(str(value))
                )

if __name__ == "__main__":
    import traceback

    try:
        app = QApplication(sys.argv)
        window = App()
        window.show()
        sys.exit(app.exec())

    except Exception as e:
        print("CRASH:")
        print(e)
        traceback.print_exc()
        
        