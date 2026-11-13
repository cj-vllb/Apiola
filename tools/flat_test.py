"""Flat test: no element may carry anything but translate + uniform scale. Also scans the source for banned terms."""
import re, sys
from playwright.sync_api import sync_playwright
SITE = 'file://' + __import__('os').path.abspath(__import__('os').path.join(__import__('os').path.dirname(__file__), '..', 'index.html'))
JS = '''() => [...document.querySelectorAll('*')].flatMap(el => {
  const t = getComputedStyle(el).transform; if (t === 'none') return [];
  if (t.startsWith('matrix3d')) return [[el.tagName + '.' + (el.className.baseVal ?? el.className), t]];
  const [a,b,c,d] = t.slice(7,-1).split(',').map(Number);
  return (Math.abs(b)>1e-3 || Math.abs(c)>1e-3 || Math.abs(a-d)>1e-3) ? [[el.tagName + '.' + (el.className.baseVal ?? el.className), t]] : [];
})'''
BANNED = ['THREE','WebGL','getContext(','<canvas','rotate(','rotateX','rotateY','rotateZ','rotate3d','skew','perspective','matrix3d','scale3d']
src = open(SITE[7:], encoding='utf8').read()
bad = [(w, [m.start() for m in re.finditer(re.escape(w), src)][:3]) for w in BANNED if w in src]
print('SOURCE SCAN:', 'clean' if not bad else bad)
fails = 0; samples = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    for (W, H) in [(1440, 900), (390, 844)]:
        pg = b.new_page(viewport={'width': W, 'height': H}); pg.goto(SITE); pg.wait_for_timeout(600)
        total = pg.evaluate('document.documentElement.scrollHeight - innerHeight')
        for i in range(0, 61):                                   # many scroll positions, floats running
            pg.evaluate(f'scrollTo({{top:{total*i/60},behavior:"instant"}})'); pg.wait_for_timeout(110)
            r = pg.evaluate(JS); samples += 1
            if r: fails += 1; print('FAIL', W, i, r[:3])
        pg.evaluate('scrollTo({top:0,behavior:"instant"})'); pg.wait_for_timeout(500)
        for rnd in range(4):                                      # sample every frame-ish during hero swaps
            pg.evaluate('document.getElementById("next").click()')
            for _ in range(22):
                r = pg.evaluate(JS); samples += 1
                if r: fails += 1; print('FAIL swap', W, r[:3])
                pg.wait_for_timeout(45)
        pg.evaluate('document.getElementById("prev").click()')
        for _ in range(22):
            r = pg.evaluate(JS); samples += 1
            if r: fails += 1; print('FAIL swap-prev', W, r[:3])
            pg.wait_for_timeout(45)
        pg.close()
    b.close()
print(f'FLAT TEST: {samples} full-page samples, {fails} failures ->', 'PASS' if fails == 0 and not bad else 'FAIL')
