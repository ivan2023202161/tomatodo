# Backend — Organizador de Alimentación Diaria
## FastAPI + MongoDB + Firebase Auth

---

## Estructura del proyecto

```
backend/
├── main.py                    # Entry point, routers, CORS, lifespan
├── requirements.txt
├── .env.example
├── firebase-credentials.json  # (tú lo descargas de Firebase Console)
├── core/
│   ├── config.py              # Variables de entorno
│   └── auth.py                # Verificación de token Firebase
├── db/
│   ├── database.py            # Conexión Motor (async MongoDB)
│   └── helpers.py             # Serialización ObjectId
├── schemas/
│   └── schemas.py             # Modelos Pydantic (request/response)
└── routers/
    ├── usuarios.py
    ├── horarios.py
    ├── cumplimiento.py
    ├── despensa.py
    ├── recetas.py
    ├── lista_compras.py
    ├── presupuesto.py
    ├── notificaciones.py
    └── progreso.py
```

---

## Instalación y configuración

### 1. Clonar e instalar dependencias
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus valores reales
```

### 3. Obtener credenciales de Firebase Admin
1. Ve a Firebase Console → Configuración del proyecto → Cuentas de servicio
2. Clic en **Generar nueva clave privada**
3. Guarda el archivo JSON como `firebase-credentials.json` en la raíz del proyecto

### 4. Tener MongoDB corriendo
```bash
# Con MongoDB local
mongod --dbpath /data/db

# O con Docker
docker run -d -p 27017:27017 --name mongo mongo:7
```

### 5. Correr el servidor
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Abrir documentación interactiva
```
http://localhost:8000/docs      ← Swagger UI
http://localhost:8000/redoc     ← ReDoc
```

---

## Autenticación

Todas las rutas requieren un **Bearer Token** de Firebase Auth.

El token lo obtiene la app Flutter con:
```dart
final token = await FirebaseAuth.instance.currentUser!.getIdToken();
```

Se envía en el header:
```
Authorization: Bearer <token>
```

---

## Endpoints CRUD

### Usuarios
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/usuarios/` | Crear perfil tras registro |
| GET | `/api/v1/usuarios/me` | Obtener perfil propio |
| PUT | `/api/v1/usuarios/me` | Actualizar nombre/rol |
| DELETE | `/api/v1/usuarios/me` | Eliminar cuenta |
| GET | `/api/v1/usuarios/` | Listar usuarios (solo admin) |

### Horarios
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/horarios/` | Crear horario |
| GET | `/api/v1/horarios/` | Listar horarios del usuario |
| GET | `/api/v1/horarios/{id}` | Obtener un horario |
| PUT | `/api/v1/horarios/{id}` | Actualizar horario |
| DELETE | `/api/v1/horarios/{id}` | Eliminar horario |

### Cumplimiento
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/cumplimiento/` | Registrar cumplimiento |
| GET | `/api/v1/cumplimiento/` | Listar registros (filtro por fecha) |
| GET | `/api/v1/cumplimiento/hoy` | Registros de hoy |
| GET | `/api/v1/cumplimiento/{id}` | Obtener un registro |
| PUT | `/api/v1/cumplimiento/{id}` | Marcar realizado/no realizado |
| DELETE | `/api/v1/cumplimiento/{id}` | Eliminar registro |

### Despensa
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/despensa/` | Agregar ingrediente |
| GET | `/api/v1/despensa/` | Listar (filtros: categoria, agotados, por_vencer) |
| GET | `/api/v1/despensa/{id}` | Obtener ingrediente |
| PUT | `/api/v1/despensa/{id}` | Actualizar ingrediente |
| DELETE | `/api/v1/despensa/{id}` | Eliminar ingrediente |

### Recetas
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/recetas/` | Crear receta (solo admin) |
| GET | `/api/v1/recetas/` | Listar recetas (búsqueda, dificultad) |
| GET | `/api/v1/recetas/recomendaciones?ingredientes=...` | Recomendadas por despensa |
| GET | `/api/v1/recetas/{id}` | Obtener receta |
| PUT | `/api/v1/recetas/{id}` | Actualizar receta (solo admin) |
| DELETE | `/api/v1/recetas/{id}` | Eliminar receta (solo admin) |

### Lista de Compras
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/lista-compras/` | Agregar ítem |
| GET | `/api/v1/lista-compras/` | Listar ítems |
| GET | `/api/v1/lista-compras/{id}` | Obtener ítem |
| PUT | `/api/v1/lista-compras/{id}` | Marcar como comprado |
| DELETE | `/api/v1/lista-compras/{id}` | Eliminar ítem |
| DELETE | `/api/v1/lista-compras/limpiar/comprados` | Limpiar todos los comprados |

### Presupuesto
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/presupuesto/` | Crear/reemplazar presupuesto |
| GET | `/api/v1/presupuesto/` | Obtener presupuesto activo |
| PUT | `/api/v1/presupuesto/` | Actualizar límite o período |
| POST | `/api/v1/presupuesto/gasto` | Registrar un gasto |
| DELETE | `/api/v1/presupuesto/` | Reiniciar presupuesto |

### Notificaciones
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/notificaciones/` | Crear notificación |
| GET | `/api/v1/notificaciones/` | Listar (filtro: solo_no_leidas) |
| GET | `/api/v1/notificaciones/{id}` | Obtener notificación |
| PUT | `/api/v1/notificaciones/{id}` | Marcar como leída |
| PUT | `/api/v1/notificaciones/leer/todas` | Marcar todas como leídas |
| DELETE | `/api/v1/notificaciones/{id}` | Eliminar notificación |

### Progreso (solo GET, calculado)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/progreso/hoy` | Resumen del día actual |
| GET | `/api/v1/progreso/semanal` | Cumplimiento últimos 7 días |
| GET | `/api/v1/progreso/mensual` | Resumen del mes actual |

---

## Conectar Flutter al backend

En Flutter, reemplaza las llamadas a Firestore por llamadas HTTP:

```dart
import 'package:http/http.dart' as http;

final token = await FirebaseAuth.instance.currentUser!.getIdToken();
final headers = {
  'Authorization': 'Bearer $token',
  'Content-Type': 'application/json',
};

// Ejemplo: listar horarios
final response = await http.get(
  Uri.parse('http://TU_IP:8000/api/v1/horarios/'),
  headers: headers,
);
```
