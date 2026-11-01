# 카드 게임으로 푸는 최장 증가 부분수열 (LIS)

2026-2학기 알고리즘 과제, 주제 A(알고리즘 동작 시각화).
같은 문제(최장 증가 부분수열)를 푸는 두 알고리즘을 한 단계씩 나란히 보여줍니다.

| | DP | 페이션스 정렬 |
|---|---|---|
| 아이디어 | dp[i] = a[i]로 끝나는 가장 긴 증가 수열의 길이 | 카드를 '맨 윗장이 자기 이상인 가장 왼쪽 더미'에 쌓으면 더미 수 = 답 |
| 시간 | Θ(n²), 모든 경우 | O(n log n), 더 정확히 O(n log L) |
| 공간 | Θ(n) | Θ(n) |

**시각화:** https://uisong1.github.io/Algo_assignment/

## 구성

- `docs/`: 웹 시각화 (GitHub Pages로 배포)
  - `lis.js`: 두 알고리즘과 단계별 설명 생성
  - `app.js`, `index.html`, `style.css`: 화면
- `analysis/`: 검증과 실측
  - `lis.py`: Python 기준 구현 (단계별 설명 포함)
  - `verify.py`: 모든 부분수열을 확인하는 완전탐색과 대조 (무작위 수열 20,000개)
  - `gen_parity.py`, `parity_test.js`: 웹(JS) 구현이 Python 구현과 모든 단계에서 같은지 대조
  - `bench.py`, `plot.py`, `bench.json`, `bench_*.png`: n과 입력 형태에 따른 비교 횟수·실행 시간

## 직접 확인하기

```sh
cd analysis
python3 verify.py                       # 완전탐색 대조
python3 gen_parity.py /tmp/parity.json  # Python 단계 기록 내보내기
node parity_test.js /tmp/parity.json    # 웹 구현과 대조
python3 bench.py && python3 plot.py     # 실측과 차트
```
