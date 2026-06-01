# REQ-003: Aszinkron perzisztencia (Kafka → PostgreSQL)

| Mező | Érték |
|------|-------|
| **ID** | REQ-003 |
| **Státusz** | done |
| **Prioritás** | P0 |

## Leírás

A trading engine hot path nem blokkol adatbázis írásra. Események Kafka topicokba mennek; külön `db-writer` consumer írja PostgreSQL-be.

## Elfogadási kritériumok

- [x] Order/fill/error események Kafka produceren keresztül mennek
- [x] `db-writer` batch insert + indexelt táblák
- [x] Kafka leállásakor engine tovább fut bounded queue-val

## Kapcsolódó kód

- `backend/src/trading_platform/adapters/persistence/`
- `infra/migrations/`
