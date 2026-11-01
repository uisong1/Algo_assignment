"""Dijkstra vs Bellman-Ford — 단계 기록(trace)을 남기는 구현.

교재(Neapolitan) 스타일:
- Dijkstra: 아직 확정되지 않은 정점 중 dist가 가장 작은 정점을 골라 '확정'하고,
  그 정점에서 나가는 간선으로 '확정되지 않은' 이웃을 완화(relax)한다. 확정된 정점은 다시 보지 않는다.
- Bellman-Ford: 모든 간선을 V-1번 완화한다. 한 라운드에서 아무 것도 안 바뀌면 조기 종료.
  V-1번 뒤에도 줄어드는 간선이 있으면 음수 사이클.
"""
import heapq
import math

INF = math.inf


def fmt(x):
    if x == INF:
        return "∞"
    x = int(x) if float(x).is_integer() else x
    return str(x).replace("-", "−")


def wfmt(w):
    """간선 가중치를 식 안에 쓸 때: 음수면 괄호."""
    return f"({fmt(w)})" if w < 0 else fmt(w)


# 숫자 뒤 조사: 받침이 있으면 '으로/이', 없거나 ㄹ이면 '로/가'
_BATCHIM = {"0": True, "1": "ㄹ", "2": False, "3": True, "4": False, "5": False,
            "6": True, "7": "ㄹ", "8": "ㄹ", "9": False}


def _last(x):
    t = fmt(x)
    if t == "∞":
        return False          # 무한대
    t = t.lstrip("−")
    if len(t) > 1 and t.endswith("0"):
        return True           # 십/백/천 → 받침
    return _BATCHIM[t[-1]]


def ro(x):
    b = _last(x)
    return fmt(x) + ("으로" if b is True else "로")


def iga(x):
    b = _last(x)
    return fmt(x) + ("이" if b is True or b == "ㄹ" else "가")


def dijkstra_trace(vertices, edges, src):
    """배열 기반 O(V^2) Dijkstra. 단계마다 상태와 설명을 기록한다."""
    adj = {v: [] for v in vertices}
    for u, v, w in edges:
        adj[u].append((v, w))
    dist = {v: INF for v in vertices}
    prev = {v: None for v in vertices}
    done = set()
    dist[src] = 0
    steps = []
    relax_checks = 0

    def snap(kind, msg, **extra):
        steps.append(dict(kind=kind, msg=msg, dist=dict(dist), prev=dict(prev),
                          done=sorted(done, key=vertices.index), **extra))

    snap("init", f"출발점 {src}의 거리를 0, 나머지는 ∞로 둔다. 아직 확정된 정점은 없다.")
    while len(done) < len(vertices):
        cand = [v for v in vertices if v not in done and dist[v] < INF]
        if not cand:
            rest = [v for v in vertices if v not in done]
            snap("stop", f"남은 정점 {', '.join(rest)}은(는) 도달할 수 없다(∞). 종료.")
            break
        u = min(cand, key=lambda v: (dist[v], vertices.index(v)))
        done.add(u)
        others = [f"{v}={fmt(dist[v])}" for v in vertices if v not in done and dist[v] < INF]
        cmp = f"(다른 후보: {', '.join(others)})" if others else ""
        snap("select", f"확정 안 된 정점 중 거리가 가장 작은 {u}({fmt(dist[u])})를 꺼내 확정한다{cmp}. "
                       f"간선이 모두 양수라면 더 먼 후보를 거쳐 돌아와도 {fmt(dist[u])}보다 짧아질 수 없기 때문이다.", node=u)
        for v, w in adj[u]:
            relax_checks += 1
            if v in done:
                if dist[u] + w < dist[v]:
                    snap("missed", f"{u}→{v}({fmt(w)}): {fmt(dist[u])} + {wfmt(w)} = {fmt(dist[u] + w)} < {fmt(dist[v])} 로 "
                                   f"실제로는 더 짧은 길이다. 하지만 {v}는 이미 확정됐고 Dijkstra는 확정을 되돌리지 않는다. "
                                   f"→ {v}의 거리 {fmt(dist[v])}는 틀린 값으로 남고, {v}를 거쳐 계산된 다른 정점도 함께 틀린다. "
                                   f"(음수 간선이 '확정 = 최단'이라는 전제를 깨뜨렸다)", edge=[u, v], node=u, wrong=v)
                else:
                    snap("skip", f"{u}→{v}({fmt(w)}): {v}는 이미 확정됐으므로 다시 보지 않는다.",
                         edge=[u, v], node=u)
                continue
            new = dist[u] + w
            if new < dist[v]:
                old = dist[v]
                dist[v] = new
                prev[v] = u
                snap("relax", f"{u}→{v}({fmt(w)}): {fmt(dist[u])} + {wfmt(w)} = {fmt(new)} < {fmt(old)} 이므로 "
                              f"{v}의 거리를 {ro(new)} 줄인다(직전 정점 {u}).", edge=[u, v], node=u, updated=v)
            else:
                snap("norelax", f"{u}→{v}({fmt(w)}): {fmt(dist[u])} + {wfmt(w)} = {fmt(new)} ≥ {fmt(dist[v])} 이므로 그대로 둔다.",
                     edge=[u, v], node=u)
    snap("end", "모든 정점을 확정했다. 표의 값이 Dijkstra의 결과다.")
    return dict(dist=dist, prev=prev, steps=steps, relax_checks=relax_checks)


def bellman_ford_trace(vertices, edges, src):
    """Bellman-Ford. 라운드마다 간선 목록 순서대로 완화하고 기록한다."""
    dist = {v: INF for v in vertices}
    prev = {v: None for v in vertices}
    dist[src] = 0
    steps = []
    relax_checks = 0
    n = len(vertices)

    def snap(kind, msg, **extra):
        steps.append(dict(kind=kind, msg=msg, dist=dict(dist), prev=dict(prev), **extra))

    snap("init", f"출발점 {src}의 거리를 0, 나머지는 ∞로 둔다. 모든 간선을 최대 V−1 = {n - 1}번 훑는다.")
    rounds_used = 0
    for r in range(1, n):
        changed = False
        snap("round", f"라운드 {r} 시작: 간선 {len(edges)}개를 순서대로 모두 검사한다. "
                      f"라운드 {iga(r)} 끝나면 간선 {r}개 이하로 가는 최단거리가 확정된다.", round=r)
        for u, v, w in edges:
            relax_checks += 1
            if dist[u] == INF:
                snap("norelax", f"{u}→{v}({fmt(w)}): {u}에 아직 도달하지 못했다(∞). 건너뛴다.", edge=[u, v], round=r)
                continue
            new = dist[u] + w
            if new < dist[v]:
                old = dist[v]
                dist[v] = new
                prev[v] = u
                changed = True
                snap("relax", f"{u}→{v}({fmt(w)}): {fmt(dist[u])} + {wfmt(w)} = {fmt(new)} < {fmt(old)} 이므로 "
                              f"{v}의 거리를 {ro(new)} 줄인다.", edge=[u, v], round=r, updated=v)
            else:
                snap("norelax", f"{u}→{v}({fmt(w)}): {fmt(dist[u])} + {wfmt(w)} = {fmt(new)} ≥ {fmt(dist[v])} 이므로 그대로 둔다.",
                     edge=[u, v], round=r)
        rounds_used = r
        if not changed:
            snap("early", f"라운드 {r}에서 바뀐 값이 하나도 없다. 더 돌려도 변하지 않으므로 조기 종료한다.", round=r)
            break
    neg_cycle = False
    if rounds_used == n - 1:
        snap("check", f"V−1 = {n - 1}번을 다 돌았다. 음수 사이클이 있는지 간선을 한 번 더 검사한다.")
        for u, v, w in edges:
            relax_checks += 1
            if dist[u] < INF and dist[u] + w < dist[v]:
                neg_cycle = True
                snap("negcycle", f"{u}→{v}({fmt(w)}): {fmt(dist[u])} + {wfmt(w)} = {fmt(dist[u] + w)} < {fmt(dist[v])} — "
                                 f"V−1번 뒤에도 또 줄어든다. 단순 경로는 간선이 최대 V−1개이므로, "
                                 f"이는 음수 사이클이 있다는 뜻이다. 최단거리가 정의되지 않는다.", edge=[u, v])
                break
        if not neg_cycle:
            snap("ok", "더 줄어드는 간선이 없다. 음수 사이클이 없으므로 결과가 확정됐다.")
    if not neg_cycle:
        snap("end", "Bellman-Ford 종료. 표의 값이 최단거리다.")
    return dict(dist=dist, prev=prev, steps=steps, relax_checks=relax_checks,
                rounds=rounds_used, neg_cycle=neg_cycle)


# ---- 벤치마크용(기록 없음) ----
def dijkstra_heap(n, adj, src=0):
    dist = [INF] * n
    dist[src] = 0
    pq = [(0, src)]
    done = [False] * n
    ops = 0
    while pq:
        d, u = heapq.heappop(pq)
        if done[u]:
            continue
        done[u] = True
        for v, w in adj[u]:
            ops += 1
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist, ops


def dijkstra_array(n, adj, src=0):
    dist = [INF] * n
    dist[src] = 0
    done = [False] * n
    ops = 0
    for _ in range(n):
        u, best = -1, INF
        for v in range(n):           # 최솟값 찾기: O(V)
            ops += 1
            if not done[v] and dist[v] < best:
                u, best = v, dist[v]
        if u == -1:
            break
        done[u] = True
        for v, w in adj[u]:
            ops += 1
            if not done[v] and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist, ops


def bellman_ford(n, edge_list, src=0, early_stop=True):
    dist = [INF] * n
    dist[src] = 0
    ops = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edge_list:
            ops += 1
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if early_stop and not changed:
            break
    return dist, ops
