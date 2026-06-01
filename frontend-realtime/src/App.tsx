import { useEffect, useState } from "react";
import { API_URL, WS_URL } from "./api";

type Event = { type: string; payload: Record<string, unknown> };

export default function App() {
  const [events, setEvents] = useState<Event[]>([]);
  const [connected, setConnected] = useState(false);
  const [stopped, setStopped] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.type === "emergency_stop") setStopped(!!msg.payload?.active);
        setEvents((prev) => [msg, ...prev].slice(0, 50));
      } catch { /* ignore */ }
    };
    const ping = setInterval(() => ws.readyState === 1 && ws.send("ping"), 15000);
    return () => { clearInterval(ping); ws.close(); };
  }, []);

  const emergencyStop = async () => {
    await fetch(`${API_URL}/api/control/emergency-stop`, { method: "POST" });
    setStopped(true);
  };

  const resetStop = async () => {
    await fetch(`${API_URL}/api/control/emergency-stop/reset`, { method: "POST" });
    setStopped(false);
  };

  const setDryRun = async (id: string) => {
    await fetch(`${API_URL}/api/control/strategies/${id}/mode/dry_run`, { method: "POST" });
  };

  return (
    <div style={{ fontFamily: "system-ui", padding: 16 }}>
      <h1>Realtime Dashboard</h1>
      <p>WS: {connected ? "Connected" : "Disconnected"} | Emergency: {stopped ? "STOPPED" : "active"}</p>
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button onClick={emergencyStop} disabled={stopped}>Emergency stop</button>
        <button onClick={resetStop} disabled={!stopped}>Reset stop</button>
        <button onClick={() => setDryRun("00000000-0000-0000-0000-000000000001")}>Set dry_run (demo)</button>
      </div>
      <p><small>No DB queries — WebSocket stream only.</small></p>
      <ul>
        {events.map((ev, i) => (
          <li key={i}><strong>{ev.type}</strong>: {JSON.stringify(ev.payload).slice(0, 120)}</li>
        ))}
      </ul>
    </div>
  );
}
