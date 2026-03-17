// Shared typeahead/autocomplete for game search inputs.
// Attaches to any input with data-typeahead-url attribute.
// Usage: <input data-typeahead-url="/games/search/" ...>

(function () {
  "use strict";

  var DEBOUNCE_MS = 100;
  var MIN_CHARS = 3;

  function debounce(fn, ms) {
    var timer;
    return function () {
      var ctx = this;
      var args = arguments;
      clearTimeout(timer);
      timer = setTimeout(function () {
        fn.apply(ctx, args);
      }, ms);
    };
  }

  function escapeHtml(text) {
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function initTypeahead(input) {
    var url = input.getAttribute("data-typeahead-url");
    if (!url) return;
    if (input.dataset.typeaheadInitialized === "1") return;
    input.dataset.typeaheadInitialized = "1";

    // Wrap input in a positioned container for the dropdown
    var wrapper = document.createElement("div");
    wrapper.className = "typeahead-wrapper";
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    var dropdown = document.createElement("div");
    dropdown.className = "typeahead-dropdown";
    dropdown.setAttribute("role", "listbox");
    dropdown.style.display = "none";
    wrapper.appendChild(dropdown);

    var activeIndex = -1;
    var currentResults = [];
    var abortController = null;

    function close() {
      dropdown.style.display = "none";
      dropdown.innerHTML = "";
      activeIndex = -1;
      currentResults = [];
    }

    function setActive(index) {
      var items = dropdown.querySelectorAll(".typeahead-item");
      items.forEach(function (item) {
        item.classList.remove("typeahead-item--active");
        item.setAttribute("aria-selected", "false");
      });
      activeIndex = index;
      if (index >= 0 && index < items.length) {
        items[index].classList.add("typeahead-item--active");
        items[index].setAttribute("aria-selected", "true");
        items[index].scrollIntoView({ block: "nearest" });
      }
    }

    function renderResults(games) {
      currentResults = games;
      activeIndex = -1;
      if (games.length === 0) {
        dropdown.innerHTML =
          '<div class="typeahead-empty">No games found</div>';
        dropdown.style.display = "block";
        return;
      }
      dropdown.innerHTML = games
        .map(function (g, i) {
          var logoHtml = g.logo_url
            ? '<img class="typeahead-item-logo" src="' +
              escapeHtml(g.logo_url) +
              '" alt="">'
            : '<span class="typeahead-item-logo typeahead-item-logo--placeholder"></span>';
          return (
            '<a href="' +
            escapeHtml(g.url) +
            '" class="typeahead-item" role="option" aria-selected="false" data-index="' +
            i +
            '">' +
            '<div class="typeahead-item-inner">' +
            logoHtml +
            '<div class="typeahead-item-text">' +
            '<span class="typeahead-item-name">' +
            escapeHtml(g.name) +
            "</span>" +
            '<span class="typeahead-item-meta">' +
            escapeHtml(g.location) +
            " · " +
            escapeHtml(g.format) +
            "</span>" +
            "</div>" +
            "</div>" +
            "</a>"
          );
        })
        .join("");
      dropdown.style.display = "block";
    }

    var doSearch = debounce(function () {
      var query = input.value.trim();
      if (query.length < MIN_CHARS) {
        close();
        return;
      }
      if (abortController) abortController.abort();
      abortController = new AbortController();
      fetch(url + "?q=" + encodeURIComponent(query), {
        signal: abortController.signal,
      })
        .then(function (res) {
          if (!res.ok) throw new Error("HTTP " + res.status);
          return res.json();
        })
        .then(function (data) {
          renderResults(data.games || []);
        })
        .catch(function (err) {
          if (err.name !== "AbortError") close();
        });
    }, DEBOUNCE_MS);

    input.addEventListener("input", doSearch);

    input.addEventListener("keydown", function (e) {
      if (dropdown.style.display === "none") return;
      var items = dropdown.querySelectorAll(".typeahead-item");
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setActive(Math.min(activeIndex + 1, items.length - 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setActive(Math.max(activeIndex - 1, 0));
      } else if (e.key === "Enter" && activeIndex >= 0) {
        e.preventDefault();
        items[activeIndex].click();
      } else if (e.key === "Escape") {
        close();
      }
    });

    // Close on click outside
    document.addEventListener("click", function (e) {
      if (!wrapper.contains(e.target)) {
        close();
      }
    });

    // Close on focus leaving the wrapper
    input.addEventListener("blur", function () {
      // Delay so click on dropdown item registers first
      setTimeout(function () {
        if (!wrapper.contains(document.activeElement)) {
          close();
        }
      }, 150);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var inputs = document.querySelectorAll("[data-typeahead-url]");
    inputs.forEach(initTypeahead);
  });
})();
