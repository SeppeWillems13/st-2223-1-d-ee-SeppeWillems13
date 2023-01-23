import json
import random

import cv2
import mediapipe as mp
from django.http import JsonResponse

from .models import Player, Round, Result, Game
from .player_logic import update_stats
from .views import resize_screenshot, draw_hand_box, process_image

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

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


def check_if_game_is_done(_game, moves):
    _players = list(moves.keys())
    if _game.score[_players[0]] == (_game.best_of / 2 + 0.5) or _game.score[_players[1]] == (_game.best_of / 2 + 0.5):
        _player = Player.objects.get(user=_game.user)
        _game.game_status = COMPLETED
        rounds = Round.objects.filter(game=_game)
        player_moves = [_round.player_move for _round in rounds]
        opponent_moves = [_round.opponent_move for _round in rounds]

        if _game.score[_players[0]] > _game.score[_players[1]]:
            _result = Result.objects.create(game=_game, result=WIN, player=_player, player_moves=player_moves,
                                            opponent_moves=opponent_moves)
            _result.save()
            _game.result = WIN

        elif _game.score[_players[0]] < _game.score[_players[1]]:
            _result = Result.objects.create(game=_game, result=LOSE, player=_player, player_moves=player_moves,
                                            opponent_moves=opponent_moves)
            _result.save()
            _game.result = LOSE

        # get the player and update his stats
        _player = Player.objects.get(user=_game.user)

        if _game.room.is_online:
            _opponent = Player.objects.get(user=_game.opponent)
            update_stats(_opponent, _result)

        update_stats(_player, _result)
    _game.save()


def is_dark_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    average_brightness = cv2.mean(gray)[0]
    # TODO FIX A TRESHOLD
    print("average_brightness" + str(average_brightness))
    if average_brightness < 65:
        return True
    else:
        return False


def get_round_prediction_offline(request, game_id):
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
                min_detection_confidence=0.33) as hands:

            # Convert the BGR image to RGB, flip the image around y-axis for correct
            # handedness output and process it with MediaPipe Hands.
            results = hands.process(cv2.flip(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB), 1))
            # results = hands.process(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))

            if results.multi_hand_landmarks is None:
                # show the image with the hand
                if is_dark_image(resized_image):
                    cv2.imshow('is dark image', cv2.flip(resized_image, 1))
                    cv2.waitKey(0)
                    class_name, confidence_score = process_image(resized_image, True)
                    # check if confidence score is high enough
                    if confidence_score < 0.75:
                        return JsonResponse(
                            {'status': False, 'message': 'No hands detected in bright mode and dark mode'})
                else:
                    cv2.imshow('is not dark image but also no hands', cv2.flip(resized_image, 1))
                    cv2.waitKey(0)
                    return JsonResponse(
                        {'status': False, 'message': 'Image is too bright for dark mode but no hands detected'})
            else:
                image_height, image_width, _ = resized_image.shape
                annotated_image = cv2.flip(resized_image.copy(), 1)
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        annotated_image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

                hand_image = draw_hand_box(annotated_image, hand_landmarks, image_height, image_width)
                class_name, confidence_score = process_image(hand_image, False)

            # if confidence_score is less than 0.5, return error
            # print(f"Confidence score: {confidence_score}")
            if confidence_score < 0.70:
                return JsonResponse(
                    {'success': False, 'player_move': class_name, 'confidence_score': str(confidence_score),
                     'hands_detected': True, 'score': _game.score})
            else:
                _round = Round.objects.create(game=_game, host=request.user)
                get_computer_move(_round)
                moves = {"User": class_name, "Computer": _round.opponent_move}
                play_round(_round, moves, game_id)
                _round.save()
                outcome = _round.outcome
                game = Game.objects.get(id=game_id)
                return JsonResponse(
                    {'success': True, 'player_move': class_name, 'confidence_score': str(confidence_score),
                     'hands_detected': True, 'computer_move': _round.opponent_move, 'result': outcome,
                     'score': game.score, 'game_over': game.game_status == 'Completed', 'winner': game.result})
    else:
        return JsonResponse({'success': False, 'message': 'Game is already finished'})


def get_round_prediction_online(request, game_id):
    _game = Game.objects.get(id=game_id)
    print(_game)
    print(_game.game_status)
    # check if the game is still active and if the user is allowed to play
    if _game.game_status == 'Completed' or _game.game_status == 'Abandoned':
        return JsonResponse({'success': False, 'message': 'Game is not active'})

    screenshot1 = json.loads(request.body)['screenshot1']
    screenshot2 = json.loads(request.body)['screenshot2']
    class_name1, class_name2, confidence_score1, confidence_score2 = process_images(screenshot1, screenshot2)

    # check if class names are valid and if confidence score is high enough
    if class_name1 == 'None' or class_name2 == 'None' or confidence_score1 < 0.70 or confidence_score2 < 0.70:
        return JsonResponse(
            {'success': False, 'player_move': class_name1, 'opps_move': class_name2,
             'confidence_score': str(confidence_score1),
             'hands_detected': False, 'opps_confidence_score': str(confidence_score2), 'score': _game.score})
    else:
        _round = Round.objects.create(game=_game, host=request.user, opponent=_game.opponent)
        moves = {"User": class_name1, "User2": class_name2}
        play_round(_round, moves, game_id)
        _round.save()
        outcome = _round.outcome
        game = Game.objects.get(id=game_id)
        return JsonResponse(
            {'success': True, 'player_move': class_name1, 'opps_move': class_name2,
             'confidence_score': str(confidence_score1),
             'hands_detected': True, 'opps_confidence_score': str(confidence_score2), 'result': outcome,
             'score': game.score, 'game_over': game.game_status == 'Completed', 'winner': game.result})


def process_images(image1, image2):
    resized_image1 = resize_screenshot(image1, 720, 720)
    resized_image2 = resize_screenshot(image2, 720, 720)

    # Run MediaPipe Hands on both images
    mp_hands = mp.solutions.hands
    with mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.33) as hands:
        results1 = hands.process(cv2.flip(cv2.cvtColor(resized_image1, cv2.COLOR_BGR2RGB), 1))
        # Check if hands were detected in both images
        if results1.multi_hand_landmarks is None:
            # show the image with the hand
            if is_dark_image(resized_image1):
                cv2.imshow('is dark image', cv2.flip(resized_image1, 1))
                cv2.waitKey(0)
                class_name, confidence_score = process_image(resized_image1, True)
                # check if confidence score is high enough
                if confidence_score < 0.75:
                    return JsonResponse(
                        {'status': False, 'message': 'No hands detected in bright mode and dark mode'})
            else:
                cv2.imshow('is not dark image but also no hands', cv2.flip(resized_image1, 1))
                cv2.waitKey(0)
                return JsonResponse(
                    {'status': False, 'message': 'Image is too bright for dark mode but no hands detected'})
        else:
            # Draw hand landmarks and create hand images for both images
            image_height, image_width, _ = resized_image1.shape
            annotated_image1 = cv2.flip(resized_image1.copy(), 1)
            for hand_landmarks in results1.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    annotated_image1,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

            hand_image1 = draw_hand_box(annotated_image1, hand_landmarks, image_height, image_width)
            class_name1, confidence_score1 = process_image(hand_image1, False)

        results2 = hands.process(cv2.flip(cv2.cvtColor(resized_image2, cv2.COLOR_BGR2RGB), 1))
        # Check if hands were detected in both images
        if results2.multi_hand_landmarks is None:
            # show the image with the hand
            if is_dark_image(resized_image2):
                cv2.imshow('is dark image', cv2.flip(resized_image2, 1))
                cv2.waitKey(0)
                class_name, confidence_score = process_image(resized_image2, True)
                # check if confidence score is high enough
                if confidence_score < 0.75:
                    return JsonResponse(
                        {'status': False, 'message': 'No hands detected in bright mode and dark mode'})
            else:
                cv2.imshow('is not dark image but also no hands', cv2.flip(resized_image2, 1))
                cv2.waitKey(0)
                return JsonResponse(
                    {'status': False, 'message': 'Image is too bright for dark mode but no hands detected'})
        else:
            image_height, image_width, _ = resized_image2.shape
            annotated_image2 = cv2.flip(resized_image2.copy(), 1)
            for hand_landmarks in results2.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    annotated_image2,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

            hand_image2 = draw_hand_box(annotated_image2, hand_landmarks, image_height, image_width)
            class_name2, confidence_score2 = process_image(hand_image2, False)

            # show the images
            cv2.imshow('Hand Image 1', hand_image1)
            cv2.waitKey(0)
            cv2.imshow('Hand Image 2', hand_image2)
            cv2.waitKey(0)
            print('Class Name 1: ' + class_name1)
            print('Class Name 2: ' + class_name2)
            print('Confidence Score 1: ' + str(confidence_score1))
            print('Confidence Score 2: ' + str(confidence_score2))

        return class_name1, class_name2, confidence_score1, confidence_score2


def get_computer_move(_round):
    _round.opponent_move = random.choice(list(dict(GAME_MOVE_CHOICES).keys()))


def play_round(_round, moves, game_id):
    _game = Game.objects.get(pk=game_id)
    _players = list(moves.keys())
    print(moves)

    if not _game.score:
        _game.score = {_players[0]: 0, _players[1]: 0}
        _game.save()
    if _game.game_status == COMPLETED:
        return
    else:
        _game.rounds_played += 1
        _round.round_number = _game.rounds_played
        _round.player_move = moves['User']
        if _players[1] == 'Computer':
            _round.opponent_move = moves['Computer']
        else:
            _round.opponent_move = moves['User2']
        print("MOVES PLAYER 1: " + moves[_players[0]])
        print("MOVES COMPUTER: " + moves[_players[1]])

        if moves[_players[0]] == moves[_players[1]]:
            _round.outcome = TIE
        elif (moves[_players[0]] == ROCK and _round.opponent_move == SCISSORS) or \
                (moves[_players[0]] == SCISSORS and _round.opponent_move == PAPER) or \
                (moves[_players[0]] == PAPER and _round.opponent_move == ROCK):
            _round.outcome = WIN
            _game.score[_players[0]] += 1
        else:
            _round.outcome = LOSE
            _game.score[_players[1]] += 1

        _game.save()
        check_if_game_is_done(_game, moves)
        _round.save()
