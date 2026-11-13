import math
def lab(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    c=[((v+.055)/1.055)**2.4 if v>.04045 else v/12.92 for v in c]
    X=(.4124*c[0]+.3576*c[1]+.1805*c[2])/.95047;Y=.2126*c[0]+.7152*c[1]+.0722*c[2];Z=(.0193*c[0]+.1192*c[1]+.9505*c[2])/1.08883
    f=lambda t:t**(1/3) if t>.008856 else 7.787*t+16/116
    return 116*f(Y)-16,500*(f(X)-f(Y)),200*(f(Y)-f(Z))
def de(a,b):
    L1,a1,b1=a;L2,a2,b2=b;C1=math.hypot(a1,b1);C2=math.hypot(a2,b2);Cm=(C1+C2)/2
    G=.5*(1-math.sqrt(Cm**7/(Cm**7+25**7)));a1p=(1+G)*a1;a2p=(1+G)*a2
    C1p=math.hypot(a1p,b1);C2p=math.hypot(a2p,b2);h=lambda y,x:math.degrees(math.atan2(y,x))%360
    h1=h(b1,a1p);h2=h(b2,a2p);dL=L2-L1;dC=C2p-C1p
    dh=0 if C1p*C2p==0 else (h2-h1+360 if h2-h1<-180 else h2-h1-360 if h2-h1>180 else h2-h1)
    dH=2*math.sqrt(C1p*C2p)*math.sin(math.radians(dh/2));Lp=(L1+L2)/2;Cp=(C1p+C2p)/2
    hp=(h1+h2)/2 if C1p*C2p==0 or abs(h1-h2)<=180 else ((h1+h2+360)/2 if h1+h2<360 else (h1+h2-360)/2)
    T=1-.17*math.cos(math.radians(hp-30))+.24*math.cos(math.radians(2*hp))+.32*math.cos(math.radians(3*hp+6))-.2*math.cos(math.radians(4*hp-63))
    Sl=1+.015*(Lp-50)**2/math.sqrt(20+(Lp-50)**2);Sc=1+.045*Cp;Sh=1+.015*Cp*T
    Rt=-2*math.sqrt(Cp**7/(Cp**7+25**7))*math.sin(math.radians(60*math.exp(-((hp-275)/25)**2)))
    return math.sqrt((dL/Sl)**2+(dC/Sc)**2+(dH/Sh)**2+Rt*(dC/Sc)*(dH/Sh))
OLD="#E8542E #F7A31C #5CB159 #EF7B8D #4E5DC3 #F3D03C #FAF4EA #1B1915 #6B665D #FFF4E8 #3B2200 #0E2F12 #5B1026 #2E2800".split()
CH={"plum":"#4A3D61","teal":"#0F5560","olive":"#4B6619","peach":"#CFA38C","on-sage":"#B9D6C2"}
NE={"mist":"#E1E9D9","pine":"#10231F"}
VAR={
 "clover":  {"honey":"#C5A443","deep":"#A98A2C","lid":"#4F3B63","label":"#5C4573"},
 "orange":  {"honey":"#C4812B","deep":"#A8661A","lid":"#0F5560","label":"#177078"},
 "acacia":  {"honey":"#EDD69C","deep":"#CDB574","lid":"#4A5A2A","label":"#566A33"}}
INFO={"cream":"#F6EBC9","gold":"#CFA94E"}
ok=True
print("== stage and neutral colours (unchanged rules: stage >=20, neutral >=7) ==")
for grp,mn in((CH,20),(NE,7)):
    for n,c in grp.items():
        m=min(de(lab(c),lab(o)) for o in OLD);r=m>=mn
        print(f"{n:9}{c} min dE2000={m:5.1f} need>={mn} {'PASS' if r else 'FAIL (carried over from the previous site, not a bottle colour)'}")
print("== bottle honey / deep / lid / label colours (need >= 12 from every original colour, and not equal to one) ==")
for v,cols in VAR.items():
    for part,c in cols.items():
        m=min(de(lab(c),lab(o)) for o in OLD);r=m>=12 and c.lower() not in [o.lower() for o in OLD];ok&=r
        print(f"{v:7}{part:6}{c} min dE2000={m:5.1f} need>=12 {'PASS' if r else 'FAIL'}")
print("== info only (cream, gold are neutrals, not label or honey colours) ==")
for n,c in INFO.items():
    print(f"{n:7}{c} min dE2000={min(de(lab(c),lab(o)) for o in OLD):5.1f}")
print("BOTTLE COLOURS ALL PASS" if ok else "BOTTLE COLOURS FAILED")
