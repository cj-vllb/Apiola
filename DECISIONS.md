# Decisions
- **Flat 2D only.** All 3D code, canvases, fallbacks and the vendored 3D library are gone. Every bottle is one SVG symbol (`bottle-clover`, `bottle-orange`, `bottle-acacia`) built by `buildBottle()` from plain shapes. Petals and blooms are computed from polar coordinates, so the artwork carries no transforms at all.
- **Three layers per bottle:** `.slot` (translate + uniform scale only) > `.shadow` + `.floater` (float keyframes only) > `svg.bottle`. The hero positions are written per frame as `translate() translate(-50%,-50%) scale()`, so the float keeps running through swaps, hand-off and the pinned zoom.
- **Hero wrap-around** bottle travels in a straight line behind the centre bottle at side scale (`z-index` 1 during the move).
- **Arrows** moved to the outer edges (3vw) because the side bottles now occupy the old 30% and 70% positions. On phones they sit at the bottom.
- **Float delays are negative phase offsets** (-0.7 s, -1.4 s and so on) so every bottle is already moving on page load instead of waiting out a delay.
- **Float amplitude is set in vh** (floored at 6px) so it scales with bottle size. The hero centre bottle uses variant A, side bottles B, and the pinned bottle C (`FLOAT_IN_PINNED`). Amplitude changes ease via a registered `--amp` property; period and phase stay fixed per bottle so nothing jumps.
- **Honey tints were shifted** to pass the CIEDE2000 >= 12 rule against the previous palette: clover `#C5A443` (deep `#A98A2C`), orange blossom `#C4812B` (deep `#A8661A`), acacia `#EDD69C` (deep `#CDB574`). Clover honey is the biggest move (toward green-gold) and reads more golden-olive than amber. Lids and labels passed unchanged.
- **FAQ plus/cross icon** no longer rotates; the glyph swaps between + and a minus sign so the flat test can hold for every element.
- **Decorative floaters:** ten in total (4 hero, 3 Why Apiola, 3 newsletter), hidden below 768px, `aria-hidden`.
- **Reduced motion:** no floating or drift; hero swaps fade over about 200 ms; background changes cross-fade in 200 ms with no curtain; the pinned stages keep their scroll length but have no zoom and swap by cross-fade, rather than becoming separate unpinned panels.
- **Off-screen sections** pause their animations through an IntersectionObserver.
- **Fonts:** Fraunces and Manrope load from Google Fonts. Offline, the bottles fall back to Georgia/serif and system sans.
- **Reference picture** was not attached to this conversation, so the finish follows the written style notes only. No artwork, text or layout from any reference is used.
- Trademark and domain status of the name "Apiola" is unchecked.

## Responsive pass
- **Three tiers, desktop untouched.** `<=900px` (tablet portrait / small), `<=767px` (phone), and `max-height:520px` landscape (phones on their side). Desktop (>900 wide, landscape) is pixel-identical apart from size caps that never bite there (`min(70vh,62vw)` cards, `min(58%,56vw)` hero bottles, `min(70vh,48vw)` newsletter bottles, `min(86vh,79vw)` Why bottle).
- **Phone nav:** the link row collapses into a menu button (`#mt` / `#menu`; closes on link tap, outside tap, Escape and resize). "Find a stockist" stays in the bar.
- **Phone hero:** the tagline, counter, arrows and CTA are a bottom-anchored grid instead of separately absolute-positioned, so they cannot overlap on short phones. `#hname` is `nowrap` and `fitName()` shrinks it only when "orange blossom" would be wider than the screen.
- **"just nectar / & patience."** `fitBub()` sizes the lines to the screen on narrow, portrait or short viewports (font-independent: measures the text), stacks the bottle below on portrait, and slides the lines a quarter as far so they stay on screen. Desktop keeps the original oversize sliding text.
- **Stable scroll maths on phones:** frame loop uses the pinned stage height (`svh`) instead of `innerHeight`, so the address bar sliding away no longer makes the pinned scenes jump.
- **Sections** clear the fixed nav (`max(Nvh,104px)` top padding); Why stacks at <=900; newsletter bottles drop to the bottom on portrait so they never cover the headline; the newsletter grid cell is `minmax(0,1fr)` (it used to size to its content and push text to the screen edge); footer columns reflow in a grid (they caused the 398px horizontal scroll).
- **Touch:** hover lift on cards only where hover exists; swipe to change honey needs a clearly horizontal gesture; open FAQ answers re-measure on resize; stockist panel closes on Escape and blocks background scroll; `viewport-fit=cover` plus safe-area insets for notched phones.
