import json
from datetime import date


def build_website_jsonld(request):
    """Build WebSite + SearchAction JSON-LD for the homepage."""
    base_url = f"{request.scheme}://{request.get_host()}"
    data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "LRG Network",
        "url": f"{base_url}/",
        "description": (
            "Discover and connect with Live Reality Games — fan-created "
            "competitions inspired by Survivor, Big Brother, The Traitors, and more."
        ),
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{base_url}/games/?q={{search_term_string}}",
            "query-input": "required name=search_term_string",
        },
    }
    return json.dumps(data)


def build_event_jsonld(game, request):
    """Build Event JSON-LD for a game detail page.

    Only returns JSON if the game has a concrete upcoming start date.
    Returns None if no valid event data is available.
    """
    upcoming = (
        game.next_season_date.filter(start_date__gte=date.today())
        .order_by("start_date")
        .first()
    )
    if not upcoming or not upcoming.start_date:
        return None

    base_url = f"{request.scheme}://{request.get_host()}"
    data = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": game.name,
        "description": (
            f"{game.name} — a {game.get_game_format_display()} style "
            f"Live Reality Game in {game.location_display()}."
        ),
        "url": f"{base_url}{request.path}",
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "startDate": upcoming.start_date.isoformat(),
        "location": {
            "@type": "Place",
            "name": game.location_display(),
            "address": _build_address(game),
        },
    }

    if upcoming.end_date:
        data["endDate"] = upcoming.end_date.isoformat()

    if game.host:
        data["organizer"] = {"@type": "Person", "name": game.host}

    if game.logo:
        logo_url = game.logo.url
        if not logo_url.startswith("http"):
            logo_url = f"{base_url}{logo_url}"
        data["image"] = logo_url

    return json.dumps(data)


def _build_address(game):
    """Build a PostalAddress dict from game location fields."""
    address = {"@type": "PostalAddress"}
    if game.city:
        address["addressLocality"] = game.city.name
    if game.region:
        address["addressRegion"] = game.region.name
    if game.country:
        address["addressCountry"] = game.country.code2 or game.country.name
    return address
