"""V, E를 키워 가며 실제 연산 횟수와 실행 시간을 잰다.

연산 횟수(ops): 간선 완화 검사 1번 = 1 (배열 Dijkstra는 최솟값 찾기 비교도 1로 셈).
컴퓨터 성능과 무관해서 이론 복잡도와 직접 비교할 수 있다.
"""
import json
import random
import time

from sp import bellman_ford, dijkstra_array, dijkstra_heap

random.seed(2026)


def random_graph(n, m):
    """정점 n, 간선 약 m개의 무작위 방향 그래프. 0번에서 모두 도달 가능하도록 경로를 하나 깐다."""
    perm = list(range(1, n))
    random.shuffle(perm)
    order = [0] + perm
    edges = {(order[i], order[i + 1]) for i in range(n - 1)}
    while len(edges) < m:
        u, v = random.randrange(n), random.randrange(n)
        if u != v:
            edges.add((u, v))
    edges = [(u, v, random.randint(1, 100)) for u, v in edges]
    random.shuffle(edges)
    return edges


def worst_bf_graph(n):
    """경로 0→1→…→n-1, 간선을 뒤에서부터 나열 → Bellman-Ford가 라운드마다 정점 1개씩만 확정."""
    path = [(i, i + 1, 1) for i in range(n - 1)]
    return list(reversed(path))


def adj_of(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    return adj


def timed(f, *a, reps=1):
    best = float("inf")
    out = None
    for _ in range(reps):
        t = time.perf_counter()
        out = f(*a)
        best = min(best, time.perf_counter() - t)
    return out, best


rows = []

# 실험 1: 희소 그래프 E = 4V (도로망처럼 정점마다 간선 몇 개)
for n in [100, 200, 400, 800, 1600, 3200]:
    m = 4 * n
    E = random_graph(n, m)
    A = adj_of(n, E)
    (dh, oh), th = timed(dijkstra_heap, n, A, reps=3)
    (da, oa), ta = timed(dijkstra_array, n, A, reps=1)
    (db, ob), tb = timed(bellman_ford, n, E, reps=1)
    (_, obn), tbn = timed(lambda: bellman_ford(n, E, early_stop=False)) if n <= 1600 else ((None, None), None)
    assert dh == da == db
    rows.append(dict(exp="sparse", V=n, E=len(E), dh_ops=oh, dh_t=th, da_ops=oa, da_t=ta,
                     bf_ops=ob, bf_t=tb, bf_full_ops=obn, bf_full_t=tbn))
    print(rows[-1])

# 실험 2: Bellman-Ford 최악 순서 (경로 그래프, 간선 역순) — 정확히 V-1 라운드
for n in [100, 200, 400, 800, 1600]:
    E = worst_bf_graph(n)
    A = adj_of(n, E)
    (dh, oh), th = timed(dijkstra_heap, n, A, reps=3)
    (db, ob), tb = timed(bellman_ford, n, E)
    assert dh == db
    rows.append(dict(exp="bf_worst", V=n, E=len(E), dh_ops=oh, dh_t=th, bf_ops=ob, bf_t=tb))
    print(rows[-1])

# 실험 3: 밀집 그래프 E ≈ V^2/2 — 배열 Dijkstra O(V^2) vs 힙 Dijkstra O(E log V)
for n in [100, 200, 400, 800]:
    m = n * (n - 1) // 2
    E = random_graph(n, m)
    A = adj_of(n, E)
    (dh, oh), th = timed(dijkstra_heap, n, A, reps=3)
    (da, oa), ta = timed(dijkstra_array, n, A, reps=3)
    assert dh == da
    rows.append(dict(exp="dense", V=n, E=len(E), dh_ops=oh, dh_t=th, da_ops=oa, da_t=ta))
    print(rows[-1])

json.dump(rows, open("bench.json", "w"), indent=1)
