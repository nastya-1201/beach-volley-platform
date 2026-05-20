from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('players/', views.players_list, name='players'),
    path('tournaments/', views.tournaments_list, name='tournaments'),
    path('tournaments/<int:tournament_id>/', views.tournament_detail, name='tournament_detail'),
    path('matches/', views.matches_list, name='matches'),
    path('matches/<int:match_id>/', views.match_detail, name='match_detail'),
    path('courts/', views.courts_list, name='courts'),
    path('standings/', views.standings, name='standings'),
    path('tournaments/<int:tournament_id>/bracket/save/', views.save_bracket, name='save_bracket'),
    path('tournaments/<int:tournament_id>/bracket/load/', views.load_bracket, name='load_bracket'),
    path('players/<int:player_id>/', views.player_detail, name='player_detail'),
]
