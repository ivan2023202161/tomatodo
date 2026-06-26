from fastapi import APIRouter, Depends, HTTPException, status
from db.database import col_lista_compras
from db.helpers import serialize, serialize_list
from schemas.schemas import ItemCompraCreate, ItemCompraUpdate, ItemCompraOut
from core.auth import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/lista-compras", tags=["Lista de Compras"])


# ── POST /lista-compras — Agregar ítem ─────────────────────────────────────
@router.post("/", response_model=ItemCompraOut, status_code=status.HTTP_201_CREATED)
async def agregar_item(
    data: ItemCompraCreate,
    user: dict = Depends(get_current_user)
):
    doc = data.model_dump()
    doc["uid"] = user["uid"]
    result = await col_lista_compras().insert_one(doc)
    created = await col_lista_compras().find_one({"_id": result.inserted_id})
    return serialize(created)


# ── GET /lista-compras — Listar ítems del usuario ──────────────────────────
@router.get("/", response_model=list[ItemCompraOut])
async def listar_items(user: dict = Depends(get_current_user)):
    docs = await col_lista_compras().find({"uid": user["uid"]})\
        .sort("comprado", 1).to_list(length=200)
    return serialize_list(docs)


# ── GET /lista-compras/{id} — Obtener un ítem ──────────────────────────────
@router.get("/{item_id}", response_model=ItemCompraOut)
async def obtener_item(
    item_id: str,
    user: dict = Depends(get_current_user)
):
    doc = await col_lista_compras().find_one(
        {"_id": ObjectId(item_id), "uid": user["uid"]}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return serialize(doc)


# ── PUT /lista-compras/{id} — Actualizar ítem (marcar comprado, etc.) ──────
@router.put("/{item_id}", response_model=ItemCompraOut)
async def actualizar_item(
    item_id: str,
    data: ItemCompraUpdate,
    user: dict = Depends(get_current_user)
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    result = await col_lista_compras().find_one_and_update(
        {"_id": ObjectId(item_id), "uid": user["uid"]},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    return serialize(result)


# ── DELETE /lista-compras/{id} — Eliminar ítem ─────────────────────────────
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_item(
    item_id: str,
    user: dict = Depends(get_current_user)
):
    result = await col_lista_compras().delete_one(
        {"_id": ObjectId(item_id), "uid": user["uid"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")


# ── DELETE /lista-compras/limpiar/comprados — Eliminar todos los comprados ─
@router.delete("/limpiar/comprados", status_code=status.HTTP_204_NO_CONTENT)
async def limpiar_comprados(user: dict = Depends(get_current_user)):
    await col_lista_compras().delete_many(
        {"uid": user["uid"], "comprado": True}
    )
