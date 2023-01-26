from .models import Player
from .models import WIN, LOSE


def add_player_to_room(_room, request):
    player = Player.objects.get(user=request.user)
    _room.players.add(player)
    _room.save()


def update_stats(_player, result):
    if result.result == WIN:
        _player.wins += 1
        _player.loss_streak = 0
        _player.win_streak += 1
    elif result.result == LOSE:
        _player.losses += 1
        _player.win_streak = 0
        _player.loss_streak += 1

    total_games = _player.wins + _player.losses
    _player.win_percentage = round(_player.wins / total_games * 100, 2)

    # update the played_moves field with the moves played in the game
    for move in result.player_moves:
        if move in _player.played_moves:
            _player.played_moves[move] += 1
        else:
            _player.played_moves[move] = 1

    _player.most_played_move = max(_player.played_moves, key=_player.played_moves.get)

    for move in result.opponent_moves:
        if move in _player.faced_moves:
            _player.faced_moves[move] += 1
        else:
            _player.faced_moves[move] = 1

    _player.most_faced_move = max(_player.faced_moves, key=_player.faced_moves.get)
    _player.save()
