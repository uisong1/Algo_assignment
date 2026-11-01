// 사용법: node analysis/parity_test.js <parity.json>
// 웹(docs/lis.js)이 Python(analysis/lis.py)과 모든 단계에서 똑같은지 대조한다.
const LIS = require("../docs/lis.js");
const cases = require(require("path").resolve(process.argv[2]));
let bad = 0;
for (const c of cases) {
  for (const [key, f] of [["dp", LIS.lisDpTrace], ["pat", LIS.lisPatienceTrace]]) {
    const js = f(c.a), py = c[key];
    if (JSON.stringify(js) !== JSON.stringify(py)) {
      bad++;
      if (bad <= 3) {
        const i = js.steps.findIndex((s, k) => JSON.stringify(s) !== JSON.stringify(py.steps[k]));
        console.log("MISMATCH", key, JSON.stringify(c.a), "step", i, "\n js:", JSON.stringify(js.steps[i]), "\n py:", JSON.stringify(py.steps[i]));
      }
    }
  }
}
// 화면의 예제 설명이 실제 결과와 맞는지도 확인
const b = LIS.lisPatienceTrace(LIS.PRESETS.basic.a);
if (b.seq.join() !== "3,5,6,7") { bad++; console.log("basic preset answer changed:", b.seq); }
console.log(`${cases.length} cases x 2 algorithms, mismatches: ${bad}`);
process.exit(bad ? 1 : 0);
