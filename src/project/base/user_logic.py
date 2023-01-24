from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import UserForm, MyUserCreationForm
from .models import Room, Game, Player
from .models import User


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


def registerPage(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            if user.avatar == '':
                user.avatar = 'https://picsum.photos/200'
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

def logoutUser(request):
    logout(request)
    return redirect('home')

def get_user(request, member_id):
    user = get_object_or_404(User, pk=member_id)
    user_data = {
        'name': user.username,
        'email': user.email,
    }
    return JsonResponse(user_data)


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


def userProfile(request, pk):
    user = get_object_or_404(User, pk=pk)
    player = Player.objects.get(user=user)
    rooms = Room.objects.filter(host=user)
    room_games = Game.objects.filter(Q(user=user) | Q(opponent=user), game_status='Completed').order_by('-updated')[0:5]
    template_name = 'base/profile.html'
    context = {'user': user, 'rooms': rooms,
               'room_games': room_games, 'player': player}
    return render(request, template_name, context)


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