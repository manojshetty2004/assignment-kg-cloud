# Internship Assignment: AI Knowledge Graph & Cloud Engineering

Submitted for the deadline of Monday, 19 October 2026.

## What is in this repo

```
.
├── README.md                  this file
├── HOW_I_WORKED.md            AI tools used, dated progress, one rejected-AI example
├── q1_knowledge_graph/
│   ├── README.md              how to run Q1 in detail
│   ├── loan_reasoning_graph.py
│   ├── NOTE.md                half-page note: why I modelled it this way, what I left out
│   └── graph_sketch.jpg       photo of my hand-drawn graph
└── q2_cloud/
    ├── part_a.md              the broken padlock: cause, fix, prevention, worries
    ├── part_b.md              cloud plan: options, GPU maths, costs, safety, move
    ├── diagram.jpg            photo of my hand-drawn setup
    └── part_c/                optional: docker-compose.yml, Caddyfile, .env.example, backup.sh
```

## Question 1: Knowledge Graph (short version)

Two loan applications look the same on paper (credit score 720 vs 710, same collateral, same amount). The one difference is that Application B pays its suppliers on day 5 instead of day 28. A beginner reads that as responsible. An experienced officer asks why the business is paying so early.

The graph has three layers:
1. **Case facts:** what the form says.
2. **Shared knowledge:** the officer's hidden reasoning: early payment → paying before the due date → possible supplier pressure / liquidity strain → thin cash buffer → potential repayment risk.
3. **Conditions:** evidence that cancels the worry (a deliberate discount, strong cash reserves, a seasonal bulk-buy discount) or increases it (supplier requires prepayment).

The program walks the chain for each application and prints the path and a recommendation. It gives "needs review", not "reject", because this is a weak signal that should lead to a question, not a verdict.

**To run it:**
```bash
cd q1_knowledge_graph
python loan_reasoning_graph.py
```
Needs Python 3.10 or later. See `q1_knowledge_graph/README.md` for details.

## Question 2: Cloud (short version)

- **Part A:** after the router was replaced in September, port 80 stopped reaching Caddy and the router's own admin page answered instead. Certificate renewal failed, and the certificate expired on 12 October.
- **Part B:** I chose a small cloud server for the website, API, database and worker, plus a rented 24 GB GPU that runs only during working hours. The total is about Rs. 21,500 a month, under the Rs. 25,000 budget. The office GPU stays as an emergency fallback.
- **Part C (optional):** a docker-compose file, a Caddyfile and a backup script.

## Honest notes

- **Part C was not run.** I did not have Docker, an NVIDIA GPU or the app's images on my machine. I only checked the syntax of the files. The image names in `.env.example` are placeholders.
- **Prices in Part B** were checked on the dates written next to each one. Cloud prices change, so please re-check them.
- **I used AI tools** and describe how in `HOW_I_WORKED.md`. I can explain everything in this repo in my own words.