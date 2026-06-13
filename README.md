# World Cup Predictor

Jedna aplikacja FastAPI ze statycznym frontendem do predykcji meczow, symulacji live, grup i turnieju.

## Uruchomienie lokalne

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python run_server.py
```

Adres aplikacji:

```text
http://127.0.0.1:8011/
```

Dokumentacja API:

```text
http://127.0.0.1:8011/docs
```

Pierwsze wywolanie endpointu trenuje model i zapisuje go do:

```text
artifacts/world_cup_model.joblib
```

## Endpointy

- `GET /health`
- `GET /teams`
- `GET /group-matches`
- `POST /predict-match`
- `POST /simulate-match`
- `POST /simulate-group-stage`
- `POST /simulate-world-cup`

Symulacja meczu jest zintegrowana w glownym backendzie. Nie trzeba uruchamiac osobnego serwera ani drugiego portu.
