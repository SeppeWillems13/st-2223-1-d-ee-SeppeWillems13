# import the necessary modules
import random
import sqlite3


class Leaderboard:
    def __init__(self):
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


# ask the player for their username
username = input('Enter your username: ')

# main game loop
while username:
    # ask the player how many times they want to play
    num_plays = int(input('Enter the number of times you want to play: '))
    # define the possible choices for the game
    choices = ['rock', 'paper', 'scissors']

    # define the win conditions for the game
    win_conditions = [
        ('rock', 'scissors'),
        ('paper', 'rock'),
        ('scissors', 'paper')
    ]

    # initialize game statistics
    wins = 0
    losses = 0
    ties = 0

    # create an instance of the Leaderboard class
    leaderboard = Leaderboard()

    # get the player's stats from the database
    player_stats = leaderboard.get_player_stats(username)
    wins = player_stats['wins']
    losses = player_stats['losses']
    ties = player_stats['ties']

    for i in range(num_plays):
        # get the player's choice
        player_choice = input('Choose rock, paper, or scissors: ')

        # check if the player wants to stop the game
        if player_choice == 'stop':
            break

        # validate the player's choice
        if player_choice not in choices:
            print('Invalid choice, try again.')
            continue

        # get the computer's choice
        computer_choice = random.choice(choices)

        # compare the choices and determine the winner
        if (player_choice, computer_choice) in win_conditions:
            print(f'You win! {player_choice} beats {computer_choice}.')
            wins += 1
        elif (computer_choice, player_choice) in win_conditions:
            print(f'You lose! {computer_choice} beats {player_choice}.')
            losses += 1
        else:
            print(f'It\'s a tie! Both players chose {player_choice}.')
            ties += 1

        # display game statistics
        print(f'Wins: {wins} Losses: {losses} Ties: {ties}')

    # update the player's stats in the database
    leaderboard.update_player_stats(username, wins, losses, ties)

    # ask the player if they want to play again
    play_again = input('Do you want to play again? (y/n) ')
    if play_again == 'y':
        # ask the player how many times they want to play
        num_plays = int(input('Enter the number of times you want to play: '))
    else:
        print('Thanks for playing!')
        break
