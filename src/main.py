# import the necessary modules
import random

# define the possible choices for the game
choices = ['rock', 'paper', 'scissors']

# define the win conditions for the game
win_conditions = [
    ('rock', 'scissors'),
    ('paper', 'rock'),
    ('scissors', 'paper')
]

# main game loop
while True:
    # get the player's choice
    player_choice = input('Choose rock, paper, or scissors: ')

    # validate the player's choice
    if player_choice not in choices:
        print('Invalid choice, try again.')
        continue

    # get the computer's choice
    computer_choice = random.choice(choices)

    # compare the choices and determine the winner
    if (player_choice, computer_choice) in win_conditions:
        print(f'You win! {player_choice} beats {computer_choice}.')
    elif (computer_choice, player_choice) in win_conditions:
        print(f'You lose! {computer_choice} beats {player_choice}.')
    else:
        print(f'It\'s a tie! Both players chose {player_choice}.')
