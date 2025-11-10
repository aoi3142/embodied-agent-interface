prompt = """
The task is to guide the robot to take actions from the current state to fulfill some node goals, edge goals, and action goals. The input will be the related objects in the scene, nodes and edges in the current environment, and the desired node goals, edge goals, and action goals. The output should be action commands in JSON format so that after the robot executes the action commands sequentially, the ending environment would satisfy the goals.

Data format:
Objects in the scene indicates those objects involved in the action execution. It follows the format: <object_name> (object_id)

Nodes and edges in the current environment shows the nodes' names, states and properties, and edges in the environment. 
Nodes follow the format: object_name, states:... , properties:...
Edges follow the format: object_name A is ... to object_name B
 
Node goals show the target object states in the ending environment. They follow the format: object_name is ... (some state)

Edge goals show the target relationships of objects in the ending environment. They follow the format: object_name A is ... (some relationship) to object_name B.

Action goals specify the necessary actions you need to include in your predicted action commands sequence, and the order they appear in action goals should also be the RELATIVE order they appear in your predicted action commands sequence if there are more than one line. Each line in action goals include one action or more than one actions concatenated by OR. You only need to include ONE of the actions concatenated by OR in the same line. For example, if the action goal is:
The following action(s) should be included:
GRAB
TYPE or TOUCH
OPEN
------------------------
Then your predicted action commands sequence should include GRAB, either TYPE or TOUCH, and OPEN. Besides, GRAB should be executed earlier than TYPE or TOUCH, and TYPE or TOUCH should be executed earlier than OPEN.
If the action goal is:
The following action(s) should be included:
There is no action requirement.
It means there is no action you have to include in output, and you can use any action to achieve the node and edge goals. Warning: No action requirement does not mean empty output. You should always output some actions and their arguments.

Action commands include action names and objects. Each action's number of objects is fixed (0, 1, or 2), and the output should include object names followed by their IDs:
[]: Represents 0 objects.
[object, object_id]: Represents 1 object.
[object 1, object_1_id, object 2, object_2_id]: Represents 2 objects.
The output must be in JSON format, where:
Each dictionary key is an action name.
Each dictionary value is a single list containing the objects (with their IDs) for the corresponding action.
The order of execution is determined by the order in which the key-value pairs appear in the JSON list.

STRICT JSON OUTPUT REQUIREMENTS:
- Output ONLY a JSON array of objects. No prose, no code fences, no bracketed pseudo-actions like "[WALK] <light> (411)".
- Every action object has exactly one key (UPPERCASE action name) and one value (a list of strings: [obj_name, obj_id, ...]).
- Use ONLY object names and IDs that appear in the input. Never invent objects or IDs.
- Always include the numeric IDs (as strings) for every object argument.

For example, If you want to first FIND the sink and then PUTBACK a cup into the sink, you should express it as:
[
  {"FIND": ["sink", "sink_id"]},
  {"PUTBACK": ["cup", "cup_id", "sink", "sink_id"]}
]

The object of action also needs to satisfied some properties preconditions. For example, SWITCHON's object number is 1. To switch on something, the object should 'HAS_SWITCH'. The rule is represented as SWITCHON = ("Switch on", 1, [['HAS_SWITCH']]). Another example is POUR. POUR's object number is 2. To pour sth A into sth B, A should be pourable and drinkable, and B should be RECIPIENT. The rule is represented as POUR = ("Pour", 2, [['POURABLE', 'DRINKABLE'], ['RECIPIENT']]).

Action Definitions Format:
Each action is defined as a combination of:
Action Name (String): A descriptive name for the action.
Required Number of Parameters (Integer): The count of parameters needed to perform the action.
Preconditions for Each Object (List of Lists of Strings): Conditions that must be met for each object involved in the action.

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

Notice:
1. CLOSE action is opposed to OPEN action, CLOSE sth means changing the object's state from OPEN to CLOSE. 

2. You cannot [PUTIN] <character> <room name>. If you want robot INSIDE some room, please [WALK] <room name>.

3. The subject of all these actions is <character>, that is, robot itself. Do not include <character> as object_name. NEVER EVER use character as any of the object_name, that is, the argument of actions.

4. The action name should be upper case without white space. 

5. Importantly, if you want to apply ANY action on <object_name>, you should NEAR it. Therefore, you should apply WALK action as [WALK] <object_name> to first get near to the object before you apply any following actions, if you have no clue you are already NEAR <object_name>

6. Output only object names and their IDs, not just the names.

7. Output should not be empty! Always output some actions and their arguments.

8. If you want to apply an action on an object, you should WALK to the object first. For example, if you want to apply an action to an item in another room, you should first WALK to that item, and then apply the action.

9. If an object is placed with a grabbable container, the container will inherit the properties of the object. For example, if water is DRINKABLE and it is contained in a cup, then the cup is also DRINKABLE.

Rules and recipes to avoid common mistakes (follow strictly):

R1. Always WALK before acting on an object.
- Before applying ANY action to an object, first WALK to that specific object.
- You may skip WALK only if the input explicitly states the character is NEAR that object (an "is NEAR to" edge) at the moment of action. When unsure, WALK.

R2. Use PLUGIN only when required by the state.
- Use PLUGIN only if the device has HAS_PLUG and its node state includes PLUGGED_OUT.
- If it is already PLUGGED_IN (or no plug state is given), do NOT add PLUGIN. Prefer SWITCHON directly for devices with HAS_SWITCH.

R3. Canonical action sequences (maintain this order):
- Power and use an electric device (e.g., computer, light, stereo):
  WALK device → (PLUGIN if PLUGGED_OUT) → SWITCHON device → then use it (e.g., TYPE, WATCH, etc.). Never TYPE/USE before SWITCHON.
- Washing hands/dishes: WALK faucet or sink area → SWITCHON faucet (if water source is needed/off) → WASH target → RINSE target.
- Getting a drink: WALK container (cup/glass) → GRAB container → If needed, WALK water source → (OPEN container/cupboard if the water is inside) → (SWITCHON faucet if needed) → POUR water into container → DRINK from container.

R4. Containers and access:
- If an object is INSIDE a CLOSED container, WALK the container → OPEN it before GRAB/PUTIN/PUTBACK.

R5. Goal-aligned final actions:
- For "character is ON to X": make SIT or LIE on X the last action relating to X.
- For "character is FACING/CLOSE to X": include TURNTO/LOOKAT/WATCH (as appropriate) after any necessary setup so the relation holds at the end.

R6. Avoid redundancy and no-ops:
- Do not repeat the same action on the same object consecutively (e.g., double LIE/DRINK/TOUCH).
- Do not act on irrelevant objects (e.g., WASH faucet itself).

R7. Prefer WALK over FIND when IDs are provided.
- Since inputs include object IDs, directly WALK to the target object instead of issuing FIND unless explicitly required by action goals.

R8. Never include <character> as an action object.
- The subject is always the character; action arguments must be non-character objects from the input list with their IDs.

Submission checklist (verify before outputting):
- Every acted-on object has a preceding WALK unless NEAR is explicitly given in the input just before that action.
- Devices to be used are SWITCHON before TYPE/WATCH/other usage, and PLUGIN is included only if PLUGGED_OUT.
- For washing: WASH occurs before RINSE.
- For items inside containers: OPEN precedes GRAB/PUTIN/PUTBACK.
- No duplicate consecutive actions on the same object; stop after goals are satisfied.
- Output is a pure JSON array with correct action objects and argument lists with IDs; no extra text.

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

Please output the list of action commands in json format so that after the robot executes the action commands sequentially, the ending environment would satisfy all the node goals, edge goals and action goals. The dictionary keys should be action names. The dictionary values should be a list containing the objects of the corresponding action. Only output the json of action commands in a dictionary with nothing else.

Output:
"""

if __name__ == "__main__":
    pass