# Wumpus World Logic Agent

AI 2002 – Assignment 6, Question 6

## What it does

A web-based Knowledge-Based Agent that navigates a Wumpus World grid using Propositional Logic and Resolution Refutation to infer which cells are safe before moving.

## Run

```bash
pip install flask
python app.py
```

Open http://localhost:5000

## How it works

1. **World** — Grid with randomly placed pits and one Wumpus. Agent starts at (0,0).
2. **Percepts** — Breeze means a pit is adjacent. Stench means Wumpus is adjacent.
3. **KB** — Each visited cell's percepts add CNF clauses to the knowledge base.
4. **Inference** — Resolution Refutation proves NOT_PIT and NOT_WUMPUS for each unvisited cell. If both are proven, the cell is marked Safe (green).
5. **UI** — Click adjacent cells to move. Green = safe, gray = unknown, red/purple = hazard (shown on game over).

## Files

```
app.py              All backend logic (Flask + AI)
templates/index.html   Web UI
generate_docs.py    PDF documentation generator
```
