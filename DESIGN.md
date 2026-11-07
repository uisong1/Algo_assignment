# Design: 각주 원고 (Marginal Ledger)
**Date:** 2026-11-08 · **Status:** confirmed
**Archetype:** Sage (정밀, 엄밀) + Ruler (단정, 고급) · **Register:** calm structure · expressive at: 카드를 더미에 놓는 순간, 마지막 답 복원
**Grounding:** Edward Tufte 책의 여백 주석(sidenote) + 스위스 철도(SBB) 시간표의 숫자 조판
**DNA:** Swiss / International (글꼴은 사용자 지정: IBM Plex Sans KR) · **Dominant axis:** composition (여백 주석)
**Composition:** Marginalia (dealer: swiss-international × marginalia, variance 5, seed lis-visualizer|2026-11-08|0, hue 211.1 cyan)
**Pins:** 사용자 선택: 후보 ① 구성. 글꼴은 명조 대신 IBM Plex Sans KR(후보 비교 E안)로 교체. 카드 테이블의 펠트 초록은 콘텐츠 색으로 유지.

## Direction
채점하는 교수님과 같은 반 학생이 두 알고리즘을 한 단계씩 나란히 보며 "무엇을/왜"를 바로 읽게 한다. 학술서의 여백 주석처럼, 본문(두 패널)은 그림만 보여 주고 설명은 오른쪽 여백의 번호 주석이 맡는다. 단정한 격자와 숫자 조판, 한 가족의 IBM Plex(본문·코드)가 정밀하고 정돈된 인상을 만든다.

## Signature move
지금 단계에서 바뀐 칸(DP의 dp[i], 페이션스의 방금 놓은 카드)에 위첨자 주석 번호(¹, ²)가 붙고, 같은 번호의 주석이 오른쪽 여백에 "무엇을 / 왜"로 적힌다. 번호와 주석은 같은 잉크색(accent-11)이고, 이 색은 주석 연결에만 쓴다.

## Expressive moments
- 카드가 덱에서 더미로 날아가는 순간: 0.32초 이동(유일하게 긴 움직임).
- 마지막 단계의 답 복원: 정답 경로 색(--mark-path)이 이때만 등장.
- 그 외 모든 곳은 차분한 구조를 유지한다.

## Type
- Display: IBM Plex Sans KR 600/700 (Google Fonts) — 제목, 패널 제목, 카드 숫자. 제목 자간 -0.02em
- Body: IBM Plex Sans KR 400/500 — 본문, 라벨, 표 숫자(font-variant-numeric: tabular-nums)
- Code: IBM Plex Mono, 한글 주석은 IBM Plex Sans KR로 대체. 복잡도 표기(Θ, O)는 Mono의 Θ가 0처럼 보이므로 Sans로 쓴다
- Scale: 1.25 from 15px — 12 · 15 · 18.75 · 23.4 · 29.3 · 36.6
- Leading: body 1.65 / display 1.25 · Weights: 400, 500, 600(굵게는 제목만)
- 작은 대문자 라벨: 12px, letter-spacing 0.08em

## Color tokens
palette.mjs --seed 211.1 --chroma balanced --harmony mono (light만 사용)
```css
:root {
  --neutral-1: #fcfdfd;
  --neutral-2: #f7f9f9;
  --neutral-3: #eef1f2;
  --neutral-4: #e4e9ea;
  --neutral-5: #d8dfe1;
  --neutral-6: #cbd4d6;
  --neutral-7: #bbc6c8;
  --neutral-8: #a1adb0;
  --neutral-9: #abbbbe;
  --neutral-10: #99a8ab;
  --neutral-11: #5d6567;
  --neutral-12: #2a2f30;
  --accent-1: #f8feff;
  --accent-2: #f2fbfd;
  --accent-3: #e0f5f9;
  --accent-4: #d0eef4;
  --accent-5: #bde7ef;
  --accent-6: #a8dde7;
  --accent-7: #8ed0dd;
  --accent-8: #67b9c9;
  --accent-9: #5fc9dc;
  --accent-10: #51b5c7;
  --accent-11: #356d77;
  --accent-12: #163338;
  --accent-on-solid: #041012;
  --error-3: #ffebe9;
  --error-9: #e1524f;
  --error-11: #974843;
  --success-3: #e0f8e0;
  --success-9: #5ad664;
  --success-11: #337437;
  --warning-3: #f9f0dd;
  --warning-9: #dbb155;
  --warning-11: #76602f;
  --info-3: #e3f3ff;
  --info-9: #5baee5;
  --info-11: #3d6886;
  --background: var(--neutral-1);
  --surface: var(--neutral-2);
  --surface-hover: var(--neutral-3);
  --surface-active: var(--neutral-4);
  --border-subtle: var(--neutral-6);
  --border: var(--neutral-7);
  --border-strong: var(--neutral-8);
  --text-secondary: var(--neutral-11);
  --text: var(--neutral-12);
  --accent-bg-subtle: var(--accent-3);
  --accent-solid: var(--accent-9);
  --accent-solid-hover: var(--accent-10);
  --accent-text: var(--accent-11);
}
```
데이터 전용 색(크롬에는 쓰지 않음):
```css
--mark-i: var(--accent-11);       --mark-i-bg: var(--accent-3);     /* 지금 칸 i, 방금 놓은 카드 */
--mark-j: var(--warning-11);      --mark-j-bg: var(--warning-3);    /* 비교 중인 j */
--mark-path: #a8445e;             --mark-path-bg: #f8e6eb;          /* 정답 경로(마지막 단계만) */
--felt: #2e4a3e;                  --felt-deep: #24392f;             /* 카드 테이블 */
--card: #fbfaf6;
```
Contrast:
```
/* Contrast report (WCAG 2.x)
   PASS  [light] neutral-11 on neutral-2: 5.66:1 (target 4.5:1)
   PASS  [light] neutral-12 on neutral-2: 12.89:1 (target 7:1)
   PASS  [light] neutral-12 on neutral-3: 11.98:1 (target 4.5:1)
   PASS  [light] accent-11 on neutral-2: 5.54:1 (target 4.5:1)
   PASS  [light] accent-11 on accent-2: 5.56:1 (target 4.5:1)
   PASS  [light] accent-on-solid on accent-9: 10:1 (target 4.5:1)
   PASS  [dark] neutral-11 on neutral-2: 8.78:1 (target 4.5:1)
   PASS  [dark] neutral-12 on neutral-2: 14.28:1 (target 7:1)
   PASS  [dark] neutral-12 on neutral-3: 12.95:1 (target 4.5:1)
   PASS  [dark] accent-11 on neutral-2: 8.93:1 (target 4.5:1)
   PASS  [dark] accent-11 on accent-2: 8.91:1 (target 4.5:1)
   PASS  [dark] accent-on-solid on accent-9: 10:1 (target 4.5:1)
*/
```

## Space, shape, depth
- Spacing scale: 4 · 8 · 12 · 16 · 24 · 32 · 48 · 72
- Radius: 0 (칸, 버튼, 패널). 카드만 3px (실물 카드 모서리)
- Borders/shadows: 1px 헤어라인(--border-subtle) 구분선. 그림자는 카드에만, 펠트 색으로 물든 그림자(rgba(20,40,32,.28)). 순검정 그림자 금지

## Motion
- Timing: 120ms(상태) / 320ms(카드 이동) · Easing: cubic-bezier(.2,.7,.2,1)
- Allowed: 칸 강조 전환, 카드 이동, 의사코드 줄 강조 · Never: 페이드인 등장, 튀는 easing, 호버 확대
- prefers-reduced-motion: 모든 전환 0ms, 카드는 바로 제자리에

## Never (this project's tells at risk)
- 한쪽만 두꺼운 색 테두리를 단 설명 상자 (현재 사이트의 설명 상자)
- 둥근 카드 안에 또 둥근 카드
- 청록 강조를 어두운 배경에 쓰기 (cyan-on-dark)
- 강조색을 버튼·제목·배지마다 뿌리기: 잉크색은 주석 연결과 i 표시에만
- 가운데 정렬 레이아웃: 전부 왼쪽 정렬

## Open questions
- 노트북 1280px에서 패널 둘 + 여백이 빠듯하면 여백 폭을 260px까지 줄인다
- 모바일(<760px): 여백 주석은 각 패널 바로 아래로 내려간다
