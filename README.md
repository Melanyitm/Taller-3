# Taller 3 — Mesa de servicios (laboratorios)

API con **FastAPI** y **PostgreSQL** para gestión de tickets, según la guía del repositorio de clase ([`apps_services` / `clase-10-Taller-3`](https://github.com/Juanmorales177809/apps_services/tree/clase-10-Taller-3)).

## Actividad 2 (modelo conceptual)

En código reutilizable para las actividades 4 y 5:

- `app/domain/actividad2.py` — roles, scopes por rol, estados del ticket, transiciones y prioridades.

## Actividad 3 (lo implementado aquí)

- Conexión con `DATABASE_URL` y tablas en el schema `DB_SCHEMA` (definidos en `.env`).
- Modelos SQLAlchemy: `usuarios`, `laboratorios`, `servicios`, `tickets`.
- Esquemas Pydantic y endpoints:

| Método | Ruta |
|--------|------|
| POST | `/usuarios/` |
| GET | `/usuarios/` |
| GET | `/usuarios/me` *(JWT)* |
| GET | `/usuarios/{id_usuario}` |
| POST | `/auth/token` |
| POST | `/laboratorios/` |
| GET | `/laboratorios/` |
| GET | `/laboratorios/{id_laboratorio}` |
| POST | `/servicios/` |
| GET | `/servicios/` |
| GET | `/servicios/{id_servicio}` |
| POST | `/tickets/` |
| GET | `/tickets/` |
| GET | `/tickets/{id_ticket}` |
| PATCH | `/tickets/{id_ticket}/estado` |

Al iniciar la aplicación se ejecuta `CREATE SCHEMA IF NOT EXISTS` y `create_all` sobre ese schema (entorno de laboratorio). Para migraciones formales conviene introducir Alembic más adelante.

**Nota:** La validación estricta de transiciones de estado y la autorización por **scopes** corresponden a la **actividad 5**; el `PATCH` de estado aún no aplica todas las reglas de negocio.

## Actividad 4 (autenticación JWT)

- **POST `/auth/token`** — cuerpo *form* OAuth2: `username` = correo del usuario, `password` = contraseña. Respuesta: `access_token` y `token_type` (`bearer`).
- El token incluye en el payload: `sub` (correo), `id_usuario`, `rol`, `scopes` (lista según `ROLE_SCOPES` en `app/domain/actividad2.py`) y `exp`.
- Contraseñas: **bcrypt** al crear usuario (`POST /usuarios/`) y verificación en el login.
- **Dependencia** `get_current_user` (`app/deps.py`): lee el Bearer token, valida firma y expiración y carga el usuario en base de datos.
- **Ruta protegida de ejemplo:** **GET `/usuarios/me`** — sin `Authorization: Bearer` responde **401**.

### Probar en Swagger

1. `POST /usuarios/` — crear usuario con correo y contraseña.
2. `POST /auth/token` — enviar el mismo correo en `username` y la contraseña en `password`.
3. Copiar `access_token` → botón **Authorize** → pegar `Bearer <token>` o solo el token (Swagger añade `Bearer` según configuración).
4. Ejecutar **GET `/usuarios/me`** y comprobar **200**; sin autorizar, **401**.

## Configuración

1. Python 3.10+ y PostgreSQL en ejecución.
2. Crea la base de datos que uses en `DATABASE_URL` (el usuario PostgreSQL debe poder crear objetos en el schema indicado).
3. Copia variables en `.env`:
   - `DATABASE_URL`
   - `DB_SCHEMA` — nombre del schema **asignado por el docente**
   - `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` (JWT; actividad 4)

4. Entorno virtual e instalación:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

5. Ejecutar la API:

```powershell
uvicorn app.main:app --reload
```

Documentación interactiva: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Integrantes

_(Completa con nombres y aportes para la entrega final.)_
