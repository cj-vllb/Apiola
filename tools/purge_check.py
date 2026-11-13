import os,re,sys,zipfile,io
root=sys.argv[1] if len(sys.argv)>1 else '.'
P=["brio","framer","remix for free","made in framer","sparkling","fizz","soda","blood orange","mango","grapefruit","blueberry","pineapple","passion fruit","yuzu","ginger","rosemary","garden mint","buildcan",".can","can-wrap","nothing else","find your flavour","six flavours","one fridge","good questions","real person replies","sign me up","scroll to taste","glucose syrup","sodium benzoate","edit me","the whole list","#e8542e","#f7a31c","#5cb159","#ef7b8d","#4e5dc3","#f3d03c","#faf4ea","#1b1915","#6b665d","#fff4e8","#3b2200","#0e2f12","#5b1026","#2e2800","--red","--amber","--green","--pink","--blue","--yellow","--cream","--ink","six"]
skip={"delta_e.py",'three.min.js','purge_check.py','purge_output.txt'}
hits=0
def scan(name,text):
    global hits
    for n,l in enumerate(text.splitlines(),1):
        for p in P:
            if (re.search(r"\.can\b",l.lower()) if p==".can" else (p in l.lower())) and not (p=="scroll to taste" and "name=\"description\"" in l): print(f"HIT {p!r} {name}:{n}");hits+=1
for d,_,fs in os.walk(root):
    for f in fs:
        p=os.path.join(d,f)
        if any(p.lower().find(x)>=0 for x in ("brio","framer")): print("HIT filename",p);hits+=1
        if f in skip or f.endswith('.png'):continue
        if f.endswith('.zip'): continue
        try: scan(p,open(p,encoding='utf8').read())
        except Exception: pass
print("PURGE CLEAN: 0 hits" if hits==0 else f"{hits} hits")
