# Sådan lægger du platformen op på Render (gratis)

## Trin 1 – GitHub
1. Gå til https://github.com og log ind (eller opret konto)
2. Klik **New repository**
3. Navn f.eks. `trading-bot-platform`
4. Vælg **Public**
5. Klik **Create repository**

## Trin 2 – Upload koden
Du kan enten:
- Downloade zip’en jeg gav dig og uploade filerne manuelt via GitHub’s “uploading an existing file”
- Eller bruge Git hvis du kender det

## Trin 3 – Opret Web Service på Render
1. Gå til https://render.com og log ind med GitHub
2. Klik **New +** → **Web Service**
3. Vælg dit repository `trading-bot-platform`
4. Udfyld sådan her:

| Felt              | Værdi                                      |
|-------------------|--------------------------------------------|
| Name              | trading-bot-platform                       |
| Region            | Frankfurt (eller tættest på dig)           |
| Root Directory    | `backend`                                  |
| Runtime           | Python                                     |
| Build Command     | `pip install -r requirements.txt`          |
| Start Command     | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type     | Free                                       |

5. Klik **Create Web Service**

## Trin 4 – Vent
Render bygger projektet (tager 2–5 minutter).  
Når den er grøn, får du et link som:

`https://trading-bot-platform-xxxx.onrender.com`

## Trin 5 – Test
Åbn linket → du skal se login-siden.  
Opret en konto og test.

---

### Vigtigt om gratis plan
- SQLite-databasen nulstilles hvis Render genstarter servicen (kan ske efter inaktivitet).
- Til rigtig brug anbefales det senere at tilføje en gratis PostgreSQL database på Render.

### Brug for hjælp?
Sig bare til hvis du sidder fast på et trin, så guider jeg dig videre.
