# REQ-005: Adaptive Ladder stratégia

| Mező | Érték |
|------|-------|
| **ID** | REQ-005 |
| **Státusz** | in_progress |
| **Prioritás** | P0 |

## Leírás

Automatikus coin discovery, lépcsőzetes pozíciók (több leg ugyanarra a symbolra, long/short), risk management. **Piaci profit nem garantálható** — a stratégia risk szabályokat követ.

## Elfogadási kritériumok

- [ ] Top N coin volume/volatility alapján
- [ ] Több párhuzamos pozíció ugyanazon symbolon
- [ ] Leverage bump margin hibára
- [ ] Trailing stop / max drawdown per symbol

## Kapcsolódó kód

- `backend/src/trading_platform/strategies/adaptive_ladder/`
