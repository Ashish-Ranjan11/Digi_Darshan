from __future__ import annotations

from datetime import datetime, timezone
from random import randint


def clamp(value: int | float, minimum: int | float, maximum: int | float):
    return max(minimum, min(value, maximum))


def classify_risk(
    occupancy_percent: float,
    density_score: float,
    inflow_per_min: int,
    outflow_per_min: int,
) -> str:
    net_flow = inflow_per_min - outflow_per_min

    if occupancy_percent >= 90 or density_score >= 0.88:
        return "critical"

    if occupancy_percent >= 80 and net_flow > 20:
        return "critical"

    if occupancy_percent >= 70 or density_score >= 0.70:
        return "high"

    if occupancy_percent >= 45 or density_score >= 0.45:
        return "medium"

    return "low"


def trend_label(inflow_per_min: int, outflow_per_min: int) -> str:
    net_flow = inflow_per_min - outflow_per_min

    if net_flow >= 25:
        return "rapidly_rising"

    if net_flow >= 8:
        return "rising"

    if net_flow <= -15:
        return "falling"

    return "stable"


def movement_advice(level: str) -> str:
    if level == "critical":
        return "Stop new entry temporarily, open emergency corridors, redirect pilgrims to alternate gates, and alert response teams."

    if level == "high":
        return "Slow down entry, open additional gates, divert pilgrims to lower-density corridors, and increase volunteer presence."

    if level == "medium":
        return "Maintain controlled entry, keep queue lanes active, and monitor inflow closely."

    return "Crowd movement is normal. Continue standard queue flow."


def gate_advice(level: str) -> dict:
    if level == "critical":
        return {
            "entry_gate_status": "restricted",
            "exit_gate_status": "fully_open",
            "recommended_gate_action": "Use Gate B and Gate C for exit pressure release. Pause Gate A entry.",
        }

    if level == "high":
        return {
            "entry_gate_status": "controlled",
            "exit_gate_status": "open",
            "recommended_gate_action": "Open one extra entry lane and keep all exit lanes active.",
        }

    if level == "medium":
        return {
            "entry_gate_status": "normal_controlled",
            "exit_gate_status": "open",
            "recommended_gate_action": "Maintain current gate allocation and monitor inflow.",
        }

    return {
        "entry_gate_status": "normal",
        "exit_gate_status": "normal",
        "recommended_gate_action": "No gate intervention required.",
    }


def build_live_payload(
    temple,
    occupancy: int,
    inflow_per_min: int,
    outflow_per_min: int,
    source: str = "sensor-simulation",
    notes: str | None = None,
) -> dict:
    max_capacity = temple.max_capacity or 1

    safe_occupancy = int(clamp(occupancy, 0, max_capacity))
    occupancy_percent = round((safe_occupancy / max_capacity) * 100, 2)

    net_flow = max(0, inflow_per_min - outflow_per_min)
    density_score = round(clamp((occupancy_percent / 100) + (net_flow / 220), 0, 1), 2)

    level = classify_risk(
        occupancy_percent=occupancy_percent,
        density_score=density_score,
        inflow_per_min=inflow_per_min,
        outflow_per_min=outflow_per_min,
    )

    gate = gate_advice(level)

    return {
        "type": "crowd_update",
        "temple_id": temple.id,
        "temple_name": temple.name,
        "city": temple.city,
        "source": source,
        "occupancy": safe_occupancy,
        "max_capacity": max_capacity,
        "occupancy_percent": occupancy_percent,
        "inflow_per_min": inflow_per_min,
        "outflow_per_min": outflow_per_min,
        "net_flow_per_min": inflow_per_min - outflow_per_min,
        "density_score": density_score,
        "crowd_level": level,
        "trend": trend_label(inflow_per_min, outflow_per_min),
        "recommendation": movement_advice(level),
        "entry_gate_status": gate["entry_gate_status"],
        "exit_gate_status": gate["exit_gate_status"],
        "recommended_gate_action": gate["recommended_gate_action"],
        "notes": notes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def next_simulated_counts(temple) -> tuple[int, int, int]:
    current = temple.current_occupancy or 0
    max_capacity = temple.max_capacity or 1
    percent = (current / max_capacity) * 100

    if percent < 35:
        inflow = randint(35, 90)
        outflow = randint(10, 45)
    elif percent < 65:
        inflow = randint(25, 75)
        outflow = randint(20, 60)
    elif percent < 85:
        inflow = randint(15, 55)
        outflow = randint(25, 75)
    else:
        inflow = randint(5, 35)
        outflow = randint(40, 95)

    next_occupancy = current + inflow - outflow
    next_occupancy = int(clamp(next_occupancy, 0, max_capacity))

    return next_occupancy, inflow, outflow
