from django.contrib import admin
from .models import Tournament, TournamentGroup, Player, TournamentPair, Court, Match, SetResult, News

admin.site.site_header = 'Администрирование Beach Volley Platform'
admin.site.site_title = 'Панель администратора'
admin.site.index_title = 'Управление данными турниров'

admin.site.register(Tournament)
admin.site.register(TournamentGroup)
admin.site.register(Player)
admin.site.register(TournamentPair)
admin.site.register(Court)
admin.site.register(Match)
admin.site.register(SetResult)
admin.site.register(News)