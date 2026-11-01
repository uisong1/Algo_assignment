// node analysis/parity_test.js <parity.json> : JS 구현이 Python 구현과 단계까지 같은지 대조
const SP = require("../docs/algo.js");
const cases = require(process.argv[2]);
const norm = (o) => JSON.parse(JSON.stringify(o, (k, v) => (v === Infinity ? "INF" : v)));
let bad = 0;
for (const c of cases) {
  const e = c.edges.map(([u, v, w]) => [u, v, w]);
  if (SP.EXAMPLES[c.name]) {   // 웹앱 예제 정의가 Python 예제와 같은지도 확인
    const ex = SP.EXAMPLES[c.name];
    if (JSON.stringify(ex.edges) !== JSON.stringify(e) || JSON.stringify(ex.vertices) !== JSON.stringify(c.vertices)) {
      bad++; console.log("example definition differs:", c.name);
    }
  }
  for (const [key, f] of [["dij", SP.dijkstraTrace], ["bf", SP.bellmanFordTrace]]) {
    const js = JSON.stringify(norm(f(c.vertices, e, c.src)));
    const py = JSON.stringify(c[key]);
    if (js !== py) {
      bad++;
      if (bad < 4) {
        const a = norm(f(c.vertices, e, c.src)).steps, b = c[key].steps;
        const i = a.findIndex((s, j) => JSON.stringify(s) !== JSON.stringify(b[j]));
        console.log("MISMATCH", c.name, key, "step", i, "\n js:", JSON.stringify(a[i]), "\n py:", JSON.stringify(b[i]));
      }
    }
  }
}
console.log(`${cases.length} cases x 2 algorithms, mismatches: ${bad}`);
process.exit(bad ? 1 : 0);
