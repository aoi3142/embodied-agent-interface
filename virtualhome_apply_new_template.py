import json
import os

from src.virtualhome_eval.evaluation.action_sequencing.prompts.one_shot import prompt as virtualhome_action_sequencing_prompt
from src.virtualhome_eval.evaluation.goal_interpretation.prompts.one_shot import prompt as virtualhome_goal_interpretation_prompt
from src.virtualhome_eval.evaluation.subgoal_decomposition.prompts.meta_prompt import system_prompt as virtualhome_subgoal_decomposition_prompt, target_task_prompt as virtualhome_subgoal_decomposition_task_prompt
from src.virtualhome_eval.evaluation.transition_modeling.prompts.one_shot import prompt as virtualhome_transition_modeling_prompt

# Python code to apply our v2 prompt template to the prompts released during the evaluation phase

if not os.path.isdir("eai_starter_kit_eval"):
    import gdown
    gdown.download("https://drive.google.com/uc?id=1d-SfGfp109NjRVhY8tFWrNu_KyWpLJbB", "eai_starter_kit_eval.zip", quiet=False)
    os.system("unzip eai_starter_kit_eval.zip -d eai_starter_kit_eval && rm eai_starter_kit_eval.zip")

env = "virtualhome"
tasks = ["goal_interpretation", "subgoal_decomposition", "action_sequencing", "transition_modeling"]
prompt_version = "v2"

system_prompt_list = [
    virtualhome_goal_interpretation_prompt, 
    virtualhome_subgoal_decomposition_prompt + "\n" + virtualhome_subgoal_decomposition_task_prompt, 
    virtualhome_action_sequencing_prompt, 
    virtualhome_transition_modeling_prompt
]

out_dir = f"submission_{prompt_version}/llm_prompts"
os.makedirs(out_dir, exist_ok=True)

def load_prompts(env, task):
    with open(f"eai_starter_kit_eval/llm_prompts/{env}_{task}_prompts.json", "r") as f:
        new_prompts = json.load(f)
        new_prompts = {i["identifier"]: i["llm_prompt"] for i in new_prompts}
    return new_prompts

####################################################

task_idx = 0

task = tasks[task_idx]
system_prompt = system_prompt_list[task_idx]

new_prompts = load_prompts(env, task)
problems_fields = {}
replaced_new_values = {}
for k, v in new_prompts.items():
    object_in_scene = v.split("\n\n\n")[2].split("\n",1)[1].strip()
    relation_types = v.split("\n\n\n")[3].split("\n",1)[1].strip()
    relation_types += "\n\n" + "\n\n".join(v.split("\n\n\n")[4].split("\n\n",2)[:-1]).strip()
    rel_obj_pairs = v.split("\n\n\n")[4].split("\n\n")[2].split("\n",1)[1].strip()
    action_space = v.split("\n\n\n")[4].split("\n\n")[3].split("\n",1)[1].strip()
    goal_str = "\n\n".join(v.split("\n\n\n")[4].rsplit("\n\n",2)[-2:]).split("\n",1)[1].strip()
    problems_fields[k] = {
        "object_in_scene": object_in_scene,
        "relation_types": relation_types,
        "rel_obj_pairs": rel_obj_pairs,
        "action_space": action_space,
        "goal_str": goal_str
    }
    assert "<object_in_scene>" in system_prompt
    assert "<relation_types>" in system_prompt
    assert "<rel_obj_pairs>" in system_prompt
    assert "<action_space>" in system_prompt
    assert "<goal_str>" in system_prompt
    replaced_new_values[k] = system_prompt\
        .replace("<object_in_scene>", object_in_scene)\
        .replace("<relation_types>", relation_types)\
        .replace("<rel_obj_pairs>", rel_obj_pairs)\
        .replace("<action_space>", action_space)\
        .replace("<goal_str>", goal_str)\
        .strip()
with open(f"{out_dir}/{prompt_version}_{env}_{task}_prompts.json", "w") as f:
    json.dump([{"identifier": k, "llm_prompt": v} for k, v in replaced_new_values.items()], f, indent=2)

####################################################

task_idx = 1

task = tasks[task_idx]
system_prompt = system_prompt_list[task_idx]

new_prompts = load_prompts(env, task)
problems_fields = {}
replaced_new_values = {}
for k, v in new_prompts.items():
    v_split = v.rsplit("\n\n", 6)[1:]
    task_name = v_split[0].split("Task category is ")[-1].strip()
    relevant_objects = v_split[1].split("\n",1)[1].strip()
    initial_states = v_split[2].split("\n",1)[1].strip()
    final = v_split[3].split("[States]",1)[1].strip()
    final_states = final.split("[Actions Must Include]")[0].strip()
    final_actions = final.split("[Actions Must Include]")[1].split("\n",1)[1].strip()
    necessity = v_split[4].split("\n",1)[1].strip()
    problems_fields[k] = {
        "task_name": task_name,
        "relevant_objects": relevant_objects,
        "initial_states": initial_states,
        "final_states": final_states,
        "final_actions": final_actions,
        "necessity": necessity
    }
    assert "<task_name>" in system_prompt
    assert "<relevant_objects>" in system_prompt
    assert "<initial_states>" in system_prompt
    assert "<final_states>" in system_prompt
    assert "<final_actions>" in system_prompt
    assert "<necessity>" in system_prompt
    replaced_new_values[k] = system_prompt\
        .replace("<task_name>", task_name)\
        .replace("<relevant_objects>", relevant_objects)\
        .replace("<initial_states>", initial_states)\
        .replace("<final_states>", final_states)\
        .replace("<final_actions>", final_actions)\
        .replace("<necessity>", necessity)\
        .strip()
with open(f"{out_dir}/{prompt_version}_{env}_{task}_prompts.json", "w") as f:
    json.dump([{"identifier": k, "llm_prompt": v} for k, v in replaced_new_values.items()], f, indent=2)

####################################################

task_idx = 2

task = tasks[task_idx]
system_prompt = system_prompt_list[task_idx]

new_prompts = load_prompts(env, task)
problems_fields = {}
replaced_new_values = {}
for k, v in new_prompts.items():
    v_split = v.split("\n\n\n")[:-1]
    object_in_scene = v_split[0].rsplit("The relevant objects in the scene are:\n")[1].replace("-", "").strip()
    cur_change = v_split[1].split("\n",1)[1].replace("-", "").strip()
    node_goals = v_split[2].split("\n",1)[1].replace("-", "").strip()
    edge_goals = v_split[3].split("\n",1)[1].replace("-", "").strip()
    action_goals = v_split[4].split("\n",1)[1].replace("-", "").strip()
    if not node_goals:
        node_goals = "None"
    if not edge_goals:
        edge_goals = "None"
    if not action_goals:
        action_goals = "None"
    problems_fields[k] = {
        "object_in_scene": object_in_scene,
        "cur_change": cur_change,
        "node_goals": node_goals,
        "edge_goals": edge_goals,
        "action_goals": action_goals
    }
    assert "<object_in_scene>" in system_prompt
    assert "<cur_change>" in system_prompt
    assert "<node_goals>" in system_prompt
    assert "<edge_goals>" in system_prompt
    assert "<action_goals>" in system_prompt
    replaced_new_values[k] = system_prompt\
        .replace("<object_in_scene>", object_in_scene)\
        .replace("<cur_change>", cur_change)\
        .replace("<node_goals>", node_goals)\
        .replace("<edge_goals>", edge_goals)\
        .replace("<action_goals>", action_goals)\
        .strip().rsplit("\n",1)[0].strip()
with open(f"{out_dir}/{prompt_version}_{env}_{task}_prompts.json", "w") as f:
    json.dump([{"identifier": k, "llm_prompt": v} for k, v in replaced_new_values.items()], f, indent=2)

####################################################

task_idx = 3

task = tasks[task_idx]
system_prompt = system_prompt_list[task_idx]

new_prompts = load_prompts(env, task)
problems_fields = {}
replaced_new_values = {}
for k, v in new_prompts.items():
    v_split = v.rsplit("Input:",1)[1].rsplit("\n\n",1)[0].split("(:action",1)
    problem_file = v_split[0].strip().replace("\n", "\n    ").rsplit("\n",1)[0].replace("        (:", "    (:") + "\n)"
    for spaces in range(20,0,-4):
        problem_file = problem_file.replace(" " * spaces, " " * (spaces -2))
    action_handlers = ("(:action" + v_split[1]).strip()
    problems_fields[k] = {
        "problem_file": problem_file,
        "action_handlers": action_handlers
    }
    assert "<problem_file>" in system_prompt
    assert "<action_handlers>" in system_prompt
    replaced_new_values[k] = system_prompt\
        .replace("<problem_file>", problem_file + "\n")\
        .replace("<action_handlers>", action_handlers)\
        .strip().rsplit("\n",1)[0].strip()
with open(f"{out_dir}/{prompt_version}_{env}_{task}_prompts.json", "w") as f:
    json.dump([{"identifier": k, "llm_prompt": v} for k, v in replaced_new_values.items()], f, indent=2)