const state = {
  teams: [],
  lastResult: null,
  animationTimer: null,
  matches: [],
  selectedMatch: null,
  selectedMatchDetail: null,
  apiAnimationTimer: null,
  activePanel: "panelMatches",
  matchesMode: "today",
};

const els = {
  statusText: document.getElementById("statusText"),
  homeTeam: document.getElementById("homeTeam"),
  awayTeam: document.getElementById("awayTeam"),
  matchForm: document.getElementById("matchForm"),
  tournamentOptions: document.getElementById("tournamentOptions"),
  extraTime: document.getElementById("extraTime"),
  goldenGoal: document.getElementById("goldenGoal"),
  penaltiesAfter90: document.getElementById("penaltiesAfter90"),
  neutralVenue: document.getElementById("neutralVenue"),
  simulateBtn: document.getElementById("simulateBtn"),
  boardHome: document.getElementById("boardHome"),
  boardAway: document.getElementById("boardAway"),
  boardHomeBadge: document.getElementById("boardHomeBadge"),
  boardAwayBadge: document.getElementById("boardAwayBadge"),
  boardHomeScore: document.getElementById("boardHomeScore"),
  boardAwayScore: document.getElementById("boardAwayScore"),
  boardMinute: document.getElementById("boardMinute"),
  boardPhase: document.getElementById("boardPhase"),
  goalMarkers: document.getElementById("goalMarkers"),
  eventFeed: document.getElementById("eventFeed"),
  resultSummary: document.getElementById("resultSummary"),
  penaltyPanel: document.getElementById("penaltyPanel"),
  penaltyGrid: document.getElementById("penaltyGrid"),
  penaltyTotal: document.getElementById("penaltyTotal"),
  toast: document.getElementById("toast"),
  tabSimulate: document.getElementById("tabSimulate"),
  tabMatches: document.getElementById("tabMatches"),
  panelSimulate: document.getElementById("panelSimulate"),
  panelMatches: document.getElementById("panelMatches"),
  matchDate: document.getElementById("matchDate"),
  loadUpcomingBtn: document.getElementById("loadUpcomingBtn"),
  matchesSource: document.getElementById("matchesSource"),
  matchList: document.getElementById("matchList"),
  apiBoardHome: document.getElementById("apiBoardHome"),
  apiBoardAway: document.getElementById("apiBoardAway"),
  apiBoardHomeBadge: document.getElementById("apiBoardHomeBadge"),
  apiBoardAwayBadge: document.getElementById("apiBoardAwayBadge"),
  apiBoardHomeScore: document.getElementById("apiBoardHomeScore"),
  apiBoardAwayScore: document.getElementById("apiBoardAwayScore"),
  apiBoardMinute: document.getElementById("apiBoardMinute"),
  apiBoardPhase: document.getElementById("apiBoardPhase"),
  apiGoalMarkers: document.getElementById("apiGoalMarkers"),
  apiEventFeed: document.getElementById("apiEventFeed"),
  apiMatchDetail: document.getElementById("apiMatchDetail"),
  simulateFromApiBtn: document.getElementById("simulateFromApiBtn"),
};

const PHASE_LABELS = {
  regular: "Regulaminowy czas",
  extra_first: "Dogrywka I połowa",
  extra_second: "Dogrywka II połowa",
  penalties: "Rzuty karne",
};

const DECIDED_LABELS = {
  "90_minutes": "Po 90 minutach",
  extra_time: "Po dogrywce",
  golden_goal: "Złota bramka",
  penalties: "Rzuty karne",
};

const DISPLAY_EVENTS = new Set([
  "kickoff",
  "goal",
  "golden_goal",
  "full_time",
  "phase_start",
  "penalty_goal",
  "penalty_miss",
]);

const API_DISPLAY_EVENTS = new Set([
  "kickoff",
  "goal",
  "card",
  "substitution",
  "full_time",
]);

const MATCH_STATUS_LABELS = {
  NS: "Zaplanowany",
  "1H": "I połowa",
  "HT": "Przerwa",
  "2H": "II połowa",
  FT: "Koniec",
  ET: "Dogrywka",
  PEN: "Karne",
  LIVE: "Na żywo",
};

function showToast(message, isError = false) {
  els.toast.textContent = message;
  els.toast.className = `toast visible${isError ? " error" : ""}`;
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    els.toast.className = "toast";
  }, 3500);
}

function formatApiError(response, payload) {
  const detail = payload?.detail;
  if (typeof detail === "string") {
    if (response.status === 404 && (detail === "Not Found" || detail === "not found")) {
      return "Serwer nie odpowiada — sprawdź połączenie lub uruchom lokalnie: python -m uvicorn api:app --port 8010";
    }
    if (response.status === 404) {
      return detail.startsWith("Nie znaleziono") ? detail : `Nie znaleziono meczu (${detail})`;
    }
    if (response.status === 502) {
      return detail.startsWith("Błąd") ? detail : `Problem z TheSportsDB: ${detail}`;
    }
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || String(item)).join("; ");
  }
  const labels = {
    404: "Nie znaleziono meczu",
    502: "Nie udało się pobrać danych z TheSportsDB",
    500: "Błąd serwera — spróbuj ponownie",
    503: "Serwis tymczasowo niedostępny",
  };
  return labels[response.status] || `Błąd połączenia (${response.status})`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(formatApiError(response, payload));
  }
  return payload;
}

function getSelectedMode() {
  return document.querySelector('input[name="mode"]:checked')?.value || "friendly";
}

function updateModeUI() {
  els.tournamentOptions.hidden = getSelectedMode() !== "tournament";
}

function minuteToPercent(minute, phase, maxMinute = 120) {
  if (phase === "penalties") return 98;
  return Math.max(1, Math.min(100, (minute / maxMinute) * 100));
}

function markerClass(event) {
  if (event.event_type === "golden_goal") return "golden";
  if (event.phase === "extra_first" || event.phase === "extra_second") return "extra";
  return "regular";
}

function renderGoalMarkersOn(elMarkers, events, maxMinute = 120) {
  const goals = events.filter((e) => ["goal", "golden_goal"].includes(e.event_type));
  elMarkers.innerHTML = goals
    .map((event) => {
      const left = minuteToPercent(event.minute, event.phase, maxMinute);
      return `<span class="marker ${markerClass(event)}" style="left:${left}%" title="${event.minute}' ${event.team || ""}"></span>`;
    })
    .join("");
}

function eventRowClass(event) {
  const parts = [];
  if (event.event_type === "golden_goal") parts.push("golden");
  if (["goal", "golden_goal", "penalty_goal"].includes(event.event_type)) parts.push("highlight");
  if (event.event_type === "card") parts.push("penalty-row");
  if (event.phase === "penalties") parts.push("penalty-row");
  return parts.join(" ");
}

function renderEventFeedOn(elFeed, events, visibleCount = 0, displaySet = DISPLAY_EVENTS) {
  const filtered = events.filter((e) => displaySet.has(e.event_type));

  if (!filtered.length) {
    elFeed.innerHTML = '<p class="placeholder">Brak zdarzeń do wyświetlenia.</p>';
    return filtered;
  }

  elFeed.innerHTML = filtered
    .map((event, index) => {
      const visible = index < visibleCount ? "visible" : "";
      const minuteLabel = event.phase === "penalties" ? "K" : `${event.minute}'`;
      const score =
        event.home_score != null && event.away_score != null
          ? `${event.home_score}:${event.away_score}`
          : "—";
      return `
        <div class="event-row ${visible} ${eventRowClass(event)}" data-index="${index}">
          <span class="event-minute">${minuteLabel}</span>
          <span class="event-desc">${escapeHtml(event.description)}</span>
          <span class="event-score">${score}</span>
        </div>
      `;
    })
    .join("");

  if (visibleCount > 0) {
    const rows = elFeed.querySelectorAll(".event-row.visible");
    const last = rows[rows.length - 1];
    if (last) last.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  return filtered;
}

function renderGoalMarkers(events) {
  renderGoalMarkersOn(els.goalMarkers, events);
}

function renderEventFeed(events, visibleCount = 0) {
  renderEventFeedOn(els.eventFeed, events, visibleCount, DISPLAY_EVENTS);
}

function teamByName(name) {
  return state.teams.find((t) => t.name === name) || { name, badge: null };
}

function setScorebugBadge(imgEl, teamOrUrl) {
  const badge = typeof teamOrUrl === "string" ? teamOrUrl : teamOrUrl?.badge;
  const alt = typeof teamOrUrl === "string" ? "" : teamOrUrl?.name || "";
  if (badge) {
    imgEl.src = badge;
    imgEl.alt = alt;
    imgEl.hidden = false;
  } else {
    imgEl.removeAttribute("src");
    imgEl.alt = "";
    imgEl.hidden = true;
  }
}

function updateScoreboard(result, event = null) {
  const home = teamByName(result.home_team);
  const away = teamByName(result.away_team);
  els.boardHome.textContent = result.home_team;
  els.boardAway.textContent = result.away_team;
  setScorebugBadge(els.boardHomeBadge, home);
  setScorebugBadge(els.boardAwayBadge, away);

  if (event) {
    els.boardHomeScore.textContent = event.home_score;
    els.boardAwayScore.textContent = event.away_score;
    els.boardMinute.textContent = event.phase === "penalties" ? "KARNE" : `${event.minute}'`;
    els.boardPhase.textContent = PHASE_LABELS[event.phase] || event.phase;
  } else {
    els.boardHomeScore.textContent = result.home_score_final;
    els.boardAwayScore.textContent = result.away_score_final;
    els.boardMinute.textContent = "KONIEC";
    els.boardPhase.textContent = DECIDED_LABELS[result.decided_by] || result.decided_by;
  }
}

function renderResultSummary(result) {
  const decided = DECIDED_LABELS[result.decided_by] || result.decided_by;

  let winnerHtml = "";
  if (result.winner) {
    winnerHtml = `<p class="result-winner">Zwycięzca: ${escapeHtml(result.winner)}</p>`;
  } else if (result.is_draw) {
    winnerHtml = `<p class="result-winner">Remis (mecz towarzyski)</p>`;
  }

  const penAfter90 = result.home_score_penalties != null
    ? `<p>Karne: <strong>${result.home_score_penalties}:${result.away_score_penalties}</strong></p>`
    : "";

  els.resultSummary.className = "result-box";
  els.resultSummary.innerHTML = `
    <div class="result-final">${result.home_score_final} : ${result.away_score_final}</div>
    <div class="result-meta">
      <p>Po 90 min: ${result.home_score_90}:${result.away_score_90}</p>
      <p>Rozstrzygnięcie: <strong>${escapeHtml(decided)}</strong></p>
      <p>Bramki: ${escapeHtml(result.timeline_summary)}</p>
      ${penAfter90}
      ${winnerHtml}
    </div>
  `;

  if (result.penalty_shootout?.length) {
    els.penaltyPanel.hidden = false;
    els.penaltyGrid.innerHTML = result.penalty_shootout
      .map((kick) => `
        <tr class="${kick.scored ? "goal" : "miss"}">
          <td>${kick.kick_number}</td>
          <td>${escapeHtml(kick.team)}</td>
          <td>${kick.scored ? "GOL" : "PUDŁO"}</td>
        </tr>
      `)
      .join("");
    els.penaltyTotal.textContent =
      `Wynik karnych: ${result.home_score_penalties}:${result.away_score_penalties}`;
  } else {
    els.penaltyPanel.hidden = true;
    els.penaltyGrid.innerHTML = "";
    els.penaltyTotal.textContent = "";
  }
}

function stopAnimation() {
  if (state.animationTimer) {
    clearInterval(state.animationTimer);
    state.animationTimer = null;
  }
}

function stopApiAnimation() {
  if (state.apiAnimationTimer) {
    clearInterval(state.apiAnimationTimer);
    state.apiAnimationTimer = null;
  }
}

function playAnimationOn(config) {
  const {
    result,
    feedEl,
    markersEl,
    onUpdate,
    onComplete,
    displaySet = DISPLAY_EVENTS,
    maxMinute = 120,
    timerKey = "animationTimer",
  } = config;

  if (state[timerKey]) {
    clearInterval(state[timerKey]);
    state[timerKey] = null;
  }

  const filtered = renderEventFeedOn(feedEl, result.events, 0, displaySet);
  renderGoalMarkersOn(markersEl, [], maxMinute);
  if (filtered[0] && onUpdate) onUpdate(filtered[0]);

  const delay = filtered.length > 40 ? 280 : filtered.length > 15 ? 350 : 450;
  let step = 0;

  state[timerKey] = setInterval(() => {
    step += 1;
    const current = filtered[step - 1];
    if (current && onUpdate) onUpdate(current);
    renderEventFeedOn(feedEl, result.events, step, displaySet);

    const goalsSoFar = result.events
      .filter((e) => ["goal", "golden_goal"].includes(e.event_type))
      .filter((goal) => {
        const idx = filtered.findIndex(
          (e) =>
            e.minute === goal.minute &&
            e.team === goal.team &&
            e.event_type === goal.event_type,
        );
        return idx >= 0 && idx < step;
      });
    renderGoalMarkersOn(markersEl, goalsSoFar, maxMinute);

    if (step >= filtered.length) {
      clearInterval(state[timerKey]);
      state[timerKey] = null;
      if (onComplete) onComplete();
      renderGoalMarkersOn(markersEl, result.events, maxMinute);
    }
  }, delay);
}

function playAnimation(result) {
  playAnimationOn({
    result,
    feedEl: els.eventFeed,
    markersEl: els.goalMarkers,
    onUpdate: (event) => updateScoreboard(result, event),
    onComplete: () => updateScoreboard(result),
    displaySet: DISPLAY_EVENTS,
    timerKey: "animationTimer",
  });
}

function normalizeTeam(entry) {
  if (typeof entry === "string") {
    return { name: entry, badge: null, country: entry, rating: null };
  }
  return entry;
}

function populateTeamSelects(teams) {
  const normalized = teams.map(normalizeTeam);
  const options = normalized
    .map((team) => {
      const label = team.country && team.country !== team.name
        ? `${team.name} (${team.country})`
        : team.name;
      return `<option value="${escapeHtml(team.name)}">${escapeHtml(label)}</option>`;
    })
    .join("");

  els.homeTeam.innerHTML = options;
  els.awayTeam.innerHTML = options;

  const argIdx = normalized.findIndex((t) => t.name === "Argentina");
  const fraIdx = normalized.findIndex((t) => t.name === "France");
  if (argIdx >= 0) els.homeTeam.selectedIndex = argIdx;
  if (fraIdx >= 0) els.awayTeam.selectedIndex = fraIdx;
}

function setSelectValue(selectEl, value) {
  const options = Array.from(selectEl.options);
  const idx = options.findIndex((o) => o.value === value);
  if (idx >= 0) {
    selectEl.selectedIndex = idx;
    return true;
  }
  return false;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatDatePL(isoOrDateString) {
  if (!isoOrDateString) return "";
  const s = String(isoOrDateString).trim();
  const iso = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (iso) return `${iso[3]}.${iso[2]}.${iso[1]}`;
  return s;
}

function parseDatePL(plDate) {
  if (!plDate) return "";
  const s = String(plDate).trim();
  const m = s.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/);
  if (!m) return "";
  const day = Number(m[1]);
  const month = Number(m[2]);
  const year = Number(m[3]);
  if (month < 1 || month > 12 || day < 1 || day > 31) return "";
  const date = new Date(year, month - 1, day);
  if (date.getFullYear() !== year || date.getMonth() !== month - 1 || date.getDate() !== day) {
    return "";
  }
  return `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

function todayPL() {
  const d = new Date();
  return `${String(d.getDate()).padStart(2, "0")}.${String(d.getMonth() + 1).padStart(2, "0")}.${d.getFullYear()}`;
}

function formatDateInputMask(raw) {
  const digits = String(raw).replace(/\D/g, "").slice(0, 8);
  if (digits.length <= 2) return digits;
  if (digits.length <= 4) return `${digits.slice(0, 2)}.${digits.slice(2)}`;
  return `${digits.slice(0, 2)}.${digits.slice(2, 4)}.${digits.slice(4)}`;
}

function getMatchDateISO() {
  return parseDatePL(els.matchDate.value);
}

function applyMatchDateChange() {
  const iso = getMatchDateISO();
  if (!iso) {
    els.matchDate.classList.add("invalid");
    if (els.matchDate.value.trim()) {
      showToast("Nieprawidłowa data. Użyj formatu DD.MM.RRRR", true);
    }
    return;
  }
  els.matchDate.classList.remove("invalid");
  els.loadUpcomingBtn.classList.remove("active");
  loadMatchesForDate(iso);
}

function formatMatchTime(timeStr) {
  if (!timeStr) return "—";
  const parts = timeStr.split(":");
  if (parts.length >= 2) return `${parts[0]}:${parts[1]}`;
  return timeStr;
}

function formatScore(match) {
  if (match.home_score != null && match.away_score != null) {
    return `${match.home_score}:${match.away_score}`;
  }
  return "vs";
}

function statusLabel(status, isLive) {
  if (isLive) return `<span class="match-status-live">${MATCH_STATUS_LABELS[status] || status || "LIVE"}</span>`;
  if (status === "FT") return `<span class="match-status-ft">Koniec</span>`;
  return MATCH_STATUS_LABELS[status] || status || "Zaplanowany";
}

function renderMatchList(matches) {
  if (!matches.length) {
    els.matchList.innerHTML = '<li class="placeholder">Brak meczów dla wybranych kryteriów.</li>';
    return;
  }

  els.matchList.innerHTML = matches
    .map((match) => {
      const selected = state.selectedMatch?.id === match.id ? "selected" : "";
      const homeBadge = match.home_badge
        ? `<img class="match-item-badge" src="${escapeHtml(match.home_badge)}" alt="" />`
        : "";
      const awayBadge = match.away_badge
        ? `<img class="match-item-badge" src="${escapeHtml(match.away_badge)}" alt="" />`
        : "";
      const score =
        match.home_score != null
          ? `<span class="match-item-score">${match.home_score}:${match.away_score}</span>`
          : "";
      const meta = match.is_live
        ? statusLabel(match.status, true)
        : (match.league ? escapeHtml(match.league) : statusLabel(match.status, false));
      const timeDisplay =
        state.matchesMode === "upcoming" && match.date
          ? `${formatDatePL(match.date)} ${formatMatchTime(match.time)}`
          : formatMatchTime(match.time);
      return `
        <li class="match-item ${selected}" data-id="${escapeHtml(match.id)}" role="button" tabindex="0">
          <span class="match-item-time">${timeDisplay}</span>
          <div class="match-item-teams">
            ${homeBadge}${escapeHtml(match.home_team)}
            <span>–</span>
            ${awayBadge}${escapeHtml(match.away_team)}
            ${score}
          </div>
          <div class="match-item-meta">${meta}</div>
        </li>
      `;
    })
    .join("");
}

function updateApiScoreboard(match, event = null) {
  els.apiBoardHome.textContent = match.home_team;
  els.apiBoardAway.textContent = match.away_team;
  setScorebugBadge(els.apiBoardHomeBadge, match.home_badge);
  setScorebugBadge(els.apiBoardAwayBadge, match.away_badge);

  if (event) {
    els.apiBoardHomeScore.textContent = event.home_score ?? "0";
    els.apiBoardAwayScore.textContent = event.away_score ?? "0";
    els.apiBoardMinute.textContent = `${event.minute}'`;
    els.apiBoardPhase.textContent = event.event_type === "goal" ? "Bramka" : "Przebieg";
  } else if (match.home_score != null) {
    els.apiBoardHomeScore.textContent = match.home_score;
    els.apiBoardAwayScore.textContent = match.away_score;
    els.apiBoardMinute.textContent = match.is_finished ? "KONIEC" : (MATCH_STATUS_LABELS[match.status] || match.status);
    els.apiBoardPhase.textContent = match.league || "";
  } else {
    els.apiBoardHomeScore.textContent = "—";
    els.apiBoardAwayScore.textContent = "—";
    els.apiBoardMinute.textContent = formatMatchTime(match.time);
    els.apiBoardPhase.textContent = formatDatePL(match.date);
  }
}

function renderApiTimelinePlaceholder(match, timelinePayload, simulationTeams) {
  const canSim = simulationTeams?.can_simulate;
  const simHint = canSim
    ? "Użyj przycisku <strong>Symuluj</strong> poniżej, aby wygenerować przebieg."
    : "Te drużyny nie są dostępne w symulatorze.";

  if (match.is_upcoming || timelinePayload?.is_upcoming) {
    const when = [formatDatePL(match.date), formatMatchTime(match.time)].filter(Boolean).join(" · ");
    els.apiEventFeed.innerHTML = `
      <div class="timeline-placeholder upcoming">
        <p><strong>Mecz jeszcze się nie rozpoczął.</strong></p>
        <p>${when ? `Zaplanowany: ${escapeHtml(when)}.` : "Status: zaplanowany."}</p>
        <p>TheSportsDB nie udostępnia przebiegu przed rozpoczęciem meczu.</p>
        <p>${simHint}</p>
      </div>
    `;
    els.apiGoalMarkers.innerHTML = "";
    els.simulateFromApiBtn.hidden = false;
    els.simulateFromApiBtn.disabled = !canSim;
    return;
  }

  const score = formatScore(match);
  if (match.is_finished || timelinePayload?.is_finished) {
    els.apiEventFeed.innerHTML = `
      <div class="timeline-placeholder finished-empty">
        <p><strong>Mecz zakończony (${escapeHtml(score)}).</strong></p>
        <p>TheSportsDB nie zwróciło szczegółowego przebiegu dla tego spotkania.</p>
        <p>${simHint}</p>
      </div>
    `;
  } else if (match.is_live || timelinePayload?.is_live) {
    els.apiEventFeed.innerHTML = `
      <div class="timeline-placeholder live-empty">
        <p><strong>Mecz trwa (${escapeHtml(score)}).</strong></p>
        <p>Brak zdarzeń w timeline — API może opóźniać aktualizację lub nie obejmuje tej ligi.</p>
      </div>
    `;
  } else {
    els.apiEventFeed.innerHTML = `
      <div class="timeline-placeholder">
        <p>Brak przebiegu dla tego meczu w TheSportsDB.</p>
        <p>${simHint}</p>
      </div>
    `;
  }
  els.apiGoalMarkers.innerHTML = "";
}

function playApiTimelineAnimation(match, events, timelineSource) {
  const pseudoResult = {
    home_team: match.home_team,
    away_team: match.away_team,
    events,
  };
  playAnimationOn({
    result: pseudoResult,
    feedEl: els.apiEventFeed,
    markersEl: els.apiGoalMarkers,
    onUpdate: (event) => updateApiScoreboard(match, event),
    onComplete: () => updateApiScoreboard(match),
    displaySet: API_DISPLAY_EVENTS,
    maxMinute: 90,
    timerKey: "apiAnimationTimer",
  });
  if (timelineSource === "score_fallback") {
    showToast("Przebieg odtworzony z wyniku końcowego — brak szczegółów w API.");
  }
}

function renderApiMatchDetail(match, simulationTeams) {
  const canSim = simulationTeams?.can_simulate;
  const status = match.is_live
    ? "Na żywo"
    : match.is_finished
      ? "Koniec"
      : `${escapeHtml(formatDatePL(match.date))} · ${formatMatchTime(match.time)}`;
  const league = match.league ? `<span class="api-detail-league">${escapeHtml(match.league)}</span>` : "";

  els.apiMatchDetail.className = "api-detail-bar filled";
  els.apiMatchDetail.innerHTML = `
    <span class="api-detail-teams">${escapeHtml(match.home_team)} <span class="api-detail-vs">vs</span> ${escapeHtml(match.away_team)}</span>
    <span class="api-detail-score">${formatScore(match)}</span>
    <span class="api-detail-status">${status}</span>
    ${league}
  `;

  const showSimBtn = match.is_upcoming || (!match.is_finished && !match.is_live);
  els.simulateFromApiBtn.hidden = !showSimBtn;
  els.simulateFromApiBtn.disabled = !canSim;
  els.simulateFromApiBtn.title = canSim ? "" : "Drużyny niedostępne w symulatorze";
}

function formatMatchesSource(count, label) {
  if (!count) return `Brak meczów (${label})`;
  const word = count === 1 ? "mecz" : count < 5 ? "mecze" : "meczów";
  return `${count} ${word} · ${label}`;
}

async function loadMatchesForDate(dateStr) {
  state.matchesMode = "today";
  els.loadUpcomingBtn.classList.remove("active");
  els.matchesSource.textContent = "Ładowanie…";
  try {
    const query = dateStr ? `?date=${encodeURIComponent(dateStr)}` : "";
    const payload = await api(`/matches${query}`);
    state.matches = payload.matches || [];
    const dateLabel = payload.date ? formatDatePL(payload.date) : "dziś";
    els.matchesSource.textContent = formatMatchesSource(payload.count, dateLabel);
    renderMatchList(state.matches);
  } catch (error) {
    els.matchesSource.textContent = "Błąd ładowania";
    renderMatchList([]);
    showToast(error.message, true);
  }
}

async function loadUpcomingMatches() {
  state.matchesMode = "upcoming";
  els.loadUpcomingBtn.classList.add("active");
  els.matchesSource.textContent = "Ładowanie…";
  try {
    const payload = await api("/matches/upcoming");
    state.matches = payload.matches || [];
    els.matchesSource.textContent = formatMatchesSource(payload.count, "nadchodzące");
    renderMatchList(state.matches);
  } catch (error) {
    els.matchesSource.textContent = "Błąd ładowania";
    renderMatchList([]);
    showToast(error.message, true);
  }
}

async function selectMatch(eventId) {
  stopApiAnimation();
  try {
    const detailPayload = await api(`/matches/${encodeURIComponent(eventId)}`);
    const match = detailPayload.match;
    state.selectedMatch = state.matches.find((m) => m.id === eventId) || match;
    state.selectedMatchDetail = detailPayload;
    renderMatchList(state.matches);
    renderApiMatchDetail(match, detailPayload.simulation_teams);
    updateApiScoreboard(match);

    if (match.is_finished || match.is_live) {
      const timelinePayload = await api(`/matches/${encodeURIComponent(eventId)}/timeline`);
      const events = timelinePayload.events || [];
      if (events.length) {
        playApiTimelineAnimation(match, events, timelinePayload.timeline_source);
      } else {
        renderApiTimelinePlaceholder(match, timelinePayload, detailPayload.simulation_teams);
      }
    } else {
      renderApiTimelinePlaceholder(match, { is_upcoming: true }, detailPayload.simulation_teams);
    }
  } catch (error) {
    showToast(error.message, true);
  }
}

async function simulateFromApiMatch() {
  const detail = state.selectedMatchDetail;
  if (!detail?.simulation_teams?.can_simulate) {
    showToast("Te drużyny nie są dostępne w symulatorze", true);
    return;
  }

  const { home, away } = detail.simulation_teams;
  const match = state.selectedMatch;

  stopApiAnimation();
  els.simulateFromApiBtn.disabled = true;
  els.simulateFromApiBtn.textContent = "Symuluję…";

  try {
    const payload = await api("/simulate-match", {
      method: "POST",
      body: JSON.stringify({
        home_team: home,
        away_team: away,
        mode: "friendly",
        neutral_venue: true,
        extra_time: true,
        golden_goal: false,
        penalties_after_90: false,
        seed: Math.floor(Math.random() * 100000),
      }),
    });

    const simMatch = {
      ...match,
      home_team: payload.home_team,
      away_team: payload.away_team,
      home_score: payload.home_score_final,
      away_score: payload.away_score_final,
      is_finished: true,
      is_live: false,
    };
    renderApiMatchDetail(simMatch, detail.simulation_teams);
    els.apiMatchDetail.querySelector(".api-detail-score").textContent =
      `${payload.home_score_final}:${payload.away_score_final}`;

    playAnimationOn({
      result: payload,
      feedEl: els.apiEventFeed,
      markersEl: els.apiGoalMarkers,
      onUpdate: (event) => updateApiScoreboard(simMatch, event),
      onComplete: () => updateApiScoreboard(simMatch),
      displaySet: DISPLAY_EVENTS,
      maxMinute: 120,
      timerKey: "apiAnimationTimer",
    });
  } catch (error) {
    showToast(error.message, true);
  } finally {
    els.simulateFromApiBtn.disabled = !detail.simulation_teams.can_simulate;
    els.simulateFromApiBtn.textContent = "Symuluj";
  }
}

function switchPanel(panelId) {
  state.activePanel = panelId;
  const isSim = panelId === "panelSimulate";
  els.panelSimulate.classList.toggle("hidden", !isSim);
  els.panelSimulate.hidden = !isSim;
  els.panelMatches.classList.toggle("hidden", isSim);
  els.panelMatches.hidden = isSim;
  els.tabSimulate.classList.toggle("active", isSim);
  els.tabMatches.classList.toggle("active", !isSim);
  els.tabSimulate.setAttribute("aria-selected", String(isSim));
  els.tabMatches.setAttribute("aria-selected", String(!isSim));
}

document.querySelectorAll('input[name="mode"]').forEach((input) => {
  input.addEventListener("change", updateModeUI);
});

els.penaltiesAfter90.addEventListener("change", () => {
  if (els.penaltiesAfter90.checked) {
    els.extraTime.checked = false;
    els.goldenGoal.checked = false;
  }
});

els.extraTime.addEventListener("change", () => {
  if (els.extraTime.checked) els.penaltiesAfter90.checked = false;
});

els.matchForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (els.homeTeam.value === els.awayTeam.value) {
    showToast("Wybierz dwie różne drużyny", true);
    return;
  }

  stopAnimation();
  els.simulateBtn.disabled = true;
  els.simulateBtn.textContent = "Symuluję…";

  try {
    const mode = getSelectedMode();
    const payload = await api("/simulate-match", {
      method: "POST",
      body: JSON.stringify({
        home_team: els.homeTeam.value,
        away_team: els.awayTeam.value,
        mode,
        neutral_venue: els.neutralVenue.checked,
        extra_time: els.extraTime.checked,
        golden_goal: els.goldenGoal.checked,
        penalties_after_90: els.penaltiesAfter90.checked,
        seed: Math.floor(Math.random() * 100000),
      }),
    });

    state.lastResult = payload;
    renderResultSummary(payload);
    playAnimation(payload);
  } catch (error) {
    showToast(error.message, true);
  } finally {
    els.simulateBtn.disabled = false;
    els.simulateBtn.textContent = "Symuluj mecz";
  }
});

document.querySelectorAll(".main-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    switchPanel(tab.dataset.panel);
    if (tab.dataset.panel === "panelMatches" && !state.matches.length) {
      const iso = getMatchDateISO();
      if (iso) loadMatchesForDate(iso);
    }
  });
});

els.matchDate.addEventListener("input", () => {
  const el = els.matchDate;
  const pos = el.selectionStart;
  const prevLen = el.value.length;
  el.value = formatDateInputMask(el.value);
  const diff = el.value.length - prevLen;
  el.setSelectionRange(Math.max(0, pos + diff), Math.max(0, pos + diff));
  el.classList.remove("invalid");
});

els.matchDate.addEventListener("change", applyMatchDateChange);

els.matchDate.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    els.matchDate.blur();
  }
});

els.loadUpcomingBtn.addEventListener("click", loadUpcomingMatches);
els.simulateFromApiBtn.addEventListener("click", simulateFromApiMatch);

els.matchList.addEventListener("click", (event) => {
  const item = event.target.closest(".match-item");
  if (!item?.dataset.id) return;
  selectMatch(item.dataset.id);
});

els.matchList.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" && event.key !== " ") return;
  const item = event.target.closest(".match-item");
  if (!item?.dataset.id) return;
  event.preventDefault();
  selectMatch(item.dataset.id);
});

async function init() {
  els.matchDate.value = todayPL();

  try {
    const payload = await api("/teams");
    state.teams = (payload.teams || []).map(normalizeTeam);
    populateTeamSelects(state.teams);
    const source = payload.source === "cache" ? "cache" : payload.source || "API";
    els.statusText.textContent = `${state.teams.length} drużyn (${source})`;
  } catch (error) {
    els.statusText.textContent = "Błąd połączenia";
    showToast(error.message, true);
  }
  updateModeUI();
  switchPanel("panelMatches");
  await loadMatchesForDate(getMatchDateISO());
}

init();
