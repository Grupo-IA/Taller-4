from __future__ import annotations

from planning.pddl import ActionSchema

# ---------------------------------------------------------------------------
# Punto 1a – Complete the preconditions and effects of each action schema.
#
# Each schema uses string variable names as placeholders:
#   "r"         → the robot
#   "from_cell" → source cell       "to_cell" → destination cell
#   "obj"       → any pickable object
#   "s"         → medical supplies  "p" → patient
#   "loc"       → a cell (used as the robot's current location)
#
# Fluent templates are tuples whose elements are either variable names or
# literal constant strings. get_applicable_actions() will substitute
# variable names with real constants during grounding.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Move(r, from_cell, to_cell)
# Move the robot one step to an adjacent, free cell.
# This one is given as an example. You can use it as a template for the other actions.
# ---------------------------------------------------------------------------

MOVE: ActionSchema = ActionSchema(
    name="Move",
    parameters=["r", "from_cell", "to_cell"],
    precond_pos=[
        ("At", "r", "from_cell"),
        ("Adjacent", "from_cell", "to_cell"),
        ("Free", "to_cell"),
    ],
    precond_neg=[],
    add_list=[
        ("At", "r", "to_cell"),
        ("Free", "from_cell"),
    ],
    del_list=[
        ("At", "r", "from_cell"),
        ("Free", "to_cell"),
    ],
)


# ---------------------------------------------------------------------------
# PickUp(r, obj, loc)
# Pick up a pickable object at the robot's current cell.
# After pickup: the object is no longer At loc, and the robot is no longer HandsFree.
# ---------------------------------------------------------------------------

PICKUP: ActionSchema = ActionSchema(
    name="PickUp",
    parameters=["r", "obj", "loc"],
    precond_pos=[
        ("At", "r", "loc"),       # el robot está en la misma celda
        ("At", "obj", "loc"),     # el objeto está en esa celda
        ("HandsFree", "r"),       # las manos del robot están libres
        ("Pickable", "obj"),      # el objeto puede ser recogido
    ],
    precond_neg=[],
    add_list=[
        ("Holding", "r", "obj"),  # ahora el robot lo sostiene
    ],
    del_list=[
        ("At", "obj", "loc"),     # el objeto desaparece del suelo
        ("HandsFree", "r"),       # el robot ya no tiene manos libres
    ],
    
)


# ---------------------------------------------------------------------------
# PutDown(r, obj, loc)
# Place a held object at the robot's current cell.
# After putdown: the object is At loc, and the robot is HandsFree again.
# ---------------------------------------------------------------------------

PUTDOWN: ActionSchema = ActionSchema(
    name="PutDown",
    parameters=["r", "obj", "loc"],
    precond_pos=[
        ("At", "r", "loc"),        # el robot está en esa celda
        ("Holding", "r", "obj"),   # el robot sostiene el objeto
    ],
    precond_neg=[],
    add_list=[
        ("At", "obj", "loc"),      # el objeto aparece en el suelo
        ("HandsFree", "r"),        # el robot queda con manos libres
    ],
    del_list=[
        ("Holding", "r", "obj"),   # el robot deja de sostenerlo
    ],
)


# ---------------------------------------------------------------------------
# Rescue(r, p, loc)
# Rescue a patient who is at a medical post where supplies are ready.
# After rescue: patient is marked as Rescued and no longer At loc.
# ---------------------------------------------------------------------------

RESCUE: ActionSchema = ActionSchema(
    name="Rescue",
    parameters=["r", "p", "loc"],
    precond_pos=[
        ("At", "r", "loc"),          # el robot está en el puesto médico
        ("At", "p", "loc"),          # el paciente está ahí también
        ("MedicalPost", "loc"),      # loc es un puesto médico
        ("SuppliesReady", "loc"),    # los suministros están listos
    ],
    precond_neg=[],
    add_list=[
        ("Rescued", "p"),            # el paciente queda rescatado ✓
    ],
    del_list=[
        ("At", "p", "loc"),          # el paciente ya no ocupa la celda
    ],
)


# ---------------------------------------------------------------------------
# SetupSupplies(r, s, loc)
# Set up medical supplies at a medical post.
# The robot must be at loc, holding the supplies, and loc must be a MedicalPost.
# Note: there is no At(s, loc) precondition because the robot is carrying s;
# the fluent At(s, loc) was removed when the robot picked it up.
# ---------------------------------------------------------------------------

SETUP_SUPPLIES: ActionSchema = ActionSchema(
    name="SetupSupplies",
    parameters=["r", "s", "loc"],
    precond_pos=[
        ("At", "r", "loc"),          # el robot está en el puesto médico
        ("MedicalPost", "loc"),      # loc es efectivamente un puesto médico
        ("Holding", "r", "s"),       # el robot lleva los suministros encima
    ],
    precond_neg=[
        ("SuppliesReady", "loc"),    # los suministros NO deben estar ya instalados
    ],
    add_list=[
        ("SuppliesReady", "loc"),    # el puesto queda equipado con suministros
        ("HandsFree", "r"),          # el robot tiene manos libres de nuevo
    ],
    del_list=[
        ("Holding", "r", "s"),       # el robot ya no carga los suministros
    ],
)


DOMAIN: list[ActionSchema] = [MOVE, PICKUP, PUTDOWN, RESCUE, SETUP_SUPPLIES]
