# World Cup Predictor

Backend FastAPI + statyczny frontend do predykcji meczow i symulacji turnieju.

## Uruchomienie lokalne

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python -m uvicorn api:app --reload
```

Frontend:

```text
http://127.0.0.1:8000/
```

Dokumentacja API:

```text
http://127.0.0.1:8000/docs
```

Pierwsze wywolanie endpointu trenuje model i zapisuje go do:

```text
artifacts/world_cup_model.joblib
```

## Endpointy

- `GET /teams`
- `GET /group-matches`
- `POST /predict-match`
- `POST /simulate-group-stage`
- `POST /simulate-world-cup`
