from __future__ import annotations

from planning.pddl import Action, Problem, apply_action, get_all_groundings, is_applicable
from planning.utils import Queue, PriorityQueue


# ---------------------------------------------------------------------------
# HTN Infrastructure
# ---------------------------------------------------------------------------


class HLA:
    """
    A High-Level Action (HLA) in HTN planning.

    An HLA is an abstract task that can be refined into sequences of
    more primitive actions (or other HLAs). Each refinement is a list
    of HLA or Action objects.

    name:        Human-readable name for display
    refinements: List of possible refinements, each a list of HLA/Action objects
    """

    def __init__(self, name: str, refinements: list[list] | None = None) -> None:
        self.name = name
        self.refinements = refinements or []

    def __repr__(self) -> str:
        return f"HLA({self.name})"


def is_primitive(action: Action | HLA) -> bool:
    """Return True if action is a primitive (grounded Action), False if it is an HLA."""
    return isinstance(action, Action)


def is_plan_primitive(plan: list[Action | HLA]) -> bool:
    """Return True if every step in the plan is a primitive action."""
    return all(is_primitive(step) for step in plan)


# ---------------------------------------------------------------------------
# Punto 5a – hierarchicalSearch
# ---------------------------------------------------------------------------


def hierarchicalSearch(problem: Problem, hlas: list[HLA]) -> list[Action]:
    """
    HTN planning via BFS over hierarchical plan refinements.

    Start with an initial plan containing a single top-level HLA.
    At each step, find the first non-primitive step in the plan and
    replace it with one of its refinements. Continue until the plan
    is fully primitive and achieves the goal when executed from the
    initial state.

    Returns a list of primitive Action objects, or [] if no plan found.

    Tip: The search space consists of (partial plan, current plan index) pairs.
         Use a Queue (BFS) to explore all refinement choices fairly.
         A plan is a solution when:
           1. It contains only primitive actions (is_plan_primitive), AND
           2. Executing it from the initial state reaches a goal state.
         To simulate execution, apply each action in order using apply_action().
    """
    ### Your code here ###
    if not hlas:
        return []
    
    initial_plan= [hlas[0]]
    queue= Queue()
    queue.push(initial_plan)
    
    while queue.isEmpty() == False:
        current_plan= queue.pop()
        if all(not hasattr(task, 'refinements') for task in current_plan):
            state = problem.getStartState()
        if is_plan_primitive(current_plan):
            state= problem.initial_state
            for action in current_plan:
                state= apply_action(state, action)
            if problem.goal == state:
                return current_plan
            continue
        
        cent= False
        i= 0
        while cent == False and i < len(current_plan):
            action= current_plan[i]
            if not is_primitive(action):
                hla= action
                for refinement_sequence in hla.refinements:
                    new_plan= current_plan[:i] + refinement_sequence + current_plan[i+1:]
                    queue.push(new_plan)
                cent= True
            i+= 1
            
    return []
    ### End of your code ###


# ---------------------------------------------------------------------------
# Punto 5b – HLA Definitions
# ---------------------------------------------------------------------------


def build_htn_hierarchy(problem: Problem) -> list[HLA]:
    """
    Build HTN HLAs for the rescue domain.

    The hierarchy defines four HLA types:
      - Navigate(from, to):       Move the robot step by step from one cell to another
      - PrepareSupplies(s, m):    Collect supplies and set them up at the medical post
      - ExtractPatient(p, m):     Pick up the patient and bring them to the medical post
      - FullRescueMission(s,p,m): Complete one rescue: prepare supplies + extract + rescue

    Refinements are built from the ground state to generate concrete Action objects.

    Tip: Refinements for Navigate are all single-step Move sequences between
         adjacent cells. PrepareSupplies and ExtractPatient chain Navigate HLAs
         with primitive PickUp, SetupSupplies, PutDown, and Rescue actions.
    """
    ### Your code here ###
    domain = problem.domain
    objects = problem.objects
    
    robots = objects.get("robots", [])
    cells = objects.get("cells", [])
    supplies = objects.get("supplies", [])
    patients = objects.get("patients", [])
    medical_posts = objects.get("medical_posts", [])
    
    hla_list = []
    all_grounded = get_all_groundings(domain, objects)
    
    for r in robots:
        for from_cell in cells:
            for to_cell in cells:
                if from_cell != to_cell:
                    navigate_hla = HLA(f"Navigate({from_cell}, {to_cell})")
                    target_move_name = f"Move({r}, {from_cell}, {to_cell})"
                    move_action = next((a for a in all_grounded if a.name == target_move_name), None)
                    
                    if move_action:
                        navigate_hla.refinements.append([move_action])
                        hla_list.append(navigate_hla)
    
    for s in supplies:
        for m in medical_posts:
            prepare_hla = HLA(f"PrepareSupplies({s}, {m})")
            for r in robots:
                for from_cell in cells:
                    for cell in cells:
                        pick_up = next((a for a in all_grounded if a.name.startswith(f"PickUp({r}, {s}")), None)
                        setup = next((a for a in all_grounded if a.name.startswith(f"SetupSupplies({r}, {s}")), None)
                        
                        if pick_up and setup:
                            nav_to_supply = next((h for h in hla_list if h.name == f"Navigate({from_cell}, {cell})"), None)
                            nav_to_post = next((h for h in hla_list if h.name == f"Navigate({cell}, {m})"), None)
                            
                            secuencia = []
                            if nav_to_supply: 
                                secuencia.append(nav_to_supply)
                            secuencia.append(pick_up)
                            if nav_to_post: 
                                secuencia.append(nav_to_post)
                            secuencia.append(setup)
                            
                            prepare_hla.refinements.append(secuencia)
            hla_list.append(prepare_hla)
    
    for p in patients:
        for m in medical_posts:
            extract_hla = HLA(f"ExtractPatient({p}, {m})")
            for r in robots:
                for from_cell in cells:
                    for cell in cells:
                        pick_up = next((a for a in all_grounded if a.name.startswith(f"PickUp({r}, {p}")), None)
                        put_down = next((a for a in all_grounded if a.name.startswith(f"PutDown({r}, {p}")), None)
                        
                        if pick_up and put_down:
                            nav_to_patient = next((h for h in hla_list if h.name == f"Navigate({from_cell}, {cell})"), None)
                            nav_to_post = next((h for h in hla_list if h.name == f"Navigate({cell}, {m})"), None)
                            
                            secuencia = []
                            if nav_to_patient: 
                                secuencia.append(nav_to_patient)
                            secuencia.append(pick_up)
                            if nav_to_post: 
                                secuencia.append(nav_to_post)
                            secuencia.append(put_down)
                            
                            extract_hla.refinements.append(secuencia)
            hla_list.append(extract_hla)
            
    for s in supplies:
        for p in patients:
            for m in medical_posts:
                full_rescue_hla = HLA(f"FullRescueMission({s}, {p}, {m})")
                
                prepare_hla = next((h for h in hla_list if h.name == f"PrepareSupplies({s}, {m})"), None)
                extract_hla = next((h for h in hla_list if h.name == f"ExtractPatient({p}, {m})"), None)
                rescue_action = next((a for a in all_grounded if a.name.startswith("Rescue")), None)
                
                if prepare_hla and extract_hla and rescue_action:
                    full_rescue_hla.refinements.append([prepare_hla, extract_hla, rescue_action])
                    hla_list.append(full_rescue_hla)
                
    return hla_list
    ### End of your code ###
