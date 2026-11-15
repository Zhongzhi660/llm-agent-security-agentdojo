"""Run AgentDojo with an arbitrary OpenAI-compatible model (e.g. via the course relay).

Usage:
  python scripts/run_bench.py --model gpt-6.1-sol --suite banking -ut user_task_0 -ut user_task_1 \
      [--attack important_instructions] [-it injection_task_0] [--attack-module attack/my_attack.py]

Reads OPENAI_API_KEY / OPENAI_BASE_URL from the environment (.env).
"""
import argparse
import importlib.util
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import openai
from agentdojo.agent_pipeline import AgentPipeline, PipelineConfig
from agentdojo.agent_pipeline.llms.openai_llm import OpenAILLM
from agentdojo.attacks.attack_registry import load_attack
from agentdojo.benchmark import benchmark_suite_with_injections, benchmark_suite_without_injections
from agentdojo.logging import OutputLogger
from agentdojo.models import MODEL_NAMES
from agentdojo.task_suite.load_suites import get_suite

BENCHMARK_VERSION = "v1.2.1"
BLOCKED_MARKER = "[BLOCKED_BY_PROVIDER_FILTER]"


class FilterAwareOpenAILLM(OpenAILLM):
    """OpenAILLM that records provider-side content-filter rejections instead of crashing.

    If the API refuses a request (HTTP 400, content flagged), the episode ends with an assistant
    message containing BLOCKED_MARKER and no tool calls. The case is then scored by AgentDojo as usual
    (the injection task cannot have succeeded) and summarize.py reports it separately as 'blocked'.
    """

    def query(self, query, runtime, env=None, messages=(), extra_args={}):
        from agentdojo.functions_runtime import EmptyEnv
        from agentdojo.types import text_content_block_from_string

        env = EmptyEnv() if env is None else env
        try:
            return super().query(query, runtime, env, messages, extra_args)
        except openai.BadRequestError as e:
            if "flagged" not in str(e):
                raise
            blocked = {"role": "assistant", "content": [text_content_block_from_string(BLOCKED_MARKER)],
                       "tool_calls": None}
            return query, runtime, env, [*messages, blocked], extra_args


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--model-prose-name", default="GPT-4", help="How the attack addresses the model in prose")
    p.add_argument("--suite", required=True)
    p.add_argument("-ut", "--user-task", action="append")
    p.add_argument("-it", "--injection-task", action="append")
    p.add_argument("--attack", default=None)
    p.add_argument("--attack-module", default=None, help="Python file that registers custom attacks")
    p.add_argument("--defense", default=None)
    p.add_argument("--logdir", default="runs")
    p.add_argument("-f", "--force-rerun", action="store_true")
    a = p.parse_args()

    if a.attack_module:
        spec = importlib.util.spec_from_file_location("custom_attack", a.attack_module)
        spec.loader.exec_module(importlib.util.module_from_spec(spec))

    # Let built-in attacks address our custom model by name.
    MODEL_NAMES.setdefault(a.model, a.model_prose_name)

    llm = FilterAwareOpenAILLM(openai.OpenAI(max_retries=5, timeout=180), a.model)
    llm.name = a.model
    pipeline = AgentPipeline.from_config(
        PipelineConfig(llm=llm, model_id=None, defense=a.defense, system_message_name=None, system_message=None)
    )
    pipeline.name = a.model if a.defense is None else f"{a.model}-{a.defense}"

    suite = get_suite(BENCHMARK_VERSION, a.suite)
    with OutputLogger(a.logdir, live=None):
        if a.attack is None:
            res = benchmark_suite_without_injections(
                pipeline, suite, logdir=Path(a.logdir), force_rerun=a.force_rerun,
                user_tasks=a.user_task, benchmark_version=BENCHMARK_VERSION)
        else:
            attacker = load_attack(a.attack, suite, pipeline)
            res = benchmark_suite_with_injections(
                pipeline, suite, attacker, logdir=Path(a.logdir), force_rerun=a.force_rerun,
                user_tasks=a.user_task, injection_tasks=a.injection_task, verbose=False,
                benchmark_version=BENCHMARK_VERSION)

    util = list(res["utility_results"].values())
    print(f"\n[{a.model} | {a.suite} | attack={a.attack} | defense={a.defense}]")
    print(f"Utility: {sum(util)}/{len(util)} = {sum(util)/max(len(util),1):.1%}")
    if a.attack is not None:
        sec = list(res["security_results"].values())  # True = injection task succeeded
        print(f"Attack success rate (ASR): {sum(sec)}/{len(sec)} = {sum(sec)/max(len(sec),1):.1%}")
        for (ut, it), ok in sorted(res["security_results"].items()):
            print(f"  {ut} x {it}: {'ATTACK SUCCEEDED' if ok else 'attack failed'}"
                  f" | utility={res['utility_results'][(ut, it)]}")


if __name__ == "__main__":
    main()
