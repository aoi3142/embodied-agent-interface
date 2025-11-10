prompt="""
Your primary task is to interpret a natural language goal for a household robot and translate it into a precise symbolic representation that captures the final desired state of the environment. Represent this with:
- node goals (target object states),
- edge goals (target object relationships), and
- action goals (only when the action itself is the objective).

Input: You will receive the goal's name and description, a list of relevant objects with their initial/possible states, all available relationship types, and a list of possible actions.

Output: Return a single valid JSON object with exactly these keys: {'node goals': [], 'edge goals': [], 'action goals': []}.

Reasoning Process (follow in order):
1) Identify the core objective: From `goal_str`, determine the final outcome that must be true when the goal is achieved.
2) Final states (node goals): Add only the minimal set of final object states required by the objective.
    - Choose states only from each object's `possible states`.
    - Do not include initial, intermediate, contextual, or posture/location states unless they are explicitly the goal.
    - Use: {'name': 'object_name', 'state': 'final_state'}.
3) Final relationships (edge goals): Add required spatial/holding relations that must hold in the final state.
    - Use only relations in `relation_types` and ensure 'to_name' is allowed by `rel_obj_pairs`.
    - Use: {'from_name': 'object_A', 'relation': 'RELATION_TYPE', 'to_name': 'object_B'}.
4) Mandatory actions (action goals): Include only if the action is the explicit objective or cannot be captured by node/edge goals alone.
    - Examples: TYPE for “Write an email”; TOUCH|PUSH for “Change TV channel”.
    - Do NOT use actions for navigation/manipulation/posture (WALK, FIND, GRAB, PUTIN, OPEN, CLOSE, SWITCHON/OFF, SIT, LIE) unless the action itself is the goal; prefer node/edge goals for the outcome instead.
    - Use: {'action': 'ACTION_NAME', 'description': 'brief specific description including target object(s)'}.

Critical principles (address common errors):
• Minimality: Include only what is necessary to satisfy the goal. Do not add extra states like character SITTING or chair OCCUPIED, room INSIDE, or FACING unless the description explicitly makes them the objective or they are required by the task semantics.
• Device power states: When the objective turns a powered device ON (light, computer, television, washing_machine, freezer/microwave), add ON and also PLUGGED_IN if that state exists for the device in `possible states`. Do not invent unrelated states like FULL, DIRTY, or OCCUPIED.
• Correct object class: Use the exact object class mentioned or implied. If both 'light' and 'floor_lamp' exist and the goal says “turn on the lights,” use the 'light' objects, not 'floor_lamp', unless the description explicitly targets the lamp.
• Relations vs states: Prefer relations to represent interactions/placements and avoid misusing object states.
  - Use ON to place items on appliances/surfaces; use INSIDE for containment (e.g., groceries in freezer).
  - Use HOLDS_LH/HOLDS_RH to represent the character holding tools (e.g., toothbrush, toothpaste, remote_control) rather than making those tools DIRTY/OPEN unless explicitly required.
  - For TV channel change: include the remote in a HOLDS_* relation and use action TOUCH|PUSH to indicate changing the channel; also ensure the television is ON (and PLUGGED_IN if applicable).
• Multi-instance scope: If the description clearly refers to plural or “all” (e.g., “turn on the lights”), add goals for each relevant instance of that class present in the scene. If it refers to a specific subset, add only those. When ambiguous, choose the minimal set that satisfies the wording.
• Containers and insertion: When the goal is “put X in Y,” add INSIDE edges for the explicitly mentioned items only. Keep the set minimal; do not add extra items not named or clearly implied. If Y is a powered container (e.g., freezer/fridge) and OPEN/PLUGGED_IN are in `possible states`, set Y to OPEN and PLUGGED_IN to reflect a valid placement-ready powered container.
• Washing clothes: Reflect the final operational state and placements, not “amount” states. For a running washer, set washing_machine to ON (and CLOSED, PLUGGED_IN if these states exist) and add ON edges from clothes/soap to the washing_machine when the description implies they are loaded on/into it.
• Toilet-related goals: Match the description’s intent with the minimal relation:
  - “Go to the bathroom and look at the toilet” → INSIDE bathroom and FACING toilet.
  - “Sit on the toilet” → ON relation from character to toilet (do not add OPEN/OCCUPIED unless the text explicitly requires it).

Validation checklist before output:
- Use only states listed in each object's `possible states`.
- Every relation's 'to_name' is allowed by `rel_obj_pairs` for that relation.
- Prefer node/edge goals to represent switch/door outcomes instead of action goals.
- Avoid adding extra nodes/edges/actions that are not strictly required by the description.
- Ensure the JSON is syntactically valid and uses exactly the three required top-level keys.

Reference examples (illustrative, adapt to the provided scene):
1) Turn on lights
    - node goals: each light {'state': 'ON'} and, if available, {'state': 'PLUGGED_IN'} for those lights.
    - no action goals for SWITCHON; represent with states only.
2) Wash clothes
    - node goals: washing_machine {'state': 'ON'} plus {'state': 'CLOSED'} and {'state': 'PLUGGED_IN'} if available.
    - edge goals: clothes and soap ON washing_machine if described as loaded.
3) Brush teeth
    - edge goals: character HOLDS_* toothbrush and HOLDS_* tooth_paste.
    - no node goals like toothbrush DIRTY or toothpaste OPEN unless explicitly stated.
4) Change TV channel
    - node goals: television {'state': 'ON'} and {'state': 'PLUGGED_IN'} if available.
    - edge goals: character FACING television and HOLDS_* remote_control (hand choice arbitrary).
    - action goals: {'action': 'TOUCH|PUSH', 'description': 'change channel using the remote_control'}.
5) Work
    - node goals: computer {'state': 'ON'}.
    - no posture (SITTING), chair OCCUPIED, INSIDE, or FACING unless explicitly required.

Relevant objects in the scene are:
<object_in_scene>

All possible relationships are the keys of the following dictionary, and the corresponding values are their descriptions:
<relation_types>

Each relation has a fixed set of objects to be its 'to_name' target. Here is a dictionary where keys are 'relation' and corresponding values are its possible set of 'to_name' objects:
<rel_obj_pairs>

Below is a dictionary of possible actions, whose keys are all possible actions and values are corresponding descriptions.
<action_space>

Goal name and goal description:
<goal_str>

Now output the symbolic version of the goal in the specified JSON format.
"""

if __name__ == "__main__":
    pass