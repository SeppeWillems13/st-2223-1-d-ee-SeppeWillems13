import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rps_project.settings')

import random
from enum import Enum


class Outcome(Enum):
    WIN = 'win'
    LOSE = 'lose'
    TIE = 'tie'


class Choice(Enum):
    ROCK = 'rock'
    PAPER = 'paper'
    SCISSORS = 'scissors'


class RPSGame:
    def __init__(self):
        self.score = {'player1': 0, 'player2': 0}
        self.history = {'player1': [], 'player2': []}
        self.overall_winner = None

    def determine_winner(self, player1_choice, player2_choice):
        if player1_choice == player2_choice:
            return Outcome.TIE
        elif player1_choice == Choice.ROCK and player2_choice == Choice.SCISSORS:
            return Outcome.WIN
        elif player1_choice == Choice.PAPER and player2_choice == Choice.ROCK:
            return Outcome.WIN
        elif player1_choice == Choice.SCISSORS and player2_choice == Choice.PAPER:
            return Outcome.WIN
        else:
            return Outcome.LOSE

    def validate_choice(self, choice):
        if choice not in Choice:
            raise ValueError('Invalid choice')
        return choice

    def record_choice(self, player, choice):
        self.history[player].append(choice)

    def display_history(self):
        for player, choices in self.history.items():
            print(f'{player}: {choices}')

    def random_choice(self):
        return random.choice(['rock', 'paper', 'scissors'])

    def play(self, player1_choice, player2_choice):
        result = self.determine_winner(player1_choice, player2_choice)
        if result == Outcome.WIN:
            self.score['player1'] += 1
        elif result == Outcome.LOSE:
            self.score['player2'] += 1
        self.record_choice('player1', player1_choice)
        self.record_choice('player2', player2_choice)
        self.determine_overall_winner()

        game = Game(player1_choice=player1_choice, player2_choice=player2_choice, outcome=result)
        game.save()

        return result

    def get_score(self):
        return self.score

    def reset_score(self):
        self.score = {'player1': 0, 'player2': 0}

    def get_winner(self):
        if self.score['player1'] > self.score['player2']:
            return 'player1'
        elif self.score['player1'] < self.score['player2']:
            return 'player2'
        else:
            return 'draw'

    def determine_overall_winner(self):
        if self.score['player1'] > self.score['player2']:
            self.overall_winner = Outcome.WIN
        elif self.score['player1'] < self.score['player2']:
            self.overall_winner = Outcome.LOSE
        else:
            self.overall_winner = Outcome.TIE
