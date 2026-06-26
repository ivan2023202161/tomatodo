from fastapi import APIRouter, Depends, HTTPException, status
from db.database import col_horarios
from db.helpers import serialize, serialize_list
from schemas.schemas import HorarioCreate, HorarioUpdate, HorarioOut
from core.auth import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/horarios", tags=["Horarios"])


# ── POST /horarios — Crear horario ──────────────────────────────────────────
@router.post("/", response_model=HorarioOut, status_code=status.HTTP_201_CREATED)
async def crear_horario(
    data: HorarioCreate,
    user: dict = Depends(get_current_user)
):
    doc = data.model_dump()
    doc["uid"] = user["uid"]
    result = await col_horarios().insert_one(doc)
    created = await col_horarios().find_one({"_id": result.inserted_id})
    return serialize(created)


# ── GET /horarios — Listar horarios del usuario ─────────────────────────────
@router.get("/", response_model=list[HorarioOut])
async def listar_horarios(user: dict = Depends(get_current_user)):
    docs = await col_horarios().find({"uid": user["uid"]}).to_list(length=50)
    return serialize_list(docs)


# ── GET /horarios/{id} — Obtener un horario ─────────────────────────────────
@router.get("/{horario_id}", response_model=HorarioOut)
async def obtener_horario(
    horario_id: str,
    user: dict = Depends(get_current_user)
):
    doc = await col_horarios().find_one(
        {"_id": ObjectId(horario_id), "uid": user["uid"]}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    return serialize(doc)


# ── PUT /horarios/{id} — Actualizar horario ─────────────────────────────────
@router.put("/{horario_id}", response_model=HorarioOut)
async def actualizar_horario(
    horario_id: str,
    data: HorarioUpdate,
    user: dict = Depends(get_current_user)
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    result = await col_horarios().find_one_and_update(
        {"_id": ObjectId(horario_id), "uid": user["uid"]},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    return serialize(result)


# ── DELETE /horarios/{id} — Eliminar horario ────────────────────────────────
@router.delete("/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_horario(
    horario_id: str,
    user: dict = Depends(get_current_user)
):
    result = await col_horarios().delete_one(
        {"_id": ObjectId(horario_id), "uid": user["uid"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
