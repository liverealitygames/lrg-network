from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from games.models import Game


def game_list(request):
    query = request.GET.get("q", "")
    games = Game.objects.all().order_by("name")

    if query:
        games = games.filter(Q(name__icontains=query) | Q(description__icontains=query))

    paginator = Paginator(games, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "games/game_list.html",
        {
            "page_obj": page_obj,
            "query": query,
        },
    )


def game_detail(request, slug):
    game = Game.objects.get(slug=slug)
    return render(request, "games/game_detail.html", {"game": game})
