# REQ-007: Audit és hibák naplózása

| Mező | Érték |
|------|-------|
| **ID** | REQ-007 |
| **Státusz** | done |
| **Prioritás** | P0 |

## Leírás

Minden fontos esemény (trade, config, mode switch) és hiba (exchange, engine, API) végül PostgreSQL `events` / `errors` táblában landol.

## Elfogadási kritériumok

- [x] Exchange HTTP/WS hibák → `trading.errors` → `errors` tábla
- [x] Config változás → `trading.audit` → `events` tábla
- [x] Indexek: `(source, ts)`, `(event_type, ts)`, `(severity, ts)`

## Kapcsolódó kód

- `backend/src/trading_platform/adapters/persistence/db_writer.py`
