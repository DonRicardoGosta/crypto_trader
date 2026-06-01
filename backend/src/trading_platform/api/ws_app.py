from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from trading_platform.engine.realtime_hub import hub

ws_app = FastAPI(title="Realtime WS")


@ws_app.websocket("/realtime")
async def realtime_ws(websocket: WebSocket):
    await hub.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        await hub.disconnect(websocket)
