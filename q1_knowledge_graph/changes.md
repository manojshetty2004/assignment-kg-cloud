# Knowledge Graph Visualization – Changes Made

1. Added `visualization.py` to generate a visual representation of the existing loan reasoning knowledge graph.
2. The visualization displays Application A and Application B, their relevant facts, and the reasoning path leading to repayment risk.
3. Mitigating and amplifying conditions are visually distinguished to make their effects easier to understand.
4. The graph is generated using the existing `build_graph()` function, preserving the original graph structure and reasoning logic.
5. Install the required dependencies using `pip install -r requirements.txt`.
6. Run `python visualization.py` to generate the PNG image at `output/knowledge_graph.png`.