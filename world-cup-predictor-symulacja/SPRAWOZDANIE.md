# Sprawozdanie — Symulacja meczu (World Cup Predictor)

## Cel zadania

Rozszerzenie koncepcji projektu [World Cup Predictor](https://github.com/Bartek0083/ProjektZesp---World-Cup-Predicter) o **szczegółową symulację przebiegu meczu** z animacją zdarzeń, trybami towarzyskim i turniejowym oraz regulaminem pucharowym (dogrywka, złota bramka, rzuty karne).

Oryginalny projekt przewiduje wynik meczu jako `home_win` / `draw` / `away_win` bez minut bramek. Niniejsze rozwiązanie jest **samodzielnym modułem** w folderze `world-cup-predictor-symulacja/`, kompatybilnym koncepcyjnie z predyktorem, ale nie wymagającym trenowania modelu ML.

## Podział ról w zespole

| Osoba | Zakres prac |
|-------|-------------|
| **Bartłomiej Muranowicz** | Główny projekt [World Cup Predictor](https://github.com/Bartek0083/ProjektZesp---World-Cup-Predicter): model ML, predykcja wyników, symulacja fazy grupowej i całego turnieju, oryginalny backend (`api.py`, `model.py`, `simulator.py`) i frontend aplikacji. Koordynacja zespołu, specyfikacja wymagań modułu meczowego (animacja przebiegu, tryby towarzyski/turniejowy, dogrywka, złota bramka, karne). |
| **Jakub Szych** | Moduł `world-cup-predictor-symulacja/`: silnik symulacji minutowej (`match_engine.py`), interfejs webowy (score bug, boisko, relacja na żywo), integracja TheSportsDB (drużyny, mecze na dziś, timeline), testy jednostkowe, demo terminalowe, sprawozdanie, konfiguracja deployu (Docker, Render). |

Moduł symulacji jest **samodzielny** — można go uruchomić osobno albo w przyszłości wpiąć w zakładkę „Mecz” głównej aplikacji Bartka.

## Co zrobiono

### 1. Silnik symulacji (`match_engine.py`)

- Generowanie bramek minuta po minucie (rozkład Poissona + losowe minuty z wagą na drugą połowę).
- Lista zdarzeń: rozpoczęcie, bramki, koniec połowy/regulaminu, start dogrywki, złota bramka, karne.
- **Tryb towarzyski** — 90 minut, remis możliwy.
- **Tryb turniejowy** z opcjami:
  - dogrywka do 120 minut,
  - złota bramka (pierwsza bramka w dogrywce kończy mecz),
  - karne bezpośrednio po 90 minutach (bez dogrywki),
  - karne po remisie po dogrywce.

### 2. API web (`api.py` + `frontend/`)

- FastAPI z endpointem `POST /simulate-match`.
- Interfejs w przeglądarce (HTML/CSS/JS bez frameworków):
  - tablica wyniku na żywo,
  - „boisko” z markerami bramek na osi czasu 0–120 min,
  - feed zdarzeń z animacją krok po kroku,
  - panel wyniku końcowego i siatka rzutów karnych.

#### Interfejs użytkownika (UI)

Wygląd celowo prosty — jak studencki moduł do wyników piłkarskich, a nie „dashboard startupowy”:

- **Paleta:** szare tło strony, ciemny pasek wyniku (score bug jak w transmisji TV), zielona murawa z białymi liniami boiska.
- **Typografia:** `Segoe UI` / `system-ui` — bez zewnętrznych fontów.
- **Układ:** trzy kolumny — formularz ustawień | widok meczu (wynik + boisko + relacja) | podsumowanie i karne.
- **Formularz:** listy rozwijane z drużynami z API, typ meczu (towarzyski/turniejowy), opcje pucharowe (dogrywka, złota bramka, karne po 90 min).
- **Animacja:** po kliknięciu „Symuluj mecz” relacja odkrywa zdarzenia minuta po minucie; markery bramek pojawiają się na boisku.
- **Karne:** tabela z numerem rzutu, drużyną i wynikiem (GOL/PUDŁO) plus suma karnych.

### 3. Demo terminalowe (`demo_terminal.py`)

- Cztery scenariusze testowe (towarzyski, dogrywka+karne, złota bramka, karne po 90 min).
- Opcja `--animate` z opóźnieniem między zdarzeniami.

### 4. Mecze z API — wybór aktualnych i nadchodzących (`sportsdb_client.py` + zakładka UI)

- **Cel:** użytkownik wybiera prawdziwe mecze z TheSportsDB zamiast ręcznego wpisywania drużyn.
- **Free tier (klucz `123`):**
  - `eventsday.php?s=Soccer&d=YYYY-MM-DD` — do **3 meczów** piłkarskich na dzień,
  - `eventsnextleague.php?id={idLeague}` — **1 najbliższy** mecz na ligę,
  - **brak** livescore v2 (tylko premium) — w UI wyjaśniono, że pokazujemy mecze na dziś / nadchodzące, nie pełny feed na żywo.
- **Ligi w cache nadchodzących:** FIFA World Cup (`4429`), Liga Mistrzów, Premier League, La Liga, Bundesliga, Serie A.
- **Cache meczów:** `data/matches_cache.json`, TTL **20 min**; seed awaryjny: `data/matches_seed.json`.
- **Endpointy backendu:**
  - `GET /matches?date=YYYY-MM-DD` — mecze na dany dzień (domyślnie dziś),
  - `GET /matches/upcoming` — nadchodzące z popularnych lig,
  - `GET /matches/{event_id}` — szczegóły (+ `?timeline=1`),
  - `GET /matches/{event_id}/timeline` — prawdziwy przebieg (bramki, kartki, zmiany),
  - `POST /matches/refresh` — odświeżenie cache meczów.
- **Frontend — zakładka „Mecze z API”:**
  - lista meczów (data, godzina, herby, wynik / status),
  - kliknięcie → szczegóły + animowany timeline dla rozegranych,
  - przycisk **„Symuluj ten mecz”** dla nadchodzących — wstawia drużyny do symulatora i uruchamia symulację.

```powershell
curl "http://127.0.0.1:8010/matches"
curl "http://127.0.0.1:8010/matches/upcoming"
curl "http://127.0.0.1:8010/matches/2391728"
curl "http://127.0.0.1:8010/matches/2391728/timeline"
curl -X POST http://127.0.0.1:8010/matches/refresh
```

### 5. Integracja TheSportsDB — drużyny (`sportsdb_client.py`)

- **Proxy przez backend** — klucz API w zmiennej `THESPORTSDB_API_KEY` (domyślnie `123` na free tier), nigdy w frontendzie.
- **Cache lokalny** — `data/teams_cache.json`; symulacja nie woła zewnętrznego API przy każdym meczu.
- **Pobieranie drużyn** — liga `FIFA World Cup` + reprezentacje po kraju (`search_all_teams.php?s=Soccer&c=...`); przy małej odpowiedzi free tier — merge z seedem z `teams_data.py`.
- **Rating** — `attack` / `defense` z rankingu lub znanych wartości FIFA; używane w `match_engine` przez `get_team_rating()`.
- **Endpointy:**
  - `GET /teams` — lista obiektów `{id, name, country, badge, rating, attack, defense}`
  - `POST /teams/refresh` — odświeżenie cache z TheSportsDB (opóźnienie między zapytaniami ~0,35 s)
- **Frontend** — selecty z `/teams`, herb (badge) w score bugu obok nazwy drużyny.
- **Fallback** — przy niedostępnym API działa cache lub seed; symulacja bez zmian w UX.

```powershell
# opcjonalnie własny klucz API
$env:THESPORTSDB_API_KEY = "123"
curl http://127.0.0.1:8010/teams
curl -X POST http://127.0.0.1:8010/teams/refresh
```

### 6. Testy (`tests/`)

- Remis w meczu towarzyskim, brak karnych.
- Karn po 90 min, dogrywka, złota bramka, powtarzalność z seedem.
- `test_sportsdb_matches.py` — parsowanie meczów, timeline, seed fallback, endpointy `/matches*`.

## Jak uruchomić

### Wymagania

- Python 3.10+

### Instalacja

```powershell
cd "E:\6 semestr\world-cup-predictor-symulacja"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Aplikacja web

```powershell
python -m uvicorn api:app --reload --port 8010
```

Otwórz: **http://127.0.0.1:8010/**

### Demo w terminalu

```powershell
python demo_terminal.py
python demo_terminal.py --animate
```

### Testy

```powershell
python -m unittest discover -s tests -v
```

## Widoki i dashboardy

| Widok | Opis |
|-------|------|
| **Score bug** | Ciemny pasek: drużyny, wynik, minuta i faza meczu |
| **Boisko** | Murawa w pasy, linie boiska, markery bramek na osi 0–120 min |
| **Relacja na żywo** | Tabela zdarzeń (minuta, opis, wynik) z animacją krok po kroku |
| **Podsumowanie** | Wynik końcowy, wynik po 90 min, sposób rozstrzygnięcia, lista bramek |
| **Tabela karnych** | Numer rzutu, drużyna, GOL / PUDŁO, wynik serii |
| **Mecze z API** | Lista meczów na dziś / nadchodzące, szczegóły, prawdziwy timeline, symulacja wybranego meczu |

## Przykładowe obserwacje z testów

Uruchomiono `python demo_terminal.py` (seedy ustalone) oraz testy jednostkowe.

**Scenariusz 1 — towarzyski (Argentyna vs Brazylia, seed=42):**
- Regulaminowy czas z bramkami w konkretnych minutach.
- Mecz rozstrzygnięty w 90 minutach lub remis — bez dogrywki i karnych.

**Scenariusz 2 — turniej, dogrywka + karne (Francja vs Anglia, seed=7):**
- Po remisie 90' uruchamia się dogrywka (91–105', 106–120').
- Przy dalszym remisie — seria karnych z widocznym wynikiem karnych i zwycięzcą.

**Scenariusz 3 — złota bramka (Hiszpania vs Niemcy, seed=99):**
- W dogrywce pierwsza bramka oznaczona jako `★ ZŁOTA BRAMKA` kończy symulację (`decided_by: golden_goal`).

**Scenariusz 4 — karne po 90 min (Portugalia vs Holandia, seed=123):**
- Przy remisie po 90' pomijana jest dogrywka; od razu faza `penalties`.

**Testy automatyczne:** 8 testów — wszystkie zaliczone (`OK`).

## Powiązanie z oryginalnym repo

Oryginalny `simulator.py` w projekcie GitHub:
- `simulate_match()` — losuje wynik 1X2 z prawdopodobieństw modelu.
- `simulate_knockout_match()` — przy remisie wybiera zwycięzcę karnych „w ciemno” (FIFA points).

Niniejszy moduł zastępuje to **warstwą prezentacji i regulaminu**, pokazując *kiedy* padają bramki i *jak* mecz się kończy. W przyszłości można podłączyć prawdopodobieństwa z `predict_match_proba()` jako parametry siły ataku/obrony.

## Struktura plików

```
world-cup-predictor-symulacja/
├── api.py
├── match_engine.py
├── sportsdb_client.py
├── teams_data.py
├── demo_terminal.py
├── requirements.txt
├── SPRAWOZDANIE.md
├── data/
│   ├── teams_cache.json
│   ├── matches_cache.json
│   └── matches_seed.json
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
└── tests/
    ├── test_match_engine.py
    └── test_sportsdb_matches.py
```
