# Kubo Studio

Site officiel de Kubo Studio — des logiciels simples pour la vraie vie.
MonKiosk, Pécule et les prochaines apps. Fait à Toulouse.

- Hébergement : Cloudflare Workers (déploiement automatique depuis la branche `main`, fichiers du site dans `public/`)
- Paiements : Polar

## Organisation

- `pages/` : le contenu de chaque page en français ; `pages/en/` et `pages/pt/` : les versions anglaise et portugaise (même nom de fichier).
- `tools/build.py` : ajoute l'en-tête, le pied de page et les icônes communes, et remplace les liens (`{{CHECKOUT_MONKIOSK}}`, `{{PORTAL}}`…), puis écrit les pages dans `public/`.
- `public/site.css`, `public/site.js` : le style et les animations communs.
- `public/img/` : les captures d'écran des apps.
- `public/mentions-legales.html`, `conditions.html`, `confidentialite.html`, `404.html` : pages écrites directement dans `public/`.

## Modifier une page

1. Modifier le fichier dans `pages/` (ou les liens en haut de `tools/build.py`).
2. Lancer `python3 tools/build.py`.
3. Envoyer les modifications sur `main` : Cloudflare met le site à jour.
