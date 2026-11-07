// 화면 그리기와 조작. 알고리즘과 설명 문장은 lis.js에 있다.
(() => {
  const { lisDpTrace, lisPatienceTrace, PRESETS, eul } = window.LIS;
  const $ = (id) => document.getElementById(id);
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const DP_CODE = [
    ["LIS_DP(a[1..n])", ""],
    ["  for i = 1 to n", ""],
    ["    dp[i] = 1;  prev[i] = 0", "  // a[i] 혼자서 길이 1"],
    ["    for j = 1 to i − 1", ""],
    ["      if a[j] < a[i] and dp[j] + 1 > dp[i]", ""],
    ["        dp[i] = dp[j] + 1;  prev[i] = j", ""],
    ["  best = dp가 가장 큰 위치", ""],
    ["  return dp[best]", "  // prev를 거꾸로 따라가 수열 복원"],
  ];
  const DP_LINE = { init: 0, start: 2, nolink: 4, noupdate: 4, update: 5, fixed: 3, answer: 7 };

  const PAT_CODE = [
    ["LIS_Patience(a[1..n])", ""],
    ["  piles = 0", ""],
    ["  for i = 1 to n", "                  // 카드 a[i]를 뽑는다"],
    ["    k = 이분검색: a[top[k]] ≥ a[i]인 가장 왼쪽 더미", ""],
    ["    back[i] = (k > 1) ? top[k − 1] : 0", "   // 왼쪽 더미 맨 윗장"],
    ["    if k == piles + 1:  piles = piles + 1", "  // 새 더미"],
    ["    top[k] = i", "                    // 더미 k 위에 올림"],
    ["  return piles", "                    // top[piles]부터 back을 따라 복원"],
  ];
  const PAT_LINE = { init: 1, draw: 2, probe: 3, newpile: 5, place: 6, answer: 7 };

  const KIND_LABEL = {
    init: "준비", start: "새 칸 시작", update: "비교 → 갱신", noupdate: "비교 → 그대로", nolink: "비교 → 붙일 수 없음",
    fixed: "칸 확정", answer: "답", draw: "카드 뽑기", probe: "이분검색", newpile: "새 더미", place: "기존 더미에 올리기",
  };

  const state = { a: [], dp: null, pat: null, di: 0, pi: 0, timer: null, preset: "basic" };

  // ── 입력 ──
  function buildPresets() {
    const box = document.querySelector(".presets");
    for (const [key, p] of Object.entries(PRESETS)) {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = p.label;
      b.dataset.key = key;
      b.addEventListener("click", () => load(p.a, key));
      box.appendChild(b);
    }
  }

  function load(a, presetKey = null) {
    stop();
    state.a = a.slice();
    state.dp = lisDpTrace(state.a);
    state.pat = lisPatienceTrace(state.a);
    state.di = 0; state.pi = 0; state.preset = presetKey;
    document.querySelectorAll(".presets button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.key === presetKey)));
    $("seqLabel").textContent = `입력 수열 · ${state.a.length}개`;
    $("seqView").innerHTML = state.a.map((v) => `<span>${v}</span>`).join("");
    $("presetNote").textContent = presetKey ? PRESETS[presetKey].note : "직접 입력한 수열이에요.";
    $("customInput").value = presetKey ? "" : state.a.join(", ");
    $("formMsg").textContent = "";
    try { history.replaceState(null, "", "#a=" + state.a.join(",")); } catch (e) { /* 파일로 열었을 때 */ }
    renderAll();
  }

  function parseInput(text) {
    const parts = text.split(/[\s,]+/).filter(Boolean);
    if (!parts.length) return { err: "숫자를 1개 이상 입력하세요." };
    if (parts.length > 10) return { err: `최대 10개까지 입력할 수 있어요. 지금 ${parts.length}개예요.` };
    const a = [];
    for (const p of parts) {
      if (!/^-?\d+$/.test(p)) return { err: `정수만 입력할 수 있어요: '${p}'` };
      const v = Number(p);
      if (v < -99 || v > 999) return { err: `카드에 들어갈 수 있게 −99 ~ 999 사이로 입력하세요: ${p}` };
      a.push(v);
    }
    return { a };
  }

  $("customForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const r = parseInput($("customInput").value);
    if (r.err) { $("formMsg").textContent = r.err; return; }
    const hit = Object.entries(PRESETS).find(([, p]) => p.a.join() === r.a.join());
    load(r.a, hit ? hit[0] : null);
  });

  // ── 진행 ──
  const dpEnd = () => state.di >= state.dp.steps.length - 1;
  const patEnd = () => state.pi >= state.pat.steps.length - 1;

  function step(pane, dir) {
    if (pane === "dp") state.di = clamp(state.di + dir, 0, state.dp.steps.length - 1);
    else state.pi = clamp(state.pi + dir, 0, state.pat.steps.length - 1);
  }
  const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));

  function go(dir, pane = "both") {
    const before = { di: state.di, pi: state.pi };
    if (pane !== "pat") step("dp", dir);
    if (pane !== "dp") step("pat", dir);
    renderAll({ forward: dir > 0, patMoved: state.pi !== before.pi });
  }

  function play() {
    if (state.timer) { stop(); return; }
    if (dpEnd() && patEnd()) { state.di = 0; state.pi = 0; renderAll(); }
    $("btnPlay").textContent = "일시정지";
    const tick = () => {
      if (dpEnd() && patEnd()) { stop(); return; }
      go(1);
      state.timer = setTimeout(tick, Number($("speed").value));
    };
    state.timer = setTimeout(tick, 200);
  }
  function stop() {
    clearTimeout(state.timer); state.timer = null;
    $("btnPlay").textContent = "자동 재생";
  }

  $("btnNext").addEventListener("click", () => { stop(); go(1); });
  $("btnPrev").addEventListener("click", () => { stop(); go(-1); });
  $("btnPlay").addEventListener("click", play);
  $("btnReset").addEventListener("click", () => { stop(); state.di = 0; state.pi = 0; renderAll(); });
  $("btnEnd").addEventListener("click", () => {
    stop(); state.di = state.dp.steps.length - 1; state.pi = state.pat.steps.length - 1; renderAll();
  });
  document.querySelectorAll(".mini button").forEach((b) =>
    b.addEventListener("click", () => { stop(); go(Number(b.dataset.dir), b.dataset.pane); }));
  document.addEventListener("keydown", (e) => {
    if (e.target.closest("input, select, textarea")) return;
    if (e.key === "ArrowRight") { e.preventDefault(); stop(); go(1); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); stop(); go(-1); }
    else if (e.key === " ") { e.preventDefault(); play(); }
    else if (e.key === "Home") { stop(); state.di = 0; state.pi = 0; renderAll(); }
    else if (e.key === "End") { $("btnEnd").click(); }
  });
  addEventListener("resize", () => drawThreads(state.pat.steps[state.pi]));

  // ── 그리기 ──
  function renderAll(opt = {}) {
    renderDp(state.dp.steps[state.di]);
    renderPat(state.pat.steps[state.pi], opt.forward && opt.patMoved);
    $("btnPrev").disabled = state.di === 0 && state.pi === 0;
    $("btnNext").disabled = dpEnd() && patEnd();
    renderResult();
  }

  function renderCode(el, lines, active) {
    el.innerHTML = lines.map(([code, cmt], k) =>
      `<span class="${k === active ? "on" : ""}">${esc(code)}<em class="c">${esc(cmt)}</em></span>`).join("");
  }
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  // 여백 주석: 번호 · 단계 이름 · 위치 · 설명
  function renderNote(pre, s, ctx) {
    $(pre + "Kind").textContent = KIND_LABEL[s.kind] || "";
    $(pre + "Ctx").textContent = ctx;
    $(pre + "Msg").textContent = s.msg;
    $(pre + "Msg").closest(".note").className = "note k-" + s.kind;
  }
  const FN = (n) => `<span class="fn" aria-hidden="true">${n}</span>`;

  function renderDp(s) {
    const n = state.a.length;
    const onPath = new Set(s.kind === "answer" ? s.path : []);
    const col = (k) => {
      const c = [];
      if (onPath.has(k)) c.push("on-path");
      else if (s.i === k && s.kind !== "answer") c.push("is-i");
      else if (s.j === k) c.push("is-j");
      return c.join(" ");
    };
    let h = `<table class="dp-grid"><thead><tr><th></th>`;
    for (let k = 1; k <= n; k++) {
      const m = s.kind !== "answer" && s.i === k ? `<span class="marker i">i</span>` : s.j === k ? `<span class="marker j">j</span>` : `<span class="marker"></span>`;
      h += `<th>${m}</th>`;
    }
    h += `</tr></thead><tbody><tr class="r-idx"><th>위치</th>`;
    for (let k = 1; k <= n; k++) h += `<th style="text-align:center">${k}</th>`;
    h += `</tr><tr class="r-a"><th>a[i]</th>`;
    for (let k = 1; k <= n; k++) h += `<td class="${col(k)}">${state.a[k - 1]}</td>`;
    h += `</tr><tr class="r-dp"><th>dp[i]</th>`;
    for (let k = 1; k <= n; k++) {
      const v = s.dp[k - 1];
      const mark = s.i === k && v != null && s.kind !== "answer" && s.kind !== "init" ? FN(1) : "";
      h += `<td class="${v == null ? "empty" : col(k)}">${v ?? "·"}${mark}</td>`;
    }
    h += `</tr><tr class="r-prev"><th>prev[i]</th>`;
    for (let k = 1; k <= n; k++) {
      const v = s.dp[k - 1];
      h += `<td class="${v == null ? "empty" : ""}">${v == null ? "·" : s.prev[k - 1] ?? "–"}</td>`;
    }
    h += `</tr></tbody></table>`;
    let cmp = "";
    if (s.j) {
      const aj = state.a[s.j - 1], ai = state.a[s.i - 1];
      cmp = aj < ai
        ? `a[${s.j}] = ${aj} &lt; a[${s.i}] = ${ai} → <span class="yes">이어 붙일 수 있음</span>`
        : `a[${s.j}] = ${aj} ≥ a[${s.i}] = ${ai} → <span class="no">이어 붙일 수 없음</span>`;
    } else if (s.kind === "answer") {
      cmp = `답: <span class="ans">${s.path.map((p) => state.a[p - 1]).join(", ")}</span> (길이 ${s.path.length})`;
    }
    $("dpBoard").innerHTML = h + `<p class="dp-cmp">${cmp}</p>`;
    renderNote("dp", s, s.kind === "answer" ? "I · DP · 답 복원"
      : s.i ? `I · DP · i = ${s.i}` + (s.j ? `, j = ${s.j}` : "") : "I · DP");
    renderCode($("dpCode"), DP_CODE, DP_LINE[s.kind]);
    $("dpCount").textContent = `비교 ${s.comps}번`;
    $("dpStep").textContent = `${state.di + 1} / ${state.dp.steps.length}`;
  }

  const CARD_GAP = 22, LABEL_H = 0, CARD_H = 70, FOOT = 26;

  function cardEl(idx, extra = "", mark = "") {
    return `<div class="card ${extra}" data-idx="${idx}"><small>a[${idx}]</small><b class="v">${state.a[idx - 1]}</b>${mark}</div>`;
  }

  function renderPat(s, animate) {
    // 이동 애니메이션을 위해 그리기 전 '들고 있는 카드' 위치를 기억
    let fromRect = null;
    if (animate && (s.kind === "place" || s.kind === "newpile") && !reduceMotion) {
      const el = document.querySelector(`.deck .card[data-idx="${s.i}"]`);
      if (el) fromRect = el.getBoundingClientRect();
    }
    const placed = new Set(s.piles.flat());
    const holding = (s.kind === "draw" || s.kind === "probe") ? s.i : null;

    // 남은 카드
    let d = "";
    for (let k = 1; k <= state.a.length; k++) {
      const cls = placed.has(k) ? "used" : holding === k ? "drawn" : "";
      d += cardEl(k, cls, holding === k ? FN(2) : "");
    }
    $("deck").innerHTML = d;
    if (holding) {   // 좁은 화면에서도 지금 뽑은 카드가 보이게 덱을 옆으로 민다
      const deck = $("deck"), el = deck.querySelector(`.card[data-idx="${holding}"]`);
      if (el && deck.scrollWidth > deck.clientWidth) deck.scrollLeft = el.offsetLeft - deck.clientWidth / 2;
    }

    // 더미
    const onPath = new Set(s.kind === "answer" ? s.path : []);
    const tops = s.piles.map((p) => p[p.length - 1]);
    let h = "";
    s.piles.forEach((pile, k) => {
      const inRange = s.kind === "probe" ? k >= s.lo && k < s.hi : true;
      const cls = ["pile", s.kind === "probe" && s.probe === k ? "probe" : "", inRange ? "" : "out"].join(" ");
      const height = LABEL_H + (pile.length - 1) * CARD_GAP + CARD_H + FOOT;
      h += `<div class="${cls}" style="height:${height}px"><span class="pile-label">더미 ${k + 1}</span>`;
      pile.forEach((idx, depth) => {
        const c = [];
        if (onPath.has(idx)) c.push("on-path");
        else if (idx !== tops[k]) c.push("under");
        if (s.kind === "probe" && s.probe === k && idx === tops[k]) c.push("top-probe");
        const fresh = (s.kind === "place" || s.kind === "newpile") && idx === s.i;
        if (fresh) c.push("new");
        h += `<div class="card ${c.join(" ")}" data-idx="${idx}" style="top:${LABEL_H + depth * CARD_GAP}px"><small>a[${idx}]</small><b class="v">${state.a[idx - 1]}</b>${fresh ? FN(2) : ""}</div>`;
      });
      h += `</div>`;
    });
    $("piles").innerHTML = h;
    const tallest = Math.max(0, ...s.piles.map((p) => LABEL_H + (p.length - 1) * CARD_GAP + CARD_H + FOOT));
    $("piles").style.minHeight = Math.max(110, tallest + 8) + "px";

    if (fromRect) {
      const el = document.querySelector(`.piles .card[data-idx="${s.i}"]`);
      if (el) {
        const to = el.getBoundingClientRect();
        el.style.transition = "none";
        el.style.transform = `translate(${fromRect.left - to.left}px, ${fromRect.top - to.top}px)`;
        el.style.zIndex = 4;
        requestAnimationFrame(() => requestAnimationFrame(() => {
          el.style.transition = "transform .32s cubic-bezier(.2,.7,.2,1)";
          el.style.transform = "";
          el.addEventListener("transitionend", () => drawThreads(s), { once: true });
        }));
      }
    }
    drawThreads(s);
    renderNote("pat", s, s.kind === "answer" ? "II · 페이션스 · 답 복원"
      : s.i ? `II · 페이션스 · 카드 a[${s.i}] = ${state.a[s.i - 1]}` : "II · 페이션스");
    renderCode($("patCode"), PAT_CODE, PAT_LINE[s.kind]);
    $("patCount").textContent = `비교 ${s.comps}번 · 더미 ${s.piles.length}개`;
    $("patStep").textContent = `${state.pi + 1} / ${state.pat.steps.length}`;
  }

  // 역포인터(back) 화살표: 카드 위쪽 가운데 → 위로 휘어서 → 가리키는 카드 위쪽 가운데
  function drawThreads(s) {
    const svg = $("threads");
    const felt = $("felt");
    const base = felt.getBoundingClientRect();
    svg.setAttribute("width", felt.scrollWidth);
    svg.setAttribute("height", felt.scrollHeight);
    const pathSet = new Set(s.kind === "answer" ? s.path : []);
    const fresh = (s.kind === "place" || s.kind === "newpile") ? s.i : null;
    const head = (id, color) => `<marker id="${id}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9"
      markerUnits="userSpaceOnUse" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="${color}"/></marker>`;
    const C = { base: "rgba(232,239,233,.42)", fresh: "#bde7ef", path: "#f0a6b9" };
    let out = `<defs>${head("hd", C.base)}${head("hdNew", C.fresh)}${head("hdPath", C.path)}</defs>`;
    const top = (el, inset) => {
      const r = el.getBoundingClientRect();
      return [r.left - base.left + felt.scrollLeft + r.width / 2, r.top - base.top + inset];
    };
    s.back.forEach((target, k) => {
      const src = k + 1;
      if (target == null) return;
      const a = felt.querySelector(`.piles .card[data-idx="${src}"]`);
      const b = felt.querySelector(`.piles .card[data-idx="${target}"]`);
      if (!a || !b) return;
      const [x1, y1] = top(a, 2), [x2, y2] = top(b, 13);   // 끝은 가리키는 카드 안쪽까지
      const lift = 22;
      const c1x = x1 - 6, c1y = Math.min(y1, y2) - lift, c2x = x2 + 6, c2y = Math.min(y1, y2) - lift;
      const onPath = pathSet.has(src) && pathSet.has(target);
      const isNew = src === fresh;
      const stroke = onPath ? C.path : isNew ? C.fresh : C.base;
      const w = onPath || isNew ? 2 : 1.25;
      const mk = onPath ? "hdPath" : isNew ? "hdNew" : "hd";
      out += `<path d="M${x1},${y1} C${c1x},${c1y} ${c2x},${c2y} ${x2},${y2 - 1}" fill="none" stroke="${stroke}" stroke-width="${w}" marker-end="url(#${mk})"/>`;
    });
    svg.innerHTML = out;
  }

  function renderResult() {
    const box = $("result");
    if (!(dpEnd() && patEnd())) { box.hidden = true; return; }
    const d = state.dp, p = state.pat, n = state.a.length;
    const same = d.seq.join() === p.seq.join();
    $("resultBody").innerHTML = `
      <table class="res-table">
        <thead><tr><th></th><th>DP</th><th>페이션스 정렬</th></tr></thead>
        <tbody>
          <tr><th>LIS 길이</th><td class="dpc">${d.length}</td><td class="patc">${p.length}</td></tr>
          <tr><th>찾은 수열</th><td class="dpc">${d.seq.join(", ")}</td><td class="patc">${p.seq.join(", ")}</td></tr>
          <tr><th>비교 횟수</th><td class="dpc"><b>${d.comps}</b>번 = n(n−1)/2 = ${n}·${n - 1}/2</td><td class="patc"><b>${p.comps}</b>번 (더미 ${p.length}개에서 이분검색)</td></tr>
          <tr><th>보여준 단계 수</th><td>${d.steps.length}</td><td>${p.steps.length}</td></tr>
        </tbody>
      </table>
      <p class="verdict">두 방법 모두 길이 <b>${d.length}</b>${eul(d.length).slice(String(d.length).length)} 찾았습니다. ${same ? "고른 수열도 같습니다." : "LIS가 여러 개라서 서로 다른 수열을 골랐지만, 둘 다 길이가 같은 올바른 답입니다."}
      DP는 칸마다 왼쪽을 전부 비교해서 ${d.comps}번, 페이션스는 맨 윗장만 이분검색해서 ${p.comps}번 비교했습니다.
      n이 커질수록 차이가 벌어집니다(n = 8,000에서 약 594배).</p>`;
    box.hidden = false;
  }

  // ── 시작 ──
  buildPresets();
  const fromHash = /#a=([-\d,]+)/.exec(location.hash);
  const parsed = fromHash ? parseInput(fromHash[1].replace(/,/g, ", ")) : null;
  if (parsed && parsed.a) {
    const hit = Object.entries(PRESETS).find(([, p]) => p.a.join() === parsed.a.join());
    load(parsed.a, hit ? hit[0] : null);
  } else {
    load(PRESETS.basic.a, "basic");
  }
})();
