prompt="""

Problem:
You are designing instructions for a household robot. 
The goal is to guide the robot to modify its environment from an initial state to a desired final state. 
The input will be the initial environment state, the target environment state, the objects you can interact with in the environment. 
The output should be a list of action commands so that after the robot executes the action commands sequentially, the environment will change from the initial state to the target state. 

Data format: After # is the explanation.

Format of the states:
The environment state is a list that starts with a unary predicate or a binary predicate, followed by one or two objects.
You will be provided with multiple environment states as the initial state and the target state.
For example:
['inside', 'strawberry_0', 'fridge_97'] #strawberry_0 is inside fridge_97
['not', 'sliced', 'peach_0'] #peach_0 is not sliced
['ontop', 'jar_1', 'countertop_84'] #jar_1 is on top of countertop_84

Format of the action commands:
Action commands is a dictionary with the following format:
{{
        "action": "action_name", 
        "object": "target_obj_name",
}}

or 

{{
        "action": "action_name", 
        "object": "target_obj_name1,target_obj_name2",
}}

The action_name must be one of the following:
LEFT_GRASP # the robot grasps the object with its left hand, to execute the action, the robot's left hand must be empty, e.g. {{'action': 'LEFT_GRASP', 'object': 'apple_0'}}.
RIGHT_GRASP # the robot grasps the object with its right hand, to execute the action, the robot's right hand must be empty, e.g. {{'action': 'RIGHT_GRASP', 'object': 'apple_0'}}.
LEFT_PLACE_ONTOP # the robot places the object in its left hand on top of the target object and release the object in its left hand, e.g. {{'action': 'LEFT_PLACE_ONTOP', 'object': 'table_1'}}.
RIGHT_PLACE_ONTOP # the robot places the object in its right hand on top of the target object and releases the object in its right hand, e.g. {{'action': 'RIGHT_PLACE_ONTOP', 'object': 'table_1'}}.
LEFT_PLACE_INSIDE # the robot places the object in its left hand inside the target object and release the object in its left hand, to execute the action, the robot's left hand must hold an object, and the target object can't be closed e.g. {{'action': 'LEFT_PLACE_INSIDE', 'object': 'fridge_1'}}.
RIGHT_PLACE_INSIDE # the robot places the object in its right hand inside the target object and releases the object in its right hand, to execute the action, the robot's right hand must hold an object, and the target object can't be closed, e.g. {{'action': 'RIGHT_PLACE_INSIDE', 'object': 'fridge_1'}}.
RIGHT_RELEASE # the robot directly releases the object in its right hand; to execute, the robot's right hand must be holding an object, e.g. {{'action': 'RIGHT_RELEASE', 'object': 'apple_0'}}.
LEFT_RELEASE # the robot directly releases the object in its left hand; to execute, the robot's left hand must be holding an object, e.g. {{'action': 'LEFT_RELEASE', 'object': 'apple_0'}}.
OPEN # the robot opens the target object, to execute the action, the target object should be openable and closed, e.g. {{'action': 'OPEN', 'object': 'fridge_1'}}.
CLOSE # the robot closes the target object, to execute the action, the target object should be openable and open, e.g. {{'action': 'CLOSE', 'object': 'fridge_1'}}.
COOK # the robot cooks the target object, to execute the action, the target object should be put in a pan, e.g. {{'action': 'COOK', 'object': 'apple_0'}}.
CLEAN # the robot cleans the target object; to execute, the robot should have a cleaning tool such as a rag, the cleaning tool should be soaked if possible, or the target object should be put into a toggled-on cleaner like a sink or a dishwasher. Do not CLEAN objects that are already clean (not dusty/stained). e.g. {{'action': 'CLEAN', 'object': 'window_0'}}.
FREEZE # the robot freezes the target object e.g. {{'action': 'FREEZE', 'object': 'apple_0'}}.
UNFREEZE # the robot unfreezes the target object, e.g. {{'action': 'UNFREEZE', 'object': 'apple_0'}}.
SLICE # the robot slices the target object; to execute, the robot should have a knife in one hand and at least one hand free to operate as required, e.g. {{'action': 'SLICE', 'object': 'apple_0'}}.
SOAK # the robot soaks the target object, to execute the action, the target object must be put in a toggled on sink, e.g. {{'action': 'SOAK', 'object': 'rag_0'}}.
DRY # the robot dries the target object, e.g. {{'action': 'DRY', 'object': 'rag_0'}}.
TOGGLE_ON # the robot toggles on the target object, to execute the action, if the target object is openable (e.g., dishwasher), the target object must be first closed, e.g. {{'action': 'TOGGLE_ON', 'object': 'light_0'}}.
TOGGLE_OFF # the robot toggles off the target object, e.g. {{'action': 'TOGGLE_OFF', 'object': 'light_0'}}.
LEFT_PLACE_NEXTTO # the robot places the object in its left hand next to the target object and release the object in its left hand, e.g. {{'action': 'LEFT_PLACE_NEXTTO', 'object': 'table_1'}}.
RIGHT_PLACE_NEXTTO # the robot places the object in its right hand next to the target object and release the object in its right hand, e.g. {{'action': 'RIGHT_PLACE_NEXTTO', 'object': 'table_1'}}.
LEFT_TRANSFER_CONTENTS_INSIDE # the robot transfers the contents in the object in its left hand inside the target object, e.g. {{'action': 'LEFT_TRANSFER_CONTENTS_INSIDE', 'object': 'bow_1'}}.
RIGHT_TRANSFER_CONTENTS_INSIDE # the robot transfers the contents in the object in its right hand inside the target object, e.g. {{'action': 'RIGHT_TRANSFER_CONTENTS_INSIDE', 'object': 'bow_1'}}.
LEFT_TRANSFER_CONTENTS_ONTOP # the robot transfers the contents in the object in its left hand on top of the target object, e.g. {{'action': 'LEFT_TRANSFER_CONTENTS_ONTOP', 'object': 'table_1'}}.
RIGHT_TRANSFER_CONTENTS_ONTOP # the robot transfers the contents in the object in its right hand on top of the target object, e.g. {{'action': 'RIGHT_TRANSFER_CONTENTS_ONTOP', 'object': 'table_1'}}.
LEFT_PLACE_NEXTTO_ONTOP # the robot places the object in its left hand next to target object 1 and on top of the target object 2 and release the object in its left hand, e.g. {{'action': 'LEFT_PLACE_NEXTTO_ONTOP', 'object': 'window_0, table_1'}}.
RIGHT_PLACE_NEXTTO_ONTOP # the robot places the object in its right hand next to object 1 and on top of the target object 2 and release the object in its right hand, e.g. {{'action': 'RIGHT_PLACE_NEXTTO_ONTOP', 'object': 'window_0, table_1'}}.
LEFT_PLACE_UNDER # the robot places the object in its left hand under the target object and release the object in its left hand, e.g. {{'action': 'LEFT_PLACE_UNDER', 'object': 'table_1'}}.
RIGHT_PLACE_UNDER # the robot places the object in its right hand under the target object and release the object in its right hand, e.g. {{'action': 'RIGHT_PLACE_UNDER', 'object': 'table_1'}}.

Format of the interactable objects:
Interactable objects will contain multiple lines, each line is a dictionary with the following format:
{{
    "name": "object_name",
    "category": "object_category"
}}
object_name is the name of the object, which you must use in the action command, object_category is the category of the object, which provides a hint for you in interpreting initial and goal condtions.

Please pay special attention:
1. Hand capacity and availability:
    - The robot can only hold one object in each hand. If both hands are occupied, PLACE or RELEASE an object to free a hand before GRASP, OPEN, CLOSE, TOGGLE, SLICE, or CLEAN.
    - Actions OPEN, CLOSE, TOGGLE_ON/OFF, SLICE, CLEAN require at least one free hand.
2. Valid actions and object names:
    - Action name must be one of the above, and the object name must be one of the interactable objects.
3. PLACE and RELEASE semantics:
    - All PLACE actions release the object in that hand automatically. Do not call RELEASE immediately after a PLACE.
    - RIGHT_RELEASE/LEFT_RELEASE require the corresponding hand to be holding something.
4. Multi-target PLACE (NEXTTO_ONTOP):
    - For LEFT_PLACE_NEXTTO_ONTOP and RIGHT_PLACE_NEXTTO_ONTOP, use {{'action': 'action_name', 'object': 'obj_name1, obj_name2'}}.
5. Container access and gating:
    - You cannot GRASP from or PLACE into a closed container (e.g., cabinet, fridge, jar). OPEN it first. Only CLOSE if the target state requires it or to enable a device (e.g., dishwasher before TOGGLE_ON).
6. State-aware actions (avoid no-ops):
    - Only OPEN if the object is closed; only CLOSE if it is open and needed; only CLEAN if the object is dusty/stained; avoid repeating CLEAN after the state is satisfied.
7. Preconditioned actions:
    - CLEAN requires a soaked cleaning tool (e.g., rag) when applicable, or the target object placed into a toggled-on cleaner (sink/dishwasher).
    - SOAK requires the target object placed in a toggled-on sink.
8. Slicing and post-slice affordances:
    - Before slicing, interact with the whole object (e.g., peach_0). After SLICE, the original becomes parts named like peach_0_part_0, peach_0_part_1, ... You must interact with these parts thereafter (do not refer to the original whole).
9. Quantifiers and goal coverage:
    - If the target state includes quantifiers like 'forall', 'exists', 'forpairs', or 'forn', plan to satisfy ALL required instances, pairing or counting deterministically as needed (e.g., pair basket_i with item_i in order). Do not stop after partially satisfying a universal condition.
10. Planning discipline:
    - Sequence actions to satisfy preconditions before effects (e.g., open container, ensure hand free, position tool, then act).
    - Do not include redundant or contradictory actions. Keep the action list minimal while fully satisfying the target state.

Examples: after# is the explanation.

Example 1:
Input:
initial environment state:
['stained', 'sink_7']
['stained', 'bathtub_4']
['not', 'soaked', 'rag_0']
['onfloor', 'rag_0', 'room_floor_bathroom_0']
['inside', 'rag_0', 'cabinet_1']
['not', 'open', 'cabinet_1']


target environment state:
['not', 'stained', 'bathtub_4']
['not', 'stained', 'sink_7']
['and', 'soaked', 'rag_0', 'inside', 'rag_0', 'bucket_0']


interactable objects:
{{'name': 'sink_7', 'category': 'sink.n.01'}}
{{'name': 'bathtub_4', 'category': 'bathtub.n.01'}}
{{'name': 'bucket_0', 'category': 'bucket.n.01'}}
{{'name': 'rag_0', 'category': 'rag.n.01'}}
{{'name': 'cabinet_1', 'category': 'cabinet.n.01'}}


Please output the list of action commands (in the given format) so that after the robot executes the action commands sequentially, the current environment state will change to target environment state. Usually, the robot needs to execute multiple action commands consecutively to achieve final state. Please output multiple action commands rather than just one. Only output the list of action commands with nothing else.

Output:
[
    {{
        "action": "OPEN",
        "object": "cabinet_1"
    }}, # you want to get the rag_0 from cabinet_1, should open it first
    {{
        "action": "RIGHT_GRASP",
        "object": "rag_0"
    }}, # you want to clean the sink_7 and bathtub_4, you found them stained, so you need to soak the rag_0 first
    {{
        "action": "RIGHT_PLACE_INSIDE",
        "object": "sink_7"
    }}, # to soak the rag_0, you need to place it inside the sink_7
    {{
        "action": "TOGGLE_ON",
        "object": "sink_7"
    }}, # to soak the rag_0, you need to toggle on the sink_7
    {{
        "action": "SOAK",
        "object": "rag_0"
    }}, # now you can soak the rag_0
    {{
        "action": "TOGGLE_OFF",
        "object": "sink_7"
    }}, # after soaking the rag_0, you need to toggle off the sink_7
    {{
        "action": "LEFT_GRASP",
        "object": "rag_0"
    }}, # now you can grasp soaked rag_0 to clean stain
    {{
        "action": "CLEAN",
        "object": "sink_7"
    }}, # now you clean the sink_7
    {{
        "action": "CLEAN",
        "object": "bathtub_4"
    }}, # now you clean the bathtub_4
    {{
        "action": "LEFT_PLACE_INSIDE",
        "object": "bucket_0"
    }} # after cleaning the sink_7, you need to place the rag_0 inside the bucket_0
]

Your task:
Input:
initial environment state:
{init_state}

target environment state:
{target_state}

interactable objects:
{obj_list}

Please output the list of action commands (in the given format) so that after the robot executes the action commands sequentially, the current environment state will change to target environment state. Usually, the robot needs to execute multiple action commands consecutively to achieve final state. Please output multiple action commands rather than just one. Only output the list of action commands with nothing else.

Output:
"""


if __name__ == "__main__":
    print(prompt.format(init_state=123,target_state=456,obj_list="123"))
    