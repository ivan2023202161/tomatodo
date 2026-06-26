from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from db.database import col_despensa
from db.helpers import serialize, serialize_list
from schemas.schemas import IngredienteCreate, IngredienteUpdate, IngredienteOut
from core.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/despensa", tags=["Despensa"])


# ── POST /despensa — Agregar ingrediente ────────────────────────────────────
@router.post("/", response_model=IngredienteOut, status_code=status.HTTP_201_CREATED)
async def agregar_ingrediente(
    data: IngredienteCreate,
    user: dict = Depends(get_current_user)
):
    doc = data.model_dump()
    doc["uid"] = user["uid"]
    result = await col_despensa().insert_one(doc)
    created = await col_despensa().find_one({"_id": result.inserted_id})
    return serialize(created)


# ── GET /despensa — Listar ingredientes (filtros opcionales) ─────────────────
@router.get("/", response_model=list[IngredienteOut])
async def listar_despensa(
    user: dict = Depends(get_current_user),
    categoria: Optional[str] = Query(None),
    solo_agotados: bool = Query(False),
    solo_por_vencer: bool = Query(False),
):
    filtro: dict = {"uid": user["uid"]}

    if categoria:
        filtro["categoria"] = categoria
    if solo_agotados:
        filtro["cantidad"] = {"$lte": 0}
    if solo_por_vencer:
        ahora = datetime.utcnow()
        en_3_dias = datetime(ahora.year, ahora.month, ahora.day + 3)
        filtro["fecha_vencimiento"] = {"$lte": en_3_dias, "$gte": ahora}

    docs = await col_despensa().find(filtro)\
        .sort("nombre", 1).to_list(length=200)
    return serialize_list(docs)


# ── GET /despensa/{id} — Obtener un ingrediente ──────────────────────────────
@router.get("/{ingrediente_id}", response_model=IngredienteOut)
async def obtener_ingrediente(
    ingrediente_id: str,
    user: dict = Depends(get_current_user)
):
    doc = await col_despensa().find_one(
        {"_id": ObjectId(ingrediente_id), "uid": user["uid"]}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    return serialize(doc)


# ── PUT /despensa/{id} — Actualizar ingrediente ──────────────────────────────
@router.put("/{ingrediente_id}", response_model=IngredienteOut)
async def actualizar_ingrediente(
    ingrediente_id: str,
    data: IngredienteUpdate,
    user: dict = Depends(get_current_user)
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    result = await col_despensa().find_one_and_update(
        {"_id": ObjectId(ingrediente_id), "uid": user["uid"]},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    return serialize(result)


# ── DELETE /despensa/{id} — Eliminar ingrediente ─────────────────────────────
@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_ingrediente(
    ingrediente_id: str,
    user: dict = Depends(get_current_user)
):
    result = await col_despensa().delete_one(
        {"_id": ObjectId(ingrediente_id), "uid": user["uid"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
