"""
Referencia de la Actividad 2 (comprensión del problema).
Estos datos se reutilizan en Actividades 4 y 5 (scopes en JWT y reglas de negocio).
"""

from typing import FrozenSet

# Roles del sistema (tabla usuarios.rol)
ROLES: tuple[str, ...] = (
    "solicitante",
    "responsable_tecnico",
    "auxiliar",
    "tecnico_especializado",
    "admin",
)

# Scopes y qué roles los poseen al emitir el token
ROLE_SCOPES: dict[str, FrozenSet[str]] = {
    "solicitante": frozenset({"tickets:crear", "tickets:ver_propios"}),
    "responsable_tecnico": frozenset(
        {
            "tickets:ver_propios",
            "tickets:recibir",
            "tickets:asignar",
            "tickets:finalizar",
        }
    ),
    "auxiliar": frozenset({"tickets:ver_propios", "tickets:atender"}),
    "tecnico_especializado": frozenset({"tickets:ver_propios", "tickets:atender"}),
    "admin": frozenset(
        {
            "tickets:crear",
            "tickets:ver_propios",
            "tickets:recibir",
            "tickets:asignar",
            "tickets:atender",
            "tickets:finalizar",
            "tickets:ver_todos",
            "usuarios:gestionar",
        }
    ),
}

# Estados válidos de un ticket
ESTADOS_TICKET: tuple[str, ...] = (
    "solicitado",
    "recibido",
    "asignado",
    "en_proceso",
    "en_revision",
    "terminado",
)

# Transiciones: (estado_actual, estado_siguiente) -> scope requerido
# Quién puede ejecutarla se valida en Actividad 5; aquí solo documentamos el flujo.
TRANSICIONES: tuple[tuple[str, str, str], ...] = (
    ("solicitado", "recibido", "tickets:recibir"),
    ("recibido", "asignado", "tickets:asignar"),
    ("asignado", "en_proceso", "tickets:atender"),
    ("en_proceso", "en_revision", "tickets:atender"),
    ("en_revision", "terminado", "tickets:finalizar"),
)

PRIORIDADES: tuple[str, ...] = ("baja", "media", "alta")
