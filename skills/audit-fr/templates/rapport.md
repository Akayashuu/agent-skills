# Audit web FR: {cible}

- Date (UTC): {date}
- URL: {url}
- Repo: {repo_ou_aucun}
- Acteur: {asso|ei|societe|ecommerce|public|plateforme}
- Modules actifs: {liste}
- Outils: probe.py {oui/non} ; navigateur {oui/non} ; repo {oui/non}
- Limite: vue publique. Pas un avis juridique. Pas un test d'intrusion PASSI. Pentest limité: H + K. SEO technique: L. Pas un audit de ranking.

## Synthèse

| Sévérité | Nombre |
|---|---|
| critique | {n} |
| majeur | {n} |
| mineur | {n} |
| info | {n} |
| **total** | **{n}** |

Une phrase: {ce qui pèse le plus}.

## Fait

{surface sondée, pages lues, probe.json}

## Avance

{écarts déjà corrigés pendant l'audit, s'il y en a}

## Bloque / à valider

{décision éditeur, accès manquant, publication du rapport}

## Constats

Trier critique → info. Un bloc par constat.

### {id} {titre}

| Champ | Valeur |
|---|---|
| Sévérité | critique / majeur / mineur / info |
| Module | B–L |
| Statut | manquant / incomplet / ecart |
| URL | |
| Preuve | extrait, en-tête, cookie, ou chemin probe.json |
| Texte | ex. LCEN art. 1-1 ; RGPD art. 13 / 32 ; LIL art. 82 ; ASVS v5.0.0-3.4.1 ; Search Central title-link / canonical |

**Attendu:**
**Observé:**
**Reco (une ligne, sans payload):**

## Grille

Reprendre [references/grille.md](../references/grille.md): une ligne par item actif, statut + preuve courte. Items inactifs: `hors champ`.

## Sources

Pages officielles réellement ouvertes pour cet audit (URL + date). Reprendre [references/sources.md](../references/sources.md) et n'ajouter que ce qui a été relu. Pas de blog. Si F37351 et Légifrance divergent, Légifrance gagne.

## Hors champ

{ce qui n'a pas été testé: JS, mobile, tunnel de paiement, registre interne}
