import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


class DB:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            connection_timeout=5
        )
        self.cursor = self.conn.cursor()

    def create_player(self, username, chips=1000):
        self.cursor.execute(
            "INSERT INTO players (username, chips) VALUES (%s, %s)",
            (username, chips)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def save_hand(self, player_id, opponent_id, player_cards,
                  community_cards, result, probability, pot):
        self.cursor.execute(
            """INSERT INTO history 
               (player_id, opponent_id, player_cards, community_cards, result, win_probability, pot_size)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (player_id, opponent_id, player_cards, community_cards, result, probability, pot)
        )
        self.conn.commit()

    def get_all_players(self):
        self.cursor.execute("SELECT player_id, username, chips FROM players")
        return self.cursor.fetchall()

    def get_player_history(self, player_id):
        self.cursor.execute(
            """SELECT hh.history_id, hh.player_cards, hh.community_cards, hh.result,
                      hh.win_probability, hh.game_date, p.username
               FROM history hh
               JOIN players p ON hh.opponent_id = p.player_id
               WHERE hh.player_id = %s
               ORDER BY hh.game_date DESC""",
            (player_id,)
        )
        return self.cursor.fetchall()
    
    def update_history(self, history_id, result, probability):
        self.cursor.execute(
            """UPDATE history
               SET result = %s, win_probability = %s
               WHERE history_id = %s""",
            (result, probability, history_id)
        )
        self.conn.commit()

    def get_opponent_hands(self, opponent_id, limit=500):
        self.cursor.execute(
            """SELECT DISTINCT player_cards
            FROM history
            WHERE opponent_id = %s
            LIMIT %s""",
            (opponent_id, limit)
        )
        rows = self.cursor.fetchall()
        return [r[0] for r in rows]
    def update_chips(self, player_id, chips):
        self.cursor.execute(
            "UPDATE players SET chips = %s WHERE player_id = %s",
            (chips, player_id)
        )
        self.conn.commit()

    def delete_player(self, player_id):
        self.cursor.execute(
            "DELETE FROM players WHERE player_id = %s",
            (player_id,)
        )
        self.conn.commit()

    def delete_history(self, history_id):
        self.cursor.execute(
            "DELETE FROM history WHERE history_id = %s",
            (history_id,)
        )
        self.conn.commit()

    def clear_history(self):
        self.cursor.execute("DELETE FROM history")
        self.conn.commit()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            
