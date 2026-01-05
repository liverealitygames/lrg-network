from cities_light.models import Country, Region, City
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from games.models import Game


def game_list(request):
    query = request.GET.get("q", "")
    game_format = request.GET.get("game_format")
    game_duration = request.GET.get("game_duration")
    filming_status = request.GET.get("filming_status")
    country_id = request.GET.get("country")
    region_id = request.GET.get("region")
    city_id = request.GET.get("city")
    inactive_filter = request.GET.get("inactive_filter", "")
    college_filter = request.GET.get("college_filter", "")
    friends_and_family_filter = request.GET.get("friends_and_family_filter", "")
    charity_filter = request.GET.get("charity_filter", "")
    casting_filter = request.GET.get("casting_filter", "")

    games = Game.objects.select_related("country", "region", "city").order_by("name")

    if query:
        games = games.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if game_format:
        games = games.filter(game_format=game_format)

    if game_duration:
        games = games.filter(game_duration=game_duration)

    if filming_status:
        games = games.filter(filming_status=filming_status)

    if country_id:
        games = games.filter(country_id=country_id)

    if region_id:
        games = games.filter(region_id=region_id)

    if city_id:
        games = games.filter(city_id=city_id)

    # Inactive Games trinary filter
    if inactive_filter == "exclude":
        games = games.filter(active=True)
    elif inactive_filter == "only":
        games = games.filter(active=False)

    # College Only Games trinary filter
    if college_filter == "exclude":
        games = games.filter(Q(college_game=False) | Q(college_game__isnull=True))
    elif college_filter == "only":
        games = games.filter(college_game=True)

    # Friends & Family Only Games trinary filter
    if friends_and_family_filter == "exclude":
        games = games.filter(
            Q(friends_and_family=False) | Q(friends_and_family__isnull=True)
        )
    elif friends_and_family_filter == "only":
        games = games.filter(friends_and_family=True)

    # Charity Games trinary filter
    if charity_filter == "exclude":
        games = games.filter(Q(for_charity=False) | Q(for_charity__isnull=True))
    elif charity_filter == "only":
        games = games.filter(for_charity=True)

    # Casting Games trinary filter
    if casting_filter == "exclude":
        games = games.filter(Q(casting_link__isnull=True) | Q(casting_link=""))
    elif casting_filter == "only":
        games = games.filter(casting_link__isnull=False).exclude(casting_link="")

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
            "inactive_filter": inactive_filter,
            "college_filter": college_filter,
            "friends_and_family_filter": friends_and_family_filter,
            "charity_filter": charity_filter,
            "casting_filter": casting_filter,
            "pagination_querystring": pagination_querystring,
        },
    )


def game_detail(request, slug):
    game = get_object_or_404(
        Game.objects.select_related("country", "region", "city").prefetch_related(
            "seasons", "images", "next_season_date"
        ),
        slug=slug,
    )
    return render(request, "games/game_detail.html", {"game": game})
