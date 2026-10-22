from collections import Counter
from datetime import datetime
from typing import Optional
from fastapi.responses import RedirectResponse
import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Incident & Log Analyzer API",
    description="Analyze logs and check incident SLA status.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# SLA targets in minutes: (response, resolution)
SLA = {
    "P1": (15, 240),
    "P2": (30, 480),
    "P3": (120, 1440),
    "P4": (480, 4320),
}

LOG_PATTERN = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>INFO|WARN|WARNING|ERROR|CRITICAL|DEBUG)\s+(?P<msg>.*)"
)


class LogInput(BaseModel):
    logs: str


class SlaInput(BaseModel):
    priority: str
    opened_at: datetime
    resolved_at: Optional[datetime] = None

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(data: LogInput):
    levels = Counter()
    errors = Counter()
    hours = Counter()
    for line in data.logs.splitlines():
        m = LOG_PATTERN.search(line)
        if not m:
            continue
        level = m["level"].replace("WARNING", "WARN")
        levels[level] += 1
        if level in ("ERROR", "CRITICAL"):
            errors[m["msg"].strip()] += 1
            hours[m["ts"][11:13] + ":00"] += 1
    peak = hours.most_common(1)
    return {
        "total_lines_parsed": sum(levels.values()),
        "by_level": dict(levels),
        "top_errors": [{"message": k, "count": v} for k, v in errors.most_common(5)],
        "peak_error_hour": peak[0][0] if peak else None,
    }


@app.post("/sla")
def sla(data: SlaInput):
    p = data.priority.upper()
    if p not in SLA:
        return {"error": "priority must be P1, P2, P3, or P4"}
    _, resolution_limit = SLA[p]
    end = data.resolved_at or datetime.now(data.opened_at.tzinfo)
    elapsed = (end - data.opened_at).total_seconds() / 60
    return {
        "priority": p,
        "elapsed_minutes": round(elapsed, 1),
        "resolution_target_minutes": resolution_limit,
        "status": "within_sla" if elapsed <= resolution_limit else "breached",
        "resolved": data.resolved_at is not None,
    }