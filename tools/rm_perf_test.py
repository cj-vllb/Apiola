import os, time
from playwright.sync_api import sync_playwright
SITE = 'file://' + os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'index.html'))
out = []
with sync_playwright() as p:
    b = p.chromium.launch()
    # reduced motion: no animations running, hero swap is a fade (no slide)
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce'); pg = ctx.new_page(); pg.goto(SITE); pg.wait_for_timeout(600)
    n = pg.evaluate('document.getAnimations().filter(a => a instanceof CSSAnimation && a.playState === "running").length')
    xs0 = pg.evaluate("[...document.querySelectorAll('#bots .slot')].map(s => Math.round(s.getBoundingClientRect().left))")
    pg.evaluate('document.getElementById("next").click()'); pg.wait_for_timeout(50)
    mid = pg.evaluate("[...document.querySelectorAll('#bots .slot')].map(s => Math.round(s.getBoundingClientRect().left))")
    op = pg.evaluate("getComputedStyle(document.getElementById('bots')).opacity")
    pg.wait_for_timeout(500)
    xs1 = pg.evaluate("[...document.querySelectorAll('#bots .slot')].map(s => Math.round(s.getBoundingClientRect().left))")
    out.append(f'reduced motion: running CSS animations = {n} (need 0): {"PASS" if n == 0 else "FAIL"}')
    out.append(f'reduced motion swap: x before {xs0}, 50 ms in {mid} (no slide, bots opacity {op}), after {xs1}: {"PASS" if mid == xs0 and xs1 != xs0 else "FAIL"}')
    # pinned zoom disabled
    hs = []
    for pr in (.25, .3, .35, .42):
        pg.evaluate(f'__apiola.seek("flavours", {pr})'); pg.wait_for_timeout(1300)
        hs.append(round(pg.evaluate("(() => { const s = [...document.querySelectorAll('#bots .slot')].find(s => getComputedStyle(s).visibility !== 'hidden' && +getComputedStyle(s).opacity > .5); return s ? s.querySelector('svg').getBoundingClientRect().height : 0 })()")))
    out.append(f'reduced motion pinned heights at 3 scroll points {hs}: {"PASS" if len(set(hs)) == 1 else "FAIL"}')
    ctx.close()
    # performance: 4x CPU throttle, scroll the page, count running animations
    pg = b.new_page(viewport={'width': 1440, 'height': 900}); cdp = pg.context.new_cdp_session(pg); cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    pg.goto(SITE); pg.wait_for_timeout(800)
    total = pg.evaluate('document.documentElement.scrollHeight - innerHeight')
    pg.evaluate('window.__t = []; (function f(t0){ requestAnimationFrame(t => { if (window.__stop) return; window.__t.push(t); f(t0) }) })()')
    mx = 0
    for i in range(0, 81):
        pg.evaluate(f'scrollTo({{top:{total*i/80},behavior:"instant"}})'); pg.wait_for_timeout(120)
        n = pg.evaluate('document.getAnimations().filter(a => a instanceof CSSAnimation && a.playState === "running").length'); mx = max(mx, n)
    pg.evaluate('window.__stop = true'); ts = pg.evaluate('window.__t')
    gaps = sorted(b - a for a, b in zip(ts, ts[1:]))
    med = gaps[len(gaps)//2]; p95 = gaps[int(len(gaps)*.95)]
    out.append(f'4x CPU throttle: max simultaneous running animations = {mx} (need < ~20): {"PASS" if mx < 20 else "FAIL"}')
    out.append(f'4x CPU throttle: frame gap median {med:.1f} ms, p95 {p95:.1f} ms over {len(ts)} frames (headless software rendering, indicative only)')
    b.close()
print('\n'.join(out))
