"""n을 키워 가며 두 알고리즘의 비교 횟수와 실행 시간을 잰다.

비교 횟수: DP는 a[j] < a[i] 비교, 페이션스는 이분검색의 맨 윗장 비교. 컴퓨터 성능과 무관하다.
입력 형태 3가지: 무작위 / 오름차순(더미가 계속 늘어나는 최악) / 내림차순(더미 1개뿐인 최선).
"""
import json
import math
import random
import time

from lis import lis_dp, lis_patience

random.seed(2026)


def timed(f, a, reps):
    best = float("inf")
    out = None
    for _ in range(reps):
        t = time.perf_counter()
        out = f(a)
        best = min(best, time.perf_counter() - t)
    return out, best


rows = []
for n in [250, 500, 1000, 2000, 4000, 8000]:
    for shape in ["random", "ascending", "descending"]:
        if shape == "random":
            a = random.sample(range(10 * n), n)
        elif shape == "ascending":
            a = list(range(n))
        else:
            a = list(range(n, 0, -1))
        (Ld, cd), td = timed(lis_dp, a, reps=1)
        (Lp, cp), tp = timed(lis_patience, a, reps=5)
        assert Ld == Lp
        rows.append(dict(n=n, shape=shape, L=Lp, dp_comps=cd, dp_t=td, pat_comps=cp, pat_t=tp,
                         n_log2_n=round(n * math.log2(n)), n_log2_L=round(n * math.log2(Lp + 1))))
        r = rows[-1]
        print(f"n={n:5d} {shape:10s} L={Lp:5d}  DP {cd:>10,} comps {td*1000:9.2f} ms | "
              f"Patience {cp:>7,} comps {tp*1000:7.3f} ms | n·log2(L+1)={r['n_log2_L']:,}")

# 페이션스만 큰 n까지 (DP는 너무 느려서 생략)
for n in [10**4, 10**5, 10**6]:
    a = random.sample(range(10 * n), n)
    (Lp, cp), tp = timed(lis_patience, a, reps=1)
    rows.append(dict(n=n, shape="random_big", L=Lp, pat_comps=cp, pat_t=tp))
    print(f"n={n:8d} random  L={Lp}  Patience {cp:,} comps {tp:.3f} s")

json.dump(rows, open("bench.json", "w"), indent=1)
