import base64
import math

import cv2
import numpy as np
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from .hand_recognition import HandClassifier
from .models import Room, Game, Player, Round


# Create your views here.


@login_required(login_url='login')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''

    players = Player.objects.all()[0:5]

    rooms = Room.objects.filter(Q(name__icontains=q))
    room_count = rooms.count()
    context = {'rooms': rooms, 'room_count': room_count, 'players': players,
               'players_ranked': Player.objects.all().order_by('-win_percentage')}
    return render(request, 'base/home.html', context)


def playerDetailsPage(request, pk):
    player = Player.objects.get(id=pk)

    return render(request, 'base/player_details.html', {'player': player})


def process_image(image, dark_mode):
    classifier = HandClassifier.HandClassifier(dark_mode)
    return classifier.classify(image)


def resize_screenshot(image, width, height):
    screenshot = base64.b64decode(image.split(',')[1])
    screenshot = np.frombuffer(screenshot, dtype=np.uint8)
    screenshot = cv2.imdecode(screenshot, cv2.IMREAD_COLOR)
    DESIRED_HEIGHT = width
    DESIRED_WIDTH = height

    h, w = screenshot.shape[:2]
    if h < w:
        img = cv2.resize(screenshot, (DESIRED_WIDTH, math.floor(h / (w / DESIRED_WIDTH))))
    else:
        img = cv2.resize(screenshot, (math.floor(w / (h / DESIRED_HEIGHT)), DESIRED_HEIGHT))

    return img


def draw_hand_box(annotated_image, hand_landmarks, image_height, image_width):
    min_x, min_y, max_x, max_y = 1.0, 1.0, 0.0, 0.0
    print(hand_landmarks)
    for landmark in hand_landmarks.landmark:
        min_x, min_y = min(landmark.x, min_x), min(landmark.y, min_y)
        max_x, max_y = max(landmark.x, max_x), max(landmark.y, max_y)
    offset_x, offset_y = 0.05, 0.05
    min_x, min_y = int(min_x * image_width - offset_x * image_width), int(
        min_y * image_height - offset_y * image_height)
    max_x, max_y = int(max_x * image_width + offset_x * image_width), int(
        max_y * image_height + offset_y * image_height)
    hand_image = annotated_image[min_y:max_y, min_x:max_x]
    return hand_image


# add a game detail view
def game_detail(request, game_id):
    game = Game.objects.get(id=game_id)
    rounds = Round.objects.filter(game=game)
    #get the current user

    return render(request, 'base/game_detail.html', {'game': game, 'rounds': rounds, 'is_online': game.room.is_online})
