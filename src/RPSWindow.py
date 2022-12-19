import random
import sqlite3
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit


class RPSWindow(QWidget):
    def __init__(self):
        super().__init__()

        # create a connection to the leaderboard database
        self.conn = sqlite3.connect('leaderboard.db')
        self.cursor = self.conn.cursor()

        # create the leaderboard table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard (
                username text PRIMARY KEY,
                wins integer,
                losses integer,
                ties integer,
                games_played integer )
                ''')

        # define the possible choices for the game
        self.choices = ['rock', 'paper', 'scissors']

        # define the win conditions for the game
        self.win_conditions = [
            ('rock', 'scissors'),
            ('paper', 'rock'),
            ('scissors', 'paper')
        ]

        # initialize game statistics
        self.wins = 0
        self.losses = 0
        self.ties = 0

        # create the user interface
        self.create_ui()

    def get_player_stats(self, username):
        # get the player's stats from the database
        self.cursor.execute('''SELECT * FROM leaderboard WHERE username=?''', (username,))
        player_stats = self.cursor.fetchone()
        if player_stats:
            # return the player's stats
            return {
                'wins': player_stats[1],
                'losses': player_stats[2],
                'ties': player_stats[3],
                'games_played': player_stats[4]
            }
        else:
            # the player is not in the database, return default stats
            return {
                'wins': 0,
                'losses': 0,
                'ties': 0,
                'games_played': 0
            }

    def update_player_stats(self, username, wins, losses, ties):
        # update the player's stats in the database
        self.cursor.execute('''
            INSERT OR REPLACE INTO leaderboard (username, wins, losses, ties, games_played)
            VALUES (?, ?, ?, ?, (SELECT games_played FROM leaderboard WHERE username=?)+1)
        ''', (username, wins, losses, ties, username))
        self.conn.commit()

    def create_ui(self):
        # create the username input field
        self.username_label = QLabel('Username:')
        self.username_input = QLineEdit()

        # create the play button
        self.play_button = QPushButton('Play')
        self.play_button.clicked.connect(self.play)

        # create the stop button
        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop)

        # create the reset button
        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.reset)

        # create the choice buttons
        self.rock_button = QPushButton('Rock')
        self.rock_button.clicked.connect(lambda: self.choose('rock'))
        self.paper_button = QPushButton('Paper')
        self.paper_button.clicked.connect(lambda: self.choose('paper'))
        self.scissors_button = QPushButton('Scissors')
        self.scissors_button.clicked.connect(lambda: self.choose('scissors'))

        # create the game status label
        self.game_status_label = QLabel('')

        # create the game statistics labels
        self.wins_label = QLabel(f'Wins: {self.wins}')
        self.losses_label = QLabel(f'Losses: {self.losses}')
        self.ties_label = QLabel(f'Ties: {self.ties}')

        # create the horizontal layout for the choice buttons
        choice_buttons_layout = QHBoxLayout()
        choice_buttons_layout.addWidget(self.rock_button)
        choice_buttons_layout.addWidget(self.paper_button)
        choice_buttons_layout.addWidget(self.scissors_button)

        # create the vertical layout for the game controls
        game_controls_layout = QVBoxLayout()
        game_controls_layout.addWidget(self.username_label)
        game_controls_layout.addWidget(self.username_input)
        game_controls_layout.addWidget(self.play_button)
        game_controls_layout.addWidget(self.stop_button)
        game_controls_layout.addWidget(self.reset_button)
        game_controls_layout.addLayout(choice_buttons_layout)
        game_controls_layout.addWidget(self.game_status_label)
        game_controls_layout.addWidget(self.wins_label)
        game_controls_layout.addWidget(self.losses_label)
        game_controls_layout.addWidget(self.ties_label)

        # set the main layout for the window
        self.setLayout(game_controls_layout)

        # set the window properties
        self.setWindowTitle('Rock-Paper-Scissors')
        self.setGeometry(300, 300, 300, 200)

        # show the window
        self.show()

    def play(self):
        self.username = self.username_input.text()

        # get the player's stats from the database
        player_stats = self.get_player_stats(self.username)
        self.wins = player_stats['wins']
        self.losses = player_stats['losses']
        self.ties = player_stats['ties']

        # update the game statistics labels
        self.wins_label.setText(f'Wins: {self.wins}')
        self.losses_label.setText(f'Losses: {self.losses}')
        self.ties_label.setText(f'Ties: {self.ties}')

        # enable the choice buttons
        self.rock_button.setEnabled(True)
        self.paper_button.setEnabled(True)
        self.scissors_button.setEnabled(True)

        # disable the play button
        self.play_button.setEnabled(False)

    def stop(self):
        # disable the choice buttons
        self.rock_button.setEnabled(False)
        self.paper_button.setEnabled(False)
        self.scissors_button.setEnabled(False)

        # enable the play button
        self.play_button.setEnabled(True)

    def reset(self):
        # reset the game statistics
        self.wins = 0
        self.losses = 0
        self.ties = 0

        # update the game statistics labels
        self.wins_label.setText(f'Wins: {self.wins}')
        self.losses_label.setText(f'Losses: {self.losses}')
        self.ties_label.setText(f'Ties: {self.ties}')

        # reset the game status label
        self.game_status_label.setText('')

    def choose(self, choice):
        # get the computer's choice
        computer_choice = random.choice(['rock', 'paper', 'scissors'])

        # compare the choices and determine the winner
        if (choice, computer_choice) in self.win_conditions:
            self.game_status_label.setText(f'You win! {choice} beats {computer_choice}.')
            self.wins += 1
        elif (computer_choice, choice) in self.win_conditions:
            self.game_status_label.setText(f'You lose! {computer_choice} beats {choice}.')
            self.losses += 1
        else:
            self.game_status_label.setText(f'It\'s a tie! Both players chose {choice}.')
            self.ties += 1

        # update the game statistics labels
        self.wins_label.setText(f'Wins: {self.wins}')
        self.losses_label.setText(f'Losses: {self.losses}')
        self.ties_label.setText(f'Ties: {self.ties}')

        # update the player's stats in the database
        self.update_player_stats(self.username, self.wins, self.losses, self.ties)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RPSWindow()
    window.show()
    sys.exit(app.exec())
