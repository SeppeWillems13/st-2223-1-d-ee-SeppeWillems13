from django.urls import path

from . import room_logic, game_logic, user_logic
from . import views

urlpatterns = [
    path('', views.home, name="home"),

    # login views
    path('login/', user_logic.loginPage, name="login"),
    path('logout/', user_logic.logoutUser, name="logout"),
    path('register/', user_logic.registerPage, name="register"),
    path('update-user/', user_logic.updateUser, name="update-user"),
    path('profile/<str:pk>/', user_logic.userProfile, name="user-profile"),
    path('get_user/<str:member_id>/', user_logic.get_user, name='get_user'),

    # romm views
    path('room/<str:pk>/', room_logic.room, name="room"),
    path('join-room/str:code/', room_logic.joinRoom, name="join-room"),
    path('create-room/', room_logic.createRoom, name="create-room"),
    path('update-room/<str:pk>/', room_logic.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', room_logic.deleteRoom, name="delete-room"),

    # game views
    path('delete-game/<str:pk>/', game_logic.deleteGame, name="delete-game"),
    path('start_game_offline/<str:room_id>', game_logic.start_game_offline, name='start_game_offline'),
    path('start_game_online/<str:room_id>', game_logic.start_game_online, name='start_game_online'),

    path('game_detail/<str:game_id>/', views.game_detail, name='game_detail'),

    # round views
    path('get_round_prediction_offline/<str:game_id>/', game_logic.get_round_prediction_offline,
         name='get_round_prediction_offline'),
    path('get_round_prediction_online/<str:game_id>/', game_logic.get_round_prediction_online,
         name='get_round_prediction_online'),

]
