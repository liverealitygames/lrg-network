from cities_light.models import Country, Region, City
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from games.models import Game


def game_list(request):
    query = request.GET.get("q", "")
    game_format = request.GET.get("game_format")
    game_duration = request.GET.get("game_duration")
    filming_status = request.GET.get("filming_status")
    only_active = request.GET.get("only_active") == "on"
    only_for_charity = request.GET.get("only_for_charity") == "on"
    include_college_games = request.GET.get("include_college_games") == "on"
    include_friends_and_family = request.GET.get("include_friends_and_family") == "on"
    country_id = request.GET.get("country")
    region_id = request.GET.get("region")
    city_id = request.GET.get("city")

    games = Game.objects.all().order_by("name")

    if query:
        games = games.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if game_format:
        games = games.filter(game_format=game_format)

    if game_duration:
        games = games.filter(game_duration=game_duration)

    if filming_status:
        games = games.filter(filming_status=filming_status)

    if only_active:
        games = games.filter(active=True)

    if only_for_charity:
        games = games.filter(for_charity=True)

    if not include_college_games:
        games = games.filter(Q(college_game=False) | Q(college_game__isnull=True))

    if not include_friends_and_family:
        games = games.filter(
            Q(friends_and_family=False) | Q(friends_and_family__isnull=True)
        )

    if country_id:
        games = games.filter(country_id=country_id)

    if region_id:
        games = games.filter(region_id=region_id)

    if city_id:
        games = games.filter(city_id=city_id)

    paginator = Paginator(games, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    game_formats = Game.GameFormat.choices
    game_durations = Game.GameDuration.choices
    filming_statuses = Game.FilmingStatus.choices
    countries = Country.objects.all()
    regions = Region.objects.filter(country_id=country_id) if country_id else []
    cities = City.objects.filter(region_id=region_id) if region_id else []

    return render(
        request,
        "games/game_list.html",
        {
            "page_obj": page_obj,
            "query": query,
            "game_formats": game_formats,
            "game_durations": game_durations,
            "filming_statuses": filming_statuses,
            "countries": countries,
            "regions": regions,
            "cities": cities,
            "selected_country": country_id,
            "selected_region": region_id,
            "selected_city": city_id,
            "selected_game_format": game_format,
            "selected_game_duration": game_duration,
            "selected_filming_status": filming_status,
            "only_active": only_active,
            "only_for_charity": only_for_charity,
            "include_college_games": include_college_games,
            "include_friends_and_family": include_friends_and_family,
        },
    )


def game_detail(request, slug):
    game = Game.objects.get(slug=slug)
    return render(request, "games/game_detail.html", {"game": game})
