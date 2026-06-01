# REQ-006: Frontend — élő vs előzmények szétválasztás

| Mező | Érték |
|------|-------|
| **ID** | REQ-006 |
| **Státusz** | done |
| **Prioritás** | P1 |

## Leírás

Egyetlen Vite/React alkalmazás, oldal szinten szétválasztva: az **Élő** oldal csak WebSocket + minimál REST (vészleállítás); a **Beállítások** és **Előzmények** oldalak REST/DB lekérdezéseket használnak.

## Elfogadási kritériumok

- [x] Élő oldal nem tölt history/backtest adatot mountkor
- [x] Előzmények oldal nem kötődik folyamatos WS streamhez
- [x] Egy dev/build port (5173) és egy Docker szolgáltatás (`frontend`)
- [x] Egységes, sötét trading UI (sidebar navigáció)

## Kapcsolódó kód

- `frontend/` — `LivePage`, `SettingsPage`, `HistoryPage`
