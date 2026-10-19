"""Render the loan reasoning graph as a frontend-friendly PNG.

Run from this directory: python visualization.py
Output: output/knowledge_graph.png
"""
from __future__ import annotations

from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import networkx as nx

from loan_reasoning_graph import build_graph, assess_case

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "output" / "knowledge_graph.png"


def wrap(label: str, width: int = 23) -> str:
    return "\n".join(textwrap.wrap(label, width=width, break_long_words=False))


def draw_box(ax, x, y, w, h, label, *, face, edge, fontsize=9, weight="normal", radius=0.025):
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle=f"round,pad=0.012,rounding_size={radius}",
        linewidth=1.5, edgecolor=edge, facecolor=face, zorder=3,
    )
    ax.add_patch(patch)
    ax.text(x, y, label, ha="center", va="center", fontsize=fontsize,
            fontweight=weight, color="#172033", zorder=4, linespacing=1.15)
    return patch


def arrow(ax, start, end, label, *, color="#64748b", style="solid", rad=0.0, label_offset=(0, 0)):
    patch = FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=13, linewidth=1.35,
        color=color, linestyle=style, connectionstyle=f"arc3,rad={rad}",
        shrinkA=3, shrinkB=3, zorder=2,
    )
    ax.add_patch(patch)
    mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
    ax.text(mx + label_offset[0], my + label_offset[1], label, fontsize=7.5,
            ha="center", va="center", color=color,
            bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "none", "alpha": 0.92}, zorder=5)


def main() -> None:
    graph = build_graph()
    # Coordinates group graph nodes by their source-defined layer. All labels,
    # relationships, and condition targets are read from build_graph().
    pos = {
        "app_A": (0.8, 7.0), "credit_A": (2.5, 8.1), "collateral_A": (2.5, 7.45),
        "amount_A": (2.5, 6.8), "payment_A": (2.5, 6.15),
        "app_B": (0.8, 3.8), "credit_B": (2.5, 4.9), "collateral_B": (2.5, 4.25),
        "amount_B": (2.5, 3.6), "payment_B": (2.5, 2.95),
        "early_payment": (5.1, 2.95), "before_due": (7.25, 2.95),
        "supplier_pressure": (9.45, 2.95), "thin_buffer": (11.7, 2.95),
        "repayment_risk": (13.85, 2.95),
        "discount": (7.5, 6.35), "seasonal_bulk_discount": (9.75, 6.35),
        "strong_reserves": (12.0, 6.35), "supplier_demand": (13.6, 5.0),
    }

    fig, ax = plt.subplots(figsize=(19, 10.5), dpi=180)
    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#f8fafc")
    ax.set_xlim(-0.25, 15.0)
    ax.set_ylim(-0.05, 9.2)
    ax.axis("off")

    ax.text(0.0, 8.95, "Loan Application Reasoning Graph", fontsize=22, fontweight="bold", color="#0f172a")
    ax.text(0.0, 8.58, "Observed facts → cautious hypothesis chain → evidence that mitigates or amplifies risk",
            fontsize=11, color="#475569")

    # Layer headers / subtle backgrounds
    ax.add_patch(FancyBboxPatch((0.0, 2.0), 3.65, 6.2, boxstyle="round,pad=0.03,rounding_size=0.12",
                                facecolor="#eff6ff", edgecolor="#bfdbfe", linewidth=1.0, zorder=0))
    ax.add_patch(FancyBboxPatch((4.0, 2.15), 10.15, 1.6, boxstyle="round,pad=0.03,rounding_size=0.12",
                                facecolor="#f1f5f9", edgecolor="#cbd5e1", linewidth=1.0, zorder=0))
    ax.add_patch(FancyBboxPatch((6.35, 5.75), 6.9, 1.25, boxstyle="round,pad=0.03,rounding_size=0.12",
                                facecolor="#f0fdf4", edgecolor="#bbf7d0", linewidth=1.0, zorder=0))
    ax.text(0.2, 8.0, "CASE LAYER", fontsize=9, fontweight="bold", color="#1d4ed8")
    ax.text(4.2, 3.5, "SHARED KNOWLEDGE LAYER", fontsize=9, fontweight="bold", color="#334155")
    ax.text(6.55, 6.82, "CONDITIONS LAYER", fontsize=9, fontweight="bold", color="#15803d")

    # Edges are drawn from the graph itself. Case fact edges are intentionally subtle.
    for u, v, attrs in graph.edges(data=True):
        if u not in pos or v not in pos:
            continue
        relation = attrs.get("relation", "")
        if relation in {"has_fact", "has_payment_timing"}:
            arrow(ax, pos[u], pos[v], "", color="#94a3b8", rad=0.0)
        elif relation in {"cancels", "amplifies"}:
            color = "#15803d" if relation == "cancels" else "#dc2626"
            style = "dashed"
            # Conditions are routed from their displayed boxes to their graph targets.
            curve = 0.0 if u != "supplier_demand" else -0.18
            arrow(ax, pos[u], pos[v], relation, color=color, style=style, rad=curve,
                  label_offset=(0.0, 0.3 if relation == "cancels" else -0.35))
        else:
            arrow(ax, pos[u], pos[v], relation, color="#475569", label_offset=(0, 0.38))

    # Render graph nodes using source labels and layer/kind metadata.
    for node, attrs in graph.nodes(data=True):
        if node not in pos:
            continue
        x, y = pos[node]
        layer, kind = attrs.get("layer"), attrs.get("kind")
        label = wrap(attrs.get("label", node), 23 if layer != "case" else 22)
        if layer == "case" and kind == "Application":
            draw_box(ax, x, y, 1.35, 0.48, label, face="#dbeafe", edge="#2563eb", fontsize=10, weight="bold")
        elif layer == "case":
            draw_box(ax, x, y, 1.75, 0.48, label, face="#ffffff", edge="#93c5fd", fontsize=7.8)
        elif layer == "knowledge":
            if kind == "Risk":
                face, edge = "#fee2e2", "#dc2626"
            elif kind == "Hypothesis":
                face, edge = "#fef3c7", "#d97706"
            else:
                face, edge = "#e2e8f0", "#64748b"
            draw_box(ax, x, y, 1.72 if node != "supplier_pressure" else 2.0, 0.72, label, face=face, edge=edge, fontsize=8.3, weight="medium")
        else:
            is_amp = attrs.get("effect") == "amplifies"
            draw_box(ax, x, y, 1.75 if node != "seasonal_bulk_discount" else 2.0, 0.58, label,
                     face="#fee2e2" if is_amp else "#dcfce7",
                     edge="#dc2626" if is_amp else "#16a34a", fontsize=8.1, weight="medium")

    # Scenario strip is calculated with the same assessment logic as the CLI.
    scenarios = [
        ("Application A", assess_case(graph, "app_A"), 0.2, 1.25, 3.3),
        ("Application B", assess_case(graph, "app_B"), 3.9, 1.25, 3.3),
        ("B + seasonal discount + reserves", assess_case(graph, "app_B", {"seasonal_bulk_discount", "strong_reserves"}), 7.6, 1.25, 3.5),
        ("B + supplier prepayment demand", assess_case(graph, "app_B", {"supplier_demand"}), 11.5, 1.25, 3.4),
    ]
    for title, result, x, y, width in scenarios:
        level = result["level"]
        is_mitigated = "mitigated" in level.lower() or "no warning" in level.lower()
        is_elevated = "Elevated" in level
        edge = "#16a34a" if is_mitigated else ("#dc2626" if is_elevated else "#d97706")
        face = "#f0fdf4" if is_mitigated else ("#fff1f2" if is_elevated else "#fffbeb")
        ax.add_patch(FancyBboxPatch((x, y - 0.42), width, 0.9, boxstyle="round,pad=0.03,rounding_size=0.08",
                                    facecolor=face, edgecolor=edge, linewidth=1.3, zorder=1))
        ax.text(x + 0.12, y + 0.23, title, fontsize=8.2, fontweight="bold", color="#172033", zorder=3)
        ax.text(x + 0.12, y - 0.08, level, fontsize=7.7, color=edge, zorder=3)

    ax.text(0.15, 0.28, "Green dashed edges = mitigating evidence (cancels)     Red dashed edges = amplifying evidence",
            fontsize=8.5, color="#475569")
    ax.text(14.7, 0.28, "Illustrative example — not a validated credit model", fontsize=8, color="#64748b", ha="right")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Saved graph image: {OUTPUT_PATH}")
    print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")


if __name__ == "__main__":
    main()
