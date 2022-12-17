import streamlit as st
import random

# Create a list of options
options = ['rock', 'paper', 'scissors']

# Start the game
st.title('Rock, Paper, Scissors')
st.write('Choose your option:')

# Get the player's choice
player_choice = st.selectbox('Your turn:', options)

# Get the computer's choice
computer_choice = random.choice(options)

# Compare the choices and determine the winner
if player_choice == computer_choice:
    result = 'It\'s a tie!'
elif player_choice == 'rock' and computer_choice == 'scissors':
    result = 'You win!'
elif player_choice == 'paper' and computer_choice == 'rock':
    result = 'You win!'
elif player_choice == 'scissors' and computer_choice == 'paper':
    result = 'You win!'
else:
    result = 'You lose!'

# Display the results
st.write(f'You chose {player_choice} and the computer chose {computer_choice}')
st.write(result)
