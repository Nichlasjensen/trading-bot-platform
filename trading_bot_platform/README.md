# Trading Bot Platform – Multi-User med Individuel Aggressivitet

Komplet MVP af en trading bot platform hvor hver bruger har sin egen konto, kan indstille hvor aggressiv botten skal køre, og styre sin egen bot.

## Funktioner

- Bruger-registrering & login (JWT)
- Individuel aggressivitets-slider (1–10)
- Paper-trading (sikkert default)
- Modulær strategi (nem at udskifte)
- Start/stop bot pr. bruger
- Live status, trades og PnL
- Simpel web-dashboard

## Hurtig start

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend (valgfrit)

Åbn `frontend/index.html` i browseren (eller kør en simpel server).

### 3. Test-bruger

Efter start kan du registrere dig via `/docs` eller frontend.

## Aggressivitet

| Niveau | Position size | Stop-loss | Take-profit | Max trades/dag |
|--------|---------------|-----------|-------------|----------------|
| 1–3    | Lav           | Tæt       | Lav         | Få             |
| 4–6    | Medium        | Normal    | Medium      | Medium         |
| 7–10   | Høj           | Bredere   | Høj         | Flere          |

## Strategi

Standard-strategien er en simpel EMA-crossover (9/21) på 15m candles.
Du kan erstatte den i `backend/app/strategies/ema_crossover.py`.

## Vigtigt

- Dette er **paper-trading** som default. Rigtige penge kræver at du selv tilføjer live-trading og håndterer API-nøgler sikkert.
- Trading indebærer risiko for tab.
- Kør aldrig med rigtige penge før du har testet grundigt.

## Struktur

```
trading_bot_platform/
├── backend/
│   ├── app/
│   │   ├── api/          # Routes
│   │   ├── core/         # Config, security, database
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic + bot engine
│   │   ├── strategies/   # Trading strategies
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   └── index.html
└── README.md
```
