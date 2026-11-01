"""최장 증가 부분수열(LIS, 엄격히 증가) — DP O(n^2) vs 페이션스 정렬 O(n log n).

두 함수 모두 단계 기록(trace)을 남긴다. 기록의 문장은 웹 시각화(docs/lis.js)와 똑같이 맞춘다.
인덱스는 화면·보고서와 맞추려고 1부터 센다(a[1..n]).
"""


def _pos(i):
    return f"a[{i}]"


# ── 숫자 뒤 조사 (숫자를 읽는 소리 기준: 3=삼, 10=십, 2=이 …) ──
_BATCHIM = {"0": True, "1": "ㄹ", "2": False, "3": True, "4": False, "5": False,
            "6": True, "7": "ㄹ", "8": "ㄹ", "9": False}


def _final(x):
    t = str(x).lstrip("-−")
    if len(t) > 1 and t.endswith("0"):
        return True                      # 십·백·천
    return _BATCHIM[t[-1]]


def eul(x):   # 을/를
    return f"{x}" + ("을" if _final(x) else "를")


def eun(x):   # 은/는
    return f"{x}" + ("은" if _final(x) else "는")


def iga(x):   # 이/가
    return f"{x}" + ("이" if _final(x) else "가")


def ro(x):    # 으로/로 (ㄹ 받침은 '로')
    return f"{x}" + ("으로" if _final(x) is True else "로")


def pp(x, with_b, without_b):   # 조사만 돌려준다: 괄호 뒤에 붙일 때
    return with_b if _final(x) else without_b


def ida(x):   # 이라서/라서
    return f"{x}" + ("이라서" if _final(x) else "라서")


# ───────────────────────── DP: O(n^2) ─────────────────────────
def lis_dp_trace(a):
    """dp[i] = a[i]로 끝나는 가장 긴 증가 부분수열의 길이."""
    n = len(a)
    A = [None] + list(a)                 # 1-based
    dp = [None] * (n + 1)
    prev = [None] * (n + 1)
    steps = []
    comps = 0

    def snap(kind, msg, **extra):
        steps.append(dict(kind=kind, msg=msg, dp=dp[1:], prev=prev[1:], comps=comps, **extra))

    snap("init", f"dp[i] = '{_pos('i')}로 끝나는' 가장 긴 증가 부분수열의 길이. "
                 f"왼쪽 칸부터 하나씩 채운다. 칸 i를 채울 때는 왼쪽 칸 1..i−1만 보면 된다.")
    for i in range(1, n + 1):
        dp[i], prev[i] = 1, None
        snap("start", f"i = {i}: {_pos(i)} = {A[i]}. 일단 {A[i]} 혼자만으로도 길이 1이므로 dp[{i}] = 1로 시작한다.",
             i=i)
        for j in range(1, i):
            comps += 1
            if A[j] < A[i]:
                if dp[j] + 1 > dp[i]:
                    old = dp[i]
                    dp[i], prev[i] = dp[j] + 1, j
                    snap("update", f"j = {j}: {A[j]} < {A[i]} 이므로 {ro(A[j])} 끝나는 수열(길이 {dp[j]}) 뒤에 "
                                   f"{eul(A[i])} 붙일 수 있다. {dp[j]} + 1 = {dp[i]} > {old} → dp[{i}] = {dp[i]}, "
                                   f"앞 원소는 a[{j}].", i=i, j=j)
                else:
                    snap("noupdate", f"j = {j}: {A[j]} < {ida(A[i])} 붙일 수는 있지만 {dp[j]} + 1 = {dp[j] + 1} ≤ {dp[i]} 로 "
                                     f"지금보다 길어지지 않는다. 그대로 둔다.", i=i, j=j)
            else:
                snap("nolink", f"j = {j}: {A[j]} ≥ {A[i]} 이므로 {A[j]} 뒤에 {eul(A[i])} 붙이면 증가가 아니다. 건너뛴다.",
                     i=i, j=j)
        snap("fixed", f"dp[{i}] = {dp[i]} 확정. "
                      + (f"(a[{prev[i]}] = {A[prev[i]]} 뒤에 붙인 것)" if prev[i] else "(앞에 붙일 수 있는 원소가 없었다)"),
             i=i)
    best = max(range(1, n + 1), key=lambda k: (dp[k], -k))      # 최댓값 중 가장 앞
    path = []
    k = best
    while k:
        path.append(k)
        k = prev[k]
    path.reverse()
    snap("answer", f"dp 중 최댓값은 dp[{best}] = {dp[best]}. 여기서 prev를 거꾸로 따라가면 "
                   f"{' ← '.join(_pos(p) for p in reversed(path))} → 수열 "
                   f"{', '.join(str(A[p]) for p in path)} (길이 {dp[best]}).", path=path, i=best)
    return dict(length=dp[best], path=path, seq=[A[p] for p in path], steps=steps, comps=comps)


# ──────────────────── 페이션스 정렬: O(n log n) ────────────────────
def lis_patience_trace(a):
    """카드를 '맨 윗장이 자기 이상인 가장 왼쪽 더미'에 올린다. 더미 개수 = LIS 길이."""
    n = len(a)
    A = [None] + list(a)
    piles = []          # 각 더미 = 인덱스 목록(아래→위)
    back = [None] * (n + 1)   # 카드를 놓을 때 왼쪽 더미 맨 윗장
    steps = []
    comps = 0

    def tops():
        return [p[-1] for p in piles]

    def snap(kind, msg, **extra):
        steps.append(dict(kind=kind, msg=msg, piles=[list(p) for p in piles], back=back[1:], comps=comps, **extra))

    snap("init", "카드를 한 장씩 왼쪽부터 꺼낸다. 규칙: 맨 윗장이 '이 카드 이상'인 더미 중 가장 왼쪽 더미에 올린다. "
                 "그런 더미가 없으면 오른쪽 끝에 새 더미를 만든다.")
    for i in range(1, n + 1):
        x = A[i]
        T = tops()
        if T:
            snap("draw", f"{_pos(i)} = {x} 카드를 꺼낸다. 지금 맨 윗장은 왼쪽부터 [{', '.join(str(A[t]) for t in T)}]. "
                         f"맨 윗장은 왼쪽에서 오른쪽으로 항상 커지므로, {eul(x)} 올릴 더미를 이분검색으로 찾는다.", i=i)
        else:
            snap("draw", f"{_pos(i)} = {x} 카드를 꺼낸다. 아직 더미가 하나도 없다.", i=i)
        lo, hi = 0, len(T)               # [lo, hi) 안에서 '맨 윗장 ≥ x'인 첫 더미 찾기
        while lo < hi:
            mid = (lo + hi) // 2
            comps += 1
            if A[T[mid]] >= x:
                snap("probe", f"이분검색: 더미 {mid + 1}의 맨 윗장 {A[T[mid]]} ≥ {x} → 답은 더미 {mid + 1} 이하. 왼쪽 절반을 본다.",
                     i=i, probe=mid, lo=lo, hi=hi)
                hi = mid
            else:
                snap("probe", f"이분검색: 더미 {mid + 1}의 맨 윗장 {A[T[mid]]} < {x} → {eun(x)} 여기 못 올라간다. 오른쪽 절반을 본다.",
                     i=i, probe=mid, lo=lo, hi=hi)
                lo = mid + 1
        k = lo
        back[i] = T[k - 1] if k > 0 else None
        link = (f"놓는 순간 왼쪽 더미 맨 윗장 {A[back[i]]}({_pos(back[i])}){pp(A[back[i]], '을', '를')} 가리키는 화살표를 남긴다 "
                f"({A[back[i]]} < {x} 이므로 {A[back[i]]} 다음에 {iga(x)} 올 수 있다).") if back[i] else \
               "가장 왼쪽 더미라서 가리킬 카드가 없다(수열의 첫 원소 후보)."
        if k == len(piles):
            piles.append([i])
            snap("newpile", f"{x}보다 크거나 같은 맨 윗장이 없다 → 오른쪽 끝에 새 더미 {eul(k + 1)} 만든다. "
                            f"더미가 {len(piles)}개가 됐다 = 지금까지 길이 {len(piles)}짜리 증가 수열을 만들 수 있다는 뜻. {link}",
                 i=i, pile=k)
        else:
            covered = A[piles[k][-1]]
            piles[k].append(i)
            snap("place", f"더미 {k + 1}(맨 윗장 {covered})에 {eul(x)} 올린다. 더미 {k + 1}의 맨 윗장은 "
                          f"'길이 {k + 1}짜리 증가 수열이 끝날 수 있는 가장 작은 값'이다. {ro(covered)} 끝나는 것보다 "
                          f"{ro(x)} 끝나는 쪽이 뒤에 더 많은 수를 붙일 수 있으니 {ro(x)} 바꿔 둔다. {link}", i=i, pile=k)
    L = len(piles)
    t = piles[-1][-1]
    path = []
    while t:
        path.append(t)
        t = back[t]
    path.reverse()
    T = tops()
    note = ""
    bad = next((k for k in range(len(T) - 1) if T[k] > T[k + 1]), None)
    if bad is not None:      # 맨 윗장들이 원래 순서를 어기면 답이 아니다
        x, y = T[bad], T[bad + 1]
        note = (f" 주의: 마지막 맨 윗장들 [{', '.join(str(A[t]) for t in T)}]은 증가하는 것처럼 보이지만 답이 아니다. "
                f"{A[x]}({_pos(x)}){pp(A[x], '은', '는')} {A[y]}({_pos(y)})보다 뒤에 나온 수라서 이 순서로 뽑을 수 없다. "
                f"그래서 맨 윗장이 아니라 화살표를 따라가야 한다.")
    snap("answer", f"더미가 {L}개 → LIS 길이는 {L}. 마지막 더미의 맨 윗장에서 화살표를 거꾸로 따라가면 "
                   f"{', '.join(str(A[p]) for p in path)}.{note}", path=path)
    return dict(length=L, path=path, seq=[A[p] for p in path], steps=steps, comps=comps)


# ─────────────── 벤치마크용(기록 없음, 비교 횟수만 셈) ───────────────
def lis_dp(a):
    n = len(a)
    dp = [1] * n
    comps = 0
    for i in range(n):
        ai = a[i]
        best = 1
        for j in range(i):
            comps += 1
            if a[j] < ai and dp[j] + 1 > best:
                best = dp[j] + 1
        dp[i] = best
    return (max(dp) if dp else 0), comps


def lis_patience(a):
    tops = []
    comps = 0
    for x in a:
        lo, hi = 0, len(tops)
        while lo < hi:
            mid = (lo + hi) // 2
            comps += 1
            if tops[mid] >= x:
                hi = mid
            else:
                lo = mid + 1
        if lo == len(tops):
            tops.append(x)
        else:
            tops[lo] = x
    return len(tops), comps
