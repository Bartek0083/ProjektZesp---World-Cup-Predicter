# Deploy — Symulator meczu

## Render.com (zalecane, darmowy plan)

1. Wgraj folder `world-cup-predictor-symulacja` na GitHub (osobne repo lub podfolder).
2. Wejdź na [render.com](https://render.com) → **New** → **Blueprint** (lub **Web Service**).
3. Połącz repozytorium, wskaż plik `render.yaml` (Blueprint) albo:
   - **Runtime:** Docker
   - **Root directory:** `world-cup-predictor-symulacja` (jeśli repo nadrzędne)
4. Zmienne środowiskowe:
   - `THESPORTSDB_API_KEY` = `123` (lub własny klucz premium)
5. Deploy → po kilku minutach URL typu `https://world-cup-symulacja.onrender.com`

Health check: `GET /health` → `{"status":"ok"}`

## Docker (lokalnie lub własny serwer)

```powershell
cd "E:\6 semestr\world-cup-predictor-symulacja"
docker build -t world-cup-symulacja .
docker run --rm -p 8080:8000 -e THESPORTSDB_API_KEY=123 world-cup-symulacja
```

Aplikacja: http://localhost:8080/

## Uwagi produkcyjne

- Cache meczów/drużyn (`data/*.json`) jest zapisywany na dysku kontenera — po restarcie Render odświeży z API lub seeda.
- Free tier Render usypia usługę po ~15 min bez ruchu — pierwsze wejście może trwać ~30 s.
- Klucz API **nigdy** nie trafia do frontendu — tylko backend.
