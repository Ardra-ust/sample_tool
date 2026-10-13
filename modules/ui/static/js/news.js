/* News grid (SP-09, SP-10). Wiring: GET /api/news, POST /api/refresh, GET /api/refresh/status
 * (contract operations getNews, startRefresh, getRefreshStatus). No business logic runs here.
 * All feed text is inserted with textContent, never as HTML. */
(function () {
  "use strict";

  var DEALS = [
    { key: "mergers_acquisitions", label: "Mergers & Acquisitions", colour: "green" },
    { key: "partnerships", label: "Partnerships", colour: "blue" },
    { key: "joint_ventures", label: "Joint Ventures", colour: "violet" },
    { key: "strategic_investments", label: "Strategic Investments", colour: "yellow" },
    { key: "spin_offs_divestitures", label: "Spin-offs", colour: "amber" },
    { key: "alliances", label: "Alliances", colour: "red" }
  ];
  var DEAL_BY_KEY = {};
  DEALS.forEach(function (deal) { DEAL_BY_KEY[deal.key] = deal; });

  var REFRESHING_TEXT = "Refreshing news - this may take a while...";  // BRD §10
  var LOAD_ERROR_TEXT = "No news loaded, check your connection";        // owner copy (design brief)
  var POLL_INTERVAL_MS = 3000;  // implementation choice; the BRD gives no interval

  var state = { articles: [], domain: "All", deal: null, sort: "priority" };

  var el = {
    updated: document.getElementById("updated"),
    sort: document.getElementById("sort"),
    domain: document.getElementById("domain"),
    refresh: document.getElementById("refresh"),
    dealChips: document.getElementById("deal-chips"),
    clearDeal: document.getElementById("clear-deal"),
    notice: document.getElementById("notice"),
    loading: document.getElementById("loading"),
    grid: document.getElementById("grid"),
    empty: document.getElementById("empty")
  };

  function setNotice(text) {
    el.notice.textContent = text || "";
    el.notice.hidden = !text;
  }

  function setLoading(on) {
    el.loading.hidden = !on;
  }

  function sortArticles(list) {
    var copy = list.slice();
    if (state.sort === "date") {
      copy.sort(function (a, b) { return String(b.published).localeCompare(String(a.published)); });
    } else {
      copy.sort(function (a, b) {
        var byPriority = (Number(b.priority) || 0) - (Number(a.priority) || 0);  // BR-018
        return byPriority !== 0 ? byPriority : String(b.published).localeCompare(String(a.published));
      });
    }
    return copy;
  }

  function visibleArticles() {
    return sortArticles(state.articles.filter(function (article) {
      var domainOk = state.domain === "All" || article.domain === state.domain;
      var dealOk = !state.deal || (article.deal_categories || []).indexOf(state.deal) !== -1;
      return domainOk && dealOk;
    }));
  }

  function renderChips() {
    el.dealChips.textContent = "";
    DEALS.forEach(function (deal) {
      var count = state.articles.filter(function (a) {
        return (a.deal_categories || []).indexOf(deal.key) !== -1;
      }).length;
      var chip = document.createElement("button");
      chip.type = "button";
      chip.className = "chip " + deal.colour;
      chip.textContent = deal.label + " (" + count + ")";
      chip.setAttribute("aria-pressed", String(state.deal === deal.key));
      chip.addEventListener("click", function () {
        state.deal = state.deal === deal.key ? null : deal.key;
        render();
      });
      el.dealChips.appendChild(chip);
    });
  }

  function safeHref(link) {
    // Only http and https links are used as hrefs; anything else is shown as plain text.
    return typeof link === "string" && /^https?:\/\//i.test(link) ? link : null;
  }

  function buildCard(article) {
    var card = document.createElement("article");
    card.className = "card";

    var heading = document.createElement("h2");
    var href = safeHref(article.link);
    if (href) {
      var anchor = document.createElement("a");
      anchor.href = href;
      anchor.target = "_blank";
      anchor.rel = "noopener noreferrer";
      anchor.textContent = article.title || "";
      heading.appendChild(anchor);
    } else {
      heading.textContent = article.title || "";
    }
    card.appendChild(heading);

    var summary = document.createElement("p");
    summary.className = "summary clamped";
    summary.textContent = article.summary || "";
    card.appendChild(summary);

    var more = document.createElement("button");
    more.type = "button";
    more.className = "more";
    more.textContent = "See more...";
    more.hidden = true;
    more.addEventListener("click", function () {
      var expanded = summary.classList.toggle("clamped") === false;
      more.textContent = expanded ? "See less" : "See more...";
    });
    card.appendChild(more);

    var tags = document.createElement("div");
    tags.className = "tags";
    if (article.domain) {
      var domainTag = document.createElement("span");
      domainTag.className = "tag";
      domainTag.textContent = article.domain;
      tags.appendChild(domainTag);
    }
    (article.deal_categories || []).forEach(function (key) {
      var deal = DEAL_BY_KEY[key];
      if (!deal) { return; }
      var dealTag = document.createElement("span");
      dealTag.className = "tag deal " + deal.colour;
      dealTag.textContent = deal.label;
      tags.appendChild(dealTag);
    });
    card.appendChild(tags);

    var meta = document.createElement("div");
    meta.className = "meta";
    var source = document.createElement("span");
    source.textContent = article.source || "";
    var published = document.createElement("span");
    published.textContent = article.published || "";
    meta.appendChild(source);
    meta.appendChild(published);
    card.appendChild(meta);

    return { card: card, summary: summary, more: more };
  }

  function showSeeMoreWhereCut(entries) {
    // Show "See more..." only on summaries that are actually cut short.
    entries.forEach(function (entry) {
      entry.more.hidden = entry.summary.scrollHeight <= entry.summary.clientHeight + 1;
    });
  }

  function render() {
    renderChips();
    el.domain.value = state.domain;
    el.sort.value = state.sort;
    el.grid.textContent = "";
    var list = visibleArticles();
    el.empty.hidden = list.length > 0;
    var entries = list.map(function (article) {
      var entry = buildCard(article);
      el.grid.appendChild(entry.card);
      return entry;
    });
    requestAnimationFrame(function () { showSeeMoreWhereCut(entries); });
  }

  function setUpdated(fetchedAt) {
    if (fetchedAt) {
      el.updated.textContent = "Updated: " + fetchedAt;
      el.updated.hidden = false;
    } else {
      el.updated.textContent = "";
      el.updated.hidden = true;
    }
  }

  function loadNews() {
    setLoading(true);
    setNotice("");
    return fetch("/api/news", { cache: "no-store" })
      .then(function (response) {
        if (!response.ok) { throw new Error("HTTP " + response.status); }
        return response.json();
      })
      .then(function (body) {
        state.articles = Array.isArray(body.results) ? body.results : [];
        setUpdated(body.fetched_at);
        setLoading(false);
        el.grid.hidden = false;
        render();
      })
      .catch(function () {
        setLoading(false);
        el.grid.textContent = "";
        el.empty.hidden = true;
        setNotice(LOAD_ERROR_TEXT);
      });
  }

  function pollUntilFinished() {
    return fetch("/api/refresh/status", { cache: "no-store" })
      .then(function (response) {
        if (!response.ok) { throw new Error("HTTP " + response.status); }
        return response.json();
      })
      .then(function (status) {
        if (status.running) {
          setTimeout(pollUntilFinished, POLL_INTERVAL_MS);
          return;
        }
        window.location.reload();  // FR-030: reload when the refresh finishes
      })
      .catch(function () {
        el.refresh.disabled = false;
        setNotice(LOAD_ERROR_TEXT);
      });
  }

  function startRefresh() {
    el.refresh.disabled = true;
    setNotice(REFRESHING_TEXT);
    fetch("/api/refresh", { method: "POST", cache: "no-store" })
      .then(function (response) {
        if (!response.ok) { throw new Error("HTTP " + response.status); }
        return response.json();
      })
      .then(function () { return pollUntilFinished(); })
      .catch(function () {
        // The contract gives no error copy for a failed start (open item UD-06); re-enable the button.
        el.refresh.disabled = false;
        setNotice("");
      });
  }

  el.sort.addEventListener("change", function () { state.sort = el.sort.value; render(); });
  el.domain.addEventListener("change", function () { state.domain = el.domain.value; render(); });
  el.clearDeal.addEventListener("click", function () { state.deal = null; render(); });
  el.refresh.addEventListener("click", startRefresh);

  loadNews();
})();
