prompt = """
The following is predicates defined in this domain file. Pay attention to the types for each predicate.
(define (domain virtualhome)
(:requirements :typing)
  ;; types in virtualhome domain
  (:types 
    object character  ; Define 'object' and 'character' as types
  )

  ;; Predicates defined on this domain. Note the types for each predicate.
  (:predicates
    (closed ?obj - object)  ; obj is closed
    (open ?obj - object)  ; obj is open
    (on ?obj - object)  ; obj is turned on, or it is activated
    (off ?obj - object)  ; obj is turned off, or it is deactivated
    (plugged_in ?obj - object)  ; obj is plugged in
    (plugged_out ?obj - object)  ; obj is unplugged
    (sitting ?char - character)  ; char is sitting, and this represents a state of a character
    (lying ?char - character)  ; char is lying
    (clean ?obj - object)  ; obj is clean
    (dirty ?obj - object)  ; obj is dirty
    (obj_ontop ?obj1 ?obj2 - object)  ; obj1 is on top of obj2
    (ontop ?char - character ?obj - object)  ; char is on obj
    (on_char ?obj - object ?char - character) ; obj is on char
    (inside_room ?obj ?room - object) ; obj is inside room
    (obj_inside ?obj1 ?obj2 - object)  ; obj1 is inside obj2
    (inside ?char - character ?obj - object)  ; char is inside obj
    (obj_next_to ?obj1 ?obj2 - object)  ; obj1 is close to or next to obj2
    (next_to ?char - character ?obj - object) ; char is close to or next to obj
    (between ?obj1 ?obj2 ?obj3 - object)  ; obj1 is between obj2 and obj3
    (facing ?char - character ?obj - object)  ; char is facing obj
    (holds_rh ?char - character ?obj - object)  ; char is holding obj with right hand
    (holds_lh ?char - character ?obj - object)  ; char is holding obj with left hand
    (grabbable ?obj - object)  ; obj can be grabbed
    (cuttable ?obj - object)  ; obj can be cut
    (can_open ?obj - object)  ; obj can be opened
    (readable ?obj - object)  ; obj can be read
    (has_paper ?obj - object)  ; obj has paper
    (movable ?obj - object)  ; obj is movable
    (pourable ?obj - object)  ; obj can be poured from
    (cream ?obj - object)  ; obj is cream
    (has_switch ?obj - object)  ; obj has a switch
    (lookable ?obj - object)  ; obj can be looked at
    (has_plug ?obj - object)  ; obj has a plug
    (drinkable ?obj - object)  ; obj is drinkable
    (body_part ?obj - object)  ; obj is a body part
    (recipient ?obj - object)  ; obj is a recipient
    (containers ?obj - object)  ; obj is a container
    (cover_object ?obj - object)  ; obj is a cover object
    (surfaces ?obj - object)  ; obj has surfaces
    (sittable ?obj - object)  ; obj can be sat on
    (lieable ?obj - object)  ; obj can be lied on
    (person ?obj - object)  ; obj is a person
    (hangable ?obj - object)  ; obj can be hanged
    (clothes ?obj - object)  ; obj is clothes
    (eatable ?obj - object)  ; obj is eatable
  )
  ;; Actions to be predicted
)

Objective: Given the problem file of pddl, which defines objects in the task (:objects), initial conditions (:init) and goal conditions (:goal), write the body of PDDL actions (:precondition and :effect) given specific action names and parameters, so that after executing the actions in some order, the goal conditions can be reached from initial conditions.

Each PDDL action definition consists of four main components: action name, parameters, precondition, and effect. Here is the general format to follow:
(:action [action name]
  :parameters ([action parameters])
  :precondition ([action precondition])
  :effect ([action effect]) 
)

The :parameters is the list of variables on which the action operates. It lists variable names and variable types. 

The :precondition is a first-order logic sentence specifying preconditions for an action. The precondition consists of predicates and 4 possible logical operators: or, and, not, exists! 
1. The precondition should be structured in Disjunctive Normal Form (DNF), meaning an OR of ANDs. 
2. The not operator should only be used within these conjunctions. For example, (or (and (predicate1 ?x) (predicate2 ?y)) (and (predicate3 ?x)))
3. Exists operator is followed by two parts, variable and body. It follows the format: exists (?x - variable type) (predicate1 ?x), which means there exists an object ?x of certain variable type, that predicate1 ?x satisfies.

The :effect lists the changes which the action imposes on the current state. Effects support the following logical operators: and, not, when, forall. (Do NOT use or or exists in effects.)
1. Effects should generally be several literals connected by AND.
2. Use WHEN for conditional effects: (when [condition] [effect]) means if the condition holds before the action, then the effect occurs after the action.
3. If an effect is unconditional, write the predicate directly.
4. Use NOT to delete a fact after the action.
5. Use FORALL only when necessary to clear relations tied to the specific object(s) acted upon; avoid global cleanups that blow up the search space.

Example: (and (when (predicate1 ?x) (not (predicate2 ?y))) (predicate3 ?x))

Formally, the preconditions and effects are all clauses <Clause>.
<Clause> := (predicate ?x)
<Clause> := (and <Clause1> <Clause2> ...)
<Clause> := (or <Clause1> <Clause2> ...)
<Clause> := (not <Clause>)
<Clause> := (when <Clause1> <Clause2>)
<Clause> := (exists (?x - object type) <Clause>) ; only allowed in preconditions
<Clause> := (forall (?x - object type) <Clause>)

In any case, the occurrence of a predicate should agree with its declaration in terms of number and types of arguments defined in DOMAIN FILE at the beginning.

Here is an example of the input problem file and unfinished action. Observe carefully how to think step by step to write the action body of hang_up_clothes:
Input:
Problem file:
(define (problem hang-clothes-problem)
  (:domain virtualhome)
  (:objects
    character - character
    shirt - object
    hanger - object
  ) ; This section declares the instances needed for the problem: character is an instance of a character; shirt is an instance of an object classified as clothes; hanger is an object that is suitable for hanging clothes.
  (:init
    (clothes shirt)
    (hangable hanger)
    (holds_rh alice shirt)
    (next_to alice hanger)
  ) ; This section declares the initial conditions. (clothes shirt) and (hangable hanger) tells the properties of objects; (holds_rh alice shirt) indicates that Alice is holding the shirt in her right hand; (next_to alice hanger) means Alice is next to the hanger, ready to hang the shirt.
  (:goal
    (and
      (obj_ontop shirt hanger)
    )
  ) ; This section declares the goal.  (obj_ontop shirt hanger) is the goal, where the shirt should end up hanging on the hanger.
)
Action to be finished:
(:action hang_up_clothes
  :parameters (?char - character ?clothes - object ?hang_obj - object)
  :precondition ()
  :effect ()
)

Example output: 
Given the objects in the problem file, and what typically needs to be true to perform an action like hanging up clothes: 1. clothes must indeed be a type of clothing. 2. hang_obj should be something on which clothes can be hung (hangable). 3. char should be holding the clothes, either in the right or left hand. 4. char needs to be next to the hanging object to hang the clothes. Besides, we need to write preconditions in Disjunctive Normal Form.
These insights guide us to write:
:precondition (or
  (and
    (clothes ?clothes)  ; the object must be a piece of clothing
    (hangable ?hang_obj)  ; the target must be an object suitable for hanging clothes
    (holds_rh ?char ?clothes)  ; character is holding clothes in the right hand
    (next_to ?char ?hang_obj)  ; character is next to the hanging object
  )
  (and
    (clothes ?clothes)  ; the object must be a piece of clothing
    (hangable ?hang_obj)  ; the target must be an object suitable for hanging clothes
    (holds_lh ?char ?clothes)  ; character is holding clothes in the left hand
    (next_to ?char ?hang_obj)  ; character is next to the hanging object
  )
)
Effects describe how the world state changes due to the action. After hanging up clothes, you'd expect: 1. char is no longer holding the clothes. 2. clothes is now on the hang_obj.
These expectations convert into effects:
:effect (and
  (when (holds_rh ?char ?clothes)(not (holds_rh ?char ?clothes)))  ; if clothes are held in the right hand, they are no longer held
  (when (holds_lh ?char ?clothes)(not (holds_lh ?char ?clothes)))  ; if clothes are held in the left hand, they are no longer held
  (obj_ontop ?clothes ?hang_obj)  ; clothes are now hanging on the object
)

Combining these parts, the complete hang_up_clothes action becomes:
(:action hang_up_clothes
  :parameters (?char - character ?clothes - object ?hang_obj - object)
  :precondition (or
    (and
      (clothes ?clothes)
      (hangable ?hang_obj)
      (holds_rh ?char ?clothes)
      (next_to ?char ?hang_obj)
    )
    (and
      (clothes ?clothes)
      (hangable ?hang_obj)
      (holds_lh ?char ?clothes)
      (next_to ?char ?hang_obj)
    )
  )
  :effect (and
    (when (holds_rh ?char ?clothes)(not (holds_rh ?char ?clothes))) 
    (when (holds_lh ?char ?clothes)(not (holds_lh ?char ?clothes))) 
    (obj_ontop ?clothes ?hang_obj) 
  )
)

Above is a good example of given predicates in domain file, problem file, action names and parameters, how to reason step by step and write the action body in PDDL. Pay attention to the usage of different connectives and their underlying logic.

Here are canonical, planner-friendly templates for common actions in this domain:

; movement
(:action walk_towards
  :parameters (?char - character ?obj - object)
  :precondition (and (not (next_to ?char ?obj))) ; keep it minimal; do NOT change inside/room here
  :effect (next_to ?char ?obj)
)

; power
(:action switch_on
  :parameters (?char - character ?obj - object)
  :precondition (and (has_switch ?obj) (off ?obj) (next_to ?char ?obj) (plugged_in ?obj))
  :effect (and (on ?obj) (not (off ?obj)))
)

; pick up (default to right hand, ensure capacity)
(:action grab
  :parameters (?char - character ?obj - object)
  :precondition (and
    (grabbable ?obj)
    (next_to ?char ?obj)
    (not (exists (?x - object) (holds_rh ?char ?x)))
  )
  :effect (and
    (holds_rh ?char ?obj)
    ; clear previous placements of the object (bounded cleanup)
    (forall (?c - object) (when (obj_inside ?obj ?c) (not (obj_inside ?obj ?c))))
    (forall (?s - object) (when (obj_ontop ?obj ?s) (not (obj_ontop ?obj ?s))))
  )
)

; place on a surface
(:action put_on
  :parameters (?char - character ?obj1 - object ?obj2 - object)
  :precondition (or
    (and (holds_rh ?char ?obj1) (next_to ?char ?obj2))
    (and (holds_lh ?char ?obj1) (next_to ?char ?obj2))
  )
  :effect (and
    (obj_ontop ?obj1 ?obj2)
    (when (holds_rh ?char ?obj1) (not (holds_rh ?char ?obj1)))
    (when (holds_lh ?char ?obj1) (not (holds_lh ?char ?obj1)))
    ; optional: if object was inside something, clear that relation
    (forall (?c - object) (when (obj_inside ?obj1 ?c) (not (obj_inside ?obj1 ?c))))
  )
)

; place into a container
(:action put_inside
  :parameters (?char - character ?obj1 - object ?obj2 - object)
  :precondition (or
    (and (holds_rh ?char ?obj1) (containers ?obj2) (open ?obj2) (next_to ?char ?obj2))
    (and (holds_lh ?char ?obj1) (containers ?obj2) (open ?obj2) (next_to ?char ?obj2))
  )
  :effect (and
    (obj_inside ?obj1 ?obj2)
    (when (holds_rh ?char ?obj1) (not (holds_rh ?char ?obj1)))
    (when (holds_lh ?char ?obj1) (not (holds_lh ?char ?obj1)))
    ; optional: clear any prior on-top relation
    (forall (?s - object) (when (obj_ontop ?obj1 ?s) (not (obj_ontop ?obj1 ?s))))
  )
)

; simple gesture example
(:action bow
  :parameters (?char - character ?target - character)
  :precondition (next_to ?char ?target)
  :effect ()
)

hint:
1. Precondition shape: Use DNF (an OR of AND groups). If only one case, a single AND group is enough.
2. Effects: Only use and, not, when, forall. Do NOT use or or exists in effects. Avoid empty (and). If an action truly has no precondition, write :precondition ().
3. Keep movement semantics simple: walk_towards must only assert (next_to ?char ?obj). Do NOT modify inside/inside_room in movement actions.
4. switch_on should require (has_switch ?obj) (off ?obj) (next_to ?char ?obj) and (plugged_in ?obj) when power is needed; do NOT require unrelated facts like (closed ?obj).
5. Maintain invariants: when you grab, you should not leave the object both held and placed. Use targeted conditional deletions (bounded forall with when) tied to the acted-on object; avoid global, unconstrained cleanups.
6. You MUST only use predicates and object types exactly as they appear in the domain file at the beginning.
7. Use and only use the arguments provided in :parameters for each action. Don't propose additional parameters; quantifiers (exists/forall) are fine inside conditions where allowed.
8. It is possible that an action has no precondition or no effect; if so, keep it empty with ().
9. The KEY of the task is to ensure the goal is reachable from the init using your actions. Be minimal and consistent to reduce search timeouts.
10. When there is only one predicate, do not wrap it in logic connectives.

For actions to be finished, write their preconditions and effects, and return in standard PDDL format:
(:action [action name]
  :parameters ([action parameters])
  :precondition ([action precondition])
  :effect ([action effect]) 
)
Concatenate all actions PDDL string into a single string. Output in json format where key is "output" and value is your output string: {"output": YOUR OUTPUT STRING}

Input:
<problem_file>
<action_handlers>

Output:
"""

if __name__ == "__main__":
    pass