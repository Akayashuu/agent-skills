---
name: audit-fr
description: Use when reviewing a French-facing website before launch or delivery: bugs, limited surface pentest (TLS, headers, debug leaks, known paths), LCEN identification, RGPD/cookies, consumer law, accessibility (RGAA/EAA), and technical SEO. Observation and evidence only: no payloads, not legal advice, not a PASSI pentest, not a ranking audit.
---

# Audit web France

Revue factuelle d'un site ou d'une app destinés au public français: bugs, pentest limité (surface / debug / hygiène), identification, RGPD, cookies, conso, accessibilité, SEO technique. Ce n'est pas un avis juridique, pas un test d'intrusion PASSI, et pas un audit de ranking. Chaque constat a une preuve (URL, en-tête, extrait, capture) et un texte de référence. Pas de preuve = pas de constat, ou statut `non verifie`.

Cadre et sources: [references/cadre-legal.md](references/cadre-legal.md). Sécu: [references/pentest-limite.md](references/pentest-limite.md). SEO: [references/seo.md](references/seo.md). URLs relues: [references/sources.md](references/sources.md). Grille: [references/grille.md](references/grille.md). Rapport: [templates/rapport.md](templates/rapport.md).

## When to Use

- Review d'un site avant livraison ou mise en ligne.
- Audit global: bugs, pentest limité, RGPD, mentions, cookies, accessibilité, SEO technique.
- Contrôle ciblé: page légale, bandeau cookies, formulaire, surface sécu / debug, indexation.

Don't use for: avis juridique opposable; pentest avec exploitation, payload, fuzz, brute-force; prestation PASSI; promesse de position / trafic; revue de code interne sans URL publique ou de préprod.

## Prerequisites

- URL publique, ou dépôt + URL de préprod. Sans cible, s'arrêter.
- Classer l'acteur avant de cocher la grille: association, EI, société, e-commerce B2C, service public, plateforme.
- Outils: `python3` (stdlib), un GET HTTP. Navigateur si disponible. Sans navigateur, le sondage HTTP reste valable et le JS n'est pas observé.
- Ne jamais coller mot de passe, cookie de session, ni clé dans le rapport.

## How to Run

```bash
python3 skills/audit-fr/scripts/probe.py "https://exemple.fr" -o ./audit-probe.json
```

Puis suivre la Procedure. Rapport dans `./audit-fr-<slug>-<date>.md`.

## Quick Reference

| Action | Commande |
|---|---|
| Surface HTTP / TLS / cookies / liens légaux / chemins connus / SEO | `python3 skills/audit-fr/scripts/probe.py URL -o probe.json` |
| Accueil seulement (pas de liste de chemins) | `python3 skills/audit-fr/scripts/probe.py URL --no-surface` |
| Relire un certificat / proto TLS | `probe.json` → `tls` (`protocol`, `legacy_accepted`, `days_left`) |
| Relire fuites / surface | `probe.json` → `leaks`, `surface`, `http_upgrade` |
| Relire SEO | `probe.json` → `seo` (`title`, `canonical`, `robots`, `sitemap`, `hreflang`, `flags`) |
| Tests offline du sondeur | `python3 skills/audit-fr/scripts/test_probe.py` |

## Procedure

### 1. Cadrer

Noter: URL, repo s'il est fourni, date UTC, acteur, ce qui est en ligne vs en préprod. Activer seulement les modules de la grille qui s'appliquent (une asso vitrine n'a pas de CGV B2C; un e-commerce si).

Fait quand: le rapport a une ligne Acteur + Modules actifs, sans module hors champ coché comme échec.

### 2. Sonder la surface

Lancer `probe.py` sur l'accueil, puis sur `/mentions-legales`, `/politique-de-confidentialite` (et variantes: `/legal`, `/privacy`, `/cookies`, `/cgv`, `/accessibilite`). Suivre la chaîne de redirects. Recouper un 403 / timeout avant d'écrire « down ».

Fait quand: `probe.json` existe et chaque URL sondée a un code final.

### 3. Identifier et pages légales

Contrôler accessibilité permanente (lien footer ou équivalent sur l'accueil) et le contenu attendu pour l'acteur. Source de vérité: LCEN art. 1-1 / 1-2 (Légifrance). F37351 / F31228 listent encore l'ancien art. 6: utiles pour la liste, pas pour le numéro. Exiger le directeur de la publication (1-1, I, 3°). Détail dans la grille module C.

Fait quand: chaque mention obligatoire est `ok`, `manquant`, `incomplet`, ou `non applicable`, avec extrait ou URL.

### 4. RGPD et cookies (vue publique)

Politique distincte des CGV. Formulaires: information au moment de la collecte. Bandeau: refus aussi simple que l'acceptation; pas de traceur non exempté avant choix. Relire `probe.json` → `cookies` et `trackers` (premier GET, sans JS). Si navigateur: charger l'accueil sans cliquer, lister cookies et scripts tiers, puis tester « tout refuser ».

Fait quand: le rapport dit ce qui part avant consentement, avec noms de cookies / domaines, ou dit clairement « JS non observé ».

### 5. Bugs, pentest limité, debug

Lire [references/pentest-limite.md](references/pentest-limite.md). Cocher H puis K.

1. Relire `probe.json`: `tls`, `security_headers`, `http_upgrade`, `cookies`, `html.forms`.
2. Surface: chaque ligne `surface[]` a un verdict. `exposed` avec signature = constat. `catchall` / `gated` / `absent` = pas un écart.
3. Fuites: `leaks.debug_signatures` et `leaks.secret_types` (type seulement). Une 5xx ou une 404 habillée: même scan.
4. Flux principal et pages légales: liens cassés, formulaires, pas de mixte.
5. Repo fourni: revue statique (secrets, `eval`, SQL concat). Pas de payload.
6. TLS ≤ 30 j: le noter; ne pas engager un renouvellement payant sans accord.

Fait quand: chaque trou H/K a une preuve reproduisible, ou le point est `non verifie`. Zéro valeur secrète dans le markdown.

### 6. SEO technique

Lire [references/seo.md](references/seo.md). Cocher L. Relire `probe.json` → `seo` et `seo.flags`.

1. Accueil: title, meta description, `html lang`, viewport, H1.
2. Indexation: `noindex` / `X-Robots-Tag`. En préprod, `noindex` = `ok`.
3. Canonical: HTTPS, absolu, pas de fragment, pas de conflit HTML vs `Link`.
4. `robots.txt` et sitemap (déjà dans `surface`). `Disallow: /` sur une prod publique = écart. `Disallow` ≠ `noindex`.
5. Si `hreflang` présent: self + URLs absolues; lire `hreflang_return` (3 GET max).
6. JSON-LD: types seulement. Absent = info. CWV = `non verifie`.
7. Autre page sondée (mentions, locale): title distinct si le HTML l'est. Un SPA catch-all: le dire.

Fait quand: chaque case L active a un statut + preuve, ou `non verifie`. Aucun constat « ça ne ranke pas ».

### 7. Modules conditionnels

E-commerce / abo: CGV, prix TTC, rétractation 14 j, médiateur, « résilier votre contrat » si abo (depuis 2023-06-01), « renoncer au contrat ici » si vente en ligne (depuis 2026-06-19). Accessibilité: EAA / RGAA seulement si le champ s'applique; sinon fumée (contraste, labels, clavier) en `mineur` / reco. IA (art. 50 depuis 2026-08-02), santé, mineurs, plateforme: voir cadre-legal.

Fait quand: chaque module inactif est marqué `hors champ` avec la raison.

### 8. Rédiger

Remplir [templates/rapport.md](templates/rapport.md). Sévérités: `critique` (donnée ou paiement exposé, auth cassée, infraction manifeste + preuve), `majeur` (obligation absente), `mineur` (incomplet / hygiène), `info` (hors champ, outil manquant). Relire: zéro constat sans preuve. Publication du rapport ou envoi au client: accord de l'éditeur.

Fait quand: le fichier rapport existe, les totaux du tableau égalent les constats listés, et la cible a été relue (probe + pages légales) après rédaction.

## Pitfalls

- Identification éditeur = LCEN art. 1-1 / 1-2 (SREN, 23 mai 2024). F37351 / F31228 citent encore l'art. 6. Légifrance gagne. Le directeur de publication est obligatoire (1-1, I, 3°); les fiches SP ne le listent pas.
- Courriel et TVA: pas dans 1-1. Art. 19 (e-commerce) et RGPD art. 13.
- L.34-5: 75 000 € PP / 375 000 € PM. Pas 15 000 € (erreur fréquente).
- Rétractation en ligne (L.221-21) en vigueur depuis le 19 juin 2026. Résiliation abo (L.215-1-1) depuis le 1er juin 2023. Ce n'est pas le même bouton.
- Premier GET sans JS: les cookies et tags posés en JavaScript n'apparaissent pas. Le dire.
- Absence de bandeau ≠ écart: un site sans traceur non exempté n'a pas à en afficher un. Fermer le bandeau = refus.
- Consentement multi-terminaux: facultatif (reco CNIL janv. 2026). Ne pas le cocher comme manquant.
- Micro-entreprise prestataire (< 10 personnes et CA ou bilan ≤ 2 M€, L.412-13): EAA hors champ. Ne pas inventer l'effectif. RGAA ≠ EAA (250 M€ / public vs service listé). Un e-commerce privé n'a pas à publier une déclaration RGAA. Le délai 2030 vise les produits déjà utilisés, pas le site.
- EAA, sanction: R.451-4-I = contravention 5e classe (fiche DGCCRF). Corps de R.451-4 souvent derrière Cloudflare. Montants lus sur France Num (17 déc. 2025) et ecologie.gouv.fr: 1 500 € / 3 000 € récidive (PP), 7 500 € / 15 000 € récidive (PM), cumulables par service et par obligation. Aligné CP 131-13, 131-41, 132-11, 132-15. Ne pas écrire ces montants comme s'ils figuraient dans le corps de R.451-4.
- Ce skill ne « valide » pas un traitement interne (registre, DPA, 72 h). Vue publique seulement, sauf si l'éditeur fournit les docs internes.
- Pas d'exploit, pas de scan agressif, pas de mot de passe dans le livrable. Chemins GET: liste figée de `probe.py`. On n'ajoute pas un path traversal ni un paramètre crafté.
- Catch-all SPA (200 HTML = accueil sur `/.env`): pas un secret exposé.
- HSTS / CSP absents sur une vitrine: `mineur`, pas `critique`. Cookie de session sans `Secure` sur un flux compte: `critique`.
- TLS 1.0/1.1: un handshake de config (refus/accepté). Pas un scan de suites.
- Auth L1 (longueur mdp, MFA, comptes par défaut): `non verifie` sans compte de test fourni. On n'essaie aucun mot de passe.
- Ce skill n'est pas une portée PASSI (archi / conf machine / code / intrusion / orga). Un client qui demande « un pentest »: revue de surface, le dire.
- SEO: Search Central, pas un blog. Canonical / sitemap / JSON-LD absents = info, sauf conflit ou `noindex` de prod. `Disallow` ≠ masquer une URL. Ranking, backlinks, CWV: hors sondeur.
- Title générique (`Home`, `Accueil`): mineur. Title vide sur l'accueil public: majeur. Google peut réécrire le title link.

## Verification

- `probe.py` a tourné sur l'accueil (sortie JSON lue, pas inventée). `tls` + `surface` + `leaks` + `seo` présents sauf `--no-surface` (seo HTML reste).
- `python3 skills/audit-fr/scripts/test_probe.py` passe si le sondeur a été modifié.
- Chaque case de la grille active (dont H, K et L) a un statut.
- Chaque constat critique/majeur a URL + extrait ou en-tête.
- Totaux du rapport = nombre de constats.
- Aucune clé ni session dans le markdown.
