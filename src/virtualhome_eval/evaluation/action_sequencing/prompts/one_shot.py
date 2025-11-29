prompt = """
The task is to guide the robot from the current state to fulfill node goals, edge goals, and action goals. You receive: relevant objects, current nodes & edges, and desired goals. You must output a JSON list of action dictionaries that, when executed in order, achieves ALL goals while obeying action preconditions and logical procedural steps.

Data format reminders:
Objects in scene: <object_name> (object_id)
Nodes: object_name, states: [...], properties:[...]
Edges: <object_name A> (idA) is RELATION to <object_name B> (idB)
Node goals: object_name is STATE
Edge goals: object_name A is RELATION to object_name B
Action goals: Required actions (each line either a single action or several joined by OR). For OR lines choose EXACTLY ONE action.

Action command encoding:
[] -> 0 objects
[obj, obj_id] -> 1 object
[obj1, obj1_id, obj2, obj2_id] -> 2 objects
JSON list order = execution order. Each element: {"ACTION": [args...]}

Example:
[
  {"FIND": ["sink", "sink_id"]},
  {"PUTBACK": ["cup", "cup_id", "sink", "sink_id"]}
]

Preconditions examples:
SWITCHON requires target HAS_SWITCH.
POUR requires source (POURABLE & DRINKABLE) and target RECIPIENT; source must be held (GRAB done earlier) and accessible (OPEN container if inside & CLOSED).

Action Definitions Format:
Action Name | Parameter count | Per-object precondition lists.

Supported Actions List:
CLOSE: (1, [['CAN_OPEN']]) # Change state from OPEN to CLOSED
DRINK: (1, [['DRINKABLE', 'RECIPIENT']]) # Consume a drinkable item
FIND: (1, [obj]) # Locate and approach an item
WALK: (1, [obj]) # Move towards something
GRAB: (1, [['GRABBABLE']]) # Take hold of an item that can be grabbed
LOOKAT: (1, [obj]) # Direct your gaze towards something
OPEN: (1, [['CAN_OPEN']]) # Open an item that can be opened
POINTAT: (1, [obj]) # Point towards something
PUTBACK: (2, [['GRABBABLE'], obj]) # Place one object back onto or into another
PUTIN: (2, [['GRABBABLE'], ['CAN_OPEN']]) # Insert one object into another
RUN: (1, [obj]) # Run towards something
SIT: (1, [['SITTABLE']]) # Sit on a suitable object
STANDUP: (0, [   ]) # Stand up from a sitting or lying position
SWITCHOFF: (1, [['HAS_SWITCH']]) # Turn off an item with a switch
SWITCHON: (1, [['HAS_SWITCH']]) # Turn on an item with a switch
TOUCH: (1, [obj]) # Physically touch something
TURNTO: (1, [obj]) # Turn your body to face something
WATCH: (1, [obj]) # Observe something attentively
WIPE: (1, [obj]) # Clean or dry something by rubbing
PUTON: (1, [['CLOTHES']]) # Dress oneself with the item of clothing currently held
PUTOFF: (1, [['CLOTHES']]) # Remove an item of clothing
GREET: (1, [['PERSON']]) # Offer a greeting to a person
DROP: (1, [obj]) # Let go of something so it falls
READ: (1, [['READABLE']]) # Read text from an object
LIE: (1, [['LIEABLE']]) # Lay oneself down on an object
POUR: (2, [['POURABLE', 'DRINKABLE'], ['RECIPIENT']]) # Transfer a liquid from one container to another
PUSH: (1, [['MOVABLE']]) # Exert force on something to move it away from you
PULL: (1, [['MOVABLE']]) # Exert force on something to bring it towards you
MOVE: (1, [['MOVABLE']]) # Change the location of an object
WASH: (1, [obj]) # Clean something by immersing and agitating it in water
RINSE: (1, [obj]) # Remove soap from something by applying water
SCRUB: (1, [obj]) # Clean something by rubbing it hard with a brush
SQUEEZE: (1, [['CLOTHES']]) # Compress clothes to extract liquid
PLUGIN: (1, [['HAS_PLUG']]) # Connect an electrical device to a power source
PLUGOUT: (1, [['HAS_PLUG']]) # Disconnect an electrical device from a power source
CUT: (1, [['EATABLE', 'CUTTABLE']]) # Cut some food
EAT: (1, [['EATABLE']]) # Eat some food
RELEASE: (1, [obj]) # Let go of something inside the current room
TYPE: (1, [['HAS_SWITCH']]) # Type on a keyboard

Notice (core rules):
1. CLOSE changes OPEN -> CLOSED only if currently OPEN.
2. Never attempt to PUTIN <character> <room>; use WALK for room changes.
3. Do NOT use character as an action argument.
4. Action names are UPPER CASE.
5. If unsure you are NEAR an object, WALK to it first. Do not act from afar.
6. Always include IDs with object names.
7. Output must be non-empty.
8. To act on an object in another room: WALK that object (or its room) first.

Additional critical rules to prevent common errors:
9. ROOM TRANSITION: If current INSIDE room differs from target object's room/context, include a WALK to object (or its room) before other actions.
10. LOCALIZATION: For small or newly referenced objects, sequence: WALK -> FIND (once) -> next interaction (GRAB / OPEN / SWITCHON etc.). Skip FIND only if already clearly NEAR (explicit NEAR/ON edge given).
11. ACTION GOALS OR LINES: For each OR line choose exactly ONE action; never output both. If an action appears (e.g., SLEEP) you must output that exact action.
12. PRECONDITIONS: Ensure states before action. Example: SWITCHON only after (a) device is PLUGGED_IN (PLUGIN if PLUGGED_OUT) and (b) proximity established via WALK/FIND.
13. DEVICE ACTIVATION TEMPLATE (unplugged device): WALK device -> (FIND if needed) -> PLUGIN (if PLUGGED_OUT) -> SWITCHON.
14. COMPUTER USAGE (if chair present): WALK/FIND chair -> SIT -> WALK/FIND computer -> SWITCHON. Do not SWITCHON before being proximate; SIT usually precedes activation in seated contexts.
15. TELEVISION VIEWING: SWITCHON before WATCH / LOOKAT. If seating (couch/chair) exists and viewing implied, SIT first, then TURNTO television, then LOOKAT or WATCH.
16. DRINKING PATTERNS:
   a) Filled accessible container: WALK -> FIND (if needed) -> GRAB -> DRINK.
   b) Need to fill: OPEN storage (if CLOSED) -> FIND & GRAB container -> FIND & GRAB liquid source -> POUR -> DRINK -> CLOSE storage if reopened.
   c) Never POUR without GRABbing source first.
17. HAND WASHING / RINSING: WALK sink/faucet -> FIND faucet -> SWITCHON faucet -> (optional FIND & GRAB soap) -> SCRUB (if soap) -> RINSE -> SWITCHOFF faucet -> (optional FIND & GRAB towel) -> WIPE. Do not RINSE before water available.
18. AVOID DUPLICATES: Do not repeat identical actions on same object unless they change state (e.g., cannot DRINK same glass twice without refill).
19. NO HALLUCINATION: Do not assume PLUGGED_IN, OPEN, or NEAR states that are not listed; add necessary actions instead.
20. CHECKLIST BEFORE OUTPUT: Each action has prior proximity, preconditions satisfied, OR lines each satisfied exactly once, no redundant repeats, logical ordering (e.g., SWITCHON before WATCH, GRAB source before POUR).
21. Economy: Provide all needed steps, but exclude decorative / purposeless actions.

Conflict resolution priority: (1) Fulfill action goal lines exactly; (2) Maintain preconditions & spatial correctness; (3) Avoid redundancy.

Input:
The relevant objects in the scene are:
<object_in_scene>

The current environment state is
<cur_change>

Node goals are:
<node_goals>

Edge goals are:
<edge_goals>

Action goals are:
<action_goals>

Output ONLY the JSON action command list (no commentary, no extra text):
"""

if __name__ == "__main__":
    pass