# import the necessary modules
import random

# ask the player for their username
username = input('Enter your username: ')
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

# main game loop
while username:
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
