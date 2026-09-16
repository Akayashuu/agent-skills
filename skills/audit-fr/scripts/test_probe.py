#!/usr/bin/env python3
"""Offline tests for audit-fr probe helpers. No network."""

from __future__ import annotations

import unittest

from probe import (
    classify_surface,
    extract_seo,
    looks_like_env,
    parse_csp,
    parse_hsts,
    parse_link_header,
    parse_robots,
    parse_sitemap,
    scan_leaks,
    seo_flags,
)


class HstsCsp(unittest.TestCase):
    def test_hsts_year(self) -> None:
        parsed = parse_hsts("max-age=31536000; includeSubDomains; preload")
        self.assertEqual(parsed["max_age"], 31536000)
        self.assertTrue(parsed["include_subdomains"])
        self.assertTrue(parsed["preload"])
        self.assertTrue(parsed["max_age_ok_l1"])

    def test_hsts_short(self) -> None:
        parsed = parse_hsts("max-age=3600")
        self.assertFalse(parsed["max_age_ok_l1"])

    def test_csp_flags(self) -> None:
        parsed = parse_csp("default-src *; script-src 'unsafe-inline' 'unsafe-eval'")
        self.assertTrue(parsed["has_default_src"])
        self.assertTrue(parsed["default_src_star"])
        self.assertTrue(parsed["unsafe_inline"])
        self.assertTrue(parsed["unsafe_eval"])
        self.assertFalse(parsed["has_frame_ancestors"])


class Leaks(unittest.TestCase):
    def test_traceback(self) -> None:
        body = "Oops\nTraceback (most recent call last):\n  File"
        found = scan_leaks(body)
        self.assertIn("python-traceback", found["debug_signatures"])

    def test_secret_type_only(self) -> None:
        body = "const k = 'sk_live_" + ("a" * 24) + "';"
        found = scan_leaks(body)
        self.assertEqual(found["secret_types"][0]["type"], "stripe-live")
        dumped = str(found)
        self.assertNotIn("sk_live_" + ("a" * 24), dumped)

    def test_env_lines(self) -> None:
        self.assertTrue(looks_like_env("DATABASE_URL=postgres://x\nSECRET_KEY=abc\n"))
        self.assertFalse(looks_like_env("<!doctype html><html><body>SECRET_KEY=no</body>"))


class Surface(unittest.TestCase):
    def test_git_exposed(self) -> None:
        self.assertEqual(
            classify_surface("git-head", 200, "ref: refs/heads/main\n", "Home", "x"),
            "exposed",
        )

    def test_catchall_same_title(self) -> None:
        html = "<html><head><title>Home</title></head><body>spa</body></html>"
        self.assertEqual(classify_surface("dotenv", 200, html, "Home", "other"), "catchall")

    def test_gated(self) -> None:
        self.assertEqual(classify_surface("actuator", 403, "", "", ""), "gated")

    def test_absent(self) -> None:
        self.assertEqual(classify_surface("phpinfo", 404, "nope", "", ""), "absent")

    def test_robots_is_present_not_exposed(self) -> None:
        body = "User-Agent: *\nDisallow: /admin\n"
        self.assertEqual(classify_surface("robots", 200, body, "Home", "x"), "present")


class Seo(unittest.TestCase):
    def test_robots_disallow_all(self) -> None:
        parsed = parse_robots("User-agent: *\nDisallow: /\nSitemap: https://ex.fr/sitemap.xml\n")
        self.assertTrue(parsed["ok"])
        self.assertTrue(parsed["disallow_all"])
        self.assertEqual(parsed["sitemaps"], ["https://ex.fr/sitemap.xml"])

    def test_robots_allow_empty_disallow(self) -> None:
        parsed = parse_robots("User-agent: *\nDisallow:\n")
        self.assertFalse(parsed["disallow_all"])

    def test_robots_rejects_html(self) -> None:
        parsed = parse_robots("<!doctype html><html><body>nope</body></html>")
        self.assertFalse(parsed["ok"])

    def test_sitemap_https(self) -> None:
        body = """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://ex.fr/a</loc></url>
  <url><loc>http://ex.fr/b</loc></url>
</urlset>
"""
        parsed = parse_sitemap(body)
        self.assertEqual(parsed["kind"], "urlset")
        self.assertEqual(parsed["url_count"], 2)
        self.assertEqual(parsed["http_locs"], 1)
        self.assertEqual(parsed["https_locs"], 1)

    def test_link_header_canonical(self) -> None:
        items = parse_link_header('<https://ex.fr/>; rel="canonical", <https://ex.fr/fr>; rel="alternate"; hreflang="fr"')
        rels = {item.get("rel"): item.get("href") for item in items}
        self.assertEqual(rels.get("canonical"), "https://ex.fr/")
        self.assertEqual(rels.get("alternate"), "https://ex.fr/fr")

    def test_extract_and_flags(self) -> None:
        html = """<!doctype html>
<html lang="fr">
<head>
<title>Home</title>
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="http://ex.fr/">
<script type="application/ld+json">{"@type":"Organization","name":"Ex"}</script>
</head>
<body><h1>Accueil</h1></body>
</html>
"""
        seo = extract_seo("https://ex.fr/", html, {})
        self.assertTrue(seo["ok"])
        self.assertTrue(seo["title"]["generic"])
        self.assertTrue(seo["noindex"])
        self.assertEqual(seo["h1_count"], 1)
        self.assertIn("Organization", seo["jsonld_types"])
        ids = {flag["id"] for flag in seo_flags(seo)}
        self.assertIn("title_generic", ids)
        self.assertIn("noindex_present", ids)
        self.assertIn("canonical_http", ids)
        self.assertIn("description_missing", ids)
        self.assertIn("viewport_missing", ids)

    def test_hreflang_deduped(self) -> None:
        html = """<html lang="fr"><head><title>Studio FR</title>
<link rel="alternate" hreflang="fr" href="https://ex.fr/fr/">
<link rel="alternate" hreflang="en" href="https://ex.fr/en/">
<link rel="alternate" hreflang="fr" href="https://ex.fr/fr/">
<link rel="alternate" hreflang="en" href="https://ex.fr/en/">
<meta name="description" content="Studio de développement web sur mesure pour les TPE.">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="https://ex.fr/fr/">
</head><body><h1>Studio</h1>
<script type="application/ld+json">{"@type":"WebSite"}</script>
</body></html>"""
        seo = extract_seo("https://ex.fr/fr/", html, {})
        self.assertEqual([(a["lang"], a["href"]) for a in seo["hreflang"]], [("fr", "https://ex.fr/fr/"), ("en", "https://ex.fr/en/")])
        ids = {flag["id"] for flag in seo_flags(seo)}
        self.assertNotIn("hreflang_no_self", ids)
        self.assertTrue(all(flag["severity"] != "majeur" for flag in seo_flags(seo)))

    def test_title_empty_is_majeur(self) -> None:
        html = "<html><head><title>  </title></head><body></body></html>"
        seo = extract_seo("https://ex.fr/", html, {})
        flags = {flag["id"]: flag["severity"] for flag in seo_flags(seo)}
        self.assertEqual(flags["title_empty"], "majeur")
        self.assertEqual(flags["h1_missing"], "mineur")


if __name__ == "__main__":
    unittest.main()
