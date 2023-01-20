from django.urls import path

from . import views
from . import room_logic, game_logic
urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),

    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),

    path('join-room/str:code/', room_logic.joinRoom, name="join-room"),
    path('leave_room/<str:room_code>/', room_logic.leave_room, name='leave_room'),
    path('create-room/', room_logic.createRoom, name="create-room"),
    path('update-room/<str:pk>/', room_logic.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', room_logic.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.deleteGame, name="delete-message"),

    path('update-user/', views.updateUser, name="update-user"),
    path('players/', views.playersPage, name="players"),
    path('activity/', views.activityPage, name="activity"),

    path('start_game_offline/<str:room_id>', views.start_game_offline, name='start_game_offline'),
    path('play_round/<str:game_id>/', game_logic.play_round, name='play_round'),
    path('game_detail/<str:game_id>/', views.game_detail, name='game_detail'),
]
