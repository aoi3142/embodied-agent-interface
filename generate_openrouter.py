import json
import os
import sys
import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm
from schemas import schemas

# -------------- CLI ARGUMENTS -----------------
if len(sys.argv) < 2:
    print("Usage: python run_eai_eval_async.py <model_name>")
    print('Example: python run_eai_eval_async.py "deepseek/deepseek-chat-v3.1:free"')
    sys.exit(1)

model = sys.argv[1]  # e.g. "deepseek/deepseek-chat-v3.1:free"
# ----------------------------------------------

prompts_dir = "eai_starter_kit/llm_prompts"
end = None  # Set to None to process all prompts, or limit for quick testing

seed = 0
top_k = 20
reasoning = True
enforce_json = False
use_json_schema = False

assert not (reasoning and enforce_json), "Cannot enable both reasoning and enforce_json"

url = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Please set OPENROUTER_API_KEY environment variable")

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

min_limiter = AsyncLimiter(1, 3 + 0.01)  # 1 request per 3 seconds
day_limiter = AsyncLimiter(99999, 60*60*24)

output_dir = f"output/{model.split('/')[-1].split(':')[0]}"
os.makedirs(output_dir, exist_ok=True)


MAX_RETRIES = 3          # number of retries before giving up
RETRY_DELAY = 5          # seconds between retries

async def ask(session, query, schema) -> dict:
    prompt = query["llm_prompt"].strip()

    async with min_limiter:
        async with day_limiter:
            messages = [{"role": "user", "content": prompt}]
            payload = {
                "model": model,
                "messages": messages,
                "top_k": top_k,
                "seed": seed,
            }
            if reasoning:
                payload["messages"].append({"role": "assistant", "content": "<think>"})
            if enforce_json:
                if use_json_schema:
                    payload["response_format"] = {
                        "type": "json_schema",
                        "json_schema": schema
                    }
                else:
                    payload["response_format"] = {"type": "json_object"}

            output = ""
            reasoning_trace = ""

            # 🔁 Retry loop
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    async with session.post(url, headers=headers, json=payload) as response:
                        if response.status != 200:
                            tqdm.write(f"HTTP {response.status} for prompt {query['identifier']}: {await response.text()}")
                            # Don’t retry for client-side errors like 400
                            # if 400 <= response.status < 500:
                            #     return {"identifier": query["identifier"], "llm_output": "", "reasoning": ""}
                            # Retry for transient server errors (>=500)
                            await asyncio.sleep(RETRY_DELAY)
                            continue

                        completion = await response.json()

                        if not completion:
                            tqdm.write(f"Empty completion (attempt {attempt}) for prompt {query['identifier']}")
                            if attempt < MAX_RETRIES:
                                await asyncio.sleep(RETRY_DELAY)
                                continue
                            return {"identifier": query["identifier"], "llm_output": "", "reasoning": ""}

                        if 'choices' not in completion or not completion['choices']:
                            tqdm.write(f"No choices in response for prompt {query['identifier']}")
                            return {"identifier": query["identifier"], "llm_output": "", "reasoning": ""}

                        content = completion['choices'][0]['message'].get('content', "")
                        reasoning_trace = completion['choices'][0]['message'].get('reasoning', "")

                        if reasoning_trace is None and isinstance(content, str) and "</think>" in content:
                            content = content.rsplit("</think>", 1)
                            reasoning_trace = content[0].strip()
                            content = content[-1]

                        output = (content or "").strip()
                        break  # ✅ got a valid completion, exit retry loop

                except asyncio.TimeoutError:
                    tqdm.write(f"Timeout for prompt {query['identifier']} (attempt {attempt})")
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    output = ""
                    reasoning_trace = ""
                except Exception as e:
                    tqdm.write(f"Error for prompt {query['identifier']} (attempt {attempt}): {type(e).__name__}: {e}")
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    output = ""
                    reasoning_trace = ""

            return {
                "identifier": query["identifier"],
                "llm_output": output,
                "reasoning": reasoning_trace,
            }
        
# async def ask(session, query, schema) -> dict:
#     prompt = query["llm_prompt"].strip()
#     async with min_limiter:
#         async with day_limiter:
#             messages = [{"role": "user", "content": prompt}]
#             payload = {
#                 "model": model,
#                 "messages": messages,
#                 "top_k": top_k,
#                 "seed": seed,
#             }
#             if reasoning:
#                 payload["messages"].append({"role": "assistant", "content": "<think>"})
#             if enforce_json:
#                 if use_json_schema:
#                     payload["response_format"] = {
#                         "type": "json_schema",
#                         "json_schema": schema
#                     }
#                 else:
#                     payload["response_format"] = {"type": "json_object"}

#             try:
#                 async with session.post(url, headers=headers, json=payload) as response:
#                     if response.status != 200:
#                         tqdm.write(f"HTTP {response.status} for prompt {query['identifier']}: {await response.text()}")
#                         return {"identifier": query["identifier"], "llm_output": ""}

#                     completion = await response.json()
#                     if not completion:
#                         print("completion is None!")
#                         return {"identifier": query["identifier"], "llm_output": "", "reasoning": ""}
#                     if 'choices' not in completion or not completion['choices']:
#                         tqdm.write(f"No choices in response for prompt {query['identifier']}")
#                         return {"identifier": query["identifier"], "llm_output": ""}

#                     content = completion['choices'][0]['message']['content']
#                     reasoning_trace = completion['choices'][0]['message'].get('reasoning', "")
#                     if reasoning_trace is None and "</think>" in content:
#                         content = content.rsplit("</think>", 1)
#                         reasoning_trace = content[0].strip()
#                         content = content[-1]
#                     output = content.strip()

#             except asyncio.TimeoutError:
#                 tqdm.write(f"Timeout for prompt {query['identifier']}")
#                 output = ""
#                 reasoning_trace = ""
#             except Exception as e:
#                 tqdm.write(f"Error for prompt {query['identifier']}: {type(e).__name__}: {e}")
#                 output = ""
#                 reasoning_trace = ""
#             return {"identifier": query["identifier"], "llm_output": output, "reasoning": reasoning_trace}

async def main():
    envs = ["behavior", "virtualhome"]
    tasks = ["goal_interpretation", "subgoal_decomposition", "action_sequencing", "transition_modeling"]

    timeout = aiohttp.ClientTimeout(total=30 * 60)
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

                with open(f"{output_dir}/{env}_{task}_outputs_.json", "w") as f:
                    json.dump(results, f, indent=2)

                curr_outdir = f"{output_dir}/{env}/{task}"
                os.makedirs(curr_outdir, exist_ok=True)
                with open(f"{curr_outdir}/{env}_{task}_outputs.json", "w") as f:
                    json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
