#!/usr/bin/env python3
"""Surface probe for the audit-fr skill.

Defensive only: GET, redirects, TLS handshake, response headers, HTTP cookies,
HTML hints, and a fixed list of well-known paths. No payloads, no auth, no
fuzz, no crawl beyond the URLs given and SURFACE_PATHS.

Stdlib only. Usage:
  python3 probe.py https://example.fr -o probe.json
  python3 probe.py https://example.fr --no-surface
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import socket
import ssl
import sys
import warnings
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

UA = "VSK-audit-fr/0.4 (+https://vskstudio.fr)"
TIMEOUT = 20
GENERIC_TITLES = frozenset(
    {
        "home",
        "accueil",
        "untitled",
        "sans titre",
        "new page",
        "document",
        "index",
        "welcome",
        "bienvenue",
        "page",
    }
)
SOFT_404_TITLE = (
    "page not found",
    "page introuvable",
    "404 not found",
    "erreur 404",
    "this page does not exist",
    "cette page n'existe pas",
)

SECURITY_HEADERS = (
    "strict-transport-security",
    "content-security-policy",
    "content-security-policy-report-only",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
    "permissions-policy",
    "cross-origin-opener-policy",
    "cross-origin-resource-policy",
    "cross-origin-embedder-policy",
    "access-control-allow-origin",
    "access-control-allow-credentials",
    "clear-site-data",
)

BANNER_HEADERS = (
    "server",
    "x-powered-by",
    "x-aspnet-version",
    "x-aspnetmvc-version",
    "x-drupal-cache",
    "x-generator",
    "x-runtime",
)

LEGAL_TEXT = (
    "mentions légales",
    "mentions legales",
    "legal notice",
    "données personnelles",
    "donnees personnelles",
    "politique de confidentialité",
    "politique de confidentialite",
    "privacy policy",
    "gestion des cookies",
    "politique cookies",
    "cookie policy",
    "conditions générales de vente",
    "conditions generales de vente",
    "conditions générales d'utilisation",
    "accessibilité",
    "accessibilite",
    "déclaration d'accessibilité",
    "mediateur de la consommation",
    "médiateur de la consommation",
    "directeur de la publication",
    "directeur de publication",
    "resilier votre contrat",
    "résilier votre contrat",
    "renoncer au contrat ici",
    "confirmer la rétractation",
    "confirmer la retractation",
)

LEGAL_PATH = (
    "/mentions",
    "/legal",
    "/privacy",
    "/rgpd",
    "/confidentialite",
    "/confidentialité",
    "/cookies",
    "/cookie-policy",
    "/cgv",
    "/cgu",
    "/accessibilite",
    "/accessibilité",
    "/mediateur",
    "/médiateur",
    "/retractation",
    "/resiliation",
    "/résiliation",
)

TRACKER_NEEDLES = (
    ("googletagmanager.com/gtag/js", "gtag"),
    ("www.googletagmanager.com", "gtm"),
    ("google-analytics.com", "ga"),
    ("connect.facebook.net", "meta-pixel"),
    ("fbevents.js", "meta-pixel"),
    ("static.hotjar.com", "hotjar"),
    ("cdn.mxpnl.com", "mixpanel"),
    ("snap.licdn.com", "linkedin-insight"),
    ("www.tiktok.com/tag", "tiktok"),
    ("analytics.tiktok.com", "tiktok"),
    ("bat.bing.com", "bing-uet"),
    ("hcaptcha.com", "hcaptcha"),
    ("www.google.com/recaptcha", "recaptcha"),
    ("challenges.cloudflare.com", "turnstile"),
)

# Fixed GET list. Do not invent extra paths at runtime.
SURFACE_PATHS: tuple[tuple[str, str], ...] = (
    ("/.well-known/security.txt", "security-txt"),
    ("/robots.txt", "robots"),
    ("/sitemap.xml", "sitemap"),
    ("/.git/HEAD", "git-head"),
    ("/.git/config", "git-config"),
    ("/.svn/entries", "svn"),
    ("/.env", "dotenv"),
    ("/.env.local", "dotenv-local"),
    ("/.env.production", "dotenv-prod"),
    ("/composer.json", "composer"),
    ("/package.json", "package-json"),
    ("/package-lock.json", "package-lock"),
    ("/.htaccess", "htaccess"),
    ("/web.config", "web-config"),
    ("/phpinfo.php", "phpinfo"),
    ("/server-status", "server-status"),
    ("/server-info", "server-info"),
    ("/actuator", "actuator"),
    ("/actuator/health", "actuator-health"),
    ("/actuator/env", "actuator-env"),
    ("/swagger.json", "swagger-json"),
    ("/swagger-ui.html", "swagger-ui"),
    ("/openapi.json", "openapi"),
    ("/graphql", "graphql"),
    ("/debug", "debug"),
    ("/_debug", "debug-underscore"),
    ("/elmah.axd", "elmah"),
    ("/trace.axd", "trace-axd"),
    ("/backup.sql", "backup-sql"),
    ("/dump.sql", "dump-sql"),
    ("/wp-config.php.bak", "wp-config-bak"),
    ("/config.json", "config-json"),
)

SURFACE_SIG: dict[str, tuple[str, ...]] = {
    "security-txt": ("contact:", "expires:", "canonical:"),
    "robots": ("user-agent:", "disallow:", "allow:", "sitemap:"),
    "sitemap": ("<urlset", "<sitemapindex"),
    "git-head": ("ref: refs/",),
    "git-config": ("[core]", "[remote"),
    "svn": ("dir\n", "svn:"),
    "dotenv": (),
    "dotenv-local": (),
    "dotenv-prod": (),
    "composer": ('"require"', '"name"'),
    "package-json": ('"dependencies"', '"name"'),
    "package-lock": ('"lockfileversion"', '"packages"'),
    "htaccess": ("rewriteengine", "rewriterule", "deny from"),
    "web-config": ("<configuration", "<system.web"),
    "phpinfo": ("phpinfo()", "<title>phpinfo", "php version"),
    "server-status": ("apache server status", "server version"),
    "server-info": ("apache server information",),
    "actuator": ('"_links"', '"health"'),
    "actuator-health": ('"status"',),
    "actuator-env": ('"propertySources"', '"activeProfiles"'),
    "swagger-json": ('"swagger"', '"openapi"'),
    "swagger-ui": ("swagger-ui",),
    "openapi": ('"openapi"',),
    "graphql": ("graphql", "__schema", "graphiql"),
    "debug": ("debug", "werkzeug", "django"),
    "debug-underscore": ("debug",),
    "elmah": ("elmah", "error log"),
    "trace-axd": ("application trace", "trace.axd"),
    "backup-sql": ("insert into", "create table", "dump"),
    "dump-sql": ("insert into", "create table", "dump"),
    "wp-config-bak": ("db_name", "db_password", "db_user"),
    "config-json": ('"password"', '"secret"', '"apikey"', '"api_key"'),
}

DEBUG_NEEDLES = (
    ("traceback (most recent call last)", "python-traceback"),
    ("django.debug", "django-debug"),
    ("django version:", "django-error-page"),
    ("werkzeug debugger", "werkzeug"),
    ("the debugger caught an exception", "werkzeug"),
    ("symfony exception", "symfony"),
    ("ignition.laravel.com", "laravel-ignition"),
    ("whoops!", "whoops"),
    ("next.js error", "nextjs-error"),
    ("__next_data__", "next-data"),
    ("webpack://", "webpack-source"),
    ("//# sourcemappingurl=", "sourcemap"),
    ("//@ sourcemappingurl=", "sourcemap"),
    ("phpinfo()", "phpinfo"),
    ("<title>phpinfo", "phpinfo"),
    ("xdebug", "xdebug"),
    ("index of /", "dir-listing"),
    ("directory listing for", "dir-listing"),
    ("nullpointerexception", "java-npe"),
    ("fatal error:", "php-fatal"),
    ("undefined index:", "php-notice"),
    ("stack trace:", "stack-trace"),
)

CSRF_NAMES = (
    "csrf",
    "csrfmiddlewaretoken",
    "_csrf",
    "_token",
    "authenticity_token",
    "__requestverificationtoken",
    "x-csrf-token",
)

# Value never stored. Type + offset only.
SECRET_RES: tuple[tuple[str, str], ...] = (
    (r"AKIA[0-9A-Z]{16}", "aws-access-key-id"),
    (r"sk_live_[0-9a-zA-Z]{20,}", "stripe-live"),
    (r"rk_live_[0-9a-zA-Z]{20,}", "stripe-restricted-live"),
    (r"ghp_[0-9A-Za-z]{36}", "github-pat"),
    (r"github_pat_[0-9A-Za-z_]{20,}", "github-fine-grained"),
    (r"xox[baprs]-[0-9A-Za-z-]{10,}", "slack-token"),
    (r"AIza[0-9A-Za-z\-_]{35}", "google-api-key"),
    (r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----", "private-key"),
    (r"-----BEGIN OPENSSH PRIVATE KEY-----", "openssh-private-key"),
)

ENV_LINE = re.compile(r"^[A-Z][A-Z0-9_]{1,80}=.+$", re.M)


class _Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self._in_title = False
        self.lang: str | None = None
        self.links: list[dict[str, str]] = []
        self.scripts: list[dict[str, str]] = []
        self.forms: list[dict[str, Any]] = []
        self.images_missing_alt = 0
        self.images_total = 0
        self.password_fields = 0
        self.password_unmasked = 0
        self.sri_scripts = 0
        self.metas: list[dict[str, str]] = []
        self.rel_links: list[dict[str, str]] = []
        self.headings: list[dict[str, Any]] = []
        self.jsonld_types: list[str] = []
        self.jsonld_blocks = 0
        self.itemtypes: list[str] = []
        self._form: dict[str, Any] | None = None
        self._current_a: dict[str, str] | None = None
        self._in_textarea = False
        self._heading_level: int | None = None
        self._heading_parts: list[str] = []
        self._in_ldjson = False
        self._ldjson_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = ad.get("lang") or ad.get("xml:lang") or self.lang
        elif tag == "title":
            self._in_title = True
        elif tag == "a":
            href = ad.get("href", "")
            self._current_a = {"href": href, "text": ""}
            self.links.append(self._current_a)
        elif tag == "script":
            src = ad.get("src", "")
            integrity = ad.get("integrity", "")
            if src:
                self.scripts.append({"src": src, "integrity": bool(integrity)})
                if integrity:
                    self.sri_scripts += 1
        elif tag == "form":
            self._form = {
                "action": ad.get("action", ""),
                "method": (ad.get("method") or "get").lower(),
                "has_csrf": False,
                "has_password": False,
                "autocomplete": ad.get("autocomplete", ""),
            }
            self.forms.append(self._form)
        elif tag == "input" and self._form is not None:
            name = (ad.get("name") or ad.get("id") or "").lower()
            itype = (ad.get("type") or "text").lower()
            if name in CSRF_NAMES or "csrf" in name:
                self._form["has_csrf"] = True
            if itype == "password":
                self._form["has_password"] = True
                self.password_fields += 1
            elif name in {"password", "passwd", "motdepasse", "mot_de_passe"} and itype != "password":
                self.password_unmasked += 1
        elif tag == "img":
            self.images_total += 1
            if "alt" not in ad:
                self.images_missing_alt += 1
        elif tag == "meta":
            self.metas.append(
                {
                    "name": ad.get("name", "").lower(),
                    "property": ad.get("property", "").lower(),
                    "http_equiv": ad.get("http-equiv", "").lower(),
                    "charset": ad.get("charset", ""),
                    "content": (ad.get("content") or "")[:500],
                }
            )
        elif tag == "link":
            self.rel_links.append(
                {
                    "rel": ad.get("rel", "").lower(),
                    "href": ad.get("href", ""),
                    "hreflang": ad.get("hreflang", ""),
                    "media": ad.get("media", ""),
                }
            )
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading_level = int(tag[1])
            self._heading_parts = []
        if tag == "script" and "ld+json" in ad.get("type", "").lower():
            self._in_ldjson = True
            self._ldjson_parts = []
        itemtype = ad.get("itemtype")
        if itemtype:
            self.itemtypes.append(itemtype.rsplit("/", 1)[-1][:80])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "a":
            self._current_a = None
        if tag == "form":
            self._form = None
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and self._heading_level is not None:
            text = re.sub(r"\s+", " ", "".join(self._heading_parts)).strip()
            self.headings.append({"level": self._heading_level, "text": text[:120]})
            self._heading_level = None
            self._heading_parts = []
        if tag == "script" and self._in_ldjson:
            self._in_ldjson = False
            blob = "".join(self._ldjson_parts)
            self.jsonld_blocks += 1
            self.jsonld_types.extend(jsonld_types(blob))
            self._ldjson_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._current_a is not None and data.strip():
            prev = self._current_a.get("text", "")
            self._current_a["text"] = (prev + " " + data).strip()
        if self._heading_level is not None:
            self._heading_parts.append(data)
        if self._in_ldjson:
            self._ldjson_parts.append(data)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _headers_dict(headers: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in headers.items():
        out[k.lower()] = v
    return out


def _parse_cookies(header_val: str | None, extra: list[str]) -> list[dict[str, Any]]:
    raw: list[str] = []
    if header_val:
        raw.append(header_val)
    raw.extend(extra)
    cookies = []
    for item in raw:
        parts = [p.strip() for p in item.split(";")]
        if not parts or "=" not in parts[0]:
            continue
        name, value = parts[0].split("=", 1)
        flags = {p.split("=", 1)[0].strip().lower(): (p.split("=", 1)[1] if "=" in p else True) for p in parts[1:]}
        cookies.append(
            {
                "name": name,
                "value_len": len(value),
                "secure": "secure" in flags,
                "httponly": "httponly" in flags,
                "samesite": flags.get("samesite"),
                "path": flags.get("path"),
                "prefix_host": name.startswith("__Host-"),
                "prefix_secure": name.startswith("__Secure-"),
            }
        )
    return cookies


def _looks_like_html(body: str) -> bool:
    head = body.lstrip()[:200].lower()
    return head.startswith("<!doctype html") or head.startswith("<html") or "<html" in head[:80]


def parse_hsts(value: str) -> dict[str, Any]:
    parts = [p.strip() for p in value.split(";") if p.strip()]
    max_age = None
    include_sub = False
    preload = False
    for part in parts:
        low = part.lower()
        if low.startswith("max-age"):
            _, _, rest = part.partition("=")
            try:
                max_age = int(rest.strip())
            except ValueError:
                max_age = None
        elif low == "includesubdomains":
            include_sub = True
        elif low == "preload":
            preload = True
    return {
        "max_age": max_age,
        "include_subdomains": include_sub,
        "preload": preload,
        "max_age_ok_l1": (max_age or 0) >= 31536000,
    }


def parse_csp(value: str) -> dict[str, Any]:
    low = value.lower()
    return {
        "has_default_src": "default-src" in low,
        "default_src_star": bool(re.search(r"default-src[^;]*\*", low)),
        "unsafe_inline": "unsafe-inline" in low,
        "unsafe_eval": "unsafe-eval" in low,
        "has_frame_ancestors": "frame-ancestors" in low,
    }


def looks_like_env(body: str) -> bool:
    if _looks_like_html(body):
        return False
    lines = [ln for ln in body.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    if len(lines) < 1:
        return False
    hits = sum(1 for ln in lines if ENV_LINE.match(ln))
    return hits >= 1 and hits >= max(1, len(lines) // 3)


def scan_leaks(body: str) -> dict[str, Any]:
    low = body.lower()
    debug = []
    for needle, name in DEBUG_NEEDLES:
        if needle in low:
            debug.append(name)
    secrets = []
    for pattern, name in SECRET_RES:
        match = re.search(pattern, body)
        if match:
            secrets.append({"type": name, "offset": match.start()})
    return {
        "debug_signatures": sorted(set(debug)),
        "secret_types": secrets,
    }


def classify_surface(kind: str, status: int | None, body: str, home_title: str, home_hash: str) -> str:
    if status is None:
        return "error"
    if status in {401, 403}:
        return "gated"
    if status in {404, 410}:
        return "absent"
    if status in {301, 302, 303, 307, 308}:
        return "redirect"
    if status != 200:
        return f"http-{status}"
    snippet = body[:8000]
    digest = hashlib.sha256(body.encode("utf-8", errors="replace")).hexdigest()
    if home_hash and digest == home_hash:
        return "catchall"
    if home_title and _looks_like_html(body):
        title = ""
        m = re.search(r"<title[^>]*>(.*?)</title>", body, flags=re.I | re.S)
        if m:
            title = re.sub(r"\s+", " ", m.group(1)).strip()
        if title and title == home_title:
            return "catchall"
    if kind.startswith("dotenv"):
        return "exposed" if looks_like_env(snippet) else "catchall"
    sigs = SURFACE_SIG.get(kind, ())
    low = snippet.lower()
    if kind in {"robots", "sitemap", "security-txt"}:
        if _looks_like_html(snippet):
            return "catchall"
        if (sigs and any(s in low for s in sigs)) or snippet.strip():
            return "present"
        return "empty"
    if sigs and any(s in low for s in sigs):
        return "exposed"
    if _looks_like_html(snippet) and not sigs:
        return "catchall"
    if snippet.strip():
        return "present"
    return "empty"


def tls_info(host: str, port: int = 443) -> dict[str, Any]:
    ctx = ssl.create_default_context()
    try:
        with ctx.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host) as sock:
            sock.settimeout(TIMEOUT)
            sock.connect((host, port))
            cert = sock.getpeercert()
            version = sock.version()
            cipher = sock.cipher()
    except Exception as exc:  # noqa: BLE001. Surface probe: report the error.
        return {"ok": False, "error": str(exc)}
    if not cert:
        return {"ok": False, "error": "empty certificate"}
    not_after = cert.get("notAfter")
    days_left = None
    if not_after:
        exp = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        days_left = (exp - datetime.now(timezone.utc)).days
    issuer = {}
    for part in cert.get("issuer", ()):
        for k, v in part:
            issuer[k] = v
    legacy = {}
    for label, vmin, vmax in (
        ("tls1_0", ssl.TLSVersion.TLSv1, ssl.TLSVersion.TLSv1),
        ("tls1_1", ssl.TLSVersion.TLSv1_1, ssl.TLSVersion.TLSv1_1),
    ):
        legacy[label] = _tls_version_accepted(host, port, vmin, vmax)
    return {
        "ok": True,
        "subject": dict(x for tup in cert.get("subject", ()) for x in tup),
        "issuer": issuer,
        "not_before": cert.get("notBefore"),
        "not_after": not_after,
        "days_left": days_left,
        "protocol": version,
        "cipher": {"name": cipher[0], "version": cipher[1], "bits": cipher[2]} if cipher else None,
        "legacy_accepted": legacy,
    }


def _tls_version_accepted(host: str, port: int, minimum: ssl.TLSVersion, maximum: ssl.TLSVersion) -> dict[str, Any]:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ctx.minimum_version = minimum
            ctx.maximum_version = maximum
    except ValueError as exc:
        return {"accepted": False, "error": str(exc)}
    try:
        with ctx.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host) as sock:
            sock.settimeout(8)
            sock.connect((host, port))
            return {"accepted": True, "protocol": sock.version()}
    except Exception as exc:  # noqa: BLE001
        return {"accepted": False, "error": type(exc).__name__}


def fetch(url: str, method: str = "GET") -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*"}, method=method)
    chain: list[dict[str, Any]] = []
    current = url
    body = ""
    final_headers: dict[str, str] = {}
    cookies: list[dict[str, Any]] = []
    status = None
    seen: set[str] = set()
    for _ in range(8):
        if current in seen:
            chain.append({"url": current, "error": "redirect loop"})
            break
        seen.add(current)
        try:
            with urlopen(req, timeout=TIMEOUT, context=ssl.create_default_context()) as resp:
                status = resp.getcode()
                final_headers = _headers_dict(resp.headers)
                set_all = []
                if hasattr(resp.headers, "get_all"):
                    set_all = resp.headers.get_all("Set-Cookie") or []
                cookies.extend(_parse_cookies(None if set_all else final_headers.get("set-cookie"), set_all))
                raw = resp.read(1_500_000)
                ctype = final_headers.get("content-type", "")
                if "text" in ctype or "json" in ctype or "html" in ctype or "xml" in ctype or not ctype:
                    body = raw.decode(errors="replace")
                chain.append({"url": current, "status": status, "final": resp.geturl()})
                current = resp.geturl()
                break
        except HTTPError as exc:
            status = exc.code
            final_headers = _headers_dict(exc.headers or {})
            set_all = []
            if exc.headers and hasattr(exc.headers, "get_all"):
                set_all = exc.headers.get_all("Set-Cookie") or []
            cookies.extend(_parse_cookies(None if set_all else final_headers.get("set-cookie"), set_all))
            loc = exc.headers.get("Location") if exc.headers else None
            chain.append({"url": current, "status": status, "location": loc})
            if loc and status in {301, 302, 303, 307, 308} and method == "GET":
                current = urljoin(current, loc)
                req = Request(current, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
                continue
            try:
                body = exc.read(200_000).decode(errors="replace")
            except Exception:
                body = ""
            break
        except URLError as exc:
            chain.append({"url": current, "error": str(exc.reason)})
            status = None
            break
    return {
        "requested": url,
        "final_url": current,
        "status": status,
        "redirects": chain,
        "headers": final_headers,
        "cookies": cookies,
        "body": body,
    }


def jsonld_types(blob: str) -> list[str]:
    types: list[str] = []
    try:
        data = json.loads(blob)
    except json.JSONDecodeError:
        return types

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            typed = obj.get("@type")
            if isinstance(typed, str):
                types.append(typed.rsplit("/", 1)[-1])
            elif isinstance(typed, list):
                for item in typed:
                    if isinstance(item, str):
                        types.append(item.rsplit("/", 1)[-1])
            for val in obj.values():
                walk(val)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)
    return types


def parse_link_header(value: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if not value:
        return items
    for part in re.split(r",(?=\s*<)", value):
        match = re.match(r"\s*<([^>]+)>\s*(.*)$", part.strip())
        if not match:
            continue
        href, rest = match.group(1), match.group(2)
        attrs = {"href": href}
        for am in re.finditer(r"(\w+)\s*=\s*(?:\"([^\"]+)\"|([^;,]+))", rest):
            attrs[am.group(1).lower()] = (am.group(2) or am.group(3) or "").strip()
        items.append(attrs)
    return items


def parse_robots(body: str) -> dict[str, Any]:
    if _looks_like_html(body):
        return {"ok": False, "error": "html"}
    sitemaps: list[str] = []
    groups: list[dict[str, Any]] = []
    uas: list[str] = []
    disallows: list[str] = []
    allows: list[str] = []
    has_noindex_line = False

    def flush() -> None:
        nonlocal uas, disallows, allows
        if uas or disallows or allows:
            groups.append({"user_agents": uas, "disallow": disallows, "allow": allows})
        uas, disallows, allows = [], [], []

    for raw in body.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip()
        if key == "sitemap":
            sitemaps.append(val)
        elif key == "user-agent":
            if disallows or allows:
                flush()
            uas.append(val)
        elif key == "disallow":
            disallows.append(val)
        elif key == "allow":
            allows.append(val)
        elif key == "noindex":
            has_noindex_line = True
    flush()
    star_disallow_all = any(
        any(ua == "*" for ua in group["user_agents"]) and any(d == "/" for d in group["disallow"])
        for group in groups
    )
    return {
        "ok": True,
        "sitemaps": sitemaps,
        "groups": groups[:20],
        "disallow_all": star_disallow_all,
        "unsupported_noindex_line": has_noindex_line,
    }


def parse_sitemap(body: str) -> dict[str, Any]:
    if _looks_like_html(body):
        return {"ok": False, "error": "html"}
    low = body.lower()
    locs = [re.sub(r"\s+", "", item) for item in re.findall(r"<loc>\s*([^<]+)\s*</loc>", body, flags=re.I)]
    kind = "other"
    if "<sitemapindex" in low:
        kind = "sitemapindex"
    elif "<urlset" in low:
        kind = "urlset"
    elif locs:
        kind = "xml-locs"
    else:
        lines = [ln.strip() for ln in body.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        if lines and all(ln.startswith("http://") or ln.startswith("https://") for ln in lines):
            kind = "text"
            locs = lines
    return {
        "ok": True,
        "kind": kind,
        "url_count": len(locs),
        "http_locs": sum(1 for item in locs if item.lower().startswith("http://")),
        "https_locs": sum(1 for item in locs if item.lower().startswith("https://")),
        "relative_locs": sum(
            1 for item in locs if not item.lower().startswith("http://") and not item.lower().startswith("https://")
        ),
        "sample_locs": locs[:10],
    }


def _norm_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{path}"


def extract_seo(url: str, html: str, headers: dict[str, str]) -> dict[str, Any]:
    page = _Page()
    try:
        page.feed(html)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}
    title = re.sub(r"\s+", " ", "".join(page.title_parts)).strip()
    desc = ""
    robots_meta: list[str] = []
    viewport = ""
    charset = ""
    refresh = ""
    og: dict[str, str] = {}
    twitter: dict[str, str] = {}
    for meta in page.metas:
        name = meta.get("name") or ""
        prop = meta.get("property") or ""
        content = meta.get("content") or ""
        if meta.get("charset"):
            charset = meta["charset"]
        if name == "description" and not desc:
            desc = content
        if name in {"robots", "googlebot"} and content:
            robots_meta.append(f"{name}:{content}")
        if name == "viewport":
            viewport = content
        if meta.get("http_equiv") == "refresh":
            refresh = content
        if meta.get("http_equiv") == "content-type" and "charset=" in content.lower():
            charset = content.split("charset", 1)[-1].lstrip("=").strip()
        if prop.startswith("og:") and prop not in og:
            og[prop] = content[:200]
        if name.startswith("twitter:") and name not in twitter:
            twitter[name] = content[:200]
    canonicals: list[dict[str, Any]] = []
    hreflang: list[dict[str, str]] = []
    for link in page.rel_links:
        rels = (link.get("rel") or "").split()
        raw_href = link.get("href") or ""
        href = urljoin(url, raw_href) if raw_href else ""
        if "canonical" in rels:
            parsed = urlparse(raw_href)
            canonicals.append(
                {
                    "href": href,
                    "raw": raw_href[:300],
                    "absolute": bool(parsed.scheme),
                    "https": parsed.scheme.lower() == "https"
                    or (not parsed.scheme and urlparse(url).scheme == "https"),
                    "fragment": bool(urlparse(raw_href).fragment),
                    "has_hreflang": bool(link.get("hreflang")),
                    "has_media": bool(link.get("media")),
                    "source": "html",
                }
            )
        if "alternate" in rels and link.get("hreflang"):
            hreflang.append(
                {
                    "lang": link.get("hreflang") or "",
                    "href": href,
                    "raw": raw_href[:300],
                    "absolute": bool(urlparse(raw_href).scheme),
                }
            )
    for item in parse_link_header(headers.get("link") or ""):
        rels = (item.get("rel") or "").lower().split()
        href = item.get("href") or ""
        if "canonical" in rels:
            parsed = urlparse(href)
            canonicals.append(
                {
                    "href": href,
                    "raw": href[:300],
                    "absolute": bool(parsed.scheme),
                    "https": parsed.scheme.lower() == "https",
                    "fragment": bool(parsed.fragment),
                    "has_hreflang": bool(item.get("hreflang")),
                    "has_media": bool(item.get("media")),
                    "source": "header",
                }
            )
        if "alternate" in rels and item.get("hreflang"):
            hreflang.append(
                {
                    "lang": item.get("hreflang") or "",
                    "href": href,
                    "raw": href[:300],
                    "absolute": bool(urlparse(href).scheme),
                }
            )
    seen_alt: set[tuple[str, str]] = set()
    unique_alt: list[dict[str, str]] = []
    for item in hreflang:
        key = (item.get("lang") or "", item.get("href") or "")
        if key in seen_alt:
            continue
        seen_alt.add(key)
        unique_alt.append(item)
    hreflang = unique_alt
    xrobots = headers.get("x-robots-tag") or ""
    robots_blob = " ".join(robots_meta + [xrobots]).lower()
    h1s = [h for h in page.headings if h["level"] == 1]
    skip = False
    prev = 0
    for heading in page.headings:
        lvl = int(heading["level"])
        if prev and lvl > prev + 1:
            skip = True
        prev = lvl
    title_low = title.lower().strip()
    compact_viewport = viewport.replace(" ", "").lower()
    return {
        "ok": True,
        "page_url": url,
        "title": {
            "text": title[:200],
            "chars": len(title),
            "empty": not title,
            "generic": title_low in GENERIC_TITLES,
        },
        "meta_description": {
            "present": bool(desc.strip()),
            "chars": len(desc.strip()),
            "text": desc.strip()[:240],
        },
        "robots_meta": robots_meta,
        "x_robots_tag": xrobots or None,
        "noindex": "noindex" in robots_blob,
        "nofollow": "nofollow" in robots_blob,
        "viewport": viewport[:200],
        "viewport_device_width": "width=device-width" in compact_viewport,
        "charset": charset[:40],
        "refresh_meta": refresh[:200] or None,
        "canonicals": canonicals[:8],
        "hreflang": hreflang[:20],
        "open_graph": og,
        "twitter": twitter,
        "jsonld_types": sorted(set(page.jsonld_types))[:30],
        "jsonld_blocks": page.jsonld_blocks,
        "itemtypes": sorted(set(page.itemtypes))[:20],
        "h1": [h["text"] for h in h1s][:8],
        "h1_count": len(h1s),
        "headings": page.headings[:40],
        "heading_skip": skip,
        "lang": page.lang,
        "soft_404_hint": any(needle in title_low for needle in SOFT_404_TITLE),
    }


def seo_flags(seo: dict[str, Any]) -> list[dict[str, str]]:
    if not seo.get("ok"):
        return [{"id": "seo_parse_error", "severity": "info", "detail": str(seo.get("error") or "parse")}]
    flags: list[dict[str, str]] = []
    title = seo.get("title") or {}
    if title.get("empty"):
        flags.append({"id": "title_empty", "severity": "majeur", "detail": "title element empty"})
    elif title.get("generic"):
        flags.append({"id": "title_generic", "severity": "mineur", "detail": title.get("text") or ""})
    elif int(title.get("chars") or 0) > 70:
        flags.append({"id": "title_long", "severity": "info", "detail": f"{title.get('chars')} chars"})
    desc = seo.get("meta_description") or {}
    if not desc.get("present"):
        flags.append({"id": "description_missing", "severity": "mineur", "detail": "no meta description"})
    elif int(desc.get("chars") or 0) < 20:
        flags.append({"id": "description_short", "severity": "mineur", "detail": f"{desc.get('chars')} chars"})
    if seo.get("noindex"):
        flags.append({"id": "noindex_present", "severity": "majeur", "detail": "reclass ok if staging"})
    if not seo.get("viewport"):
        flags.append({"id": "viewport_missing", "severity": "mineur", "detail": "no viewport meta"})
    elif not seo.get("viewport_device_width"):
        flags.append({"id": "viewport_no_device_width", "severity": "mineur", "detail": seo.get("viewport") or ""})
    if not seo.get("lang"):
        flags.append({"id": "lang_missing", "severity": "mineur", "detail": "html lang absent"})
    if seo.get("refresh_meta"):
        flags.append({"id": "refresh_meta", "severity": "mineur", "detail": seo.get("refresh_meta") or ""})
    canons = seo.get("canonicals") or []
    if not canons:
        flags.append({"id": "canonical_missing", "severity": "info", "detail": "google does not require it"})
    else:
        hrefs = {(item.get("href") or "").split("#", 1)[0] for item in canons}
        if len(hrefs) > 1:
            flags.append({"id": "canonical_conflict", "severity": "majeur", "detail": "multiple distinct canonicals"})
        for item in canons:
            raw = item.get("raw") or ""
            href = item.get("href") or ""
            if raw.lower().startswith("http://") or href.lower().startswith("http://"):
                flags.append({"id": "canonical_http", "severity": "majeur", "detail": raw or href})
            if not item.get("absolute"):
                flags.append({"id": "canonical_relative", "severity": "mineur", "detail": raw})
            if item.get("fragment"):
                flags.append({"id": "canonical_fragment", "severity": "mineur", "detail": raw})
            if item.get("has_hreflang") or item.get("has_media"):
                flags.append({"id": "canonical_ignored_attrs", "severity": "mineur", "detail": "hreflang/media on canonical"})
    if int(seo.get("h1_count") or 0) == 0:
        flags.append({"id": "h1_missing", "severity": "mineur", "detail": "no h1"})
    elif int(seo.get("h1_count") or 0) > 1:
        flags.append({"id": "h1_multiple", "severity": "info", "detail": str(seo.get("h1_count"))})
    robots = seo.get("robots") or {}
    if robots.get("ok") and robots.get("disallow_all"):
        flags.append({"id": "robots_disallow_all", "severity": "majeur", "detail": "User-agent: * Disallow: /"})
    if robots.get("unsupported_noindex_line"):
        flags.append({"id": "robots_noindex_line", "severity": "info", "detail": "Noindex in robots.txt is not a Google rule"})
    sitemap = seo.get("sitemap")
    if sitemap is None:
        flags.append({"id": "sitemap_unparsed", "severity": "info", "detail": "no sitemap body parsed"})
    elif sitemap.get("ok") and sitemap.get("http_locs"):
        flags.append({"id": "sitemap_http_locs", "severity": "mineur", "detail": str(sitemap.get("http_locs"))})
    elif sitemap.get("ok") and sitemap.get("relative_locs"):
        flags.append({"id": "sitemap_relative_locs", "severity": "mineur", "detail": str(sitemap.get("relative_locs"))})
    alts = seo.get("hreflang") or []
    if alts:
        if any(not item.get("absolute") for item in alts):
            flags.append({"id": "hreflang_relative", "severity": "mineur", "detail": "relative hreflang href"})
        page = seo.get("page_url") or ""
        if page and not any(_norm_url(item.get("href") or "") == _norm_url(page) for item in alts if item.get("href")):
            flags.append({"id": "hreflang_no_self", "severity": "mineur", "detail": "no self hreflang"})
        returns = seo.get("hreflang_return") or []
        missing = [item for item in returns if item.get("self") is False and item.get("returns") is False]
        if missing:
            flags.append({"id": "hreflang_no_return", "severity": "mineur", "detail": f"{len(missing)} alternate(s)"})
    if not seo.get("jsonld_types") and not seo.get("itemtypes"):
        flags.append({"id": "structured_data_absent", "severity": "info", "detail": "no json-ld or microdata"})
    if seo.get("soft_404_hint"):
        flags.append({"id": "soft_404_hint", "severity": "majeur", "detail": "title looks like a 404"})
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for flag in flags:
        if flag["id"] in seen:
            continue
        seen.add(flag["id"])
        unique.append(flag)
    return unique


def check_hreflang_return(page_url: str, alternates: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page_n = _norm_url(page_url)
    fetched = 0
    for alt in alternates:
        href = alt.get("href") or ""
        lang = alt.get("lang") or ""
        if not href:
            continue
        if _norm_url(href) == page_n:
            rows.append({"href": href, "lang": lang, "self": True, "returns": True})
            continue
        if fetched >= 3 or not href.startswith("http"):
            rows.append({"href": href, "lang": lang, "self": False, "returns": None, "note": "not fetched"})
            continue
        fetched += 1
        got = fetch(href)
        body = got.pop("body", "") or ""
        other = extract_seo(got.get("final_url") or href, body, got.get("headers") or {})
        back = any(_norm_url(item.get("href") or "") == page_n for item in (other.get("hreflang") or []) if item.get("href"))
        rows.append(
            {
                "href": href,
                "lang": lang,
                "self": False,
                "status": got.get("status"),
                "returns": back,
            }
        )
    return rows


def analyze_html(url: str, html: str) -> dict[str, Any]:
    page = _Page()
    try:
        page.feed(html)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}
    title = re.sub(r"\s+", " ", "".join(page.title_parts)).strip()
    legal = []
    query_secrets = []
    for link in page.links:
        text = (link.get("text") or "").lower()
        href = urljoin(url, link.get("href", ""))
        parsed = urlparse(href)
        path = parsed.path.lower()
        if any(h in text for h in LEGAL_TEXT) or any(p in path for p in LEGAL_PATH):
            legal.append({"text": (link.get("text") or "")[:120], "href": href})
        q = (parsed.query or "").lower()
        if any(k in q for k in ("token=", "access_token=", "api_key=", "apikey=", "session=")):
            query_secrets.append(parsed._replace(query="[redacted]").geturl()[:180])
    seen: set[str] = set()
    legal_u = []
    for item in legal:
        if item["href"] in seen:
            continue
        seen.add(item["href"])
        legal_u.append(item)
    trackers = []
    blob = html.lower()
    for needle, name in TRACKER_NEEDLES:
        if needle in blob:
            trackers.append(name)
    mixed = []
    if urlparse(url).scheme == "https":
        mixed = re.findall(r"""(?:src|href)=["'](http://[^"']+)""", html, flags=re.I)[:20]
    http_actions = [
        f["action"]
        for f in page.forms
        if (f.get("action") or "").lower().startswith("http://")
    ]
    return {
        "ok": True,
        "title": title[:200],
        "lang": page.lang,
        "legal_links": legal_u[:40],
        "scripts": [s["src"] for s in page.scripts][:40],
        "scripts_with_sri": page.sri_scripts,
        "forms": page.forms[:20],
        "password_fields": page.password_fields,
        "password_unmasked": page.password_unmasked,
        "http_form_actions": http_actions,
        "images_total": page.images_total,
        "images_missing_alt": page.images_missing_alt,
        "trackers_in_html": sorted(set(trackers)),
        "mixed_http_urls": mixed,
        "query_secret_hints": query_secrets[:10],
    }


def security_view(headers: dict[str, str]) -> dict[str, Any]:
    present = {h: headers[h] for h in SECURITY_HEADERS if h in headers}
    missing = [h for h in SECURITY_HEADERS if h not in headers]
    hsts = parse_hsts(present["strict-transport-security"]) if "strict-transport-security" in present else None
    csp = parse_csp(present["content-security-policy"]) if "content-security-policy" in present else None
    cors_origin = headers.get("access-control-allow-origin")
    cors_cred = headers.get("access-control-allow-credentials", "").lower() == "true"
    banners = {h: headers[h] for h in BANNER_HEADERS if h in headers}
    return {
        "present": present,
        "missing": missing,
        "hsts": hsts,
        "csp": csp,
        "cors_star": cors_origin == "*",
        "cors_star_with_credentials": cors_origin == "*" and cors_cred,
        "banners": banners,
        "content_type": headers.get("content-type"),
    }


def probe_surface(base: str, home_title: str, home_hash: str) -> list[dict[str, Any]]:
    parsed = urlparse(base)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    rows = []
    for path, kind in SURFACE_PATHS:
        fetched = fetch(urljoin(origin + "/", path.lstrip("/")))
        body = fetched.pop("body")
        status = fetched.get("status")
        verdict = classify_surface(kind, status, body, home_title, home_hash)
        row: dict[str, Any] = {
            "path": path,
            "kind": kind,
            "status": status,
            "final_url": fetched.get("final_url"),
            "verdict": verdict,
            "content_type": (fetched.get("headers") or {}).get("content-type"),
            "body_bytes": len(body.encode("utf-8", errors="replace")) if body else 0,
        }
        if kind == "robots" and verdict == "present":
            row["robots"] = parse_robots(body)
        elif kind == "sitemap" and verdict == "present":
            row["sitemap"] = parse_sitemap(body)
        rows.append(row)
    return rows


def http_upgrade(host: str) -> dict[str, Any]:
    url = f"http://{host}/"
    fetched = fetch(url)
    body = fetched.pop("body")
    final = fetched.get("final_url") or ""
    return {
        "requested": url,
        "status": fetched.get("status"),
        "final_url": final,
        "upgrades_to_https": final.startswith("https://"),
        "redirects": fetched.get("redirects"),
        "body_bytes": len(body.encode("utf-8", errors="replace")) if body else 0,
    }


def options_allow(url: str) -> dict[str, Any]:
    fetched = fetch(url, method="OPTIONS")
    fetched.pop("body", None)
    allow = (fetched.get("headers") or {}).get("allow")
    return {"status": fetched.get("status"), "allow": allow}


def probe_one(url: str, *, surface: bool = True, check_http: bool = True) -> dict[str, Any]:
    parsed = urlparse(url)
    rec: dict[str, Any] = {"url": url, "fetched_at": _now()}
    if parsed.scheme == "https" and parsed.hostname:
        rec["tls"] = tls_info(parsed.hostname, parsed.port or 443)
    else:
        rec["tls"] = {"ok": False, "error": "not https"}
    fetched = fetch(url)
    body = fetched.pop("body")
    rec.update(fetched)
    rec["security_headers"] = security_view(fetched["headers"])
    rec["options"] = options_allow(url)
    home_title = ""
    home_hash = ""
    if body:
        rec["html"] = analyze_html(fetched.get("final_url") or url, body)
        rec["body_bytes"] = len(body.encode("utf-8", errors="replace"))
        rec["leaks"] = scan_leaks(body)
        rec["seo"] = extract_seo(fetched.get("final_url") or url, body, fetched.get("headers") or {})
        home_title = rec["html"].get("title") or ""
        home_hash = hashlib.sha256(body.encode("utf-8", errors="replace")).hexdigest()
    else:
        rec["html"] = {"ok": False, "error": "empty body"}
        rec["body_bytes"] = 0
        rec["leaks"] = {"debug_signatures": [], "secret_types": []}
        rec["seo"] = {"ok": False, "error": "empty body"}
    if check_http and parsed.hostname:
        rec["http_upgrade"] = http_upgrade(parsed.hostname)
    if surface:
        rec["surface"] = probe_surface(fetched.get("final_url") or url, home_title, home_hash)
        for row in rec["surface"]:
            if row.get("robots"):
                rec["seo"]["robots"] = row["robots"]
            if row.get("sitemap"):
                rec["seo"]["sitemap"] = row["sitemap"]
        if rec["seo"].get("hreflang"):
            rec["seo"]["hreflang_return"] = check_hreflang_return(
                rec["seo"].get("page_url") or fetched.get("final_url") or url,
                rec["seo"]["hreflang"],
            )
    rec["seo"]["flags"] = seo_flags(rec["seo"])
    return rec


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Defensive surface probe for audit-fr")
    p.add_argument("urls", nargs="+")
    p.add_argument("-o", "--output", help="Write JSON report")
    p.add_argument("--no-surface", action="store_true", help="Skip well-known path GETs")
    p.add_argument("--no-http-upgrade", action="store_true", help="Skip port-80 upgrade check")
    args = p.parse_args(argv)
    report = {
        "generated_at": _now(),
        "note": "HTTP cookies and static HTML only. JS-set cookies are invisible. No payloads.",
        "version": "0.4.0",
        "targets": [
            probe_one(u, surface=not args.no_surface, check_http=not args.no_http_upgrade) for u in args.urls
        ],
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
