CREATE DATABASE IF NOT EXISTS poker;

USE poker;

CREATE TABLE players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    chips INT DEFAULT 1000
);

CREATE TABLE history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    opponent_id INT NOT NULL,
    player_cards VARCHAR(10) NOT NULL,
    community_cards VARCHAR(30),
    result VARCHAR(10),
    win_probability DECIMAL(5, 4),
    pot_size INT,
    game_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players (player_id) ON DELETE CASCADE,
    FOREIGN KEY (opponent_id) REFERENCES players (player_id) ON DELETE CASCADE
);

drop Table IF EXISTS history;

INSERT INTO players (username, chips) VALUES ('player', 1000);

INSERT INTO players (username, chips) VALUES ('ai', 1000);