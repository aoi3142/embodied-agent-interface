import json

import os
import asyncio
from aiolimiter import AsyncLimiter
from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm
from typing import Optional, Tuple
import time
import concurrent.futures
from itertools import repeat
from copy import deepcopy
import traceback

import aiohttp
import requests
import argparse

# from schemas import schemas
schemas = repeat(None)  # No schema

# Directory containing the prompt files
prompts_file = "submission_v4/llm_prompts/v2_{env}_{task}_prompts.json"
end = None  # Set to None to process all prompts, or set to a positive integer to test with a subset

# output_dir = f"submission_v2/sample_submission"
output_dir = f"testing/sample_submission"
os.makedirs(output_dir, exist_ok=True)
output_json = "{output_dir}/{env}_{task}_outputs.json"

envs = [
    # "behavior", 
    "virtualhome"
    ]
tasks = [
    "goal_interpretation", 
    # "subgoal_decomposition", 
    # "action_sequencing", 
    # "transition_modeling"
    ]

# Specify OpenRouter Model
# model = "qwen-3-235b-a22b-thinking-2507"
model = "qwen/qwen3-235b-a22b-thinking-2507"

url = "https://openrouter.ai/api/v1/chat/completions"
# url = "https://api.cerebras.ai/v1/chat/completions"

# Rate limiting parameters
max_rate = 10     # max requests within time_period (rate limiter throttle)
time_period = 10  # window size in seconds for rate limiter

# aiohttp default simultaneous connection limit is ~100; raise if you want more in-flight requests
CONCURRENCY_LIMIT = 250  # Increase this (e.g. 500 or 1000) to allow more simultaneous connections

MAX_WORKERS = 1  # Number of concurrent threads for different env-task combinations

seed = 0
top_k = 20

# Outer loop retry limit for no output / incomplete outputs (when server returns incomplete reasoning or completion)
MAX_NO_OUTPUT_RETRIES = 10

# Inner loop retry limit for no response / rate limiting from server (set to a higher value to retry when rate limited or server error)
MAX_NO_RESPONSE_RETRIES = 3

# Number of copies to generate per prompt, should be 1 for most cases
COPIES_PER_PROMPT = 1

# Manually append <think> for reasoning, only tested with DeepSeek and Qwen
reasoning = False
expect_reasoning = True # Model itself is doing reasoning, for figuring out if the output is complete.

# Enforce JSON output format
enforce_json = False

# Reflexion
REFLEXION_PROMPT = "Check whether your previous answer satisfies the task requirements. If it does, simply repeat your previous answer. If it does not, please provide a corrected answer."
MAX_REFLEXION_ROUNDS = 0    # Set to 0 to disable reflexion
assert MAX_REFLEXION_ROUNDS <= 1, "Only support up to 1 reflexion round for now"

# Use JSON schema for response format, doesn't work for deepseek
# From initial experiments, using json_schema frequently causes failed responses (return empty string)
# However, if successful, it guarantees the output is valid JSON of the desired format
use_json_schema = False

assert not (reasoning and enforce_json), "Cannot enable both reasoning and enforce_json, as reasoning is not in json format"

# Add your OpenRouter API key here
# Set `export OPENROUTER_API_KEY="your_api_key"` in your environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Please set OPENROUTER_API_KEY environment variable")

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "model": model,
    # "top_k": top_k,
    # "top_p": 0.95,
    # "seed": seed,
    "temperature": 0.0,
    # "logprobs": True,
    # "top_logprobs": 20,
    "max_tokens": int(16384*1.5),
    # "stop_token_ids": [3],  # Deal with NaN
    "provider": {   # For OpenRouter, force provider to support all provided parameters
        "require_parameters": True,
        "quantizations": ["bf16"],
        "allow_fallbacks": False,
        "sort": "price"
    }
}

# Global thread pool executor for non-blocking I/O operations
_io_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="io_worker")

def wait_for_url_to_be_up(url: str, timeout: int = 5, retry_interval: int = 1):
    """
    Check if the URL is up and accessible. 
    Loops forever until the URL responds successfully.
    Uses a global lock to ensure this only runs once across all threads.

    Args:
        url: The URL to check
        timeout: Timeout for each request in seconds
        retry_interval: Time to sleep between retries in seconds
    """
    # tqdm.write(f"Checking if {url} is up...")
    spinner = ['|', '/', '-', '\\']
    spinner_idx = 0

    # Extract base URL for health check
    base_url = url.rsplit('/v1/', 1)[0] if '/v1/' in url else url.rsplit('/', 1)[0]
    check_url = f"{base_url}/health" if base_url != url else url

    while True:
        try:
            # Try health endpoint first, fallback to base URL
            response = requests.get(check_url, timeout=timeout)
            if response.status_code in [200, 404, 405]:  # 404/405 means server is up but endpoint doesn't exist
                tqdm.write(f"\r✓ Server at {base_url} is up and running!" + " " * 20)
                return
        except Exception:
            pass

        # Sleep with spinning wheel animation
        for spinner_idx in range(retry_interval * 10):  # 10 updates per second
            print(f"\rWaiting for {check_url}... {spinner[spinner_idx % len(spinner)]}", end='', flush=True)
            time.sleep(0.1)

async def rate_limited_post(min_limiter, session, url, headers, payload, identifier, delay=1) -> dict:
    async with min_limiter:
        try:
            async with session.post(url, headers=headers, json=payload) as response:

                completion = await response.json()
                if response.status == 403:  # Key limit
                    tqdm.write(f"Key limited for prompt {identifier}")
                    return {}
                if response.status == 429:  # Rate limit
                    raise ValueError(f"Rate limited")
                if response.status == 503:  # Provider not available
                    raise ValueError(f"Provider not available")
                if response.status == 500:
                    raise ValueError(f"Server error 500: {await response.text()}")
                if response.status != 200:
                    raise ValueError(f"HTTP {response.status}: {await response.text()}")
                if not completion or 'choices' not in completion or not completion['choices']:
                    raise ValueError("No choices in response.")
                if completion["choices"][0]['finish_reason'] == "length":
                    # tqdm.write(f"Warning: Completion for prompt {identifier} finished due to max token length.")
                    return {}

                return completion

        except asyncio.CancelledError:
            # Re-raise cancellation to properly terminate the task
            raise
        except Exception as e:
            tqdm.write(f"Error for prompt {identifier}: {type(e).__name__}: {e}, ", end='')
            delay *= 2  # Exponential backoff
            if delay >= 2**MAX_NO_RESPONSE_RETRIES:   # return None
                tqdm.write(f"exceeded max response retries, returning empty output")
                return {}
            tqdm.write(f"sleeping for {delay} seconds")
            await asyncio.sleep(delay)  # Async sleep
            return await rate_limited_post(min_limiter, session, url, headers, payload, identifier, delay)

async def ask(session, min_limiter, identifier, env, task, messages, schema, post_processing = lambda x: x, no_output_retries = MAX_NO_OUTPUT_RETRIES, reflexion_round = 0) -> Tuple[dict, dict]:

    completion = {}
    curr_payload = deepcopy(payload)
    curr_payload["messages"] = messages
    if reasoning:
        # If reasoning, append <think> to prompt to force reasoning
        # Deepseek and Qwen doesnt seem to support "reasoning" argument in payload
        # Thus, we manually append <think> to the prompt to force reasoning
        curr_payload["messages"].append({
            "role": "assistant",
            "content": "<think>",
        })
    if enforce_json:
        if use_json_schema:
            curr_payload["response_format"] = {
                "type": "json_schema",
                "json_schema": schema
            }
        else:
            curr_payload["response_format"] = {"type": "json_object"}

    completion = await rate_limited_post(min_limiter, session, url, headers, curr_payload, identifier, delay=1)
    try:
        content = completion['choices'][0]['message']['content'].strip()
    except Exception:
        content = ""
    try:
        reasoning_trace = completion['choices'][0]['message']['reasoning']
    except Exception:
        reasoning_trace = ""
    if reasoning_trace == "":
        # if "<think>" not in content:
        #     pass
        if "</think>" in content:
            content = content.rsplit("</think>", 1)
            reasoning_trace = content[0].strip()
            content = content[-1].strip()
    try:
        print_content = json.loads(content)
    except Exception:
        tqdm.write(f"Failed to parse content for prompt {identifier} as JSON.")
        content = ""
        reasoning_trace = ""
        print_content = {}
    if task == "transition_modeling":
        try:
            print_content = print_content["output"]
        except Exception:
            content = ""
            reasoning_trace = ""
            print_content = content
    else:
        print_content = content
    if (expect_reasoning and reasoning_trace == "") or content == "":
        # Deal with completion not containing end of reasoning (likely backend failure)
        if no_output_retries > 0:
            tqdm.write(f"No output for prompt {identifier}, retrying ({no_output_retries} retries left)...")
            no_output_retries -= 1
            await asyncio.sleep(2 * (MAX_NO_OUTPUT_RETRIES - no_output_retries))  # Async sleep
            return await ask(session, min_limiter, identifier, env, task, messages, schema, post_processing, no_output_retries, reflexion_round)
        else:
            return {"identifier": identifier, "llm_output": content.strip(), "reasoning": "", "prompt_tokens": 0, "completion_tokens": 0}, completion

    if reflexion_round < MAX_REFLEXION_ROUNDS:
        reflexion_round += 1
        # Simple reflexion: if output is empty, retry once
        messages.append({
            "role": "assistant",
            "content": content,
        })
        messages.append({
            "role": "user",
            "content": REFLEXION_PROMPT,
        })
        # tqdm.write(f"Reflexion round {reflexion_round} for prompt {identifier}...")
        new_results, new_completions = await ask(session, min_limiter, identifier, env, task, messages, schema, post_processing, reflexion_round = reflexion_round)
        return new_results, {"reflexion_completion": new_completions, "original_completion": completion}

    content = post_processing(content)
    try:
        tokens_input = completion["usage"]["prompt_tokens"]
    except KeyError:
        tokens_input = 0
    try:
        tokens_generated = completion["usage"]["completion_tokens"]
    except KeyError:
        tokens_generated = 0
    try:
        provider = f"({completion['provider']})"
    except KeyError:
        provider = ""
    tqdm.write("_" * 20 + "\n" + f"{env} {task} {identifier} (tokens: {tokens_input}|{tokens_generated}){provider}" + "\n\n" + print_content + "\n")
    return {"identifier": identifier, "llm_output": content, "reasoning": reasoning_trace, "prompt_tokens": tokens_input, "completion_tokens": tokens_generated}, completion

async def process_env_task(session, min_limiter, env, task, schema, postprocessing):
    """Process a single environment-task combination"""
    tqdm.write(f"Processing {env} - {task}")
    out_json = output_json.format(output_dir=output_dir, env=env, task=task)
    completions_pkl = f"{output_dir}/{env}_{task}_completions.pkl"
    prompt_file = prompts_file.format(env=env, task=task)

    if MAX_REFLEXION_ROUNDS > 0:
        with open(out_json, "r") as f:
            existing_outputs = json.load(f)
        tqdm.write(f"Loaded {len(existing_outputs)} existing outputs for reflexion for {env} - {task} from {out_json}")
        existing_outputs = {item["identifier"]: item["llm_output"] for item in existing_outputs}
        out_json = out_json.rsplit("/", 1)[0] + f"/reflexion{MAX_REFLEXION_ROUNDS}_" + out_json.rsplit("/", 1)[1]
        completions_pkl = completions_pkl.rsplit("/", 1)[0] + f"/reflexion{MAX_REFLEXION_ROUNDS}_" + completions_pkl.rsplit("/", 1)[1]
    else:
        existing_outputs = {}

    with open(prompt_file, "r") as f:
        starter_llm_prompt = json.load(f)

    load_logs = [f"***{env} - {task}***"]
    load_logs.append(f"Loaded {len(starter_llm_prompt)} prompts from {prompt_file}")

    prev_exists = False
    prev_out_ = []
    completed_ids = set()
    not_completed_ids = set(item["identifier"] for item in starter_llm_prompt)
    if os.path.exists(out_json):
        load_logs.append(f"Found previous output file {out_json}, resuming...")
        prev_exists = True
        with open(out_json, "r") as f:
            prev_out = json.load(f)

        completed_ids = set(item["identifier"] for item in prev_out if (item["reasoning"] and item["llm_output"]))
        for item in prev_out:
            if item["identifier"] in completed_ids:
                prev_out_.append(item)
                not_completed_ids.discard(item["identifier"])
        if len(not_completed_ids) == 0:
            load_logs.append(f"All prompts already completed, skipping...")
        else:
            starter_llm_prompt = [p for p in starter_llm_prompt if p["identifier"] in not_completed_ids]
            load_logs.append(f"Resuming from previous run, {len(starter_llm_prompt)} prompts remaining...")
    tqdm.write("\n".join(load_logs))
    if len(not_completed_ids) == 0:
        return

    starter_llm_prompt = [p for p in starter_llm_prompt]

    # Check if the URL is up before proceeding
    wait_for_url_to_be_up(url)

    chats = {}
    added_count = 0
    for prompt in starter_llm_prompt:
        chats[prompt["identifier"]] = [
            {
                "role": "user",
                "content": prompt["llm_prompt"],
            }
        ]
        if MAX_REFLEXION_ROUNDS > 0 and prompt["identifier"] in existing_outputs:
            # If reflexion is enabled, and we have existing outputs, add them to the chat history
            chats[prompt["identifier"]].append({
                "role": "assistant",
                "content": existing_outputs[prompt["identifier"]],
            })
            chats[prompt["identifier"]].append({
                "role": "user",
                "content": REFLEXION_PROMPT,
            })
            added_count += 1
    if added_count > 0:
        tqdm.write(f"Added {added_count} existing outputs to chat histories for {env} - {task}")

    # Create tasks as Task objects so we can cancel them on interrupt
    _tasks = [asyncio.create_task(ask(session, min_limiter, identifier, env, task, chat, schema, postprocessing, reflexion_round=(len(chat)//2))) for _, (identifier, chat) in zip(range(end if end is not None else len(chats)), chats.items()) for _ in range(COPIES_PER_PROMPT)]
    
    try:
        gathered_results = await tqdm_asyncio.gather(*_tasks, desc=f"{env} - {task}", total=len(_tasks))
    except KeyboardInterrupt:
        tqdm.write(f"\nKeyboard interrupt detected for {env} - {task}. Cancelling pending requests and saving completed results...")
        
        # Cancel all pending tasks
        for task_obj in _tasks:
            if not task_obj.done():
                task_obj.cancel()
        
        # Wait for all cancellations to complete
        await asyncio.gather(*_tasks, return_exceptions=True)
        
        # Gather only completed results (ignore cancelled ones)
        gathered_results = []
        for task_obj in _tasks:
            if task_obj.done() and not task_obj.cancelled():
                try:
                    gathered_results.append(task_obj.result())
                except Exception:
                    pass  # Skip failed tasks
        
        tqdm.write(f"Collected {len(gathered_results)} completed results out of {len(_tasks)} total tasks.")
        
        if not gathered_results:
            tqdm.write(f"No completed results to save for {env} - {task}.")
            return  # Exit gracefully without saving

    results = []
    # completions = []
    failures = 0
    for r, c in gathered_results:
        if r["identifier"] in completed_ids:
            continue
        if not (c and r["llm_output"] and r["reasoning"]):
            r["llm_output"] = ""
            r["reasoning"] = ""
            r["completion_tokens"] = 0
            failures += 1
        completed_ids.add(r["identifier"])
        results.append(r)
        # completions.append(c)
    if not any(results):
        tqdm.write(f"No successful completions for {env} - {task}, skipping saving outputs.")
        return

    if prev_exists:
        results = prev_out_ + results

    # Save results for eai-eval
    tqdm.write(f"Saving {len(results)} results to {out_json} for {env} - {task}, {failures} failures.")
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    os.makedirs(out_json.rsplit("/", 1)[0] + f"/{env}/{task}/", exist_ok=True)
    with open(f"/{env}/{task}/".join(out_json.rsplit("/", 1)), "w") as f:
        json.dump(results, f, indent=2)

async def run_env_task_worker(env, task, schema, postprocessing):
    """Worker function to run a single env-task combination in its own event loop"""
    # Create limiters in this event loop
    min_limiter = AsyncLimiter(max_rate=max_rate, time_period=time_period)

    # Create session with timeout
    timeout = aiohttp.ClientTimeout(total=10 * 60)  # 10 minutes timeout
    # Increase connector limit to allow >100 simultaneous connections if desired
    connector = aiohttp.TCPConnector(limit=CONCURRENCY_LIMIT)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        try:
            await process_env_task(session, min_limiter, env, task, schema, postprocessing)
        finally:
            # Wait for any pending tasks in the executor to complete
            await asyncio.sleep(0.1)  # Give time for callbacks to complete

def main():

    # Create all env-task combinations
    work_items = []
    for env in envs:
        for task, schema in zip(tasks, schemas):
            if env == "virtualhome" and task == "action_sequencing":
                postprocessing = lambda x: x.replace('[]', '[   ]') # Fix for virtualHome action sequencing action STANDUP
            else:
                postprocessing = lambda x: x
            work_items.append((env, task, schema, postprocessing))

    # Function to run async work in a thread
    def run_async_work(env, task, schema, postprocessing):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_env_task_worker(env, task, schema, postprocessing))
        finally:
            loop.close()

    # Use ThreadPoolExecutor to run work items in parallel
    max_workers = min(len(work_items), MAX_WORKERS)  # Limit concurrent threads to avoid overwhelming the API
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all work items
        future_to_work = {
            executor.submit(run_async_work, env, task, schema, postprocessing): (env, task)
            for env, task, schema, postprocessing in work_items
        }

        # Wait for all to complete
        for future in concurrent.futures.as_completed(future_to_work):
            env, task = future_to_work[future]
            try:
                future.result()
                tqdm.write(f"Completed {env} - {task}")
            except FileNotFoundError as fnf_exc:
                tqdm.write(f"File not found for {env} - {task}: {fnf_exc}")
            except Exception as exc:
                traceback.print_exc()
                tqdm.write(f"Error processing {env} - {task}: {exc}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run OpenRouter tasks")
    parser.add_argument("--model", type=str, default=model, help="OpenRouter model to use")
    parser.add_argument("--url", type=str, default=url, help="URL for OpenRouter API")
    parser.add_argument("--port", type=int, default=None, help="Port for vLLM server for local testing, overrides URL to localhost")
    parser.add_argument("--max_tokens", type=int, default=payload.get("max_tokens"), help="Max tokens for generation")
    parser.add_argument("--max_rate", type=int, default=max_rate, help="Rate limiter: max requests per window")
    parser.add_argument("--time_period", type=int, default=time_period, help="Rate limiter window in seconds")
    parser.add_argument("--concurrency_limit", type=int, default=CONCURRENCY_LIMIT, help="aiohttp TCPConnector simultaneous connection limit")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help="Thread workers for env-task combos")
    args = parser.parse_args()

    # Apply CLI overrides
    model = args.model
    if args.port is not None:
        url = f"http://localhost:{args.port}/v1/chat/completions"
        model = "Qwen/Qwen3-235B-A22B-Thinking-2507"
        payload.pop("provider", None)  # Remove provider for local vLLM
    if args.max_tokens is not None:
        payload["max_tokens"] = args.max_tokens
    if args.max_rate is not None:
        max_rate = args.max_rate
    if args.time_period is not None:
        time_period = args.time_period
    if args.concurrency_limit is not None:
        CONCURRENCY_LIMIT = args.concurrency_limit
    if args.workers is not None:
        MAX_WORKERS = args.workers

    payload["model"] = model
    tqdm.write(f"Using model: {model} on URL: {url}\nRate limit: {max_rate}/{time_period}s, aiohttp concurrency: {CONCURRENCY_LIMIT}, workers: {MAX_WORKERS}")
    try:
        main()
    finally:
        _io_executor.shutdown(wait=False)