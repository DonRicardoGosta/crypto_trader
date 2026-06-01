# REQ-004: Risk limitek stratégiánként

| Mező | Érték |
|------|-------|
| **ID** | REQ-004 |
| **Státusz** | done |
| **Prioritás** | P0 |

## Leírás

`max_capital_usd`, `min_investment_usd` (fix stake), `leverage_multiplier` (exposure). Margin hiba esetén automatikus szorzó emelés max-ig.

## Elfogadási kritériumok

- [ ] `RiskEngine.propose_order` elutasít ha túllépi a max tőkét
- [ ] `min_investment_usd` nem változik szorzó emeléskor
- [ ] Insufficient margin → leverage +1, retry, majd `leverage_bump_exhausted` esemény

## Kapcsolódó kód

- `backend/src/trading_platform/risk/engine.py`
