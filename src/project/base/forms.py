from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from .models import Room, User, Game


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']


class RoomForm(ModelForm):
    def __init__(self, *args, **kwargs):
        host_id = kwargs.pop('host_id')
        super().__init__(*args, **kwargs)
        self.fields['opponent'].queryset = User.objects.exclude(pk=host_id)

    class Meta:
        model = Room
        fields = ['name', 'code', 'is_online', 'opponent']
        exclude = ("host",)
        widgets = {
            'is_online': forms.Select(choices=[(True, 'Online'), (False, 'Offline')]),
            'opponent': forms.Select(),
            'code': forms.TextInput(attrs={'required': 'true'}),
            'name': forms.TextInput(attrs={'required': 'true'}),
        }


class JoinRoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['code']
        widgets = {
            'code': forms.TextInput(attrs={'required': 'true'}),
        }


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['best_of']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email']
