from django.shortcuts import render

from games.models import Game


def game_list(request):
    games = Game.objects.all()
    return render(request, "games/game_list.html", {"games": games})


def game_detail(request, slug):
    game = Game.objects.get(slug=slug)
    return render(request, "games/game_detail.html", {"game": game})
