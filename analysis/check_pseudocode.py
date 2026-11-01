"""보고서에 실은 의사코드를 글자 그대로 옮겨서 완전탐색과 대조한다 (1-based)."""
import itertools, math, random, json
from verify import brute

def lis_dp_pseudo(n, a):            # a[1..n]
    dp = [0] * (n + 1); prev = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = 1; prev[i] = 0
        for j in range(1, i):
            if a[j] < a[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1; prev[i] = j
    best = max(range(1, n + 1), key=lambda k: (dp[k], -k))
    return dp[best]

def lis_patience_pseudo(n, a):
    piles = 0; top = [0] * (n + 2); back = [0] * (n + 1)
    for i in range(1, n + 1):
        lo, hi = 1, piles + 1
        while lo < hi:
            mid = (lo + hi) // 2
            if a[top[mid]] >= a[i]: hi = mid
            else: lo = mid + 1
        k = lo
        back[i] = top[k - 1] if k > 1 else 0
        if k == piles + 1: piles += 1
        top[k] = i
    # back을 따라 복원해서 증가 수열인지도 확인
    seq = []; t = top[piles]
    while t: seq.append(a[t]); t = back[t]
    seq.reverse()
    assert all(seq[x] < seq[x + 1] for x in range(len(seq) - 1)) and len(seq) == piles
    return piles

random.seed(9); bad = 0
for _ in range(10000):
    n = random.randint(1, 11); arr = [random.randint(-4, 12) for _ in range(n)]
    a = [None] + arr; L = brute(arr)
    if lis_dp_pseudo(n, a) != L or lis_patience_pseudo(n, a) != L: bad += 1
print("pseudocode vs brute force mismatches:", bad, "/ 10000")

# 보고서 숫자
asc = sum(math.ceil(math.log2(i)) for i in range(2, 8001))
print("ascending n=8000: sum ceil(log2 i) =", asc)
rows = json.load(open("bench.json"))
r = [x for x in rows if x["n"] == 8000 and x["shape"] == "random"][0]
ns_per = r["dp_t"] / r["dp_comps"] * 1e9
big = [x for x in rows if x["shape"] == "random_big"]
for x in big:
    n = x["n"]; dpc = n * (n - 1) // 2
    print(f"n={n:>8,}: DP comps {dpc:.3e}, est {dpc*ns_per/1e9/3600:.2f} h | patience {x['pat_comps']:,} comps {x['pat_t']:.3f}s | L={x['L']} 2sqrt(n)={2*math.sqrt(n):.0f}")
print(f"DP ns/comparison (n=8000 random): {ns_per:.1f}")
for x in rows:
    if x["shape"] == "random": print(x["n"], x["L"], round(2*math.sqrt(x["n"])), round(x["dp_comps"]/x["pat_comps"]), f"{x['dp_t']/x['pat_t']:.0f}")
