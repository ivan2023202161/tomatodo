from fastapi import APIRouter, Depends, HTTPException, status
from db.database import col_usuarios
from db.helpers import serialize, serialize_list
from schemas.schemas import UsuarioCreate, UsuarioUpdate, UsuarioOut
from core.auth import get_current_user

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# ── POST /usuarios — Crear perfil (se llama tras registro en Firebase Auth) ──
@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    data: UsuarioCreate,
    user: dict = Depends(get_current_user)
):
    # Solo el propio usuario puede crear su perfil
    if user["uid"] != data.uid:
        raise HTTPException(status_code=403, detail="No autorizado")

    existing = await col_usuarios().find_one({"uid": data.uid})
    if existing:
        raise HTTPException(status_code=409, detail="El usuario ya existe")

    doc = data.model_dump()
    result = await col_usuarios().insert_one(doc)
    created = await col_usuarios().find_one({"_id": result.inserted_id})
    return serialize(created)


# ── GET /usuarios/me — Obtener perfil propio ────────────────────────────────
@router.get("/me", response_model=UsuarioOut)
async def obtener_perfil(user: dict = Depends(get_current_user)):
    doc = await col_usuarios().find_one({"uid": user["uid"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return serialize(doc)


# ── PUT /usuarios/me — Actualizar perfil ────────────────────────────────────
@router.put("/me", response_model=UsuarioOut)
async def actualizar_perfil(
    data: UsuarioUpdate,
    user: dict = Depends(get_current_user)
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    result = await col_usuarios().find_one_and_update(
        {"uid": user["uid"]},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return serialize(result)


# ── DELETE /usuarios/me — Eliminar cuenta ──────────────────────────────────
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_cuenta(user: dict = Depends(get_current_user)):
    result = await col_usuarios().delete_one({"uid": user["uid"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")


# ── GET /usuarios — Listar todos (solo admin) ───────────────────────────────
@router.get("/", response_model=list[UsuarioOut])
async def listar_usuarios(user: dict = Depends(get_current_user)):
    perfil = await col_usuarios().find_one({"uid": user["uid"]})
    if not perfil or perfil.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")
    docs = await col_usuarios().find().to_list(length=200)
    return serialize_list(docs)

@router.put("/me/fcm-token", status_code=status.HTTP_200_OK)
async def actualizar_fcm_token(
    data: dict,
    user: dict = Depends(get_current_user)
):
    token = data.get("fcm_token")
    if not token:
        raise HTTPException(status_code=400, detail="Token requerido")

    # Agrega el token a la lista si no existe ya
    await col_usuarios().update_one(
        {"uid": user["uid"]},
        {"$addToSet": {"fcm_tokens": token}}  # ← addToSet evita duplicados
    )
    return {"ok": True}

@router.delete("/me/fcm-token/{token}", status_code=status.HTTP_200_OK)
async def eliminar_fcm_token(
    token: str,
    user: dict = Depends(get_current_user)
):
    await col_usuarios().update_one(
        {"uid": user["uid"]},
        {"$pull": {"fcm_tokens": token}}  # ← elimina solo ese token de la lista
    )
    return {"ok": True}