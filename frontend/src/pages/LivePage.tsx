import { useEffect, useState } from "react";
import { API_URL, WS_URL } from "../api";

type WsEvent = { type: string; payload: Record<string, unknown> };

export default function LivePage() {
  const [events, setEvents] = useState<WsEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [stopped, setStopped] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data) as WsEvent;
        if (msg.type === "emergency_stop") setStopped(!!msg.payload?.active);
        setEvents((prev) => [msg, ...prev].slice(0, 80));
      } catch {
        /* ignore */
      }
    };
    const ping = setInterval(() => {
      if (ws.readyState === 1) ws.send("ping");
    }, 15000);
    return () => {
      clearInterval(ping);
      ws.close();
    };
  }, []);

  const emergencyStop = async () => {
    await fetch(`${API_URL}/api/control/emergency-stop`, { method: "POST" });
    setStopped(true);
  };

  const resetStop = async () => {
    await fetch(`${API_URL}/api/control/emergency-stop/reset`, { method: "POST" });
    setStopped(false);
  };

  return (
    <div>
      <header className="page-header">
        <div>
          <h1>Élő működés</h1>
          <p className="subtitle">WebSocket stream — gyors frissítés, nincs lassú DB lekérdezés ezen az oldalon.</p>
        </div>
        <div className="status-row">
          <span className={`badge ${connected ? "badge-ok" : "badge-off"}`}>
            {connected ? "● WS csatlakozva" : "○ WS nincs"}
          </span>
          <span className={`badge ${stopped ? "badge-danger" : "badge-ok"}`}>
            {stopped ? "Vészleállítva" : "Aktív"}
          </span>
        </div>
      </header>

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h2>Vezérlés</h2>
        <div className="form-actions">
          <button type="button" className="btn-danger" onClick={emergencyStop} disabled={stopped}>
            Vészleállítás
          </button>
          <button type="button" className="btn-secondary" onClick={resetStop} disabled={!stopped}>
            Leállítás feloldása
          </button>
        </div>
      </div>

      <div className="card">
        <h2>Események</h2>
        {events.length === 0 ? (
          <p className="subtitle">Várakozás eseményekre…</p>
        ) : (
          <ul className="event-list">
            {events.map((ev, i) => (
              <li key={i}>
                <span className="event-type">{ev.type}</span>
                <span className="mono event-payload">
                  {JSON.stringify(ev.payload).slice(0, 160)}
                  {(JSON.stringify(ev.payload).length ?? 0) > 160 ? "…" : ""}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <style>{`
        .page-header {
          display: flex;
          flex-wrap: wrap;
          justify-content: space-between;
          align-items: flex-start;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }
        .page-header h1 { font-size: 1.5rem; font-weight: 700; }
        .subtitle { color: var(--text-muted); font-size: 0.9rem; margin-top: 0.25rem; }
        .status-row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
        .event-list { list-style: none; display: flex; flex-direction: column; gap: 0.5rem; }
        .event-list li {
          display: grid;
          grid-template-columns: 120px 1fr;
          gap: 0.75rem;
          padding: 0.65rem 0.75rem;
          background: var(--bg);
          border-radius: 8px;
          border: 1px solid var(--border);
          align-items: start;
        }
        .event-type {
          font-weight: 600;
          font-size: 0.8rem;
          color: var(--accent);
        }
        .event-payload { color: var(--text-muted); word-break: break-all; }
      `}</style>
    </div>
  );
}
