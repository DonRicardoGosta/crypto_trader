import { useEffect, useState } from "react";
import { WS_URL } from "./api";

type Event = { type: string; payload: Record<string, unknown> };

export default function App() {
  const [events, setEvents] = useState<Event[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        setEvents((prev) => [msg, ...prev].slice(0, 50));
      } catch { /* ignore */ }
    };
    const ping = setInterval(() => ws.readyState === 1 && ws.send("ping"), 15000);
    return () => { clearInterval(ping); ws.close(); };
  }, []);

  return (
    <div style={{ fontFamily: "system-ui", padding: 16 }}>
      <h1>Realtime Dashboard</h1>
      <p>Status: {connected ? "Connected" : "Disconnected"}</p>
      <p><small>WebSocket only — no DB queries on this app.</small></p>
      <ul>
        {events.map((ev, i) => (
          <li key={i}><strong>{ev.type}</strong>: {JSON.stringify(ev.payload).slice(0, 120)}</li>
        ))}
      </ul>
    </div>
  );
}
