import base64
import json
import math

import cv2
import numpy as np
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from .forms import UserForm, MyUserCreationForm
from .hand_recognition import HandClassifier
from .models import Room, Game, User, Player, Round


# Create your views here.
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            print(user)
            login(request, user)
            messages.success(request, 'You have been registered and logged in.')
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
    else:
        form = MyUserCreationForm()

    return render(request, 'base/login_register.html', {'form': form})


@login_required(login_url='login')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''

    players = Player.objects.all()[0:5]

    rooms = Room.objects.filter(Q(name__icontains=q))
    room_count = rooms.count()
    context = {'rooms': rooms, 'room_count': room_count, 'players': players,
               'players_ranked': Player.objects.all().order_by('-win_percentage')}
    return render(request, 'base/home.html', context)


def userProfile(request, pk):
    # Retrieve the user instance or return a 404 error if it does not exist
    user = get_object_or_404(User, pk=pk)
    # get the player instance
    player = Player.objects.get(user=user)
    # Retrieve the rooms created by the user
    rooms = Room.objects.filter(host=user)
    # Retrieve the 5 most recent games played by the user
    room_games = Game.objects.filter(user=user).order_by('-created')[0:5]
    # Define the template name
    template_name = 'base/profile.html'
    context = {'user': user, 'rooms': rooms,
               'room_games': room_games, 'player': player}
    return render(request, template_name, context)


def room(request, pk):
    try:
        _room = Room.objects.get(pk=pk)
    except Room.DoesNotExist:
        return room_not_found(request, pk)

    # Define the template name
    template_name = 'base/room.html'
    if request.method == 'POST':
        # Validate the form data
        if not request.POST.get('body'):
            messages.error(request, 'The message cannot be empty')
        else:
            return redirect(reverse('room', args=[pk]))

    players = Player.objects.filter(room=_room)
    if request.user not in [player.user for player in players]:
        player = Player.objects.get(user=request.user)
        _room.players.add(player)
        print(_room.players.all())
        _room.save()

    room_games = _room.game_set.select_related('user').all()
    players_json = serializers.serialize("json", players)
    context = {'room': _room, 'room_games': room_games,
               'players': players, 'players_json': players_json}
    return render(request, template_name, context)


def room_not_found(request, pk):
    context = {"pk": pk}
    return render(request, 'base/room_not_found.html', context)


@login_required(login_url='login')
def deleteGame(request, pk):
    try:
        game = Game.objects.get(id=pk)
    except Game.DoesNotExist:
        return redirect('user-profile', pk=request.user.id)

    if request.user != game.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        game.delete()
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    return render(request, 'base/delete.html', {'obj': game})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update_user.html', {'form': form})


def activityPage(request):
    room_messages = Game.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})


def playersPage(request):
    # q = request.GET.get('q') if request.GET.get('q') is not None else ''
    # players = Player.objects.filter(user__username__icontains=q)

    players = Player.objects.all()
    return render(request, 'base/players.html', {'players': players})


def playerDetailsPage(request, pk):
    player = Player.objects.get(id=pk)

    return render(request, 'base/player_details.html', {'player': player})


@login_required(login_url='login')
def start_game_offline(request, room_id):
    if request.method == 'POST':
        _room = get_object_or_404(Room, code=room_id)
        # check if a game exists for this _room and set the status to aborted
        old_game = Game.objects.filter(room=_room)
        if old_game.exists() and old_game[0].game_status == 'Ongoing':
            old_game = old_game[0]
            old_game.game_status = 'Abandoned'
            old_game.save()

        best_of = int(json.loads(request.body).get('bestOf'))
        if best_of not in [1, 3, 5, 7, 9, 11, 13]:
            best_of = 3

        game = Game.objects.create(room=_room, user=request.user, best_of=best_of)

        print(game)
        game.save()
        game_dict = model_to_dict(game)
        return JsonResponse({
            'success': True,
            'message': 'Game started',
            'game': game_dict,
            'game_id': game.id
        })
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required(login_url='login')
def start_game_online(request, room_id):
    if request.method == 'POST':
        _room = get_object_or_404(Room, code=room_id)
        # check if a game exists for this _room and set the status to aborted
        old_game = Game.objects.filter(room=_room)
        if old_game.exists() and old_game[0].game_status == 'Ongoing':
            old_game = old_game[0]
            old_game.game_status = 'Abandoned'
            old_game.save()

        players = json.loads(request.body).get('players')
        player_ids = [player['pk'] for player in players]
        users = User.objects.filter(id__in=player_ids)
        opponent = users[0]
        if opponent == _room.host:
            opponent = users[1]

        best_of = int(json.loads(request.body).get('bestOf'))
        if best_of not in [1, 3, 5, 7, 9, 11, 13]:
            best_of = 3

        game = Game.objects.create(room=_room, user=request.user, opponent=opponent, best_of=best_of)

        game.save()
        game_dict = model_to_dict(game)
        return JsonResponse({
            'success': True,
            'message': 'Game started',
            'game': game_dict,
            'game_id': game.id
        })
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


def process_image(image):
    classifier = HandClassifier.HandClassifier()
    return classifier.classify(image)


def my_fallback_detection_algorithm(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply a Gaussian blur to the image
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Perform thresholding on the image
    ret, thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest contour
    if contours:
        hand_contour = max(contours, key=cv2.contourArea)
        return hand_contour
    else:
        return None



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
    return render(request, 'base/game_detail.html', {'game': game, 'rounds': rounds})
