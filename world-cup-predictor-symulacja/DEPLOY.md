# Deploy i utrzymanie — Symulator meczu

## Uruchomienie lokalne (zalecane)

```powershell
cd "E:\6 semestr\world-cup-predictor-symulacja"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn api:app --reload --port 8010
```

Aplikacja: http://127.0.0.1:8010/  
Health check: `GET /health` → `{"status":"ok"}`

## Docker (własny serwer / maszyna)

```powershell
cd "E:\6 semestr\world-cup-predictor-symulacja"
docker build -t world-cup-symulacja .
docker run --rm -p 8080:8000 -e THESPORTSDB_API_KEY=123 world-cup-symulacja
```

Aplikacja: http://localhost:8080/

## Uwagi produkcyjne

| Temat | Opis |
|---|---|
| **Cache** | Pliki `data/*.json` zapisywane na dysku kontenera — po restarcie odświeżenie z API lub seeda |
| **Bezpieczeństwo** | Klucz API **nigdy** nie trafia do frontendu — tylko backend (`THESPORTSDB_API_KEY`) |
| **Limity API** | Free tier TheSportsDB: max 3 mecze/dzień, brak livescore v2 — aplikacja używa cache i seedów |

## Utrzymanie

### Po uruchomieniu

1. Sprawdź `GET /health` — usługa odpowiada `200`.
2. Otwórz stronę główną — UI ładuje listę drużyn.
3. Opcjonalnie: `POST /teams/refresh` i `POST /matches/refresh` po dłuższej przerwie.

### Po restarcie kontenera

- Cache drużyn i meczów może być pusty — pierwsze zapytanie pobierze dane z API lub użyje seeda (`data/matches_seed.json`, `teams_data.py`).

### Monitoring

- Logi Uvicorn na stdout (lokalnie lub w kontenerze Docker).
- Błędy API: endpointy zwracają `502` z opisem przy awarii TheSportsDB.

### Aktualizacja

1. Zmiany w repozytorium Git.
2. Przed commitem: `python -m unittest discover -s tests -v`
3. Przebudowa obrazu Docker przy deployu kontenerowym: `docker build -t world-cup-symulacja .`

## Koszt

| Pozycja | Koszt |
|---|---|
| TheSportsDB (klucz `123`) | 0 PLN |
| Uruchomienie lokalne / Docker | 0 PLN |
| **Łącznie** | **0 PLN** |
