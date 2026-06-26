from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from db.database import col_recetas, col_usuarios
from db.helpers import serialize, serialize_list
from schemas.schemas import RecetaCreate, RecetaUpdate, RecetaOut
from core.auth import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/recetas", tags=["Recetas"])


async def verificar_admin(user: dict):
    perfil = await col_usuarios().find_one({"uid": user["uid"]})
    if not perfil or perfil.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")


# ── POST /recetas — Crear receta (solo admin) ───────────────────────────────
@router.post("/", response_model=RecetaOut, status_code=status.HTTP_201_CREATED)
async def crear_receta(
    data: RecetaCreate,
    user: dict = Depends(get_current_user)
):
    await verificar_admin(user)
    doc = data.model_dump()
    result = await col_recetas().insert_one(doc)
    created = await col_recetas().find_one({"_id": result.inserted_id})
    return serialize(created)


# ── GET /recetas — Listar recetas (todos los usuarios) ─────────────────────
@router.get("/", response_model=list[RecetaOut])
async def listar_recetas(
    user: dict = Depends(get_current_user),
    busqueda: Optional[str] = Query(None),
    dificultad: Optional[str] = Query(None),
    tiempo_max: Optional[int] = Query(None),
    tipo: Optional[str] = Query(None),          
    categoria: Optional[str] = Query(None),
):
    filtro: dict = {}

    if busqueda:
        filtro["$or"] = [
            {"nombre": {"$regex": busqueda, "$options": "i"}},
            {"ingredientes": {"$elemMatch": {"$regex": busqueda, "$options": "i"}}},
        ]
    if dificultad:
        filtro["dificultad"] = dificultad
    if tiempo_max:                                      
        filtro["tiempo_min"] = {"$lte": tiempo_max}
    #commit
    if tipo:                          
        filtro["tipo"] = tipo
    if categoria:                      
        filtro["categoria"] = categoria

    docs = await col_recetas().find(filtro)\
        .sort("nombre", 1).to_list(length=100)
    return serialize_list(docs)


# ── GET /recetas/recomendaciones — Recetas según despensa ──────────────────
@router.get("/recomendaciones", response_model=list[RecetaOut])
async def recomendar_recetas(
    user: dict = Depends(get_current_user),
    ingredientes: str = Query(..., description="Lista separada por comas"),
):
    disponibles = [i.strip().lower() for i in ingredientes.split(",")]

    pipeline = [
        {
            "$addFields": {
                "coincidencias": {
                    "$size": {
                        "$filter": {
                            "input": "$ingredientes",
                            "as": "ing",
                            "cond": {
                                "$or": [
                                    {"$in": [{"$toLower": "$$ing.nombre"}, disponibles]}
                                ]
                            }
                        }
                    }
                }
            }
        },
        {"$match": {"coincidencias": {"$gt": 0}}},
        {"$sort": {"coincidencias": -1}},
        {"$limit": 5},
    ]

    docs = await col_recetas().aggregate(pipeline).to_list(length=5)
    return serialize_list(docs)


# ── GET /recetas/{id} — Obtener una receta ──────────────────────────────────
@router.get("/{receta_id}", response_model=RecetaOut)
async def obtener_receta(
    receta_id: str,
    user: dict = Depends(get_current_user)
):
    doc = await col_recetas().find_one({"_id": ObjectId(receta_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return serialize(doc)


# ── PUT /recetas/{id} — Actualizar receta (solo admin) ──────────────────────
@router.put("/{receta_id}", response_model=RecetaOut)
async def actualizar_receta(
    receta_id: str,
    data: RecetaUpdate,
    user: dict = Depends(get_current_user)
):
    await verificar_admin(user)
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    result = await col_recetas().find_one_and_update(
        {"_id": ObjectId(receta_id)},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return serialize(result)


# ── DELETE /recetas/{id} — Eliminar receta (solo admin) ─────────────────────
@router.delete("/{receta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_receta(
    receta_id: str,
    user: dict = Depends(get_current_user)
):
    await verificar_admin(user)
    result = await col_recetas().delete_one({"_id": ObjectId(receta_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
