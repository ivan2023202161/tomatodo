from fastapi import APIRouter, Depends, HTTPException, status
from db.database import col_presupuesto
from db.helpers import serialize
from schemas.schemas import PresupuestoCreate, PresupuestoUpdate, PresupuestoOut
from core.auth import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/presupuesto", tags=["Presupuesto"])


# ── POST /presupuesto — Crear o reemplazar presupuesto ─────────────────────
@router.post("/", response_model=PresupuestoOut, status_code=status.HTTP_201_CREATED)
async def crear_presupuesto(
    data: PresupuestoCreate,
    user: dict = Depends(get_current_user)
):
    doc = data.model_dump()
    doc["uid"] = user["uid"]
    doc["gastado"] = 0.0

    # Upsert: solo uno por usuario
    result = await col_presupuesto().find_one_and_update(
        {"uid": user["uid"]},
        {"$set": doc},
        upsert=True,
        return_document=True,
    )
    return serialize(result)


# ── GET /presupuesto — Obtener presupuesto activo ──────────────────────────
@router.get("/", response_model=PresupuestoOut)
async def obtener_presupuesto(user: dict = Depends(get_current_user)):
    doc = await col_presupuesto().find_one({"uid": user["uid"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Sin presupuesto configurado")
    return serialize(doc)


# ── PUT /presupuesto — Actualizar límite, gasto o período ──────────────────
@router.put("/", response_model=PresupuestoOut)
async def actualizar_presupuesto(
    data: PresupuestoUpdate,
    user: dict = Depends(get_current_user)
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    result = await col_presupuesto().find_one_and_update(
        {"uid": user["uid"]},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Sin presupuesto configurado")
    return serialize(result)


# ── POST /presupuesto/gasto — Sumar un gasto al total ─────────────────────
@router.post("/gasto", response_model=PresupuestoOut)
async def registrar_gasto(
    monto: float,
    user: dict = Depends(get_current_user)
):
    if monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")

    result = await col_presupuesto().find_one_and_update(
        {"uid": user["uid"]},
        {"$inc": {"gastado": monto}},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Sin presupuesto configurado")
    return serialize(result)


# ── DELETE /presupuesto — Reiniciar presupuesto ────────────────────────────
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_presupuesto(user: dict = Depends(get_current_user)):
    result = await col_presupuesto().delete_one({"uid": user["uid"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Sin presupuesto configurado")
