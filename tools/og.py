"""Generates the social share image site/img/og-cover.jpg."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
og = Image.new("RGB", (W, H), (7, 26, 62)); dr = ImageDraw.Draw(og)
for i in range(H): dr.line([(0, i), (W, i)], fill=(7 + int(4 * i / H), 26 + int(10 * i / H), 62 + int(30 * i / H)))
dr.arc((-300, 180, 1500, 1400), 200, 330, fill=(227, 188, 110), width=4)
card = Image.new("RGB", (820, 330), "white"); lg = Image.open("site/img/credsey-logo.png"); lg.thumbnail((740, 300))
card.paste(lg, ((820 - lg.size[0]) // 2, (330 - lg.size[1]) // 2), lg)
m = Image.new("L", card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *card.size), 28, fill=255)
og.paste(card, ((W - 820) // 2, 120), m)
try: f = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 34)
except OSError: f = ImageFont.load_default()
s = "Personal · Home · Business · Gold Loans  |  Free EMI Calculator"
dr.text(((W - dr.textlength(s, font=f)) / 2, 500), s, fill=(227, 188, 110), font=f)
og.save("site/img/og-cover.jpg", quality=88)
