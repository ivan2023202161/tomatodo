from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

client: AsyncIOMotorClient = None

async def connect_db():
    global client
    client = AsyncIOMotorClient(settings.MONGO_URI)
    print(f"✅ Conectado a MongoDB: {settings.MONGO_DB}")

async def close_db():
    global client
    if client:
        client.close()
        print("🔌 Conexión MongoDB cerrada")

def get_db():
    return client[settings.MONGO_DB]

# ── Colecciones ────────────────────────────────────────────────────────────
def col_usuarios():       return get_db()["usuarios"]
def col_horarios():       return get_db()["horarios"]
def col_cumplimiento():   return get_db()["cumplimiento"]
def col_despensa():       return get_db()["despensa"]
def col_recetas():        return get_db()["recetas"]
def col_lista_compras():  return get_db()["lista_compras"]
def col_presupuesto():    return get_db()["presupuesto"]
def col_notificaciones(): return get_db()["notificaciones"]
