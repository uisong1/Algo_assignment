# 단계별 다이어그램(DP 표 / 페이션스 더미) HTML 생성
A = [10, 3, 11, 5, 8, 6, 1, 2, 7]
n = len(A)

# ---------- DP ----------
dp, prev, dp_steps = [0]*n, [-1]*n, []
for i in range(n):
    dp[i], prev[i] = 1, -1
    for j in range(i):
        if A[j] < A[i] and dp[j] + 1 > dp[i]:
            dp[i], prev[i] = dp[j] + 1, j
    dp_steps.append((i, prev[i], dp[:i+1], prev[:i+1]))
best = max(range(n), key=lambda k: (dp[k], -k))
path = []; k = best
while k != -1: path.append(k); k = prev[k]
path = path[::-1]

def dp_panel(i, j, dps, title, what, why, final=False):
    cw, gap, x0 = 28, 4, 30
    W = x0 + n*(cw+gap); H = 112
    s = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    for k in range(n):
        x = x0 + k*(cw+gap)
        s.append(f'<text x="{x+cw/2}" y="12" class="ix">{k+1}</text>')
    s.append('<text x="24" y="36" class="lab" text-anchor="end">a</text><text x="24" y="74" class="lab" text-anchor="end">dp</text>')
    for k in range(n):
        x = x0 + k*(cw+gap)
        if final: cls = "p" if k in path else ""
        else: cls = "i" if k == i else ("j" if k == j else ("" if k < i else "fut"))
        s.append(f'<rect x="{x}" y="18" width="{cw}" height="28" rx="5" class="c {cls}"/><text x="{x+cw/2}" y="37" class="v {cls}">{A[k]}</text>')
        if k < len(dps):
            s.append(f'<rect x="{x}" y="56" width="{cw}" height="28" rx="5" class="c {cls}"/><text x="{x+cw/2}" y="75" class="v {cls}">{dps[k]}</text>')
        else:
            s.append(f'<rect x="{x}" y="56" width="{cw}" height="28" rx="5" class="c empty"/>')
    def arc(a, b, cls):
        xa = x0 + a*(cw+gap) + cw/2; xb = x0 + b*(cw+gap) + cw/2
        mid = (xa+xb)/2; dy = 14 + abs(b-a)*3
        return f'<path d="M{xa} 86 Q{mid} {86+dy} {xb} 88" class="arc {cls}" marker-end="url(#m{cls})"/>'
    if final:
        for a, b in zip(path, path[1:]): s.append(arc(a, b, "p"))
    elif j is not None and j >= 0:
        s.append(arc(j, i, "i"))
    s.append('</svg>')
    return f'''<div class="panel{' final' if final else ''}"><div class="hd"><b>{title}</b></div>{''.join(s)}
<p class="w"><i>무엇을</i><span>{what}</span></p><p class="w"><i>왜</i><span>{why}</span></p></div>'''

dp_html = []
for (i, j, dps, prs) in dp_steps:
    title = f"Step {i+1} · a[{i+1}] = {A[i]}"
    smaller = [k for k in range(i) if A[k] < A[i]]
    if j == -1:
        what = f"dp[{i+1}] = 1"
        why = f"앞에 {A[i]}보다 작은 수가 없어 혼자서 길이 1" if i else "첫 원소라 혼자서 길이 1"
    else:
        what = f"dp[{i+1}] = dp[{j+1}] + 1 = {dps[i]}, prev = {j+1}"
        cand = ", ".join(f"{A[k]}({dps[k]})" for k in smaller)
        why = f"{A[i]}보다 작은 앞의 수 {cand} 중 dp가 가장 큰 {A[j]} 뒤에 붙임"
    dp_html.append(dp_panel(i, j, dps, title, what, why))
dp_html.append(dp_panel(None, None, dp, "답 복원",
    f"dp 최댓값 {dp[best]} (위치 {best+1})에서 prev를 거꾸로",
    " ← ".join(f"a[{k+1}]" for k in path[::-1]) + f" → <b>{', '.join(str(A[k]) for k in path)}</b>", final=True))

# ---------- Patience ----------
piles, tops, back, pt_steps = [], [], [-1]*n, []
for i, x in enumerate(A):
    lo, hi = 0, len(tops)
    while lo < hi:
        mid = (lo+hi)//2
        if A[tops[mid]] >= x: hi = mid
        else: lo = mid + 1
    k = lo
    back[i] = tops[k-1] if k > 0 else -1
    replaced = tops[k] if k < len(tops) else None
    if k == len(tops): piles.append([]); tops.append(i)
    else: tops[k] = i
    piles[k].append(i)
    pt_steps.append((i, k, replaced, [p[:] for p in piles], tops[:]))
ppath = []; k = tops[-1]
while k != -1: ppath.append(k); k = back[k]
ppath = ppath[::-1]

def pt_panel(i, k, piles_now, title, what, why, final=False):
    cw, ch, gap, step = 34, 44, 10, 18
    W = 4*(cw+gap) + 12; maxh = max(len(p) for p in piles_now)
    H = 16 + (maxh-1)*step + ch + 22
    H = max(H, 16 + 2*step + ch + 22)
    s = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect x="0" y="0" width="{W}" height="{H}" rx="8" class="felt"/>']
    pos = {}
    for pk, p in enumerate(piles_now):
        x = 8 + pk*(cw+gap)
        for d, idx in enumerate(p):
            y = 10 + d*step; pos[idx] = (x, y)
            top = d == len(p) - 1
            if final: cls = "p" if idx in ppath and top or (idx in ppath) else ""
            else: cls = "i" if idx == i else ""
            s.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="4" class="card {cls}"/>')
            if top: s.append(f'<text x="{x+cw/2}" y="{y+29}" class="cv {cls}">{A[idx]}</text>')
            else: s.append(f'<text x="{x+5}" y="{y+13}" class="cb {cls}">{A[idx]}</text>')
        s.append(f'<text x="{x+cw/2}" y="{H-6}" class="pl">더미{pk+1}</text>')
    def arrow(a, b, cls):
        xa, ya = pos[a]; xb, yb = pos[b]
        x1, y1 = xa + cw/2, ya + 2; x2, y2 = xb + cw - 6, yb + 6
        return f'<path d="M{x1} {y1} Q{(x1+x2)/2} {min(y1,y2)-10} {x2} {y2}" class="arc {cls}" marker-end="url(#m{cls})"/>'
    if final:
        for a, b in zip(ppath[1:], ppath): s.append(arrow(a, b, "pw"))
    elif back[i] != -1:
        s.append(arrow(i, back[i], "iw"))
    s.append('</svg>')
    return f'''<div class="panel{' final' if final else ''}"><div class="hd"><b>{title}</b></div>{''.join(s)}
<p class="w"><i>무엇을</i><span>{what}</span></p><p class="w"><i>왜</i><span>{why}</span></p></div>'''

pt_html = []
for (i, k, rep, ps, tp) in pt_steps:
    x = A[i]; before = [A[t] for t in (pt_steps[i-1][4] if i else [])]
    title = f"Step {i+1} · 카드 a[{i+1}] = {x}"
    if rep is None:
        what = f"새 더미 {k+1} 만들기" + (f", 화살표 → {A[back[i]]}" if back[i] != -1 else "")
        why = (f"맨 윗장 [{', '.join(map(str,before))}] 모두 {x}보다 작음 → 길이 {k+1}" if before else "첫 카드라 더미가 없음")
    else:
        what = f"더미 {k+1}의 {A[rep]} 위에 올리기" + (f", 화살표 → {A[back[i]]}" if back[i] != -1 else "")
        why = f"맨 윗장 [{', '.join(map(str,before))}] 중 {x} 이상인 가장 왼쪽이 {A[rep]} (이분검색). 길이 {k+1}의 끝값을 {A[rep]}→{x}로 낮춤"
    pt_html.append(pt_panel(i, k, ps, title, what, why))
pt_html.append(pt_panel(None, None, pt_steps[-1][3], "답 복원",
    f"더미 {len(tops)}개 → 길이 {len(tops)}. 마지막 더미의 {A[tops[-1]]}에서 화살표를 거꾸로",
    f"<b>{', '.join(str(A[t]) for t in ppath)}</b>. 맨 윗장 [{', '.join(str(A[t]) for t in tops)}]은 답이 아님 (2가 6보다 뒤에 나옴)", final=True))

CSS = '''
body{margin:0;background:#fff;font-family:Geist,"Pretendard Variable",sans-serif;color:#171717;letter-spacing:-.01em}
.sheet{padding:28px 32px 32px;width:1640px;box-sizing:border-box}
h2{margin:0 0 4px;font-size:26px;font-weight:600;letter-spacing:-.04em}
.sub{margin:0 0 18px;color:#4d4d4d;font-size:15px}
.grid{display:grid;grid-template-columns:repeat(var(--cols),1fr);gap:28px 30px}
.panel{position:relative;border:1px solid #ebebeb;border-radius:8px;padding:12px 14px 12px;box-shadow:0 1px 2px rgba(0,0,0,.05);background:#fff}
.g5 .panel:not(.final):not(:nth-child(5n))::after, .g4 .panel:not(.final):not(:nth-child(4n))::after{content:"→";position:absolute;right:-24px;top:50%;font-size:18px;color:#a1a1a1}
.panel.final{border-color:#b49be6;background:#fbf9ff}
.hd{font-size:14px;margin-bottom:8px} .hd b{font-weight:600}
svg{display:block;margin:0 auto 8px;overflow:visible}
.w{margin:3px 0 0;font-size:12.5px;line-height:1.5;display:grid;grid-template-columns:40px 1fr;color:#171717}
.w i{font-style:normal;font-family:"Geist Mono",monospace;font-size:11px;color:#888;padding-top:1px}
.ix{font:11px "Geist Mono",monospace;fill:#a1a1a1;text-anchor:middle}
.lab{font:12px "Geist Mono",monospace;fill:#4d4d4d}
.c{fill:#fff;stroke:#e5e5e5} .c.empty{fill:none;stroke:#e5e5e5;stroke-dasharray:3 3} .c.fut{fill:#fafafa}
.c.i{fill:#d3e5ff;stroke:#0761d1;stroke-width:1.5} .c.j{fill:#ffefcf;stroke:#ab570a;stroke-width:1.5} .c.p{fill:#d8ccf1;stroke:#4c2889;stroke-width:1.5}
.v{font-size:14px;font-weight:500;text-anchor:middle;fill:#171717} .v.fut{fill:#a1a1a1} .v.i{fill:#0761d1;font-weight:600} .v.j{fill:#ab570a;font-weight:600} .v.p{fill:#4c2889;font-weight:600}
.arc{fill:none;stroke-width:1.5} .arc.i{stroke:#0761d1} .arc.p{stroke:#4c2889} .arc.iw{stroke:#6aa8ff;stroke-width:1.6} .arc.pw{stroke:#b49be6;stroke-width:1.6}
.felt{fill:#171717}
.card{fill:#fff;stroke:rgba(0,0,0,.25)} .card.i{fill:#d3e5ff;stroke:#0070f3;stroke-width:2} .card.p{fill:#d8ccf1;stroke:#b49be6;stroke-width:1.5}
.cv{font-size:17px;font-weight:600;text-anchor:middle;fill:#171717} .cv.i{fill:#0761d1} .cv.p{fill:#4c2889}
.cb{font-size:11px;font-weight:600;fill:#4d4d4d} .cb.p{fill:#4c2889}
.pl{font:10px "Geist Mono",monospace;fill:#a1a1a1;text-anchor:middle}
.legend{display:flex;gap:18px;font-size:13px;color:#4d4d4d;margin:0 0 18px}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px;border:1.5px solid}
'''
DEFS = '''<svg width="0" height="0" style="position:absolute"><defs>
<marker id="mi" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#0761d1"/></marker>
<marker id="mp" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#4c2889"/></marker>
<marker id="miw" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#6aa8ff"/></marker>
<marker id="mpw" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#b49be6"/></marker>
</defs></svg>'''
HEAD = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono&display=swap"><link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"><style>'+CSS+'</style></head><body>'+DEFS
seq = ", ".join(map(str, A))
open("dp.html","w").write(HEAD+f'''<div class="sheet" id="s"><h2>동적계획법(DP) — 표를 왼쪽부터 채우기</h2>
<p class="sub">입력 {seq}. dp[i] = a[i]로 끝나는 가장 긴 증가 부분수열의 길이. 각 단계는 i번째 칸 하나를 채운다.</p>
<div class="legend"><span><i class="sw" style="background:#d3e5ff;border-color:#0761d1"></i>이번에 채운 칸 i</span><span><i class="sw" style="background:#ffefcf;border-color:#ab570a"></i>이어 붙인 앞 원소 j (prev)</span><span><i class="sw" style="background:#d8ccf1;border-color:#4c2889"></i>정답 경로</span></div>
<div class="grid g4" style="--cols:4">{''.join(dp_html)}</div></div></body></html>''')
open("pat.html","w").write(HEAD+f'''<div class="sheet" id="s"><h2>페이션스 정렬 — 카드를 더미에 쌓기</h2>
<p class="sub">입력 {seq}. 각 카드를 "맨 윗장이 그 카드 이상인 가장 왼쪽 더미"에 올리고, 없으면 오른쪽에 새 더미를 만든다. 더미 개수가 LIS 길이.</p>
<div class="legend"><span><i class="sw" style="background:#d3e5ff;border-color:#0070f3"></i>이번에 놓은 카드</span><span><i class="sw" style="background:#fff;border-color:#6aa8ff"></i>화살표: 왼쪽 더미 맨 윗장 (back)</span><span><i class="sw" style="background:#d8ccf1;border-color:#4c2889"></i>정답 경로</span></div>
<div class="grid g5" style="--cols:5">{''.join(pt_html)}</div></div></body></html>''')
print("dp", [d[2] for d in dp_steps][-1], "path", [A[k] for k in path], "| pat tops", [A[t] for t in tops], "path", [A[t] for t in ppath])
