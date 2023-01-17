from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User, Game
from django import forms


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'code', 'online']
        exclude = ("host",)
        widgets = {
            'online': forms.Select(choices=[(True, 'Online'), (False, 'Offline')]),
            'code': forms.TextInput(attrs={'required': 'true'}),
            'name': forms.TextInput(attrs={'required': 'true'}),
        }


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['best_of']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']
