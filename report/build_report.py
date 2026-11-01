"""보고서(HTML → PDF) 생성기.

단계별 다이어그램은 analysis/lis.py의 단계 기록에서 자동으로 그린다.
그래서 그림 속 숫자는 실제 실행 결과와 항상 같다.
사용: python3 build_report.py  → report.html
"""
import html
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "analysis"))
from lis import eul, eun, iga, lis_dp_trace, lis_patience_trace, ro  # noqa: E402

INFO = json.load(open(os.path.join(HERE, "student.json"), encoding="utf-8"))
A = [10, 3, 11, 5, 8, 6, 1, 2, 7]
WEB = "https://uisong1.github.io/Algo_assignment/"
REPO = "https://github.com/uisong1/Algo_assignment"
esc = html.escape

DP = lis_dp_trace(A)
PAT = lis_patience_trace(A)
N = len(A)

# ───────────────────────── 그림: DP 표 ─────────────────────────
CELL, GAPX = 26, 4


def dp_frame(i):
    """칸 i를 채운 직후의 표. i: 파랑, prev[i]: 노랑."""
    st = next(s for s in DP["steps"] if s["kind"] == "fixed" and s["i"] == i)
    dp, prev = st["dp"], st["prev"]
    j = prev[i - 1]
    x0, w = 34, N * (CELL + GAPX)
    out = [f'<svg viewBox="0 0 {x0 + w} 92" class="fig-svg" role="img" aria-label="DP 표, i={i}">']
    out.append(f'<text x="0" y="40" class="rl">a[i]</text><text x="0" y="72" class="rl">dp[i]</text>')
    for k in range(1, N + 1):
        x = x0 + (k - 1) * (CELL + GAPX)
        cls = "ci" if k == i else "cj" if k == j else ""
        out.append(f'<text x="{x + CELL / 2}" y="12" class="ix">{k}</text>')
        out.append(f'<rect x="{x}" y="20" width="{CELL}" height="{CELL}" rx="4" class="c {cls}"/>'
                   f'<text x="{x + CELL / 2}" y="38" class="cv">{A[k - 1]}</text>')
        v = dp[k - 1]
        if v is None:
            out.append(f'<rect x="{x}" y="52" width="{CELL}" height="{CELL}" rx="4" class="c empty"/>')
        else:
            out.append(f'<rect x="{x}" y="52" width="{CELL}" height="{CELL}" rx="4" class="c {cls}"/>'
                       f'<text x="{x + CELL / 2}" y="70" class="cv">{v}</text>')
    if j:  # j → i 화살표
        xa = x0 + (j - 1) * (CELL + GAPX) + CELL / 2
        xb = x0 + (i - 1) * (CELL + GAPX) + CELL / 2
        out.append(f'<path d="M{xa},{80} Q{(xa + xb) / 2},{92} {xb},{80}" class="arrow-j" marker-end="url(#mj)"/>')
    out.append("</svg>")
    return "".join(out)


def dp_caption(i):
    ai = A[i - 1]
    st = next(s for s in DP["steps"] if s["kind"] == "fixed" and s["i"] == i)
    dp = st["dp"]
    cands = [(j, A[j - 1], dp[j - 1]) for j in range(1, i) if A[j - 1] < ai]
    if not cands:
        why = (f"왼쪽에 {ai}보다 작은 수가 없다. 그래서 {ai} 혼자서 길이 1이다."
               if i > 1 else "첫 칸이라 왼쪽에 아무것도 없다. 혼자서 길이 1이다.")
        return f"<b>무엇을</b> dp[{i}] = 1. <b>왜</b> {why}"
    best = max(c[2] for c in cands)
    pick = next(c for c in cands if c[2] == best)
    lst = ", ".join(f"{v}(dp {d})" for _, v, d in cands)
    tie = ""
    if sum(1 for c in cands if c[2] == best) > 1:
        tie = f" dp가 같은 후보가 여럿이면 앞쪽 원소({pick[1]})를 고른다."
    return (f"<b>무엇을</b> dp[{i}] = {best} + 1 = {best + 1}, prev[{i}] = {pick[0]}. "
            f"<b>왜</b> {ai} 앞에 올 수 있는 것은 왼쪽에서 {ai}보다 작은 {lst}이다. "
            f"이 중 가장 긴 수열(길이 {best})로 끝나는 {pick[1]} 뒤에 {eul(ai)} 붙이는 게 가장 길다.{tie}")


# ─────────────────────── 그림: 카드 더미 ───────────────────────
CW, CH, PG, OFF, TOPPAD = 30, 42, 12, 15, 22


def pile_svg(piles, back, hi=None, path=(), width_piles=4, label=True, arrows="new", ghost=None):
    """piles: 인덱스 목록. hi: 방금 놓은 카드. arrows: 'new'(방금 놓은 카드만) / 'all' / 'path'."""
    pathset = set(path)
    depth = max((len(p) for p in piles), default=1)
    W = width_piles * (CW + PG) + 4
    H = TOPPAD + (depth - 1) * OFF + CH + (16 if label else 4)
    pos = {}
    out = [f'<svg viewBox="0 0 {W} {H}" class="fig-svg felt-svg" role="img" aria-label="카드 더미">',
           f'<rect x="0" y="0" width="{W}" height="{H}" rx="6" class="felt"/>']
    for k, pile in enumerate(piles):
        x = 4 + k * (CW + PG)
        for d, idx in enumerate(pile):
            y = TOPPAD + d * OFF
            pos[idx] = (x, y)
            top = d == len(pile) - 1
            cls = "card"
            if idx in pathset: cls += " onpath"
            if idx == hi: cls += " new"
            out.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="4" class="{cls}"/>')
            if top:
                out.append(f'<text x="{x + CW / 2}" y="{y + 28}" class="cardv{" pv" if idx in pathset else ""}">{A[idx - 1]}</text>')
            else:
                out.append(f'<text x="{x + 4}" y="{y + 11}" class="cardu{" pv" if idx in pathset else ""}">{A[idx - 1]}</text>')
        if label:
            out.append(f'<text x="{x + CW / 2}" y="{H - 4}" class="pl">더미 {k + 1}</text>')
    if ghost:  # (pile, value) 가정 상황의 점선 카드
        k, v = ghost
        x = 4 + k * (CW + PG); y = TOPPAD + (len(piles[k]) if k < len(piles) else 0) * OFF
        out.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="4" class="card ghost"/>'
                   f'<text x="{x + CW / 2}" y="{y + 28}" class="cardv">{v}</text>')
    for idx, tgt in enumerate(back, start=1):
        if tgt is None or idx not in pos or tgt not in pos:
            continue
        on = idx in pathset and tgt in pathset
        if arrows == "new" and idx != hi:
            continue
        if arrows == "path" and not on:
            continue
        (x1, y1), (x2, y2) = pos[idx], pos[tgt]
        x1 += CW / 2; x2 += CW / 2; y1 += 1; y2 += 9
        cy = min(y1, y2) - 16
        cls = "ar-path" if on and arrows != "new" else "ar-new"
        mk = "mp" if cls == "ar-path" else "mn"
        out.append(f'<path d="M{x1},{y1} C{x1 - 4},{cy} {x2 + 4},{cy} {x2},{y2}" class="{cls}" marker-end="url(#{mk})"/>')
    out.append("</svg>")
    return "".join(out)


def pat_frames():
    frames = []
    steps = PAT["steps"]
    for i in range(1, N + 1):
        ss = [s for s in steps if s.get("i") == i]
        draw = ss[0]
        probes = [s for s in ss if s["kind"] == "probe"]
        put = ss[-1]
        before = next(s for s in steps if s.get("i") == i and s["kind"] == "draw")
        tops = [p[-1] for p in before["piles"]]
        x = A[i - 1]
        k = put["pile"]
        # 무엇을
        if put["kind"] == "newpile":
            what = f"새 더미 {eul(k + 1)} 만들고 {eul(x)} 놓는다."
        else:
            covered = A[before["piles"][k][-1] - 1]
            what = f"더미 {k + 1}의 {covered} 위에 {eul(x)} 올린다."
        # 왜
        if not tops:
            why = "아직 더미가 없다."
        else:
            seq = []
            for pr in probes:
                t = A[tops[pr["probe"]] - 1]
                seq.append(f"{t} ≥ {x}" if t >= x else f"{t} < {x}")
            why = f"맨 윗장 [{', '.join(str(A[t - 1]) for t in tops)}]에서 이분검색({', '.join(seq)})"
            why += (f" → {x} 이상인 맨 윗장이 없다." if put["kind"] == "newpile"
                    else f" → {x} 이상인 가장 왼쪽은 더미 {k + 1}.")
        if put["kind"] == "newpile":
            why += f" 더미가 {k + 1}개 = 길이 {k + 1}짜리 증가 수열을 만들 수 있다."
        elif tops:
            covered = A[before["piles"][k][-1] - 1]
            why += f" 길이 {k + 1}짜리 수열이 끝날 수 있는 가장 작은 값이 {covered}에서 {ro(x)} 낮아진다."
        b = put["back"][i - 1]
        link = f" 화살표는 왼쪽 더미 맨 윗장 {A[b - 1]}." if b else ""
        frames.append(dict(i=i, x=x, svg=pile_svg(put["piles"], put["back"], hi=i),
                           cap=f"<b>무엇을</b> {what}{link} <b>왜</b> {why}",
                           key=(i == 6), tail=(i == 9)))
    return frames


# ───────────────────── 그림: 핵심 장면 (가정 비교) ─────────────────────
def counterfactual():
    """6을 8 위에 올렸을 때 vs 올리지 않았다고 가정했을 때 7의 운명."""
    real = next(s for s in PAT["steps"] if s.get("i") == 9 and s["kind"] == "newpile")
    real_svg = pile_svg(real["piles"], real["back"], hi=9, arrows="new")
    # 가정: 6을 버리고(무시하고) 8이 그대로 있었다면, 7은 맨 윗장 [1, 2, 8]에서 8 위에 올라간다.
    fake_piles = [[1, 2, 7], [3, 4, 8], [5, 9]]   # 인덱스: 8이 남아 있고 7(a[9])이 그 위
    fake_back = [None] * N
    fake_svg = pile_svg(fake_piles, fake_back, hi=9, arrows="none", width_piles=4)
    return real_svg, fake_svg


# ───────────────────────── 본문 ─────────────────────────
def code_block(lines):
    return "<pre class='code'>" + "\n".join(esc(l) for l in lines) + "</pre>"


DP_CODE = [
    "int lis_dp (int n, const keytype a[], index prev[])",
    "{",
    "  index i, j, best;",
    "  int dp[1..n];",
    "  for (i = 1; i <= n; i++) {",
    "    dp[i] = 1;  prev[i] = 0;            // a[i] 혼자서 길이 1",
    "    for (j = 1; j < i; j++)               // 왼쪽 칸을 전부 본다",
    "      if (a[j] < a[i] && dp[j] + 1 > dp[i]) {",
    "        dp[i] = dp[j] + 1;               // a[j]로 끝나는 수열 뒤에 a[i]를 붙임",
    "        prev[i] = j;",
    "      }",
    "  }",
    "  best = dp[1..n]이 가장 큰 위치(같으면 앞쪽);",
    "  return dp[best];                       // best에서 prev를 거꾸로 따라가면 수열",
    "}",
]
PAT_CODE = [
    "int lis_patience (int n, const keytype a[], index back[])",
    "{",
    "  index i, k, lo, hi, mid;",
    "  int piles = 0;",
    "  index top[1..n];                       // top[k]: 더미 k 맨 윗장의 위치",
    "  for (i = 1; i <= n; i++) {              // 카드 a[i]를 뽑는다",
    "    lo = 1;  hi = piles + 1;              // a[top[k]] >= a[i]인 가장 왼쪽 k",
    "    while (lo < hi) {                     // 맨 윗장은 왼쪽→오른쪽 증가 → 이분검색",
    "      mid = (lo + hi) / 2;",
    "      if (a[top[mid]] >= a[i]) hi = mid;",
    "      else lo = mid + 1;",
    "    }",
    "    k = lo;",
    "    back[i] = (k > 1) ? top[k-1] : 0;    // 왼쪽 더미 맨 윗장을 가리킨다",
    "    if (k == piles + 1) piles++;          // 올릴 곳이 없으면 새 더미",
    "    top[k] = i;                           // 더미 k 위에 a[i]를 올린다",
    "  }",
    "  return piles;                          // top[piles]에서 back을 따라가면 수열",
    "}",
]


def dur(sec):
    if sec < 60:
        return f"{sec:.1f}초"
    if sec < 3600:
        return f"{sec / 60:.0f}분"
    return f"{sec / 3600:.0f}시간"


def bench_table():
    rows = json.load(open(os.path.join(HERE, "..", "analysis", "bench.json")))
    r = [x for x in rows if x["shape"] == "random"]
    tr = "".join(
        f"<tr><td>{x['n']:,}</td><td>{x['L']}</td><td>{2 * math.sqrt(x['n']):.0f}</td><td>{x['dp_comps']:,}</td>"
        f"<td>{x['pat_comps']:,}</td><td>{x['dp_comps'] / x['pat_comps']:.0f}배</td>"
        f"<td>{x['dp_t'] * 1000:,.1f}</td><td>{x['pat_t'] * 1000:,.2f}</td></tr>" for x in r)
    big = [x for x in rows if x["shape"] == "random_big"]
    ref = r[-1]
    ns = ref["dp_t"] / ref["dp_comps"] * 1e9
    tb = "".join(
        f"<tr><td>{x['n']:,}</td><td>{x['L']:,}</td><td>{2 * math.sqrt(x['n']):,.0f}</td>"
        f"<td>{x['n'] * (x['n'] - 1) // 2:.2e}</td><td>{x['pat_comps']:,}</td>"
        f"<td>약 {dur(x['n'] * (x['n'] - 1) / 2 * ns / 1e9)} (추정)</td><td>{x['pat_t']:.3f}초</td></tr>" for x in big)
    shapes = [x for x in rows if x["n"] == 8000 and x["shape"] in ("ascending", "random", "descending")]
    name = {"ascending": "오름차순", "random": "무작위", "descending": "내림차순"}
    ts = "".join(
        f"<tr><td>{name[x['shape']]}</td><td>{x['L']:,}</td><td>{x['dp_comps']:,}</td><td>{x['pat_comps']:,}</td>"
        f"<td>{x['pat_comps'] / x['n']:.2f}</td><td>{x['n'] * math.ceil(math.log2(x['L'] + 1)):,}</td></tr>" for x in shapes)
    return tr, tb, ts, ns


def build():
    dp_cells = "".join(
        f'<figure class="step"><figcaption class="sn">i = {i} &nbsp; a[{i}] = {A[i - 1]}</figcaption>{dp_frame(i)}<p>{dp_caption(i)}</p></figure>'
        for i in range(1, N + 1))
    pat_cells = "".join(
        f'<figure class="step{" key" if f["key"] else ""}"><figcaption class="sn">카드 {f["i"]} &nbsp; a[{f["i"]}] = {f["x"]}'
        f'{" &nbsp;<span class=tag>핵심 장면</span>" if f["key"] else ""}</figcaption>{f["svg"]}<p>{f["cap"]}</p></figure>'
        for f in pat_frames())
    final = PAT["steps"][-1]
    final_svg = pile_svg(final["piles"], final["back"], path=final["path"], arrows="path")
    real_svg, fake_svg = counterfactual()
    tr, tb, ts, ns = bench_table()
    dp_path = " ← ".join(f"a[{p}]={A[p - 1]}" for p in reversed(DP["path"]))
    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    rep = {
        "{{STUDENT_ID}}": esc(INFO["student_id"]), "{{NAME}}": esc(INFO["name"]), "{{SECTION}}": esc(INFO["section"]),
        "{{WEB}}": WEB, "{{REPO}}": REPO,
        "{{A}}": ", ".join(map(str, A)),
        "{{DP_CELLS}}": dp_cells, "{{PAT_CELLS}}": pat_cells,
        "{{DP_CODE}}": code_block(DP_CODE), "{{PAT_CODE}}": code_block(PAT_CODE),
        "{{FINAL_SVG}}": final_svg, "{{REAL_SVG}}": real_svg, "{{FAKE_SVG}}": fake_svg,
        "{{DP_PATH}}": dp_path, "{{DP_COMPS}}": str(DP["comps"]), "{{PAT_COMPS}}": str(PAT["comps"]),
        "{{BENCH_ROWS}}": tr, "{{BIG_ROWS}}": tb, "{{SHAPE_ROWS}}": ts, "{{NS}}": f"{ns:.0f}",
    }
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    assert "{{" not in tpl, tpl[tpl.index("{{") - 40: tpl.index("{{") + 40]
    open(os.path.join(HERE, "report.html"), "w", encoding="utf-8").write(tpl)
    print("report.html written")


if __name__ == "__main__":
    build()
