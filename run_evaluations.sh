#!/bin/bash

# Define parameter lists
datasets=("virtualhome" "behavior")
eval_types=("action_sequencing" "transition_modeling" "goal_interpretation" "subgoal_decomposition")
#datasets=("virtualhome")
#eval_types=("action_sequencing")
#models=("deepseek-chat-v3.1" "qwen/qwen3-235b-a22b:free")
# models=("llama-3.1-8b-instruct")
models=("qwen3-235b-a22b-thinking-2507")

# Base command
base_cmd="eai-eval"

# Iterate over all combinations
for dataset in "${datasets[@]}"; do
  for eval_type in "${eval_types[@]}"; do
    for model in "${models[@]}"; do
      echo "Running evaluation for:"
      echo "  Dataset: $dataset"
      echo "  Eval type: $eval_type"
      echo "  Model: $model"
      echo "---------------------------------------------"

      # Run the evaluation command
      $base_cmd \
        --dataset "$dataset" \
        --eval-type "$eval_type" \
        --mode evaluate_results \
        --llm-response-path "output/$model" \
        --output "./output_evaluation/$model"

      echo "✅ Completed: $dataset / $eval_type / $model"
      echo
    done
  done
done

echo "🎉 All evaluations completed."