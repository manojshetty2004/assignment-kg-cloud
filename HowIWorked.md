# How I worked

## 1. AI tools I used, and for what

- **Claude:** to understand the assignment, to talk through the loan reasoning, to review my drafts the way a reviewer would, to explain Part A and the GPU maths, and to help draft the notes and README.
- **Codex:** to generate a first draft of the Q2 files (Part A, Part B and the Part C templates).
- I built and ran the Q1 knowledge graph code myself and checked each output. I read through the AI-drafted Q2 text and edited it so that I can explain it.

### Times I did not accept what the AI suggested

1. **Codex tried to run the whole app.** It tried to launch Docker, Postgres and the GPU model, and reported that it could not. The assignment only asks for written files, so I told it to stop and only check the syntax of the compose file and the backup script. I have said in the README that Part C was not run.
2. **Codex left the GPU price as "TODO" and picked the hybrid option.** I did not accept this. The hybrid keeps the AI dependent on the office, and Part A showed that the office was the unreliable part. I looked up a real GPU price and redid the cost comparison. I chose a rented GPU that runs only during working hours.
3. **I did not add numeric strengths to the edges in the Q1 graph.** The AI suggested low/medium/high labels. I left them out because I have no real data, and made-up numbers would look precise without being true. The Q1 note says this.
4. **My first Q1 diagram was too much like a fact graph.** It had one rule and fixed approve/reject arrows. I rebuilt it with a shared reasoning chain, conditions that can cancel or increase the risk, and a "needs review" result instead of a fixed reject.

## 2. How my work progressed

- **18 October:** I read the assignment and decided to start with Q1 and design it on paper before writing any code. I chose my small detail: Application B pays its suppliers on day 5, while Application A pays on day 28.
- **18 October:** My first diagram stored facts and had a single rule. I got feedback that it showed only one hop and had no conditions, so I rebuilt it as three layers: case facts, a shared knowledge chain, and conditions.
- **18 October:** My first working code printed one path, with unlabelled scenarios, and skipped Application A without explanation. I fixed this by labelling every scenario, adding an explicit timing check with an illustrative 10-day threshold, and adding a live test (a seasonal bulk-buy discount) to show that new evidence can be added without changing the code.
- **18 October:** I wrote the Q1 note and README, and hand-drew the graph.
- **18 October:** For Q2, Codex could not launch the app, so I redirected it to only write the files. I reviewed Part A, added the timeline and the observation that port 443 still works, and found that Part B had an unpriced GPU, so I looked up a real price and redid the budget.
- **19 October:** I drew the cloud diagram by hand, cleaned up the Q2 files, checked every price link, and submitted.

What did not work the first time: the first diagram, the unlabelled output, the unpriced GPU option, and the attempt to run Docker.

## 3. Facts graph vs reasoning graph, in one sentence

A graph that stores facts records what is true, while a graph that stores reasoning also records why a fact matters and when it does not, so it can explain a conclusion and change it when new evidence arrives.