# 🔥 Operación Fénix — Robot SAR de Planificación Automatizada

> **ISIS-1611 · Inteligencia Artificial · Taller 4: Planificación Automatizada**  
> Universidad de los Andes · Departamento de Ingeniería de Sistemas y Computación

---

## Descripción del Proyecto

**Operación Fénix** es el motor de planificación de un robot SAR (*Search and Rescue*) desarrollado para la UNGRD (Unidad Nacional para la Gestión del Riesgo de Desastres). El sistema coordina la fase de **reconstrucción y atención humanitaria** posterior a un terremoto en un sector de Bogotá, modelado como una cuadrícula navegable.

El robot debe planificar autónomamente cómo recoger suministros médicos, establecerlos en puestos de atención y rescatar pacientes atrapados, utilizando técnicas formales de Inteligencia Artificial: planificación clásica (BFS hacia adelante y regresiva), búsqueda heurística (A\*) y planificación jerárquica (HTN).

El entorno se representa mediante **fluentes PDDL** (*Planning Domain Definition Language*): hechos que describen el estado del mundo, y acciones con precondiciones y efectos que transforman ese estado.

---

## Requisitos e Instalación

### Prerrequisitos

| Componente | Versión mínima | Notas |
|---|---|---|
| Python | 3.8+ | Requerido |
| Tkinter | Nativo en CPython | Para visualización gráfica |

> **Nota sobre Tkinter:** En la mayoría de instalaciones estándar de Python 3, Tkinter viene incluido. Si no está disponible, utilice los flags `-t` (texto) o `-q` (silencioso) para ejecutar sin interfaz gráfica.

### Instalación en Linux/macOS

```bash
# Verificar versión de Python
python3 --version

# Clonar el repositorio
git clone https://github.com/Grupo-IA/Taller-4.git
cd Taller-4/PhoenixOperation/PhoenixOperation

# Verificar que Tkinter esté disponible (opcional)
python3 -c "import tkinter; print('Tkinter OK')"
```

### Instalación en Windows

```bash
# Clonar el repositorio
git clone https://github.com/Grupo-IA/Taller-4.git
cd Taller-4\PhoenixOperation\PhoenixOperation

# Verificar Tkinter
python -c "import tkinter; print('Tkinter OK')"
```

### Sin dependencias externas

El proyecto **no requiere instalar paquetes de terceros** (`pip install`). Todas las dependencias son parte de la biblioteca estándar de Python.

---

## Estructura del Repositorio

```
PhoenixOperation/
└── PhoenixOperation/
    ├── main.py                     # Punto de entrada: parser de argumentos y orquestador
    │
    ├── planning/                   # 🧠 Módulo central de planificación (a completar)
    │   ├── __init__.py
    │   ├── pddl.py                 # Tipos base: Fluent, State, ActionSchema, Action, Problem
    │   ├── domain.py               # Esquemas de acción: MOVE, PICKUP, PUTDOWN, RESCUE, SETUP_SUPPLIES
    │   ├── problems.py             # Definición de problemas: SimpleRescueProblem, MultiRescueProblem
    │   ├── planner.py              # Algoritmos: forwardBFS, backwardSearch, aStarPlanner
    │   ├── heuristics.py           # Heurísticas: ignorePreconditions, ignoreDeleteLists
    │   ├── htn.py                  # Planificador HTN: HLA, hierarchicalSearch, build_htn_hierarchy
    │   └── utils.py                # Estructuras de datos: Stack, Queue, PriorityQueue
    │
    ├── world/                      # 🌍 Simulación del mundo y reglas de transición
    │   ├── __init__.py
    │   ├── game.py                 # Grid 2D booleana (mapa de celdas)
    │   ├── rescue_layout.py        # Parser de archivos .lay → RescueLayout
    │   └── rescue_rules.py         # build_initial_state(): genera fluentes PDDL desde el layout
    │
    ├── view/                       # 🖥️ Visualización de la ejecución del plan
    │   ├── __init__.py
    │   ├── graphics_display.py     # Visualizador gráfico Tkinter con animación por pasos
    │   ├── graphics_utils.py       # Canvas wrapper, paleta de colores, primitivas de dibujo
    │   └── text_display.py         # Modos TextDisplay (consola) y NullGraphics (silencioso)
    │
    └── layouts/                    # 🗺️ Mapas de prueba en formato .lay
        ├── simple/                 # Escenarios con un solo paciente
        │   ├── tinyBase.lay        # Mínimo: 5×7, una columna
        │   ├── openRescue.lay      # Espacio abierto sin obstáculos
        │   ├── cornerRescue.lay    # Paciente en esquina opuesta
        │   ├── narrowRescue.lay    # Corredor estrecho
        │   ├── smallRescue.lay     # Mapa pequeño con obstáculos
        │   ├── mediumRescue.lay    # Obstáculos en L con caminos indirectos
        │   └── warehouseRescue.lay # Depósito con paredes internas
        ├── multi/                  # Escenarios con múltiples pacientes
        │   ├── tinyMulti.lay       # Dos pacientes, mapa compacto
        │   ├── duoRescue.lay       # Dos pacientes dispersos
        │   ├── smallMulti.lay      # Múltiples pacientes y suministros
        │   └── crossMulti.lay      # Layout en forma de cruz
        └── htn/                    # Escenarios para planificación jerárquica (HTN)
            ├── tinyHTN.lay         # HTN mínimo
            └── htnBase.lay         # HTN con espacio de maniobra
```

### Símbolos del mapa (archivos `.lay`)

| Símbolo | Significado |
|---|---|
| `%` | Pared / obstáculo (impasable) |
| `R` | Posición inicial del robot SAR |
| `S` | Sobreviviente / Paciente a rescatar |
| `M` | Puesto médico (destino de rescate) |
| `T` | Suministros médicos (deben entregarse en `M`) |
| ` ` / `.` | Celda libre de suelo |

---

## Algoritmos del Motor de Planificación

El núcleo del proyecto reside en `planning/`. Los estudiantes deben completar los componentes marcados con `### Your code here ###`.

### Modelado del Dominio — `domain.py` y `pddl.py`

El estado del mundo es un `frozenset` de **fluentes**: tuplas inmutables que representan hechos lógicos.

**Fluentes principales:**

| Fluente | Significado |
|---|---|
| `("At", entidad, celda)` | La entidad está en esa celda |
| `("Adjacent", c1, c2)` | Las celdas son adyacentes |
| `("Free", celda)` | La celda no está ocupada por el robot |
| `("HandsFree", robot)` | El robot no sostiene nada |
| `("Holding", robot, objeto)` | El robot sostiene el objeto |
| `("Pickable", objeto)` | El objeto puede ser recogido |
| `("MedicalPost", celda)` | La celda es un puesto médico |
| `("SuppliesReady", celda)` | Suministros listos en el puesto médico |
| `("Rescued", paciente)` | El paciente fue rescatado |

**Esquemas de acción a implementar (`domain.py`):**

| Acción | Parámetros | Descripción |
|---|---|---|
| `Move` | `r, from_cell, to_cell` | Mueve el robot a una celda adyacente libre *(implementado como ejemplo)* |
| `PickUp` | `r, obj, loc` | Recoge un objeto en la celda actual del robot |
| `PutDown` | `r, obj, loc` | Deposita el objeto sostenido en la celda actual |
| `SetupSupplies` | `r, s, loc` | Instala suministros en un puesto médico |
| `Rescue` | `r, p, loc` | Rescata al paciente (requiere suministros listos) |

**Funciones base a implementar (`pddl.py`):**

```python
def is_applicable(state, action) -> bool:
    # precond_pos ⊆ state  AND  precond_neg ∩ state = ∅

def apply_action(state, action) -> State:
    # RESULT(s, a) = (s − DEL(a)) ∪ ADD(a)

def get_applicable_actions(state, domain, objects) -> list[Action]:
    # Enumera todas las acciones instanciadas aplicables en el estado actual
```

---

### Planificación Clásica — `planner.py`

#### Búsqueda Hacia Adelante: `forwardBFS`

Explora el espacio de estados aplicando acciones desde el estado inicial, en amplitud (BFS). Garantiza encontrar el plan de menor número de acciones si existe.

```
Estado inicial → [aplicar acciones] → ... → Estado meta
```

- Usa `problem.getSuccessors(state)` para obtener triples `(estado_siguiente, acción, costo)`.
- Mantiene un conjunto de estados visitados para evitar ciclos.

#### Búsqueda Regresiva: `backwardSearch`

Parte desde la meta y aplica **regresión** de acciones hacia atrás, buscando llegar al estado inicial.

```
Meta → [regresar acciones] → ... → Estado inicial
```

La función `regress(goal_set, action)` implementa:

```
REGRESS(g, a) = (g − ADD(a)) ∪ PRECOND_pos(a)
  si: ADD(a) ∩ g ≠ ∅  (la acción es relevante)
  y:  DEL(a) ∩ g = ∅  (la acción no deshace ningún fluente meta)
```

---

### Planificación Informada — A\* con Heurísticas (`heuristics.py`)

El planificador `aStarPlanner` usa la función de evaluación `f(n) = g(n) + h(n)`, donde:
- `g(n)` = costo acumulado real hasta el nodo `n`
- `h(n)` = estimación heurística del costo restante

**Heurística 1 — Ignorar Precondiciones (`ignorePreconditionsHeuristic`):**  
Calcula el mínimo número de acciones para satisfacer todos los fluentes meta, ignorando precondiciones. Implementa un *greedy set cover* sobre las listas de adición de acciones instanciadas. Es **admisible** (no sobreestima).

**Heurística 2 — Ignorar Listas de Borrado (`ignoreDeleteListsHeuristic`):**  
Resuelve el problema relajado donde ninguna acción elimina fluentes del estado (el estado solo crece). Usa *hill-climbing* para estimar el costo. Las precondiciones **sí aplican** en el modelo relajado.

---

### Planificación Jerárquica (HTN) — `htn.py`

El planificador HTN (*Hierarchical Task Network*) descompone tareas abstractas en acciones primitivas de forma recursiva.

**Estructura HLA (`htn.py`):**

```python
class HLA:
    name: str
    refinements: list[list]   # Cada refinamiento es una lista de HLA/Action
```

**HLAs del dominio de rescate a implementar (`build_htn_hierarchy`):**

| HLA | Descripción |
|---|---|
| `Navigate(from, to)` | Mueve el robot paso a paso entre dos celdas |
| `PrepareSupplies(s, m)` | Recoge suministros y los instala en el puesto médico |
| `ExtractPatient(p, m)` | Recoge al paciente y lo lleva al puesto médico |
| `FullRescueMission(s, p, m)` | Misión completa: prepara suministros + extrae + rescata |

**Algoritmo `hierarchicalSearch`:**

Implementa BFS sobre refinamientos jerárquicos. Parte de un plan con una única HLA raíz y, en cada paso, reemplaza el primer paso no primitivo con uno de sus refinamientos posibles, hasta obtener un plan completamente primitivo que alcance el estado meta.

---

## Guía de Ejecución

### Sintaxis General

```bash
python main.py -p PROBLEMA -f PLANIFICADOR [-h HEURISTICA] [-m] -l MAPA [opciones]
```

### Tabla de Parámetros

| Flag | Nombre | Valores aceptados | Descripción |
|---|---|---|---|
| `-p` | `--problem` | `SimpleRescueProblem`, `MultiRescueProblem` | Tipo de problema (1 paciente o múltiples) |
| `-f` | `--function` | `forwardBFS`, `backwardSearch`, `aStarPlanner`, `tinyBaseSearch` | Algoritmo de planificación |
| `-h` | `--heuristic` | `ignorePreconditions`, `ignoreDeleteLists`, `nullHeuristic` | Heurística para A\* *(requerida con `aStarPlanner`)* |
| `-l` | `--layout` | `tinyBase`, `openRescue`, `tinyMulti`, `htnBase`, ... | Nombre del mapa a cargar (sin extensión `.lay`) |
| `-m` | `--htn` | *(flag booleano)* | Activa el modo HTN; no requiere `-f` |
| `-t` | `--text` | *(flag booleano)* | Muestra la ejecución en modo texto (consola) |
| `-q` | `--quiet` | *(flag booleano)* | Modo silencioso, sin salida gráfica ni de texto |
| `-x` | `--frame-time` | número flotante (segundos) | Retardo entre fotogramas [default: `0.1`] |
| `-z` | `--zoom` | número flotante | Factor de zoom de la ventana gráfica [default: `1.0`] |

---

### Ejemplos de Ejecución

#### Planificación forward BFS (mapa mínimo, modo silencioso)
```bash
python main.py -p SimpleRescueProblem -f forwardBFS -l tinyBase -q
```

#### Planificación forward con visualización gráfica y zoom
```bash
python main.py -p SimpleRescueProblem -f forwardBFS -l tinyBase -x 0.5 -z 2.0
```

#### Planificación regresiva en mapa abierto
```bash
python main.py -p SimpleRescueProblem -f backwardSearch -l openRescue -t
```

#### A\* con heurística de ignorar precondiciones
```bash
python main.py -p SimpleRescueProblem -f aStarPlanner -h ignorePreconditions -l mediumRescue
```

#### A\* con heurística de ignorar listas de borrado (multi-paciente)
```bash
python main.py -p MultiRescueProblem -f aStarPlanner -h ignoreDeleteLists -l tinyMulti -q
```

#### Modo HTN (planificación jerárquica)
```bash
python main.py -p SimpleRescueProblem -m -l tinyHTN -t
```

#### Referencia hardcodeada `tinyBase` (para entender el formato de acciones)
```bash
python main.py -p SimpleRescueProblem -f tinyBaseSearch -l tinyBase -x 0.5 -z 2.0
```

---

### Salida esperada

```
============================================================
  Operación Fénix - ISIS-1611 Inteligencia Artificial
============================================================
  Layout:   tinyBase  (5×7)
  Problema: SimpleRescueProblem
  Pacientes: ['patient_0']
  Suministros: ['supplies_0']
  Puestos médicos: [(1, 2)]
============================================================
  Planificador: forwardBFS

  Tiempo de planificación: 0.012s
  Estados expandidos: 47

  Longitud del plan: 9 acciones

  Plan:
     1. Move(robot,(1,4),(1,3))
     2. PickUp(robot,supplies_0,(1,3))
     ...
     9. Rescue(robot,patient_0,(1,2))

  Ejecutando plan...

  ¡Misión completada exitosamente!
```

---

## Leyenda Visual (Modo Gráfico)

| Elemento | Representación |
|---|---|
| 🟦 Círculo azul **R** | Robot SAR |
| 🔶 Diamante naranja **T** | Suministros médicos |
| 🔺 Triángulo rojo **S** | Paciente / Sobreviviente |
| 🟩 Cuadrado verde **M** | Puesto médico |
| 🟡 Anillo dorado | Robot sosteniendo un objeto |
| ✅ Triángulo verde **✓** | Paciente rescatado |
| ⭕ Punto dorado | Suministros listos en puesto médico |

---

## Componentes Pendientes de Implementación

Los siguientes puntos deben ser completados por el equipo del taller:

| Punto | Archivo | Función / Clase | Descripción |
|---|---|---|---|
| 1a | `planning/domain.py` | `PICKUP`, `PUTDOWN`, `RESCUE`, `SETUP_SUPPLIES` | Esquemas de acción PDDL |
| 1b | `planning/pddl.py` | `is_applicable`, `apply_action`, `get_applicable_actions` | Funciones base del motor |
| 2 | `planning/problems.py` | `SimpleRescueProblem`, `MultiRescueProblem` | Definición de metas |
| 3 | `planning/planner.py` | `forwardBFS` | Planificación clásica hacia adelante |
| 4 | `planning/planner.py` | `regress`, `backwardSearch` | Planificación regresiva |
| 5 | `planning/planner.py` | `aStarPlanner` | Búsqueda A\* |
| 6a | `planning/heuristics.py` | `ignorePreconditionsHeuristic` | Heurística: ignorar precondiciones |
| 6b | `planning/heuristics.py` | `ignoreDeleteListsHeuristic` | Heurística: ignorar listas de borrado |
| 7a | `planning/htn.py` | `hierarchicalSearch` | Motor de búsqueda HTN |
| 7b | `planning/htn.py` | `build_htn_hierarchy` | Definición de HLAs del dominio |

---

## Créditos y Autores

```
╔══════════════════════════════════════════════════════════╗
║         Taller 4: Planificación Automatizada             ║
║         ISIS-1611 · Inteligencia Artificial              ║
║         Universidad de los Andes · 2025                  ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Nombre completo         Código de estudiante            ║
║  ─────────────────────   ────────────────────            ║
║  [ Integrante 1 ]        [ Código 1 ]                    ║
║  [ Integrante 2 ]        [ Código 2 ]                    ║
║  [ Integrante 3 ]        [ Código 3 ]                    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

---

> *"En el caos del desastre, la planificación es la diferencia entre el rescate y el abandono."*  
> — Operación Fénix, UNGRD
