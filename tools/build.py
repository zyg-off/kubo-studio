#!/usr/bin/env python3
"""Assemble les pages du site.

Chaque fichier de pages/ contient le contenu d'une page, avec en tête un bloc
de réglages (titre, description, page active). Ce script ajoute l'en-tête,
le pied de page et les icônes communes, puis écrit le résultat dans public/.

Utilisation : python3 tools/build.py
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "pages"
OUT = ROOT / "public"

CHECKOUT_MONKIOSK = "https://buy.polar.sh/polar_cl_KcnMWCV5C0ZpahK6hqf24pj72wu6yWNPwiVXa0wUJna"
CHECKOUT_PECULE_PRO = "https://buy.polar.sh/polar_cl_RZquC1pevH3ghLIsdmeln4F2vFGXhXGW9ek2N1QzRuH"
PORTAL = "https://polar.sh/kubo-studio/portal"
MONKIOSK_DEMO = "https://zyg-off.github.io/MonKiosk/"
MONKIOSK_APP = "https://zyg-off.github.io/MonKiosk/"
MONKIOSK_PC = "https://github.com/zyg-off/MonKiosk/releases/latest/download/MonKiosk-Installer.exe"
PECULE_DOWNLOAD = "https://github.com/zyg-off/pecule/releases/latest/download/Pecule-Setup.exe"
EMAIL = "kubostudio.contact@gmail.com"

LINKS = {
    "CHECKOUT_MONKIOSK": CHECKOUT_MONKIOSK,
    "CHECKOUT_PECULE_PRO": CHECKOUT_PECULE_PRO,
    "PORTAL": PORTAL,
    "MONKIOSK_DEMO": MONKIOSK_DEMO,
    "MONKIOSK_APP": MONKIOSK_APP,
    "MONKIOSK_PC": MONKIOSK_PC,
    "PECULE_DOWNLOAD": PECULE_DOWNLOAD,
    "EMAIL": EMAIL,
}

# Icônes au trait, réutilisées avec <svg><use href="#i-nom"/></svg>
ICONS = {
    "arrow": '<path d="M4 10h11m-4.5-4.5L15 10l-4.5 4.5"/>',
    "check": '<path d="M5 10.5l3.2 3.2L15 7"/>',
    "calendar": '<rect x="3" y="4.5" width="14" height="12.5" rx="2"/><path d="M3 8.5h14M7 2.5v4M13 2.5v4"/>',
    "users": '<circle cx="7.5" cy="7" r="2.8"/><path d="M2.5 16.5c.6-2.8 2.7-4.3 5-4.3s4.4 1.5 5 4.3"/><path d="M13 4.5a2.8 2.8 0 0 1 0 5.2M14.5 12.4c1.6.5 2.7 1.9 3 4.1"/>',
    "tasks": '<rect x="3" y="3" width="14" height="14" rx="3"/><path d="M6.5 10l2.5 2.5 4.5-5"/>',
    "box": '<path d="M3 6.5L10 3l7 3.5v7L10 17l-7-3.5z"/><path d="M3 6.5L10 10l7-3.5M10 10v7"/>',
    "chart": '<path d="M3.5 16.5V9M8.5 16.5V4M13.5 16.5v-6M17 16.5H2"/>',
    "home": '<path d="M3 9l7-5.5L17 9v7.5a.8.8 0 0 1-.8.8H12.5v-5h-5v5H3.8a.8.8 0 0 1-.8-.8z"/>',
    "thermo": '<path d="M8 3.5a2 2 0 0 1 4 0v8.2a3.6 3.6 0 1 1-4 0z"/><path d="M10 9v5"/>',
    "bell": '<path d="M5 13.5V9a5 5 0 0 1 10 0v4.5l1.5 1.5h-13z"/><path d="M8.5 17.5a1.6 1.6 0 0 0 3 0"/>',
    "phone": '<rect x="6" y="2.5" width="8" height="15" rx="2"/><path d="M9 15h2"/>',
    "pc": '<rect x="2.5" y="3.5" width="15" height="10" rx="1.5"/><path d="M7 17h6M10 13.5V17"/>',
    "shield": '<path d="M10 2.5l6 2.3v4.7c0 3.7-2.6 6.5-6 8-3.4-1.5-6-4.3-6-8V4.8z"/><path d="M7.3 10l2 2 3.6-3.8"/>',
    "bank": '<path d="M2.5 7.5L10 3l7.5 4.5M4 7.5v7M8 7.5v7M12 7.5v7M16 7.5v7M2.5 16.5h15"/>',
    "lock": '<rect x="4" y="9" width="12" height="8.5" rx="2"/><path d="M6.5 9V6.5a3.5 3.5 0 0 1 7 0V9"/>',
    "cart": '<path d="M2.5 3.5h2.2l2 9.5h8.6l1.8-6.8H5.5"/><circle cx="8" cy="16.3" r="1.2"/><circle cx="14" cy="16.3" r="1.2"/>',
    "mail": '<rect x="2.5" y="4.5" width="15" height="11" rx="2"/><path d="M3 5.5l7 5.5 7-5.5"/>',
    "gift": '<rect x="3" y="8" width="14" height="9" rx="1.5"/><path d="M2.5 5.5h15V8h-15zM10 5.5V17M10 5.5C9 3 6 2.5 6 4.3S9 5.5 10 5.5c1 0 4-.6 4-1.2S11 3 10 5.5"/>',
    "target": '<circle cx="10" cy="10" r="7"/><circle cx="10" cy="10" r="3.5"/><circle cx="10" cy="10" r=".6"/>',
    "sparkle": '<path d="M10 2.5l1.7 4.6 4.8 1.7-4.8 1.7L10 15l-1.7-4.5L3.5 8.8l4.8-1.7z"/><path d="M15.5 13.5l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z"/>',
    "globe": '<circle cx="10" cy="10" r="7.5"/><path d="M2.5 10h15M10 2.5c2.2 2 3.2 4.5 3.2 7.5s-1 5.5-3.2 7.5c-2.2-2-3.2-4.5-3.2-7.5s1-5.5 3.2-7.5z"/>',
    "help": '<circle cx="10" cy="10" r="7.5"/><path d="M7.8 7.8a2.3 2.3 0 1 1 3.2 2.1c-.6.3-1 .8-1 1.5v.4M10 14.3v.2"/>',
    "card": '<rect x="2.5" y="4.5" width="15" height="11" rx="2"/><path d="M2.5 8.5h15M5.5 12.5h3"/>',
    "refresh": '<path d="M16 10a6 6 0 1 1-1.8-4.3M16 3.5v3.5h-3.5"/>',
    "download": '<path d="M10 3v10M5.5 9l4.5 4.5L14.5 9M3.5 16.5h13"/>',
    "doc": '<path d="M5 2.5h6.5L15.5 6.5v11H5z"/><path d="M11 2.5V7h4.5M7.5 10.5h5M7.5 13.5h5"/>',
    "heart": '<path d="M10 16.5s-6.5-3.8-6.5-8.3A3.6 3.6 0 0 1 10 6a3.6 3.6 0 0 1 6.5 2.2c0 4.5-6.5 8.3-6.5 8.3z"/>',
    "megaphone": '<path d="M3 8.5v3h3l6.5 4v-11L6 8.5z"/><path d="M15 7.5a3.5 3.5 0 0 1 0 5"/>',
    "clock": '<circle cx="10" cy="10" r="7.5"/><path d="M10 5.5V10l3 2"/>',
    "leaf": '<path d="M4 16c0-7 4.5-11.5 12-12-.3 7.4-4.8 12-12 12z"/><path d="M4 16l6.5-6.5"/>',
    "smile": '<circle cx="10" cy="10" r="7.5"/><path d="M7 11.5a3.5 3.5 0 0 0 6 0M7.5 7.8v.2M12.5 7.8v.2"/>',
    "up": '<path d="M10 16V4m-5 5 5-5 5 5"/>',
    "user": '<circle cx="10" cy="6.8" r="3.3"/><path d="M3.5 17.2c.8-3.3 3.4-5.2 6.5-5.2s5.7 1.9 6.5 5.2"/>',
    "key": '<circle cx="6.5" cy="13.5" r="3.5"/><path d="M9 11l7.5-7.5M13.5 6.5l2 2M15.5 4.5l1.5 1.5"/>',
    "receipt": '<path d="M5 2.5h10v15l-2.5-1.5-2.5 1.5-2.5-1.5L5 17.5z"/><path d="M8 7h4M8 10.5h4"/>',
}


def sprite():
    syms = "".join(
        f'<symbol id="i-{k}" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{v}</symbol>'
        for k, v in ICONS.items()
    )
    return f'<svg width="0" height="0" style="position:absolute" aria-hidden="true">{syms}</svg>'


NAV = [
    ("index", "./", "Accueil", None),
    ("monkiosk", "monkiosk.html", "MonKiosk", "brand/monkiosk-logo.svg"),
    ("pecule", "pecule.html", "Pécule", "brand/pecule-logo.png"),
    ("tarifs", "tarifs.html", "Tarifs", None),
    ("aide", "aide.html", "Aide", None),
]


def header(current):
    items = []
    for key, href, label, icon in NAV:
        cur = ' aria-current="page"' if key == current else ""
        ico = f'<img src="{icon}" alt="">' if icon else ""
        items.append(f'<a href="{href}"{cur}>{ico}{label}</a>')
    acc = ' aria-current="page"' if current == "espace" else ""
    return f"""{sprite()}
<header class="site-header">
  <div class="wrap nav">
    <a href="./" class="logo" aria-label="Kubo Studio, accueil"><img src="brand/kubo-icon.svg" alt="">Kubo Studio</a>
    <button class="menu-btn" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="nav-links">
      <svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
    </button>
    <nav class="nav-links" id="nav-links" aria-label="Menu principal">
      {"".join(items)}
      <a href="espace-client.html" class="account-link"{acc}><svg aria-hidden="true"><use href="#i-user"/></svg>Espace client</a>
      <a href="tarifs.html" class="btn btn-dark btn-small">Commencer<svg class="arrow" aria-hidden="true"><use href="#i-arrow"/></svg></a>
    </nav>
  </div>
</header>"""


FOOTER = f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a href="./" class="logo"><img src="brand/kubo-icon.svg" alt="">Kubo Studio</a>
        <p>Des logiciels simples pour la vraie vie. Fait à Toulouse.</p>
      </div>
      <div>
        <h4>Nos apps</h4>
        <ul>
          <li><a href="monkiosk.html">MonKiosk</a></li>
          <li><a href="pecule.html">Pécule</a></li>
          <li><a href="tarifs.html">Tarifs</a></li>
        </ul>
      </div>
      <div>
        <h4>Aide</h4>
        <ul>
          <li><a href="aide.html">Questions fréquentes</a></li>
          <li><a href="aide.html#contact">Nous contacter</a></li>
          <li><a href="espace-client.html">Espace client</a></li>
        </ul>
      </div>
      <div>
        <h4>Légal</h4>
        <ul>
          <li><a href="mentions-legales.html">Mentions légales</a></li>
          <li><a href="conditions.html">Conditions de vente</a></li>
          <li><a href="confidentialite.html">Confidentialité</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 Kubo Studio</span>
      <span>Paiements sécurisés par Polar</span>
    </div>
  </div>
</footer>
<button class="to-top" aria-label="Revenir en haut"><svg width="20" height="20" aria-hidden="true"><use href="#i-up"/></svg></button>
<script src="site.js" defer></script>"""


def page(meta, body):
    title = meta["title"]
    robots = '\n<meta name="robots" content="noindex">' if meta.get("noindex") else ""
    desc = meta["description"]
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="brand/kubo-app-icon-512.png">
<meta name="theme-color" content="#FAF6F1">{robots}
<link rel="icon" href="brand/kubo-icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="brand/kubo-app-icon-512.png">
<link rel="preload" href="fonts/bricolage.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/inter-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="site.css">
</head>
<body class="{meta.get('body_class', '')}">
{header(meta['current'])}
<main>
{body}
</main>
{FOOTER}
</body>
</html>
"""


def main():
    for src in sorted(SRC.glob("*.html")):
        text = src.read_text(encoding="utf-8")
        m = re.match(r"<!--\n(.*?)\n-->\n", text, re.S)
        meta = dict(line.split(": ", 1) for line in m.group(1).splitlines())
        body = text[m.end():]
        for k, v in LINKS.items():
            body = body.replace("{{" + k + "}}", v)
        left = re.findall(r"\{\{[A-Z_]+\}\}", body)
        if left:
            raise SystemExit(f"{src.name}: lien inconnu {left}")
        (OUT / src.name).write_text(page(meta, body), encoding="utf-8")
        print("écrit", src.name)


if __name__ == "__main__":
    main()
