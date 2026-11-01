import networkx as nx, random, math
from sp import *
from examples import EXAMPLES

for key, ex in EXAMPLES.items():
    V, E, s = ex["vertices"], ex["edges"], ex["src"]
    d = dijkstra_trace(V, E, s); b = bellman_ford_trace(V, E, s)
    G = nx.DiGraph(); G.add_nodes_from(V); G.add_weighted_edges_from(E)
    print(f"\n== {key}: {ex['title']}")
    if nx.negative_edge_cycle(G):
        print("  networkx: NEGATIVE CYCLE")
        truth = None
    else:
        truth = nx.single_source_bellman_ford_path_length(G, s)
        truth = {v: truth.get(v, INF) for v in V}
    print("  truth   :", truth)
    print("  dijkstra:", {k: fmt(x) for k, x in d['dist'].items()}, "checks", d['relax_checks'], "steps", len(d['steps']))
    print("  bellman :", {k: fmt(x) for k, x in b['dist'].items()}, "checks", b['relax_checks'], "rounds", b['rounds'], "negcycle", b['neg_cycle'], "steps", len(b['steps']))
    if truth: print("  D ok?", d['dist']==truth, " BF ok?", b['dist']==truth)

# 무작위 교차검증 (양수 그래프: 셋 다 일치, 음수 간선: BF == networkx)
random.seed(1); bad=0
for t in range(3000):
    n = random.randint(2, 8); V=[chr(65+i) for i in range(n)]
    E=[(u,v,random.randint(1,9)) for u in V for v in V if u!=v and random.random()<0.35]
    d=dijkstra_trace(V,E,'A')['dist']; b=bellman_ford_trace(V,E,'A')['dist']
    G=nx.DiGraph(); G.add_nodes_from(V); G.add_weighted_edges_from(E)
    tr=nx.single_source_dijkstra_path_length(G,'A'); tr={v:tr.get(v,INF) for v in V}
    if d!=tr or b!=tr: bad+=1
    E2=[(u,v,w-3) for u,v,w in E]
    G2=nx.DiGraph(); G2.add_nodes_from(V); G2.add_weighted_edges_from(E2)
    bt=bellman_ford_trace(V,E2,'A')
    reach=nx.descendants(G2,'A')|{'A'}
    negc = any(nx.negative_edge_cycle(G2.subgraph(c).copy()) for c in nx.strongly_connected_components(G2.subgraph(reach)) if len(c)>1)
    if negc != bt['neg_cycle']: bad+=1
    elif not negc:
        tr2=nx.single_source_bellman_ford_path_length(G2,'A'); tr2={v:tr2.get(v,INF) for v in V}
        if bt['dist']!=tr2: bad+=1
print("\nrandom cross-check mismatches:", bad)
