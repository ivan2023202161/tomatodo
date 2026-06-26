from fastapi import APIRouter, Depends, HTTPException, status
from db.database import col_notificaciones
from db.helpers import serialize, serialize_list
from schemas.schemas import NotificacionCreate, NotificacionUpdate, NotificacionOut
from core.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


# ── POST /notificaciones — Crear notificación ──────────────────────────────
@router.post("/", response_model=NotificacionOut, status_code=status.HTTP_201_CREATED)
async def crear_notificacion(
    data: NotificacionCreate,
    user: dict = Depends(get_current_user)
):
    doc = data.model_dump()
    doc["uid"]   = user["uid"]
    doc["leida"] = False
    # Si tiene fecha_hora programada, usarla como fecha, si no usar ahora
    doc["fecha"] = data.fecha_hora if data.fecha_hora else datetime.utcnow()


    result = await col_notificaciones().insert_one(doc)
    created = await col_notificaciones().find_one({"_id": result.inserted_id})
    return serialize(created)


# ── GET /notificaciones — Listar notificaciones del usuario ────────────────
@router.get("/", response_model=list[NotificacionOut])
async def listar_notificaciones(
    user: dict = Depends(get_current_user),
    solo_no_leidas: bool = False,
):
    filtro: dict = {"uid": user["uid"]}
    if solo_no_leidas:
        filtro["leida"] = False

    docs = await col_notificaciones().find(filtro)\
        .sort("fecha", -1).limit(50).to_list(length=50)
    return serialize_list(docs)


# ── GET /notificaciones/{id} — Obtener una notificación ────────────────────
@router.get("/{notif_id}", response_model=NotificacionOut)
async def obtener_notificacion(
    notif_id: str,
    user: dict = Depends(get_current_user)
):
    doc = await col_notificaciones().find_one(
        {"_id": ObjectId(notif_id), "uid": user["uid"]}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return serialize(doc)


# ── PUT /notificaciones/{id} — Marcar como leída ───────────────────────────
@router.put("/{notif_id}", response_model=NotificacionOut)
async def actualizar_notificacion(
    notif_id: str,
    data: NotificacionUpdate,
    user: dict = Depends(get_current_user)
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    result = await col_notificaciones().find_one_and_update(
        {"_id": ObjectId(notif_id), "uid": user["uid"]},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return serialize(result)


# ── PUT /notificaciones/leer/todas — Marcar todas como leídas ──────────────
@router.put("/leer/todas", status_code=status.HTTP_200_OK)
async def marcar_todas_leidas(user: dict = Depends(get_current_user)):
    result = await col_notificaciones().update_many(
        {"uid": user["uid"], "leida": False},
        {"$set": {"leida": True}}
    )
    return {"actualizadas": result.modified_count}


# ── DELETE /notificaciones/{id} — Eliminar notificación ────────────────────
@router.delete("/{notif_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_notificacion(
    notif_id: str,
    user: dict = Depends(get_current_user)
):
    result = await col_notificaciones().delete_one(
        {"_id": ObjectId(notif_id), "uid": user["uid"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
