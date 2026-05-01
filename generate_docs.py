from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT = "/mnt/user-data/outputs/Wumpus_World_Documentation.pdf"

doc = SimpleDocTemplate(OUTPUT, pagesize=letter,
    leftMargin=inch, rightMargin=inch, topMargin=inch, bottomMargin=inch)

styles = getSampleStyleSheet()

title_style = ParagraphStyle("Title2", parent=styles["Title"],
    fontSize=22, textColor=colors.HexColor("#1a202c"), spaceAfter=6, alignment=TA_CENTER)

subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"],
    fontSize=12, textColor=colors.HexColor("#4a5568"), spaceAfter=20, alignment=TA_CENTER)

h1_style = ParagraphStyle("H1", parent=styles["Heading1"],
    fontSize=15, textColor=colors.HexColor("#2b6cb0"), spaceBefore=18, spaceAfter=8,
    borderPad=4)

h2_style = ParagraphStyle("H2", parent=styles["Heading2"],
    fontSize=12, textColor=colors.HexColor("#2d3748"), spaceBefore=12, spaceAfter=6)

body_style = ParagraphStyle("Body2", parent=styles["Normal"],
    fontSize=10, textColor=colors.HexColor("#2d3748"), leading=16, spaceAfter=6)

code_style = ParagraphStyle("Code", parent=styles["Code"],
    fontSize=9, textColor=colors.HexColor("#1a202c"), backColor=colors.HexColor("#f7fafc"),
    borderColor=colors.HexColor("#e2e8f0"), borderWidth=1, borderPad=6,
    leading=14, spaceAfter=8, fontName="Courier")

bullet_style = ParagraphStyle("Bullet", parent=body_style,
    leftIndent=20, bulletIndent=10, spaceAfter=4)


def h1(text): return Paragraph(text, h1_style)
def h2(text): return Paragraph(text, h2_style)
def body(text): return Paragraph(text, body_style)
def code(text): return Paragraph(text.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)
def bullet(text): return Paragraph(f"&bull; &nbsp; {text}", bullet_style)
def space(n=8): return Spacer(1, n)
def rule(): return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=10)


story = []

story += [
    Paragraph("Wumpus World Logic Agent", title_style),
    Paragraph("AI 2002 – Assignment 6, Question 6 | Complete Documentation", subtitle_style),
    rule(),
    space(10),
]

story += [
    h1("1. Project Overview"),
    body("This project implements a Knowledge-Based Agent that navigates a Wumpus World grid using Propositional Logic and the Resolution Refutation algorithm. The agent perceives its environment, builds a logical knowledge base, and infers which unexplored cells are safe before moving."),
    space(),
    body("The application is a web-based tool built with Python (Flask) on the backend and plain HTML/CSS/JavaScript on the frontend. No external JS frameworks are used."),
    space(16),
]

story += [
    h1("2. Architecture"),
    h2("2.1 Backend — app.py (Flask)"),
    body("The backend contains all AI logic and exposes three HTTP endpoints:"),
    space(4),
    bullet("<b>GET /</b> — Serves the main HTML page."),
    bullet("<b>POST /new_game</b> — Creates a new grid, randomly places pits and the Wumpus, places the agent at (0,0), and returns the initial game state."),
    bullet("<b>POST /move</b> — Moves the agent to an adjacent cell, updates the KB, runs inference, and returns the updated state."),
    space(10),

    h2("2.2 Frontend — templates/index.html"),
    body("A single-page application that renders the grid, displays percepts, shows inference metrics, and allows the user to click cells to move the agent."),
    space(16),
]

story += [
    h1("3. Core Algorithms"),

    h2("3.1 World Generation"),
    body("When a new game starts, pits are randomly placed in approximately 1/5 of all cells (excluding the start cell (0,0)). The Wumpus is placed randomly in a remaining non-pit cell."),
    space(4),
    code("num_pits = max(1, (rows * cols) // 5)\npits = random.sample(cells, num_pits)\nwumpus = random.choice(remaining_cells)"),
    space(8),

    h2("3.2 Percept Generation"),
    body("When the agent enters a cell, it receives:"),
    bullet("<b>Breeze</b> — if any directly adjacent cell contains a pit."),
    bullet("<b>Stench</b> — if any directly adjacent cell contains the Wumpus."),
    space(4),
    code("breeze = any(n in pits for n in neighbors)\nstench = wumpus in neighbors"),
    space(8),

    h2("3.3 Knowledge Base Construction"),
    body("The KB is built fresh on every move from all visited cell percepts. Each visited cell contributes clauses:"),
    space(4),
    body("<b>No Breeze at (r,c):</b> Every neighbor cannot be a pit."),
    code("if not breeze:\n    for each neighbor (nr,nc):\n        add clause: [NOT_PIT_nr_nc]"),
    space(4),
    body("<b>Breeze at (r,c):</b> At least one neighbor is a pit."),
    code("if breeze:\n    add clause: [PIT_n1, PIT_n2, ...]  (disjunction of all neighbors)"),
    space(4),
    body("The same logic applies symmetrically for Stench and Wumpus clauses."),
    space(8),

    h2("3.4 Propositional Resolution"),
    body("The resolution rule: given two clauses C1 and C2 where C1 contains literal L and C2 contains its complement NOT_L, produce the resolvent by combining both clauses minus the complementary pair."),
    space(4),
    code("def resolve(c1, c2):\n    for lit in c1:\n        neg = complement(lit)\n        if neg in c2:\n            return (c1 - {lit}) union (c2 - {neg})"),
    space(8),

    h2("3.5 Resolution Refutation (Safety Check)"),
    body("To prove a cell is safe (e.g., NOT_PIT_2_3), the agent uses proof by contradiction:"),
    space(4),
    bullet("1. Take all KB clauses."),
    bullet("2. Add the negation of the goal: if proving NOT_PIT_2_3, add clause {PIT_2_3}."),
    bullet("3. Repeatedly apply the resolution rule to all clause pairs."),
    bullet("4. If the empty clause (contradiction) is derived, the goal is proven TRUE."),
    bullet("5. If no new clauses can be produced, the goal is UNKNOWN."),
    space(4),
    code("def resolution_refutation(clauses, goal):\n    negated_goal = complement(goal)\n    all_clauses = clauses + [{negated_goal}]\n    loop:\n        try all clause pairs\n        if empty clause derived: return True\n        if no new clauses: return False"),
    space(4),
    body("A cell is marked SAFE (green) only when BOTH NOT_PIT and NOT_WUMPUS are proven for it."),
    space(16),
]

story += [
    h1("4. CNF Representation"),
    body("All KB clauses are already in Conjunctive Normal Form (CNF) by construction:"),
    bullet("Each clause is a Python list of literal strings (e.g., ['NOT_PIT_1_2', 'NOT_PIT_2_1'])."),
    bullet("The full KB is the conjunction (AND) of all clauses."),
    bullet("Literals use the naming convention: PIT_r_c, NOT_PIT_r_c, WUMPUS_r_c, NOT_WUMPUS_r_c."),
    space(4),
    body("Example KB after visiting (0,0) with Breeze=False, Stench=False on a 4x4 grid:"),
    code("Clause 1: [NOT_PIT_1_0]    (no breeze -> right neighbor not a pit)\nClause 2: [NOT_PIT_0_1]    (no breeze -> down neighbor not a pit)\nClause 3: [NOT_WUMPUS_1_0] (no stench -> right neighbor not wumpus)\nClause 4: [NOT_WUMPUS_0_1] (no stench -> down neighbor not wumpus)"),
    space(16),
]

story += [
    h1("5. Web Interface"),
    h2("5.1 Grid Display"),
    body("Each cell is color-coded based on its current status:"),
    space(4),
]

color_table_data = [
    ["Color", "Meaning"],
    ["Blue (dark)", "Agent's current position"],
    ["Green", "Inferred safe by resolution engine"],
    ["Blue (medium)", "Visited — percepts known"],
    ["Gray", "Unvisited — unknown status"],
    ["Red", "Pit (revealed on game over)"],
    ["Purple", "Wumpus (revealed on game over)"],
]

color_table = Table(color_table_data, colWidths=[2.5*inch, 4*inch])
color_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2b6cb0")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7fafc")]),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ("LEFTPADDING", (0,0), (-1,-1), 8),
    ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
]))

story += [color_table, space(10)]

story += [
    h2("5.2 Real-Time Metrics Dashboard"),
    bullet("<b>Inference Steps</b> — cumulative count of clause pair evaluations by the resolution algorithm."),
    bullet("<b>Cells Visited</b> — number of cells the agent has entered."),
    bullet("<b>Safe Cells Found</b> — number of unvisited cells proven safe by resolution."),
    bullet("<b>Current Percepts</b> — Breeze and/or Stench badges for the agent's current cell."),
    space(16),
]

story += [
    h1("6. File Structure"),
    code("wumpus/\n  app.py              Flask backend + all AI logic\n  templates/\n    index.html        Web UI (single file)\n  generate_docs.py    This documentation generator\n  README.md           Quick start guide"),
    space(16),
]

story += [
    h1("7. How to Run"),
    code("pip install flask\npython app.py"),
    body("Then open <b>http://localhost:5000</b> in a browser."),
    space(8),
    body("Grid size can be set between 2x2 and 8x8. Larger grids increase the number of inference steps required. The agent always starts at cell (0,0) in the bottom-left."),
    space(16),
]

story += [
    h1("8. Limitations and Design Choices"),
    bullet("The KB is rebuilt from scratch on each move for simplicity. A production system would maintain incremental updates."),
    bullet("Resolution is capped at 500 iterations per cell pair to prevent infinite loops on unsolvable configurations."),
    bullet("The agent is controlled manually (click to move). An autonomous agent extension would use the safe cell list to choose moves automatically."),
    bullet("Game state is stored in a server-side global dictionary — suitable for single-user demonstration only."),
    space(16),
]

story += [
    h1("9. Example Inference Trace"),
    body("Agent at (0,0), no breeze, no stench. KB receives 4 unit clauses:"),
    code("NOT_PIT_1_0,  NOT_PIT_0_1\nNOT_WUMPUS_1_0, NOT_WUMPUS_0_1"),
    space(4),
    body("To prove NOT_PIT_1_0: Negated goal adds clause {PIT_1_0}."),
    code("Clause A: [NOT_PIT_1_0]\nClause B: [PIT_1_0]  <- negated goal\nResolve A + B on PIT_1_0 / NOT_PIT_1_0 -> empty clause (contradiction)\nConclusion: NOT_PIT_1_0 is TRUE  =>  cell (1,0) is safe from pits."),
    space(16),
]

story += [
    rule(),
    Paragraph("AI 2002 – Assignment 6 | Wumpus World Logic Agent", subtitle_style),
]

doc.build(story)
print("PDF generated:", OUTPUT)
