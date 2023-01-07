class RPSGame:
    def __init__(self):
        self.score = {'player1': 0, 'player2': 0}

    def determine_winner(self, player1_choice, player2_choice):
        if player1_choice == player2_choice:
            return 'draw'
        elif player1_choice == 'rock' and player2_choice == 'scissors':
            return 'player1'
        elif player1_choice == 'paper' and player2_choice == 'rock':
            return 'player1'
        elif player1_choice == 'scissors' and player2_choice == 'paper':
            return 'player1'
        else:
            return 'player2'

    def play(self, player1_choice, player2_choice):
        result = self.determine_winner(player1_choice, player2_choice)
        if result == 'player1':
            self.score['player1'] += 1
        elif result == 'player2':
            self.score['player2'] += 1
