# Question 1 — Three-layer loan reasoning graph

## Run on Windows / VS Code
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python loan_reasoning_graph.py
```

## Layers
- **Case:** application facts and invoice-payment timing.
- **Knowledge:** Early payment → Paying before due → Possible supplier pressure / liquidity strain → Thin cash buffer → Repayment risk.
- **Conditions:** evidence that `cancels` or `amplifies` parts of the hypothesis.

The recommendation is computed by traversing the chain and applying only the conditions supplied to `assess_case`. It does not use a fixed arrow from an application to a decision. This is a toy, explainable reasoning example, not a validated credit model.
