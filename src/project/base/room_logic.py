import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from .forms import RoomForm, JoinRoomForm
from .models import Room, Player


def createRoom(request):
    if request.method == 'POST':
        form = RoomForm(request.POST or None, host_id=request.user.id)
        print(form.errors)
        if form.is_valid():
            _room = form.save(commit=False)
            _room.host = request.user
            _room.save()

            messages.success(request, 'Room created successfully')
            return redirect('room', pk=_room.code)
        else:
            messages.error(request, 'An error occurred while creating the _room')
    else:
        form = RoomForm(host_id=request.user.id)

    template_name = 'base/room_form.html'
    context = {'form': form}
    return render(request, template_name, context)


@login_required(login_url='login')
def joinRoom(request):
    form = JoinRoomForm(request.POST)
    template_name = 'base/join_room.html'
    # Render the template with the form and topics
    context = {'form': form}

    # check if post request
    if request.method == 'POST':
        # get the _room code
        room_code = request.POST.get('code')
        # check if _room exists
        _room = Room.objects.filter(code=room_code)
        if _room.exists():
            return redirect('room', pk=room_code)
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
        _room = get_object_or_404(Room, code=pk)
    except Http404:
        # Handle the case where the room does not exist
        return render(request, 'base/room_not_found.html', {'pk': pk})
    # Create a form instance with POST data, if available
    form = RoomForm(request.POST or None, host_id=request.user.id, instance=_room)
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
    if request.user != _room.host and not _room.is_online:
        return room_not_found(request, pk)
    if request.user != _room.host and not _room.is_online and _room.opponent is not None:
        return room_not_found(request, pk)
    # if request user is not host and is is_online and opponent is None add user to opponent and save and join room
    if request.user != _room.host and _room.is_online and _room.opponent is None:
        _room.opponent = request.user
        _room.save()
        return render(request, template_name, {'room': _room})
    room_games = _room.game_set.select_related('user').all()

    #if room is online players is host and opponent else only host
    if _room.is_online:
        players = Player.objects.filter(Q(user=_room.host) | Q(user=_room.opponent))
    else:
        players = Player.objects.filter(user=_room.host)

    players_json = serializers.serialize("json", players)

    print("players", players)
    host_id = json.dumps(_room.host.id)
    current_user_id = json.dumps(request.user.id)
    if _room.opponent is not None:
        opponent_id = json.dumps(_room.opponent.id)
    else:
        opponent_id = None
    context = {'room': _room, 'room_games': room_games,
               'players': players, 'players_json': players_json,
               'host_id': host_id, 'opponent_id': opponent_id, 'current_user_id': current_user_id}

    print("is online", _room.is_online)
    return render(request, template_name, context)


def room_not_found(request, pk):
    context = {"pk": pk}
    return render(request, 'base/room_not_found.html', context)
