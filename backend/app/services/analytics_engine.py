from __future__ import annotations

from datetime import datetime, timezone


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def risk_from_percent(percent: float) -> str:
    if percent >= 90:
        return "critical"
    if percent >= 75:
        return "high"
    if percent >= 50:
        return "medium"
    return "low"


def risk_score_from_level(level: str) -> int:
    if level == "critical":
        return 100
    if level == "high":
        return 75
    if level == "medium":
        return 50
    return 25


def trend_from_growth(growth_rate: float) -> str:
    if growth_rate >= 35:
        return "rapidly_rising"
    if growth_rate >= 12:
        return "rising"
    if growth_rate <= -20:
        return "falling"
    return "stable"


def analyze_anomalies(
    occupancy_percent: float,
    avg_inflow: float,
    avg_outflow: float,
    growth_rate: float,
    density_score: float,
) -> list[dict]:
    anomalies = []

    if occupancy_percent >= 90:
        anomalies.append(
            {
                "type": "critical_occupancy",
                "severity": "critical",
                "title": "Critical temple occupancy",
                "message": "Occupancy has crossed 90%. Immediate entry control is required.",
            }
        )

    if growth_rate >= 40:
        anomalies.append(
            {
                "type": "sudden_spike",
                "severity": "critical",
                "title": "Sudden crowd spike detected",
                "message": "Crowd count is rising too quickly within the selected time window.",
            }
        )

    if avg_inflow > avg_outflow * 2 and avg_inflow > 30:
        anomalies.append(
            {
                "type": "inflow_outflow_imbalance",
                "severity": "warning",
                "title": "Inflow is much higher than outflow",
                "message": "More pilgrims are entering than exiting. Gate and queue control should be adjusted.",
            }
        )

    if density_score >= 0.85:
        anomalies.append(
            {
                "type": "high_density_score",
                "severity": "critical",
                "title": "High density pressure",
                "message": "Density score is near unsafe range. Crowd diversion is recommended.",
            }
        )

    if occupancy_percent >= 75 and avg_outflow < 20:
        anomalies.append(
            {
                "type": "possible_exit_blockage",
                "severity": "warning",
                "title": "Possible exit slowdown",
                "message": "Occupancy is high while outflow is low. Exit corridor may need support.",
            }
        )

    return anomalies


def choose_intervention(
    risk_level: str,
    anomalies: list[dict],
    avg_inflow: float,
    avg_outflow: float,
) -> dict:
    anomaly_types = {item["type"] for item in anomalies}

    if risk_level == "critical" or "critical_occupancy" in anomaly_types:
        return {
            "priority": "critical",
            "primary_action": "Pause Entry",
            "secondary_action": "Activate Emergency Exit",
            "message": "Pause new entries, open all exits, and activate emergency volunteers.",
            "recommended_command": "pause_entry",
        }

    if "sudden_spike" in anomaly_types:
        return {
            "priority": "critical",
            "primary_action": "Open Alternate Gates",
            "secondary_action": "Divert Main Queue",
            "message": "Open Gate B/Gate C and divert pilgrims away from the main queue corridor.",
            "recommended_command": "open_gate_b",
        }

    if "possible_exit_blockage" in anomaly_types:
        return {
            "priority": "warning",
            "primary_action": "Clear Exit Corridor",
            "secondary_action": "Increase Volunteer Support",
            "message": "Improve exit flow and guide pilgrims towards low-density exit routes.",
            "recommended_command": "activate_emergency_exit",
        }

    if avg_inflow > avg_outflow:
        return {
            "priority": "warning",
            "primary_action": "Slow Entry",
            "secondary_action": "Prepare Diversion",
            "message": "Slow down entry and keep alternate gates ready.",
            "recommended_command": "open_gate_b",
        }

    return {
        "priority": "normal",
        "primary_action": "Continue Monitoring",
        "secondary_action": "No Immediate Action",
        "message": "Crowd flow is stable. Continue standard monitoring.",
        "recommended_command": "resume_normal_flow",
    }


def calculate_stability_score(
    occupancy_percent: float,
    growth_rate: float,
    anomaly_count: int,
    avg_density: float,
) -> int:
    score = 100

    score -= occupancy_percent * 0.35
    score -= abs(growth_rate) * 0.45
    score -= anomaly_count * 12
    score -= avg_density * 20

    return int(clamp(score, 0, 100))


def build_realtime_analysis_payload(temple, readings: list, window_minutes: int) -> dict:
    max_capacity = temple.max_capacity or 1
    current_occupancy = temple.current_occupancy or 0
    current_percent = round((current_occupancy / max_capacity) * 100, 2)

    if not readings:
        risk_level = risk_from_percent(current_percent)

        return {
            "temple_id": temple.id,
            "temple_name": temple.name,
            "city": temple.city,
            "window_minutes": window_minutes,
            "readings_count": 0,
            "current_occupancy": current_occupancy,
            "max_capacity": max_capacity,
            "current_occupancy_percent": current_percent,
            "average_occupancy": current_occupancy,
            "average_occupancy_percent": current_percent,
            "peak_occupancy": current_occupancy,
            "peak_occupancy_percent": current_percent,
            "average_inflow_per_min": 0,
            "average_outflow_per_min": 0,
            "net_flow_per_min": 0,
            "growth_rate_percent": 0,
            "average_density_score": 0,
            "risk_level": risk_level,
            "risk_score": risk_score_from_level(risk_level),
            "trend": "stable",
            "system_stability_score": calculate_stability_score(
                current_percent, 0, 0, 0
            ),
            "anomalies": [],
            "recommended_intervention": choose_intervention(risk_level, [], 0, 0),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    occupancies = [reading.occupancy or 0 for reading in readings]
    inflows = [reading.inflow_per_min or 0 for reading in readings]
    outflows = [reading.outflow_per_min or 0 for reading in readings]
    density_scores = [reading.density_score or 0 for reading in readings]

    first_occupancy = occupancies[0]
    last_occupancy = occupancies[-1]

    average_occupancy = round(sum(occupancies) / len(occupancies), 2)
    peak_occupancy = max(occupancies)

    average_occupancy_percent = round((average_occupancy / max_capacity) * 100, 2)
    peak_occupancy_percent = round((peak_occupancy / max_capacity) * 100, 2)

    avg_inflow = round(sum(inflows) / len(inflows), 2)
    avg_outflow = round(sum(outflows) / len(outflows), 2)
    avg_density = round(sum(density_scores) / len(density_scores), 2)

    net_flow = round(avg_inflow - avg_outflow, 2)

    if first_occupancy <= 0:
        growth_rate = 0
    else:
        growth_rate = round(
            ((last_occupancy - first_occupancy) / first_occupancy) * 100,
            2,
        )

    risk_level = risk_from_percent(max(current_percent, peak_occupancy_percent))

    anomalies = analyze_anomalies(
        occupancy_percent=current_percent,
        avg_inflow=avg_inflow,
        avg_outflow=avg_outflow,
        growth_rate=growth_rate,
        density_score=avg_density,
    )

    stability_score = calculate_stability_score(
        occupancy_percent=current_percent,
        growth_rate=growth_rate,
        anomaly_count=len(anomalies),
        avg_density=avg_density,
    )

    return {
        "temple_id": temple.id,
        "temple_name": temple.name,
        "city": temple.city,
        "window_minutes": window_minutes,
        "readings_count": len(readings),
        "current_occupancy": current_occupancy,
        "max_capacity": max_capacity,
        "current_occupancy_percent": current_percent,
        "average_occupancy": average_occupancy,
        "average_occupancy_percent": average_occupancy_percent,
        "peak_occupancy": peak_occupancy,
        "peak_occupancy_percent": peak_occupancy_percent,
        "average_inflow_per_min": avg_inflow,
        "average_outflow_per_min": avg_outflow,
        "net_flow_per_min": net_flow,
        "growth_rate_percent": growth_rate,
        "average_density_score": avg_density,
        "risk_level": risk_level,
        "risk_score": risk_score_from_level(risk_level),
        "trend": trend_from_growth(growth_rate),
        "system_stability_score": stability_score,
        "anomalies": anomalies,
        "recommended_intervention": choose_intervention(
            risk_level=risk_level,
            anomalies=anomalies,
            avg_inflow=avg_inflow,
            avg_outflow=avg_outflow,
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
