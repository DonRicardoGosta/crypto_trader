# REQ-001: Egységes execution módok

| Mező | Érték |
|------|-------|
| **ID** | REQ-001 |
| **Státusz** | in_progress |
| **Prioritás** | P0 |

## Leírás

Live, dry-run és backtest ugyanazt a stratégia- és risk-kódot futtatja. A különbség csak a port adapterekben van (`ExecutionPort`, `MarketDataPort`, `ClockPort`).

## Elfogadási kritériumok

- [ ] Stratégia nem hív közvetlenül Bitunix REST-et vagy SQL-t
- [ ] `BitunixLiveExecution`, `BitunixDryRunExecution`, `BacktestExecution` implementálja `ExecutionPort`-ot
- [ ] Dry-run és backtest ugyanazt a `SimulatedLedger`-t használja
- [ ] Ugyanazokkal a paraméterekkel backtest és dry-run irány/fill száma egyezik (slippage nélkül)

## Kapcsolódó kód

- `backend/src/trading_platform/core/ports.py`
- `backend/src/trading_platform/adapters/execution/`
