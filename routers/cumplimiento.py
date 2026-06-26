from fastapi import APIRouter, Depends, HTTPException, status, Query
from db.database import col_cumplimiento
from db.helpers import serialize, serialize_list
from schemas.schemas import CumplimientoCreate, CumplimientoUpdate, CumplimientoOut
from core.auth import get_current_user
from bson import ObjectId
from datetime import datetime, date
# fix missing import
from typing import Optional

router = APIRouter(prefix="/cumplimiento", tags=["Cumplimiento"])


# ── POST /cumplimiento — Registrar cumplimiento ─────────────────────────────
@router.post("/", response_model=CumplimientoOut, status_code=status.HTTP_201_CREATED)
async def registrar_cumplimiento(
    data: CumplimientoCreate,
    user: dict = Depends(get_current_user)
):
    doc = data.model_dump()
    doc["uid"] = user["uid"]
    result = await col_cumplimiento().insert_one(doc)
    created = await col_cumplimiento().find_one({"_id": result.inserted_id})
    return serialize(created)


# ── GET /cumplimiento — Listar registros (filtro por fecha opcional) ─────────
@router.get("/", response_model=list[CumplimientoOut])
async def listar_cumplimiento(
    user: dict = Depends(get_current_user),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
):
    filtro: dict = {"uid": user["uid"]}
    if desde or hasta:
        filtro["fecha"] = {}
        if desde:
            filtro["fecha"]["$gte"] = desde
        if hasta:
            filtro["fecha"]["$lte"] = hasta

    docs = await col_cumplimiento().find(filtro)\
        .sort("fecha", -1).to_list(length=200)
    return serialize_list(docs)


# ── GET /cumplimiento/hoy — Registros de hoy ───────────────────────────────
@router.get("/hoy", response_model=list[CumplimientoOut])
async def cumplimiento_hoy(user: dict = Depends(get_current_user)):
    hoy = date.today()
    inicio = datetime(hoy.year, hoy.month, hoy.day, 0, 0, 0)
    fin    = datetime(hoy.year, hoy.month, hoy.day, 23, 59, 59)
    docs = await col_cumplimiento().find({
        "uid": user["uid"],
        "fecha": {"$gte": inicio, "$lte": fin}
    }).to_list(length=50)
    return serialize_list(docs)


# ── GET /cumplimiento/{id} — Obtener un registro ────────────────────────────
@router.get("/{cumplimiento_id}", response_model=CumplimientoOut)
async def obtener_cumplimiento(
    cumplimiento_id: str,
    user: dict = Depends(get_current_user)
):
    doc = await col_cumplimiento().find_one(
        {"_id": ObjectId(cumplimiento_id), "uid": user["uid"]}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return serialize(doc)


# ── PUT /cumplimiento/{id} — Actualizar (marcar como realizado/no realizado) ─
@router.put("/{cumplimiento_id}", response_model=CumplimientoOut)
async def actualizar_cumplimiento(
    cumplimiento_id: str,
    data: CumplimientoUpdate,
    user: dict = Depends(get_current_user)
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    result = await col_cumplimiento().find_one_and_update(
        {"_id": ObjectId(cumplimiento_id), "uid": user["uid"]},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return serialize(result)


# ── DELETE /cumplimiento/{id} — Eliminar registro ───────────────────────────
@router.delete("/{cumplimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_cumplimiento(
    cumplimiento_id: str,
    user: dict = Depends(get_current_user)
):
    result = await col_cumplimiento().delete_one(
        {"_id": ObjectId(cumplimiento_id), "uid": user["uid"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Registro no encontrado")



