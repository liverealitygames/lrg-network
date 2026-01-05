from typing import Dict, Any, Optional
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet
from cities_light.models import Country, Region, City
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from games.models import Game


def _apply_filters(queryset: QuerySet[Game], filters: Dict[str, Any]) -> QuerySet[Game]:
    """
    Apply filters to a Game queryset based on filter parameters.

    Args:
        queryset: Base Game queryset
        filters: Dict containing filter values

    Returns:
        Filtered queryset
    """
    games = queryset

    # Text search
    if filters.get("query"):
        games = games.filter(
            Q(name__icontains=filters["query"])
            | Q(description__icontains=filters["query"])
        )

    # Direct field filters
    if filters.get("game_format"):
        games = games.filter(game_format=filters["game_format"])

    if filters.get("game_duration"):
        games = games.filter(game_duration=filters["game_duration"])

    if filters.get("filming_status"):
        games = games.filter(filming_status=filters["filming_status"])

    # Location filters
    if filters.get("country_id"):
        games = games.filter(country_id=filters["country_id"])

    if filters.get("region_id"):
        games = games.filter(region_id=filters["region_id"])

    if filters.get("city_id"):
        games = games.filter(city_id=filters["city_id"])

    # Trinary filters (include/exclude/only)
    inactive_filter = filters.get("inactive_filter", "")
    if inactive_filter == "exclude":
        games = games.filter(active=True)
    elif inactive_filter == "only":
        games = games.filter(active=False)

    college_filter = filters.get("college_filter", "")
    if college_filter == "exclude":
        games = games.filter(Q(college_game=False) | Q(college_game__isnull=True))
    elif college_filter == "only":
        games = games.filter(college_game=True)

    friends_and_family_filter = filters.get("friends_and_family_filter", "")
    if friends_and_family_filter == "exclude":
        games = games.filter(
            Q(friends_and_family=False) | Q(friends_and_family__isnull=True)
        )
    elif friends_and_family_filter == "only":
        games = games.filter(friends_and_family=True)

    charity_filter = filters.get("charity_filter", "")
    if charity_filter == "exclude":
        games = games.filter(Q(for_charity=False) | Q(for_charity__isnull=True))
    elif charity_filter == "only":
        games = games.filter(for_charity=True)

    casting_filter = filters.get("casting_filter", "")
    if casting_filter == "exclude":
        games = games.filter(Q(casting_link__isnull=True) | Q(casting_link=""))
    elif casting_filter == "only":
        games = games.filter(casting_link__isnull=False).exclude(casting_link="")

    return games


def _build_location_context(
    country_id: Optional[str], region_id: Optional[str]
) -> Dict[str, Any]:
    """
    Build context for location dropdowns (countries, regions, cities).

    Args:
        country_id: Selected country ID (optional)
        region_id: Selected region ID (optional)

    Returns:
        Dict with countries, regions, regions_with_games, cities
    """
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

    return {
        "countries": countries,
        "regions": regions,
        "regions_with_games": regions_with_games,
        "cities": cities,
    }


def game_list(request: HttpRequest) -> HttpResponse:
    """
    Display a paginated list of games with filtering options.
    """
    # Extract filter parameters from request
    filters = {
        "query": request.GET.get("q", ""),
        "game_format": request.GET.get("game_format"),
        "game_duration": request.GET.get("game_duration"),
        "filming_status": request.GET.get("filming_status"),
        "country_id": request.GET.get("country"),
        "region_id": request.GET.get("region"),
        "city_id": request.GET.get("city"),
        "inactive_filter": request.GET.get("inactive_filter", ""),
        "college_filter": request.GET.get("college_filter", ""),
        "friends_and_family_filter": request.GET.get("friends_and_family_filter", ""),
        "charity_filter": request.GET.get("charity_filter", ""),
        "casting_filter": request.GET.get("casting_filter", ""),
    }

    # Get base queryset with optimizations
    games = Game.objects.select_related("country", "region", "city").order_by("name")

    # Apply filters
    games = _apply_filters(games, filters)

    # Pagination
    paginator = Paginator(games, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Build querystring for pagination, excluding 'page'
    get_params = request.GET.copy()
    if "page" in get_params:
        get_params.pop("page")
    pagination_querystring = get_params.urlencode()

    # Build location context for dropdowns
    location_context = _build_location_context(
        filters["country_id"], filters["region_id"]
    )

    # Build template context
    context = {
        "page_obj": page_obj,
        "query": filters["query"],
        "game_formats": Game.GameFormat.choices,
        "game_durations": Game.GameDuration.choices,
        "filming_statuses": Game.FilmingStatus.choices,
        "selected_country": filters["country_id"],
        "selected_region": filters["region_id"],
        "selected_city": filters["city_id"],
        "selected_game_format": filters["game_format"],
        "selected_game_duration": filters["game_duration"],
        "selected_filming_status": filters["filming_status"],
        "inactive_filter": filters["inactive_filter"],
        "college_filter": filters["college_filter"],
        "friends_and_family_filter": filters["friends_and_family_filter"],
        "charity_filter": filters["charity_filter"],
        "casting_filter": filters["casting_filter"],
        "pagination_querystring": pagination_querystring,
        **location_context,  # Unpack location context (countries, regions, etc.)
    }

    return render(request, "games/game_list.html", context)


def game_detail(request: HttpRequest, slug: str) -> HttpResponse:
    game = get_object_or_404(
        Game.objects.select_related("country", "region", "city").prefetch_related(
            "seasons", "images", "next_season_date"
        ),
        slug=slug,
    )
    return render(request, "games/game_detail.html", {"game": game})
