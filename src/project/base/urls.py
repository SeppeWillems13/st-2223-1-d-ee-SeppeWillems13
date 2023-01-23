from django.urls import path

from . import room_logic, game_logic, user_logic
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),

    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),

    path('join-room/str:code/', room_logic.joinRoom, name="join-room"),
    path('create-room/', room_logic.createRoom, name="create-room"),
    path('update-room/<str:pk>/', room_logic.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', room_logic.deleteRoom, name="delete-room"),
    path('delete-game/<str:pk>/', views.deleteGame, name="delete-game"),

    path('update-user/', views.updateUser, name="update-user"),
    path('players/', views.playersPage, name="players"),
    path('activity/', views.activityPage, name="activity"),

    path('start_game_offline/<str:room_id>', views.start_game_offline, name='start_game_offline'),
    path('start_game_online/<str:room_id>', views.start_game_online, name='start_game_online'),
    path('get_round_prediction_offline/<str:game_id>/', game_logic.get_round_prediction_offline, name='get_round_prediction_offline'),
    path('get_round_prediction_online/<str:game_id>/', game_logic.get_round_prediction_online, name='get_round_prediction_online'),
    path('game_detail/<str:game_id>/', views.game_detail, name='game_detail'),
    path('get_user/<str:member_id>/', user_logic.get_user, name='get_user'),
]
