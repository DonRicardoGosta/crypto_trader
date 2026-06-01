import { useEffect, useState } from "react";
import { API_URL } from "./api";

export default function App() {
  const [orders, setOrders] = useState<unknown[]>([]);
  const [errors, setErrors] = useState<unknown[]>([]);
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");

  useEffect(() => {
    fetch(`${API_URL}/api/history/orders`).then((r) => r.json()).then(setOrders).catch(() => {});
    fetch(`${API_URL}/api/history/errors`).then((r) => r.json()).then(setErrors).catch(() => {});
  }, []);

  const saveCredentials = async () => {
    await fetch(`${API_URL}/api/credentials`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ exchange: "bitunix", label: "default", api_key: apiKey, api_secret: apiSecret }),
    });
    alert("Credentials saved (encrypted in DB)");
  };

  const createStrategy = async () => {
    await fetch(`${API_URL}/api/strategies`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Adaptive Ladder",
        strategy_type: "adaptive_ladder",
        mode: "dry_run",
        enabled: true,
        parameters: { max_active_symbols: 3 },
        risk: { max_capital_usd: 100, min_investment_usd: 1, leverage_multiplier: 2, max_leverage_multiplier: 10 },
      }),
    });
    alert("Strategy created");
  };

  return (
    <div style={{ fontFamily: "system-ui", padding: 16, maxWidth: 900 }}>
      <h1>Analytics & Settings</h1>
      <section>
        <h2>API Keys (Bitunix)</h2>
        <input placeholder="API Key" value={apiKey} onChange={(e) => setApiKey(e.target.value)} style={{ width: "100%", marginBottom: 8 }} />
        <input placeholder="API Secret" type="password" value={apiSecret} onChange={(e) => setApiSecret(e.target.value)} style={{ width: "100%", marginBottom: 8 }} />
        <button onClick={saveCredentials}>Save credentials</button>
      </section>
      <section>
        <h2>Strategy</h2>
        <button onClick={createStrategy}>Create default Adaptive Ladder</button>
      </section>
      <section>
        <h2>Order history</h2>
        <pre>{JSON.stringify(orders, null, 2)}</pre>
      </section>
      <section>
        <h2>Errors</h2>
        <pre>{JSON.stringify(errors, null, 2)}</pre>
      </section>
    </div>
  );
}
