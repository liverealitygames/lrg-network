from cities_light.models import Country, Region, City
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from urllib.parse import urlencode

from games.models import Game


def game_list(request):
    query = request.GET.get("q", "")
    game_format = request.GET.get("game_format")
    game_duration = request.GET.get("game_duration")
    filming_status = request.GET.get("filming_status")
    only_for_charity = request.GET.get("only_for_charity") == "on"
    include_college_games = request.GET.get("include_college_games") == "on"
    include_friends_and_family = request.GET.get("include_friends_and_family") == "on"
    country_id = request.GET.get("country")
    region_id = request.GET.get("region")
    city_id = request.GET.get("city")
    include_inactive = request.GET.get("include_inactive") == "on"

    games = Game.objects.all().order_by("name")

    if query:
        games = games.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if game_format:
        games = games.filter(game_format=game_format)

    if game_duration:
        games = games.filter(game_duration=game_duration)

    if filming_status:
        games = games.filter(filming_status=filming_status)

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

    # Only show active games by default, unless include_inactive is checked
    if not include_inactive:
        games = games.filter(active=True)

    paginator = Paginator(games, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Build querystring for pagination, excluding 'page'
    get_params = request.GET.copy()
    if "page" in get_params:
        get_params.pop("page")
    pagination_querystring = get_params.urlencode()

    game_formats = Game.GameFormat.choices
    game_durations = Game.GameDuration.choices
    filming_statuses = Game.FilmingStatus.choices
    countries = Country.objects.filter(
        id__in=Game.objects.values_list("country_id", flat=True).distinct()
    )
    if country_id:
        regions_with_games = set(
            Game.objects.filter(country_id=country_id)
            .values_list("region_id", flat=True)
            .distinct()
        )
        regions = Region.objects.filter(country_id=country_id)
    else:
        regions = []
        regions_with_games = set()

    if region_id:
        cities = City.objects.filter(
            id__in=Game.objects.values_list("city_id", flat=True).distinct(),
            region_id=region_id,
        )
    else:
        cities = []

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
            "regions_with_games": regions_with_games,
            "cities": cities,
            "selected_country": country_id,
            "selected_region": region_id,
            "selected_city": city_id,
            "selected_game_format": game_format,
            "selected_game_duration": game_duration,
            "selected_filming_status": filming_status,
            "only_for_charity": only_for_charity,
            "include_college_games": include_college_games,
            "include_friends_and_family": include_friends_and_family,
            "include_inactive": include_inactive,
            "pagination_querystring": pagination_querystring,
        },
    )


def game_detail(request, slug):
    game = Game.objects.get(slug=slug)
    return render(request, "games/game_detail.html", {"game": game})
