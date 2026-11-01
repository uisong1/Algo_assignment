// Dijkstra vs Bellman-Ford — 단계 기록(trace) 생성.
// analysis/sp.py 와 단계·문장까지 똑같이 나오도록 옮긴 코드다 (analysis/parity_test.mjs 로 대조).

const INF = Infinity;

function fmt(x) {
  if (x === INF) return "∞";
  return String(x).replace("-", "−");
}
const wfmt = (w) => (w < 0 ? `(${fmt(w)})` : fmt(w));

// 숫자 뒤 조사: 받침 있으면 '으로/이', 없거나 ㄹ이면 '로/가'
const BATCHIM = { 0: true, 1: "ㄹ", 2: false, 3: true, 4: false, 5: false, 6: true, 7: "ㄹ", 8: "ㄹ", 9: false };
function last(x) {
  let t = fmt(x);
  if (t === "∞") return false;
  t = t.replace(/^−/, "");
  if (t.length > 1 && t.endsWith("0")) return true;
  return BATCHIM[t[t.length - 1]];
}
const ro = (x) => fmt(x) + (last(x) === true ? "으로" : "로");
const iga = (x) => { const b = last(x); return fmt(x) + (b === true || b === "ㄹ" ? "이" : "가"); };

function dijkstraTrace(vertices, edges, src) {
  const adj = Object.fromEntries(vertices.map((v) => [v, []]));
  for (const [u, v, w] of edges) adj[u].push([v, w]);
  const dist = Object.fromEntries(vertices.map((v) => [v, INF]));
  const prev = Object.fromEntries(vertices.map((v) => [v, null]));
  const done = new Set();
  dist[src] = 0;
  const steps = [];
  let relaxChecks = 0;
  const snap = (kind, msg, extra = {}) =>
    steps.push({ kind, msg, dist: { ...dist }, prev: { ...prev },
                 done: vertices.filter((v) => done.has(v)), ...extra });

  snap("init", `출발점 ${src}의 거리를 0, 나머지는 ∞로 둔다. 아직 확정된 정점은 없다.`);
  while (done.size < vertices.length) {
    const cand = vertices.filter((v) => !done.has(v) && dist[v] < INF);
    if (cand.length === 0) {
      const rest = vertices.filter((v) => !done.has(v));
      snap("stop", `남은 정점 ${rest.join(", ")}은(는) 도달할 수 없다(∞). 종료.`);
      break;
    }
    let u = cand[0];
    for (const v of cand) if (dist[v] < dist[u]) u = v; // 동점이면 앞 정점
    done.add(u);
    const others = vertices.filter((v) => !done.has(v) && dist[v] < INF).map((v) => `${v}=${fmt(dist[v])}`);
    const cmp = others.length ? `(다른 후보: ${others.join(", ")})` : "";
    snap("select", `확정 안 된 정점 중 거리가 가장 작은 ${u}(${fmt(dist[u])})를 꺼내 확정한다${cmp}. ` +
      `간선이 모두 양수라면 더 먼 후보를 거쳐 돌아와도 ${fmt(dist[u])}보다 짧아질 수 없기 때문이다.`, { node: u });
    for (const [v, w] of adj[u]) {
      relaxChecks++;
      if (done.has(v)) {
        if (dist[u] + w < dist[v]) {
          snap("missed", `${u}→${v}(${fmt(w)}): ${fmt(dist[u])} + ${wfmt(w)} = ${fmt(dist[u] + w)} < ${fmt(dist[v])} 로 ` +
            `실제로는 더 짧은 길이다. 하지만 ${v}는 이미 확정됐고 Dijkstra는 확정을 되돌리지 않는다. ` +
            `→ ${v}의 거리 ${fmt(dist[v])}는 틀린 값으로 남고, ${v}를 거쳐 계산된 다른 정점도 함께 틀린다. ` +
            `(음수 간선이 '확정 = 최단'이라는 전제를 깨뜨렸다)`, { edge: [u, v], node: u, wrong: v });
        } else {
          snap("skip", `${u}→${v}(${fmt(w)}): ${v}는 이미 확정됐으므로 다시 보지 않는다.`, { edge: [u, v], node: u });
        }
        continue;
      }
      const nw = dist[u] + w;
      if (nw < dist[v]) {
        const old = dist[v];
        dist[v] = nw;
        prev[v] = u;
        snap("relax", `${u}→${v}(${fmt(w)}): ${fmt(dist[u])} + ${wfmt(w)} = ${fmt(nw)} < ${fmt(old)} 이므로 ` +
          `${v}의 거리를 ${ro(nw)} 줄인다(직전 정점 ${u}).`, { edge: [u, v], node: u, updated: v });
      } else {
        snap("norelax", `${u}→${v}(${fmt(w)}): ${fmt(dist[u])} + ${wfmt(w)} = ${fmt(nw)} ≥ ${fmt(dist[v])} 이므로 그대로 둔다.`,
          { edge: [u, v], node: u });
      }
    }
  }
  snap("end", "모든 정점을 확정했다. 표의 값이 Dijkstra의 결과다.");
  return { dist, prev, steps, relax_checks: relaxChecks };
}

function bellmanFordTrace(vertices, edges, src) {
  const dist = Object.fromEntries(vertices.map((v) => [v, INF]));
  const prev = Object.fromEntries(vertices.map((v) => [v, null]));
  dist[src] = 0;
  const steps = [];
  let relaxChecks = 0;
  const n = vertices.length;
  const snap = (kind, msg, extra = {}) => steps.push({ kind, msg, dist: { ...dist }, prev: { ...prev }, ...extra });

  snap("init", `출발점 ${src}의 거리를 0, 나머지는 ∞로 둔다. 모든 간선을 최대 V−1 = ${n - 1}번 훑는다.`);
  let roundsUsed = 0;
  for (let r = 1; r < n; r++) {
    let changed = false;
    snap("round", `라운드 ${r} 시작: 간선 ${edges.length}개를 순서대로 모두 검사한다. ` +
      `라운드 ${iga(r)} 끝나면 간선 ${r}개 이하로 가는 최단거리가 확정된다.`, { round: r });
    for (const [u, v, w] of edges) {
      relaxChecks++;
      if (dist[u] === INF) {
        snap("norelax", `${u}→${v}(${fmt(w)}): ${u}에 아직 도달하지 못했다(∞). 건너뛴다.`, { edge: [u, v], round: r });
        continue;
      }
      const nw = dist[u] + w;
      if (nw < dist[v]) {
        const old = dist[v];
        dist[v] = nw;
        prev[v] = u;
        changed = true;
        snap("relax", `${u}→${v}(${fmt(w)}): ${fmt(dist[u])} + ${wfmt(w)} = ${fmt(nw)} < ${fmt(old)} 이므로 ` +
          `${v}의 거리를 ${ro(nw)} 줄인다.`, { edge: [u, v], round: r, updated: v });
      } else {
        snap("norelax", `${u}→${v}(${fmt(w)}): ${fmt(dist[u])} + ${wfmt(w)} = ${fmt(nw)} ≥ ${fmt(dist[v])} 이므로 그대로 둔다.`,
          { edge: [u, v], round: r });
      }
    }
    roundsUsed = r;
    if (!changed) {
      snap("early", `라운드 ${r}에서 바뀐 값이 하나도 없다. 더 돌려도 변하지 않으므로 조기 종료한다.`, { round: r });
      break;
    }
  }
  let negCycle = false;
  if (roundsUsed === n - 1) {
    snap("check", `V−1 = ${n - 1}번을 다 돌았다. 음수 사이클이 있는지 간선을 한 번 더 검사한다.`);
    for (const [u, v, w] of edges) {
      relaxChecks++;
      if (dist[u] < INF && dist[u] + w < dist[v]) {
        negCycle = true;
        snap("negcycle", `${u}→${v}(${fmt(w)}): ${fmt(dist[u])} + ${wfmt(w)} = ${fmt(dist[u] + w)} < ${fmt(dist[v])} — ` +
          `V−1번 뒤에도 또 줄어든다. 단순 경로는 간선이 최대 V−1개이므로, ` +
          `이는 음수 사이클이 있다는 뜻이다. 최단거리가 정의되지 않는다.`, { edge: [u, v] });
        break;
      }
    }
    if (!negCycle) snap("ok", "더 줄어드는 간선이 없다. 음수 사이클이 없으므로 결과가 확정됐다.");
  }
  if (!negCycle) snap("end", "Bellman-Ford 종료. 표의 값이 최단거리다.");
  return { dist, prev, steps, relax_checks: relaxChecks, rounds: roundsUsed, neg_cycle: negCycle };
}

const EXAMPLES = {
  normal: {
    title: "일반 그래프",
    note: "가중치가 모두 양수. 두 알고리즘 모두 정답을 내지만 일하는 양이 다르다.",
    vertices: ["A", "B", "C", "D", "E", "F"], src: "A",
    edges: [["B", "D", 5], ["D", "F", 6], ["E", "F", 2], ["C", "E", 10], ["D", "E", 2],
            ["A", "B", 4], ["C", "D", 8], ["A", "C", 2], ["C", "B", 1]],
    pos: { A: [60, 200], B: [230, 80], C: [230, 320], D: [420, 80], E: [420, 320], F: [590, 200] },
  },
  negative: {
    title: "음수 간선",
    note: "C→B가 −3. 사이클은 없어서 최단거리는 존재하지만, Dijkstra는 틀린 답을 낸다.",
    vertices: ["A", "B", "C", "D", "E"], src: "A",
    edges: [["A", "B", 2], ["A", "C", 4], ["B", "D", 3], ["C", "B", -3], ["D", "E", 1]],
    pos: { A: [60, 200], B: [260, 90], C: [260, 310], D: [450, 90], E: [600, 200] },
  },
  negcycle: {
    title: "음수 사이클",
    note: "B→C→D→B를 한 바퀴 돌면 2 + 1 − 4 = −1. 돌수록 짧아져서 최단거리가 없다.",
    vertices: ["A", "B", "C", "D", "E"], src: "A",
    edges: [["A", "B", 3], ["B", "C", 2], ["C", "D", 1], ["D", "B", -4], ["C", "E", 2]],
    pos: { A: [60, 200], B: [240, 200], C: [420, 90], D: [420, 310], E: [600, 90] },
  },
};

const api = { INF, fmt, dijkstraTrace, bellmanFordTrace, EXAMPLES };
if (typeof module !== "undefined") module.exports = api;
else window.SP = api;
