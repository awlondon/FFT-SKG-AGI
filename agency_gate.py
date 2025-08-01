"""Agency gate decision logic.

This module evaluates a set of symbolic "gates" that determine how a token
should be handled by the engine.  Each call to :func:`process_agency_gates`
returns a list of dictionaries containing the gate name, decision and
confidence.  This dictionary structure is the single supported return type.
"""

from datetime import datetime
import random

# Gate decision logic
def process_agency_gates(token: str, token_data: dict, adjacency_count: int = 0) -> list[dict]:
    """
    Evaluate a series of agency gates for a token.  The gates decide whether to
    explore further, reevaluate, externalize the thought or prune the branch.

    Parameters
    ----------
    token : str
        The token being processed.
    token_data : dict
        Metadata about the token (e.g. frequency, weight) used to adjust
        probabilities.
    adjacency_count : int
        Number of adjacent tokens currently associated with this token.
    """
    print(f"[AgencyGate] Processing gates for token: {token}")
    gates = ["explore", "reevaluate", "externalize", "prune", "expression"]
    decisions: list[dict] = []
    frequency = token_data.get("frequency", 1)
    weight = token_data.get("weight", 1)
    for gate in gates:
        if gate == "explore":
            yes_weight = 0.4 + (frequency * 0.1) + (adjacency_count * 0.05)
            explore_decision = random.choices(["YES", "NO", "WITHHOLD"], weights=[yes_weight, 0.3, 0.2])[0]
            confidence = max(0.0, min(yes_weight, 1.0))
            decisions.append({
                "gate": gate,
                "decision": explore_decision,
                "confidence": confidence,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })
        elif gate == "reevaluate":
            yes_weight = 0.3 + (weight * 0.15) + (adjacency_count * 0.05)
            reevaluate_decision = random.choices(["YES", "NO", "WITHHOLD"], weights=[yes_weight, 0.4, 0.1])[0]
            confidence = max(0.0, min(yes_weight, 1.0))
            decisions.append({
                "gate": gate,
                "decision": reevaluate_decision,
                "confidence": confidence,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })
        elif gate == "externalize":
            yes_weight = 0.2 + (weight * 0.25) + (frequency * 0.05)
            externalize_decision = random.choices(["YES", "NO", "WITHHOLD"], weights=[yes_weight, 0.5, 0.1])[0]
            confidence = max(0.0, min(yes_weight, 1.0))
            decisions.append({
                "gate": gate,
                "decision": externalize_decision,
                "confidence": confidence,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })
        elif gate == "prune":
            prune_weight = 0.6 - (weight * 0.1) - (frequency * 0.05)
            prune_decision = random.choices(["YES", "NO", "WITHHOLD"], weights=[prune_weight, 0.3, 0.1])[0]
            decisions.append({
                "gate": gate,
                "decision": prune_decision,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        elif gate == "expression":
            speak_conf = min(1.0, 0.3 + (weight * 0.1))
            gesture_conf = 1.0 - speak_conf
            if speak_conf >= gesture_conf:
                decision = "speak"
                confidence = speak_conf
            else:
                decision = "gesture"
                confidence = gesture_conf
            decisions.append({
                "gate": gate,
                "decision": decision,
                "confidence": round(confidence, 2),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
    return decisions
