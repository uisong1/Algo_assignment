"""report.html -> 편집 가능한 .docx

그림(DP 표, 카드 더미 SVG), 의사코드, 수식 줄은 PNG로 찍어 넣고
제목·본문·표·목록·캡션은 Word에서 고칠 수 있는 텍스트로 남긴다.

    python3 build_docx.py <out.docx>
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SCRATCH = os.environ.get("FONTROUTE_DIR")
if SCRATCH:
    sys.path.insert(0, SCRATCH)
    from fontroute import install as install_fonts
else:
    install_fonts = lambda page: None

out_docx = Path(sys.argv[1]).resolve()
work = Path(tempfile.mkdtemp(prefix="docx_"))
(work / "img").mkdir()

# 1) 브라우저에서 그림 요소를 PNG로 찍고, 레이아웃을 Word 친화적인 흐름으로 바꾼다
SNAP = "svg.fig-svg, pre.code, .eq"
TEXT_WIDTH_PX = 600  # A4 본문 폭(약 6.3in)을 96dpi로 환산한 값보다 약간 작게

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(device_scale_factor=3, viewport={"width": 760, "height": 1000})
    install_fonts(pg)
    pg.goto((HERE / "report.html").as_uri())
    pg.wait_for_timeout(1200)
    pg.evaluate("document.fonts.ready")
    # 2열 격자를 풀어 그림 하나가 본문 폭을 넉넉히 쓰도록 한다
    pg.add_style_tag(content=".two,.cf,.steps{display:block!important}"
                             ".cf>div,.two>div{margin-bottom:8px}")
    els = pg.query_selector_all(SNAP)
    for k, el in enumerate(els):
        box = el.bounding_box()
        name = f"img/snap_{k:03d}.png"
        el.screenshot(path=str(work / name), omit_background=False)
        w = min(TEXT_WIDTH_PX, round(box["width"] * (1.25 if el.evaluate("e=>e.tagName") == "svg" else 1.0)))
        el.evaluate("""(e, a) => {
            const img = document.createElement('img');
            img.setAttribute('src', a.src); img.setAttribute('width', a.w);
            const p = document.createElement('p'); p.appendChild(img);
            e.replaceWith(p);
        }""", {"src": name, "w": w})

    pg.evaluate(r"""() => {
      const flat = (el, tag) => { const n = document.createElement(tag);
        n.innerHTML = el.innerHTML; el.replaceWith(n); return n; };
      // 단계 그림: 캡션을 굵은 문단으로, figure를 일반 div로
      document.querySelectorAll('figure.step').forEach(f => {
        const cap = f.querySelector('figcaption');
        if (cap) { const p = document.createElement('p'); p.innerHTML = '<b>' + cap.innerHTML + '</b>'; cap.replaceWith(p); }
        flat(f, 'div');
      });
      // 강조 상자와 h4는 인용 블록/굵은 문단으로
      document.querySelectorAll('.box, .bad').forEach(el => flat(el, 'blockquote'));
      document.querySelectorAll('h4').forEach(h => { const p = document.createElement('p');
        p.innerHTML = '<b>' + h.innerHTML + '</b>'; h.replaceWith(p); });
      // 웹 캡처·차트 이미지 폭과 경로
      document.querySelectorAll('img.shot').forEach(i => i.setAttribute('width', '600'));
      document.querySelectorAll('svg').forEach(v => v.remove());
      document.querySelectorAll('style, script').forEach(s => s.remove());
    }""")
    html = pg.content()
    # 원본 이미지 경로를 작업 폴더로 복사
    for src in pg.eval_on_selector_all("img", "els => els.map(e => e.getAttribute('src'))"):
        if not src.startswith("img/snap_"):
            dst = work / "img" / Path(src).name
            dst.write_bytes((HERE / src).read_bytes())
            html = html.replace(f'src="{src}"', f'src="img/{Path(src).name}"')
    b.close()

(work / "doc.html").write_text(html, encoding="utf-8")

# 2) pandoc 변환
subprocess.run(["pandoc", "doc.html", "-f", "html", "-t", "docx", "--dpi=96",
                "-o", str(out_docx)], cwd=work, check=True)

# 3) python-docx로 글꼴·표 테두리·페이지 나눔·쪽 번호 손질
from docx import Document
from docx.shared import Pt, Mm, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK

doc = Document(out_docx)
KFONT = "맑은 고딕"

def set_font(style, size=None, bold=None, color=None):
    f = style.font
    f.name = KFONT
    rpr = style.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), KFONT)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]
    if size: f.size = Pt(size)
    if bold is not None: f.bold = bold
    if color: f.color.rgb = RGBColor.from_string(color)

sizes = {"Normal": 10, "Body Text": 10, "First Paragraph": 10, "Compact": 10,
         "Block Text": 9.5, "Image Caption": 9, "Caption": 9,
         "Title": 20, "Heading 1": 17, "Heading 2": 14, "Heading 3": 11.5}
for st in doc.styles:
    if st.type == 1 or st.type == 3:  # paragraph / table
        try:
            set_font(st, sizes.get(st.name))
        except Exception:
            pass
S = {st.name: st for st in doc.styles}
for n in ("Heading 1", "Heading 2", "Heading 3", "Title"):
    if n in S:
        set_font(S[n], sizes[n], True, "1F2937")
for n in ("Body Text", "First Paragraph", "Normal", "Compact"):
    if n in S:
        pf = S[n].paragraph_format
        pf.space_after = Pt(5); pf.line_spacing = 1.3
if "Image Caption" in S:
    S["Image Caption"].font.color.rgb = RGBColor(0x55, 0x5B, 0x66)

# 여백 A4
for s in doc.sections:
    s.page_height, s.page_width = Mm(297), Mm(210)
    s.left_margin = s.right_margin = Mm(20)
    s.top_margin, s.bottom_margin = Mm(18), Mm(18)
    # 바닥글 쪽 번호
    fp = s.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run()
    for t, txt in (("begin", None), (None, " PAGE "), ("end", None)):
        if t:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), t); r._r.append(e)
        else:
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; r._r.append(e)
    r.font.size = Pt(8)

# 표: 테두리, 머리글 음영, 셀 글자 크기
def borders(tbl):
    tblPr = tbl._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), "BFC5CC")
        b.append(e)
    old = tblPr.find(qn("w:tblBorders"))
    if old is not None: tblPr.remove(old)
    tblPr.append(b)

for tbl in doc.tables:
    borders(tbl)
    for ri, row in enumerate(tbl.rows):
        for cell in row.cells:
            for para in cell.paragraphs:
                para.paragraph_format.space_after = Pt(1)
                for run in para.runs:
                    run.font.size = Pt(9)
            if ri == 0:
                tcPr = cell._tc.get_or_add_tcPr()
                sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear")
                sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), "EEF1F4")
                tcPr.append(sh)

# 표지 다음과 5장 앞에서 페이지 나눔
paras = doc.paragraphs
for i, para in enumerate(paras):
    if para.style.name.startswith("Heading") and para.text.strip().startswith(("1. ", "5. ")):
        if i > 0:
            para.paragraph_format.page_break_before = True

doc.save(out_docx)
print("saved", out_docx, "| work dir:", work)
