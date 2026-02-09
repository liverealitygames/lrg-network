import json
import os
from typing import Dict, Any, Optional
from django.db.models import QuerySet, Count, Avg
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from cities_light.models import Country, Region, City
from django.core.paginator import Paginator
from django.db.models import Q

from games.models import Game, GameImages


def _get_country_centroids() -> Dict[str, list]:
    """Load country code -> [lat, lng] from fixtures. Cached at module level."""
    if not hasattr(_get_country_centroids, "_cache"):
        path = os.path.join(
            os.path.dirname(__file__), "fixtures", "country_centroids.json"
        )
        with open(path, encoding="utf-8") as f:
            _get_country_centroids._cache = json.load(f)
    return _get_country_centroids._cache


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

    # Multi-value filters (format, duration, viewing status)
    game_formats = filters.get("game_formats") or []
    if game_formats:
        games = games.filter(game_format__in=game_formats)

    game_durations = filters.get("game_durations") or []
    if game_durations:
        games = games.filter(game_duration__in=game_durations)

    filming_statuses = filters.get("filming_statuses") or []
    if filming_statuses:
        games = games.filter(filming_status__in=filming_statuses)

    # Location filters
    if filters.get("country_id"):
        games = games.filter(country_id=filters["country_id"])

    if filters.get("no_region"):
        games = games.filter(region_id__isnull=True)

    if filters.get("region_id"):
        games = games.filter(region_id=filters["region_id"])

    if filters.get("no_city"):
        games = games.filter(city_id__isnull=True)

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


GAME_LIST_PAGE_SIZE = 12  # Divisible by 2 and 3 for grid layout


def game_list(request: HttpRequest) -> HttpResponse:
    """
    Display a paginated list of games with filtering options.
    """
    # Extract filter parameters from request (format/duration/status are multi-select)
    filters = {
        "query": request.GET.get("q", ""),
        "game_formats": request.GET.getlist("game_format"),
        "game_durations": request.GET.getlist("game_duration"),
        "filming_statuses": request.GET.getlist("filming_status"),
        "country_id": request.GET.get("country"),
        "no_region": request.GET.get("no_region") == "1",
        "region_id": request.GET.get("region"),
        "no_city": request.GET.get("no_city") == "1",
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
    paginator = Paginator(games, GAME_LIST_PAGE_SIZE)
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

    # View mode: list or map (Redfin/Zillow-style toggle)
    view_mode = request.GET.get("view", "list")
    if view_mode not in ("list", "map"):
        view_mode = "list"

    # URLs for List/Map toggle (preserve current filters)
    get_copy = request.GET.copy()
    get_copy["view"] = "list"
    list_view_url = reverse("game_list") + "?" + get_copy.urlencode()
    get_copy["view"] = "map"
    map_view_url = reverse("game_list") + "?" + get_copy.urlencode()

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
        "selected_game_formats": filters["game_formats"],
        "selected_game_durations": filters["game_durations"],
        "selected_filming_statuses": filters["filming_statuses"],
        "inactive_filter": filters["inactive_filter"],
        "college_filter": filters["college_filter"],
        "friends_and_family_filter": filters["friends_and_family_filter"],
        "charity_filter": filters["charity_filter"],
        "casting_filter": filters["casting_filter"],
        "pagination_querystring": pagination_querystring,
        "view_mode": view_mode,
        "list_view_url": list_view_url,
        "map_view_url": map_view_url,
        **location_context,  # Unpack location context (countries, regions, etc.)
    }

    return render(request, "games/games.html", context)


def game_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Display details for a single game by slug.

    Args:
        request: HTTP request object
        slug: Game slug identifier

    Returns:
        Rendered game detail template with game context

    Raises:
        Http404: If game with given slug doesn't exist
    """
    game = get_object_or_404(
        Game.objects.select_related("country", "region", "city").prefetch_related(
            "seasons", "images", "next_season_date"
        ),
        slug=slug,
    )
    return render(request, "games/game_detail.html", {"game": game})


def _get_map_filters(request: HttpRequest) -> Dict[str, Any]:
    """Build the same filter dict as game_list for map data and location games."""
    return {
        "query": request.GET.get("q", ""),
        "game_formats": request.GET.getlist("game_format"),
        "game_durations": request.GET.getlist("game_duration"),
        "filming_statuses": request.GET.getlist("filming_status"),
        "country_id": request.GET.get("country"),
        "no_region": request.GET.get("no_region") == "1",
        "region_id": request.GET.get("region"),
        "no_city": request.GET.get("no_city") == "1",
        "city_id": request.GET.get("city"),
        "inactive_filter": request.GET.get("inactive_filter", ""),
        "college_filter": request.GET.get("college_filter", ""),
        "friends_and_family_filter": request.GET.get("friends_and_family_filter", ""),
        "charity_filter": request.GET.get("charity_filter", ""),
        "casting_filter": request.GET.get("casting_filter", ""),
    }


def map_data(request: HttpRequest) -> JsonResponse:
    """
    Return JSON with game counts and coordinates for countries, regions, and cities.
    Accepts same GET params as game_list so the map reflects current filters.
    """
    base = Game.objects.filter(is_removed=False)
    base = _apply_filters(base, _get_map_filters(request))
    centroids = _get_country_centroids()

    # Countries with at least one game
    country_counts = (
        base.values("country_id").annotate(count=Count("id")).order_by("-count")
    )
    country_ids = [r["country_id"] for r in country_counts]
    countries_qs = Country.objects.filter(id__in=country_ids).in_bulk()

    countries = []
    for row in country_counts:
        c = countries_qs.get(row["country_id"])
        if not c:
            continue
        code2 = c.code2 or ""
        lat, lng = centroids.get(code2, [0.0, 0.0])
        countries.append(
            {
                "id": str(c.id),
                "name": c.name,
                "code2": code2,
                "count": row["count"],
                "lat": float(lat),
                "lng": float(lng),
            }
        )

    # Regions with at least one game
    region_counts = (
        base.filter(region_id__isnull=False)
        .values("region_id")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    region_ids = [r["region_id"] for r in region_counts]
    regions_qs = Region.objects.filter(id__in=region_ids).select_related("country")
    regions_by_id = {r.id: r for r in regions_qs}

    region_coords = {}
    for rid in region_ids:
        agg = City.objects.filter(region_id=rid).aggregate(
            lat=Avg("latitude"), lng=Avg("longitude")
        )
        if agg["lat"] is not None and agg["lng"] is not None:
            region_coords[rid] = [float(agg["lat"]), float(agg["lng"])]

    regions = []
    for row in region_counts:
        r = regions_by_id.get(row["region_id"])
        if not r:
            continue
        code2 = r.country.code2 if r.country_id else ""
        if row["region_id"] in region_coords:
            lat, lng = region_coords[row["region_id"]]
        else:
            lat, lng = centroids.get(code2, [0.0, 0.0])
        regions.append(
            {
                "id": str(r.id),
                "name": r.name,
                "country_id": str(r.country_id),
                "count": row["count"],
                "lat": float(lat),
                "lng": float(lng),
            }
        )

    # Cities with at least one game (must have coordinates)
    city_counts = (
        base.filter(city_id__isnull=False)
        .values("city_id")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    city_ids = [r["city_id"] for r in city_counts]
    cities_qs = (
        City.objects.filter(id__in=city_ids)
        .exclude(latitude__isnull=True)
        .exclude(longitude__isnull=True)
    )
    cities_by_id = {c.id: c for c in cities_qs}

    cities = []
    for row in city_counts:
        c = cities_by_id.get(row["city_id"])
        if not c:
            continue
        cities.append(
            {
                "id": str(c.id),
                "name": c.name,
                "region_id": str(c.region_id) if c.region_id else None,
                "count": row["count"],
                "lat": float(c.latitude),
                "lng": float(c.longitude),
            }
        )

    # Games with no region/state (country-only), so they stay visible when zoomed in
    country_only_counts = (
        base.filter(region_id__isnull=True)
        .values("country_id")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    country_only = []
    for row in country_only_counts:
        c = countries_qs.get(row["country_id"])
        if not c:
            continue
        code2 = c.code2 or ""
        lat, lng = centroids.get(code2, [0.0, 0.0])
        country_only.append(
            {
                "country_id": str(c.id),
                "name": f"{c.name} (no state/region)",
                "count": row["count"],
                "lat": float(lat),
                "lng": float(lng),
            }
        )

    # Games with region but no city, so they stay visible at city zoom level
    region_only_counts = (
        base.filter(region_id__isnull=False, city_id__isnull=True)
        .values("region_id")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    region_only = []
    for row in region_only_counts:
        r = regions_by_id.get(row["region_id"])
        if not r:
            continue
        code2 = r.country.code2 if r.country_id else ""
        if row["region_id"] in region_coords:
            lat, lng = region_coords[row["region_id"]]
        else:
            lat, lng = centroids.get(code2, [0.0, 0.0])
        region_only.append(
            {
                "region_id": str(r.id),
                "name": f"{r.name} (no city)",
                "count": row["count"],
                "lat": float(lat),
                "lng": float(lng),
            }
        )

    return JsonResponse(
        {
            "countries": countries,
            "regions": regions,
            "cities": cities,
            "country_only": country_only,
            "region_only": region_only,
        }
    )


def map_location_games(request: HttpRequest) -> JsonResponse:
    """
    Return JSON list of games for a given location (for map side panel).
    GET params: country, region, city, no_region=1, no_city=1 plus all game_list filters.
    Returns: { games: [...], location_label: str, game_list_url: str }
    """
    filters = _get_map_filters(request)
    if not any([filters["country_id"], filters["region_id"], filters["city_id"]]):
        return JsonResponse({"games": [], "location_label": "", "game_list_url": ""})

    base = Game.objects.filter(is_removed=False).select_related(
        "country", "region", "city"
    )
    games = _apply_filters(base, filters).order_by("name")

    # Build location label for panel title
    location_label = ""
    if filters["city_id"]:
        city = City.objects.filter(id=filters["city_id"]).first()
        location_label = city.name if city else "Location"
    elif filters["region_id"]:
        region = (
            Region.objects.filter(id=filters["region_id"])
            .select_related("country")
            .first()
        )
        if region:
            location_label = (
                f"{region.name} (no city)" if filters["no_city"] else region.name
            )
        else:
            location_label = "Location"
    elif filters["country_id"]:
        country = Country.objects.filter(id=filters["country_id"]).first()
        if country:
            location_label = (
                f"{country.name} (no state/region)"
                if filters["no_region"]
                else country.name
            )
        else:
            location_label = "Location"

    # Build game list URL for "View all" link (list view so they see the list of games)
    get_params = request.GET.copy()
    get_params["view"] = "list"
    game_list_url = reverse("game_list") + (
        "?" + get_params.urlencode() if get_params else ""
    )

    def build_absolute_uri(path: Optional[str]) -> Optional[str]:
        if not path:
            return None
        if path.startswith("http"):
            return path
        return request.build_absolute_uri(path)

    games_data = []
    for g in games:
        logo_url = None
        if g.logo:
            logo_url = build_absolute_uri(g.logo.url)
        elif g.get_default_logo_url():
            logo_url = build_absolute_uri(g.get_default_logo_url())
        games_data.append(
            {
                "name": g.name,
                "slug": g.slug,
                "url": reverse("game_detail", args=[g.slug]),
                "logo_url": logo_url,
                "location_display": g.location_display(),
                "college_name": g.college_name or None,
            }
        )
    return JsonResponse(
        {
            "games": games_data,
            "location_label": location_label,
            "game_list_url": game_list_url,
        }
    )


def map_view(request: HttpRequest) -> HttpResponse:
    """Redirect to games list with map view (list/map unified on games page)."""
    get_params = request.GET.copy()
    get_params["view"] = "map"
    return redirect(reverse("game_list") + "?" + get_params.urlencode())


GALLERY_PAGE_SIZE = 24


def gallery(request: HttpRequest) -> HttpResponse:
    """
    Display a paginated gallery of images from all games.
    Order is deterministic but not chronological (by id; UUIDs give stable semi-random order).
    Each image links to its game's detail page.
    """
    queryset = (
        GameImages.objects.filter(is_removed=False)
        .select_related("game")
        .filter(game__is_removed=False)
        .order_by("id")
    )
    paginator = Paginator(queryset, GALLERY_PAGE_SIZE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "games/gallery.html",
        {"images": page_obj.object_list, "page_obj": page_obj},
    )
