

#Three-layer loan reasoning knowledge graph.

from __future__ import annotations

import networkx as nx


# Illustrative assumptions for the example; not lending standards.
INVOICE_TERM_DAYS = 30
EARLY_PAYMENT_THRESHOLD_DAYS = 10


def build_graph() -> nx.DiGraph:
    graph = nx.DiGraph()

    # 1. CASE LAYER: facts about the two applications
    case_nodes = {
        "app_A": {
            "label": "Application A",
            "layer": "case",
            "kind": "Application",
        },
        "app_B": {
            "label": "Application B",
            "layer": "case",
            "kind": "Application",
        },
        "credit_A": {
            "label": "Credit score: 720",
            "layer": "case",
        },
        "credit_B": {
            "label": "Credit score: 718",
            "layer": "case",
        },
        "collateral_A": {
            "label": "Collateral: ₹25 lakh",
            "layer": "case",
        },
        "collateral_B": {
            "label": "Collateral: ₹25 lakh",
            "layer": "case",
        },
        "amount_A": {
            "label": "Loan requested: ₹10 lakh",
            "layer": "case",
        },
        "amount_B": {
            "label": "Loan requested: ₹10 lakh",
            "layer": "case",
        },
        "payment_A": {
            "label": "Supplier invoices paid on day 28",
            "layer": "case",
            "days_after_invoice": 28,
            "invoice_term_days": INVOICE_TERM_DAYS,
        },
        "payment_B": {
            "label": "Supplier invoices paid on day 5",
            "layer": "case",
            "days_after_invoice": 5,
            "invoice_term_days": INVOICE_TERM_DAYS,
        },
    }

    graph.add_nodes_from(
        (node, attributes)
        for node, attributes in case_nodes.items()
    )

    for app, credit, collateral, amount, payment in [
        ("app_A", "credit_A", "collateral_A", "amount_A", "payment_A"),
        ("app_B", "credit_B", "collateral_B", "amount_B", "payment_B"),
    ]:
        graph.add_edge(app, credit, relation="has_fact")
        graph.add_edge(app, collateral, relation="has_fact")
        graph.add_edge(app, amount, relation="has_fact")
        graph.add_edge(app, payment, relation="has_payment_timing")


    # 2. SHARED KNOWLEDGE LAYER: reasoning chain

    knowledge_nodes = {
        "early_payment": {
            "label": "Early payment",
            "layer": "knowledge",
        },
        "before_due": {
            "label": "Paying before due date",
            "layer": "knowledge",
        },
        "supplier_pressure": {
            "label": "Possible supplier pressure / liquidity strain",
            "layer": "knowledge",
        },
        "thin_buffer": {
            "label": "Thin cash buffer",
            "layer": "knowledge",
        },
        "repayment_risk": {
            "label": "Potential repayment risk",
            "layer": "knowledge",
        },
    }

    graph.add_nodes_from(
        (node, attributes)
        for node, attributes in knowledge_nodes.items()
    )

    # Connect observed payment patterns to the shared knowledge node.
    graph.add_edge(
        "payment_A", "early_payment", relation="observed_as"
    )
    graph.add_edge(
        "payment_B", "early_payment", relation="observed_as"
    )

    graph.add_edge("early_payment", "before_due", relation="means")
    graph.add_edge(
        "before_due",
        "supplier_pressure",
        relation="may_suggest",
    )
    graph.add_edge(
        "supplier_pressure",
        "thin_buffer",
        relation="could_reflect",
    )
    graph.add_edge(
        "thin_buffer",
        "repayment_risk",
        relation="may_increase",
    )

    # -------------------------------------------------
    # 3. CONDITIONS LAYER: counter-evidence and amplifiers
    # -------------------------------------------------
    condition_nodes = {
        "discount": {
            "label": "Discount taken deliberately",
            "layer": "condition",
            "effect": "cancels",
            "target": "supplier_pressure",
        },
        "strong_reserves": {
            "label": "Strong cash reserves",
            "layer": "condition",
            "effect": "cancels",
            "target": "thin_buffer",
        },
        "supplier_demand": {
            "label": "Supplier requires prepayment",
            "layer": "condition",
            "effect": "amplifies",
            "target": "supplier_pressure",
        },
        # Example of adding a new condition.
        "seasonal_discount": {
            "label": "Seasonal bulk-buy discount",
            "layer": "condition",
            "effect": "cancels",
            "target": "supplier_pressure",
        },
    }

    graph.add_nodes_from(
        (node, attributes)
        for node, attributes in condition_nodes.items()
    )

    for condition, attributes in condition_nodes.items():
        graph.add_edge(
            condition,
            attributes["target"],
            relation=attributes["effect"],
        )

    return graph


def get_reasoning_path(graph: nx.DiGraph) -> list[str]:
    """Return the path from early payment to potential repayment risk."""
    return nx.shortest_path(
        graph,
        source="early_payment",
        target="repayment_risk",
    )


def assess_case(
    graph: nx.DiGraph,
    app_id: str,
    conditions_present: set[str] | None = None,
) -> dict:
    """Evaluate timing, walk the reasoning path, and apply conditions."""

    if app_id not in {"app_A", "app_B"}:
        raise ValueError("app_id must be 'app_A' or 'app_B'")

    conditions_present = conditions_present or set()

    payment_id = (
        "payment_A" if app_id == "app_A" else "payment_B"
    )
    payment = graph.nodes[payment_id]

    days_after_invoice = payment["days_after_invoice"]
    term_days = payment["invoice_term_days"]
    days_before_due = term_days - days_after_invoice

    is_early = (
        days_before_due >= EARLY_PAYMENT_THRESHOLD_DAYS
    )

    timing_check = (
        f"{days_after_invoice} days after invoice; "
        f"{days_before_due} days before due date. "
        f"Threshold: {EARLY_PAYMENT_THRESHOLD_DAYS} days."
    )

    # Application A's payment timing was checked, not skipped.
    if not is_early:
        return {
            "scenario": f"{app_id.replace('_', ' ').title()} (baseline)",
            "application": graph.nodes[app_id]["label"],
            "timing_check": timing_check,
            "assessment": "No early-payment warning from this signal",
            "decision": "Continue normal underwriting checks",
            "path": [],
            "conditions": [],
            "explanation": (
                "Payment timing was evaluated and did not meet "
                "the illustrative early-payment threshold."
            ),
        }

    path = get_reasoning_path(graph)
    cancelled_nodes = set()
    active_conditions = []
    amplified = False

    # Read the actual condition edges from the graph.
    for condition in conditions_present:
        if (
            condition not in graph
            or graph.nodes[condition].get("layer") != "condition"
        ):
            raise ValueError(f"Unknown condition node: {condition}")

        attributes = graph.nodes[condition]
        target = attributes["target"]
        relation = graph.edges[condition, target]["relation"]

        active_conditions.append(
            (attributes["label"], relation)
        )

        if relation == "cancels":
            cancelled_nodes.add(target)
        elif relation == "amplifies":
            amplified = True

    # Propagate cancellations to downstream risk nodes.
    # Cancelling supplier_pressure interrupts the downstream chain.
    if "supplier_pressure" in cancelled_nodes:
        cancelled_nodes.update(
            {"thin_buffer", "repayment_risk"}
        )

    if "thin_buffer" in cancelled_nodes:
        cancelled_nodes.add("repayment_risk")

    # Walk the path and stop at the first cancelled node.
    visible_path = []

    for node in path:
        if node in cancelled_nodes:
            break
        visible_path.append(node)

    if "repayment_risk" in cancelled_nodes:
        assessment = "Signal substantially mitigated"
        decision = (
            "Verify mitigating evidence; do not escalate "
            "on timing alone"
        )
        explanation = (
            "The path stops before a cancelled node because "
            "the evidence interrupts this particular hypothesis. "
            "This does not prove that the applicant is risk-free."
        )
    else:
        assessment = (
            "Elevated review priority"
            if amplified
            else "Needs review"
        )
        decision = (
            "Request evidence and manually review before deciding"
        )
        explanation = (
            "Early supplier payment may have a benign explanation "
            "or reflect liquidity pressure. This is a hypothesis, "
            "not proof of default."
        )

    scenario_names = {
        frozenset(): "Application B (baseline)",
        frozenset({"discount", "strong_reserves"}):
            "B + discount and strong-reserves evidence",
        frozenset({"supplier_demand"}):
            "B + supplier-required prepayment",
        frozenset({"seasonal_discount"}):
            "B + seasonal bulk-buy discount",
    }

    scenario = scenario_names.get(
        frozenset(conditions_present),
        f"{graph.nodes[app_id]['label']} (conditional scenario)",
    )

    return {
        "scenario": scenario,
        "application": graph.nodes[app_id]["label"],
        "timing_check": timing_check,
        "assessment": assessment,
        "decision": decision,
        "path": visible_path,
        "conditions": active_conditions,
        "explanation": explanation,
    }


def print_assessment(
    graph: nx.DiGraph,
    result: dict,
) -> None:
    print(f"\n=== {result['scenario']} ===")
    print(f"  Timing check: {result['timing_check']}")
    print(f"  Assessment: {result['assessment']}")
    print(f"  Recommendation: {result['decision']}")

    if result["path"]:
        print("  Walked reasoning path:")

        for index, node in enumerate(result["path"]):
            print(f"    {index + 1}. {graph.nodes[node]['label']}")

            if index < len(result["path"]) - 1:
                next_node = result["path"][index + 1]
                relation = graph.edges[node, next_node]["relation"]
                print(f"       --{relation}-->")
    else:
        print(
            "  Walked reasoning path: not activated; "
            "payment timing did not cross the threshold."
        )

    if result["conditions"]:
        print("  Conditions applied:")
        for label, relation in result["conditions"]:
            print(f"    - {label} [{relation}]")

    print(f"  Explanation: {result['explanation']}")


def main() -> None:
    graph = build_graph()

    print(
        f"Knowledge graph: {graph.number_of_nodes()} nodes, "
        f"{graph.number_of_edges()} edges"
    )

    print("Layer counts:")
    for layer in ("case", "knowledge", "condition"):
        count = sum(
            1
            for _, attributes in graph.nodes(data=True)
            if attributes.get("layer") == layer
        )
        print(f"  {layer}: {count} nodes")

    scenarios = [
        assess_case(graph, "app_A"),
        assess_case(graph, "app_B"),
        assess_case(
            graph,
            "app_B",
            {"discount", "strong_reserves"},
        ),
        assess_case(
            graph,
            "app_B",
            {"supplier_demand"},
        ),
        assess_case(
            graph,
            "app_B",
            {"seasonal_discount"},
        ),
    ]

    for result in scenarios:
        print_assessment(graph, result)


if __name__ == "__main__":
    main()
