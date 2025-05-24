from django.core.paginator import Paginator
from django.shortcuts import render

from games.models import Game


def game_list(request):
    game_queryset = Game.objects.all().order_by("name")  # or whatever ordering
    paginator = Paginator(game_queryset, 10)  # 10 games per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "games/game_list.html", {"page_obj": page_obj})


def game_detail(request, slug):
    game = Game.objects.get(slug=slug)
    return render(request, "games/game_detail.html", {"game": game})
