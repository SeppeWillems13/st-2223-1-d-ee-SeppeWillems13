import streamlit as st
import random

# Create a list of options
options = ['rock', 'paper', 'scissors']

# Start the game
st.title('Rock, Paper, Scissors')

# Get the player's name
player_name = st.text_input('Enter your name:')

# Get the number of rounds to play
num_rounds = st.slider('Number of rounds:', 1, 10, 3)

# Initialize the score
score = {'wins': 0, 'losses': 0, 'ties': 0}

# Check if the player's name and number of rounds have been entered
if player_name and num_rounds:
    # Play multiple rounds
    for i in range(num_rounds):
        st.write(f'{player_name}, choose your option:')

        # Get the player's choice
        player_choice = st.selectbox('Your turn:', options)

        # Get the computer's choice
        computer_choice = random.choice(options)

        # Compare the choices and determine the winner
        if player_choice == computer_choice:
            result = 'It\'s a tie!'
            score['ties'] += 1
        elif player_choice == 'rock' and computer_choice == 'scissors':
            result = 'You win!'
            score['wins'] += 1
        elif player_choice == 'paper' and computer_choice == 'rock':
            result = 'You win!'
            score['wins'] += 1
        elif player_choice == 'scissors' and computer_choice == 'paper':
            result = 'You win!'
            score['wins'] += 1
        else:
            result = 'You lose!'
            score['losses'] += 1

        # Display the results
        st.write(f'You chose {player_choice} and the computer chose {computer_choice}')
        st.write(result)

        # Display the score
        st.write(f'Wins: {score["wins"]}  Losses: {score["losses"]}  Ties: {score["ties"]}')
else:
    st.write('Please enter your name and number of rounds to play.')

# Ask the player if they want to play again
play_again = st.button('Play again?')

