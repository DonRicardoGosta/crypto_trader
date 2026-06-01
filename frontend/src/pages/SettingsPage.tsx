import { useEffect, useState } from "react";
import { API_URL } from "../api";

type Strategy = {
  id: string;
  name: string;
  mode: string;
  enabled: boolean;
  strategy_type: string;
};

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [strategyId, setStrategyId] = useState("");
  const [msg, setMsg] = useState("");

  const load = () => {
    fetch(`${API_URL}/api/strategies`)
      .then((r) => r.json())
      .then((data) => setStrategies(Array.isArray(data) ? data : []))
      .catch(() => setStrategies([]));
  };

  useEffect(() => {
    load();
  }, []);

  const saveCredentials = async () => {
    setMsg("");
    const res = await fetch(`${API_URL}/api/credentials`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        exchange: "bitunix",
        label: "default",
        api_key: apiKey,
        api_secret: apiSecret,
      }),
    });
    setMsg(res.ok ? "API kulcsok elmentve (titkosítva)." : "Hiba a mentéskor.");
  };

  const createStrategy = async () => {
    setMsg("");
    const res = await fetch(`${API_URL}/api/strategies`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Adaptive Ladder",
        strategy_type: "adaptive_ladder",
        mode: "dry_run",
        enabled: true,
        parameters: { max_active_symbols: 3, tick_interval_seconds: 5 },
        risk: {
          max_capital_usd: 100,
          min_investment_usd: 1,
          leverage_multiplier: 2,
          max_leverage_multiplier: 10,
        },
      }),
    });
    const data = await res.json();
    if (data.id) {
      setStrategyId(data.id);
      setMsg(`Stratégia létrehozva: ${data.id}`);
      load();
    } else setMsg("Stratégia létrehozása sikertelen.");
  };

  const setMode = async (mode: string) => {
    if (!strategyId) {
      setMsg("Előbb hozz létre vagy válassz stratégiát.");
      return;
    }
    await fetch(`${API_URL}/api/control/strategies/${strategyId}/mode/${mode}`, { method: "POST" });
    setMsg(`Mód: ${mode}`);
    load();
  };

  return (
    <div>
      <header className="page-header">
        <h1>Beállítások</h1>
        <p className="subtitle">API kulcsok és stratégia — minden itt szerkeszthető, env fájl nélkül.</p>
      </header>

      {msg && <div className="toast">{msg}</div>}

      <div className="grid-2" style={{ marginBottom: "1rem" }}>
        <div className="card">
          <h2>Bitunix API</h2>
          <div className="form-row">
            <label>API Key</label>
            <input value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder="api-key" />
          </div>
          <div className="form-row">
            <label>API Secret</label>
            <input
              type="password"
              value={apiSecret}
              onChange={(e) => setApiSecret(e.target.value)}
              placeholder="••••••••"
            />
          </div>
          <div className="form-actions">
            <button type="button" className="btn-primary" onClick={saveCredentials}>
              Mentés
            </button>
          </div>
        </div>

        <div className="card">
          <h2>Stratégia</h2>
          <p className="subtitle" style={{ marginBottom: "1rem" }}>
            Első stratégia: Adaptive Ladder (automatikus coin, lépcsők).
          </p>
          <div className="form-actions">
            <button type="button" className="btn-primary" onClick={createStrategy}>
              Adaptive Ladder létrehozása
            </button>
            <button type="button" className="btn-secondary" onClick={() => setMode("dry_run")}>
              Dry-run
            </button>
            <button type="button" className="btn-secondary" onClick={() => setMode("live")}>
              Live
            </button>
          </div>
          {strategyId && (
            <p className="mono" style={{ marginTop: "1rem", color: "var(--text-muted)" }}>
              Aktív ID: {strategyId}
            </p>
          )}
        </div>
      </div>

      <div className="card">
        <h2>Stratégiák listája</h2>
        {strategies.length === 0 ? (
          <p className="subtitle">Még nincs stratégia.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Név</th>
                <th>Típus</th>
                <th>Mód</th>
                <th>Állapot</th>
              </tr>
            </thead>
            <tbody>
              {strategies.map((s) => (
                <tr
                  key={s.id}
                  onClick={() => setStrategyId(s.id)}
                  className={strategyId === s.id ? "selected" : ""}
                >
                  <td>{s.name}</td>
                  <td className="mono">{s.strategy_type}</td>
                  <td>{s.mode}</td>
                  <td>{s.enabled ? "bekapcsolva" : "ki"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <style>{`
        .page-header { margin-bottom: 1.5rem; }
        .page-header h1 { font-size: 1.5rem; }
        .subtitle { color: var(--text-muted); font-size: 0.9rem; margin-top: 0.25rem; }
        .toast {
          background: rgba(61, 255, 168, 0.1);
          border: 1px solid var(--accent-dim);
          color: var(--accent);
          padding: 0.75rem 1rem;
          border-radius: 8px;
          margin-bottom: 1rem;
          font-size: 0.9rem;
        }
        .data-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
        .data-table th {
          text-align: left;
          color: var(--text-muted);
          font-size: 0.7rem;
          text-transform: uppercase;
          padding: 0.5rem 0.75rem;
          border-bottom: 1px solid var(--border);
        }
        .data-table td { padding: 0.65rem 0.75rem; border-bottom: 1px solid var(--border); }
        .data-table tbody tr { cursor: pointer; }
        .data-table tbody tr:hover { background: rgba(255,255,255,0.02); }
        .data-table tr.selected { background: rgba(61, 255, 168, 0.06); }
      `}</style>
    </div>
  );
}
