# Crée les images de partage (img/og-*.png). À lancer avec un serveur local sur public/ :
#   cd public && python3 -m http.server 8765   puis   python3 tools/og_images.py
from playwright.sync_api import sync_playwright
import pathlib
pub=pathlib.Path("/home/claude/kubo-studio/public")
css=f"""
@font-face {{ font-family: B; src: url('/fonts/bricolage.woff2'); font-weight: 200 800; }}
@font-face {{ font-family: I; src: url('/fonts/inter-500.woff2'); }}
body {{ margin:0; width:1200px; height:630px; overflow:hidden; font-family: I; }}
.c {{ width:1200px; height:630px; box-sizing:border-box; padding:70px 80px; display:flex; gap:40px; align-items:center; position:relative; overflow:hidden; }}
.t {{ flex: 1 1 0; min-width: 0; }}
.brand {{ display:flex; align-items:center; gap:14px; font: 800 30px B; letter-spacing:-.02em; margin-bottom:34px; }}
.brand img {{ width:44px; height:44px; }}
h1 {{ font: 800 76px/1.02 B; letter-spacing:-.035em; margin:0 0 22px; }}
p {{ font-size: 28px; margin:0; line-height:1.35; }}
.shot {{ width: 520px; flex:none; border-radius:18px; box-shadow: 0 30px 70px rgba(0,0,0,.25); transform: rotate(-3deg) translateX(40px); }}
.pill {{ display:inline-block; margin-top:30px; padding:10px 20px; border-radius:999px; font: 600 22px I; }}
"""
cards = {
 "og-kubo.png": ("#FAF6F1","#1D1B2E","#615E72", "Des logiciels simples pour la vraie vie.", "MonKiosk pour votre commerce, Pécule pour vos finances.", None, "Fait à Toulouse", "#FBE6DE","#B94F34", "kubo-icon.svg"),
 "og-monkiosk.png": ("#FFEFE7","#1D1B2E","#615E72", "Votre boutique, enfin organisée.", "Planning, équipe, hygiène, stock et ventes.", "img/monkiosk-planning.webp", "Dès 4,99 € / mois · 14 jours gratuits", "#E2603F","#FFFFFF", "monkiosk-logo.svg"),
 "og-pecule.png": ("#E6F5EC","#1D1B2E","#4C5A52", "Vos finances, simplement.", "Comptes, budgets, épargne et vie à plusieurs.", "img/pecule-accueil.webp", "Gratuit pour Windows", "#2E7D57","#FFFFFF", "pecule-logo.png"),
}
with sync_playwright() as pw:
    b=pw.chromium.launch()
    for name,(bg,ink,muted,h,sub,shot,pill,pbg,pfg,logo) in cards.items():
        brand_name = {"og-kubo.png":"Kubo Studio","og-monkiosk.png":"MonKiosk","og-pecule.png":"Pécule"}[name]
        shot_html = f'<img class="shot" src="/{shot}">' if shot else f'<img src="/brand/kubo-icon.svg" style="width:330px;flex:none;margin-right:20px">'
        html=f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div class="c" style="background:{bg};color:{ink}">
        <div class="t"><div class="brand"><img src="/brand/{logo}">{brand_name}</div><h1>{h}</h1><p style="color:{muted}">{sub}</p>
        <span class="pill" style="background:{pbg};color:{pfg}">{pill}</span></div>{shot_html}</div></body></html>"""
        pg=b.new_page(viewport={"width":1200,"height":630})
        (pub/'_og.html').write_text(html, encoding='utf-8'); pg.goto('http://127.0.0.1:8765/_og.html'); pg.wait_for_timeout(900)
        pg.screenshot(path=str(pub/"img"/name)); pg.close()
    b.close()
print("ok")
