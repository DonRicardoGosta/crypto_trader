# REQ-003: Aszinkron perzisztencia (Kafka → PostgreSQL)

| Mező | Érték |
|------|-------|
| **ID** | REQ-003 |
| **Státusz** | in_progress |
| **Prioritás** | P0 |

## Leírás

A trading engine hot path nem blokkol adatbázis írásra. Események Kafka topicokba mennek; külön `db-writer` consumer írja PostgreSQL-be.

## Elfogadási kritériumok

- [ ] Order/fill/error események Kafka produceren keresztül mennek
- [ ] `db-writer` batch insert + indexelt táblák
- [ ] Kafka leállásakor engine tovább fut bounded queue-val

## Kapcsolódó kód

- `backend/src/trading_platform/adapters/persistence/`
- `infra/migrations/`
