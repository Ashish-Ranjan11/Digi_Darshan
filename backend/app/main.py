from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import alerts, auth, bookings, crowd, dashboard, notifications, parking, scanner, slots, temples
from app.websocket_manager import manager

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Digii-Darshan Backend Running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "project": settings.PROJECT_NAME}


app.include_router(auth.router, prefix="/api")
app.include_router(temples.router, prefix="/api")
app.include_router(slots.router, prefix="/api")
app.include_router(bookings.router, prefix="/api")
app.include_router(crowd.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(parking.router, prefix="/api")
app.include_router(scanner.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")


@app.websocket("/ws/temples/{temple_id}")
async def temple_ws(websocket: WebSocket, temple_id: int):
    await manager.connect(temple_id, websocket)
    try:
        await websocket.send_json({"type": "connected", "temple_id": temple_id})
        while True:
            # Keep socket alive. Client may send ping messages.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(temple_id, websocket)
