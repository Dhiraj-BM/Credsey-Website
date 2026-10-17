from PIL import Image
import numpy as np, urllib.request, io, sys
D=r"C:\Users\Asus\Downloads"; O="site/img/"
def clear_white(im, thr=238):
    a=np.array(im.convert("RGBA")).astype(np.float32)
    rgb=a[...,:3]; m=rgb.min(axis=2)
    alpha=np.clip((255-m)/(255-thr),0,1)*255   # soft key near-white
    alpha=np.where(m<thr,255,alpha)
    a[...,3]=np.minimum(a[...,3],alpha)
    return Image.fromarray(a.astype(np.uint8))
lg=clear_white(Image.open(D+r"\CREDSEY Financial Services Logo.png"))
lg=lg.crop(lg.getbbox()); lg.thumbnail((900,900),Image.LANCZOS); lg.save(O+"credsey-logo.png",optimize=True); lg.save(O+"credsey-logo.webp",quality=92)
print("logo",lg.size)
# emblem (C mark) = left part
w,h=lg.size; em=lg.crop((0,0,int(w*0.27),h)); em=em.crop(em.getbbox())
s=max(em.size); sq=Image.new("RGBA",(s,s),(0,0,0,0)); sq.paste(em,((s-em.size[0])//2,(s-em.size[1])//2))
for n in (512,192,32): sq.resize((n,n),Image.LANCZOS).save(O+f"icon-{n}.png")
sq.resize((180,180),Image.LANCZOS).save(O+"apple-touch-icon.png")
sq.resize((48,48),Image.LANCZOS).save("site/favicon.ico",sizes=[(16,16),(32,32),(48,48)])
# white logo for dark footer: navy->white keep gold
a=np.array(lg).astype(np.int16); r,g,b=a[...,0],a[...,1],a[...,2]
blue=(b>r+15)|((r<90)&(g<90)&(b<120))
a[...,0]=np.where(blue,255,r);a[...,1]=np.where(blue,255,g);a[...,2]=np.where(blue,255,b)
Image.fromarray(a.astype(np.uint8)).save(O+"credsey-logo-white.png",optimize=True)
photos={"hero-family":"1780980301761-f6e0fa6f0bdf","personal-loan":"1704088030734-96769c4593a2","business-loan":"1766716946030-5869da2a0ead",
"home-loan":"1723110994499-df46435aa4b3","lap":"1759428679273-11d914866394","gold-loan":"1601121141461-9d6647bca1ed","car-loan":"1652509573480-a190f1c61f6d",
"education-loan":"1571260899304-425eee4c7efc","credit-card":"1656236607879-cd489955e17b","balance-transfer":"1742981365880-698cfb84492d",
"professional":"1771244688590-1e481dba1b5a","wedding":"1764286954620-28029fbae9b6","mother-daughter":"1589169011402-8b2cbd1ee593","home-model":"1560518883-ce09059eeffa"}
for n,i in photos.items():
    req=urllib.request.Request(f"https://images.unsplash.com/photo-{i}?w=1400&q=78&fm=jpg",headers={"User-Agent":"Mozilla/5.0"})
    im=Image.open(io.BytesIO(urllib.request.urlopen(req).read())).convert("RGB")
    im.save(O+n+".webp",quality=74,method=6); print(n,im.size)
og=Image.new("RGB",(1200,630),(10,35,80))
