from django.shortcuts import render
from django.shortcuts import redirect

from sc2game.models import Game, Player, Stream, Bracket


def index(request):

    streams = Stream.objects.filter(up=True)

    if len(streams) == 0:
        return render(request, 'sc2game/nothing_on.html')
    if len(streams) == 1:
        return redirect('/' + streams[0].url)

    context = {
        'streams': streams
    }

    return render(request, 'sc2game/index.html', context)


def stream(request, stream_url):
    stream_obj = Stream.objects.get(url=stream_url)
    streams = Stream.objects.filter(up=True)
    game = Game.objects.get(stream=stream_obj)
    players = Player.objects.filter(stream=stream_obj)
    bracket = Bracket.objects.filter(stream=stream_obj)
    if bracket:
        bracket = bracket[0]
    
    row_objs = []
    consistent_rows = ['name', 'score', 'supply', 'minerals', 'gas']
    consistent_row_names = ['Players',
                            'Score',
                            'Supply',
                            'Minerals',
                            'Gas']
    for field, name in zip(consistent_rows, consistent_row_names):
        row = {}
        row["player_1"] = getattr(players[0], field)
        row["player_2"] = getattr(players[1], field)
        row["name"] = name
        row_objs.append(row)
        
    optional_rows = ['workers', 'army']
    optional_row_names = ['Workers', 'Army']
    for field, name in zip(optional_rows, optional_row_names):
        if str(getattr(players[0], field)) != "-2":
            row = {}
            row["player_1"] = getattr(players[0], field)
            row["player_2"] = getattr(players[1], field)
            row["name"] = name
            row_objs.append(row)

    context = {
        'player_1': players[0],
        'player_2': players[1],
        'game': game,
        'stream_obj': stream_obj,
        'row_objs': row_objs,
        'streams': streams,
        'bracket': bracket
    }

    return render(request, 'sc2game/stream.html', context)
