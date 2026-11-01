// 최장 증가 부분수열(LIS) — DP O(n^2) vs 페이션스 정렬 O(n log n)
// analysis/lis.py 와 단계·문장까지 똑같이 나오도록 옮긴 코드 (analysis/parity_test.js 로 대조한다).
// 인덱스는 1부터 센다(a[1..n]).

const pos = (i) => `a[${i}]`;

// 숫자 뒤 조사: 숫자를 읽는 소리 기준(3=삼, 10=십, 2=이 …)
const BATCHIM = { 0: true, 1: "ㄹ", 2: false, 3: true, 4: false, 5: false, 6: true, 7: "ㄹ", 8: "ㄹ", 9: false };
function final(x) {
  const t = String(x).replace(/^[-−]+/, "");
  if (t.length > 1 && t.endsWith("0")) return true;
  return BATCHIM[t[t.length - 1]];
}
const eul = (x) => `${x}` + (final(x) ? "을" : "를");
const eun = (x) => `${x}` + (final(x) ? "은" : "는");
const iga = (x) => `${x}` + (final(x) ? "이" : "가");
const ro = (x) => `${x}` + (final(x) === true ? "으로" : "로");
const pp = (x, a, b) => (final(x) ? a : b);
const ida = (x) => `${x}` + (final(x) ? "이라서" : "라서");

function lisDpTrace(a) {
  const n = a.length;
  const A = [null, ...a];
  const dp = new Array(n + 1).fill(null);
  const prev = new Array(n + 1).fill(null);
  const steps = [];
  let comps = 0;
  const snap = (kind, msg, extra = {}) =>
    steps.push({ kind, msg, dp: dp.slice(1), prev: prev.slice(1), comps, ...extra });

  snap("init", `dp[i] = '${pos("i")}로 끝나는' 가장 긴 증가 부분수열의 길이. ` +
    `왼쪽 칸부터 하나씩 채운다. 칸 i를 채울 때는 왼쪽 칸 1..i−1만 보면 된다.`);
  for (let i = 1; i <= n; i++) {
    dp[i] = 1; prev[i] = null;
    snap("start", `i = ${i}: ${pos(i)} = ${A[i]}. 일단 ${A[i]} 혼자만으로도 길이 1이므로 dp[${i}] = 1로 시작한다.`, { i });
    for (let j = 1; j < i; j++) {
      comps++;
      if (A[j] < A[i]) {
        if (dp[j] + 1 > dp[i]) {
          const old = dp[i];
          dp[i] = dp[j] + 1; prev[i] = j;
          snap("update", `j = ${j}: ${A[j]} < ${A[i]} 이므로 ${ro(A[j])} 끝나는 수열(길이 ${dp[j]}) 뒤에 ` +
            `${eul(A[i])} 붙일 수 있다. ${dp[j]} + 1 = ${dp[i]} > ${old} → dp[${i}] = ${dp[i]}, ` +
            `앞 원소는 a[${j}].`, { i, j });
        } else {
          snap("noupdate", `j = ${j}: ${A[j]} < ${ida(A[i])} 붙일 수는 있지만 ${dp[j]} + 1 = ${dp[j] + 1} ≤ ${dp[i]} 로 ` +
            `지금보다 길어지지 않는다. 그대로 둔다.`, { i, j });
        }
      } else {
        snap("nolink", `j = ${j}: ${A[j]} ≥ ${A[i]} 이므로 ${A[j]} 뒤에 ${eul(A[i])} 붙이면 증가가 아니다. 건너뛴다.`, { i, j });
      }
    }
    snap("fixed", `dp[${i}] = ${dp[i]} 확정. ` +
      (prev[i] ? `(a[${prev[i]}] = ${A[prev[i]]} 뒤에 붙인 것)` : "(앞에 붙일 수 있는 원소가 없었다)"), { i });
  }
  let best = 1;
  for (let k = 2; k <= n; k++) if (dp[k] > dp[best]) best = k;      // 최댓값 중 가장 앞
  const path = [];
  for (let k = best; k; k = prev[k]) path.push(k);
  path.reverse();
  snap("answer", `dp 중 최댓값은 dp[${best}] = ${dp[best]}. 여기서 prev를 거꾸로 따라가면 ` +
    `${[...path].reverse().map(pos).join(" ← ")} → 수열 ` +
    `${path.map((p) => A[p]).join(", ")} (길이 ${dp[best]}).`, { path, i: best });
  return { length: dp[best], path, seq: path.map((p) => A[p]), steps, comps };
}

function lisPatienceTrace(a) {
  const n = a.length;
  const A = [null, ...a];
  const piles = [];
  const back = new Array(n + 1).fill(null);
  const steps = [];
  let comps = 0;
  const tops = () => piles.map((p) => p[p.length - 1]);
  const snap = (kind, msg, extra = {}) =>
    steps.push({ kind, msg, piles: piles.map((p) => [...p]), back: back.slice(1), comps, ...extra });

  snap("init", "카드를 한 장씩 왼쪽부터 꺼낸다. 규칙: 맨 윗장이 '이 카드 이상'인 더미 중 가장 왼쪽 더미에 올린다. " +
    "그런 더미가 없으면 오른쪽 끝에 새 더미를 만든다.");
  for (let i = 1; i <= n; i++) {
    const x = A[i];
    const T = tops();
    if (T.length) {
      snap("draw", `${pos(i)} = ${x} 카드를 꺼낸다. 지금 맨 윗장은 왼쪽부터 [${T.map((t) => A[t]).join(", ")}]. ` +
        `맨 윗장은 왼쪽에서 오른쪽으로 항상 커지므로, ${eul(x)} 올릴 더미를 이분검색으로 찾는다.`, { i });
    } else {
      snap("draw", `${pos(i)} = ${x} 카드를 꺼낸다. 아직 더미가 하나도 없다.`, { i });
    }
    let lo = 0, hi = T.length;
    while (lo < hi) {
      const mid = Math.floor((lo + hi) / 2);
      comps++;
      if (A[T[mid]] >= x) {
        snap("probe", `이분검색: 더미 ${mid + 1}의 맨 윗장 ${A[T[mid]]} ≥ ${x} → 답은 더미 ${mid + 1} 이하. 왼쪽 절반을 본다.`,
          { i, probe: mid, lo, hi });
        hi = mid;
      } else {
        snap("probe", `이분검색: 더미 ${mid + 1}의 맨 윗장 ${A[T[mid]]} < ${x} → ${eun(x)} 여기 못 올라간다. 오른쪽 절반을 본다.`,
          { i, probe: mid, lo, hi });
        lo = mid + 1;
      }
    }
    const k = lo;
    back[i] = k > 0 ? T[k - 1] : null;
    const b = back[i];
    const link = b
      ? `놓는 순간 왼쪽 더미 맨 윗장 ${A[b]}(${pos(b)})${pp(A[b], "을", "를")} 가리키는 화살표를 남긴다 ` +
        `(${A[b]} < ${x} 이므로 ${A[b]} 다음에 ${iga(x)} 올 수 있다).`
      : "가장 왼쪽 더미라서 가리킬 카드가 없다(수열의 첫 원소 후보).";
    if (k === piles.length) {
      piles.push([i]);
      snap("newpile", `${x}보다 크거나 같은 맨 윗장이 없다 → 오른쪽 끝에 새 더미 ${eul(k + 1)} 만든다. ` +
        `더미가 ${piles.length}개가 됐다 = 지금까지 길이 ${piles.length}짜리 증가 수열을 만들 수 있다는 뜻. ${link}`,
        { i, pile: k });
    } else {
      const covered = A[piles[k][piles[k].length - 1]];
      piles[k].push(i);
      snap("place", `더미 ${k + 1}(맨 윗장 ${covered})에 ${eul(x)} 올린다. 더미 ${k + 1}의 맨 윗장은 ` +
        `'길이 ${k + 1}짜리 증가 수열이 끝날 수 있는 가장 작은 값'이다. ${ro(covered)} 끝나는 것보다 ` +
        `${ro(x)} 끝나는 쪽이 뒤에 더 많은 수를 붙일 수 있으니 ${ro(x)} 바꿔 둔다. ${link}`, { i, pile: k });
    }
  }
  const L = piles.length;
  const path = [];
  for (let t = piles[L - 1][piles[L - 1].length - 1]; t; t = back[t]) path.push(t);
  path.reverse();
  const T = tops();
  let note = "";
  let bad = -1;
  for (let k = 0; k < T.length - 1; k++) if (T[k] > T[k + 1]) { bad = k; break; }
  if (bad >= 0) {
    const x = T[bad], y = T[bad + 1];
    note = ` 주의: 마지막 맨 윗장들 [${T.map((t) => A[t]).join(", ")}]은 증가하는 것처럼 보이지만 답이 아니다. ` +
      `${A[x]}(${pos(x)})${pp(A[x], "은", "는")} ${A[y]}(${pos(y)})보다 뒤에 나온 수라서 이 순서로 뽑을 수 없다. ` +
      `그래서 맨 윗장이 아니라 화살표를 따라가야 한다.`;
  }
  snap("answer", `더미가 ${L}개 → LIS 길이는 ${L}. 마지막 더미의 맨 윗장에서 화살표를 거꾸로 따라가면 ` +
    `${path.map((p) => A[p]).join(", ")}.${note}`, { path });
  return { length: L, path, seq: path.map((p) => A[p]), steps, comps };
}

const PRESETS = {
  basic: { label: "기본 예제", a: [10, 3, 11, 5, 8, 6, 1, 2, 7],
           note: "답은 3, 5, 6, 7 하나뿐. 8 위에 6을 올려 둔 덕분에 마지막 7이 새 더미를 만든다." },
  asc: { label: "이미 정렬됨", a: [1, 2, 3, 4, 5, 6, 7, 8],
         note: "카드마다 새 더미가 생긴다. 페이션스가 가장 많이 비교하는 경우." },
  desc: { label: "거꾸로 정렬됨", a: [8, 7, 6, 5, 4, 3, 2, 1],
          note: "모든 카드가 한 더미에 쌓인다. 답은 길이 1. 페이션스는 한 장당 비교 1번." },
  dup: { label: "같은 수 포함", a: [3, 5, 3, 5, 4, 6, 4, 7],
         note: "'엄격히 증가'라서 같은 수는 이어 붙일 수 없다. 같은 수는 같은 더미에 쌓인다." },
};

const api = { lisDpTrace, lisPatienceTrace, PRESETS, eul };
if (typeof module !== "undefined") module.exports = api;
else window.LIS = api;
