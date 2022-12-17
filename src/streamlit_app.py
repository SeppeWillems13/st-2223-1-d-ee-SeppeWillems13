import cv2
import streamlit as st

# Load the hand detection cascade classifier
hand_cascade = cv2.CascadeClassifier('hand.xml')

# Create a Streamlit app
@st.cache
def main():
  st.title("Seppe project")

  # Set up the camera
  cap = cv2.VideoCapture(0)

  # Set up the game logic
  def play_game(player_choice, computer_choice):
    if player_choice == computer_choice:
      return "Tie"
    elif player_choice == "rock" and computer_choice == "scissors":
      return "Player wins"
    elif player_choice == "paper" and computer_choice == "rock":
      return "Player wins"
    elif player_choice == "scissors" and computer_choice == "paper":
      return "Player wins"
    else:
      return "Computer wins"

  # Set up the hand gestures
  gestures = ["rock", "paper", "scissors"]

  # Create buttons for the player to select their hand gesture
  player_choice = st.sidebar.radio("Select your hand gesture:", gestures)

  # Capture and display the video feed
  while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect hands in the video feed
    hands = hand_cascade.detectMultiScale(gray, 1.3, 5)

    # Iterate through the detected hands
    for (x,y,w,h) in hands:
      # Draw a rectangle around the detected hand
      cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
      roi_gray = gray[y:y+h, x:x+w]
      roi_color = frame[y:y+h, x:x+w]

      # Label the detected hand as "rock," "paper," or "scissors"
      if w > 100:
        cv2.putText(frame, "rock", (x,y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)
        computer_choice = "rock"
      elif w > 50:
        cv2.putText(frame, "paper", (x,y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)
        computer_choice = "paper"
      else:
        cv2.putText(frame, "scissors", (x,y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)
        computer_choice = "scissors"

    # Display the video feed
    st.image(frame)

    # Play the game and display the results
    if st.sidebar.button("Play"):
      result = play_game(player_choice, computer_choice)
      st.write("Result: ", result)
