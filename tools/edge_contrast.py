"""4.5 acceptance: mean dE2000 between a bottle's outer-edge pixels and the stage colour behind it (need >= 8)."""
import os, io, numpy as np
from PIL import Image
from scipy import ndimage
from playwright.sync_api import sync_playwright
from skimage.color import rgb2lab, deltaE_ciede2000
SITE = 'file://' + os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'index.html'))
STAGES = {'plum': '#4A3D61', 'teal': '#0F5560', 'olive': '#4B6619'}
rows = []; ok = True
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 360, 'height': 850}); pg.goto(SITE); pg.wait_for_timeout(500)
    pg.evaluate("__apiola.freezeFloat(true)")
    pg.add_style_tag(content='body>*:not(#t){display:none!important} #t{display:flex;align-items:center;justify-content:center;width:360px;height:850px} #t .slot{height:800px;--sc:1!important;transform:none!important} #t .shadow{display:none}')
    for v in range(3):
        pg.evaluate(f'''() => {{ document.getElementById('t')?.remove(); const d = document.createElement('div'); d.id='t'; d.innerHTML = bottleHTML({v}, 'C'); document.body.append(d); }}''')
        pg.evaluate("document.querySelector('#t .floater').style.animation='none'")
        pg.wait_for_timeout(200)
        # mask: render on transparent background
        pg.evaluate("document.documentElement.style.background='transparent';document.body.style.background='transparent'")
        a = np.array(Image.open(io.BytesIO(pg.screenshot(omit_background=True))).convert('RGBA'))[..., 3] > 128
        edge = a & ~ndimage.binary_erosion(a, iterations=3)       # 3 px band just inside the silhouette
        for name, hexc in STAGES.items():
            pg.evaluate(f"document.documentElement.style.background='{hexc}';document.body.style.background='{hexc}'")
            img = np.array(Image.open(io.BytesIO(pg.screenshot())).convert('RGB')) / 255.0
            lab = rgb2lab(img); bg = rgb2lab(np.array([[[int(hexc[i:i+2], 16) / 255 for i in (1, 3, 5)]]]))
            de = deltaE_ciede2000(lab[edge], np.broadcast_to(bg[0, 0], lab[edge].shape))
            m = float(de.mean()); r = m >= 8; ok &= r
            rows.append(f"{['clover','orange blossom','acacia'][v]:15} on {name:6} mean edge dE2000 = {m:5.1f}  {'PASS' if r else 'FAIL'}")
    b.close()
print('\n'.join(rows)); print('EDGE CONTRAST:', 'ALL PASS' if ok else 'SOME FAIL')
