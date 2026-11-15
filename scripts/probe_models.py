"""Probe which models on the configured endpoint support chat.completions + tool calling (needed by AgentDojo)."""
import os, sys, time, json, concurrent.futures as cf
from openai import OpenAI

client = OpenAI(timeout=60, max_retries=0)
TOOLS = [{"type": "function", "function": {"name": "get_balance", "description": "Get the user's bank balance",
          "parameters": {"type": "object", "properties": {}, "required": []}}}]

def probe(model):
    r = {"model": model}
    t = time.time()
    try:
        c = client.chat.completions.create(model=model, messages=[{"role": "user", "content": "What's my balance? Use the tool."}], tools=TOOLS)
        m = c.choices[0].message
        r["chat+tools"] = "TOOL_CALL" if m.tool_calls else f"text:{(m.content or '')[:40]!r}"
        r["resolved_model"] = c.model
        r["usage"] = (c.usage.prompt_tokens, c.usage.completion_tokens) if c.usage else None
    except Exception as e:
        r["chat+tools"] = f"ERR {type(e).__name__}: {str(e)[:120]}"
    r["latency_s"] = round(time.time() - t, 1)
    try:
        resp = client.responses.create(model=model, input="Reply with OK.")
        r["responses"] = f"ok:{resp.output_text[:20]!r}"
    except Exception as e:
        r["responses"] = f"ERR {type(e).__name__}: {str(e)[:80]}"
    return r

models = sys.argv[1:]
with cf.ThreadPoolExecutor(8) as ex:
    for r in ex.map(probe, models):
        print(json.dumps(r, ensure_ascii=False), flush=True)
