prompt="""
Your task is to convert natural language goals into symbolic goals with maximal F1 by avoiding extra items and not missing required ones. You must reason about object end states, relationships, and only add actions that are strictly necessary beyond states/relations.

Inputs:
- Goal name and description
- Relevant objects with initial and possible states
- Allowed relations and their target objects

Output JSON must have exactly three keys: 'node goals', 'edge goals', 'action goals'.

Strict generation rules (follow in order):
1) Verb-to-state normalization
    - Map goal verbs to end states whenever possible:
        • turn on -> target object's state: ON
        • turn off -> OFF
        • open -> OPEN, close -> CLOSED
        • sit/lie -> character end state: SITTING/LYING or relation ON target if required by spec
    - Do NOT add a SWITCHON/SWITCHOFF action if the desired end state fully captures the goal.

2) Action minimality (strong filter)
    - Only include actions when node/edge goals cannot encode the goal's completion.
    - Navigation/setup actions (WALK, FIND, LOOKAT, TURNTO) are forbidden unless explicitly required by the goal and cannot be represented with states/relations.
    - Limit actions to fewer than three and prefer canonical actions: TYPE, SLEEP, RINSE, WASH, TOUCH|PUSH (button press), DRINK, READ.
    - Use the canonical action names exactly as provided; do not paraphrase descriptions.

3) Relation inference and validation
    - When text says put/place/load A in/on B, infer an edge:
        • Washing machine/dishwasher: use relation ON to the appliance (dataset convention).
        • Freezer/fridge: use INSIDE to the freezer.
    - Relations must be one of {ON, INSIDE, BETWEEN, CLOSE, FACING, HOLDS_RH, HOLDS_LH} and 'to_name' must be in the allowed set for that relation.
    - Prefer relations over actions like PUTIN unless relations suffice.

4) State pairing and deduplication
    - If a device being ON requires PLUGGED_IN in possible states, include both ON and PLUGGED_IN.
    - Do not repeat identical node goals; remove duplicates.
    - Do not add states for peripheral objects unless explicitly required.

5) Composite labels handling
    - If the goal implies alternatives like RINSE|WASH or TOUCH|PUSH, choose the minimal set that matches the described outcome (prefer both only when explicitly required).

6) Output format constraints
    - 'node goals': list of {'name': OBJECT_NAME, 'state': STATE} using only {CLOSED, OPEN, ON, OFF, SITTING, DIRTY, CLEAN, LYING, PLUGGED_IN, PLUGGED_OUT}.
    - 'edge goals': list of {'from_name': OBJECT_NAME, 'relation': RELATION, 'to_name': OBJECT_NAME} adhering to the allowed targets per relation:
        {'ON': {'table', 'character', 'dishwasher', 'toilet', 'oven', 'couch', 'bed', 'washing_machine', 'coffe_maker'},
        'HOLDS_LH': {'water_glass', 'novel', 'tooth_paste', 'keyboard', 'spectacles', 'toothbrush'},
        'HOLDS_RH': {'phone', 'mouse', 'water_glass', 'remote_control', 'address_book', 'novel', 'tooth_paste', 'cup', 'drinking_glass', 'toothbrush'},
        'INSIDE': {'home_office', 'hands_both', 'freezer', 'bathroom', 'dining_room'},
        'FACING': {'phone', 'toilet', 'television', 'computer', 'laptop', 'remote_control'},
        'CLOSE': {'shower', 'cat'}}
    - 'action goals': list of {'action': ACTION, 'description': DICTIONARY_DESCRIPTION} from the allowed dictionary below. Descriptions must match exactly.

Allowed actions dictionary:
{'CLOSE': 'as opposed to open sth, CLOSE sth means changing the state from OPEN to CLOSE, not get close to!', 'DRINK': 'drink up sth', 'FIND': 'find and get near to sth', 'WALK': 'walk towards sth, get near to sth', 'GRAB': 'grab sth', 'LOOKAT': 'look at sth, face sth', 'LOOKAT_SHORT': 'shortly look at sth', 'LOOKAT_LONG': 'look at sth for long', 'OPEN': 'open sth, as opposed to close sth', 'POINTAT': 'point at sth', 'PUTBACK': 'put object A back to object B', 'PUTIN': 'put object A into object B', 'PUTOBJBACK': 'put object back to its original place', 'RUN': 'run towards sth, get close to sth', 'SIT': 'sit on sth', 'STANDUP': 'stand up', 'SWITCHOFF': 'switch sth off (normally lamp/light)', 'SWITCHON': 'switch sth on (normally lamp/light)', 'TOUCH': 'touch sth', 'TURNTO': 'turn and face sth', 'WATCH': 'watch sth', 'WIPE': 'wipe sth out', 'PUTON': 'put on clothes, need to hold the clothes first', 'PUTOFF': 'take off clothes', 'GREET': 'greet to somebody', 'DROP': "drop something in robot's current room, need to hold the thing first", 'READ': 'read something, need to hold the thing first', 'LIE': 'lie on something, need to get close the thing first', 'POUR': 'pour object A into object B', 'TYPE': 'type on keyboard', 'PUSH': 'move sth', 'PULL': 'move sth', 'MOVE': 'move sth', 'WASH': 'wash sth', 'RINSE': 'rinse sth', 'SCRUB': 'scrub sth', 'SQUEEZE': 'squeeze the clothes', 'PLUGIN': 'plug in the plug', 'PLUGOUT': 'plug out the plug', 'CUT': 'cut some food', 'EAT': 'eat some food', 'RELEASE': 'drop sth inside the current room', 'SLEEP': 'go to sleep'}

Goal name and goal description:
<goal_str>

Relevant objects in the scene are:
<object_in_scene>

TEMPLATES (hints in brackets; adapt as needed; keep minimal and canonical) (ONLY USE OBJECTS THAT ARE IN THE SCENE):

Work
- node goals: [
    {'name': 'computer', 'state': 'ON'}
] OR [
    {'name': 'laptop', 'state': 'ON'}, {'name': 'laptop', 'state': 'PLUGGED_IN'}
] (Do not include character state, e.g., SITTING)
- edge goals: [] (No goals, do not include character relations, e.g., FACING computer)
- action goals: [] (No goals, do not include interaction with computer, e.g., TYPE, LOOKAT)

Browse internet
- node goals: [
    {'name': 'computer', 'state': 'ON'}
] OR [
    {'name': 'laptop', 'state': 'ON'}, {'name': 'laptop', 'state': 'PLUGGED_IN'}
]
- edge goals: [
    {'from_name': 'character', 'relation': 'FACING', 'to_name': 'computer'}
]
- action goals: [
    {'action': 'LOOKAT', 'description': 'look at sth, face sth'} (Mandatory)
]

Pick up phone
- node goals: [] (No goals)
- edge goals: [
    {'from_name': 'character', 'relation': 'HOLDS_RH', 'to_name': 'phone'} (Mandatory)
]
- action goals: [] (No goals)

Wash dishes with dishwasher
- node goals: [
    {'name': 'dishwasher', 'state': 'CLOSED'} (Mandatory),
    {'name': 'dishwasher', 'state': 'ON'} (Mandatory)
]
- edge goals: [
    {'from_name': <CUTLERY>, 'relation': 'ON', 'to_name': 'dishwasher'} (Repeat as needed, duplicate if multiple of same cutlery are present),
    {'from_name': 'dish_soap', 'relation': 'ON', 'to_name': 'dishwasher'} (Mandatory)
    ]
- action goals: [] (No goals)

Watch TV
- node goals: [
    {'name': 'television', 'state': 'ON'} (Mandatory),
    {'name': 'television', 'state': 'PLUGGED_IN'} (Mandatory)
] (Do not include character state, e.g., SITTING/LYING)
- edge goals: [
    {'from_name': 'character', 'relation': 'FACING', 'to_name': 'television'} (Mandatory)
] (Do not include character relation ON couch or HOLDS_RH remote_control)
- action goals: [
    {'action': 'WATCH', 'description': 'watch sth'} (Mandatory)
]

Write an email
- node goals: [
    {'name': 'computer', 'state': 'ON'}
] OR [
    {'name': 'laptop', 'state': 'ON'}, {'name': 'laptop', 'state': 'PLUGGED_IN'}
] (Do not include character state, e.g., SITTING/LYING)
- edge goals: [] (No goals, do not include character relations, e.g., FACING computer, INSIDE home_office)
- action goals: [
    {'action': 'TYPE', 'description': 'type on keyboard'} (Mandatory)
]

Wash clothes
- node goals: [
    {'name': 'washing_machine', 'state': 'CLOSED'} (Mandatory),
    {'name': 'washing_machine', 'state': 'ON'} (Mandatory),
    {'name': 'washing_machine', 'state': 'PLUGGED_IN'} (Mandatory)
]
- edge goals: [
    {'from_name': <CLOTHING>, 'relation': 'ON', 'to_name': 'washing_machine'} (Repeat as needed, duplicate if multiple of same clothing are present),
    {'from_name': <SOAP/DETERGENT>, 'relation': 'ON', 'to_name': 'washing_machine'} (Mandatory)
]
- action goals: [] (No goals)

Wash hands
- node goals: [] (No goals, do not include OFF faucet or hands CLEAN)
- edge goals: []
- action goals: [
    {'action': 'WASH', 'description': 'wash sth'}
]

Drink
- node goals: [] (No goals, do not include container state OPEN/CLOSED or OFF faucet)
- edge goals: [
    {'from_name': 'character', 'relation': 'HOLDS_RH', 'to_name': <CONTAINER>} (Mandatory)
]
- action goals: [
    {'action': 'DRINK', 'description': 'drink up sth'} (Mandatory)
] (Do not include action POUR)

Read book
- node goals: [] (No goals, do not include character state, e.g., SITTING/LYING, light state ON/PLUGGED_IN, or book state OPEN)
- edge goals: [
    {'from_name': 'character', 'relation': 'HOLDS_RH', 'to_name': <BOOK>} (Mandatory)
]
- action goals: [
    {'action': 'READ', 'description': 'read something, need to hold the thing first'} (Mandatory)
]

Change TV channel
- node goals: [
    {'name': 'television', 'state': 'ON'} (Mandatory),
    {'name': 'television', 'state': 'PLUGGED_IN'} (Mandatory)
] (Do not include character state, e.g., SITTING/LYING)
- edge goals: [
    {'from_name': 'character', 'relation': 'HOLDS_RH', 'to_name': 'remote_control'},
    {'from_name': 'character', 'relation': 'FACING', 'to_name': 'television'}
]
- action goals: [
    {'action': 'TOUCH', 'description': 'touch sth'} (Mandatory)
]

Make coffee
- node goals: [
    {'name': 'coffe_maker', 'state': 'CLOSED'} (Mandatory),
    {'name': 'coffe_maker', 'state': 'ON'} (Mandatory),
    {'name': 'coffe_maker', 'state': 'PLUGGED_IN'} (Mandatory)
] (Do not include cup state FULL)
- edge goals: [
    {'from_name': 'coffee_filter', 'relation': 'ON', 'to_name': 'coffe_maker'} (Mandatory),
    {'from_name': 'ground_coffee', 'relation': 'ON', 'to_name': 'coffe_maker'} (Mandatory)
] (Do not include water to be ON coffe_maker)
- action goals: [
    {'action': 'POUR', 'description': 'pour object A into object B'} (Mandatory)
]

Wash dishes by hand
- node goals: [] (No goals, do not include dishes CLEAN or faucet OFF)
- edge goals: [] (No goals)
- action goals: [
    {'action': 'WASH', 'description': 'wash sth'} (Mandatory),
    {'action': 'GRAB', 'description': 'grab sth'} (Mandatory)
]

Relax on sofa
- node goals: [
    {'name': 'character', 'state': <SITTING/LYING>} (Mandatory)
]
- edge goals: [
    {'from_name': 'character', 'relation': 'ON', 'to_name': 'couch'} (Mandatory)
]
- action goals: [] (No goals)

Listen to music
- node goals: [
    {'name': <DEVICE>, 'state': 'CLOSED'} (Mandatory),
    {'name': <DEVICE>, 'state': 'ON'} (Mandatory),
    {'name': <DEVICE>, 'state': 'PLUGGED_IN'} (Mandatory)
    ]
- edge goals: []
- action goals: [] (No goals)

Turn on light
- node goals: [
    {'name': 'light', 'state': 'ON'} (Mandatory),
    {'name': 'light', 'state': 'PLUGGED_IN'} (Mandatory)
] (Repeat for multiple lights if needed) OR [
    {'name': 'floor_lamp', 'state': 'ON'} (Mandatory)
]
- edge goals: [] (No goals)
- action goals: [] (No goals)

Cook some food
- node goals: [
    {'name': 'oven', 'state': 'CLOSED'} (Mandatory),
    {'name': 'oven', 'state': 'ON'} (Mandatory),
    {'name': 'oven', 'state': 'PLUGGED_IN'} (Mandatory)
] (Do not include food state COOKED or freezer state CLOSED)
- edge goals: [
    {'from_name': <COOKWARE>, 'relation': 'ON', 'to_name': 'oven'} (Mandatory)
]
- action goals: [] (No goals)

Pet cat
- node goals: [] (No goals, do not include character state, e.g., SITTING/LYING)
- edge goals: [
    {'from_name': 'character', 'relation': 'CLOSE', 'to_name': 'cat'} (Mandatory)
] (Do not include character/cat relation ON couch etc.)
- action goals: [
    {'action': 'TOUCH', 'description': 'touch sth'} (Mandatory)
]

Put groceries in Fridge
- node goals: [
    {'name': 'freezer', 'state': 'OPEN'} (Mandatory),
    {'name': 'freezer', 'state': 'PLUGGED_IN'} (Mandatory)
] (Do not include freezer state CLOSED)
- edge goals: [
    {'from_name': <ITEM>, 'relation': 'INSIDE', 'to_name': 'freezer'} (Optional)
]
- action goals: [] (No goals)

Set up table
- node goals: [] (No goals)
- edge goals: [
    {'from_name': <ITEM>, 'relation': 'ON', 'to_name': 'table'} (Repeat as needed)
]
- action goals: [] (No goals)

Wash teeth
- node goals: [] (No goals, do not include toothbrush/teeth state CLEAN/DIRTY or faucet ON/OFF, character INSIDE bathroom)
- edge goals: [
    {'from_name': 'character', 'relation': 'HOLDS_LH', 'to_name': 'toothbrush'} (Mandatory),
    {'from_name': 'character', 'relation': 'HOLDS_RH', 'to_name': 'tooth_paste'} (Mandatory)
]
- action goals: [] (No goals, do not include action RINSE/WASH)

Go to sleep
- node goals: [
    {'name': 'character', 'state': 'LYING'} (Mandatory)
]
- edge goals: [
    {'from_name': 'character', 'relation': 'ON', 'to_name': 'bed'} (Mandatory)
]
- action goals: [
    {'action': 'SLEEP', 'description': 'go to sleep'} (Mandatory)
]

Brush teeth
- node goals: [] (No goals, do not include toothbrush state CLEAN/DIRTY or faucet ON/OFF)
- edge goals: [
    {'from_name': 'character', 'relation': 'HOLDS_RH', 'to_name': 'toothbrush'} (Mandatory),
    {'from_name': 'character', 'relation': 'HOLDS_LH', 'to_name': 'tooth_paste'} (Mandatory)
] (Do not include character to be INSIDE bathroom)
- action goals: [] (No goals)

Go to toilet
- node goals: [] (No goals, do not include character state SITTING or object states, e.g., DIRTY/FLUSHED)
- edge goals: [
    {'from_name': 'character', 'relation': 'ON', 'to_name': 'toilet'} (Optional)
]
- action goals: [] (No goals, do not include WASH/TOUCH/WIPE)

Take shower
- node goals: [] (No goals, do not include shower state ON/OFF or character state CLEAN)
- edge goals: [
    {'from_name': 'character', 'relation': 'CLOSE', 'to_name': 'shower'} (Mandatory)
]
- action goals: [] (No goals, do not include action WASH)

Get some water
- node goals: [] (No goals)
- edge goals: [
    {'from_name': 'character', 'relation': 'INSIDE', 'to_name': 'dining_room'}
]
- action goals: [] (No goals)

Hint:
1. When required, "computer" needs only be "ON" but does not need to be "PLUGGED_IN", while "laptop" needs both "ON" and "PLUGGED_IN"
2. When required, "floor_lamp" needs only be "ON" but does not need to be "PLUGGED_IN", while "light" needs both "ON" and "PLUGGED_IN"

Now output only the JSON object: {'node goals': ..., 'edge goals': ..., 'action goals': ...} with no extra text.
"""

if __name__ == "__main__":
    pass