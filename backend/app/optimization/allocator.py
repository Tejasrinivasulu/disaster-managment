"""Resource allocation optimizer (OR-Tools when available, greedy fallback)."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

PRIORITY_WEIGHT = {
    "low": 1.0,
    "medium": 2.0,
    "high": 3.5,
    "critical": 5.0,
}

RESOURCE_KEYS = {
    "food_packets": "food_demand",
    "water": "water_demand_litres",
    "medical_kits": "medical_kit_demand",
    "shelter": "shelter_demand",
}

try:
    from ortools.linear_solver import pywraplp

    HAS_ORTOOLS = True
except Exception:  # pragma: no cover - optional on serverless
    pywraplp = None  # type: ignore
    HAS_ORTOOLS = False


def _demand_items(zones: List[Dict[str, Any]]) -> List[Tuple]:
    items = []
    for zone in zones:
        zid = zone["id"]
        priority = str(zone.get("priority", "medium")).lower()
        weight = PRIORITY_WEIGHT.get(priority, 2.0) * float(
            zone.get("accessibility_score", 0.7) or 0.7
        )
        for rtype, demand_key in RESOURCE_KEYS.items():
            demand = float(zone.get(demand_key, 0) or 0)
            if demand <= 0:
                continue
            items.append((zid, rtype, demand, weight, zone))
    return items


def _pack_results(items: List[Tuple], allocated_map: Dict[Tuple, float], solver_status: str):
    results = []
    for zid, rtype, demand, weight, zone in items:
        allocated = float(allocated_map.get((zid, rtype), 0.0))
        shortage = max(0.0, demand - allocated)
        coverage = (allocated / demand * 100.0) if demand > 0 else 100.0
        results.append(
            {
                "zone_id": zid,
                "zone": zone.get("name", str(zid)),
                "resource": rtype,
                "requested_quantity": round(demand, 2),
                "allocated_quantity": round(allocated, 2),
                "shortage": round(shortage, 2),
                "coverage_percentage": round(coverage, 2),
                "priority": zone.get("priority", "medium"),
            }
        )
    total_requested = sum(r["requested_quantity"] for r in results) or 1
    total_allocated = sum(r["allocated_quantity"] for r in results)
    return {
        "allocations": results,
        "summary": {
            "total_requested": round(total_requested, 2),
            "total_allocated": round(total_allocated, 2),
            "overall_coverage_pct": round(total_allocated / total_requested * 100, 2),
            "solver_status": solver_status,
        },
    }


def _allocate_greedy(
    zones: List[Dict[str, Any]],
    supplies: Dict[str, float],
    transport_capacity: float | None = None,
) -> Dict[str, Any]:
    """Weighted proportional allocation without OR-Tools."""
    items = _demand_items(zones)
    remaining = {k: float(v) for k, v in supplies.items()}
    transport_left = float(transport_capacity) if transport_capacity is not None else None
    allocated_map: Dict[Tuple, float] = {}

    # Highest weight/demand first
    ordered = sorted(items, key=lambda x: x[3] / max(x[2], 1e-6), reverse=True)
    for zid, rtype, demand, weight, zone in ordered:
        avail = remaining.get(rtype, 0.0)
        if avail <= 0:
            allocated_map[(zid, rtype)] = 0.0
            continue
        take = min(demand, avail)
        if transport_left is not None:
            take = min(take, max(0.0, transport_left))
            transport_left -= take
        allocated_map[(zid, rtype)] = take
        remaining[rtype] = avail - take

    return _pack_results(items, allocated_map, "greedy_fallback")


def _allocate_ortools(
    zones: List[Dict[str, Any]],
    supplies: Dict[str, float],
    transport_capacity: float | None = None,
) -> Dict[str, Any]:
    solver = pywraplp.Solver.CreateSolver("GLOP")
    if solver is None:
        raise RuntimeError("OR-Tools GLOP solver unavailable")

    items = _demand_items(zones)
    variables = {}
    for zid, rtype, demand, weight, zone in items:
        var = solver.NumVar(0, demand, f"z{zid}_{rtype}")
        variables[(zid, rtype)] = (var, demand, weight, zone)

    for rtype, available in supplies.items():
        related = [variables[k][0] for k in variables if k[1] == rtype]
        if related:
            solver.Add(sum(related) <= float(available))

    if transport_capacity is not None and variables:
        solver.Add(sum(v[0] for v in variables.values()) <= float(transport_capacity))

    objective = solver.Objective()
    for (zid, rtype), (var, demand, weight, zone) in variables.items():
        objective.SetCoefficient(var, weight / max(demand, 1e-6))
    objective.SetMaximization()

    status = solver.Solve()
    if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        raise RuntimeError("Optimization failed to find a feasible solution")

    allocated_map = {
        key: float(var.solution_value()) for key, (var, *_rest) in variables.items()
    }
    items_for_pack = [
        (zid, rtype, demand, weight, zone)
        for (zid, rtype), (var, demand, weight, zone) in variables.items()
    ]
    label = "optimal" if status == pywraplp.Solver.OPTIMAL else "feasible"
    return _pack_results(items_for_pack, allocated_map, label)


def allocate_resources(
    zones: List[Dict[str, Any]],
    supplies: Dict[str, float],
    transport_capacity: float | None = None,
) -> Dict[str, Any]:
    """
    Maximize weighted coverage of zone demands given limited supplies.

    zones: list with id/name/priority/accessibility and demand fields
    supplies: mapping resource_type -> available quantity
    """
    if HAS_ORTOOLS:
        try:
            return _allocate_ortools(zones, supplies, transport_capacity)
        except Exception:
            return _allocate_greedy(zones, supplies, transport_capacity)
    return _allocate_greedy(zones, supplies, transport_capacity)
