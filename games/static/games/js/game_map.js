/**
 * Games map view: Leaflet map with location bubbles and side panel.
 * Expects #games-map with data-map-data-url and data-map-location-games-url.
 */
(function () {
  "use strict";

  const mapEl = document.getElementById("games-map");
  if (!mapEl || typeof L === "undefined") return;

  const mapDataUrl = mapEl.dataset.mapDataUrl || "";
  const mapLocationGamesUrl = mapEl.dataset.mapLocationGamesUrl || "";

  function currentQueryString() {
    return window.location.search ? window.location.search.substring(1) : "";
  }

  const ZOOM_COUNTRY = 4;
  const ZOOM_REGION = 6;
  const BUBBLE_MIN_R = 12;
  const BUBBLE_MAX_R = 28;
  const BUBBLE_SCALE = 3;

  const map = L.map("games-map", {
    minZoom: 2,
    maxBounds: L.latLngBounds(L.latLng(-85, -180), L.latLng(85, 180)),
    maxBoundsViscosity: 1.0,
  }).setView([20, 0], 2);
  L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
    {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: "abcd",
      maxZoom: 20,
      noWrap: true,
    }
  ).addTo(map);

  let data = {
    countries: [],
    regions: [],
    cities: [],
    country_only: [],
    region_only: [],
  };
  const markersLayer = L.layerGroup().addTo(map);

  function radiusFromCount(count) {
    const r = Math.min(BUBBLE_MAX_R, BUBBLE_MIN_R + count * BUBBLE_SCALE);
    return Math.max(BUBBLE_MIN_R, r);
  }

  function bubbleColorClass(item) {
    if (item.type === "country" || item.type === "country_only")
      return "map-bubble--country";
    if (item.type === "region" || item.type === "region_only")
      return "map-bubble--region";
    return "map-bubble--city";
  }

  function getLevel(zoom) {
    if (zoom < ZOOM_COUNTRY) return "country";
    if (zoom < ZOOM_REGION) return "region";
    return "city";
  }

  function inBounds(lat, lng, bounds) {
    if (!bounds) return true;
    return (
      lat >= bounds.getSouth() &&
      lat <= bounds.getNorth() &&
      lng >= bounds.getWest() &&
      lng <= bounds.getEast()
    );
  }

  function buildItems() {
    const zoom = map.getZoom();
    const level = getLevel(zoom);
    const bounds = map.getBounds();
    const captionEl = document.getElementById("map-zoom-caption");
    if (captionEl) {
      if (level === "country")
        captionEl.textContent =
          "Showing countries. Zoom in for regions and cities.";
      else if (level === "region")
        captionEl.textContent =
          "Showing regions and states. Zoom in for cities.";
      else captionEl.textContent = "Showing cities.";
    }
    let items = [];
    if (level === "country") {
      items = data.countries.map(function (c) {
        return {
          id: c.id,
          name: c.name,
          count: c.count,
          lat: c.lat,
          lng: c.lng,
          type: "country",
        };
      });
    } else if (level === "region") {
      items = data.regions
        .filter(function (r) {
          return inBounds(r.lat, r.lng, bounds);
        })
        .map(function (r) {
          return {
            id: r.id,
            name: r.name,
            count: r.count,
            lat: r.lat,
            lng: r.lng,
            type: "region",
          };
        });
      data.country_only
        .filter(function (o) {
          return inBounds(o.lat, o.lng, bounds);
        })
        .forEach(function (o) {
          items.push({
            id: o.country_id,
            name: o.name,
            count: o.count,
            lat: o.lat,
            lng: o.lng,
            type: "country_only",
          });
        });
    } else {
      items = data.cities
        .filter(function (c) {
          return inBounds(c.lat, c.lng, bounds);
        })
        .map(function (c) {
          return {
            id: c.id,
            name: c.name,
            count: c.count,
            lat: c.lat,
            lng: c.lng,
            type: "city",
          };
        });
      data.country_only
        .filter(function (o) {
          return inBounds(o.lat, o.lng, bounds);
        })
        .forEach(function (o) {
          items.push({
            id: o.country_id,
            name: o.name,
            count: o.count,
            lat: o.lat,
            lng: o.lng,
            type: "country_only",
          });
        });
      data.region_only
        .filter(function (o) {
          return inBounds(o.lat, o.lng, bounds);
        })
        .forEach(function (o) {
          items.push({
            id: o.region_id,
            name: o.name,
            count: o.count,
            lat: o.lat,
            lng: o.lng,
            type: "region_only",
          });
        });
    }
    return items;
  }

  function openLocationPanelForItem(item) {
    const params = new URLSearchParams(window.location.search);
    if (item.type === "country_only") {
      params.set("country", item.id);
      params.set("no_region", "1");
    } else if (item.type === "region_only") {
      params.set("region", item.id);
      params.set("no_city", "1");
    } else {
      const param =
        item.type === "country"
          ? "country"
          : item.type === "region"
            ? "region"
            : "city";
      params.set(param, item.id);
    }
    params.set("view", "map");
    openLocationPanel(
      mapLocationGamesUrl + "?" + params.toString(),
      item.name
    );
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function escapeAttr(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML.replace(/"/g, "&quot;");
  }

  function tooltipContent(item) {
    const countText =
      item.count === 1 ? "1 game" : item.count + " games";
    return (
      "<strong>" +
      escapeHtml(item.name || "Location") +
      "</strong><br><span class=\"text-muted\">" +
      countText +
      "</span><br><em>Click to view</em>"
    );
  }

  function updateBubbles() {
    markersLayer.clearLayers();
    const items = buildItems();
    items.forEach(function (item) {
      const r = radiusFromCount(item.count);
      const colorClass = bubbleColorClass(item);
      const icon = L.divIcon({
        className: "map-bubble-div",
        html:
          "<span class=\"map-bubble " +
          colorClass +
          "\" style=\"width:" +
          r * 2 +
          "px;height:" +
          r * 2 +
          "px;line-height:" +
          r * 2 +
          "px;\">" +
          item.count +
          "</span>",
        iconSize: [r * 2, r * 2],
        iconAnchor: [r, r],
      });
      const marker = L.marker([item.lat, item.lng], { icon: icon });
      marker.bindTooltip(tooltipContent(item), {
        permanent: false,
        direction: "top",
        className: "map-bubble-tooltip",
      });
      marker.on("click", function () {
        openLocationPanelForItem(item);
      });
      markersLayer.addLayer(marker);
    });
  }

  map.on("zoomend moveend", updateBubbles);

  const panelEl = document.getElementById("map-side-panel");
  const panelBackdrop = document.getElementById("map-panel-backdrop");
  const panelTitle = document.getElementById("map-panel-title");
  const panelCount = document.getElementById("map-panel-count");
  const panelList = document.getElementById("map-panel-list");
  const panelLoading = document.getElementById("map-panel-loading");
  const panelEmpty = document.getElementById("map-panel-empty");
  const panelCloseBtn = document.getElementById("map-panel-close");

  function closePanel() {
    panelEl.classList.remove("is-open");
    panelBackdrop.classList.remove("is-visible");
    panelBackdrop.setAttribute("aria-hidden", "true");
  }

  function openLocationPanel(url, fallbackTitle) {
    panelEl.classList.add("is-open");
    panelBackdrop.classList.add("is-visible");
    panelBackdrop.setAttribute("aria-hidden", "false");
    panelTitle.textContent = fallbackTitle || "Games";
    panelCount.textContent = "";
    panelList.innerHTML = "";
    panelList.style.display = "none";
    panelEmpty.style.display = "none";
    panelLoading.style.display = "block";
    fetch(url)
      .then(function (res) {
        return res.json();
      })
      .then(function (payload) {
        panelLoading.style.display = "none";
        panelTitle.textContent =
          payload.location_label || fallbackTitle || "Games";
        if (payload.games && payload.games.length > 0) {
          panelCount.textContent =
            payload.games.length === 1
              ? "1 game"
              : payload.games.length + " games";
          panelList.style.display = "block";
          panelList.innerHTML = payload.games
            .map(function (g) {
              const logoHtml = g.logo_url
                ? '<img src="' +
                  escapeAttr(g.logo_url) +
                  '" alt="">'
                : '<span class="map-panel-game-card-no-logo"></span>';
              const meta = [];
              if (g.college_name) meta.push(escapeHtml(g.college_name));
              if (g.location_display)
                meta.push(escapeHtml(g.location_display));
              const metaHtml =
                meta.length > 0
                  ? "<p class=\"map-panel-game-card-meta\">" +
                    meta.join(" · ") +
                    "</p>"
                  : "";
              return (
                "<li><a href=\"" +
                escapeAttr(g.url) +
                "\"><div class=\"map-panel-game-card\"><div class=\"map-panel-game-card-logo\">" +
                logoHtml +
                "</div><div class=\"map-panel-game-card-body\"><h5 class=\"map-panel-game-card-title\">" +
                escapeHtml(g.name) +
                "</h5>" +
                metaHtml +
                "</div></div></a></li>"
              );
            })
            .join("");
        } else {
          panelCount.textContent = "";
          panelEmpty.style.display = "block";
        }
      })
      .catch(function () {
        panelLoading.style.display = "none";
        panelCount.textContent = "";
        panelEmpty.textContent = "Could not load games.";
        panelEmpty.style.display = "block";
      });
  }

  if (panelCloseBtn) panelCloseBtn.addEventListener("click", closePanel);
  if (panelBackdrop) panelBackdrop.addEventListener("click", closePanel);

  const qs = currentQueryString();
  fetch(mapDataUrl + (qs ? "?" + qs : ""))
    .then(function (res) {
      return res.json();
    })
    .then(function (json) {
      data = json;
      updateBubbles();
    })
    .catch(function () {
      console.error("Failed to load map data");
    });
})();
