"""벤치마크 차트 2장 (보고서용 PNG)."""
import json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

fm.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
fm.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
plt.rcParams["font.family"] = "Noto Sans CJK JP"
rows = json.load(open("bench.json"))
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"       # 검증된 범주형 팔레트 1~3번
SURF, INK, INK2, GRID = "#fcfcfb", "#1b1b1a", "#52514e", "#e6e5e1"


def style(ax, title):
    ax.set_facecolor(SURF)
    ax.set_title(title, loc="left", fontsize=12, color=INK, fontweight="bold", pad=10)
    ax.grid(True, color=GRID, lw=0.8); ax.minorticks_off()
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]: ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8)


def line(ax, xs, ys, c, label, ls="-"):
    ax.plot(xs, ys, ls, color=c, lw=2, marker="o", ms=5, markeredgecolor=SURF, markeredgewidth=1.5)
    ax.annotate(label, (xs[-1], ys[-1]), xytext=(8, 0), textcoords="offset points", va="center", fontsize=9, color=INK)


rnd = [r for r in rows if r["shape"] == "random"]
N = [r["n"] for r in rnd]

# 1) 비교 횟수: DP vs 페이션스 (무작위 입력)
fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200); fig.patch.set_facecolor(SURF)
line(ax, N, [r["dp_comps"] for r in rnd], S2, "DP  O(n²)")
line(ax, N, [r["pat_comps"] for r in rnd], S1, "페이션스  O(n log n)")
ax.set_xscale("log", base=2); ax.set_yscale("log")
ax.set_xticks(N); ax.set_xticklabels([f"{v:,}" for v in N])
last = rnd[-1]
ax.annotate(f"{last['dp_comps'] / last['pat_comps']:,.0f}배 차이", xy=(last["n"], math.sqrt(last["dp_comps"] * last["pat_comps"])),
            xytext=(-62, 0), textcoords="offset points", fontsize=9, color=INK2, va="center")
ax.vlines(last["n"], last["pat_comps"] * 1.25, last["dp_comps"] / 1.25, color=INK2, lw=0.8)
ax.set_xlabel("수열 길이 n (무작위 수열)", color=INK2, fontsize=9)
ax.set_ylabel("비교 횟수 (로그 눈금)", color=INK2, fontsize=9)
style(ax, "n이 2배가 될 때: DP는 4배, 페이션스는 약 2배")
ax.set_xlim(N[0] / 1.3, N[-1] * 3.2)
fig.text(0.01, 0.01, "같은 수열에 두 방법 실행. DP 비교 = a[j] < a[i], 페이션스 비교 = 이분검색의 맨 윗장 비교",
         fontsize=7, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("bench_comps.png", facecolor=SURF); plt.close(fig)

# 2) 페이션스: 입력 형태별 '카드 한 장당 비교 횟수'
fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=200); fig.patch.set_facecolor(SURF)
for shape, c, lab in [("ascending", S2, "오름차순 (더미 n개)"), ("random", S1, "무작위 (더미 ≈ 2√n개)"),
                      ("descending", S3, "내림차순 (더미 1개)")]:
    rs = [r for r in rows if r["shape"] == shape]
    line(ax, [r["n"] for r in rs], [r["pat_comps"] / r["n"] for r in rs], c, lab)
ax.set_xscale("log", base=2)
ax.set_xticks(N); ax.set_xticklabels([f"{v:,}" for v in N])
ax.set_ylim(0, 12)
ax.set_xlabel("수열 길이 n", color=INK2, fontsize=9)
ax.set_ylabel("카드 한 장당 평균 비교 횟수", color=INK2, fontsize=9)
style(ax, "페이션스는 더미 수 L에 따라 달라진다: 한 장당 약 log L번")
ax.set_xlim(N[0] / 1.3, N[-1] * 4.2)
fig.text(0.01, 0.01, "DP는 세 경우 모두 비교 횟수가 똑같이 n(n−1)/2 (모든 경우 분석)", fontsize=7, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("bench_shape.png", facecolor=SURF); plt.close(fig)
print("ok")
