from collections import OrderedDict
from django.shortcuts import render, get_object_or_404, redirect
from .models import Tournament, Player, TournamentPair, Match, Court, News
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


SIZE_CHOICES = [
    (6, '6 команд'),
    (8, '8 команд'),
    (10, '10 команд'),
    (12, '12 команд'),
    (16, '16 команд'),
    (24, '24 команды'),
    (32, '32 команды'),
]


def home(request):
    latest_news = News.objects.order_by('-created_at')[:3]
    return render(request, 'tournament/home.html', {'latest_news': latest_news})


def players_list(request):
    query = request.GET.get('q', '')
    players = Player.objects.all()
    if query:
        players = players.filter(last_name__icontains=query) | players.filter(first_name__icontains=query)
    return render(request, 'tournament/players.html', {'players': players, 'query': query})


def matches_list(request):
    pair_query = request.GET.get('pair', '')
    status_query = request.GET.get('status', '')
    matches = Match.objects.select_related('pair1', 'pair2', 'court', 'tournament', 'winner').all()
    if pair_query:
        matches = matches.filter(pair1__player1__last_name__icontains=pair_query) \
            | matches.filter(pair1__player2__last_name__icontains=pair_query) \
            | matches.filter(pair2__player1__last_name__icontains=pair_query) \
            | matches.filter(pair2__player2__last_name__icontains=pair_query)
    if status_query:
        matches = matches.filter(status=status_query)
    return render(request, 'tournament/matches.html', {
        'matches': matches, 'pair_query': pair_query, 'status_query': status_query,
    })


def match_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    sets = match.sets.all().order_by('set_number')
    return render(request, 'tournament/match_detail.html', {'match': match, 'sets': sets})


def courts_list(request):
    query = request.GET.get('q', '')
    courts = Court.objects.all()
    if query:
        courts = courts.filter(name__icontains=query) | courts.filter(address__icontains=query)
    return render(request, 'tournament/courts.html', {'courts': courts, 'query': query})


def standings(request):
    tournaments = Tournament.objects.all()
    selected_tournament = tournaments.first()
    table = []
    if selected_tournament:
        pairs = TournamentPair.objects.filter(tournament=selected_tournament)
        for pair in pairs:
            played = wins = losses = points = 0
            matches = Match.objects.filter(tournament=selected_tournament, status='finished').filter(pair1=pair) \
                | Match.objects.filter(tournament=selected_tournament, status='finished').filter(pair2=pair)
            for match in matches:
                played += 1
                if match.winner == pair:
                    wins += 1; points += 3
                elif match.winner is not None:
                    losses += 1
            table.append({'pair': pair, 'played': played, 'wins': wins, 'losses': losses, 'points': points})
        table = sorted(table, key=lambda x: (-x['points'], -x['wins'], x['losses']))
        for i, row in enumerate(table, start=1):
            row['place'] = i
    return render(request, 'tournament/standings.html', {
        'tournaments': tournaments, 'selected_tournament': selected_tournament, 'table': table,
    })



def tournaments_list(request):
    query = request.GET.get('q', '')
    tournaments = Tournament.objects.all().order_by('-start_date')
    if query:
        tournaments = tournaments.filter(name__icontains=query) | tournaments.filter(location__icontains=query)
    return render(request, 'tournament/tournaments.html', {'tournaments': tournaments, 'query': query})


def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    groups = tournament.groups.all().order_by('name')
    matches = tournament.matches.all().order_by('match_date', 'match_time', 'match_number')
    news_items = tournament.news.all().order_by('-created_at')

    group_tables = []
    for group in groups:
        pairs = group.pairs.all()
        table = []
        for pair in pairs:
            played = wins = losses = points = 0
            finished = Match.objects.filter(tournament=tournament, group=group, status='finished').filter(pair1=pair) \
                | Match.objects.filter(tournament=tournament, group=group, status='finished').filter(pair2=pair)
            for match in finished:
                played += 1
                if match.winner == pair:
                    wins += 1; points += 3
                elif match.winner is not None:
                    losses += 1
            table.append({'pair': pair, 'played': played, 'wins': wins, 'losses': losses, 'points': points})
        table = sorted(table, key=lambda x: (-x['points'], -x['wins'], x['losses']))
        for i, row in enumerate(table, start=1):
            row['place'] = i
        group_tables.append({'group': group, 'table': table})

    return render(request, 'tournament/tournament_detail.html', {
        'tournament': tournament,
        'groups': groups,
        'matches': matches,
        'group_tables': group_tables,
        'news_items': news_items,
        'size_choices': SIZE_CHOICES,
    })


def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    pairs = TournamentPair.objects.filter(player1=player) | TournamentPair.objects.filter(player2=player)
    history = [{'tournament': pair.tournament, 'pair': pair} for pair in pairs]
    return render(request, 'tournament/player_detail.html', {'player': player, 'history': history})
@csrf_exempt
@require_http_methods(['POST'])
def save_bracket(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    try:
        data = json.loads(request.body)
        tournament.bracket_data = data
        tournament.save()
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def load_bracket(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    return JsonResponse({'data': tournament.bracket_data or {}})
