from src.game_logic.RPSGame import RPSGame

game = RPSGame()
game.play('rock', 'scissors')
game.play('paper', 'rock')
print(game.score)  # {'player1': 2, 'player2': 0}
