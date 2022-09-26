import random
import math
from Choices import Choices


def play():
    user = input("What's your choice? '1' for rock, '2' for paper, '3' for scissors, '4' for lizard, '5' for spock\n")

    # validate user input and convert to Choices enum
    user = int(user)
    if not 1 <= user <= 5:
        print('Invalid input. You have to choose between 1 and 5')
        return
    user = Choices(user)

    # computer chooses randomly
    computer = random.choice(list(Choices))

    # determine winner
    if user == computer:
        return 0, user, computer
    elif is_win(user, computer):
        return 1, user, computer
    else:
        return -1, user, computer

def is_win(user, computer):
    # user wins if it beats the computer
    # rock beats scissors and lizard
    if user == Choices.ROCK:
        return computer == Choices.SCISSORS or computer == Choices.LIZARD
    # paper beats rock and spock
    elif user == Choices.PAPER:
        return computer == Choices.ROCK or computer == Choices.SPOCK
    # scissors beats paper and lizard
    elif user == Choices.SCISSORS:
        return computer == Choices.PAPER or computer == Choices.LIZARD
    # lizard beats paper and spock
    elif user == Choices.LIZARD:
        return computer == Choices.PAPER or computer == Choices.SPOCK
    # spock beats rock and scissors
    elif user == Choices.SPOCK:
        return computer == Choices.ROCK or computer == Choices.SCISSORS


def play_best_of(n):
    player_wins = 0
    computer_wins = 0
    wins_necessary = math.ceil(n / 2)
    while player_wins < wins_necessary and computer_wins < wins_necessary:
        result, user, computer = play()
        # tie
        if result == 0:
            print('It is a tie. You both choose {}. \n'.format(user))
        # you win
        elif result == 1:
            player_wins += 1
            print('You chose {} and the computer chose {}. You win!\n'.format(user, computer))
        else:
            computer_wins += 1
            print('You chose {} and the computer chose {}. You lose.\n'.format(user, computer))

    if player_wins > computer_wins:
        print('You have won the best of {} games'.format(n))
    else:
        print('Unfortunately, the computer has won the best of {} games. Better luck next time!'.format(n))


if __name__ == '__main__':
    play_best_of(25)  # play best of n games (first to n/2 wins)
