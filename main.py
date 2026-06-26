from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db.database import connect_db, close_db
from core.config import settings
from routers import notificaciones_push #noti


from routers import (
    usuarios,
    horarios,
    cumplimiento,
    despensa,
    recetas,
    lista_compras,
    presupuesto,
    notificaciones,
    progreso,
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Lifespan (reemplaza on_event deprecated) ───────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="API — Organizador de Alimentación Diaria",
    description="""
Backend REST para la app de organización de alimentación diaria.
Autenticación via Firebase Auth (Bearer token).
Base de datos: MongoDB.
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS (permite peticiones desde la app Flutter) ─────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # En producción: especifica el dominio de la app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(usuarios.router,       prefix=PREFIX)
app.include_router(horarios.router,       prefix=PREFIX)
app.include_router(cumplimiento.router,   prefix=PREFIX)
app.include_router(despensa.router,       prefix=PREFIX)
app.include_router(recetas.router,        prefix=PREFIX)
app.include_router(lista_compras.router,  prefix=PREFIX)
app.include_router(presupuesto.router,    prefix=PREFIX)
app.include_router(notificaciones.router, prefix=PREFIX)
app.include_router(progreso.router,       prefix=PREFIX)

app.include_router(notificaciones_push.router, prefix=PREFIX)

# ── Health check ───────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "app":    "Organizador de Alimentación Diaria API",
        "version": "1.0.0",
        "docs":   "/docs",
    }
