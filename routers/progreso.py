from fastapi import APIRouter, Depends
from db.database import col_cumplimiento, col_presupuesto
from db.helpers import serialize
from core.auth import get_current_user
from datetime import datetime, date, timedelta

router = APIRouter(prefix="/progreso", tags=["Progreso"])


# ── GET /progreso/semanal — Cumplimiento de los últimos 7 días ─────────────
@router.get("/semanal")
async def progreso_semanal(user: dict = Depends(get_current_user)):
    hoy    = date.today()
    inicio = datetime(hoy.year, hoy.month, hoy.day) - timedelta(days=6)

    docs = await col_cumplimiento().find({
        "uid": user["uid"],
        "fecha": {"$gte": inicio}
    }).to_list(length=500)

    # Agrupar por día
    resumen = {}
    for i in range(7):
        dia = (inicio + timedelta(days=i)).date()
        resumen[str(dia)] = {"total": 0, "realizados": 0, "porcentaje": 0.0}

    for d in docs:
        dia_str = str(d["fecha"].date())
        if dia_str in resumen:
            resumen[dia_str]["total"] += 1
            if d.get("realizado"):
                resumen[dia_str]["realizados"] += 1

    for dia_str, val in resumen.items():
        if val["total"] > 0:
            val["porcentaje"] = round(val["realizados"] / val["total"] * 100, 1)

    return {"semana": resumen}


# ── GET /progreso/hoy — Resumen del día actual ─────────────────────────────
@router.get("/hoy")
async def progreso_hoy(user: dict = Depends(get_current_user)):
    hoy    = date.today()
    inicio = datetime(hoy.year, hoy.month, hoy.day, 0, 0, 0)
    fin    = datetime(hoy.year, hoy.month, hoy.day, 23, 59, 59)

    docs = await col_cumplimiento().find({
        "uid": user["uid"],
        "fecha": {"$gte": inicio, "$lte": fin}
    }).to_list(length=50)

    total     = len(docs)
    realizados = sum(1 for d in docs if d.get("realizado"))
    porcentaje = round(realizados / total * 100, 1) if total > 0 else 0.0

    presupuesto = await col_presupuesto().find_one({"uid": user["uid"]})
    presup_info = None
    if presupuesto:
        presup_info = {
            "limite":     presupuesto.get("limite", 0),
            "gastado":    presupuesto.get("gastado", 0),
            "restante":   presupuesto.get("limite", 0) - presupuesto.get("gastado", 0),
            "porcentaje": round(
                presupuesto.get("gastado", 0) / presupuesto.get("limite", 1) * 100, 1
            )
        }

    return {
        "fecha":       str(hoy),
        "total":       total,
        "realizados":  realizados,
        "porcentaje":  porcentaje,
        "presupuesto": presup_info,
    }


# ── GET /progreso/mensual — Resumen del mes actual ─────────────────────────
@router.get("/mensual")
async def progreso_mensual(user: dict = Depends(get_current_user)):
    hoy    = date.today()
    inicio = datetime(hoy.year, hoy.month, 1)

    docs = await col_cumplimiento().find({
        "uid": user["uid"],
        "fecha": {"$gte": inicio}
    }).to_list(length=1000)

    total      = len(docs)
    realizados = sum(1 for d in docs if d.get("realizado"))
    porcentaje = round(realizados / total * 100, 1) if total > 0 else 0.0

    # Días con cumplimiento 100%
    por_dia: dict = {}
    for d in docs:
        dia = str(d["fecha"].date())
        if dia not in por_dia:
            por_dia[dia] = {"total": 0, "realizados": 0}
        por_dia[dia]["total"] += 1
        if d.get("realizado"):
            por_dia[dia]["realizados"] += 1

    dias_perfectos = sum(
        1 for v in por_dia.values()
        if v["total"] > 0 and v["realizados"] == v["total"]
    )

    return {
        "mes":            f"{hoy.year}-{hoy.month:02d}",
        "total":          total,
        "realizados":     realizados,
        "porcentaje":     porcentaje,
        "dias_perfectos": dias_perfectos,
        "dias_registrados": len(por_dia),
    }
