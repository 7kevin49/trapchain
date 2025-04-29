from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, TypedDict

import pandas as pd
import requests
import structlog
from dateutil.tz import tzutc
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from trapchain.settings import CHUNK_SIZE, LOKI_URL, MODEL_NAME, OPENAI_API_KEY

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

logger = structlog.get_logger(__name__)

# Prompt and LLM Set Up

_SYSTEM_BLURB = """
You Are a SOC Analyst Assistant. You can read logs and categorize them into severity levels.

Read the logs given, and consider their context. Think about the following:
- What is the nature of the event?
- What is the source of the event? (e.g., IP address, user agent)
- Is it a normal event, or does it indicate a potential security incident?
- What is the severity level of the event? (e.g., INFO, WARNING, ERROR, CRITICAL)
- What action should be taken? (e.g., investigate, ignore, escalate)
- Are the failed logins related to a brute-force attack? Or is it a normal event?
- IGNORE ALL INTERNAL LOGS.

Consider that logs may come from separate actors; do not lump all logs together.
When consolidating multiple chunks, preserve all original fields and group related events by actor.

Severity levels:
- INFO: Normal event, no action needed
- MEDIUM: Potential issue, agent must investigate over the next 24h
- HIGH: Serious issue, agent must investigate immediately
- CRITICAL: Immediate action required, escalate to SOC team

All responses should return a JSON list of objects with these fields:
- severity, action, logs, context, source, timestamp, technique

After categorizing, consolidate the chunk-level outputs into a unified list grouping by actor.
"""

prompt = ChatPromptTemplate.from_messages(
    [("system", _SYSTEM_BLURB), ("human", " Logs: \n{logs}")]
)
llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0.1,
    openai_api_key=OPENAI_API_KEY,
)

categorise_runnable = prompt | llm | StrOutputParser()
consolidate_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a SOC Analyst Assistant. Consolidate the following categorized events into a single JSON list, preserving all fields and grouping related events by actor. Return valid JSON.",
        ),
        ("human", "Events: {events}"),
    ]
)
consolidate_runnable = consolidate_prompt | llm | StrOutputParser()

### End of Prompt and LLM Set Up ###


# Loki Helpers
def _query_loki(
    start_ns: int,
    end_ns: int,
    apps: list[str] = ["cowrie", "dionaea"],
    limit: int = 800,
):
    all_results, current_start = [], start_ns
    app_regex = "|".join(apps)
    query = f'{{namespace="honeypots", app=~"{app_regex}"}}'
    while current_start < end_ns:
        params = {
            "query": query,
            "start": str(current_start),
            "end": str(end_ns),
            "limit": limit,
            "direction": "FORWARD",
        }
        resp = requests.get(f"{LOKI_URL}/loki/api/v1/query_range", params=params)
        resp.raise_for_status()
        result = resp.json().get("data", {}).get("result", [])
        if not result:
            break
        all_results.extend(result)
        last_entry = result[-1]["values"][-1]
        current_start = int(last_entry[0]) + 1
    return all_results


def _extract_lines(streams) -> List[str]:
    lines: List[str] = []
    for s in streams:
        for ts, msg in s.get("values", []):
            ts_iso = datetime.fromtimestamp(int(ts) / 1e9, tzutc()).isoformat()
            if msg := msg.strip():
                lines.append(f"[{ts_iso}] {msg}")
    return lines


# State Definition
class EventState(TypedDict):
    start_ns: int
    end_ns: int
    raw_logs: List[str]
    chunk: List[str] | None
    result: List[Dict[str, Any]] | None
    agg: List[Any]


# Graph Nodes
def fetch_logs(state: EventState) -> EventState:
    streams = _query_loki(state["start_ns"], state["end_ns"])
    state["raw_logs"] = _extract_lines(streams)
    state["agg"] = []
    logger.info(f"[FetchLogs] pulled {len(state['raw_logs'])} lines")
    return state


def chunker(state: EventState) -> EventState:
    if not state["raw_logs"]:
        state["chunk"] = None
        return state
    state["chunk"] = state["raw_logs"][:CHUNK_SIZE]
    state["raw_logs"] = state["raw_logs"][CHUNK_SIZE:]
    logger.info(
        f"[Chunker] emitting {len(state['chunk'])} lines ({len(state['raw_logs'])} left)"
    )
    return state


def categoriser(state: EventState) -> EventState:
    if state["chunk"] is None:
        return state
    joined = (
        "\n".join(state["chunk"])
        if isinstance(state["chunk"], list)
        else state["chunk"]
    )
    raw_txt = categorise_runnable.invoke({"logs": joined}).strip()
    cleaned = raw_txt.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[-2]
    try:
        parsed = json.loads(cleaned)
    except Exception:
        parsed = [
            {
                "severity": "UNKNOWN",
                "action": "investigate",
                "logs": state["chunk"],
                "context": "",
                "source": "",
                "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "technique": "",
            }
        ]
    state["result"] = parsed
    for entry in parsed:
        logger.info(f"[Categoriser] → {entry.get('severity', 'UNKNOWN')}")
    return state


def merger(state: EventState) -> EventState:
    if state.get("result"):
        state["agg"].append(state["result"])
    return state


def consolidate(state: EventState) -> EventState:
    flat = [entry for chunk in state.get("agg", []) for entry in chunk]
    raw = consolidate_runnable.invoke({"events": json.dumps(flat)})
    try:
        state["agg"] = [json.loads(raw)]
    except Exception:
        state["agg"] = [flat]
    return state

### End of Graph Nodes ###

# Builds the pipeline
def compile_pipeline():
    g = StateGraph(EventState)
    g.add_node("fetch", fetch_logs)
    g.add_node("chunker", chunker)
    g.add_node("categorise", categoriser)
    g.add_node("merge", merger)
    g.add_node("consolidate", consolidate)

    def _summarise_node(state: EventState) -> EventState:
        state["report"] = summarise(state["agg"])
        return state

    g.add_node("summarise", _summarise_node)
    g.set_entry_point("fetch")
    g.add_edge("fetch", "chunker")

    def _after_chunk(state: EventState):
        return "consolidate" if state["chunk"] is None else "categorise"

    g.add_conditional_edges("chunker", _after_chunk)
    g.add_edge("categorise", "merge")
    g.add_edge("merge", "chunker")
    g.add_edge("consolidate", "summarise")
    g.add_edge("summarise", END)

    return g.compile()


pipeline = compile_pipeline()


# Summary Helper
def summarise(aggregate: List[Any]) -> pd.DataFrame:
    # Handle possible dict-of-groups at top level
    groups: List[Dict[str, Any]] = []
    for item in aggregate:
        if isinstance(item, dict) and all(
            isinstance(k, str) and k.isdigit() for k in item.keys()
        ):
            groups.extend(item.values())
        elif isinstance(item, list):
            groups.extend(item)
        else:
            groups.append(item)

    rows: List[Dict[str, Any]] = []
    for group in groups:
        if isinstance(group, dict):
            actor = group.get("actor")
            events = group.get("events")
            if isinstance(events, list):
                for ev in events:
                    row = {**ev}
                    if actor is not None:
                        row["actor"] = actor
                    rows.append(row)
            else:
                row = {**group}
                if actor is not None:
                    row["actor"] = actor
                rows.append(row)
        else:
            logger.warning("Unexpected group format", group=group)

    df = pd.DataFrame(rows)
    return df
