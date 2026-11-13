import os, math
from playwright.sync_api import sync_playwright
SITE = 'file://' + os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'index.html'))
res = {}
def p2p(v): return max(v) - min(v)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900}); pg.goto(SITE); pg.wait_for_timeout(700)
    FY = '''() => [...document.querySelectorAll('#bots .floater')].map(f => { const m = getComputedStyle(f).transform; return m === 'none' ? 0 : +m.slice(7,-1).split(',')[5] })'''
    # 1. float: 8 s, arrows pressed twice
    ys = [[], [], []]; swaps = 0
    for i in range(160):
        if i in (40, 100): pg.evaluate('document.getElementById("next").click()'); swaps += 1
        for k, v in enumerate(pg.evaluate(FY)): ys[k].append(v)
        pg.wait_for_timeout(50)
    pp = [round(p2p(y), 1) for y in ys]
    # stall check: longest window (in samples) where a floater did not change at all
    def stall(y):
        run = best = 0
        for a, c in zip(y, y[1:]):
            run = run + 1 if abs(a - c) < 1e-4 else 0; best = max(best, run)
        return best
    st = [stall(y) for y in ys]
    res['1 float (peak-to-peak px per hero bottle over 8 s, with 2 arrow presses)'] = (pp, 'longest stall samples', st, 'PASS' if min(pp) >= 6 and max(st) < 8 else 'FAIL')
    # 2. hero swap: positions, z-order of wrapping bottle
    pg.evaluate('scrollTo({top:0,behavior:"instant"})'); pg.evaluate('__apiola.setHero(0)'); pg.wait_for_timeout(1500)
    S = '''() => [...document.querySelectorAll('#bots .slot')].map(s => { const r = s.getBoundingClientRect(); return [Math.round(r.left + r.width/2), getComputedStyle(s).zIndex, getComputedStyle(s).transform.slice(0,24)] })'''
    before = pg.evaluate(S); pg.evaluate('document.getElementById("next").click()')
    seen_back = False; mid = None
    for i in range(24):
        pg.wait_for_timeout(50); cur = pg.evaluate(S)
        if any(c[1] == '1' for c in cur): seen_back = True
        if i == 9: mid = cur
    after = pg.evaluate(S); after = pg.evaluate(S)
    xs_b = [c[0] for c in before]; xs_a = [c[0] for c in after]
    moved = [xs_b[k] != xs_a[k] for k in range(3)]
    # next: bottle1 right->centre, bottle0 centre->left, bottle2 left->right
    order_ok = xs_a[1] in range(700, 740) and xs_a[0] < xs_a[1] < xs_a[2]
    res['2 hero swap (x before / after; wrap bottle z-index 1 seen)'] = (xs_b, xs_a, seen_back, 'PASS' if all(moved) and order_ok and seen_back else 'FAIL')
    pg.evaluate('__apiola.setHero(0)'); pg.wait_for_timeout(1200)
    # 3. pinned zoom
    H = 900; ok_all = True; detail = []
    for k in range(3):
        hs = []; cx = []
        for fi in range(0, 17):
            f = fi * .05
            pr = (k + f) / 3
            pg.evaluate(f'__apiola.seek("flavours", {(0.8 + 3*pr) / 4.8 * (4.8*H) / (4.8*H - H) * (4.8*H - H) / (4.8*H - H) / 1})')
            pg.wait_for_timeout(750)
            r = pg.evaluate('''() => { const s = [...document.querySelectorAll('#bots .slot')].find(s => getComputedStyle(s).visibility !== 'hidden' && +getComputedStyle(s).opacity > .5); if (!s) return null; const r = s.querySelector('svg').getBoundingClientRect(); const st = document.querySelector('#flavours .stage').getBoundingClientRect(); return [r.height, (r.left + r.width/2 - st.left) / st.width, document.querySelectorAll('img,picture,video,canvas').length] }''')
            if r: hs.append(r[0]); cx.append(r[1]); nophoto = r[2] == 0
        mono = all(hs[i] >= hs[i+1] - 0.6 for i in range(len(hs)-1))
        ratio = hs[0] / hs[-1]
        inx = all(.62 <= c <= .82 for c in cx)
        detail.append((k, round(hs[0]), round(hs[-1]), round(ratio, 2), mono, inx))
        ok_all &= mono and inx and 1.25 < ratio < 1.5
    res['3 pinned zoom (stage, h start, h end, ratio, monotonic, centre x in 62-82%)'] = (detail, 'no img/picture/video/canvas:', nophoto, 'PASS' if ok_all and nophoto else 'FAIL')
    # 4. why apiola
    pg.evaluate('__apiola.seek("why",0)'); pg.wait_for_timeout(600)
    y = []
    for i in range(80): y.append(pg.evaluate('(() => { const f = document.querySelector("#why .floater"); return +getComputedStyle(f).transform.slice(7,-1).split(",")[5] })()')); pg.wait_for_timeout(50)
    btn = pg.evaluate('document.querySelectorAll("#why button, #why a, #why [tabindex]").length')
    res['4 why apiola (float peak-to-peak px, clickable elements)'] = (round(p2p(y), 1), btn, 'PASS' if p2p(y) >= 6 and btn == 0 else 'FAIL')
    # 5. range hover
    pg.evaluate('__apiola.seek("range",0)'); pg.wait_for_timeout(600)
    card = pg.locator('.card').nth(1); card.hover(); pg.wait_for_timeout(700)
    m = pg.evaluate('''() => { const s = document.querySelectorAll('.card .slot')[1]; return getComputedStyle(s).transform }''')
    a, bb, c, d = [float(v) for v in m[7:-1].split(',')[:4]]
    res['5 range hover (slot matrix a, b, c, d)'] = ((round(a, 3), round(bb, 3), round(c, 3), round(d, 3)), 'PASS' if abs(a - 1.06) < .01 and abs(bb) < 1e-3 and abs(c) < 1e-3 else 'FAIL')
    b.close()
for k, v in res.items(): print(k, '->', v)
print('MOTION TESTS:', 'ALL PASS' if all(v[-1] == 'PASS' for v in res.values()) else 'SOME FAIL')
