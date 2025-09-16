import json

import os
import asyncio
from aiolimiter import AsyncLimiter
from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm

import aiohttp

from schemas import schemas

# Directory containing the prompt files
prompts_dir = "eai_starter_kit/llm_prompts"
end = None  # Set to None to process all prompts, or set to a positive integer to test with a subset

# Specify OpenRouter Model
model = "deepseek/deepseek-chat-v3.1:free"
# model = "qwen/qwen3-235b-a22b:free"

seed = 0
top_k = 20

# Manually append <think> for reasoning, only tested with DeepSeek and Qwen
reasoning = False

# Enforce JSON output format
enforce_json = True

# Use JSON schema for response format, doesn't work for deepseek
# From initial experiments, using json_schema frequently causes failed responses (return empty string)
# However, if successful, it guarantees the output is valid JSON of the desired format
use_json_schema = False

assert not (reasoning and enforce_json), "Cannot enable both reasoning and enforce_json, as reasoning is not in json format"

url = "https://openrouter.ai/api/v1/chat/completions"

# Add your OpenRouter API key here
# Set `export OPENROUTER_API_KEY="your_api_key"` in your environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Please set OPENROUTER_API_KEY environment variable")

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

min_limiter = AsyncLimiter(1, 3 + 0.01)  # 1 request per 3 seconds
day_limiter = AsyncLimiter(999, 60*60*24)  # 1000 requests per day

output_dir = f"output/{model.split('/')[-1].split(':')[0]}"
os.makedirs(output_dir, exist_ok=True)

async def ask(session, query, schema) -> dict:
    prompt = query["llm_prompt"].strip()
    async with min_limiter:
        async with day_limiter:
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
            payload = {
                "model": model,
                "messages": messages,
                "top_k": top_k,
                "seed": seed,
            }
            if reasoning:
                # If reasoning, append <think> to prompt to force reasoning
                # Deepseek and Qwen doesnt seem to support "reasoning" argument in payload
                # Thus, we manually append <think> to the prompt to force reasoning
                payload["messages"].append({
                    "role": "assistant",
                    "content": "<think>",
                })
            if enforce_json:
                if use_json_schema:
                    payload["response_format"] = {
                        "type": "json_schema",
                        "json_schema": schema
                    }
                else:
                    payload["response_format"] = {"type": "json_object"}
            reasoning_trace = ""
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        tqdm.write(f"HTTP {response.status} for prompt {query['identifier']}: {await response.text()}")
                        return {"identifier": query["identifier"], "llm_output": ""}

                    completion = await response.json()
                    if 'choices' not in completion or not completion['choices']:
                        tqdm.write(f"No choices in response for prompt {query['identifier']}")
                        return {"identifier": query["identifier"], "llm_output": ""}

                    content = completion['choices'][0]['message']['content']
                    reasoning_trace = completion['choices'][0]['message']['reasoning']
                    if reasoning_trace is None:
                        if "</think>" in content:
                            content = content.rsplit("</think>", 1)
                            reasoning_trace = content[0].strip()
                            content = content[-1]
                        else:
                            reasoning_trace = ""
                    output = content.strip()

            except asyncio.TimeoutError:
                tqdm.write(f"Timeout for prompt {query['identifier']}")
                output = ""
            except Exception as e:
                tqdm.write(f"Error for prompt {query['identifier']}: {type(e).__name__}: {e}")
                output = ""
            return {"identifier": query["identifier"], "llm_output": output, "reasoning": reasoning_trace}

async def main():
    envs = ["behavior", "virtualhome"]
    tasks = ["goal_interpretation", "subgoal_decomposition", "action_sequencing", "transition_modeling"]

    # Create session with timeout
    timeout = aiohttp.ClientTimeout(total=30 * 60)  # 30 minutes timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for i, env in enumerate(envs):
            for j, (task, schema) in enumerate(zip(tasks, schemas)):
                tqdm.write(f"Processing {env}({i+1}/{len(envs)}) - {task}({j+1}/{len(tasks)})")

                with open(f"{prompts_dir}/{env}_{task}_prompts.json", "r") as f:
                    starter_llm_prompt = json.load(f)

                if end is not None:
                    starter_llm_prompt = starter_llm_prompt[:end]

                _tasks = [ask(session, prompt, schema) for prompt in starter_llm_prompt]
                results = await tqdm_asyncio.gather(*_tasks)

                # Save results for eai-eval
                with open(f"{output_dir}/{env}_{task}_outputs_.json", "w") as f:
                    json.dump(results, f, indent=2)

                # Save results for submission
                curr_outdir = f"{output_dir}/{env}/{task}"
                os.makedirs(curr_outdir, exist_ok=True)
                with open(f"{output_dir}/{env}/{task}/{env}_{task}_outputs.json", "w") as f:
                    json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())