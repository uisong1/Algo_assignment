import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/03197a7e-b736-56e4-8716-315fb60c98c4/scratchpad")
from fontlib import install
from playwright.sync_api import sync_playwright
url, outdir, pane = sys.argv[1], sys.argv[2], sys.argv[3]   # pane: dp | pat
other = "pat" if pane == "dp" else "dp"
keep_note = 1 if pane == "dp" else 2
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 1100}, device_scale_factor=1)
    install(pg); pg.goto(url); pg.wait_for_timeout(1200); pg.evaluate("document.fonts.ready")
    pg.add_style_tag(content=f"""
      .controls{{position:static!important}}
      .sheet{{grid-template-columns:minmax(0,1fr) 320px!important;border-bottom:0!important;padding-bottom:20px!important}}
      .pane.{other}{{display:none!important}}
      .pane.pat{{padding-left:0!important;margin-left:0!important;border-left:0!important}}
      .notes .note:nth-of-type({3-keep_note}){{display:none!important}}
      .aside-foot{{display:none}}
      .legend span:nth-of-type({2 if pane=='dp' else 0}){{}}""")
    sheet = pg.query_selector(".sheet")
    nxt = pg.query_selector(f'.mini button[data-pane="{pane}"][data-dir="1"]')
    k = 0
    while True:
        sheet.screenshot(path=f"{outdir}/f{k:03d}.png"); k += 1
        cur, tot = [int(x) for x in pg.inner_text(f"#{pane}Step").split("/")]
        if cur >= tot: break
        nxt.click(); pg.wait_for_timeout(520)
    print(pane, "frames", k); b.close()
