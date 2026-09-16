# Grille d'audit

Statuts: `ok` | `manquant` | `incomplet` | `ecart` | `hors champ` | `non verifie`.

Chaque ligne active: statut + preuve (URL, en-tête, extrait ≤ 200 car, ou `probe.json`).

Textes: [cadre-legal.md](cadre-legal.md). Sources: [sources.md](sources.md).

## A. Périmètre

- [ ] URL canonique, chaîne de redirects, code final
- [ ] Acteur classé (asso / EI / société / e-commerce / public / plateforme)
- [ ] Modules actifs listés; les autres en `hors champ` + raison
- [ ] Repo fourni ou `hors champ`

## B. Dispo et bugs

- [ ] Accueil joignable (recouper 403 / timeout, controles-sites)
- [ ] Pages légales en 200, pas une 404 habillée
- [ ] Flux critique (contact, compte, commande) va au bout ou `non verifie`
- [ ] Formulaires: validation vide / invalide, pas de 5xx
- [ ] Liens footer et menu: pas de 404 de masse
- [ ] Console JS (si navigateur): erreurs bloquantes
- [ ] Mobile: overflow, bouton trop petit, contenu coupé (si viewport testé)

## C. Identification (LCEN art. 1-1 / 1-2)

Preuve: page mentions, ou CGV si les mentions y sont. Lien depuis l'accueil. Standard ouvert (HTML lisible, LCEN art. 4).

Ne pas citer « LCEN art. 6 » pour l'éditeur: c'est l'ancien numéro. F37351 / F31228 le font encore.

### Tous les éditeurs professionnels (1-1, I)

- [ ] Lien permanent depuis l'accueil (footer ou équivalent)
- [ ] Téléphone de l'éditeur
- [ ] Directeur ou codirecteur de la publication (1-1, I, 3°). Souvent oublié.
- [ ] Hébergeur: nom ou dénomination, adresse, téléphone (1-1, I, 4°)
- [ ] Stockage éditorial tiers, même gratuit: nommé si un fait le montre (1-1, I, 5°), sinon `hors champ`

Société / personne morale (1-1, I, 2°):

- [ ] Dénomination ou raison sociale, siège
- [ ] Si assujettie RCS/RNE: numéro, capital, adresse du siège
- [ ] Si immatriculée RCS: « RCS + ville du greffe » + SIREN sur le site (C. com R.123-237)

EI (1-1, I, 1° + F31228):

- [ ] Nom, prénoms, domicile, mention EI
- [ ] Numéro d'inscription si assujetti

Association: personne morale. Pas de capital ni RCS sauf activité commerciale. RNA: utile, pas exigé par 1-1.

Éditeur non professionnel: 1-1, II. Anonymat possible. Contrôler seulement hébergeur (nom + adresse).

### En plus si commerce électronique (art. 19) ou si assujetti

- [ ] Courriel (art. 19, 2°; aussi RGPD art. 13)
- [ ] TVA si assujetti (art. 19, 4°)
- [ ] Autorité si activité réglementée
- [ ] Profession réglementée: titre, État, ordre

## D. RGPD / LIL (vue publique)

- [ ] Politique « Données personnelles » / « Confidentialité », distincte des CGV
- [ ] Lien visible sur chaque page contrôlée
- [ ] Responsable du traitement nommé + coordonnées
- [ ] Finalités
- [ ] Bases légales
- [ ] Destinataires / sous-traitants visibles
- [ ] Durées de conservation (ou critères)
- [ ] Droits: accès, rectif, effacement, limitation; opposition / portabilité / retrait si la base le demande
- [ ] Réclamation CNIL
- [ ] Transferts hors UE: dit ou « aucun »
- [ ] DPO: présent, ou `hors champ` si aucun indice d'obligation
- [ ] Formulaire: info au moment de la collecte (lien ou mention courte)
- [ ] Cases consentement: pas pré-cochées
- [ ] Newsletter: opt-in séparé (L.34-5) si la case existe. Compte sans commande ≠ client.

## E. Cookies / art. 82 LIL

- [ ] Inventaire premier chargement (HTTP via probe + DOM si navigateur)
- [ ] Traceurs non exemptés absents avant choix, ou bandeau conforme
- [ ] Si bandeau: tout accepter et tout refuser même niveau
- [ ] Finalités présentées avant un accept global
- [ ] Liste des responsables / lien
- [ ] Fermer le bandeau ≠ accepter
- [ ] Lien « gérer les cookies » après choix
- [ ] Audience: exemption CNIL justifiée (premier parti, pas de cross-site), ou consentement
- [ ] Tags connus (gtag, Meta, TikTok, Hotjar, etc.) absents avant accept
- [ ] Multi-terminaux: `hors champ` sauf si le site le revendique (facultatif, reco janv. 2026)

Sans aucun traceur non exempté: bandeau `hors champ`, noter l'inventaire vide.

## F. Conso / e-commerce (si vente B2C)

- [ ] CGV accessibles avant commande (L.111-1, L.221-5)
- [ ] Prix TTC, frais, délai; taxes et livraison si un prix est affiché (LCEN art. 19)
- [ ] Rétractation 14 j (L.221-18) ou exception L.221-28 citée + formulaire type
- [ ] Depuis le 19 juin 2026: « renoncer au contrat ici » (L.221-21, D.221-5), visible pendant le délai, « confirmer la rétractation »
- [ ] Garanties légales (L.217-3 et vices cachés)
- [ ] Médiateur de la conso (L.616-1)
- [ ] Tunnel: récap avant paiement
- [ ] Si abo / contrat reconduit: « résilier votre contrat » (L.215-1-1, depuis 2023-06-01)

B2B seul: CGV communicables (L.441-1 C. com), pas forcément en ligne. `hors champ` si aucun prix consommateur.

## G. Accessibilité

RGAA (art. 47 loi 2005-102 + décret 2019-768): public, délégataire, ou CA France ≥ 250 M€. Déclaration + schéma + signalement.
EAA (L.412-13): service listé (dont e-commerce B2C) depuis 2025-06-28, hors prestataire < 10 personnes et CA ou bilan ≤ 2 M€. Page publique d'info (annexe D.412-57, France Num): description, norme, conforme/exceptions, dérogations, contact. Pas une déclaration RGAA. Le 28 juin 2030 ne recule pas l'obligation sur le site.

- [ ] Champ classé: RGAA / EAA / les deux / hors champ + raison
- [ ] Si RGAA: déclaration d'accessibilité + mécanisme de signalement
- [ ] Si EAA et effectif établi: page « Information sur l'accessibilité » (annexe D.412-57), pas « déclaration RGAA »
- [ ] Si EAA et effectif inconnu: `non verifie`
- Fumée, toujours utile en `mineur` si pas d'obligation:
- [ ] `html lang`
- [ ] Images de contenu: `alt`
- [ ] Champs: label visible
- [ ] Contraste manifeste (texte gris sur gris)
- [ ] Clavier: focus visible sur le flux principal (si testé)

## H. Pentest limité: transport, en-têtes, session (toujours actif)

Méthode: [pentest-limite.md](pentest-limite.md). Mapping ASVS 5.0 L1 / ANSSI navigateur v2.0. Pas un PASSI.

### H1. Transport

- [ ] HTTPS partout sur le parcours contrôlé; pas de mixte (`html.mixed_http_urls`)
- [ ] Port 80: redirige vers HTTPS (`http_upgrade.upgrades_to_https`)
- [ ] Certificat d'une CA publique; dates; alerte si ≤ 30 j
- [ ] Proto négocié TLS 1.2 ou 1.3 (`tls.protocol`)
- [ ] TLS 1.0 / 1.1 refusés (`tls.legacy_accepted.*.accepted` = false)

### H2. En-têtes navigateur

- [ ] HSTS présent; `max-age` ≥ 31536000 (ASVS v5.0.0-3.4.1). `includeSubDomains` / preload: info
- [ ] `X-Content-Type-Options: nosniff`
- [ ] CSP par en-tête: `default-src` présent, pas `*`; noter `unsafe-inline` / `unsafe-eval`
- [ ] Clickjacking: CSP `frame-ancestors` ou `X-Frame-Options`
- [ ] `Referrer-Policy` (reco ANSSI)
- [ ] `Permissions-Policy`: présence notée, absence = info
- [ ] `Content-Type` présent et cohérent (ASVS v5.0.0-4.1.1)
- [ ] CORS: `Access-Control-Allow-Origin` absent, fixe, ou `*` seulement sur une ressource non sensible. `*` + credentials = écart

### H3. Cookies et formulaires

- [ ] Cookie de session (s'il existe en HTTP): `Secure`, `HttpOnly`, `SameSite`
- [ ] Préfixe `__Host-` / `__Secure-`: info s'il est là (ASVS 3.3.1, pas un échec vitrine)
- [ ] Formulaire: pas d'action `http://`
- [ ] Champ mot de passe: `type=password` (ASVS v6.2.6)
- [ ] POST sensible: champ CSRF nommé présent, ou `non verifie` (jeton peut être header)

### H4. Auth vue (sans compte: rester là)

- [ ] Page login: existe ou `hors champ`
- [ ] Pas de question secrète affichée (ASVS v6.4.2)
- [ ] Comptes par défaut / MFA / politique de mot de passe: `non verifie` sans compte de test fourni

Interdit: payload, fuzz, login forcés, outillage d'exploit.

## K. Debug, fuites, surface connue (toujours actif)

- [ ] `probe.py --surface` a tourné; chaque chemin a un verdict
- [ ] `/.git/HEAD`, `/.svn`: `absent` ou `gated`. `exposed` = critique (ASVS v13.4.1)
- [ ] `/.env` et backups (`backup.sql`, `wp-config.php.bak`): `exposed` = critique. Un 200 HTML catch-all n'est pas un écart
- [ ] phpinfo / server-status / actuator / debug: pas en 200 avec signature
- [ ] Swagger / OpenAPI / GraphQL playground: pas un schéma interne en 200, ou `hors champ` si API publique voulue
- [ ] Stack / mode debug / listing dans le HTML ou une 5xx (`leaks.debug_signatures`)
- [ ] Sourcemap (`sourceMappingURL` / `webpack://`): `mineur` sauf secret dedans
- [ ] Bannière `Server` / `X-Powered-By`: `mineur` / info
- [ ] Secret live dans HTML/JS public: type seulement, jamais la valeur (`leaks.secret_types`)
- [ ] Lien public avec `token=` / `api_key=` en query (ASVS v14.2.1)
- [ ] Scripts tiers: SRI (`integrity`) absent = `mineur` s'il y a un script cross-origin
- [ ] `security.txt`: info (RFC 9116). Absent ≠ écart
- [ ] `robots.txt`: info. Un `Disallow` n'est pas une faille
- [ ] Repo fourni: secret, `.env` commité, `eval` / `innerHTML` sur entrée, SQL concat. Sinon `hors champ`

Catch-all SPA: verdict `catchall`, pas `exposed`.

## L. SEO technique (toujours actif sur une URL publique)

Méthode: [seo.md](seo.md). Search Central, pas un ranking. Préprod / `noindex` voulu: `ok`.

### L1. Document

- [ ] `<title>` présent, non vide, pas générique (`Home`, `Accueil`, `Untitled`, `Sans titre`)
- [ ] Meta description présente sur une page clé (accueil, fiche). Absente = mineur, pas majeur
- [ ] `html lang` (recoupe G)
- [ ] Viewport: `width=device-width` (mobile-first)
- [ ] Soft 404: title / corps « not found » / « page introuvable » en 200 sur une URL censée exister

### L2. Indexation et crawl

- [ ] Pas de `noindex` (meta robots / googlebot ou `X-Robots-Tag`) sur une page de prod publique
- [ ] `robots.txt`: `present` ou info si absent. `Disallow: /` pour `User-agent: *` = majeur en prod
- [ ] Ligne `Sitemap:` dans robots, ou sitemap trouvé autrement
- [ ] Sitemap: urlset / index / texte; `loc` en HTTPS absolu. `http://` dans les loc = mineur
- [ ] `Disallow` n'est pas lu comme un `noindex`

### L3. Canonical

- [ ] Canonical HTML et / ou `Link` HTTP: un seul, pas contradictoire
- [ ] URL absolue `https://`, pas de fragment
- [ ] Relatif: mineur (Google accepte, déconseille)
- [ ] Canonical `http://` depuis une page HTTPS: majeur
- [ ] Absent: info (Google n'exige pas)

### L4. International et structure

- [ ] Si le site a plusieurs langues (fait: chemins `/fr/` `/en/`, sélecteur, ou `hreflang`): annotations présentes ou `non verifie`
- [ ] `hreflang`: self + URLs absolues; retour lu sur `seo.hreflang_return` (3 GET max)
- [ ] `x-default` si sélecteur / fallback, sinon info
- [ ] Au moins un H1 sur l'accueil. Plusieurs H1: info
- [ ] JSON-LD: types notés. Absent = info. `data-vocabulary.org` = info (plus éligible)

Interdit: score inventé, mots-clés prescrits, CWV sans mesure.

## I. Contenu

- [ ] Pas de lorem / page vide présentée comme livrée
- [ ] Mentions d'image / crédit si contenus visiblement tiers
- [ ] Pas de faux avis inventés par l'audit (on ne fabrique rien)

## J. Conditionnel

Activer seulement sur un fait:

- [ ] Chatbot / IA: information dès la première interaction que l'interlocuteur n'est pas humain (AI Act art. 50, depuis 2026-08-02)
- [ ] Compte mineur: âge, parental, pas de pub ciblée évidente
- [ ] Santé: pas de donnée de santé dans un formulaire non cadré
- [ ] Plateforme: voie de signalement de contenu illicite (DSA art. 16)
- [ ] NIS2 / HDS: `hors champ` sauf preuve que l'entité y est
