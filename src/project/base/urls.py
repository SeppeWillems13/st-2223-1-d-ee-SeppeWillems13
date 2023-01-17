from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),

    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),

    path('join-room/str:code/', views.joinRoom, name="join-room"),
    path('leave_room/<str:room_code>/', views.leave_room, name='leave_room'),
    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),

    path('update-user/', views.updateUser, name="update-user"),
    path('players/', views.playersPage, name="players"),
    path('activity/', views.activityPage, name="activity"),

    path('start_game_offline/<str:room_id>', views.start_game_offline, name='start_game_offline'),
    path('play_game/<str:game_id>/', views.play_game, name='play_game'),

]
