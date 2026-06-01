import { useEffect, useState } from "react";
import { API_URL } from "./api";

export default function App() {
  const [orders, setOrders] = useState<unknown[]>([]);
  const [errors, setErrors] = useState<unknown[]>([]);
  const [strategies, setStrategies] = useState<unknown[]>([]);
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [strategyId, setStrategyId] = useState("");
  const [backtestResult, setBacktestResult] = useState<unknown>(null);

  const load = () => {
    fetch(`${API_URL}/api/history/orders`).then((r) => r.json()).then(setOrders).catch(() => {});
    fetch(`${API_URL}/api/history/errors`).then((r) => r.json()).then(setErrors).catch(() => {});
    fetch(`${API_URL}/api/strategies`).then((r) => r.json()).then(setStrategies).catch(() => {});
  };

  useEffect(() => { load(); }, []);

  const saveCredentials = async () => {
    await fetch(`${API_URL}/api/credentials`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ exchange: "bitunix", label: "default", api_key: apiKey, api_secret: apiSecret }),
    });
    alert("Credentials saved");
  };

  const createStrategy = async () => {
    const res = await fetch(`${API_URL}/api/strategies`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Adaptive Ladder",
        strategy_type: "adaptive_ladder",
        mode: "dry_run",
        enabled: true,
        parameters: { max_active_symbols: 3, tick_interval_seconds: 5 },
        risk: { max_capital_usd: 100, min_investment_usd: 1, leverage_multiplier: 2, max_leverage_multiplier: 10 },
      }),
    });
    const data = await res.json();
    setStrategyId(data.id);
    load();
    alert("Strategy created: " + data.id);
  };

  const runBacktest = async () => {
    if (!strategyId) { alert("Create strategy first"); return; }
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
  };

  return (
    <div style={{ fontFamily: "system-ui", padding: 16, maxWidth: 960 }}>
      <h1>Analytics & Settings</h1>
      <section>
        <h2>API Keys</h2>
        <input placeholder="API Key" value={apiKey} onChange={(e) => setApiKey(e.target.value)} style={{ width: "100%", marginBottom: 8 }} />
        <input placeholder="Secret" type="password" value={apiSecret} onChange={(e) => setApiSecret(e.target.value)} style={{ width: "100%", marginBottom: 8 }} />
        <button onClick={saveCredentials}>Save</button>
      </section>
      <section>
        <h2>Strategy</h2>
        <button onClick={createStrategy}>Create Adaptive Ladder</button>
        <button onClick={runBacktest} style={{ marginLeft: 8 }}>Run backtest</button>
        {backtestResult && <pre>{JSON.stringify(backtestResult, null, 2)}</pre>}
      </section>
      <section>
        <h2>Strategies</h2>
        <pre>{JSON.stringify(strategies, null, 2)}</pre>
      </section>
      <section>
        <h2>Orders</h2>
        <pre>{JSON.stringify(orders, null, 2)}</pre>
      </section>
      <section>
        <h2>Errors</h2>
        <pre>{JSON.stringify(errors, null, 2)}</pre>
      </section>
    </div>
  );
}
