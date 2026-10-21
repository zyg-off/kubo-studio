#!/usr/bin/env python3
"""Assemble les pages du site.

Chaque fichier de pages/ contient le contenu d'une page, avec en tête un bloc
de réglages (titre, description, page active). Ce script ajoute l'en-tête,
le pied de page et les icônes communes, puis écrit le résultat dans public/.

Utilisation : python3 tools/build.py
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "pages"
OUT = ROOT / "public"
SITE_URL = "https://kubo-studio.kubostudio.workers.dev"
LANGS = ["fr", "en", "pt"]

CHECKOUT_PECULE_PRO = "https://buy.polar.sh/polar_cl_RZquC1pevH3ghLIsdmeln4F2vFGXhXGW9ek2N1QzRuH"
CHECKOUT_PECULE_PRO_YEAR = "https://buy.polar.sh/polar_cl_2uup4r4aYjmyYCtpMZtRg3ZRee5egw7a20tgV4BQhJu"
PORTAL = "https://polar.sh/kubo-studio/portal"
MONKIOSK_DEMO = "https://zyg-off.github.io/MonKiosk/"
MONKIOSK_APP = "https://zyg-off.github.io/MonKiosk/"
MONKIOSK_PC = "https://github.com/zyg-off/MonKiosk/releases/latest/download/MonKiosk-Installer.exe"
PECULE_DOWNLOAD = "https://github.com/zyg-off/pecule/releases/latest/download/Pecule-Setup.exe"
EMAIL = "kubostudio.contact@gmail.com"

LINKS = {
    "CHECKOUT_PECULE_PRO": CHECKOUT_PECULE_PRO,
    "CHECKOUT_PECULE_PRO_YEAR": CHECKOUT_PECULE_PRO_YEAR,
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



# ---------------------------------------------------------------------------
# Textes communs (en-tête, pied de page, cartes de prix) dans les 3 langues
# ---------------------------------------------------------------------------
T = {
    "fr": {
        "home": "Accueil", "pricing": "Tarifs", "help": "Aide", "account": "Espace client", "start": "Commencer",
        "menu": "Ouvrir le menu", "main_menu": "Menu principal", "home_aria": "Kubo Studio, accueil",
        "tagline": "Des logiciels simples pour la vraie vie. Fait à Toulouse.",
        "our_apps": "Nos apps", "faq": "Questions fréquentes", "contact": "Nous contacter", "news": "Nouveautés",
        "guides": "Guides", "legal": "Légal", "legal_notice": "Mentions légales", "terms": "Conditions de vente",
        "privacy": "Confidentialité", "secure": "Paiements sécurisés par Polar", "to_top": "Revenir en haut",
        "lang_label": "Langue", "for_jobs": "Pour votre métier",
        # MonKiosk
        "per_month": "/ mois", "per_emp": "par salarié et par mois", "recommended": "Conseillée",
        "try14": "Essayer 14 jours gratuits", "calc_q": "Combien de salariés dans votre équipe ?",
        "for_n": "Pour", "emps": "salariés", "emp": "salarié", "per_month_total": "/ mois",
        # Pécule
        "pp_desc": "Les quatre fonctions avancées de Pécule, et le soutien au développement de l'app.",
        "billing": "Période de facturation", "monthly": "Mensuel", "yearly": "Annuel", "per_year": "/ an",
        "eq_month": "soit 2 € par mois", "pp_items": ["Tout Pécule gratuit, et en plus :", "Synchro automatique avec votre banque",
        "Vos comptes et budgets sur le téléphone", "Plusieurs profils sur le même PC", "Chiffrement de vos données"],
        "sub_m": "S'abonner · 2,99 € / mois", "sub_y": "S'abonner · 24 € / an",
        "pf_desc": "L'app de finances personnelles pour Windows, gratuite.",
        "pf_items": ["Comptes, budgets, analyses et objectifs", "Import de relevés CSV et OFX", "Courses, repas, foyer et agenda",
                     "Sans publicité, sans limite de durée"],
        "dl_free": "Télécharger gratuitement",
    },
    "en": {
        "home": "Home", "pricing": "Pricing", "help": "Help", "account": "My account", "start": "Get started",
        "menu": "Open the menu", "main_menu": "Main menu", "home_aria": "Kubo Studio, home",
        "tagline": "Simple software for real life. Made in Toulouse, France.",
        "our_apps": "Our apps", "faq": "FAQ", "contact": "Contact us", "news": "What's new",
        "guides": "Guides (FR)", "legal": "Legal", "legal_notice": "Legal notice (FR)", "terms": "Terms of sale (FR)",
        "privacy": "Privacy (FR)", "secure": "Secure payments by Polar", "to_top": "Back to top",
        "lang_label": "Language", "for_jobs": "For your trade (FR)",
        "per_month": "/ month", "per_emp": "per employee per month", "recommended": "Recommended",
        "try14": "Try free for 14 days", "calc_q": "How many employees on your team?",
        "for_n": "For", "emps": "employees", "emp": "employee", "per_month_total": "/ month",
        "pp_desc": "Pécule's four advanced features, and support for the app's development.",
        "billing": "Billing period", "monthly": "Monthly", "yearly": "Yearly", "per_year": "/ year",
        "eq_month": "that's €2 a month", "pp_items": ["Everything in free Pécule, plus:", "Automatic sync with your bank",
        "Your accounts and budgets on your phone", "Several profiles on the same PC", "Encryption of your data"],
        "sub_m": "Subscribe · €2.99 / month", "sub_y": "Subscribe · €24 / year",
        "pf_desc": "The personal finance app for Windows, free.",
        "pf_items": ["Accounts, budgets, analyses and goals", "CSV and OFX statement import", "Shopping, meals, household and calendar",
                     "No ads, no time limit"],
        "dl_free": "Download for free",
    },
    "pt": {
        "home": "Início", "pricing": "Preços", "help": "Ajuda", "account": "Área de cliente", "start": "Começar",
        "menu": "Abrir o menu", "main_menu": "Menu principal", "home_aria": "Kubo Studio, início",
        "tagline": "Software simples para a vida real. Feito em Toulouse.",
        "our_apps": "As nossas apps", "faq": "Perguntas frequentes", "contact": "Contacte-nos", "news": "Novidades",
        "guides": "Guias (FR)", "legal": "Legal", "legal_notice": "Informações legais (FR)", "terms": "Condições de venda (FR)",
        "privacy": "Privacidade (FR)", "secure": "Pagamentos seguros com a Polar", "to_top": "Voltar ao topo",
        "lang_label": "Idioma", "for_jobs": "Para o seu ofício (FR)",
        "per_month": "/ mês", "per_emp": "por funcionário e por mês", "recommended": "Recomendada",
        "try14": "Experimentar 14 dias grátis", "calc_q": "Quantos funcionários tem a sua equipa?",
        "for_n": "Para", "emps": "funcionários", "emp": "funcionário", "per_month_total": "/ mês",
        "pp_desc": "As quatro funções avançadas do Pécule, e o apoio ao desenvolvimento da app.",
        "billing": "Período de faturação", "monthly": "Mensal", "yearly": "Anual", "per_year": "/ ano",
        "eq_month": "ou seja, 2 € por mês", "pp_items": ["Tudo o que o Pécule grátis tem, e mais:", "Sincronização automática com o seu banco",
        "As suas contas e orçamentos no telemóvel", "Vários perfis no mesmo PC", "Encriptação dos seus dados"],
        "sub_m": "Subscrever · 2,99 € / mês", "sub_y": "Subscrever · 24 € / ano",
        "pf_desc": "A app de finanças pessoais para Windows, grátis.",
        "pf_items": ["Contas, orçamentos, análises e objetivos", "Importação de extratos CSV e OFX", "Compras, refeições, casa e agenda",
                     "Sem publicidade, sem limite de tempo"],
        "dl_free": "Descarregar grátis",
    },
}

# Formules MonKiosk : prix de base par commerce et prix par salarié (par mois, TTC)
MONKIOSK_FORMULES = [
    {
        "key": "essentiel", "name": "Essentiel", "base": 4.99, "per": 3.00,
        "desc": {"fr": "L'essentiel pour organiser la boutique et l'équipe.",
                 "en": "The essentials to organise your shop and team.",
                 "pt": "O essencial para organizar a loja e a equipa."},
        "lead": None,
        "items": {"fr": ["Planning, équipe et congés", "Checklists et relevés de température", "Stock, commandes et ventes",
                         "Pertes et invendus", "Ordinateur et téléphone, synchronisés"],
                  "en": ["Schedule, team and leave", "Checklists and temperature logs", "Stock, orders and sales",
                         "Waste and unsold goods", "Computer and phone, in sync"],
                  "pt": ["Horários, equipa e férias", "Checklists e registos de temperatura", "Stock, encomendas e vendas",
                         "Perdas e sobras", "Computador e telemóvel, sincronizados"]},
    },
    {
        "key": "pro", "name": "Pro", "base": 29.00, "per": 2.50, "featured": True,
        "desc": {"fr": "Pour piloter l'équipe et la rentabilité au quotidien.",
                 "en": "To run your team and profitability day to day.",
                 "pt": "Para gerir a equipa e a rentabilidade no dia a dia."},
        "lead": {"fr": "Tout Essentiel, plus :", "en": "Everything in Essentiel, plus:", "pt": "Tudo do Essentiel, e mais:"},
        "items": {"fr": ["Espace salarié et badgeuse", "Coût salarial et rentabilité", "Statistiques et prévisions de ventes",
                         "Registre d'hygiène en PDF", "Export pour l'expert-comptable"],
                  "en": ["Employee space and time clock", "Payroll cost and profitability", "Statistics and sales forecasts",
                         "Hygiene log as PDF", "Export for your accountant"],
                  "pt": ["Área do funcionário e ponto", "Custo salarial e rentabilidade", "Estatísticas e previsões de vendas",
                         "Registo de higiene em PDF", "Exportação para o contabilista"]},
    },
    {
        "key": "premium", "name": "Premium", "base": 49.00, "per": 2.00,
        "desc": {"fr": "Pour les commerces qui veulent tout, ou plusieurs boutiques.",
                 "en": "For shops that want everything, or several locations.",
                 "pt": "Para quem quer tudo, ou tem várias lojas."},
        "lead": {"fr": "Tout Pro, plus :", "en": "Everything in Pro, plus:", "pt": "Tudo do Pro, e mais:"},
        "items": {"fr": ["Documents salariés", "Mode tablette en boutique", "Boutiques regroupées"],
                  "en": ["Employee documents", "In-store tablet mode", "Multi-shop dashboard"],
                  "pt": ["Documentos dos funcionários", "Modo tablet na loja", "Lojas agrupadas"]},
    },
]


def eur(x, lang="fr"):
    if lang == "en":
        return "€" + (f"{x:,.2f}".replace(".00", ""))
    return f"{x:,.2f}".replace(",", " ").replace(".", ",").replace(",00", "") + " €"


def monkiosk_plans(lang="fr"):
    t = T[lang]
    cards = []
    for f in MONKIOSK_FORMULES:
        featured = f.get("featured")
        cls = "plan featured" if featured else "plan"
        badge = f'<span class="badge">{t["recommended"]}</span>' if featured else ""
        lead = f'<li class="lead-li">{f["lead"][lang]}</li>' if f["lead"] else ""
        items = "".join(f"<li>{i}</li>" for i in f["items"][lang])
        btn = "btn-primary" if featured else "btn-light"
        cards.append(f"""<article class="{cls}" data-base="{f['base']}" data-per="{f['per']}">
      {badge}
      <div class="plan-head"><img src="brand/monkiosk-logo.svg" alt=""><div class="plan-name">{f['name']}</div></div>
      <p class="plan-desc">{f['desc'][lang]}</p>
      <div><span class="price">{eur(f['base'], lang)}</span><span class="cadence">{t['per_month']}</span></div>
      <div class="per-line">+ {eur(f['per'], lang)} {t['per_emp']}</div>
      <div class="calc-total" aria-live="polite">{t['for_n']} <b data-n>5</b> {t['emps']} : <b data-total>{eur(f['base'] + 5 * f['per'], lang)}</b> {t['per_month_total']}</div>
      <ul>{lead}{items}</ul>
      <div class="cta"><a class="btn {btn} btn-block" href="{MONKIOSK_APP}"><span class="shine"></span>{t['try14']}<svg class="arrow" aria-hidden="true"><use href="#i-arrow"/></svg></a></div>
    </article>""")
    return f"""<div class="calc" data-calc data-lang="{lang}" data-emp="{t['emp']}" data-emps="{t['emps']}" data-for="{t['for_n']}">
    <label class="calc-label" for="calc-n">{t['calc_q']}</label>
    <div class="calc-row">
      <input type="range" id="calc-n" min="1" max="30" value="5" step="1">
      <output for="calc-n" class="calc-out"><b data-n>5</b> {t['emps']}</output>
    </div>
    <div class="plans plans-3">
    {"".join(cards)}
    </div>
  </div>"""


def pecule_cards(lang="fr"):
    t = T[lang]
    pp = "".join(f"<li>{i}</li>" for i in t["pp_items"])
    pf = "".join(f"<li>{i}</li>" for i in t["pf_items"])
    return f"""<div class="plans">
    <article class="plan featured" data-billing>
      <div class="plan-head"><img src="brand/pecule-logo.png" alt=""><div class="plan-name">Pécule Pro</div></div>
      <p class="plan-desc">{t['pp_desc']}</p>
      <div class="bill-toggle" role="group" aria-label="{t['billing']}">
        <button type="button" data-period="month" aria-pressed="true">{t['monthly']}</button>
        <button type="button" data-period="year" aria-pressed="false">{t['yearly']} <span class="save-chip">−33 %</span></button>
      </div>
      <div data-show="month"><span class="price">{eur(2.99, lang)}</span><span class="cadence">{t['per_month']}</span></div>
      <div data-show="year" hidden><span class="price">{eur(24, lang)}</span><span class="cadence">{t['per_year']}</span><div class="per-line">{t['eq_month']}</div></div>
      <ul>{pp}</ul>
      <div class="cta">
        <a data-show="month" class="btn btn-mint btn-block" href="{CHECKOUT_PECULE_PRO}"><span class="shine"></span>{t['sub_m']}<svg class="arrow" aria-hidden="true"><use href="#i-arrow"/></svg></a>
        <a data-show="year" hidden class="btn btn-mint btn-block" href="{CHECKOUT_PECULE_PRO_YEAR}"><span class="shine"></span>{t['sub_y']}<svg class="arrow" aria-hidden="true"><use href="#i-arrow"/></svg></a>
      </div>
    </article>
    <article class="plan free-card">
      <div class="plan-head"><img src="brand/pecule-logo.png" alt=""><div class="plan-name">Pécule</div></div>
      <p class="plan-desc">{t['pf_desc']}</p>
      <div style="margin-top: 60px"><span class="price">{eur(0, lang)}</span></div>
      <ul>{pf}</ul>
      <div class="cta"><a class="btn btn-outline-light btn-block" href="{PECULE_DOWNLOAD}">{t['dl_free']}</a></div>
    </article>
  </div>"""


# ---------------------------------------------------------------------------
# Comparatif détaillé des formules MonKiosk (repris des modules de l'app)
# formule minimale : "e" Essentiel, "p" Pro, "m" Premium
# ---------------------------------------------------------------------------
MONKIOSK_MODULES = [
    ("group", {"fr": "Organiser l'équipe", "en": "Organise your team", "pt": "Organizar a equipa"}),
    ("e", {"fr": "Planning de l'équipe", "en": "Team schedule", "pt": "Horário da equipa"}),
    ("e", {"fr": "Alertes légales (repos, heures sup, contrats)", "en": "Legal alerts (rest, overtime, contracts)", "pt": "Alertas legais (descanso, horas extra, contratos)"}),
    ("e", {"fr": "Semaines types", "en": "Template weeks", "pt": "Semanas-tipo"}),
    ("e", {"fr": "Congés et absences", "en": "Leave and absences", "pt": "Férias e ausências"}),
    ("e", {"fr": "Disponibilités des salariés", "en": "Staff availability", "pt": "Disponibilidades dos funcionários"}),
    ("e", {"fr": "Échanges de créneaux", "en": "Shift swaps", "pt": "Trocas de turnos"}),
    ("e", {"fr": "Annonces et messagerie d'équipe", "en": "Announcements and team chat", "pt": "Avisos e mensagens da equipa"}),
    ("p", {"fr": "Espace salarié (chacun voit son planning)", "en": "Employee space (everyone sees their schedule)", "pt": "Área do funcionário (cada um vê o seu horário)"}),
    ("p", {"fr": "Badgeuse avec le code du jour", "en": "Time clock with the daily code", "pt": "Ponto com o código do dia"}),
    ("m", {"fr": "Documents salariés (contrats, fiches de paie)", "en": "Employee documents (contracts, payslips)", "pt": "Documentos (contratos, recibos)"}),
    ("group", {"fr": "Boutique et hygiène", "en": "Shop and hygiene", "pt": "Loja e higiene"}),
    ("e", {"fr": "Checklists d'ouverture et de fermeture", "en": "Opening and closing checklists", "pt": "Checklists de abertura e fecho"}),
    ("e", {"fr": "Relevés de température", "en": "Temperature logs", "pt": "Registos de temperatura"}),
    ("e", {"fr": "Rappels si un relevé est oublié", "en": "Reminders when a log is missed", "pt": "Lembretes se faltar um registo"}),
    ("e", {"fr": "Signalements (panne, casse, hygiène)", "en": "Issue reports (breakdown, breakage, hygiene)", "pt": "Ocorrências (avaria, quebra, higiene)"}),
    ("p", {"fr": "Registre d'hygiène en PDF", "en": "Hygiene log as PDF", "pt": "Registo de higiene em PDF"}),
    ("m", {"fr": "Mode tablette en boutique", "en": "In-store tablet mode", "pt": "Modo tablet na loja"}),
    ("group", {"fr": "Stock et ventes", "en": "Stock and sales", "pt": "Stock e vendas"}),
    ("e", {"fr": "Stock et liste de commande", "en": "Stock and order list", "pt": "Stock e lista de encomendas"}),
    ("e", {"fr": "Pertes et invendus", "en": "Waste and unsold goods", "pt": "Perdas e sobras"}),
    ("e", {"fr": "Ventes (chiffre d'affaires, panier moyen)", "en": "Sales (revenue, average basket)", "pt": "Vendas (faturação, cesto médio)"}),
    ("p", {"fr": "Statistiques mensuelles", "en": "Monthly statistics", "pt": "Estatísticas mensais"}),
    ("p", {"fr": "Prévisions de ventes et effectif conseillé", "en": "Sales forecasts and staffing advice", "pt": "Previsões de vendas e equipa aconselhada"}),
    ("group", {"fr": "Gestion", "en": "Management", "pt": "Gestão"}),
    ("p", {"fr": "Coût salarial du planning", "en": "Payroll cost of the schedule", "pt": "Custo salarial do horário"}),
    ("p", {"fr": "Rentabilité par semaine et par mois", "en": "Weekly and monthly profitability", "pt": "Rentabilidade semanal e mensal"}),
    ("p", {"fr": "Export pour l'expert-comptable", "en": "Export for your accountant", "pt": "Exportação para o contabilista"}),
    ("m", {"fr": "Boutiques regroupées (plusieurs commerces)", "en": "Multi-shop dashboard", "pt": "Lojas agrupadas (vários negócios)"}),
]

CMP = {
    "fr": {"feature": "Fonction", "price": "Prix", "per_emp": "par salarié", "yes": "Inclus", "no": "Non inclus", "caption": "Comparatif des formules MonKiosk"},
    "en": {"feature": "Feature", "price": "Price", "per_emp": "per employee", "yes": "Included", "no": "Not included", "caption": "MonKiosk plans compared"},
    "pt": {"feature": "Função", "price": "Preço", "per_emp": "por funcionário", "yes": "Incluído", "no": "Não incluído", "caption": "Comparação das fórmulas MonKiosk"},
}


def monkiosk_compare(lang="fr"):
    c = CMP[lang]
    order = {"e": 0, "p": 1, "m": 2}
    heads = "".join(f'<th scope="col"{" class=pro" if f.get("featured") else ""}>{f["name"]}</th>' for f in MONKIOSK_FORMULES)
    price_row = "".join(f'<td><b>{eur(f["base"], lang)}</b><span class="cmp-sub">+ {eur(f["per"], lang)} {c["per_emp"]}</span></td>' for f in MONKIOSK_FORMULES)
    rows = []
    for level, label in MONKIOSK_MODULES:
        if level == "group":
            rows.append(f'<tr class="cmp-group"><th scope="rowgroup" colspan="4">{label[lang]}</th></tr>')
            continue
        cells = ""
        for i in range(3):
            ok = i >= order[level]
            cells += f'<td class="{"yes" if ok else "no"}"><span aria-hidden="true">{"✓" if ok else "—"}</span><span class="sr-only">{c["yes"] if ok else c["no"]}</span></td>'
        rows.append(f'<tr><th scope="row">{label[lang]}</th>{cells}</tr>')
    return f"""<div class="table-scroll">
    <table class="compare compare-3">
      <caption class="sr-only">{c['caption']}</caption>
      <thead><tr><th scope="col">{c['feature']}</th>{heads}</tr></thead>
      <tbody>
        <tr class="cmp-price"><th scope="row">{c['price']}</th>{price_row}</tr>
        {"".join(rows)}
      </tbody>
    </table>
  </div>"""


# ---------------------------------------------------------------------------
# Quiz « Quelle formule pour moi ? »
# ---------------------------------------------------------------------------
QUIZ = {
    "fr": {
        "q_emp": "Combien de salariés dans votre équipe ?",
        "qs": [
            ("staff", "Vos salariés doivent-ils voir leur planning sur leur téléphone, ou badger leurs heures ?"),
            ("manage", "Voulez-vous suivre le coût salarial, la rentabilité, ou préparer la paie pour votre comptable ?"),
            ("premium", "Avez-vous plusieurs boutiques, ou besoin de ranger les documents des salariés ou d'une tablette en boutique ?"),
        ],
        "yes": "Oui", "no": "Non", "next": "Suivant", "back": "Retour", "step": "Question", "of": "sur",
        "result": "Notre conseil", "for": "Pour", "emps": "salariés", "emp": "salarié", "month": "/ mois",
        "why": {
            "essentiel": "Vous avez besoin de l'essentiel : planning, congés, checklists, hygiène, stock et ventes.",
            "pro": "Vos salariés ont leur propre accès, et vous suivez les coûts et la rentabilité.",
            "premium": "Vous avez besoin de tout, y compris plusieurs boutiques, les documents salariés ou le mode tablette.",
        },
        "cta": "Essayer 14 jours gratuits", "restart": "Recommencer", "compare": "Voir le comparatif",
    },
    "en": {
        "q_emp": "How many employees on your team?",
        "qs": [
            ("staff", "Should your employees see their schedule on their phone, or clock in?"),
            ("manage", "Do you want to track payroll cost and profitability, or prepare payroll for your accountant?"),
            ("premium", "Do you have several shops, or need employee documents or an in-store tablet?"),
        ],
        "yes": "Yes", "no": "No", "next": "Next", "back": "Back", "step": "Question", "of": "of",
        "result": "Our advice", "for": "For", "emps": "employees", "emp": "employee", "month": "/ month",
        "why": {
            "essentiel": "You need the essentials: schedule, leave, checklists, hygiene, stock and sales.",
            "pro": "Your employees get their own access, and you track costs and profitability.",
            "premium": "You need everything, including several shops, employee documents or tablet mode.",
        },
        "cta": "Try free for 14 days", "restart": "Start again", "compare": "See the comparison",
    },
    "pt": {
        "q_emp": "Quantos funcionários tem a sua equipa?",
        "qs": [
            ("staff", "Os seus funcionários devem ver o horário no telemóvel, ou registar o ponto?"),
            ("manage", "Quer acompanhar o custo salarial e a rentabilidade, ou preparar os salários para o contabilista?"),
            ("premium", "Tem várias lojas, ou precisa de guardar documentos dos funcionários ou de um tablet na loja?"),
        ],
        "yes": "Sim", "no": "Não", "next": "Seguinte", "back": "Voltar", "step": "Pergunta", "of": "de",
        "result": "O nosso conselho", "for": "Para", "emps": "funcionários", "emp": "funcionário", "month": "/ mês",
        "why": {
            "essentiel": "Precisa do essencial: horários, férias, checklists, higiene, stock e vendas.",
            "pro": "Os seus funcionários têm acesso próprio, e acompanha os custos e a rentabilidade.",
            "premium": "Precisa de tudo, incluindo várias lojas, documentos dos funcionários ou o modo tablet.",
        },
        "cta": "Experimentar 14 dias grátis", "restart": "Recomeçar", "compare": "Ver a comparação",
    },
}


def monkiosk_quiz(lang="fr"):
    q = QUIZ[lang]
    total = len(q["qs"]) + 1
    plans = {f["key"]: f for f in MONKIOSK_FORMULES}
    steps = [f"""<fieldset class="quiz-step" data-step="0">
      <legend><span class="quiz-count">{q['step']} 1 {q['of']} {total}</span>{q['q_emp']}</legend>
      <div class="quiz-num">
        <button type="button" class="num-btn" data-delta="-1" aria-label="−1">−</button>
        <input type="number" id="quiz-n" min="1" max="200" value="5" inputmode="numeric" aria-label="{q['q_emp']}">
        <button type="button" class="num-btn" data-delta="1" aria-label="+1">+</button>
      </div>
      <div class="quiz-nav"><button type="button" class="btn btn-primary" data-next>{q['next']}<svg class="arrow" aria-hidden="true"><use href="#i-arrow"/></svg></button></div>
    </fieldset>"""]
    for i, (key, text) in enumerate(q["qs"], start=1):
        steps.append(f"""<fieldset class="quiz-step" data-step="{i}" hidden>
      <legend><span class="quiz-count">{q['step']} {i + 1} {q['of']} {total}</span>{text}</legend>
      <div class="quiz-choices">
        <button type="button" class="choice" data-answer="{key}" data-value="1">{q['yes']}</button>
        <button type="button" class="choice" data-answer="{key}" data-value="0">{q['no']}</button>
      </div>
      <div class="quiz-nav"><button type="button" class="btn btn-ghost btn-small" data-back>{q['back']}</button></div>
    </fieldset>""")
    results = []
    for key in ["essentiel", "pro", "premium"]:
        f = plans[key]
        results.append(f"""<div class="quiz-result" data-result="{key}" data-base="{f['base']}" data-per="{f['per']}" hidden>
      <span class="eyebrow">{q['result']}</span>
      <h3>MonKiosk {f['name']}</h3>
      <p>{q['why'][key]}</p>
      <p class="quiz-price"><span data-total>{eur(f['base'] + 5 * f['per'], lang)}</span> {q['month']} <span class="muted">· {q['for']} <span data-n>5</span> <span data-word>{q['emps']}</span></span></p>
      <div class="actions">
        <a class="btn btn-primary" href="{MONKIOSK_APP}"><span class="shine"></span>{q['cta']}<svg class="arrow" aria-hidden="true"><use href="#i-arrow"/></svg></a>
        <a class="btn btn-ghost" href="#comparatif">{q['compare']}</a>
        <button type="button" class="link-btn" data-restart>{q['restart']}</button>
      </div>
    </div>""")
    return f"""<div class="quiz" data-quiz data-emp="{q['emp']}" data-emps="{q['emps']}" aria-live="polite">
    <div class="quiz-bar" aria-hidden="true"><b></b></div>
    {"".join(steps)}
    {"".join(results)}
  </div>"""


# ---------------------------------------------------------------------------
# En-tête, pied de page
# ---------------------------------------------------------------------------
def prefix(lang):
    return "/" if lang == "fr" else f"/{lang}/"


def lang_links(lang, name, available):
    out = []
    for l in LANGS:
        if name not in available.get(l, set()):
            continue
        href = prefix(l) + ("" if name == "index.html" else name)
        cur = ' aria-current="true"' if l == lang else ""
        out.append(f'<a href="{href}" hreflang="{l}" lang="{l}"{cur}>{l.upper()}</a>')
    return "".join(out)


def header(current, lang, name, available):
    t = T[lang]
    nav = [("index", "./", t["home"], None), ("monkiosk", "monkiosk.html", "MonKiosk", "brand/monkiosk-logo.svg"),
           ("pecule", "pecule.html", "Pécule", "brand/pecule-logo.png"), ("tarifs", "tarifs.html", t["pricing"], None),
           ("aide", "aide.html", t["help"], None)]
    items = []
    for key, href, label, icon in nav:
        cur = ' aria-current="page"' if key == current else ""
        ico = f'<img src="{icon}" alt="">' if icon else ""
        items.append(f'<a href="{href}"{cur}>{ico}{label}</a>')
    acc = ' aria-current="page"' if current == "espace" else ""
    langs = lang_links(lang, name, available)
    lang_html = f'<div class="lang-pick" role="group" aria-label="{t["lang_label"]}">{langs}</div>' if langs.count("<a") > 1 else ""
    return f"""{sprite()}
<a class="skip" href="#contenu">{'Aller au contenu' if lang == 'fr' else 'Skip to content' if lang == 'en' else 'Ir para o conteúdo'}</a>
<header class="site-header">
  <div class="wrap nav">
    <a href="./" class="logo" aria-label="{t['home_aria']}"><img src="brand/kubo-icon.svg" alt="">Kubo Studio</a>
    <button class="menu-btn" aria-label="{t['menu']}" aria-expanded="false" aria-controls="nav-links">
      <svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
    </button>
    <nav class="nav-links" id="nav-links" aria-label="{t['main_menu']}">
      {"".join(items)}
      {lang_html}
      <a href="espace-client.html" class="account-link"{acc}><svg aria-hidden="true"><use href="#i-user"/></svg>{t['account']}</a>
      <a href="tarifs.html" class="btn btn-dark btn-small">{t['start']}<svg class="arrow" aria-hidden="true"><use href="#i-arrow"/></svg></a>
    </nav>
  </div>
</header>"""


def footer(lang):
    t = T[lang]
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a href="./" class="logo"><img src="brand/kubo-icon.svg" alt="">Kubo Studio</a>
        <p>{t['tagline']}</p>
      </div>
      <div>
        <h4>{t['our_apps']}</h4>
        <ul>
          <li><a href="monkiosk.html">MonKiosk</a></li>
          <li><a href="pecule.html">Pécule</a></li>
          <li><a href="tarifs.html">{t['pricing']}</a></li>
          <li><a href="nouveautes.html">{t['news']}</a></li>
        </ul>
      </div>
      <div>
        <h4>{t['help']}</h4>
        <ul>
          <li><a href="aide.html">{t['faq']}</a></li>
          <li><a href="aide.html#contact">{t['contact']}</a></li>
          <li><a href="espace-client.html">{t['account']}</a></li>
          <li><a href="guides.html">{t['guides']}</a></li>
        </ul>
      </div>
      <div>
        <h4>{t['legal']}</h4>
        <ul>
          <li><a href="mentions-legales.html">{t['legal_notice']}</a></li>
          <li><a href="conditions.html">{t['terms']}</a></li>
          <li><a href="confidentialite.html">{t['privacy']}</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 Kubo Studio</span>
      <span>{t['secure']}</span>
    </div>
  </div>
</footer>
<button class="to-top" aria-label="{t['to_top']}"><svg width="20" height="20" aria-hidden="true"><use href="#i-up"/></svg></button>
<script src="/site.js" defer></script>"""


# ---------------------------------------------------------------------------
# Données structurées (pour Google)
# ---------------------------------------------------------------------------
def jsonld(kind, lang):
    org = {"@type": "Organization", "name": "Kubo Studio", "url": SITE_URL + "/", "logo": SITE_URL + "/brand/kubo-app-icon-512.png",
           "email": EMAIL, "address": {"@type": "PostalAddress", "addressLocality": "Toulouse", "addressCountry": "FR"}}
    if kind == "org":
        data = dict(org, **{"@context": "https://schema.org"})
    elif kind == "monkiosk":
        data = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "MonKiosk",
                "applicationCategory": "BusinessApplication", "operatingSystem": "Web, Windows, Android, iOS",
                "url": SITE_URL + prefix(lang) + "monkiosk.html", "image": SITE_URL + "/img/og-monkiosk.png",
                "offers": {"@type": "AggregateOffer", "priceCurrency": "EUR", "lowPrice": "4.99", "highPrice": "49.00", "offerCount": 3},
                "publisher": org}
    elif kind == "pecule":
        data = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Pécule",
                "applicationCategory": "FinanceApplication", "operatingSystem": "Windows 10, Windows 11",
                "url": SITE_URL + prefix(lang) + "pecule.html", "image": SITE_URL + "/img/og-pecule.png",
                "offers": [{"@type": "Offer", "price": "0", "priceCurrency": "EUR", "name": "Pécule"},
                           {"@type": "Offer", "price": "2.99", "priceCurrency": "EUR", "name": "Pécule Pro (mensuel)"},
                           {"@type": "Offer", "price": "24.00", "priceCurrency": "EUR", "name": "Pécule Pro (annuel)"}],
                "publisher": org}
    else:
        return ""
    return '\n<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


def faq_jsonld(body):
    qs = re.findall(r"<summary>(.*?)<span class=\"plus\".*?</summary>\s*<div class=\"answer\">(.*?)</div>", body, re.S)
    if not qs:
        return ""
    strip = lambda h: re.sub(r"<[^>]+>", "", h).strip()
    data = {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qs]}
    return '\n<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


# ---------------------------------------------------------------------------
# Modèle de page
# ---------------------------------------------------------------------------
def page(meta, body, lang, name, available):
    title = meta["title"]
    desc = meta["description"]
    noindex = bool(meta.get("noindex"))
    robots = '\n<meta name="robots" content="noindex">' if noindex else ""
    path = prefix(lang) + ("" if name == "index.html" else name)
    url = SITE_URL + path
    og_img = SITE_URL + "/img/" + meta.get("og", "og-kubo.png")
    alternates = ""
    if not noindex:
        for l in LANGS:
            if name in available.get(l, set()):
                alternates += f'\n<link rel="alternate" hreflang="{l}" href="{SITE_URL}{prefix(l)}{"" if name == "index.html" else name}">'
        if name in available.get("fr", set()):
            alternates += f'\n<link rel="alternate" hreflang="x-default" href="{SITE_URL}/{"" if name == "index.html" else name}">'
    ld = jsonld(meta.get("jsonld", ""), lang) + (faq_jsonld(body) if meta.get("faq_ld") else "")
    locale = {"fr": "fr_FR", "en": "en_GB", "pt": "pt_PT"}[lang]
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">{alternates}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Kubo Studio">
<meta property="og:locale" content="{locale}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#FAF6F1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#14131B" media="(prefers-color-scheme: dark)">{robots}
<link rel="icon" href="/brand/kubo-icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/brand/kubo-app-icon-512.png">
<link rel="preload" href="/fonts/bricolage.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/inter-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/site.css">{ld}
</head>
<body class="{meta.get('body_class', '')}">
{header(meta['current'], lang, name, available)}
<main id="contenu">
{body}
</main>
{footer(lang)}
</body>
</html>
"""


ROOT_ONLY = {"mentions-legales.html", "conditions.html", "confidentialite.html", "404.html"}


def absolutize(html, lang, available):
    """Chemins absolus : les images et styles depuis la racine, les pages dans la bonne langue."""
    html = re.sub(r'((?:src|href|data-src|data-zoom|poster)=")(brand|img|fonts|video)/', r'\1/\2/', html)
    pre = prefix(lang)

    def fix(m):
        attr, target, anchor = m.group(1), m.group(2), m.group(3) or ""
        if target == "./":
            return f'{attr}"{pre}{anchor}"'
        if target in available.get(lang, set()):
            return f'{attr}"{pre}{"" if target == "index.html" else target}{anchor}"'
        return f'{attr}"/{target}{anchor}"'
    return re.sub(r'(href=)"(\./|[a-z0-9-]+\.html)(#[^"]*)?"', fix, html)


def sources():
    """Les pages de chaque langue : pages/*.html (fr), pages/en/*.html, pages/pt/*.html."""
    out = {}
    for lang in LANGS:
        folder = SRC if lang == "fr" else SRC / lang
        out[lang] = sorted(folder.glob("*.html")) if folder.exists() else []
    return out


def main():
    srcs = sources()
    available = {lang: {p.name for p in files} for lang, files in srcs.items()}
    available["fr"] |= ROOT_ONLY
    sitemap = []
    for lang, files in srcs.items():
        dest = OUT if lang == "fr" else OUT / lang
        dest.mkdir(exist_ok=True)
        for src in files:
            text = src.read_text(encoding="utf-8")
            m = re.match(r"<!--\n(.*?)\n-->\n", text, re.S)
            meta = dict(line.split(": ", 1) for line in m.group(1).splitlines())
            body = text[m.end():]
            links = dict(LINKS, MONKIOSK_PLANS=monkiosk_plans(lang), PECULE_PLANS=pecule_cards(lang),
                         MONKIOSK_COMPARE=monkiosk_compare(lang), MONKIOSK_QUIZ=monkiosk_quiz(lang))
            for k, v in links.items():
                body = body.replace("{{" + k + "}}", v)
            left = re.findall(r"\{\{[A-Z_]+\}\}", body)
            if left:
                raise SystemExit(f"{lang}/{src.name}: lien inconnu {left}")
            html = absolutize(page(meta, body, lang, src.name, available), lang, available)
            (dest / src.name).write_text(html, encoding="utf-8")
            if not meta.get("noindex"):
                sitemap.append(prefix(lang) + ("" if src.name == "index.html" else src.name))
            print("écrit", ("" if lang == "fr" else lang + "/") + src.name)
    for legal in ["mentions-legales.html", "conditions.html", "confidentialite.html"]:
        sitemap.append("/" + legal)
    urls = "".join(f"  <url><loc>{SITE_URL}{p}</loc></url>\n" for p in sitemap)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    print("écrit sitemap.xml et robots.txt")


if __name__ == "__main__":
    main()
