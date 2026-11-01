"""웹(JS) 엔진 대조용: Python 단계 기록을 JSON으로 내보낸다."""
import json, random, sys
from lis import lis_dp_trace, lis_patience_trace
cases = [[10, 3, 11, 5, 8, 6, 1, 2, 7], [1, 2, 3, 4, 5, 6, 7, 8], [8, 7, 6, 5, 4, 3, 2, 1], [3, 5, 3, 5, 4, 6, 4, 7]]
random.seed(5)
for _ in range(2000):
    n = random.randint(1, 10)
    cases.append([random.randint(-3, 20) for _ in range(n)])
out = [dict(a=a, dp=lis_dp_trace(a), pat=lis_patience_trace(a)) for a in cases]
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False)
print(len(out), "cases exported")
