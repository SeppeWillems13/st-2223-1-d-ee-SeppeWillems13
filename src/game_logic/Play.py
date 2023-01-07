import os
import sys
sys.path.insert(0, '../rps_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rps_project.settings')
from src.game_logic.RPSGame import RPSGame, Choice

game = RPSGame()
game.play(Choice.ROCK, Choice.SCISSORS)
game.play(Choice.PAPER, Choice.ROCK)
print(game.score)  # {'player1': 2, 'player2': 0}