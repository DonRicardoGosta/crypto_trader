import { useEffect, useState } from "react";
import { API_URL } from "../api";

export default function HistoryPage() {
  const [orders, setOrders] = useState<unknown[]>([]);
  const [errors, setErrors] = useState<unknown[]>([]);
  const [strategyId, setStrategyId] = useState("");
  const [backtestResult, setBacktestResult] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);

  const load = () => {
    fetch(`${API_URL}/api/history/orders`)
      .then((r) => r.json())
      .then(setOrders)
      .catch(() => setOrders([]));
    fetch(`${API_URL}/api/history/errors`)
      .then((r) => r.json())
      .then(setErrors)
      .catch(() => setErrors([]));
    fetch(`${API_URL}/api/strategies`)
      .then((r) => r.json())
      .then((list: { id: string }[]) => {
        if (Array.isArray(list) && list[0] && !strategyId) setStrategyId(list[0].id);
      })
      .catch(() => {});
  };

  useEffect(() => {
    load();
  }, []);

  const runBacktest = async () => {
    if (!strategyId) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/backtests`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          strategy_id: strategyId,
          start_ts: new Date(Date.now() - 7 * 86400000).toISOString(),
          end_ts: new Date().toISOString(),
          symbols: ["BTCUSDT"],
          slippage_bps: 0,
        }),
      });
      setBacktestResult(await res.json());
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <header className="page-header">
        <h1>Előzmények</h1>
        <p className="subtitle">Rendelések, hibák és backtest — adatbázisból (lassabb, részletes).</p>
      </header>

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h2>Backtest</h2>
        <div className="form-row">
          <label>Strategy ID</label>
          <input value={strategyId} onChange={(e) => setStrategyId(e.target.value)} className="mono" />
        </div>
        <div className="form-actions">
          <button type="button" className="btn-primary" onClick={runBacktest} disabled={loading || !strategyId}>
            {loading ? "Fut…" : "Backtest indítása (7 nap)"}
          </button>
          <button type="button" className="btn-secondary" onClick={load}>
            Frissítés
          </button>
        </div>
        {backtestResult != null && (
          <pre className="pre-block" style={{ marginTop: "1rem" }}>
            {JSON.stringify(backtestResult, null, 2)}
          </pre>
        )}
      </div>

      <div className="grid-2">
        <div className="card">
          <h2>Orders ({Array.isArray(orders) ? orders.length : 0})</h2>
          <pre className="pre-block">{JSON.stringify(orders, null, 2)}</pre>
        </div>
        <div className="card">
          <h2>Hibák ({Array.isArray(errors) ? errors.length : 0})</h2>
          <pre className="pre-block">{JSON.stringify(errors, null, 2)}</pre>
        </div>
      </div>

      <style>{`
        .page-header { margin-bottom: 1.5rem; }
        .page-header h1 { font-size: 1.5rem; }
        .subtitle { color: var(--text-muted); font-size: 0.9rem; margin-top: 0.25rem; }
      `}</style>
    </div>
  );
}
