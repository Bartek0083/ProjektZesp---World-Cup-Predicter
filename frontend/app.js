const state = {
  teams: [],
  defaultMatches: [],
  latestGroupSummary: null,
};

const TEAM_FLAG_CODES = {
  Afghanistan: "AF",
  Albania: "AL",
  Algeria: "DZ",
  "American Samoa": "AS",
  Andorra: "AD",
  Angola: "AO",
  Anguilla: "AI",
  "Antigua and Barbuda": "AG",
  Argentina: "AR",
  Armenia: "AM",
  Aruba: "AW",
  Australia: "AU",
  Austria: "AT",
  Azerbaijan: "AZ",
  Bahamas: "BS",
  Bahrain: "BH",
  Bangladesh: "BD",
  Barbados: "BB",
  Belarus: "BY",
  Belgium: "BE",
  Belize: "BZ",
  Benin: "BJ",
  Bermuda: "BM",
  Bhutan: "BT",
  Bolivia: "BO",
  "Bosnia and Herzegovina": "BA",
  Botswana: "BW",
  Brazil: "BR",
  "British Virgin Islands": "VG",
  Brunei: "BN",
  Bulgaria: "BG",
  "Burkina Faso": "BF",
  Burundi: "BI",
  Cambodia: "KH",
  Cameroon: "CM",
  Canada: "CA",
  "Cape Verde": "CV",
  "Cayman Islands": "KY",
  "Central African Republic": "CF",
  Chad: "TD",
  Chile: "CL",
  "China PR": "CN",
  Colombia: "CO",
  Comoros: "KM",
  Congo: "CG",
  "Cook Islands": "CK",
  "Costa Rica": "CR",
  Croatia: "HR",
  Cuba: "CU",
  Curaçao: "CW",
  Cyprus: "CY",
  "Czech Republic": "CZ",
  "DR Congo": "CD",
  Denmark: "DK",
  Djibouti: "DJ",
  Dominica: "DM",
  "Dominican Republic": "DO",
  Ecuador: "EC",
  Egypt: "EG",
  "El Salvador": "SV",
  "Equatorial Guinea": "GQ",
  Eritrea: "ER",
  Estonia: "EE",
  Eswatini: "SZ",
  Ethiopia: "ET",
  "Faroe Islands": "FO",
  Fiji: "FJ",
  Finland: "FI",
  France: "FR",
  Gabon: "GA",
  Gambia: "GM",
  Georgia: "GE",
  Germany: "DE",
  Ghana: "GH",
  Gibraltar: "GI",
  Greece: "GR",
  Grenada: "GD",
  Guam: "GU",
  Guatemala: "GT",
  Guinea: "GN",
  "Guinea-Bissau": "GW",
  Guyana: "GY",
  Haiti: "HT",
  Honduras: "HN",
  "Hong Kong": "HK",
  Hungary: "HU",
  Iceland: "IS",
  India: "IN",
  Indonesia: "ID",
  Iran: "IR",
  Iraq: "IQ",
  Israel: "IL",
  Italy: "IT",
  "Ivory Coast": "CI",
  Jamaica: "JM",
  Japan: "JP",
  Jordan: "JO",
  Kazakhstan: "KZ",
  Kenya: "KE",
  Kosovo: "XK",
  Kuwait: "KW",
  Laos: "LA",
  Latvia: "LV",
  Lebanon: "LB",
  Lesotho: "LS",
  Liberia: "LR",
  Libya: "LY",
  Liechtenstein: "LI",
  Lithuania: "LT",
  Luxembourg: "LU",
  Macau: "MO",
  Madagascar: "MG",
  Malawi: "MW",
  Malaysia: "MY",
  Maldives: "MV",
  Mali: "ML",
  Malta: "MT",
  Mauritania: "MR",
  Mauritius: "MU",
  Mexico: "MX",
  Moldova: "MD",
  Mongolia: "MN",
  Montenegro: "ME",
  Montserrat: "MS",
  Morocco: "MA",
  Mozambique: "MZ",
  Myanmar: "MM",
  Namibia: "NA",
  Nepal: "NP",
  Netherlands: "NL",
  "New Caledonia": "NC",
  "New Zealand": "NZ",
  Nicaragua: "NI",
  Niger: "NE",
  Nigeria: "NG",
  "North Korea": "KP",
  "North Macedonia": "MK",
  Norway: "NO",
  Oman: "OM",
  Pakistan: "PK",
  Palestine: "PS",
  Panama: "PA",
  "Papua New Guinea": "PG",
  Paraguay: "PY",
  Peru: "PE",
  Philippines: "PH",
  Poland: "PL",
  Portugal: "PT",
  "Puerto Rico": "PR",
  Qatar: "QA",
  "Republic of Ireland": "IE",
  Romania: "RO",
  Russia: "RU",
  Rwanda: "RW",
  "Saint Kitts and Nevis": "KN",
  "Saint Lucia": "LC",
  "Saint Vincent and the Grenadines": "VC",
  Samoa: "WS",
  "San Marino": "SM",
  "Saudi Arabia": "SA",
  Senegal: "SN",
  Serbia: "RS",
  Seychelles: "SC",
  "Sierra Leone": "SL",
  Singapore: "SG",
  Slovakia: "SK",
  Slovenia: "SI",
  "Solomon Islands": "SB",
  Somalia: "SO",
  "South Africa": "ZA",
  "South Korea": "KR",
  "South Sudan": "SS",
  Spain: "ES",
  "Sri Lanka": "LK",
  Sudan: "SD",
  Suriname: "SR",
  Sweden: "SE",
  Switzerland: "CH",
  Syria: "SY",
  "São Tomé and Príncipe": "ST",
  Tahiti: "PF",
  Taiwan: "TW",
  Tajikistan: "TJ",
  Tanzania: "TZ",
  Thailand: "TH",
  "Timor-Leste": "TL",
  Togo: "TG",
  Tonga: "TO",
  "Trinidad and Tobago": "TT",
  Tunisia: "TN",
  Turkey: "TR",
  Turkmenistan: "TM",
  "Turks and Caicos Islands": "TC",
  Uganda: "UG",
  Ukraine: "UA",
  "United Arab Emirates": "AE",
  "United States": "US",
  "United States Virgin Islands": "VI",
  Uruguay: "UY",
  Uzbekistan: "UZ",
  Vanuatu: "VU",
  Venezuela: "VE",
  Vietnam: "VN",
  Yemen: "YE",
  Zambia: "ZM",
  Zimbabwe: "ZW",
};

const BRACKET_SIDES = {
  left: [
    { label: "1/16 finalu", ids: ["R32_03", "R32_06", "R32_01", "R32_04", "R32_12", "R32_11", "R32_10", "R32_09"], depth: 0 },
    { label: "1/8 finalu", ids: ["R16_01", "R16_02", "R16_05", "R16_06"], depth: 1 },
    { label: "Cwiercfinaly", ids: ["QF_01", "QF_02"], depth: 2 },
    { label: "Polfinal", ids: ["SF_01"], depth: 3 },
  ],
  right: [
    { label: "Polfinal", ids: ["SF_02"], depth: 3 },
    { label: "Cwiercfinaly", ids: ["QF_03", "QF_04"], depth: 2 },
    { label: "1/8 finalu", ids: ["R16_03", "R16_04", "R16_07", "R16_08"], depth: 1 },
    { label: "1/16 finalu", ids: ["R32_02", "R32_05", "R32_07", "R32_08", "R32_15", "R32_14", "R32_13", "R32_16"], depth: 0 },
  ],
};

const SPECIAL_FLAG_CLASSES = {
  England: "flag-england",
  "Northern Ireland": "flag-northern-ireland",
  Scotland: "flag-scotland",
  Wales: "flag-wales",
};

const els = {
  statusText: document.getElementById("statusText"),
  toast: document.getElementById("toast"),
  teamsList: document.getElementById("teamsList"),
  tabs: [...document.querySelectorAll(".tab-button")],
  views: [...document.querySelectorAll(".view")],
  matchForm: document.getElementById("matchForm"),
  homeTeam: document.getElementById("homeTeam"),
  awayTeam: document.getElementById("awayTeam"),
  matchTournament: document.getElementById("matchTournament"),
  neutralMatch: document.getElementById("neutralMatch"),
  matchResult: document.getElementById("matchResult"),
  loadDefaultGroups: document.getElementById("loadDefaultGroups"),
  addMatchRow: document.getElementById("addMatchRow"),
  groupTables: document.getElementById("groupTables"),
  groupMatchesBody: document.getElementById("groupMatchesBody"),
  groupSimulationForm: document.getElementById("groupSimulationForm"),
  groupSimulationCount: document.getElementById("groupSimulationCount"),
  groupSeed: document.getElementById("groupSeed"),
  groupSummary: document.getElementById("groupSummary"),
  worldCupForm: document.getElementById("worldCupForm"),
  worldCupSimulationCount: document.getElementById("worldCupSimulationCount"),
  worldCupSeed: document.getElementById("worldCupSeed"),
  useEditedGroups: document.getElementById("useEditedGroups"),
  worldCupSummary: document.getElementById("worldCupSummary"),
  bracketTree: document.getElementById("bracketTree"),
};

function showToast(message, type = "info") {
  els.toast.textContent = message;
  els.toast.className = `toast visible ${type === "error" ? "error" : ""}`;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    els.toast.className = "toast";
  }, 3400);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  let payload = null;
  try {
    payload = await response.json();
  } catch (_error) {
    payload = null;
  }

  if (!response.ok) {
    const detail = payload?.detail || `HTTP ${response.status}`;
    throw new Error(Array.isArray(detail) ? detail.map((item) => item.msg).join(", ") : detail);
  }

  return payload;
}

function setLoading(button, isLoading, labelWhenLoading = "Pracuje") {
  if (!button) return;
  if (isLoading) {
    button.dataset.originalText = button.textContent;
    button.textContent = labelWhenLoading;
    button.disabled = true;
  } else {
    button.textContent = button.dataset.originalText || button.textContent;
    button.disabled = false;
  }
}

function percent(value) {
  return `${Number(value || 0).toFixed(2)}%`;
}

function flagBadge(team) {
  const specialClass = SPECIAL_FLAG_CLASSES[team];
  if (specialClass) {
    return `<span class="flag-badge css-flag ${specialClass}" aria-hidden="true"></span>`;
  }
  const code = TEAM_FLAG_CODES[team];
  if (!code) {
    return `<span class="flag-badge flag-fallback" aria-hidden="true">??</span>`;
  }

  const lowerCode = escapeAttr(code.toLowerCase());
  const upperCode = escapeAttr(code.toUpperCase());
  return `
    <span class="flag-badge flag-image-badge" aria-hidden="true">
      <img
        src="https://flagcdn.com/w40/${lowerCode}.png"
        srcset="https://flagcdn.com/w80/${lowerCode}.png 2x"
        alt=""
        loading="lazy"
        onerror="this.parentElement.classList.add('flag-fallback'); this.parentElement.textContent='${upperCode}'"
      />
    </span>
  `;
}

function teamInline(team) {
  return `
    <span class="team-inline">
      ${flagBadge(team)}
      <span class="team-name">${escapeHtml(team)}</span>
    </span>
  `;
}

function renderProbabilityResult(result) {
  const rows = [
    [teamInline(result.home_team), result.home_win * 100, "home"],
    ["Remis", result.draw * 100, "draw"],
    [teamInline(result.away_team), result.away_win * 100, "away"],
  ];

  els.matchResult.className = "probability-stack";
  els.matchResult.innerHTML = `
    <div class="match-title">${teamInline(result.home_team)} <span class="versus">vs</span> ${teamInline(result.away_team)}</div>
    ${rows
      .map(
        ([label, value, type]) => `
          <div class="prob-row">
            <div class="prob-label">${label}</div>
            <div class="meter" aria-hidden="true">
              <div class="meter-fill ${type}" style="width:${Math.max(0, Math.min(100, value))}%"></div>
            </div>
            <div class="prob-value">${percent(value)}</div>
          </div>
        `,
      )
      .join("")}
  `;
}

function renderTeamsList(teams) {
  els.teamsList.innerHTML = teams.map((team) => `<option value="${escapeHtml(team)}"></option>`).join("");
}

function renderGroupRows(matches) {
  els.groupMatchesBody.innerHTML = "";
  matches.forEach((match) => appendGroupRow(match));
  state.latestGroupSummary = null;
  renderGroupTables();
}

function appendGroupRow(match = { group: "A", home_team: "", away_team: "" }) {
  const row = document.createElement("tr");
  row.innerHTML = `
    <td><input class="group-input" value="${escapeAttr(match.group || "")}" /></td>
    <td><input class="home-input" list="teamsList" value="${escapeAttr(match.home_team || "")}" /></td>
    <td><input class="away-input" list="teamsList" value="${escapeAttr(match.away_team || "")}" /></td>
    <td><button class="icon-action" type="button" title="Usun mecz" aria-label="Usun mecz">x</button></td>
  `;
  row.querySelector("button").addEventListener("click", () => {
    row.remove();
    state.latestGroupSummary = null;
    renderGroupTables();
  });
  els.groupMatchesBody.appendChild(row);
  state.latestGroupSummary = null;
  renderGroupTables();
}

function collectGroupMatches() {
  return [...els.groupMatchesBody.querySelectorAll("tr")]
    .map((row) => ({
      group: row.querySelector(".group-input").value.trim(),
      home_team: row.querySelector(".home-input").value.trim(),
      away_team: row.querySelector(".away-input").value.trim(),
    }))
    .filter((match) => match.group && match.home_team && match.away_team);
}

function optionalNumber(input) {
  const value = input.value.trim();
  return value ? Number(value) : null;
}

function buildGroupTableRowsFromMatches(matches) {
  const groups = new Map();
  matches.forEach((match) => {
    if (!groups.has(match.group)) {
      groups.set(match.group, []);
    }
    const rows = groups.get(match.group);
    [match.home_team, match.away_team].forEach((team) => {
      if (team && !rows.some((row) => row.team === team)) {
        rows.push({ group: match.group, team });
      }
    });
  });
  return groups;
}

function buildGroupTableRowsFromSummary(summaryRows) {
  const groups = new Map();
  [...summaryRows]
    .sort((a, b) => {
      const groupCompare = String(a.group).localeCompare(String(b.group), "pl", { numeric: true });
      if (groupCompare !== 0) return groupCompare;
      return (
        Number(b["qualified_%"] || 0) - Number(a["qualified_%"] || 0) ||
        Number(b["group_winner_%"] || 0) - Number(a["group_winner_%"] || 0) ||
        Number(b.avg_points || 0) - Number(a.avg_points || 0)
      );
    })
    .forEach((row) => {
      if (!groups.has(row.group)) {
        groups.set(row.group, []);
      }
      groups.get(row.group).push(row);
    });
  return groups;
}

function renderGroupTables(summaryRows = state.latestGroupSummary) {
  const groups = summaryRows
    ? buildGroupTableRowsFromSummary(summaryRows)
    : buildGroupTableRowsFromMatches(collectGroupMatches());

  if (groups.size === 0) {
    els.groupTables.className = "empty-state";
    els.groupTables.textContent = "Brak druzyn w grupach.";
    return;
  }

  els.groupTables.className = "group-tables-grid";
  els.groupTables.innerHTML = [...groups.entries()]
    .sort(([groupA], [groupB]) => String(groupA).localeCompare(String(groupB), "pl", { numeric: true }))
    .map(([group, rows]) => {
      const hasSummary = rows.some((row) => row["qualified_%"] !== undefined);
      return `
        <article class="group-table-card">
          <div class="group-table-title">
            <span>Tabela</span>
            <strong>Grupa ${escapeHtml(group)}</strong>
          </div>
          <table class="group-table">
            <thead>
              <tr>
                <th class="rank-cell">#</th>
                <th>Druzyna</th>
                ${hasSummary ? "<th>Awans</th><th>Pkt</th>" : ""}
              </tr>
            </thead>
            <tbody>
              ${rows
                .map(
                  (row, index) => `
                    <tr>
                      <td class="rank-cell">${index + 1}</td>
                      <td>${teamInline(row.team)}</td>
                      ${
                        hasSummary
                          ? `<td>${percent(row["qualified_%"])}</td><td>${Number(row.avg_points || 0).toFixed(2)}</td>`
                          : ""
                      }
                    </tr>
                  `,
                )
                .join("")}
            </tbody>
          </table>
        </article>
      `;
    })
    .join("");
}

function renderSummaryTable(target, rows, columns, maxRows = 32) {
  if (!rows || rows.length === 0) {
    target.className = "empty-state";
    target.textContent = "Brak wynikow.";
    return;
  }

  const visibleRows = rows.slice(0, maxRows);
  target.className = "table-wrap";
  target.innerHTML = `
    <table class="summary-table">
      <thead>
        <tr>
          <th class="rank-cell">#</th>
          ${columns.map((column) => `<th>${column.label}</th>`).join("")}
        </tr>
      </thead>
      <tbody>
        ${visibleRows
          .map(
            (row, index) => `
              <tr>
                <td class="rank-cell">${index + 1}</td>
                ${columns.map((column) => renderCell(row, column)).join("")}
              </tr>
            `,
          )
          .join("")}
      </tbody>
    </table>
  `;
}

function renderCell(row, column) {
  const value = row[column.key];
  if (column.bar) {
    const numericValue = Number(row[column.barKey || column.key] || 0);
    return `
      <td>
        <div class="team-with-bar">
          ${teamInline(row.team || "")}
          <div class="mini-meter" aria-hidden="true">
            <span style="width:${Math.max(0, Math.min(100, numericValue))}%"></span>
          </div>
        </div>
      </td>
    `;
  }
  if (column.percent) {
    return `<td>${percent(value)}</td>`;
  }
  return `<td>${escapeHtml(value ?? "")}</td>`;
}

function renderBracket(knockoutResults) {
  if (!knockoutResults || knockoutResults.length === 0) {
    els.bracketTree.className = "empty-state";
    els.bracketTree.textContent = "Brak danych drabinki.";
    return;
  }

  const simulationIds = knockoutResults
    .map((row) => Number(row.simulation_id || 1))
    .filter((id) => Number.isFinite(id));
  const selectedSimulationId = simulationIds.length ? Math.max(...simulationIds) : 1;
  const rows = knockoutResults.filter((row) => Number(row.simulation_id || 1) === selectedSimulationId);
  const champion = rows.find((row) => row.round === "Final")?.winner;
  const matchById = Object.fromEntries(rows.map((row) => [row.match_id, row]));
  const finalMatch = matchById.FINAL;

  els.bracketTree.className = "bracket-wrap";
  els.bracketTree.innerHTML = `
    <div class="bracket-meta">
      <span>Ostatnia symulacja: ${selectedSimulationId}</span>
      ${champion ? `<strong>${teamInline(champion)}</strong>` : ""}
    </div>
    <div class="bracket-split">
      ${renderBracketSide("left", matchById)}
      <section class="bracket-center">
        <div class="champion-card">
          <span>Winner</span>
          ${champion ? teamInline(champion) : ""}
        </div>
        ${finalMatch ? renderBracketMatch(finalMatch, "center") : ""}
      </section>
      ${renderBracketSide("right", matchById)}
    </div>
  `;
}

function renderBracketSide(side, matchById) {
  return `
    <div class="bracket-side bracket-${side}">
      ${BRACKET_SIDES[side]
        .map(
          (column) => `
            <section class="bracket-round depth-${column.depth}">
              <h3>${column.label}</h3>
              <div class="bracket-matches">
                ${column.ids
                  .map((id) => matchById[id])
                  .filter(Boolean)
                  .map((match) => renderBracketMatch(match, side))
                  .join("")}
              </div>
            </section>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderBracketMatch(match, side = "left") {
  return `
    <article class="bracket-match bracket-match-${side}">
      <div class="bracket-id">${escapeHtml(match.match_id)}</div>
      ${renderBracketTeam(match.home_team, match.winner)}
      ${renderBracketTeam(match.away_team, match.winner)}
    </article>
  `;
}

function renderBracketTeam(team, winner) {
  const isWinner = team === winner;
  return `
    <div class="bracket-team ${isWinner ? "winner" : ""}">
      ${teamInline(team)}
      ${isWinner ? '<span class="winner-mark">W</span>' : ""}
    </div>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
  return escapeHtml(value);
}

function activateView(viewId) {
  els.tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.view === viewId));
  els.views.forEach((view) => view.classList.toggle("active", view.id === viewId));
}

async function loadInitialData() {
  try {
    const [teamsPayload, matchesPayload] = await Promise.all([
      api("/teams"),
      api("/group-matches"),
    ]);
    state.teams = teamsPayload.teams || [];
    state.defaultMatches = matchesPayload.matches || [];
    renderTeamsList(state.teams);
    renderGroupRows(state.defaultMatches);
    els.statusText.textContent = `Model gotowy - ${state.teams.length} druzyn`;
  } catch (error) {
    els.statusText.textContent = "Blad ladowania";
    showToast(error.message, "error");
  }
}

els.tabs.forEach((tab) => {
  tab.addEventListener("click", () => activateView(tab.dataset.view));
});

els.matchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.submitter;
  setLoading(button, true, "Licze");
  try {
    const payload = await api("/predict-match", {
      method: "POST",
      body: JSON.stringify({
        home_team: els.homeTeam.value.trim(),
        away_team: els.awayTeam.value.trim(),
        tournament: els.matchTournament.value.trim() || "FIFA World Cup",
        neutral: els.neutralMatch.checked ? 1 : 0,
      }),
    });
    renderProbabilityResult(payload);
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setLoading(button, false);
  }
});

els.loadDefaultGroups.addEventListener("click", () => {
  renderGroupRows(state.defaultMatches);
  showToast("Zaladowano domyslne mecze grupowe");
});

els.addMatchRow.addEventListener("click", () => appendGroupRow());

els.groupMatchesBody.addEventListener("input", () => {
  state.latestGroupSummary = null;
  renderGroupTables();
});

els.groupSimulationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.submitter;
  const matches = collectGroupMatches();
  if (matches.length === 0) {
    showToast("Dodaj przynajmniej jeden mecz", "error");
    return;
  }

  setLoading(button, true, "Symuluje");
  try {
    const payload = await api("/simulate-group-stage", {
      method: "POST",
      body: JSON.stringify({
        matches,
        n_simulations: Number(els.groupSimulationCount.value || 1000),
        seed: optionalNumber(els.groupSeed),
      }),
    });

    state.latestGroupSummary = payload.summary || [];
    renderGroupTables(state.latestGroupSummary);
    renderSummaryTable(
      els.groupSummary,
      payload.summary || [],
      [
        { label: "Druzyna", key: "qualified_%", bar: true },
        { label: "Grupa", key: "group" },
        { label: "Awans", key: "qualified_%", percent: true },
        { label: "1. miejsce", key: "group_winner_%", percent: true },
        { label: "Pkt", key: "avg_points" },
      ],
      48,
    );
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setLoading(button, false);
  }
});

els.worldCupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.submitter;
  const editedMatches = collectGroupMatches();
  const useEditedMatches = els.useEditedGroups.checked && editedMatches.length > 0;

  setLoading(button, true, "Symuluje");
  try {
    const payload = await api("/simulate-world-cup", {
      method: "POST",
      body: JSON.stringify({
        matches: useEditedMatches ? editedMatches : null,
        n_simulations: Number(els.worldCupSimulationCount.value || 100),
        seed: optionalNumber(els.worldCupSeed),
        include_knockout_results: true,
      }),
    });

    renderSummaryTable(
      els.worldCupSummary,
      payload.summary || [],
      [
        { label: "Druzyna", key: "champion_%", bar: true },
        { label: "Mistrz", key: "champion_%", percent: true },
        { label: "Final", key: "final_%", percent: true },
        { label: "1/2", key: "semi_final_%", percent: true },
        { label: "1/4", key: "quarter_final_%", percent: true },
      ],
      24,
    );
    renderBracket(payload.knockout_results || []);
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setLoading(button, false);
  }
});

loadInitialData();
