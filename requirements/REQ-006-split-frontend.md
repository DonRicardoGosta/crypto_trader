# REQ-006: Frontend szétválasztás (WS vs DB)

| Mező | Érték |
|------|-------|
| **ID** | REQ-006 |
| **Státusz** | in_progress |
| **Prioritás** | P1 |

## Leírás

Két külön Vite alkalmazás: realtime csak WebSocket + minimál REST; analytics csak REST/DB lekérdezések.

## Elfogadási kritériumok

- [ ] `frontend-realtime` nem importál history/query modulokat
- [ ] `frontend-analytics` nem kötődik live WS streamhez
- [ ] Külön dev portok (5173, 5174)

## Kapcsolódó kód

- `frontend-realtime/`
- `frontend-analytics/`
