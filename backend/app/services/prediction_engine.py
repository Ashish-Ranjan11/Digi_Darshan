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


def action_from_risk(risk: str) -> str:
    if risk == "critical":
        return "Pause new entries, open all exits, activate emergency volunteers, and divert pilgrims to alternate corridors."
    if risk == "high":
        return "Slow down entry, open additional gates, increase volunteer guidance, and redirect pilgrims to low-density areas."
    if risk == "medium":
        return "Maintain controlled entry, monitor queue lanes, and prepare alternate route support."
    return "Crowd condition is normal. Continue standard queue flow."


def trend_from_flow(inflow: int, outflow: int) -> str:
    net = inflow - outflow

    if net >= 30:
        return "rapidly_rising"
    if net >= 10:
        return "rising"
    if net <= -15:
        return "falling"
    return "stable"


def build_heatmap(occupancy_percent: float, inflow: int, outflow: int) -> list[dict]:
    net = inflow - outflow

    gate_a = clamp(occupancy_percent + net * 0.20 + 8, 5, 100)
    gate_b = clamp(occupancy_percent - net * 0.10 - 10, 5, 100)
    main_queue = clamp(occupancy_percent + net * 0.15 + 15, 5, 100)
    darshan_hall = clamp(occupancy_percent + 5, 5, 100)
    exit_route = clamp(occupancy_percent - outflow * 0.10, 5, 100)
    parking_zone = clamp(occupancy_percent + inflow * 0.05 - 5, 5, 100)

    zones = [
        {
            "zone": "Gate A Entry",
            "crowd_percent": round(gate_a, 2),
            "role": "Primary entry pressure point",
        },
        {
            "zone": "Gate B Alternate Entry",
            "crowd_percent": round(gate_b, 2),
            "role": "Diversion entry route",
        },
        {
            "zone": "Main Queue Corridor",
            "crowd_percent": round(main_queue, 2),
            "role": "Main pilgrim movement lane",
        },
        {
            "zone": "Darshan Hall",
            "crowd_percent": round(darshan_hall, 2),
            "role": "Core temple occupancy zone",
        },
        {
            "zone": "Exit Corridor",
            "crowd_percent": round(exit_route, 2),
            "role": "Emergency and normal exit flow",
        },
        {
            "zone": "Parking / Shuttle Zone",
            "crowd_percent": round(parking_zone, 2),
            "role": "Vehicle and shuttle coordination zone",
        },
    ]

    for zone in zones:
        level = risk_from_percent(zone["crowd_percent"])
        zone["level"] = level

        if level == "critical":
            zone["advice"] = "Immediate intervention required."
        elif level == "high":
            zone["advice"] = "Divert crowd and increase control staff."
        elif level == "medium":
            zone["advice"] = "Monitor closely and keep route prepared."
        else:
            zone["advice"] = "Normal flow."

    return zones


def forecast_occupancy(
    current_occupancy: int,
    max_capacity: int,
    inflow: int,
    outflow: int,
    festival_mode: bool = False,
) -> list[dict]:
    multiplier = 1.35 if festival_mode else 1.0
    net_per_min = int((inflow * multiplier) - outflow)

    forecast = []

    for minutes in [15, 30, 60]:
        predicted = current_occupancy + net_per_min * minutes
        predicted = int(clamp(predicted, 0, max_capacity))

        percent = round((predicted / max_capacity) * 100, 2)
        risk = risk_from_percent(percent)

        forecast.append(
            {
                "minutes": minutes,
                "predicted_occupancy": predicted,
                "predicted_percent": percent,
                "risk": risk,
                "action": action_from_risk(risk),
            }
        )

    return forecast


def choose_safe_exit_route(heatmap: list[dict]) -> str:
    sorted_zones = sorted(heatmap, key=lambda item: item["crowd_percent"])

    for zone in sorted_zones:
        if "Exit" in zone["zone"] or "Gate B" in zone["zone"]:
            return f"Use {zone['zone']} because it currently has lower crowd pressure."

    return f"Use {sorted_zones[0]['zone']} as the safest available route."


def choose_parking_advice(heatmap: list[dict]) -> str:
    parking = next(
        (zone for zone in heatmap if "Parking" in zone["zone"]),
        None,
    )

    if not parking:
        return "Parking data unavailable."

    if parking["level"] in ["high", "critical"]:
        return "Redirect vehicles to secondary parking and increase shuttle frequency."

    if parking["level"] == "medium":
        return "Keep secondary parking ready and monitor vehicle inflow."

    return "Primary parking is currently manageable."


def build_prediction_payload(
    temple,
    readings: list,
    festival_mode: bool = False,
) -> dict:
    latest = readings[-1] if readings else None

    current_occupancy = temple.current_occupancy or 0
    max_capacity = temple.max_capacity or 1

    inflow = latest.inflow_per_min if latest else 0
    outflow = latest.outflow_per_min if latest else 0

    occupancy_percent = round((current_occupancy / max_capacity) * 100, 2)
    current_risk = risk_from_percent(occupancy_percent)

    heatmap = build_heatmap(
        occupancy_percent=occupancy_percent,
        inflow=inflow,
        outflow=outflow,
    )

    forecast = forecast_occupancy(
        current_occupancy=current_occupancy,
        max_capacity=max_capacity,
        inflow=inflow,
        outflow=outflow,
        festival_mode=festival_mode,
    )

    highest_forecast = max(forecast, key=lambda item: item["predicted_percent"])

    return {
        "temple_id": temple.id,
        "temple_name": temple.name,
        "city": temple.city,
        "festival_mode": festival_mode,
        "current_occupancy": current_occupancy,
        "max_capacity": max_capacity,
        "occupancy_percent": occupancy_percent,
        "current_risk": current_risk,
        "inflow_per_min": inflow,
        "outflow_per_min": outflow,
        "net_flow_per_min": inflow - outflow,
        "trend": trend_from_flow(inflow, outflow),
        "forecast": forecast,
        "heatmap": heatmap,
        "highest_predicted_risk": highest_forecast["risk"],
        "recommended_action": action_from_risk(highest_forecast["risk"]),
        "safe_exit_route": choose_safe_exit_route(heatmap),
        "parking_advice": choose_parking_advice(heatmap),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
