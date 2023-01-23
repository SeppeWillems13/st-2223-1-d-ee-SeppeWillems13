from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from .forms import RoomForm
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
    form = RoomForm(request.POST)
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
            player = Player.objects.get(user=request.user)
            _room = _room[0]
            _room.players.add(player)
            return redirect('room', pk=_room.code)
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
