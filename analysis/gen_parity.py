import json, math, random
from sp import dijkstra_trace, bellman_ford_trace
from examples import EXAMPLES
def clean(o):
    if isinstance(o, float) and math.isinf(o): return "INF"
    if isinstance(o, float) and o.is_integer(): return int(o)
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(x) for x in o]
    return o
cases = [dict(name=k, vertices=e["vertices"], edges=e["edges"], src=e["src"]) for k, e in EXAMPLES.items()]
random.seed(7)
for t in range(500):
    n = random.randint(2, 8); V = [chr(65 + i) for i in range(n)]
    E = [(u, v, random.randint(-4, 9)) for u in V for v in V if u != v and random.random() < 0.3]
    random.shuffle(E)
    cases.append(dict(name=f"rand{t}", vertices=V, edges=E, src="A"))
for c in cases:
    c["dij"] = clean(dijkstra_trace(c["vertices"], c["edges"], c["src"]))
    c["bf"] = clean(bellman_ford_trace(c["vertices"], c["edges"], c["src"]))
    c["edges"] = clean(c["edges"])
json.dump(cases, open("/tmp/claude-0/-home-claude/03197a7e-b736-56e4-8716-315fb60c98c4/scratchpad/parity.json", "w"), ensure_ascii=False)
print(len(cases), "cases")
