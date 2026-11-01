"""LIS 구현 검증: 모든 부분수열을 다 확인하는 완전탐색과 대조한다."""
import itertools, random
from lis import lis_dp_trace, lis_patience_trace, lis_dp, lis_patience

def brute(a):
    n = len(a)
    for L in range(n, 0, -1):
        for idx in itertools.combinations(range(n), L):
            if all(a[idx[k]] < a[idx[k + 1]] for k in range(L - 1)):
                return L
    return 0

def is_valid(a, path, L):
    # path는 1-based 인덱스, 순서가 증가하고 값도 엄격히 증가해야 함
    return (len(path) == L and all(path[k] < path[k + 1] for k in range(L - 1))
            and all(a[path[k] - 1] < a[path[k + 1] - 1] for k in range(L - 1)))

random.seed(11)
bad = 0; total = 0
for t in range(20000):
    n = random.randint(1, 12)
    a = [random.randint(-5, 12) for _ in range(n)]          # 중복·음수 포함
    if t % 5 == 0: a = sorted(a)                             # 오름차순
    if t % 7 == 0: a = sorted(a, reverse=True)               # 내림차순
    L = brute(a)
    d = lis_dp_trace(a); p = lis_patience_trace(a)
    ok = (d["length"] == p["length"] == L == lis_dp(a)[0] == lis_patience(a)[0]
          and is_valid(a, d["path"], L) and is_valid(a, p["path"], L)
          and d["comps"] == lis_dp(a)[1] and p["comps"] == lis_patience(a)[1]
          and d["comps"] == n * (n - 1) // 2)
    total += 1
    if not ok:
        bad += 1
        if bad < 5: print("BAD", a, L, d["length"], p["length"], d["path"], p["path"])
print(f"{total} random cases, mismatches: {bad}")
