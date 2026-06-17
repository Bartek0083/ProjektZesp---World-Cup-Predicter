# World Cup Predictor — moduł symulacji

Rozszerzony moduł projektu zespołowego **World Cup Predictor** (Jakub Szych): symulacja minutowa, TheSportsDB, analiza Poissona, wykresy.

## Projekt zespołowy — gdzie co jest

| Co | Gdzie | Port |
|---|---|---|
| **Cała aplikacja** (ML, grupy, turniej, mecz) | [`../ProjektZesp---World-Cup-Predicter`](../ProjektZesp---World-Cup-Predicter) | **8011** |
| **Ten moduł** (TheSportsDB, API analityczne) | ten folder lub `ProjektZesp.../world-cup-predictor-symulacja/` | **8010** |

**GitHub:** [ProjektZesp---World-Cup-Predicter](https://github.com/Bartek0083/ProjektZesp---World-Cup-Predicter)  
**Sprawozdanie zespołowe:** [`SPRAWOZDANIE.md`](SPRAWOZDANIE.md)  
**Zespół:** Bartłomiej Muranowicz (ML, główna app) · Jakub Szych (moduł symulacji)

## Funkcje modułu

- Symulacja minutowa — tryb towarzyski i turniejowy (dogrywka, złota bramka, karne)
- Integracja **TheSportsDB** — mecze na dziś, nadchodzące, timeline
- Analiza przedmeczowa: xG, prawdopodobieństwa 1/X/2 (Poisson)
- Porównanie symulacji z rzeczywistym wynikiem z API
- 27 testów jednostkowych, wykresy do sprawozdania

## Szybki start (moduł)

```powershell
cd world-cup-predictor-symulacja
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn api:app --reload --port 8010
```

**http://127.0.0.1:8010/** · **http://127.0.0.1:8010/docs**

## Aplikacja główna zespołu (ML)

```powershell
cd ..\ProjektZesp---World-Cup-Predicter
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_server.py
```

**http://127.0.0.1:8011/**

## Testy

```powershell
python -m unittest discover -s tests -v
```

## Wykresy

```powershell
python generate_charts.py
```

Wynik: `docs/wykresy/*.png`

## Dokumentacja

- [`SPRAWOZDANIE.md`](SPRAWOZDANIE.md) — pełne sprawozdanie (zespołowe + techniczne)
- [`DEPLOY.md`](DEPLOY.md) — uruchomienie lokalne / Docker
- [`../ProjektZesp---World-Cup-Predicter/README.md`](../ProjektZesp---World-Cup-Predicter/README.md) — opis głównej aplikacji
