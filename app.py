from flask import Flask, jsonify, request, render_template
import random

app = Flask(__name__)


def get_adjacent(r, c, rows, cols):
    neighbors = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < rows and 0 <= nc < cols:
            neighbors.append((nr, nc))
    return neighbors


def generate_world(rows, cols):
    cells = [(r, c) for r in range(rows) for c in range(cols)]
    cells.remove((0, 0))

    num_pits = max(1, (rows * cols) // 5)
    pits = random.sample(cells, min(num_pits, len(cells)))

    remaining = [c for c in cells if c not in pits]
    wumpus = random.choice(remaining) if remaining else None

    return pits, wumpus


def get_percepts(position, pits, wumpus, rows, cols):
    r, c = position
    neighbors = get_adjacent(r, c, rows, cols)
    breeze = any(n in pits for n in neighbors)
    stench = wumpus in neighbors if wumpus else False
    return breeze, stench


def build_kb(visited_percepts, rows, cols):
    clauses = []
    for (r, c), (breeze, stench) in visited_percepts.items():
        neighbors = get_adjacent(r, c, rows, cols)

        if not breeze:
            for (nr, nc) in neighbors:
                clauses.append([f"NOT_PIT_{nr}_{nc}"])
        else:
            clauses.append([f"PIT_{nr}_{nc}" for (nr, nc) in neighbors])

        if not stench:
            for (nr, nc) in neighbors:
                clauses.append([f"NOT_WUMPUS_{nr}_{nc}"])
        else:
            clauses.append([f"WUMPUS_{nr}_{nc}" for (nr, nc) in neighbors])

    return clauses


def resolve(c1, c2):
    for lit in c1:
        neg = lit[4:] if lit.startswith("NOT_") else "NOT_" + lit
        if neg in c2:
            new_clause = [l for l in c1 if l != lit] + [l for l in c2 if l != neg]
            return list(dict.fromkeys(new_clause))
    return None


def resolution_refutation(clauses, goal_literal):
    negated_goal = goal_literal[4:] if goal_literal.startswith("NOT_") else "NOT_" + goal_literal
    all_clauses = [list(c) for c in clauses] + [[negated_goal]]

    seen = set(frozenset(c) for c in all_clauses)
    steps = 0

    for _ in range(500):
        new_clauses = []
        n = len(all_clauses)
        for i in range(n):
            for j in range(i+1, n):
                resolvent = resolve(all_clauses[i], all_clauses[j])
                steps += 1
                if resolvent is None:
                    continue
                if len(resolvent) == 0:
                    return True, steps
                key = frozenset(resolvent)
                if key not in seen:
                    seen.add(key)
                    new_clauses.append(resolvent)
        if not new_clauses:
            return False, steps
        all_clauses.extend(new_clauses)

    return False, steps


def infer_safe_cells(visited_percepts, rows, cols):
    clauses = build_kb(visited_percepts, rows, cols)
    safe = {}
    total_steps = 0

    for r in range(rows):
        for c in range(cols):
            if (r, c) in visited_percepts:
                continue
            pit_safe, s1 = resolution_refutation(clauses, f"NOT_PIT_{r}_{c}")
            wumpus_safe, s2 = resolution_refutation(clauses, f"NOT_WUMPUS_{r}_{c}")
            total_steps += s1 + s2
            safe[(r, c)] = pit_safe and wumpus_safe

    return safe, total_steps


game_state = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/new_game", methods=["POST"])
def new_game():
    data = request.json
    rows = max(2, min(int(data.get("rows", 4)), 8))
    cols = max(2, min(int(data.get("cols", 4)), 8))

    pits, wumpus = generate_world(rows, cols)

    game_state.clear()
    game_state.update({
        "rows": rows,
        "cols": cols,
        "pits": pits,
        "wumpus": wumpus,
        "agent": (0, 0),
        "visited": {},
        "inference_steps": 0,
        "game_over": False,
        "message": "Game started. Agent at (0,0)."
    })

    breeze, stench = get_percepts((0,0), pits, wumpus, rows, cols)
    game_state["visited"][(0, 0)] = (breeze, stench)

    return jsonify(build_response())


@app.route("/move", methods=["POST"])
def move():
    if game_state.get("game_over"):
        return jsonify(build_response())

    data = request.json
    r, c = data["row"], data["col"]
    rows, cols = game_state["rows"], game_state["cols"]
    ar, ac = game_state["agent"]

    if abs(r - ar) + abs(c - ac) != 1:
        game_state["message"] = "Invalid move: must move to adjacent cell."
        return jsonify(build_response())

    game_state["agent"] = (r, c)

    pits = game_state["pits"]
    wumpus = game_state["wumpus"]

    if (r, c) in pits:
        game_state["game_over"] = True
        game_state["message"] = f"Agent fell into a pit at ({r},{c})! Game over."
    elif (r, c) == wumpus:
        game_state["game_over"] = True
        game_state["message"] = f"Agent eaten by Wumpus at ({r},{c})! Game over."
    else:
        breeze, stench = get_percepts((r, c), pits, wumpus, rows, cols)
        game_state["visited"][(r, c)] = (breeze, stench)
        percept_str = []
        if breeze: percept_str.append("Breeze")
        if stench: percept_str.append("Stench")
        game_state["message"] = f"Moved to ({r},{c}). Percepts: {', '.join(percept_str) or 'None'}"

    visited_str_keys = {str(k): v for k, v in game_state["visited"].items()}
    safe_map, steps = infer_safe_cells(game_state["visited"], rows, cols)
    game_state["inference_steps"] += steps

    return jsonify(build_response(safe_map))


def build_response(safe_map=None):
    rows, cols = game_state["rows"], game_state["cols"]
    pits = game_state["pits"]
    wumpus = game_state["wumpus"]
    visited = game_state["visited"]
    agent = game_state["agent"]
    game_over = game_state.get("game_over", False)

    if safe_map is None:
        safe_map, _ = infer_safe_cells(visited, rows, cols)

    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            cell = {
                "row": r, "col": c,
                "agent": agent == (r, c),
                "visited": (r, c) in visited,
                "safe": safe_map.get((r, c), False),
                "percepts": {},
                "hazard": None
            }
            if (r, c) in visited:
                b, s = visited[(r, c)]
                cell["percepts"] = {"breeze": b, "stench": s}

            if game_over:
                if (r, c) in pits:
                    cell["hazard"] = "pit"
                elif (r, c) == wumpus:
                    cell["hazard"] = "wumpus"

            row.append(cell)
        grid.append(row)

    ar, ac = agent
    current_percepts = visited.get((ar, ac), (False, False))

    return {
        "grid": grid,
        "rows": rows,
        "cols": cols,
        "agent": {"row": ar, "col": ac},
        "inference_steps": game_state["inference_steps"],
        "current_percepts": {"breeze": current_percepts[0], "stench": current_percepts[1]},
        "message": game_state.get("message", ""),
        "game_over": game_over
    }


if __name__ == "__main__":
    app.run(debug=True, port=5000)
