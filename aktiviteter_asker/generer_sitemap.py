#!/usr/bin/env python3
"""Genererar sitemap.xml för askeridrett.no (GitHub Pages / Cloudflare).

Täcker index-sidan + alla klubbundersidor som ligger direkt på roten.
Kör:  python generer_sitemap.py
Skriver: sitemap.xml i samma mapp som skriptet.
"""
import os
import datetime
from urllib.parse import quote

BASE = "https://askeridrett.no"
HERE = os.path.dirname(os.path.abspath(__file__))

# Exkludera filer som inte ska indexeras
EXCLUDE = {
    "index.html",
    "aktiviteter_asker.html",  # innehållet serveras som / (roten)
}
# Mönster för filer som aldrig ska publiceras (backups, kopior, temp)
EXCLUDE_PATTERN = ("backup", " - Copy", "exempelklubben")

def lastmod_for(path):
    """Senaste ändringstid i W3C-format (senaste commit-tid approx)."""
    try:
        ts = os.path.getmtime(path)
        return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
    except OSError:
        return datetime.date.today().isoformat()

def build():
    urls = []
    # Index (roten)
    urls.append({"loc": f"{BASE}/", "lastmod": lastmod_for(os.path.join(HERE, "index.html"))})

    for name in sorted(os.listdir(HERE)):
        if not name.endswith(".html"):
            continue
        if name in EXCLUDE or any(p in name for p in EXCLUDE_PATTERN):
            continue
        path = os.path.join(HERE, name)
        slug = quote(name)
        urls.append({"loc": f"{BASE}/{slug}", "lastmod": lastmod_for(path)})

    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{u['loc']}</loc>")
        lines.append(f"    <lastmod>{u['lastmod']}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")

    out = os.path.join(HERE, "sitemap.xml")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Skrev {out}")
    print(f"Antal URL:er: {len(urls)} (index + undersidor)")
    return len(urls)

if __name__ == "__main__":
    n = build()
    print(f"Klart: {n} URL:er genererade.")
