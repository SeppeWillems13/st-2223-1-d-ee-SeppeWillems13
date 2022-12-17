import streamlit as st

def determine_winner(player, computer):
    if player == computer:
        return "Tie"
    elif player == "rock" and computer == "scissors":
        return "Player"
    elif player == "paper" and computer == "rock":
        return "Player"
    elif player == "scissors" and computer == "paper":
        return "Player"
    else:
        return "Computer"

st.title("Rock Paper Scissors")

player_choice = st.radio("Choose your weapon:", ("rock", "paper", "scissors"))

import random
computer_choice = random.choice(("rock", "paper", "scissors"))

result = determine_winner(player_choice, computer_choice)

st.write("You chose", player_choice)
st.write("The computer chose", computer_choice)
st.write("The winner is", result)

if st.button("Play again"):
    player_choice = st.radio("Choose your weapon:", ("rock", "paper", "scissors"))
    computer_choice = random.choice(("rock", "paper", "scissors"))
    result = determine_winner(player_choice, computer_choice)
    st.write("You chose", player_choice)
    st.write("The computer chose", computer_choice)
    st.write("The winner is", result)

st.run()
