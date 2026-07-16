from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from typing import Any

from boardroomiq.core.models import BoardroomReport

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


DEFAULT_MODEL = "gpt-4o-mini"


EXPLANATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "headline": {
            "type": "string",
            "description": "One short executive tagline grounded in the findings.",
        },
        "enhanced_summary": {
            "type": "string",
            "description": "Three concise sentences maximum, using only provided metrics.",
        },
        "action_items": {
            "type": "array",
            "maxItems": 3,
            "items": {"type": "string"},
        },
        "risk_note": {
            "type": "string",
            "description": "One short risk sentence.",
        },
        "data_limitations": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "headline",
        "enhanced_summary",
        "action_items",
        "risk_note",
        "data_limitations",
    ],
}


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def _response_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return str(text)

    chunks = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            value = getattr(content, "text", None)
            if value:
                chunks.append(str(value))
    return "\n".join(chunks)


def _fallback_metadata(reason: str, model: str) -> dict[str, Any]:
    return {
        "enabled": False,
        "model": model,
        "status": "fallback",
        "reason": reason,
    }


def build_explainer_payload(report: BoardroomReport) -> dict[str, Any]:
    return {
        "question": report.question,
        "ranked_causes": _jsonable(report.ranked_causes[:4]),
        "forecast": _jsonable(report.forecast),
        "verification": _jsonable(report.verification),
        "profiles": report.metadata.get("profiles", []),
        "rule_based_summary": report.ceo_summary,
    }


def generate_llm_explanation(report: BoardroomReport, model: str | None = None) -> dict[str, Any]:
    selected_model = model or os.getenv("BOARDROOMIQ_LLM_MODEL", DEFAULT_MODEL)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_metadata("OPENAI_API_KEY is not configured.", selected_model)

    try:
        from openai import OpenAI
    except ImportError:
        return _fallback_metadata("The openai package is not installed.", selected_model)

    payload = build_explainer_payload(report)
    instructions = (
        "You are BoardroomIQ's executive explanation layer. "
        "Use only the provided computed findings. Do not invent metrics, causes, percentages, or data. "
        "If evidence is missing, say what is missing instead of guessing."
    )
    user_prompt = {
        "task": "Convert the verified agent output into a concise executive decision brief.",
        "output_schema": {
            "headline": "One short bold-sounding executive tagline.",
            "enhanced_summary": "Three concise sentences maximum.",
            "action_items": ["Three short action items maximum."],
            "risk_note": "One short risk sentence.",
            "data_limitations": ["Any missing evidence or limitations, if present."],
        },
        "computed_findings": payload,
    }

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=selected_model,
            instructions=instructions,
            input=json.dumps(user_prompt),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "boardroomiq_executive_brief",
                    "schema": EXPLANATION_SCHEMA,
                    "strict": True,
                }
            },
        )
        raw_text = _response_text(response).strip()
        parsed = json.loads(raw_text)
        parsed.update(
            {
                "enabled": True,
                "model": selected_model,
                "status": "generated",
            }
        )
        return parsed
    except Exception as exc:
        return _fallback_metadata(f"LLM explanation failed: {exc}", selected_model)


def attach_llm_explanation(
    report: BoardroomReport,
    enabled: bool = False,
    model: str | None = None,
) -> BoardroomReport:
    if not enabled:
        report.metadata["llm"] = _fallback_metadata("LLM explanation was not requested.", model or DEFAULT_MODEL)
        return report

    report.metadata["llm"] = generate_llm_explanation(report, model=model)
    return report
