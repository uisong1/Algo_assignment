import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fm.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
plt.rcParams["font.family"] = "Noto Sans CJK JP"
rows = json.load(open("bench.json"))
sp = [r for r in rows if r["exp"] == "sparse"]
S = dict(blue="#2a78d6", orange="#eb6834", aqua="#1baf7a")
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e1"

fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
fig.patch.set_facecolor("#fcfcfb"); ax.set_facecolor("#fcfcfb")
def line(xs, ys, c, label, ls="-"):
    ax.plot(xs, ys, ls, color=c, lw=2, marker="o", ms=5, markeredgecolor="#fcfcfb", markeredgewidth=1.5)
    ax.annotate(label, (xs[-1], ys[-1]), xytext=(8, 0), textcoords="offset points",
                va="center", fontsize=9, color=INK)
V = [r["V"] for r in sp]
line(V, [r["dh_t"]*1000 for r in sp], S["blue"], "Dijkstra (힙)")
line(V, [r["bf_t"]*1000 for r in sp], S["aqua"], "Bellman-Ford\n(조기 종료)")
vf = [r for r in sp if r["bf_full_t"]]
line([r["V"] for r in vf], [r["bf_full_t"]*1000 for r in vf], S["orange"], "Bellman-Ford\n(V−1 라운드 전부)", "--")
ax.set_xscale("log", base=2); ax.set_yscale("log")
ax.set_xticks(V); ax.set_xticklabels([f"{v:,}" for v in V])
ax.set_xlabel("정점 수 V  (간선 E = 4V, 무작위 방향 그래프)", color=INK2, fontsize=9)
ax.set_ylabel("실행 시간 (ms, 로그 눈금)", color=INK2, fontsize=9)
ax.set_title("희소 그래프에서 V에 따른 실행 시간", loc="left", fontsize=12, color=INK, fontweight="bold")
ax.grid(True, which="major", color=GRID, lw=0.8); ax.minorticks_off()
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color(GRID)
ax.tick_params(colors=INK2, labelsize=8)
ax.set_xlim(80, 3200*2.6)
fig.text(0.01, 0.01, "Python 3.13, 같은 그래프에 세 방법 실행 · 각 점은 최소 시간", fontsize=7, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("bench_time.png", facecolor=fig.get_facecolor())
