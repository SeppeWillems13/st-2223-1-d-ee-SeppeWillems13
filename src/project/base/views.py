import base64
import json
import math

import cv2
import mediapipe as mp
import numpy as np
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.validators import EmailValidator
from django.db.models import Q
from django.forms import Form, model_to_dict
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from .forms import UserForm, MyUserCreationForm, RoomForm
from .hand_recognition import HandClassifier
from .models import Room, Game, User, Player, Round


# loginform validator
class LoginForm(Form):
    email = forms.EmailField(validators=[EmailValidator()])
    password = forms.CharField(min_length=8)


# Create your views here.
def loginPage(request):
    page = 'login'
    # if user is already authenticated just redirect to home page
    if request.user.is_authenticated:
        return redirect('home')
    # on post do minor checks
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'The email address or password you entered is incorrect. Please check your '
                                        'email address and password and try again.')
        else:
            messages.error(request, 'Invalid form data. Please enter a valid email address and password.')
    else:
        form = LoginForm()

    context = {'page': page, 'form': form}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    if request.method == 'GET':
        logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('home')


def registerPage(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
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

    context = {'rooms': rooms, 'room_count': room_count, 'players': players}
    return render(request, 'base/home.html', context)


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

    room_games = _room.game_set.select_related('user').all()
    players = _room.players.select_related('user').all()

    context = {'room': _room, 'room_games': room_games,
               'players': players}
    return render(request, template_name, context)


def add_player_to_room(_room, request):
    player = Player.objects.get(user=request.user)
    _room.players.add(player)
    _room.save()


def room_not_found(request, pk):
    context = {"pk": pk}
    return render(request, 'base/room_not_found.html', context)


def userProfile(request, pk):
    # Retrieve the user instance or return a 404 error if it does not exist
    user = get_object_or_404(User, pk=pk)
    # Retrieve the rooms created by the user
    rooms = Room.objects.filter(host=user)
    # Retrieve the games played by the user
    room_games = Game.objects.filter(user=user).order_by('-created')
    # Define the template name
    template_name = 'base/profile.html'

    # Add pagination to the view
    paginator = Paginator(room_games, 10)
    page = request.GET.get('page')
    room_games = paginator.get_page(page)

    context = {'user': user, 'rooms': rooms,
               'room_games': room_games}
    return render(request, template_name, context)


def createRoom(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()

            player = Player.objects.get(user=request.user)
            room.players.add(player)

            messages.success(request, 'Room created successfully')
            return redirect('home')
        else:
            messages.error(request, 'An error occurred while creating the room')
    else:
        form = RoomForm()

    template_name = 'base/room_form.html'
    context = {'form': form}
    return render(request, template_name, context)


@login_required(login_url='login')
def joinRoom(request):
    form = RoomForm(request.POST)
    template_name = 'base/join_room.html'
    # Render the template with the form and topics
    context = {'form': form}

    # check if post request
    if request.method == 'POST':
        # get the room code
        room_code = request.POST.get('code')
        # check if room exists
        room = Room.objects.filter(code=room_code)
        if room.exists():
            player = Player.objects.get(user=request.user)
            room = room[0]
            room.players.add(player)
            return redirect('room', pk=room.code)
        else:
            messages.error(request, 'Room does not exist')
            return render(request, template_name, context)
    else:
        # Define the template name
        return render(request, template_name, context)


@login_required(login_url='login')
def updateRoom(request, pk):
    # Get the room object
    try:
        _room = get_object_or_404(Room, id=pk)
    except Http404:
        # Handle the case where the room does not exist
        return render(request, 'base/room_not_found.html', {'pk': pk})
    # Create a form instance with POST data, if available
    form = RoomForm(request.POST or None, instance=_room)
    # Check if the form has been submitted
    if request.method == 'POST':
        # Validate the form data
        if form.is_valid():
            # Save the form data to the database
            form.save()
            # Redirect the user to the room page
            return redirect('room', pk=_room.id)
    # Define the template name
    template_name = 'base/room_form.html'
    # Render the template with the form and topics
    context = {'form': form, 'room': _room}
    return render(request, template_name, context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    # Handle the case where the room does not exist
    _room = get_object_or_404(Room, code=pk)

    if request.user != _room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        _room.delete()
        return redirect(reverse('home'))
    return render(request, 'base/delete.html', {'obj': _room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Game.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


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
def leave_room(request, room_code):
    if request.method == 'POST':
        room = Room.objects.filter(code=room_code)
        if room.exists():
            player = Player.objects.get(user=request.user)
            room = room[0]
            print(room)
            print(room.players)
            room.players.remove(player)
            room.save()
        else:
            print('Room does not exist')
        return redirect('/')
    else:
        return redirect('/')


from django.shortcuts import get_object_or_404
from django.http import JsonResponse


@login_required(login_url='login')
def start_game_offline(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(Room, code=room_id)
        # check if a game exists for this room and set the status to aborted
        old_game = Game.objects.filter(room=room)
        if old_game.exists():
            old_game = old_game[0]
            old_game.game_status = 'Abandoned'
            old_game.save()

        best_of = int(json.loads(request.body).get('bestOf'))
        if best_of not in [1, 3, 5, 7, 9, 11, 13]:
            best_of = 3
        game, created = Game.objects.get_or_create(room=room, user=request.user, best_of=best_of,
                                                   defaults={'score': {"player1": 0, "player2": 0}})
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


def play_round(request, game_id):
    game = Game.objects.get(id=game_id)
    if request.method == 'POST':
        # check if the game is still active and if the user is allowed to play
        if game.game_status == 'Completed' or game.game_status == 'Abandoned':
            return JsonResponse({'success': False, 'message': 'Game is not active'})
        screenshot = json.loads(request.body)['screenshot']

        def resize_and_show(image):
            # Decode the base64 encoded image data
            screenshot = base64.b64decode(image.split(',')[1])
            # Convert the raw image data to a numpy array
            screenshot = np.frombuffer(screenshot, dtype=np.uint8)
            # Decode the image and convert it to a format that OpenCV can process
            screenshot = cv2.imdecode(screenshot, cv2.IMREAD_COLOR)
            # call a hand classifier class here that gets the hand
            DESIRED_HEIGHT = 720
            DESIRED_WIDTH = 720

            h, w = screenshot.shape[:2]
            if h < w:
                img = cv2.resize(screenshot, (DESIRED_WIDTH, math.floor(h / (w / DESIRED_WIDTH))))
            else:
                img = cv2.resize(screenshot, (math.floor(w / (h / DESIRED_HEIGHT)), DESIRED_HEIGHT))

            return img

        resized_image = resize_and_show(screenshot)

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

            if not results.multi_hand_landmarks:
                return JsonResponse(
                    {'status': False, 'message': 'No hands detected', 'game_id': game_id,
                     'game_status': game.game_status})
            else:
                # Draw hand landmarks of each hand.
                image_height, image_width, _ = resized_image.shape
                annotated_image = cv2.flip(resized_image.copy(), 1)
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        annotated_image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

            hand_image = crop_handbox(annotated_image, hand_landmarks, image_height, image_width, resize_and_show)
            class_name, confidence_score = process_image(hand_image)

            # cv2.imshow('MediaPipe Hands', hand_image)
            # cv2.waitKey(0)
            folder = r"C:\Users\seppe\PycharmProjects\st-2223-1-d-ee-SeppeWillems13\src\project\base\hand_recognition\application_images"
            cv2.imwrite(f"{folder}\{confidence_score}.jpg", hand_image)

            # if confidence_score is less than 0.5, return error
            if confidence_score < 0.5:
                return JsonResponse(
                    {'success': False, 'player_move': class_name, 'confidence_score': str(confidence_score),
                     'hands_detected': True, 'score': game.score})
            else:
                _round = Round.objects.create(game=game)
                _round.play_offline_round(class_name, game_id)
                _round.save()
                outcome = _round.outcome
                computer_move = _round.opponent_move

                return JsonResponse(
                    {'success': True, 'player_move': class_name, 'confidence_score': str(confidence_score),
                     'hands_detected': True, 'computer_move': computer_move, 'result': outcome,
                     'score': game.score, 'game_over': game.game_status == 'Completed', 'winner': game.result})
    else:
        return JsonResponse({'success': False, 'message': 'Game is already finished'})


def crop_handbox(annotated_image, hand_landmarks, image_height, image_width, resize_and_show):
    min_x, min_y, max_x, max_y = 1.0, 1.0, 0.0, 0.0
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
