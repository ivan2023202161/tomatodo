from fastapi import APIRouter, Depends, HTTPException, status
from core.auth import get_current_user
from db.database import col_usuarios
from google.oauth2 import service_account
import google.auth.transport.requests
import httpx
import json
import os
from core.config import settings
router = APIRouter(prefix="/push", tags=["Notificaciones Push"])


CREDENTIALS_PATH = settings.FIREBASE_CREDENTIALS_PATH
FIREBASE_PROJECT_ID = settings.FIREBASE_PROJECT_ID
FCM_URL = f"https://fcm.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/messages:send"
print(f"FCM_URL: {FCM_URL}")

def _get_access_token():
    """Obtiene el token OAuth2 usando las credenciales de Firebase."""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/firebase.messaging"]
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token


async def _enviar_a_tokens(tokens: list[str], titulo: str, cuerpo: str):
    """Envía notificación a una lista de tokens FCM v1."""
    if not tokens:
        return

    access_token = _get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    tokens_invalidos = []

    async with httpx.AsyncClient() as client:
        for token in tokens:
            payload = {
                "message": {
                    "token": token,
                    "notification": {
                        "title": titulo,
                        "body": cuerpo,
                    }
                }
            }
            response = await client.post(FCM_URL, json=payload, headers=headers)
            data = response.json()
            print(f"FCM response: {response.status_code} - {response.text}")

                        # Si el token ya no es válido, marcarlo para eliminar
            if response.status_code == 404 or \
                data.get("error", {}).get("status") == "UNREGISTERED":
                tokens_invalidos.append(token)
                print(f"⚠️ Token inválido detectado: {token[:20]}...")
            else:
                print(f"✅ Notificación enviada: {response.status_code}")

       # Eliminar tokens inválidos de MongoDB
    if tokens_invalidos:
        await col_usuarios().update_many(
            {},
            {"$pull": {"fcm_tokens": {"$in": tokens_invalidos}}}
        )
        print(f"🗑 {len(tokens_invalidos)} tokens inválidos eliminados")

async def _verificar_admin(user: dict):
    perfil = await col_usuarios().find_one({"uid": user["uid"]})
    if not perfil or perfil.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")


@router.post("/mensaje", status_code=status.HTTP_200_OK)
async def enviar_mensaje_masivo(
    data: dict,
    user: dict = Depends(get_current_user)
):
    await _verificar_admin(user)

    titulo  = data.get("titulo", "¡Hola!")
    mensaje = data.get("mensaje", "")

    if not mensaje:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

    usuarios = await col_usuarios().find(
        {"fcm_tokens": {"$exists": True, "$not": {"$size": 0}}}
    ).to_list(length=1000)

    tokens = []
    for u in usuarios:
        tokens.extend(u.get("fcm_tokens", []))

    await _enviar_a_tokens(
        tokens=tokens,
        titulo=titulo,
        cuerpo=mensaje,
    )

    return {"enviado_a": len(tokens), "titulo": titulo}