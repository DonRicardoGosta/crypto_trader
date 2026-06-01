# REQ-002: Frontend-központú konfiguráció

| Mező | Érték |
|------|-------|
| **ID** | REQ-002 |
| **Státusz** | done |
| **Prioritás** | P0 |

## Leírás

API kulcsok, stratégia paraméterek és üzleti beállítások a frontend analytics UI-ból szerkeszthetők. Csak infrastruktúra (DB URL, Kafka, titkosítási master key) marad env-ben.

## Elfogadási kritériumok

- [ ] `POST/PUT /api/credentials` titkosítva tárolja a kulcsokat
- [ ] `PUT /api/strategies/{id}` frissíti a paramétereket
- [ ] Engine config cache-ből olvas, nem env-ből (kivéve infra)

## Kapcsolódó kód

- `backend/src/trading_platform/api/routes/config.py`
- `frontend-analytics/`
