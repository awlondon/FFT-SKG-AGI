from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class AgencyGateDecision:
    gate: str
    decision: str
    confidence: float

# Gate decision logic
def process_agency_gates(token: str, token_data: dict, adjacency_count: int = 0) -> list[AgencyGateDecision]:
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
    gates = ["explore", "reevaluate", "externalize", "prune"]
    decisions: list[AgencyGateDecision] = []
    frequency = token_data.get("frequency", 1)
    weight = token_data.get("weight", 1)
    for gate in gates:
        if gate == "explore":
            yes_weight = 0.4 + (frequency * 0.1) + (adjacency_count * 0.05)
            explore_decision = random.choices(["YES", "NO", "WITHHOLD"], weights=[yes_weight, 0.3, 0.2])[0]
            confidence = max(0.0, min(yes_weight, 1.0))
            decisions.append(AgencyGateDecision(gate, explore_decision, confidence))
        elif gate == "reevaluate":
            yes_weight = 0.3 + (weight * 0.15) + (adjacency_count * 0.05)
            reevaluate_decision = random.choices(["YES", "NO", "WITHHOLD"], weights=[yes_weight, 0.4, 0.1])[0]
            confidence = max(0.0, min(yes_weight, 1.0))
            decisions.append(AgencyGateDecision(gate, reevaluate_decision, confidence))
        elif gate == "externalize":
            yes_weight = 0.2 + (weight * 0.25) + (frequency * 0.05)
            externalize_decision = random.choices(["YES", "NO", "WITHHOLD"], weights=[yes_weight, 0.5, 0.1])[0]
            confidence = max(0.0, min(yes_weight, 1.0))
            decisions.append(AgencyGateDecision(gate, externalize_decision, confidence))
        elif gate == "prune":
            yes_weight = 0.6 - (weight * 0.1) - (frequency * 0.05)
            prune_decision = random.choices(["YES", "NO", "WITHHOLD"], weights=[yes_weight, 0.3, 0.1])[0]
            confidence = max(0.0, min(yes_weight, 1.0))
            decisions.append(AgencyGateDecision(gate, prune_decision, confidence))
    return decisions