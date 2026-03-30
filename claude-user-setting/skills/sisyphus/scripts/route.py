#!/usr/bin/env python3
"""
Sisyphus Router — deterministic intent classifier for UserPromptSubmit hook.

Reads stdin (the user prompt) and prints JSON routing decision to stdout.
Claude Code's UserPromptSubmit hook injects this output into context before
Claude responds, so Claude executes the routing decision mechanically rather
than deciding on its own.

Exit codes: 0 = success (always), non-zero = error (hook should be silent)
"""

import json
import re
import sys


def route(prompt: str) -> dict:
    """
    Classify prompt intent and return routing decision.

    Returns dict with:
      intent: "simple" | "ulw" | "plan" | "start-work" | "other"
      trigger: the matched keyword/pattern or None
      agent: recommended subagent_type or None
      note: brief reasoning for Claude to follow
    """
    text = prompt.strip()
    lower = text.lower()

    # /start-work {plan-name} — Atlas execution trigger
    start_work_match = re.search(r"/start-work\s+(\S+)", text)
    if start_work_match:
        plan_name = start_work_match.group(1)
        return {
            "intent": "start-work",
            "trigger": "/start-work",
            "plan_name": plan_name,
            "agent": "sisyphus-atlas",
            "note": f"Invoke Agent(subagent_type='sisyphus-atlas', prompt='Execute plan: .sisyphus/plans/{plan_name}.md')"
        }

    # ulw / ultrawork — autonomous execution mode (no planning, no interview)
    if re.search(r"\bulw\b|ultrawork", lower):
        return {
            "intent": "ulw",
            "trigger": "ulw/ultrawork",
            "agent": None,
            "note": "Autonomous execution mode. Skip planning interview. Research → implement → verify. Delegate via sisyphus-junior."
        }

    # @plan prefix — planning/interview mode
    if text.startswith("@plan"):
        return {
            "intent": "plan",
            "trigger": "@plan",
            "agent": "sisyphus-metis",
            "note": "Enter Prometheus planning workflow. Explore codebase patterns in parallel, then interview user, then generate plan to .sisyphus/plans/."
        }

    # Investigation/explanation — research mode (no implementation)
    investigation_patterns = [
        # English
        r"\bhow does\b.*\bwork\b",
        r"\bexplain\b",
        r"\bwhat is\b",
        r"\bwhy (does|is|are|did)\b",
        r"\bunderstand\b",
        r"\binvestigate\b",
        r"\bshow me how\b",
        # Korean
        r"어떻게 (동작|작동|작동하는지|돌아가는지)",
        r"왜 (그런|이런|저런)",
        r"(설명|이해|파악|분석).*해",
        r"어떤 (구조|흐름|방식|원리)",
        r"(알고싶|궁금)",
    ]
    impl_verbs_en = ["fix", "add", "implement", "create", "build", "write", "refactor", "change", "update", "delete", "remove"]
    impl_verbs_kr = ["고쳐", "추가", "구현", "만들어", "생성", "작성", "수정", "삭제", "리팩토"]
    if any(re.search(p, lower) for p in investigation_patterns):
        has_impl = (
            any(re.search(r"\b" + v + r"\b", lower) for v in impl_verbs_en) or
            any(v in text for v in impl_verbs_kr)
        )
        if not has_impl:
            return {
                "intent": "simple",
                "trigger": "investigation",
                "agent": None,
                "note": "Research/explanation intent. Explore codebase and explain — do NOT propose implementation."
            }

    # Bug fix / debugging
    bug_patterns = [
        # English
        r"\b(bug|error|exception|crash|broken|fails?|failing|not working|doesn't work|doesnt work)\b",
        r"\bfix\b",
        r"\bdebug\b",
        r"\btypeerror\b",
        r"\bsegfault\b",
        # Korean
        r"(버그|에러|오류|오작동|안 ?돼|안됨|실패|죽어|죽는)",
        r"(고쳐|수정해|디버그)",
    ]
    if any(re.search(p, lower) for p in bug_patterns) or any(p in text for p in ["고쳐", "에러", "버그", "오류"]):
        return {
            "intent": "simple",
            "trigger": "bug/fix",
            "agent": None,
            "note": "Bug fix intent. First explore to find root cause (git log, explore agents), then delegate minimal fix to sisyphus-junior. Do NOT refactor while fixing."
        }

    # Feature implementation / build
    feature_patterns_en = [
        r"\b(add|implement|create|build|write)\b",
    ]
    feature_keywords_kr = ["추가", "구현", "만들어", "생성해", "작성해", "개발해"]
    if (any(re.search(p, lower) for p in feature_patterns_en) or
            any(kw in text for kw in feature_keywords_kr)):
        return {
            "intent": "simple",
            "trigger": "feature/build",
            "agent": None,
            "note": "Feature implementation. Explore patterns first. For 2+ files or complex changes, delegate to sisyphus-junior. Verify after each step."
        }

    # Default — no strong signal
    return {
        "intent": "other",
        "trigger": None,
        "agent": None,
        "note": "No specific routing pattern matched. Proceed with standard judgment."
    }


def main():
    raw = sys.stdin.read()

    # Try to parse as UserPromptSubmit hook event JSON
    try:
        event = json.loads(raw)
        prompt = event.get("prompt", raw)
    except (json.JSONDecodeError, AttributeError):
        prompt = raw

    result = route(prompt)

    # Only emit context when we have a meaningful routing signal
    if result["intent"] != "other":
        context = f"[SISYPHUS ROUTER] intent={result['intent']} trigger={result['trigger']}\n{result['note']}"
        if result.get("plan_name"):
            context += f"\nplan_name={result['plan_name']}"
        output = {"hookSpecificOutput": {"additionalContext": context}}
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
