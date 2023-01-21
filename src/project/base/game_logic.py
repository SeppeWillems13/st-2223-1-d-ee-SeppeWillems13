import json
import random

import cv2
import mediapipe as mp
from django.http import JsonResponse

from .models import Player, Round, Result, Game
from .player_logic import update_stats
from .views import resize_screenshot, draw_hand_box, process_image, my_fallback_detection_algorithm

# Choices for the game_move field
ROCK = 'Rock'
PAPER = 'Paper'
SCISSORS = 'Scissors'
GAME_MOVE_CHOICES = (
    (ROCK, 'Rock'),
    (PAPER, 'Paper'),
    (SCISSORS, 'Scissors'),
)

# Choices for the game_status field
ONGOING = 'Ongoing'
COMPLETED = 'Completed'
ABANDONED = 'Abandoned'
GAME_STATUS_CHOICES = (
    (ONGOING, 'Ongoing'),
    (COMPLETED, 'Completed'),
    (ABANDONED, 'Abandoned'),
)

# Choices for the result field
WIN = 'Win'
LOSE = 'Lose'
TIE = 'Tie'
GAME_RESULT_CHOICES = (
    (WIN, 'Win'),
    (LOSE, 'Lose'),
    (TIE, 'Tie'),
)


def check_if_game_is_done(_game):
    global _result
    if _game.score['User'] == (_game.best_of / 2 + 0.5) or _game.score['Computer'] == (_game.best_of / 2 + 0.5):
        _player = Player.objects.get(user=_game.user)
        _game.game_status = COMPLETED
        rounds = Round.objects.filter(game=_game)
        player_moves = [_round.player_move for _round in rounds]
        opponent_moves = [_round.opponent_move for _round in rounds]

        if _game.score['User'] > _game.score['Computer']:
            _result = Result.objects.create(game=_game, result=WIN, player=_player, player_moves=player_moves,
                                            opponent_moves=opponent_moves)
            _result.save()
            _game.result = WIN

        elif _game.score['User'] < _game.score['Computer']:
            _result = Result.objects.create(game=_game, result=LOSE, player=_player, player_moves=player_moves,
                                            opponent_moves=opponent_moves)
            _result.save()
            _game.result = LOSE

        # get the player and update his stats
        _player = Player.objects.get(user=_game.user)
        update_stats(_player, _result)
    _game.save()


def play_round(request, game_id):
    _game = Game.objects.get(id=game_id)
    if request.method == 'POST':
        # check if the game is still active and if the user is allowed to play
        if _game.game_status == 'Completed' or _game.game_status == 'Abandoned':
            return JsonResponse({'success': False, 'message': 'Game is not active'})

        screenshot = json.loads(request.body)['screenshot']
        resized_image = resize_screenshot(screenshot, 720, 720)

        mp_hands = mp.solutions.hands
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles

        # Run MediaPipe Hands.
        with mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=1,
                min_detection_confidence=0.7) as hands:

            # Convert the BGR image to RGB, flip the image around y-axis for correct
            # handedness output and process it with MediaPipe Hands.
            results = hands.process(cv2.flip(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB), 1))

            fallback_result = None
            if not results.multi_hand_landmarks:
                fallback_result = my_fallback_detection_algorithm(resized_image)
                if fallback_result is None:
                    return JsonResponse(
                        {'status': False, 'message': 'No hands detected', 'game_id': game_id,
                         'game_status': _game.game_status})

            image_height, image_width, _ = resized_image.shape
            annotated_image = cv2.flip(resized_image.copy(), 1)

            if results.multi_hand_landmarks is not None:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        annotated_image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
            else:
                hand_landmarks = fallback_result

            print("hand_landmarks")
            print(hand_landmarks)
            print("fallback_result")
            print(fallback_result)
            hand_image = draw_hand_box(annotated_image, hand_landmarks, image_height, image_width)
            class_name, confidence_score = process_image(hand_image)

            cv2.imshow('MediaPipe Hands', hand_image)
            cv2.waitKey(0)
            folder = r"C:\Users\seppe\PycharmProjects\st-2223-1-d-ee-SeppeWillems13\src\project\base\hand_recognition" \
                     r"\application_images"
            cv2.imwrite(f"{folder}\{confidence_score}.jpg", hand_image)

            # if confidence_score is less than 0.5, return error
            if confidence_score < 0.5:
                return JsonResponse(
                    {'success': False, 'player_move': class_name, 'confidence_score': str(confidence_score),
                     'hands_detected': True, 'score': _game.score})
            else:
                _round = Round.objects.create(game=_game)
                play_offline_round(_round, class_name, game_id)
                _round.save()
                outcome = _round.outcome
                computer_move = _round.opponent_move
                game = Game.objects.get(id=game_id)
                return JsonResponse(
                    {'success': True, 'player_move': class_name, 'confidence_score': str(confidence_score),
                     'hands_detected': True, 'computer_move': computer_move, 'result': outcome,
                     'score': game.score, 'game_over': game.game_status == 'Completed', 'winner': game.result})
    else:
        return JsonResponse({'success': False, 'message': 'Game is already finished'})


def get_computer_move(_round):
    _round.opponent_move = random.choice(list(dict(GAME_MOVE_CHOICES).keys()))


def play_offline_round(_round, class_name, game_id):
    _game = Game.objects.get(pk=game_id)
    if not _game.score:
        _game.score = {'User': 0, 'Computer': 0}
        _game.save()
    if _game.game_status == COMPLETED:
        return
    else:
        _game.rounds_played += 1
        _round.round_number = _game.rounds_played
        _round.player_move = dict(GAME_MOVE_CHOICES)[class_name]
        get_computer_move(_round)
        if class_name == _round.opponent_move:
            _round.outcome = TIE
        elif (class_name == ROCK and _round.opponent_move == SCISSORS) or \
                (class_name == SCISSORS and _round.opponent_move == PAPER) or \
                (class_name == PAPER and _round.opponent_move == ROCK):
            _round.outcome = WIN
            _game.score['User'] += 1
        else:
            _round.outcome = LOSE
            _game.score['Computer'] += 1

        _game.save()
        check_if_game_is_done(_game)
        _round.save()
