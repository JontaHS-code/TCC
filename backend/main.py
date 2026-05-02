# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import gastos, politicos, ranking, chat, politicos_detalhes
from routes.analytics import router as analytics_router
from scheduler import iniciar_scheduler

# Cria as tabelas no banco (se não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Brasil Transparente API", version="1.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gastos.router)
app.include_router(politicos.router)
app.include_router(ranking.router)
app.include_router(chat.router)
app.include_router(politicos_detalhes.router)
app.include_router(analytics_router)

@app.on_event("startup")
def start_scheduler():
    iniciar_scheduler()

@app.get("/")
def root():
    return {"message": "API Brasil Transparente - Transparência de Gastos Públicos"}