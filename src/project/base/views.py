import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.core.validators import EmailValidator
from django.db.models import Q
from django.forms import Form
from django.http import HttpResponse, Http404, StreamingHttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from .forms import UserForm, MyUserCreationForm, RoomForm
from .models import Room, Game, User, Player


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
            # Create a new game instance
            game = Game.objects.create(
                user=request.user,
                room=_room,
                body=request.POST.get('body')
            )
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
            room.players.remove(player)
            room.save()
        else:
            print('Room does not exist')
        return redirect('home')
    else:
        return redirect('home')


def test_hand(request):
    if request.GET.get('hand'):
        hand = request.GET.get('hand')
        hand = hand.split(',')
        hand = [int(i) for i in hand]
        hand.sort()
        print(hand)
        return HttpResponse(hand)
    else:
        return HttpResponse('No hand')

