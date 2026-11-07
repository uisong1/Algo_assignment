import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/03197a7e-b736-56e4-8716-315fb60c98c4/scratchpad")
from fontlib import install
from playwright.sync_api import sync_playwright
url, outdir = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
    install(pg); pg.goto(url); pg.wait_for_timeout(1200); pg.evaluate("document.fonts.ready")
    pg.add_style_tag(content=".controls{position:static!important} .sheet{border-bottom:0!important;padding-bottom:20px!important} .aside-foot{display:none}")
    sheet = pg.query_selector(".sheet")
    k = 0
    while True:
        sheet.screenshot(path=f"{outdir}/f{k:03d}.png"); k += 1
        done = pg.evaluate("document.getElementById('btnNext').disabled")
        if done: break
        pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(520)
    print("frames", k); b.close()
