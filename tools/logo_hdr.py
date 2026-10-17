from PIL import Image
lg=Image.open("site/img/credsey-logo.png"); w,h=lg.size
# drop the small tagline row so the wordmark reads at header size
c=lg.crop((0,0,w,int(h*0.83))); c=c.crop(c.getbbox()); c.save("site/img/credsey-logo-hdr.png",optimize=True); c.save("site/img/credsey-logo-hdr.webp",quality=92); print(c.size)
