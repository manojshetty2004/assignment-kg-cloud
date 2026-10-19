"""
Three-layer loan reasoning knowledge graph.

Layers:
1. Case layer: observed facts for Application A and B.
2. Shared knowledge layer: early payment -> paying before due -> possible supplier
   pressure/liquidity strain -> thin cash buffer -> repayment risk.
3. Conditions layer: facts that cancel or amplify parts of the hypothesis.

The recommendation is computed by traversing the knowledge chain and applying
present conditions. This is an explainable toy example, not a validated credit model.
Run: python loan_reasoning_graph.py
"""
from __future__ import annotations

import networkx as nx


def build_graph() -> nx.DiGraph:
    graph = nx.DiGraph()

    # 1. CASE LAYER: facts only; no fixed decision edges.
    case_nodes = {
        "app_A": {"label": "Application A", "layer": "case", "kind": "Application"},
        "app_B": {"label": "Application B", "layer": "case", "kind": "Application"},
        "credit_A": {"label": "Credit score: 720", "layer": "case", "kind": "Fact"},
        "credit_B": {"label": "Credit score: 718", "layer": "case", "kind": "Fact"},
        "collateral_A": {"label": "Collateral: ₹25 lakh", "layer": "case", "kind": "Fact"},
        "collateral_B": {"label": "Collateral: ₹25 lakh", "layer": "case", "kind": "Fact"},
        "amount_A": {"label": "Loan requested: ₹10 lakh", "layer": "case", "kind": "Fact"},
        "amount_B": {"label": "Loan requested: ₹10 lakh", "layer": "case", "kind": "Fact"},
        "payment_A": {
            "label": "Invoices paid on time (not unusually early)",
            "layer": "case", "kind": "PaymentTiming", "timing": "normal"
        },
        "payment_B": {
            "label": "Invoices paid unusually early",
            "layer": "case", "kind": "PaymentTiming", "timing": "early"
        },
    }
    graph.add_nodes_from((node, attrs) for node, attrs in case_nodes.items())

    for app, credit, collateral, amount, payment in [
        ("app_A", "credit_A", "collateral_A", "amount_A", "payment_A"),
        ("app_B", "credit_B", "collateral_B", "amount_B", "payment_B"),
    ]:
        graph.add_edge(app, credit, relation="has_fact")
        graph.add_edge(app, collateral, relation="has_fact")
        graph.add_edge(app, amount, relation="has_fact")
        graph.add_edge(app, payment, relation="has_payment_timing")

    # 2. SHARED KNOWLEDGE LAYER: an explicit, uncertain hypothesis chain.
    knowledge_nodes = {
        "early_payment": {"label": "Early payment", "layer": "knowledge", "kind": "Concept"},
        "before_due": {"label": "Paying before due date", "layer": "knowledge", "kind": "Interpretation"},
        "supplier_pressure": {
            "label": "Possible supplier pressure / liquidity strain",
            "layer": "knowledge", "kind": "Hypothesis"
        },
        "thin_buffer": {"label": "Thin cash buffer", "layer": "knowledge", "kind": "Hypothesis"},
        "repayment_risk": {"label": "Potential repayment risk", "layer": "knowledge", "kind": "Risk"},
    }
    graph.add_nodes_from((node, attrs) for node, attrs in knowledge_nodes.items())

    graph.add_edge("payment_B", "early_payment", relation="observed_as")
    graph.add_edge("early_payment", "before_due", relation="means")
    graph.add_edge("before_due", "supplier_pressure", relation="may_suggest")
    graph.add_edge("supplier_pressure", "thin_buffer", relation="could_reflect")
    graph.add_edge("thin_buffer", "repayment_risk", relation="may_increase")

    # 3. CONDITIONS LAYER: scenario evidence, not assumptions about every applicant.
    condition_nodes = {
        "discount": {
            "label": "Discount taken deliberately", "layer": "condition",
            "kind": "MitigatingCondition",
            "effect": "cancels",
            "target": "supplier_pressure",
        },
        "strong_reserves": {
            "label": "Strong cash reserves", "layer": "condition",
            "kind": "MitigatingCondition",
            "effect": "cancels",
            "target": "thin_buffer",
        },
        "seasonal_bulk_discount": {
            "label": "Seasonal bulk-buy discount", "layer": "condition",
            "kind": "MitigatingCondition",
            "effect": "cancels",
            "target": "supplier_pressure",
        },
        "supplier_demand": {
            "label": "Supplier requires prepayment", "layer": "condition",
            "kind": "AmplifyingCondition",
            "effect": "amplifies",
            "target": "supplier_pressure",
        },
    }
    graph.add_nodes_from((node, attrs) for node, attrs in condition_nodes.items())
    for condition_id, attrs in condition_nodes.items():
        graph.add_edge(condition_id, attrs["target"], relation=attrs["effect"])

    return graph


def get_reasoning_path(graph: nx.DiGraph) -> list[str]:
    """Walk the shared knowledge chain from early payment to repayment risk."""
    return nx.shortest_path(graph, "early_payment", "repayment_risk")


def assess_case(
    graph: nx.DiGraph,
    app_id: str,
    conditions_present: set[str] | None = None,
) -> dict:
    """Compute a cautious recommendation from the observed timing and conditions."""
    conditions_present = conditions_present or set()
    if app_id not in {"app_A", "app_B"}:
        raise ValueError("app_id must be 'app_A' or 'app_B'")

    payment_node = "payment_A" if app_id == "app_A" else "payment_B"
    early = graph.nodes[payment_node]["timing"] == "early"

    if not early:
        return {
            "application": graph.nodes[app_id]["label"],
            "level": "No warning from this signal",
            "decision": "Continue normal underwriting checks",
            "path": [],
            "conditions": [],
            "explanation": "No unusual early-payment signal was observed.",
        }

    path = get_reasoning_path(graph)
    active_conditions = []
    cancelled = set()
    amplified = False

    for condition_id in conditions_present:
        if condition_id not in graph or graph.nodes[condition_id].get("layer") != "condition":
            raise ValueError(f"Unknown condition node: {condition_id}")
        relation = graph.edges[condition_id, graph.nodes[condition_id]["target"]]["relation"]
        active_conditions.append((graph.nodes[condition_id]["label"], relation))
        if relation == "cancels":
            cancelled.add(graph.nodes[condition_id]["target"])
        elif relation == "amplifies":
            amplified = True

    # Propagate a cancellation to downstream nodes, so a documented discount
    # interrupts the supplier-pressure path and strong reserves interrupt
    # the thin-buffer-to-risk path.
    if "supplier_pressure" in cancelled:
        cancelled.update({"thin_buffer", "repayment_risk"})
    if "thin_buffer" in cancelled:
        cancelled.add("repayment_risk")

    if "repayment_risk" in cancelled:
        level = "Signal substantially mitigated"
        decision = "Verify the mitigating evidence; do not escalate on timing alone"
        explanation = "Present counter-evidence interrupts the default risk path."
        visible_path = [node for node in path if node not in cancelled]
    else:
        level = "Elevated review priority" if amplified else "Needs review"
        decision = "Request evidence and manually review before deciding"
        explanation = (
            "The graph connects early payment to a possible liquidity concern, "
            "but the hypothesis is not proof of default."
        )
        visible_path = path

    return {
        "application": graph.nodes[app_id]["label"],
        "level": level,
        "decision": decision,
        "path": visible_path,
        "conditions": active_conditions,
        "explanation": explanation,
    }


def print_assessment(graph: nx.DiGraph, result: dict) -> None:
    print(f"\\n{result['application']}")
    print(f"  Assessment: {result['level']}")
    print(f"  Recommendation: {result['decision']}")
    if result["path"]:
        print("  Reasoning path:")
        for i, node in enumerate(result["path"]):
            print(f"    {i + 1}. {graph.nodes[node]['label']}")
            if i < len(result["path"]) - 1:
                nxt = result["path"][i + 1]
                print(f"       --{graph.edges[node, nxt]['relation']}-->")
    if result["conditions"]:
        print("  Conditions considered:")
        for label, relation in result["conditions"]:
            print(f"    - {label} [{relation}]")
    print(f"  Explanation: {result['explanation']}")


def main() -> None:
    graph = build_graph()
    print(f"Knowledge graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print("Layer counts:")
    for layer in ("case", "knowledge", "condition"):
        count = sum(1 for _, attrs in graph.nodes(data=True) if attrs.get("layer") == layer)
        print(f"  {layer}: {count} nodes")

    print_assessment(graph, assess_case(graph, "app_A"))
    print_assessment(graph, assess_case(graph, "app_B"))
    print_assessment(
        graph,
        assess_case(graph, "app_B", {"seasonal_bulk_discount", "strong_reserves"}),
    )
    print_assessment(
        graph,
        assess_case(graph, "app_B", {"supplier_demand"}),
    )


if __name__ == "__main__":
    main()
