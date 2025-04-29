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
from trapchain.nodes.nodes import EventState, fetch_logs, chunker, merger, categoriser, consolidate
from trapchain.utils.utils import summarise

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

logger = structlog.get_logger(__name__)

# ────────────────────────────────────────────────────────────────
# 1. Prompt + LLM
# ────────────────────────────────────────────────────────────────
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
        ("system", "You are a SOC Analyst Assistant. Consolidate the following categorized events into a single JSON list, preserving all fields and grouping related events by actor. Return valid JSON."),
        ("human", "Events: {events}")
    ]
)
consolidate_runnable = consolidate_prompt | llm | StrOutputParser()

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

