from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, timezone

# ── Usuario ────────────────────────────────────────────────────────────────
class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    uid: str          # uid de Firebase Auth
    rol: str = "usuario"

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    rol: Optional[str] = None
    fcm_token: Optional[str] = None #commit

class UsuarioOut(BaseModel):
    id: str
    uid: str
    nombre: str
    email: str
    rol: str

# ── Horario ────────────────────────────────────────────────────────────────
class HorarioCreate(BaseModel):
    nombre: str                        # "Desayuno"
    hora: str                          # "07:30"
    dias: List[str]                    # ["lun", "mar", ...]
    activo: bool = True

class HorarioUpdate(BaseModel):
    nombre: Optional[str] = None
    hora: Optional[str] = None
    dias: Optional[List[str]] = None
    activo: Optional[bool] = None

class HorarioOut(BaseModel):
    id: str
    uid: str
    nombre: str
    hora: str
    dias: List[str]
    activo: bool

# ── Cumplimiento ───────────────────────────────────────────────────────────
class CumplimientoCreate(BaseModel):
    horario_id: str
    nombre_comida: str
    realizado: bool
    nota: Optional[str] = None
    fecha: datetime = Field(default_factory=datetime.utcnow)

class CumplimientoUpdate(BaseModel):
    realizado: Optional[bool] = None
    nota: Optional[str] = None

class CumplimientoOut(BaseModel):
    id: str
    uid: str
    horario_id: str
    nombre_comida: str
    realizado: bool
    nota: Optional[str]
    fecha: datetime

# ── Ingrediente (Despensa) ─────────────────────────────────────────────────
class IngredienteCreate(BaseModel):
    nombre: str
    cantidad: float
    unidad: str                        # "kg", "L", "und"
    categoria: str                     # "Carnes", "Verduras", ...
    fecha_vencimiento: Optional[datetime] = None

class IngredienteUpdate(BaseModel):
    nombre: Optional[str] = None
    cantidad: Optional[float] = None
    unidad: Optional[str] = None
    categoria: Optional[str] = None
    fecha_vencimiento: Optional[datetime] = None

class IngredienteOut(BaseModel):
    id: str
    uid: str
    nombre: str
    cantidad: float
    unidad: str
    categoria: str
    fecha_vencimiento: Optional[datetime]
#######
class IngredienteReceta(BaseModel):
    nombre: str
    cantidad: float = 1.0
    unidad: str = "und"

# ── Receta ─────────────────────────────────────────────────────────────────
class RecetaCreate(BaseModel):
    nombre: str
    descripcion: str
    tiempo_min: int
    dificultad: str              # ← : "Fácil" | "Media" | "Difícil"
    tipo: str = "regular"        # ← : "regular" | "normal" | "saludable"
    categoria: str = "almuerzo"  # ← : "desayuno" | "merienda" | "almuerzo" | "postre" | "cena"

    ingredientes: List[IngredienteReceta]  #antes era List[str]
    pasos: List[str]
    emoji: str = "🍽"

class RecetaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tiempo_min: Optional[int] = None
    dificultad: Optional[str] = None
    tipo: Optional[str] = None
    categoria: Optional[str] = None
    ingredientes: Optional[List[IngredienteReceta]] = None
    pasos: Optional[List[str]] = None
    emoji: Optional[str] = None

class RecetaOut(BaseModel):
    id: str
    nombre: str
    descripcion: str
    tiempo_min: int
    dificultad: str
    tipo: str
    categoria: str
    ingredientes: List[IngredienteReceta] # ← antes era List[str] commit
    pasos: List[str]
    emoji: str

# ── Lista de compras ───────────────────────────────────────────────────────
class ItemCompraCreate(BaseModel):
    nombre: str
    categoria: str
    comprado: bool = False
    cantidad: float = 1.0   # ← NUEVO
    unidad: str = "und"     # ← NUEVO

class ItemCompraUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    comprado: Optional[bool] = None

class ItemCompraOut(BaseModel):
    id: str
    uid: str
    nombre: str
    categoria: str
    comprado: bool
    cantidad: float         # ← NUEVO
    unidad: str             # ← NUEVO

# ── Presupuesto ────────────────────────────────────────────────────────────
class PresupuestoCreate(BaseModel):
    limite: float
    periodo: str                       # "semanal" | "mensual"
    fecha_inicio: datetime = Field(default_factory=datetime.utcnow)

class PresupuestoUpdate(BaseModel):
    limite: Optional[float] = None
    gastado: Optional[float] = None
    periodo: Optional[str] = None

class PresupuestoOut(BaseModel):
    id: str
    uid: str
    limite: float
    gastado: float
    periodo: str
    fecha_inicio: datetime

# ── Notificación ───────────────────────────────────────────────────────────

class NotificacionUpdate(BaseModel):
    leida: Optional[bool] = None


class NotificacionCreate(BaseModel):
    mensaje: str
    tipo: str                           # "recordatorio" | "alerta"
    hora: Optional[str] = None          # "07:30" para repetir diario
    fecha_hora: Optional[datetime] = None  # fecha y hora específica

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class NotificacionOut(BaseModel):
    id: str
    uid: str
    mensaje: str
    tipo: str
    hora: Optional[str]
    fecha_hora: Optional[datetime]
    leida: bool
    fecha: datetime
