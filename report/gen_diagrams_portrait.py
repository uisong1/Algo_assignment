# 세로(portrait)용 다이어그램: 2열, 6칸 + 4칸 두 장으로 나눈다. gen.py의 패널을 그대로 쓴다.
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("gen.py").read())

VCSS = CSS.replace(
    ".sheet{padding:28px 32px 32px;width:1640px;box-sizing:border-box}",
    ".sheet{padding:22px 24px 26px;width:860px;box-sizing:border-box}",
) + """
.g2 .panel:not(.final):nth-child(odd)::after{content:"→";position:absolute;right:-22px;top:50%;font-size:18px;color:#a1a1a1}
.g2 .panel:not(.final):nth-child(even)::after{content:"↙";position:absolute;left:-14px;bottom:-24px;font-size:16px;color:#a1a1a1}
.g2 .panel:last-child::after{content:none!important}
.cont{color:#888;font-size:13px;margin:0 0 12px}
"""
VHEAD = HEAD.replace(CSS, VCSS)


def vpage(fname, title, sub, legend, panels, part, total):
    if part == 1:
        head = f"<h2>{title}</h2><p class=\"sub\">{sub}</p>{legend}"
    else:
        head = f"<p class=\"cont\">{title} (이어서, {part}/{total})</p>"
    body = "".join(panels)
    open(fname, "w").write(
        VHEAD + f'<div class="sheet" id="s">{head}<div class="grid g2" style="--cols:2">{body}</div></div></body></html>'
    )


dp_leg = ('<div class="legend"><span><i class="sw" style="background:#d3e5ff;border-color:#0761d1"></i>이번에 채운 칸 i</span>'
          '<span><i class="sw" style="background:#ffefcf;border-color:#ab570a"></i>이어 붙인 앞 원소 j</span>'
          '<span><i class="sw" style="background:#d8ccf1;border-color:#4c2889"></i>정답 경로</span></div>')
pt_leg = ('<div class="legend"><span><i class="sw" style="background:#d3e5ff;border-color:#0070f3"></i>이번에 놓은 카드</span>'
          '<span><i class="sw" style="background:#fff;border-color:#6aa8ff"></i>화살표: 왼쪽 더미 맨 윗장</span>'
          '<span><i class="sw" style="background:#d8ccf1;border-color:#4c2889"></i>정답 경로</span></div>')
dsub = f"입력 {seq}. dp[i] = a[i]로 끝나는 가장 긴 증가 부분수열의 길이. 한 단계에 칸 하나를 채운다."
psub = f'입력 {seq}. 카드를 "맨 윗장이 그 카드 이상인 가장 왼쪽 더미"에 올리고, 없으면 새 더미를 만든다. 더미 개수 = LIS 길이.'
T_DP, T_PT = "동적계획법(DP) — 표를 왼쪽부터 채우기", "페이션스 정렬 — 카드를 더미에 쌓기"
vpage("dp_v1.html", T_DP, dsub, dp_leg, dp_html[:6], 1, 2)
vpage("dp_v2.html", T_DP, dsub, dp_leg, dp_html[6:], 2, 2)
vpage("pat_v1.html", T_PT, psub, pt_leg, pt_html[:6], 1, 2)
vpage("pat_v2.html", T_PT, psub, pt_leg, pt_html[6:], 2, 2)
print("ok")
