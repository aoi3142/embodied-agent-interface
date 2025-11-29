prompt="""
Domain (types & predicates excerpt – use EXACT names and arities shown):
(define (domain igibson)
  (:requirements :strips :adl :typing :negative-preconditions)
  (:types vacuum_n_04 facsimile_n_02 dishtowel_n_01 apparel_n_01 seat_n_03 bottle_n_01 mouse_n_04 window_n_01 scanner_n_02 sauce_n_01 spoon_n_01 date_n_08 egg_n_02 cabinet_n_01 yogurt_n_01 parsley_n_02 notebook_n_01 dryer_n_01 saucepan_n_01 soap_n_01 package_n_02 headset_n_01 fish_n_02 vehicle_n_01 chestnut_n_03 grape_n_01 wrapping_n_01 makeup_n_01 mug_n_04 pasta_n_02 beef_n_02 scrub_brush_n_01 cracker_n_01 flour_n_01 sunglass_n_01 cookie_n_01 bed_n_01 lamp_n_02 food_n_02 painting_n_01 carving_knife_n_01 pop_n_02 tea_bag_n_01 sheet_n_03 tomato_n_01 agent_n_01 hat_n_01 dish_n_01 cheese_n_01 perfume_n_02 toilet_n_02 broccoli_n_02 book_n_02 towel_n_01 table_n_02 pencil_n_01 rag_n_01 peach_n_03 water_n_06 cup_n_01 radish_n_01 marker_n_03 tile_n_01 box_n_01 screwdriver_n_01 raspberry_n_02 banana_n_02 grill_n_02 caldron_n_01 vegetable_oil_n_01 necklace_n_01 brush_n_02 washer_n_03 hamburger_n_01 catsup_n_01 sandwich_n_01 plaything_n_01 candy_n_01 cereal_n_03 door_n_01 food_n_01 newspaper_n_03 hanger_n_02 carrot_n_03 salad_n_01 toothpaste_n_01 blender_n_01 sofa_n_01 plywood_n_01 olive_n_04 briefcase_n_01 christmas_tree_n_05 bowl_n_01 casserole_n_02 apple_n_01 basket_n_01 pot_plant_n_01 backpack_n_01 sushi_n_01 saw_n_02 toothbrush_n_01 lemon_n_01 pad_n_01 receptacle_n_01 sink_n_01 countertop_n_01 melon_n_01 bracelet_n_02 modem_n_01 pan_n_01 oatmeal_n_01 calculator_n_02 duffel_bag_n_01 sandal_n_01 floor_n_01 snack_food_n_01 stocking_n_01 dishwasher_n_01 pencil_box_n_01 chicken_n_01 jar_n_01 alarm_n_02 stove_n_01 plate_n_04 highlighter_n_02 umbrella_n_01 piece_of_cloth_n_01 bin_n_01 ribbon_n_01 chip_n_04 shelf_n_01 bucket_n_01 shampoo_n_01 folder_n_02 shoe_n_01 detergent_n_02 milk_n_01 beer_n_01 shirt_n_01 dustpan_n_02 cube_n_05 broom_n_01 candle_n_01 pen_n_01 microwave_n_02 knife_n_01 wreath_n_01 car_n_01 soup_n_01 sweater_n_01 tray_n_01 juice_n_01 underwear_n_01 orange_n_01 envelope_n_01 fork_n_01 lettuce_n_03 bathtub_n_01 earphone_n_01 pool_n_01 printer_n_03 sack_n_01 highchair_n_01 cleansing_agent_n_01 kettle_n_01 vidalia_onion_n_01 mousetrap_n_01 bread_n_01 meat_n_01 mushroom_n_05 cake_n_03 vessel_n_03 bow_n_08 gym_shoe_n_01 hammer_n_02 teapot_n_01 chair_n_01 jewelry_n_01 pumpkin_n_02 sugar_n_01 shower_n_01 ashcan_n_01 hand_towel_n_01 pork_n_01 strawberry_n_01 electric_refrigerator_n_01 oven_n_01 ball_n_01 document_n_01 sock_n_01 beverage_n_01 hardback_n_01 scraper_n_01 carton_n_02 agent)
  (:predicates
    (inside ?obj1 - object ?obj2 - object)
    (nextto ?obj1 - object ?obj2 - object)
    (ontop ?obj1 - object ?obj2 - object)
    (under ?obj1 - object ?obj2 - object)
    (cooked ?obj1 - object)
    (dusty ?obj1 - object)
    (frozen ?obj1 - object)
    (open ?obj1 - object)
    (stained ?obj1 - object)
    (sliced ?obj1 - object)
    (soaked ?obj1 - object)
    (toggled_on ?obj1 - object)
    (onfloor ?obj1 - object ?floor1 - object)
    (holding ?obj1 - object)
    (handsfull ?agent1 - agent)
    (in_reach_of_agent ?obj1 - object)
    (same_obj ?obj1 - object ?obj2 - object)
 )
)

OBJECTIVE
Given a problem file (objects, :init, :goal) and a list of unfinished action headers, write ONLY the precondition and effect bodies for those actions, producing valid PDDL action definitions. Output all completed actions concatenated as one string in JSON: {{"output": "..."}}.

FORMAT (strict):
(:action <name>
  :parameters (<typed variables>)
  :precondition (<DNF>)
  :effect (and <effects>)
)
Predicates / variable arity must match domain exactly. Every variable used appears in :parameters.

DNF RULE:
Precondition must be a single predicate OR a single (and ...) conjunction OR (or (and ...) (and ...) ...). Place NOT only inside the innermost AND groups. Avoid empty (). Provide minimally informative conditions (never leave precondition empty).

EFFECT RULE:
Effect must be a single predicate OR a single (and ...) conjunction OR (or (and ...) (and ...) ...). Use direct predicates and (not ...) forms. Use (when ...) only if a truly conditional effect is required by the action semantics (rare). Prefer no quantifiers; if absolutely needed, quantifiers must ONLY remove spatial relations of the acted-on object (?obj etc.) and introduce exactly one quantified variable (e.g., ?other - object). NEVER modify reachability or holdings of other objects with quantifiers.

CRITICAL CONSTRAINTS (addressing prior errors):
1. LOCALITY: Do NOT add/remove facts for objects not listed in :parameters (except quantified variable paired with the main object). No global clearing of reachability, holding, or nextto for all objects.
2. REACHABILITY:
   - navigate_to: effect adds (in_reach_of_agent ?objto) ONLY; DO NOT remove reachability of other objects.
   - grasp: MUST NOT remove (in_reach_of_agent ?obj); it sets holding and handsfull, leaving reach untouched.
   - release / place_*: MUST NOT add or remove (in_reach_of_agent ...) facts.
3. HANDS OCCUPANCY: Set (handsfull ?agent) to true only in grasp; set (not (handsfull ?agent)) when releasing or placing an object that was held. Never infer handsfull via exists/forall.
4. CLEANING ACTIONS: The predicate (dusty|stained|sliced ...) target is the OBJECT BEING CLEANED / SLICED (?obj), NOT the tool. Effect removes the property from ?obj only.
5. SYMMETRY: nextto actions must add both (nextto ?a ?b) and (nextto ?b ?a).
6. NO UNDECLARED VARIABLES: Every variable (including those inside when/forall) must be listed in :parameters or be the quantified variable in the quantifier. Do not invent ?container, ?surface etc. if not declared.
7. QUANTIFIER LIMIT: Allowed pattern only for grasp (optional) to clear spatial relations of the grasped object: (forall (?other - object) (and (not (inside ?obj ?other)) (not (ontop ?obj ?other)) (not (under ?obj ?other)) (not (nextto ?obj ?other)) (not (nextto ?other ?obj)) (not (onfloor ?obj ?other))))
   - Do NOT include predicates about other objects’ relations to each other or modify their reach / holding.
8. NO GLOBAL EXCLUSIVITY: Do NOT attempt to enforce that only one object is reachable, held, or cleaned.
9. NO EMPTY EFFECTS: Provide at least one state change.
10. NO COMMENTS inside the returned PDDL snippet.
11. NEVER remove or add (in_reach_of_agent ...) for any variable other than the direct target of navigate_to. Release/placing actions do not affect reach.
12. DO NOT negate a predicate unless it was made true earlier or logically must be removed (e.g., (not (holding ?obj)) when releasing).
13. SLICING: slice / slice_carvingknife effects produce (sliced ?obj) only; no removal of other relations.
14. SOAK: soak effect sets (soaked ?obj1); precondition includes (holding ?obj1) (in_reach_of_agent ?sink) (toggled_on ?sink). Does not modify reachability or handsfull.
15. OPEN: open precondition includes (in_reach_of_agent ?obj) (not (open ?obj)) (not (handsfull ?agent)). Effect: (open ?obj).
16. TOGGLE_ON: toggle_on precondition includes (in_reach_of_agent ?obj) (not (toggled_on ?obj)) (not (handsfull ?agent)). Effect: (toggled_on ?obj).

CANONICAL ACTION TEMPLATES (Copy exactly. Do not add or remove any predicates from the preconditions or effects. Adapt only if those names appear):
navigate_to:
  :precondition (not (in_reach_of_agent ?objto))
  :effect (and
    (in_reach_of_agent ?objto) (forall (?objfrom - object) (when (and (in_reach_of_agent ?objfrom) (not (same_obj ?objfrom ?objto))) (not (in_reach_of_agent ?objfrom))))
  )
grasp:
  :precondition (and
    (not (holding ?obj)) (not (handsfull ?agent)) (in_reach_of_agent ?obj) (not (exists (?obj2 - object) (and (inside ?obj ?obj2) (not (open ?obj2)))))
  )
  :effect (and
    (holding ?obj) (handsfull ?agent) (forall (?other_obj - object) (and (not (inside ?obj ?other_obj)) (not (ontop ?obj ?other_obj)) (not (under ?obj ?other_obj)) (not (under ?other_obj ?obj)) (not (nextto ?obj ?other_obj)) (not (nextto ?other_obj ?obj)) (not (onfloor ?obj ?other_obj))))
  )
release:
  :precondition (and
    (holding ?obj)
  )
  :effect (and
    (not (holding ?obj)) (not (handsfull ?agent))
  )
place_inside:
  :precondition (and
    (holding ?obj_in_hand) (in_reach_of_agent ?obj) (open ?obj)
  )
  :effect (and
    (inside ?obj_in_hand ?obj) (not (holding ?obj_in_hand)) (not (handsfull ?agent))
  )
place_onfloor:
  :precondition (and
    (holding ?obj_in_hand) (in_reach_of_agent ?floor)
  )
  :effect (and
    (onfloor ?obj_in_hand ?floor) (not (holding ?obj_in_hand)) (not (handsfull ?agent))
  )
place_nextto:
  :precondition (and
    (holding ?obj_in_hand) (in_reach_of_agent ?obj)
  )
  :effect (and
    (nextto ?obj_in_hand ?obj) (nextto ?obj ?obj_in_hand) (not (holding ?obj_in_hand)) (not (handsfull ?agent)))
place_nextto_ontop:
  :precondition (and
    (holding ?obj_in_hand) (in_reach_of_agent ?obj1)
  )
  :effect (and
    (nextto ?obj_in_hand ?obj1) (nextto ?obj1 ?obj_in_hand) (ontop ?obj_in_hand ?obj2) (not (holding ?obj_in_hand)) (not (handsfull ?agent))
  )
place_under:
  :precondition (and
    (holding ?obj_in_hand) (in_reach_of_agent ?obj)
  )
  :effect (and
    (under ?obj_in_hand ?obj) (not (holding ?obj_in_hand)) (not (handsfull ?agent))
  )
open:
  :precondition (and
    (in_reach_of_agent ?obj) (not (open ?obj)) (not (handsfull ?agent))
  )
  :effect (open ?obj)
close:
  :precondition (and
    (in_reach_of_agent ?obj) (open ?obj) (not (handsfull ?agent))
  )
  :effect (not (open ?obj))
toggle_on:
  :precondition (and
    (in_reach_of_agent ?obj) (not (handsfull ?agent))
  )
  :effect (toggled_on ?obj)
slice:
  :precondition (and
    (holding ?knife) (in_reach_of_agent ?obj)
  )
  :effect (sliced ?obj)
slice_carvingknife:
  :precondition (and
    (in_reach_of_agent ?obj) (holding ?knife) (ontop ?obj ?board) (not (sliced ?obj))
  )
  :effect (sliced ?obj)
clean_dusty_* (rag/brush/towel/cloth):
  :precondition (and
    (in_reach_of_agent ?obj) (dusty ?obj) (holding ?<tool>)
  )
  :effect (not (dusty ?obj))
clean_stained_* (rag/brush/towel/cloth):
  :precondition (and
    (in_reach_of_agent ?obj) (stained ?obj) (soaked ?<tool>) (holding ?<tool>)
  )
  :effect (not (stained ?obj))
clean_stained_dishwasher:
  :precondition (and
    (holding ?obj) (in_reach_of_agent ?dishwasher)
  )
  :effect (not (stained ?obj))
soak:
  :precondition (and
    (holding ?obj1) (in_reach_of_agent ?sink) (toggled_on ?sink)
  )
  :effect (soaked ?obj1)
soak_teapot:
  :precondition (and
    (holding ?obj1) (in_reach_of_agent ?teapot)
  )
  :effect (soaked ?obj1)
cook:
  :precondition (and
    (ontop ?obj ?pan) (not (cooked ?obj))
  )
  :effect (cooked ?obj)

ADAPTATION RULES:
Only instantiate templates for actions actually listed. If an action name differs (e.g., clean_dusty_rag), map to the appropriate template substituting variable names. Do NOT invent new actions (e.g., reach) not provided.

FORBIDDEN PATTERNS (must never appear):
* Global forall removing reach/holding of all other objects.
* Effects adding (in_reach_of_agent ...) for objects other than navigate_to target.
* Using undeclared variables like ?container, ?surface unless in :parameters.
* Cleaning the tool instead of the target (?obj).
* Omitting reciprocal nextto.
* Empty precondition or effect.
* Multiple top-level effect expressions (must be single (and ...)).

VALIDATION CHECKLIST BEFORE OUTPUT:
1. Every variable used appears in :parameters. ✔
2. Precondition is non-empty DNF. ✔
3. No global reach/holding modifications. ✔
4. nextto symmetric. ✔
5. Cleaning targets ?obj only. ✔
6. handsfull set ONLY by grasp / cleared by release or placement. ✔
7. No invented action names. ✔
8. No comments. ✔
9. Quantifiers (if any) follow rule 7 strictly. ✔
10. No extreaneous top-level (and ...) unless present in template. ✔
11. Copy templates exactly where applicable (with variable renaming). ✔

OUTPUT INSTRUCTIONS:
Return JSON: {{"output": "<concatenated actions>"}} with newline-separated complete action blocks only.

Input placeholders:
Problem file:
{problem_file}
Action to be finished:
{action_handler}
Output:
"""