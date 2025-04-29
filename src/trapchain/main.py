import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from trapchain.graph import pipeline, summarise

import structlog

logger = structlog.get_logger(__name__)


def run_window(
    hours: int = 6, md_path: str = "reports/latest_report.md"
) -> pd.DataFrame:
    now = datetime.utcnow()
    start = now - timedelta(hours=hours)

    state = pipeline.invoke(
        {
            "start_ns": int(start.timestamp() * 1e9),
            "end_ns": int(now.timestamp() * 1e9),
        },
        {"recursion_limit": 100}
    )

    df = state.get("report") or summarise(state["agg"])

    logger.info(
        "report",
        start=start.isoformat(),
        end=now.isoformat(),
        report=df.to_dict(orient="records"),
    )

    if df.empty:
        print("No relevant events.")
    else:
        print("\n=== Summary table ===")
        print(df["severity"].value_counts())

    md_file = Path(md_path)
    md_file.parent.mkdir(parents=True, exist_ok=True)

    with md_file.open("w", encoding="utf-8") as f:
        # Header
        f.write("# SOC Summary Report\n\n")
        f.write(f"Time window: **{start.isoformat()}Z** → **{now.isoformat()}Z**\n\n")

        if df.empty:
            f.write("_No relevant events detected._\n")
        else:
            # Event Breakdown table
            vc = df["severity"].value_counts().rename("count").reset_index()
            f.write("## Event Breakdown\n\n")
            f.write(vc.to_markdown(index=False))
            f.write("\n\n## Detailed Events by Severity\n\n")

            # Define severity order
            order = ["CRITICAL", "ERROR", "WARNING", "INFO", "UNKNOWN"]
            for level in order:
                subset = df[df["severity"] == level]
                if subset.empty:
                    continue
                f.write(f"### {level}\n\n")
                for _, row in subset.iterrows():
                    actor = row.get("actor", "Unknown")
                    action = row.get("action", "")
                    context = row.get("context", "")
                    source = row.get("source", "")
                    timestamp = row.get("timestamp", "")
                    technique = row.get("technique", "")
                    # Event header
                    header = f"- **Actor:** {actor} | **Action:** {action} | **Context:** {context} | **Source:** {source} | **Time:** {timestamp}"
                    if technique:
                        header += f" | **Technique:** {technique}"
                    f.write(header + "\n")
                    # Logs list
                    logs = row.get("logs", [])
                    for log in logs:
                        f.write(f"    - {log}\n")
                    f.write("\n")

    print(f"\nMarkdown report written to {md_file.resolve()}")
    return df


if __name__ == "__main__":
    run_window()