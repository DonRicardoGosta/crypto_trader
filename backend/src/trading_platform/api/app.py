from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from trading_platform.api.routes import backtests, config, control, history, strategies

app = FastAPI(title="Trading Platform API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(backtests.router, prefix="/api/backtests", tags=["backtests"])
app.include_router(control.router, prefix="/api/control", tags=["control"])


@app.get("/health")
async def health():
    return {"status": "ok"}
