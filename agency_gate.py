from datetime import datetime
import random

# Gate decision logic
def process_agency_gates(token, token_data, adjacency_count=0):
    print(f"[AgencyGate] Processing gates for token: {token}")

    # Example gates
    gates = ["explore", "reevaluate", "externalize", "prune"]
    decisions = []

    # The token data could include things like frequency, current glyph weight, etc.
    frequency = token_data.get("frequency", 1)
    weight = token_data.get("weight", 1)

    for gate in gates:
        # Adjust decision probabilities based on the token's context (e.g., weight, frequency)
        if gate == "explore":
            explore_weight = 0.4 + (frequency * 0.1) + (adjacency_count * 0.05)
            explore_decision = random.choices(["YES", "NO", "WITHHOLD"], weights=[explore_weight, 0.3, 0.2])[0]
            decisions.append({
                "gate": gate,
                "decision": explore_decision,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        
        elif gate == "reevaluate":
            # Reevaluate gate considers weight and how many adjacencies a token has
            reevaluate_weight = 0.3 + (weight * 0.15) + (adjacency_count * 0.05)
            reevaluate_decision = random.choices(["YES", "NO", "WITHHOLD"], weights=[reevaluate_weight, 0.4, 0.1])[0]
            decisions.append({
                "gate": gate,
                "decision": reevaluate_decision,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

        elif gate == "externalize":
            externalize_weight = 0.2 + (weight * 0.25) + (frequency * 0.05)
            externalize_decision = random.choices(["YES", "NO", "WITHHOLD"], weights=[externalize_weight, 0.5, 0.1])[0]
            decisions.append({
                "gate": gate,
                "decision": externalize_decision,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

        elif gate == "prune":
            prune_weight = 0.6 - (weight * 0.1) - (frequency * 0.05)
            prune_decision = random.choices(["YES", "NO", "WITHHOLD"], weights=[prune_weight, 0.3, 0.1])[0]
            decisions.append({
                "gate": gate,
                "decision": prune_decision,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

    return decisions
