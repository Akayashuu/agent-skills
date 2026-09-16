# Cadre: audit web France

Sources relues le 2026-09-16. URLs et dates: [sources.md](sources.md). Ce fichier oriente la grille. Il ne remplace pas le texte. Ce n'est pas un avis d'avocat.

## Ce que l'audit voit

Vue publique du service (pages, en-têtes, cookies HTTP, éventuellement DOM). Pas le registre des traitements, pas les contrats sous-traitants, pas le dossier CNIL.

## Qualification de l'acteur

| Acteur | Modules de base | Modules en plus |
|---|---|---|
| Association / vitrine | C, D si collecte, E si traceurs, B, H, K, L | G: fumée seulement, sauf mission de service public |
| EI / société vitrine | C, D, E, B, H, K, L | F si vente à un consommateur |
| E-commerce B2C | C, D, E, F, B, H, K, L | G si EAA applicable; résiliation si abo; rétractation en ligne |
| Service public / délégataire / CA ≥ 250 M€ | C, D, E, G RGAA, B, H, K, L | |
| Plateforme / hébergeur de contenus tiers | C, D, E, B, H, K, L | DSA notice-and-action |
| Santé, mineurs, IA, entité NIS2 | base + module nommé | ne pas activer sans fait |

Personne morale (asso, société): régime LCEN art. 1-1, I, 2° (pas de capital ni RCS si non assujettie). Éditeur non professionnel: art. 1-1, II (anonymat possible, hébergeur seulement).

## Identification (module C)

Source de vérité: LCEN art. 1-1, créée par la loi SREN n° 2024-449 du 21 mai 2024, en vigueur le 23 mai 2024. Légifrance, consolidée, dernière maj des données: 23 mai 2024.

L'ancien art. 6, III (mentions éditeur) n'existe plus. L'art. 6 actuel traite des intermédiaires (accès, hébergement, plateformes). Les fiches Service-Public F37351 et F31228 (vérifiées le 31 juillet 2023, encore en l'état le 16 sept. 2026) citent encore l'art. 6: utiles pour la liste pratique, pas pour le numéro.

Texte art. 1-1, I: les éditeurs d'un service de communication au public en ligne mettent à la disposition du public, dans un standard ouvert:

1. Personne physique: nom, prénoms, domicile, téléphone; si assujettie RCS ou RNE métiers, le numéro d'inscription.
2. Personne morale: dénomination ou raison sociale, siège, téléphone; si assujettie RCS ou RNE métiers: numéro d'inscription, capital, adresse du siège.
3. Nom du directeur ou du codirecteur de la publication (loi n° 82-652 du 29 juillet 1982, art. 93-2) et, le cas échéant, du responsable de la rédaction.
4. Nom / dénomination, adresse et téléphone du fournisseur de services d'hébergement.
5. Le cas échéant: nom / dénomination et adresse des personnes qui assurent, même à titre gratuit, le stockage de données traitées directement par elles dans le cadre de l'édition du service.

Art. 1-1, II: éditeur non professionnel peut ne publier que le nom et l'adresse de l'hébergeur, s'il a communiqué au prestataire les éléments du I.

Standard ouvert: LCEN art. 4 (protocole / format public, sans restriction). En pratique: page HTML lisible, pas uniquement une image ou un PDF scanné illisible.

### Ce que 1-1 n'exige pas (et que d'autres textes exigent)

- Courriel de l'éditeur: pas dans 1-1. Requis pour le commerce électronique (LCEN art. 19, 2°) et comme coordonnées du responsable de traitement (RGPD art. 13).
- TVA: LCEN art. 19, 4° (si assujetti et identifié). Pas 1-1.
- Forme juridique écrite en toutes lettres: pas 1-1. Utile via Code de commerce (papiers d'affaires / site).
- RNA d'une asso: pas 1-1. Le noter s'il existe, ne pas l'exiger.

### Code de commerce, site d'une personne immatriculée

Art. R.123-237: la personne immatriculée indique sur son site la mention RCS suivie de la ville du greffe, plus le numéro unique d'identification (SIREN), le lieu du siège, et le cas échéant liquidation / locataire-gérant. Ça s'ajoute à la LCEN.

### Commerce électronique (en plus, module F)

LCEN art. 19 (toujours en vigueur, titre II): accès facile, direct et permanent, standard ouvert, à: identité, adresse d'établissement, courriel, téléphone; si RCS/métiers: numéro, capital, siège; TVA si assujetti; autorité si autorisation; profession réglementée (titre, État, ordre). Prix mentionné: clair, taxes et frais de livraison inclus.

### Sanctions identification

LCEN art. 1-2: 1 an d'emprisonnement et 75 000 € d'amende pour la personne physique ou le dirigeant. Personnes morales: art. 121-2 et 131-38 du code pénal (amende au quintuple, soit 375 000 €). Ça recoupe F37351 (375 000 € société) et F31228 (1 an + 75 000 € EI).

## Données personnelles (module D)

RGPD art. 12 (forme: concise, transparente, compréhensible, aisément accessible), 13 (collecte directe), 14 (collecte indirecte). CNIL, page « informer et transparence ».

Politique distincte des CGV/CGU. Lien visible, intitulé clair (« Données personnelles » / « Confidentialité »). Information au moment de la collecte.

Mentions attendues (art. 13, lecture CNIL):

Toujours: identité et coordonnées du responsable; finalités; bases légales; caractère obligatoire ou facultatif et conséquences; destinataires / sous-traitants; durées ou critères; droits d'accès, rectification, effacement, limitation; point de contact / DPO s'il est désigné; réclamation CNIL.

Selon les cas: intérêts légitimes; transferts hors UE et garanties; décisions automatisées / profilage; retrait du consentement; opposition; portabilité.

L'audit ne « valide » pas le registre, les DPA, ni le délai de 72 h (art. 33). Vue publique seulement.

## Cookies et traceurs (module E)

Loi n° 78-17 (LIL) art. 82, transposition de la directive ePrivacy 2002/58/CE art. 5(3). Consentement = RGPD art. 4(11) et 7: libre, spécifique, éclairé, univoque, retirable aussi simplement.

Reco CNIL consolidée publiée le 16 janvier 2026 (délib. 2020-092 du 17 sept. 2020 + délib. 2025-131 du 18 déc. 2025). Le consentement multi-terminaux (art. 7 de la reco) est facultatif. Ne pas le traiter comme une obligation.

Exemptés (exemples CNIL): choix cookies, auth/sécurité, panier, langue intrinsèque, load-balancing, paywall d'échantillon, certains traceurs d'audience sous conditions.

Audience exemptée seulement si: mesure du seul site, pour le compte exclusif de l'éditeur, stats anonymes, pas de suivi cross-site, pas de cession de données non anonymes à des tiers. Reco CNIL: cookie ≤ 13 mois non prorogé auto, conservation ≤ 25 mois, information dans la politique. La CNIL ne certifie plus les outils: auto-évaluation du fournisseur.

Non exemptés: pub, réseaux sociaux, mesure hors exemption. Consentement préalable, acte positif, refus aussi simple, finalités présentées avant un accept global, liste des responsables, retrait permanent. Fermer le bandeau = refus. Poursuite de navigation = refus. Case pré-cochée interdite. Reco: conserver le choix (accept ou refus) environ 6 mois.

Absence de bandeau: conforme possible s'il n'y a aucun traceur non exempté. Le constater par inventaire, pas par l'absence de CMP.

## Prospection (si case newsletter / SMS)

Art. L.34-5 CPCE. CNIL, page prospection (maj 10 juin 2026).

B2C: opt-in préalable. Exception client: produits ou services similaires de la même entreprise + opposition à la collecte et dans chaque message. La création de compte sans commande n'ouvre pas l'exception (rappel CNIL).

B2B: information + opposition si le message tient à la fonction professionnelle.

Case dédiée, pas pré-cochée, pas noyée dans les CGU. Identité de l'émetteur et désinscription dans chaque message.

Sanctions L.34-5 (texte lu via QPC n° 2026-1210 du 25 juin 2026): amende administrative DGCCRF jusqu'à 75 000 € personne physique, 375 000 € personne morale. Le skill v0.1 citait 15 000 €: c'est faux. La QPC porte sur le cumul CNIL / DGCCRF / ARCEP; l'abrogation du passage censuré est reportée au 31 octobre 2027. Ne pas commenter le cumul dans le rapport.

## Consommation / e-commerce (module F)

Obligations: C. conso L.111-1 à L.111-8 (précontractuel), L.221-5 à L.221-7 (distance), R.111-1 et s. Fiche F33527 vérifiée le 1er juillet 2026.

Avant commande, lisible: caractéristiques, prix TTC, frais et délai, identité, garanties légales (conformité L.217-3; vices cachés), médiateur (L.616-1, R.111-1, 7°), rétractation 14 j (L.221-18) + formulaire type, exceptions L.221-28 si elles s'appliquent.

B2B seul: CGV communicables sur demande (C. com L.441-1). Pas forcément en ligne. `hors champ` si aucun prix consommateur. Un pro de 5 salariés max, hors activité principale, contrat à distance, peut être assimilé consommateur (F33527).

### Résiliation d'abonnement

Depuis le 1er juin 2023: L.215-1-1 (loi n° 2022-1158). Fonctionnalité gratuite, « résilier votre contrat » ou formule analogue, accès facile / direct / permanent, récap, bouton « notification de la résiliation », confirmation sur support durable. Même si le contrat n'a pas été conclu en ligne, dès que le professionnel propose de conclure en ligne.

F37351: amende 75 000 € (société) / F31228: 15 000 € (EI) en l'absence de fonctionnalité. Citer la fiche + la date, pas un article de sanction non relu.

### Rétractation en ligne (déjà en vigueur)

Depuis le 19 juin 2026: L.221-21 (ordonnance n° 2026-2 du 5 janvier 2026) et D.221-5 (décret n° 2026-3). France Num, fiche du 13 juillet 2026.

Contrats conclus à distance via une interface en ligne: fonctionnalité gratuite, « renoncer au contrat ici » ou analogue, visible pendant tout le délai de 14 j, confirmation « confirmer la rétractation », accusé sur support durable (date et heure). Information précontractuelle sur l'existence et l'emplacement (L.221-5). Contrats en cours au 19 juin 2026: ancien régime.

France Num: amende administrative L.242-13 jusqu'à 15 000 € PP / 75 000 € PM. L'oubli d'information sur la rétractation allonge le délai (L.221-20).

## Accessibilité (module G)

Deux régimes distincts. Ne pas les fusionner.

### RGAA (art. 47 loi n° 2005-102)

Champ officiel (accessibilite.numerique.gouv.fr): personnes morales de droit public; délégataires / organismes para-publics listés; entreprises dont le CA annuel moyen en France sur 3 exercices ≥ 250 M€.

Hors champ notamment: SMV audiovisuels; asso à but non lucratif sans service essentiel ni service destiné aux personnes handicapées.

Méthode: RGAA 4.1.2. Norme: EN 301 549. RGAA 5 annoncé fin 2026: ne pas geler un audit pour ça.

Si obligation: déclaration d'accessibilité, schéma pluriannuel, mécanisme de signalement. Charge disproportionnée: à justifier dans la déclaration, ce n'est pas une absence de déclaration.

### EAA (directive 2019/882)

Depuis le 28 juin 2025. Transposition: loi n° 2023-171 du 9 mars 2023, C. conso L.412-13 (texte lu, consolidée, en vigueur depuis le 11 mars 2023, applicable aux services fournis après le 28 juin 2025), décret n° 2023-931 et arrêté du 9 octobre 2023.

L.412-13, I (extrait): les opérateurs économiques fournissent des services conformes aux exigences d'accessibilité. « Les entreprises employant moins de dix personnes qui fournissent des services et dont le chiffre d'affaires annuel n'excède pas deux millions d'euros ou dont le total du bilan n'excède pas deux millions d'euros sont dispensées ». II: pas d'obligation si modification fondamentale de la nature du service, ou charge disproportionnée (évaluation à documenter; un financement dédié à l'accessibilité ferme l'excuse « charge »).

Services contrôlés par la DGCCRF (fiche opérateurs, handicap.gouv.fr, juil. 2025): commerce électronique; communications électroniques; accès aux médias audiovisuels; transports de voyageurs (sites, apps, billetterie); contrats et services bancaires listés. Un site e-commerce est un service, pas un produit: le délai jusqu'au 28 juin 2030 (produits déjà utilisés, contrats en cours, bornes) ne recule pas l'obligation sur le site lui-même.

Information publique EAA (France Num, 17 déc. 2025, s'appuie sur l'annexe de D.412-57): page ou écran « Information sur l'accessibilité », pas un modèle unique, pas une déclaration RGAA. Contenu attendu: description générale du service; norme utilisée; conforme / exceptions; dérogations et alternatives; moyen de contact (reco: au moins deux canaux). Ce n'est pas la déclaration RGAA (art. 47 / décret 2019-768), réservée au champ public / 250 M€. Ne pas cocher « déclaration RGAA manquante » sur un e-commerce privé.

Non-conformité: D.412-57, 4° (cité par France Num): informer immédiatement la DGCCRF, avec précisions et mesures correctives. L'audit note l'absence de page publique; il ne vérifie pas si une déclaration interne a été faite.

Sans effectif ni CA connus: `non verifie`, pas un échec. France Num parle de « microentreprises et TPE » hors champ: le texte qui gagne reste L.412-13 (< 10 personnes et CA ou bilan ≤ 2 M€).

Contrôle: DGCCRF (enquêteurs départementaux; SignalConso; injonction L.521-1). Qualification: C. conso R.451-4-I, contravention de 5e classe (fiche DGCCRF). Le corps de R.451-4 n'a pas été ouvert sur Légifrance (Cloudflare). Montants lus sur deux pages .gouv.fr: France Num (17 déc. 2025) et ecologie.gouv.fr (maj 8 avr. 2024): 1 500 € PP / 3 000 € récidive; 7 500 € PM / 15 000 € récidive; cumulables par service et par obligation. Ça recoupe CP 131-13, 131-41 (quintuple), 132-11 et 132-15. Ne pas écrire ces montants comme s'ils figuraient dans le corps de R.451-4.

Hors obligation: fumée (lang, alt, labels, contraste, clavier) en `mineur` / reco.

## Sécurité observée (modules H et K)

RGPD art. 32: mesures appropriées. L'audit note ce qui se voit (HTTPS, HSTS, cookies de session, fuite, debug). Il ne certifie pas l'art. 32.

Hygiène: TLS 1.2+, pas de secret dans le HTML, pas de `.git` / `.env` public, pas de stack en prod. Reco ANSSI + ASVS 5.0 L1 observables. Détail: [pentest-limite.md](pentest-limite.md).

Ce n'est pas une prestation PASSI (référentiel ANSSI v2.2: architecture, configuration machine, code, intrusion, orga/physique). On n'en revendique aucune portée.

`security.txt` (RFC 9116): reco. Absent ≠ écart.

NIS2: seulement si l'entité est dans le champ. Ne pas l'activer sur une vitrine.

## Autres modules (faits seulement)

- Droit d'auteur / droit à l'image: crédits, contenus visiblement tiers sans mention.
- DSA (règlement UE 2022/2065, applicable depuis le 17 février 2024): notice-and-action (art. 16) si le service héberge des contenus de tiers. Une vitrine sans UGC: hors champ.
- Règlement IA (UE) 2024/1689 art. 50: depuis le 2 août 2026, information claire, au plus tard à la première interaction, qu'on parle à un système d'IA, sauf si c'est évident. Une mention noyée dans les CGU ne suffit pas. L'obligation de conception pèse sur le fournisseur; l'interface publique doit quand même porter l'information.
- Données de santé: HDS / secret. Hors champ sauf fait.
- Mineurs: âge, consentement parental (RGPD art. 8), pas de pub ciblée évidente. Vérification d'âge pornographique: LCEN post-SREN, hors d'une vitrine standard.

## Sanctions (ordre de grandeur)

Ne pas menacer le client avec un montant. Le noter seulement si ça priorise. Toujours coller la source et la date.

| Écart | Ordre de grandeur | Source relue |
|---|---|---|
| Mentions 1-1 absentes, personne physique / dirigeant | 1 an + 75 000 € | LCEN art. 1-2 |
| Mentions 1-1 absentes, personne morale | amende au quintuple (375 000 €) | LCEN art. 1-2 + CP art. 131-38; F37351 |
| CGV B2C absentes | 15 000 € (société) / 3 000 € (EI) | F37351 / F31228 (31 juil. 2023) |
| Rétractation en ligne absente | 15 000 € PP / 75 000 € PM | France Num, L.242-13 (13 juil. 2026) |
| Prospection L.34-5 | 75 000 € PP / 375 000 € PM | L.34-5, QPC 2026-1210 |
| RGPD | jusqu'à 20 M€ ou 4 % CA mondial | RGPD art. 83. La CNIL sanctionne aussi en dessous. |
| Info manquante (voie pénale ancienne) | 1 500 € (contravention) | F37351 cite ce montant; ce n'est pas le seul risque |
| EAA, service dans le champ | 1 500 € / 3 000 € PP; 7 500 € / 15 000 € PM (5e classe, R.451-4-I) | France Num 17 déc. 2025; ecologie.gouv.fr 8 avr. 2024. Qualification R.451-4: fiche DGCCRF. Corps non lu. |

## Ce qu'il est interdit de faire dans cet audit

- Inventer un SIREN, un hébergeur, un DPO, un effectif, un article.
- Envoyer un payload (XSS, SQLi, SSTI, LFI, brute-force, fuzz, path traversal).
- Descendre un arbre `.git` après un HEAD positif. Un seul GET suffit.
- Déclarer « conforme RGPD » ou « non conforme » comme verdict global. On liste des écarts observés.
- Traiter F37351 / F31228 comme le numéro d'article en vigueur.
