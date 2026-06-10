const state = {
  teams: [],
  defaultMatches: [],
  currentMatches: [],
  latestGroupSummary: null,
  latestGroupPairings: null,
  editTarget: null,
};

const QUALIFICATION_OUTLINE_THRESHOLD = 50;

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

const R32_SLOTS = [
  { match_id: "R32_01", home_slot: "2A", away_slot: "2B" },
  { match_id: "R32_02", home_slot: "1C", away_slot: "2F" },
  { match_id: "R32_03", home_slot: "1E", away_slot: "3ABCDF" },
  { match_id: "R32_04", home_slot: "1F", away_slot: "2C" },
  { match_id: "R32_05", home_slot: "2E", away_slot: "2I" },
  { match_id: "R32_06", home_slot: "1I", away_slot: "3CDFGH" },
  { match_id: "R32_07", home_slot: "1A", away_slot: "3CEFHI" },
  { match_id: "R32_08", home_slot: "1L", away_slot: "3EHIJK" },
  { match_id: "R32_09", home_slot: "1G", away_slot: "3AEHIJ" },
  { match_id: "R32_10", home_slot: "1D", away_slot: "3BEFIJ" },
  { match_id: "R32_11", home_slot: "1H", away_slot: "2J" },
  { match_id: "R32_12", home_slot: "2K", away_slot: "2L" },
  { match_id: "R32_13", home_slot: "1B", away_slot: "3EFGIJ" },
  { match_id: "R32_14", home_slot: "2D", away_slot: "2G" },
  { match_id: "R32_15", home_slot: "1J", away_slot: "2H" },
  { match_id: "R32_16", home_slot: "1K", away_slot: "3DEIJL" },
];

const GROUP_R16_MAPPING = [
  ["R16_01", "R32_03", "R32_06"],
  ["R16_02", "R32_01", "R32_04"],
  ["R16_03", "R32_02", "R32_05"],
  ["R16_04", "R32_07", "R32_08"],
  ["R16_05", "R32_12", "R32_11"],
  ["R16_06", "R32_10", "R32_09"],
  ["R16_07", "R32_15", "R32_14"],
  ["R16_08", "R32_13", "R32_16"],
];

const GROUP_QF_MAPPING = [
  ["QF_01", "R16_01", "R16_02"],
  ["QF_02", "R16_05", "R16_06"],
  ["QF_03", "R16_03", "R16_04"],
  ["QF_04", "R16_07", "R16_08"],
];

const GROUP_SF_MAPPING = [
  ["SF_01", "QF_01", "QF_02"],
  ["SF_02", "QF_03", "QF_04"],
];

const GROUP_FINAL_MAPPING = [["FINAL", "SF_01", "SF_02"]];

const GROUP_BRACKET_MAPPINGS = [
  ...GROUP_R16_MAPPING,
  ...GROUP_QF_MAPPING,
  ...GROUP_SF_MAPPING,
  ...GROUP_FINAL_MAPPING,
];

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
  groupTables: document.getElementById("groupTables"),
  groupSimulationForm: document.getElementById("groupSimulationForm"),
  groupSimulationCount: document.getElementById("groupSimulationCount"),
  groupSummary: document.getElementById("groupSummary"),
  thirdPlaceSummary: document.getElementById("thirdPlaceSummary"),
  showGroupBracket: document.getElementById("showGroupBracket"),
  groupBracketPanel: document.getElementById("groupBracketPanel"),
  groupBracketPreview: document.getElementById("groupBracketPreview"),
  runTournamentFromGroups: document.getElementById("runTournamentFromGroups"),
  worldCupForm: document.getElementById("worldCupForm"),
  worldCupSimulationCount: document.getElementById("worldCupSimulationCount"),
  useEditedGroups: document.getElementById("useEditedGroups"),
  worldCupSummary: document.getElementById("worldCupSummary"),
  bracketTree: document.getElementById("bracketTree"),
  teamEditorOverlay: document.getElementById("teamEditorOverlay"),
  teamEditorForm: document.getElementById("teamEditorForm"),
  teamEditorCurrent: document.getElementById("teamEditorCurrent"),
  teamEditorInput: document.getElementById("teamEditorInput"),
  closeTeamEditor: document.getElementById("closeTeamEditor"),
};

const autocomplete = {
  input: null,
  menu: document.createElement("div"),
  options: [],
  activeIndex: -1,
};

autocomplete.menu.className = "autocomplete-menu";
autocomplete.menu.hidden = true;
document.body.appendChild(autocomplete.menu);

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

function formatNumber(value, digits = 2) {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? numberValue.toFixed(digits) : "-";
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
        onerror="window.fallbackFlagImage(this, '${upperCode}')"
      />
    </span>
  `;
}

window.fallbackFlagImage = (img, code) => {
  const attempt = Number(img.dataset.fallbackAttempt || 0);

  if (attempt === 0) {
    img.dataset.fallbackAttempt = "1";
    img.removeAttribute("srcset");
    img.src = `https://flagsapi.com/${code}/flat/64.png`;
    return;
  }

  img.parentElement.classList.add("flag-fallback");
  img.parentElement.textContent = code;
};

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

function normalizeSearchText(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function getTeamSuggestions(query) {
  const normalizedQuery = normalizeSearchText(query);
  if (!normalizedQuery) {
    return state.teams.slice(0, 12);
  }

  return state.teams
    .map((team) => ({
      team,
      normalized: normalizeSearchText(team),
    }))
    .filter(({ normalized }) => normalized.includes(normalizedQuery))
    .sort((a, b) => {
      const aStarts = a.normalized.startsWith(normalizedQuery);
      const bStarts = b.normalized.startsWith(normalizedQuery);
      if (aStarts !== bStarts) {
        return aStarts ? -1 : 1;
      }
      return a.team.localeCompare(b.team, "pl", { sensitivity: "base" });
    })
    .map(({ team }) => team)
    .slice(0, 12);
}

function setupTeamAutocomplete(inputs) {
  inputs.forEach((input) => {
    input.removeAttribute("list");
    input.setAttribute("autocomplete", "off");

    input.addEventListener("input", () => showAutocomplete(input));
    input.addEventListener("focus", () => showAutocomplete(input));
    input.addEventListener("keydown", handleAutocompleteKeydown);
  });

  document.addEventListener("pointerdown", (event) => {
    if (event.target === autocomplete.input || autocomplete.menu.contains(event.target)) {
      return;
    }
    closeAutocomplete();
  });

  window.addEventListener("resize", positionAutocomplete);
  window.addEventListener("scroll", positionAutocomplete, true);
}

function showAutocomplete(input) {
  autocomplete.input = input;
  autocomplete.options = getTeamSuggestions(input.value);
  autocomplete.activeIndex = autocomplete.options.length ? 0 : -1;

  if (!autocomplete.options.length) {
    autocomplete.menu.innerHTML = `<div class="autocomplete-empty">Brak druzyn</div>`;
  } else {
    autocomplete.menu.innerHTML = autocomplete.options
      .map(
        (team, index) => `
          <button
            class="autocomplete-option ${index === autocomplete.activeIndex ? "active" : ""}"
            type="button"
            data-team="${escapeAttr(team)}"
          >
            ${teamInline(team)}
          </button>
        `,
      )
      .join("");
  }

  autocomplete.menu.querySelectorAll(".autocomplete-option").forEach((button) => {
    button.addEventListener("pointerdown", (event) => {
      event.preventDefault();
      selectAutocompleteTeam(button.dataset.team);
    });
  });

  positionAutocomplete();
  autocomplete.menu.hidden = false;
}

function positionAutocomplete() {
  if (!autocomplete.input || autocomplete.menu.hidden) {
    return;
  }

  const rect = autocomplete.input.getBoundingClientRect();
  autocomplete.menu.style.left = `${rect.left}px`;
  autocomplete.menu.style.top = `${rect.bottom + 4}px`;
  autocomplete.menu.style.width = `${rect.width}px`;
}

function closeAutocomplete() {
  autocomplete.input = null;
  autocomplete.options = [];
  autocomplete.activeIndex = -1;
  autocomplete.menu.hidden = true;
}

function refreshAutocompleteActiveOption() {
  autocomplete.menu.querySelectorAll(".autocomplete-option").forEach((button, index) => {
    button.classList.toggle("active", index === autocomplete.activeIndex);
  });
}

function selectAutocompleteTeam(team) {
  if (!autocomplete.input || !team) {
    return;
  }

  autocomplete.input.value = team;
  autocomplete.input.dispatchEvent(new Event("change", { bubbles: true }));
  autocomplete.input.focus();
  closeAutocomplete();
}

function handleAutocompleteKeydown(event) {
  if (autocomplete.input !== event.currentTarget || autocomplete.menu.hidden) {
    return;
  }

  if (event.key === "ArrowDown") {
    event.preventDefault();
    autocomplete.activeIndex = Math.min(autocomplete.activeIndex + 1, autocomplete.options.length - 1);
    refreshAutocompleteActiveOption();
  }

  if (event.key === "ArrowUp") {
    event.preventDefault();
    autocomplete.activeIndex = Math.max(autocomplete.activeIndex - 1, 0);
    refreshAutocompleteActiveOption();
  }

  if (event.key === "Enter" && autocomplete.activeIndex >= 0) {
    event.preventDefault();
    selectAutocompleteTeam(autocomplete.options[autocomplete.activeIndex]);
  }

  if (event.key === "Escape") {
    event.stopPropagation();
    closeAutocomplete();
  }
}

function renderGroupRows(matches) {
  state.currentMatches = matches.map((match) => ({
    group: String(match.group || "").trim(),
    home_team: String(match.home_team || "").trim(),
    away_team: String(match.away_team || "").trim(),
  }));
  resetGroupSimulationResults();
  renderGroupTables();
}

function collectGroupMatches() {
  return state.currentMatches
    .map((match) => ({
      group: String(match.group || "").trim(),
      home_team: String(match.home_team || "").trim(),
      away_team: String(match.away_team || "").trim(),
    }))
    .filter((match) => match.group && match.home_team && match.away_team);
}

function resetGroupSimulationResults() {
  state.latestGroupSummary = null;
  state.latestGroupPairings = null;
  els.groupSummary.className = "empty-state";
  els.groupSummary.textContent = "Brak wynikow symulacji.";
  els.thirdPlaceSummary.className = "empty-state";
  els.thirdPlaceSummary.textContent = "Uruchom symulacje grup.";
  els.showGroupBracket.disabled = true;
  els.groupBracketPanel.hidden = true;
  els.groupBracketPreview.className = "empty-state";
  els.groupBracketPreview.textContent = "Brak danych drabinki.";
}

function groupHasTeam(group, team) {
  return collectGroupMatches().some(
    (match) => match.group === group && (match.home_team === team || match.away_team === team),
  );
}

function openTeamEditor(group, team) {
  state.editTarget = { group, team };
  els.teamEditorCurrent.innerHTML = `
    <span>Aktualnie w grupie ${escapeHtml(group)}</span>
    ${teamInline(team)}
  `;
  els.teamEditorInput.value = team;
  els.teamEditorOverlay.hidden = false;
  window.setTimeout(() => els.teamEditorInput.focus(), 0);
}

function closeTeamEditor() {
  state.editTarget = null;
  els.teamEditorOverlay.hidden = true;
}

function replaceTeamInGroup(group, oldTeam, newTeam) {
  state.currentMatches = state.currentMatches.map((match) => {
    if (match.group !== group) {
      return match;
    }

    return {
      ...match,
      home_team: match.home_team === oldTeam ? newTeam : match.home_team,
      away_team: match.away_team === oldTeam ? newTeam : match.away_team,
    };
  });
  resetGroupSimulationResults();
  renderGroupTables();
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

function compareGroupSummaryRows(a, b) {
  return (
    Number(b["qualified_%"] || 0) - Number(a["qualified_%"] || 0) ||
    Number(b["group_winner_%"] || 0) - Number(a["group_winner_%"] || 0) ||
    Number(b.avg_points || 0) - Number(a.avg_points || 0) ||
    String(a.team).localeCompare(String(b.team), "pl", { sensitivity: "base" })
  );
}

function compareThirdPlaceRows(a, b) {
  return (
    Number(b.avg_points || 0) - Number(a.avg_points || 0) ||
    Number(b["qualified_%"] || 0) - Number(a["qualified_%"] || 0) ||
    Number(b["group_winner_%"] || 0) - Number(a["group_winner_%"] || 0) ||
    String(a.team).localeCompare(String(b.team), "pl", { sensitivity: "base" })
  );
}

function buildGroupTableRowsFromSummary(summaryRows) {
  const groups = new Map();
  [...summaryRows]
    .sort((a, b) => {
      const groupCompare = String(a.group).localeCompare(String(b.group), "pl", { numeric: true });
      if (groupCompare !== 0) return groupCompare;
      return compareGroupSummaryRows(a, b);
    })
    .forEach((row) => {
      if (!groups.has(row.group)) {
        groups.set(row.group, []);
      }
      groups.get(row.group).push(row);
    });
  return groups;
}

function buildRankedGroupsFromSummary(summaryRows) {
  const groups = buildGroupTableRowsFromSummary(summaryRows);
  const rankedGroups = new Map();

  groups.forEach((rows, group) => {
    rankedGroups.set(
      group,
      rows.map((row, index) => ({
        ...row,
        group_position: index + 1,
      })),
    );
  });

  return rankedGroups;
}

function getThirdPlaceRows(summaryRows) {
  return [...buildRankedGroupsFromSummary(summaryRows).values()]
    .map((rows) => rows[2])
    .filter(Boolean);
}

function getBestThirdPlaceRows(summaryRows) {
  return getThirdPlaceRows(summaryRows).sort(compareThirdPlaceRows).slice(0, 8);
}

function renderThirdPlaceSummary(summaryRows) {
  if (!summaryRows || !summaryRows.length) {
    els.thirdPlaceSummary.className = "empty-state";
    els.thirdPlaceSummary.textContent = "Uruchom symulacje grup.";
    els.showGroupBracket.disabled = true;
    return;
  }

  const thirdRows = getThirdPlaceRows(summaryRows).sort(compareThirdPlaceRows);
  const qualifiedThirdKeys = new Set(
    thirdRows.slice(0, 8).map((row) => `${row.group}::${row.team}`),
  );

  els.showGroupBracket.disabled = thirdRows.length < 8;
  els.thirdPlaceSummary.className = "table-wrap";
  els.thirdPlaceSummary.innerHTML = `
    <table class="summary-table third-place-table">
      <thead>
        <tr>
          <th class="rank-cell">#</th>
          <th>Druzyna</th>
          <th>Grupa</th>
          <th>Awans</th>
          <th>Srednie pkt</th>
        </tr>
      </thead>
      <tbody>
        ${thirdRows
          .map((row, index) => {
            const isQualified = qualifiedThirdKeys.has(`${row.group}::${row.team}`);
            return `
              <tr class="${isQualified ? "third-qualified-row" : ""}">
                <td class="rank-cell">${index + 1}</td>
                <td>${teamInline(row.team)}</td>
                <td>${escapeHtml(row.group)}</td>
                <td>${percent(row["qualified_%"])}</td>
                <td>${formatNumber(row.avg_points)}</td>
              </tr>
            `;
          })
          .join("")}
      </tbody>
    </table>
  `;
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
                .map((row, index) => {
                  const isThirdPlace = index === 2;
                  const isLikelyQualified =
                    hasSummary && Number(row["qualified_%"] || 0) >= QUALIFICATION_OUTLINE_THRESHOLD;
                  return `
                    <tr class="${isLikelyQualified ? "likely-qualified-row" : ""} ${isThirdPlace ? "third-place-row" : ""}">
                      <td class="rank-cell">${index + 1}</td>
                      <td>
                        <button
                          class="team-edit-button ${isLikelyQualified ? "qualified-team" : ""} ${isThirdPlace ? "third-place-team" : ""}"
                          type="button"
                          data-group="${escapeAttr(row.group)}"
                          data-team="${escapeAttr(row.team)}"
                          title="Zmien ${escapeAttr(row.team)}"
                        >
                          ${teamInline(row.team)}
                        </button>
                      </td>
                      ${
                        hasSummary
                          ? `<td>${percent(row["qualified_%"])}</td><td>${Number(row.avg_points || 0).toFixed(2)}</td>`
                          : ""
                      }
                    </tr>
                  `;
                })
                .join("")}
            </tbody>
          </table>
        </article>
      `;
    })
    .join("");
}

function getTeamFromDirectSlot(rankedGroups, slot) {
  const position = Number(slot.slice(0, 1));
  const group = slot.slice(1);
  const rows = rankedGroups.get(group);
  const selected = rows?.find((row) => row.group_position === position);

  if (!selected) {
    throw new Error(`Brak druzyny dla slotu ${slot}`);
  }

  return selected.team;
}

function findValidThirdPlaceAssignment(thirdPlaceRows, thirdPlaceSlots) {
  const candidatesBySlot = Object.fromEntries(
    thirdPlaceSlots.map((slot) => [
      slot,
      thirdPlaceRows
        .filter((row) => slot.slice(1).includes(row.group))
        .sort(compareThirdPlaceRows),
    ]),
  );
  const slotsSorted = [...thirdPlaceSlots].sort(
    (a, b) => candidatesBySlot[a].length - candidatesBySlot[b].length,
  );
  const assignment = {};
  const usedTeams = new Set();

  function backtrack(slotIndex) {
    if (slotIndex === slotsSorted.length) {
      return true;
    }

    const slot = slotsSorted[slotIndex];
    for (const candidate of candidatesBySlot[slot]) {
      if (usedTeams.has(candidate.team)) {
        continue;
      }

      assignment[slot] = candidate.team;
      usedTeams.add(candidate.team);

      if (backtrack(slotIndex + 1)) {
        return true;
      }

      usedTeams.delete(candidate.team);
      delete assignment[slot];
    }

    return false;
  }

  if (!backtrack(0)) {
    throw new Error("Nie udalo sie przypisac trzecich miejsc do drabinki.");
  }

  return assignment;
}

function createGroupStageBracketPairings(summaryRows) {
  const rankedGroups = buildRankedGroupsFromSummary(summaryRows);
  const bestThirdPlaces = getBestThirdPlaceRows(summaryRows);

  if (bestThirdPlaces.length < 8) {
    throw new Error("Za malo trzecich miejsc do zbudowania drabinki.");
  }

  const thirdPlaceSlots = R32_SLOTS
    .map((match) => match.away_slot)
    .filter((slot) => slot.startsWith("3"));
  const thirdPlaceAssignment = findValidThirdPlaceAssignment(bestThirdPlaces, thirdPlaceSlots);

  return R32_SLOTS.map((match) => {
    const homeTeam = match.home_slot.startsWith("3")
      ? thirdPlaceAssignment[match.home_slot]
      : getTeamFromDirectSlot(rankedGroups, match.home_slot);
    const awayTeam = match.away_slot.startsWith("3")
      ? thirdPlaceAssignment[match.away_slot]
      : getTeamFromDirectSlot(rankedGroups, match.away_slot);

    return {
      ...match,
      home_team: homeTeam,
      away_team: awayTeam,
    };
  });
}

function renderGroupBracketPreview(pairings) {
  state.latestGroupPairings = pairings;
  els.groupBracketPanel.hidden = false;
  renderGroupBracketPreviewInto(
    els.groupBracketPreview,
    pairings,
    "Podglad ukladu fazy pucharowej po wynikach grup",
    "Bez symulacji zwyciezcow kolejnych rund",
  );
}

function renderWorldCupGroupBracketPreview(pairings) {
  state.latestGroupPairings = pairings;
  renderGroupBracketPreviewInto(
    els.bracketTree,
    pairings,
    "Podglad drabinki z zakladki Grupy",
    "Uruchom symulacje turnieju, aby zobaczyc wyniki",
  );
}

function getLatestGroupQualifierPairings() {
  if (state.latestGroupPairings && state.latestGroupPairings.length) {
    return state.latestGroupPairings;
  }

  if (!state.latestGroupSummary || !state.latestGroupSummary.length) {
    throw new Error("Najpierw uruchom symulacje grup, aby wybrac kwalifikantow.");
  }

  state.latestGroupPairings = createGroupStageBracketPairings(state.latestGroupSummary);
  return state.latestGroupPairings;
}

function renderGroupBracketPreviewInto(target, pairings, metaText, metaStrong) {
  const matchById = buildGroupBracketPreviewMatches(pairings);

  target.className = "bracket-wrap group-bracket-tree";
  target.innerHTML = `
    <div class="bracket-meta">
      <span>${escapeHtml(metaText)}</span>
      <strong>${escapeHtml(metaStrong)}</strong>
    </div>
    <div class="bracket-split">
      ${renderGroupBracketSide("left", matchById)}
      <section class="bracket-center group-bracket-center">
        ${renderGroupFinalPreview(matchById.FINAL)}
      </section>
      ${renderGroupBracketSide("right", matchById)}
    </div>
 `;
}

function buildGroupBracketPreviewMatches(pairings) {
  const matchById = Object.fromEntries(
    pairings.map((match) => [
      match.match_id,
      {
        ...match,
        home_placeholder: false,
        away_placeholder: false,
      },
    ]),
  );

  for (const [matchId, homeSource, awaySource] of GROUP_BRACKET_MAPPINGS) {
    matchById[matchId] = {
      match_id: matchId,
      home_team: `Zwyciezca ${homeSource}`,
      away_team: `Zwyciezca ${awaySource}`,
      home_placeholder: true,
      away_placeholder: true,
    };
  }

  return matchById;
}

function renderGroupBracketSide(side, matchById) {
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
                  .map((match) => renderGroupPreviewMatch(match, side))
                  .join("")}
              </div>
            </section>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderGroupPreviewMatch(match, side = "left") {
  return `
    <article class="bracket-match bracket-match-${side}">
      <div class="bracket-id">${escapeHtml(match.match_id)}</div>
      ${renderGroupPreviewTeam(match.home_team, match.home_placeholder, match.home_slot)}
      ${renderGroupPreviewTeam(match.away_team, match.away_placeholder, match.away_slot)}
    </article>
  `;
}

function renderGroupFinalPreview(match) {
  return `
    <article class="group-final-card" aria-label="Final mistrzostw swiata">
      <div class="group-final-icon" aria-hidden="true">
        <svg viewBox="0 0 64 64" focusable="false">
          <path d="M22 9h20v8h10v8c0 9-5 16-14 18v6h8v7H18v-7h8v-6c-9-2-14-9-14-18v-8h10V9Zm6 6v20c0 4 2 7 4 7s4-3 4-7V15h-8Zm14 8v12c3-2 5-6 5-10v-2h-5Zm-25 0v2c0 4 2 8 5 10V23h-5Z" />
        </svg>
      </div>
      <div class="group-final-heading">
        <span>${escapeHtml(match.match_id)}</span>
        <strong>Final mistrzostw swiata</strong>
        <small>Zwyciezcy polfinalow spotkaja sie tutaj</small>
      </div>
      <div class="group-final-teams">
        ${renderGroupFinalTeam(match.home_team)}
        <span class="final-vs">VS</span>
        ${renderGroupFinalTeam(match.away_team)}
      </div>
    </article>
  `;
}

function renderGroupFinalTeam(team) {
  return `
    <div class="group-final-team">
      <span class="placeholder-dot" aria-hidden="true"></span>
      <span class="team-name">${escapeHtml(team)}</span>
    </div>
  `;
}

function renderGroupPreviewTeam(team, isPlaceholder = false, slot = "") {
  if (isPlaceholder) {
    return `
      <div class="bracket-team bracket-team-placeholder">
        <span class="team-inline">
          <span class="placeholder-dot" aria-hidden="true"></span>
          <span class="team-name">${escapeHtml(team)}</span>
        </span>
      </div>
    `;
  }

  return `
    <div class="bracket-team bracket-team-live">
      ${teamInline(team)}
      ${slot ? `<span class="slot-pill">${escapeHtml(slot)}</span>` : ""}
    </div>
  `;
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
      <span>Ostatnia przeprowadzona drabinka z symulacji: ${selectedSimulationId}</span>
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

els.groupTables.addEventListener("click", (event) => {
  const button = event.target.closest(".team-edit-button");
  if (!button) {
    return;
  }
  openTeamEditor(button.dataset.group, button.dataset.team);
});

els.closeTeamEditor.addEventListener("click", closeTeamEditor);

els.teamEditorOverlay.addEventListener("click", (event) => {
  if (event.target === els.teamEditorOverlay) {
    closeTeamEditor();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !els.teamEditorOverlay.hidden) {
    closeTeamEditor();
  }
});

els.teamEditorForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!state.editTarget) {
    return;
  }

  const newTeam = els.teamEditorInput.value.trim();
  const { group, team: oldTeam } = state.editTarget;

  if (!newTeam) {
    showToast("Wybierz druzyne", "error");
    return;
  }

  if (!state.teams.includes(newTeam)) {
    showToast("Tej druzyny nie ma w danych rankingowych", "error");
    return;
  }

  if (newTeam !== oldTeam && groupHasTeam(group, newTeam)) {
    showToast("Ta druzyna juz jest w tej grupie", "error");
    return;
  }

  replaceTeamInGroup(group, oldTeam, newTeam);
  closeTeamEditor();
  showToast(`Zmieniono ${oldTeam} na ${newTeam}`);
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
      }),
    });

    state.latestGroupSummary = payload.summary || [];
    state.latestGroupPairings = null;
    renderGroupTables(state.latestGroupSummary);
    renderThirdPlaceSummary(state.latestGroupSummary);
    els.groupBracketPanel.hidden = true;
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
      state.latestGroupSummary.length,
    );
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setLoading(button, false);
  }
});

els.showGroupBracket.addEventListener("click", () => {
  if (!state.latestGroupSummary || !state.latestGroupSummary.length) {
    showToast("Najpierw uruchom symulacje grup", "error");
    return;
  }

  try {
    const pairings = getLatestGroupQualifierPairings();
    renderGroupBracketPreview(pairings);
    els.groupBracketPanel.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  } catch (error) {
    showToast(error.message, "error");
  }
});

els.runTournamentFromGroups.addEventListener("click", () => {
  if (!state.latestGroupSummary || !state.latestGroupSummary.length) {
    showToast("Najpierw uruchom symulacje grup", "error");
    return;
  }

  try {
    const pairings = getLatestGroupQualifierPairings();
    renderWorldCupGroupBracketPreview(pairings);
    els.worldCupSummary.className = "empty-state";
    els.worldCupSummary.textContent = "Uruchom symulacje turnieju dla aktualnej drabinki.";
    els.useEditedGroups.checked = true;
    activateView("worldCupView");
    els.worldCupForm.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  } catch (error) {
    showToast(error.message, "error");
  }
});

els.worldCupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.submitter;
  const useGroupQualifiers = els.useEditedGroups.checked;
  let r32Pairings = null;

  if (useGroupQualifiers) {
    if (!state.latestGroupSummary || !state.latestGroupSummary.length) {
      showToast("Najpierw uruchom symulacje grup, aby wybrac kwalifikantow", "error");
      return;
    }

    try {
      r32Pairings = getLatestGroupQualifierPairings();
      renderWorldCupGroupBracketPreview(r32Pairings);
    } catch (error) {
      showToast(error.message, "error");
      return;
    }
  }

  setLoading(button, true, "Symuluje");
  try {
    const payload = await api("/simulate-world-cup", {
      method: "POST",
      body: JSON.stringify({
        matches: null,
        r32_pairings: r32Pairings
          ? r32Pairings.map((pairing) => ({
              match_id: pairing.match_id,
              home_slot: pairing.home_slot,
              away_slot: pairing.away_slot,
              home_team: pairing.home_team,
              away_team: pairing.away_team,
            }))
          : null,
        n_simulations: Number(els.worldCupSimulationCount.value || 100),
        include_knockout_results: true,
      }),
    });

    const worldCupSummaryRows = payload.summary || [];
    renderSummaryTable(
      els.worldCupSummary,
      worldCupSummaryRows,
      [
        { label: "Druzyna", key: "champion_%", bar: true },
        { label: "Mistrz", key: "champion_%", percent: true },
        { label: "Final", key: "final_%", percent: true },
        { label: "1/2", key: "semi_final_%", percent: true },
        { label: "1/4", key: "quarter_final_%", percent: true },
      ],
      worldCupSummaryRows.length,
    );
    renderBracket(payload.knockout_results || []);
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setLoading(button, false);
  }
});

setupTeamAutocomplete([els.homeTeam, els.awayTeam, els.teamEditorInput]);
loadInitialData();
