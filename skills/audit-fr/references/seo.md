# SEO technique: crawl, indexation, extraits

Ce n'est pas une obligation légale. Ce n'est pas un audit de ranking, de mots-clés, ni de netlinking. C'est une revue de surface alignée sur Google Search Central: ce qu'un crawler voit au premier GET (HTML, en-têtes, robots.txt, sitemap).

Référentiels (relus le 2026-09-16):

- Google Search Central: title links, snippets / meta description, meta robots, canonical (maj 2026-07-10), robots.txt (maj 2025-12-10), sitemaps, hreflang (maj 2025-12-22), structured data (maj 2025-12-10), mobile-first, viewport.
- Protocole sitemaps.org (formats XML / texte que Google dit accepter).
- RFC 6596 (`rel=canonical`). Google l'accepte; un fragment dans le canonical est ignoré.

Bing / autres moteurs: hors champ sauf si un fait le demande. On ne cite pas un blog SEO, un SaaS de rank tracking, ni une « checklist 200 points ».

Chaque case active: statut + preuve. Pas de preuve = `non verifie`. Absence d'un signal *recommandé* (canonical, JSON-LD, sitemap) n'est pas un écart à elle seule: Google dit que le site « se débrouillera » sans canonical explicite.

## Ce que le skill fait

1. Document: `<title>`, meta description, `html lang`, viewport, charset.
2. Indexation: meta `robots` / `googlebot`, en-tête `X-Robots-Tag`. `noindex` sur une page vendue comme publique = écart.
3. Canonical: `<link rel=canonical>` et / ou `Link` HTTP. HTTPS, URL absolue, pas de fragment, pas de conflit HTML vs en-tête.
4. Crawl: `robots.txt` (présent / `Disallow: /` / ligne `Sitemap:`). `Disallow` n'empêche pas l'indexation de l'URL.
5. Sitemap: XML urlset / index, ou texte. URLs absolues HTTPS. Cohérence avec le canonical.
6. International: `hreflang` (self, URLs absolues, `x-default` si sélecteur). Retour réciproque: on GET au plus 3 alternates. Google ignore les paires non réciproques.
7. Structure: H1, niveaux d'intertitres, images sans `alt` (déjà dans le HTML).
8. Données structurées: types JSON-LD (`@type` seulement). Microdata `itemtype` noté. On ne valide pas le Rich Results Test.
9. Social (`og:*`, Twitter): info. Pas un facteur de ranking documenté ici.

## Ce que le skill ne fait jamais

- Promettre une position, un trafic, ou un « score SEO ».
- Keyword stuffing inverse: on ne prescrit pas une liste de mots.
- Crawl de tout le site, sitemap complet au-delà d'un échantillon, backlinks, Search Console.
- Core Web Vitals / LCP / INP / CLS: `non verifie` sans PageSpeed (l'API n'est pas dans le sondeur).
- Rendu JS: le premier GET sans exécuter les scripts. Un SPA dont le `<title>` / le H1 n'existent que côté client: le dire, ne pas inventer le DOM rendu.
- Contenu dupliqué inter-domaines, E-E-A-T, « helpful content » comme verdict.
- Acheter un outil, un abonnement GSC, ou un audit Ahrefs.

Si le ranking réel est demandé: Search Console, pas ce skill.

## Module L

Toujours actif sur une URL publique. Préprod / Basic Auth: noter que l'indexation *voulue* est souvent `noindex`. Un `noindex` de préprod est `ok`, pas un écart.

Hors champ: site privé, intranet, app store only.

## Sévérités SEO

| Sévérité | Exemples (avec preuve) |
|---|---|
| critique | n'existe pas en SEO seul. Un secret dans le JS reste le module K |
| majeur | `noindex` ou `X-Robots-Tag: noindex` sur une page de prod publique; `Disallow: /` pour `User-agent: *` sur un site livré; `<title>` vide sur l'accueil; canonical en `http://` depuis une page HTTPS; plusieurs canonicals contradictoires |
| mineur | meta description absente ou trop courte (< 20 car.) sur une page clé; viewport sans `width=device-width`; canonical relatif ou avec fragment; H1 absent; `html lang` absent; sitemap avec des `http://`; `hreflang` sans self ou URL relative; meta refresh |
| info | canonical absent (Google n'exige pas); sitemap / robots.txt absents; JSON-LD absent; Open Graph absent; title > 70 car. (tronqué, pas un échec); plusieurs H1; CWV non mesuré |

`robots.txt` introuvable: info. Google dit qu'on peut s'en passer. `Disallow` d'un chemin n'est pas une faille (déjà module K).

## Mapping Search Central (observables)

| Sujet | Observé comment |
|---|---|
| Title link | `seo.title`. Vide / générique (`Home`, `Accueil`, `Untitled`, `Sans titre`). Google peut réécrire. |
| Snippet | `seo.meta_description`. Pas de limite officielle. Google prend souvent le corps de page. |
| robots meta | `seo.robots_meta`, `seo.noindex`, `seo.nofollow` |
| X-Robots-Tag | `seo.x_robots_tag` |
| Canonical HTML / HTTP | `seo.canonical` |
| robots.txt | `seo.robots` (`disallow_all`, `sitemaps`) |
| Sitemap | `seo.sitemap` (`kind`, `url_count`, `http_locs`) |
| hreflang | `seo.hreflang`, `seo.hreflang_return` |
| Viewport | `seo.viewport` |
| Structured data | `seo.jsonld_types` |
| Mobile-first | viewport + même HTML au GET. Variante m. non testée sauf URL fournie |

## Lecture des flags `seo.flags`

Le sondeur pose des drapeaux (`id`, `severity`, `detail`). L'agent les recopie dans la grille. Il n'ajoute pas un écart « pas assez de mots-clés » ou « score 42/100 ».

`noindex_present` est majeur *si* la page est censée être indexée. En préprod / staging: reclasse en `ok` avec la raison.

## Pièges

- `Disallow` ≠ `noindex`. Une URL interdite au crawl peut quand même apparaître (sans snippet) si un tiers pointe dessus.
- Canonical relatif: Google l'accepte, le déconseille (risque de préprod crawlée).
- Canonical + `hreflang` / `media` / `type` sur le même `<link>`: Google n'utilise pas ce lien pour la canonicalisation.
- `hreflang` non réciproque: ignoré. On ne le sait que si on a GET l'alternate.
- Google ne se sert pas de `html lang` ni de `hreflang` pour *détecter* la langue; il s'en sert pour servir la bonne variante. Un `lang` faux reste un écart d'accessibilité (module G), pas un « mauvais SEO langue ».
- JSON-LD sur une info invisible: Google le refuse pour les rich results. On ne le voit pas sans comparer au texte visible.
- `data-vocabulary.org`: plus éligible aux rich results. Le noter `info` s'il apparaît.
- Catch-all SPA: title identique partout. On ne sonde que les URLs données; on ne déclare pas « tout le site a le même title » sans preuve.
- Soft 404 (200 + page vide / « not found » dans le title): majeur si l'URL est censée exister. Preuve: title + extrait.
