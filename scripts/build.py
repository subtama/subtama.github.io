#!/usr/bin/env python3
"""
Static site builder — dependency-free (Python stdlib only).

Reads content/*.md (with simple frontmatter) and produces:
  - site/articles/<slug>.html  (one per article)
  - site/index.html            (card list of all articles, newest first)

Frontmatter format (top of each .md file):
---
title: 記事タイトル
description: メタディスクリプション（120字前後）
slug: url-slug
category: VOD比較
date: 2026-08-02
updated: 2026-08-02
---

Markdown subset supported: # ## ###, paragraphs, - / 1. lists,
**bold**, [text](url), tables (| a | b |), and shortcodes:
  ::cta url | ラベル | サブテキスト::   -> CTA button
  ::lead テキスト::                      -> highlighted lead paragraph

Run:  python3 scripts/build.py
"""
import os, re, json, html, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
TPL = os.path.join(ROOT, "templates")
OUT = os.path.join(ROOT, "site")
OUT_ARTICLES = os.path.join(OUT, "articles")


def load_config():
    with open(os.path.join(ROOT, "site.json"), encoding="utf-8") as f:
        return json.load(f)


def parse_frontmatter(text):
    meta = {}
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end].strip()
            body = text[end + 4:].lstrip("\n")
            for line in fm.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
    return meta, body


def _link_sub(m):
    label, url = m.group(1), m.group(2)
    if url.startswith("http"):
        # external (affiliate/outbound): nofollow sponsored + new tab
        return f'<a href="{url}" target="_blank" rel="nofollow sponsored">{label}</a>'
    # internal link: normal follow, same tab (helps topic-cluster SEO)
    return f'<a href="{url}">{label}</a>'


def inline(text):
    """Inline markdown: escape HTML first, then apply bold/links."""
    text = html.escape(text, quote=False)
    # links [label](url) — internal vs external handled in _link_sub
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link_sub, text)
    # bold **x**
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def md_to_html(body):
    lines = body.split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # shortcodes ::name ...::
        m = re.match(r"::cta\s+(.+?)::", stripped)
        if m:
            parts = [p.strip() for p in m.group(1).split("|")]
            url = parts[0]
            label = parts[1] if len(parts) > 1 else "公式サイトを見る"
            sub = parts[2] if len(parts) > 2 else ""
            sub_html = f"<small>{html.escape(sub)}</small>" if sub else ""
            out.append(f'<a class="cta" href="{html.escape(url)}" target="_blank" '
                       f'rel="nofollow sponsored">{html.escape(label)}{sub_html}</a>')
            i += 1
            continue
        m = re.match(r"::lead\s+(.+?)::", stripped)
        if m:
            out.append(f'<p class="lead">{inline(m.group(1))}</p>')
            i += 1
            continue

        # headings
        if stripped.startswith("### "):
            out.append(f"<h3>{inline(stripped[4:])}</h3>")
            i += 1
            continue
        if stripped.startswith("## "):
            out.append(f"<h2>{inline(stripped[3:])}</h2>")
            i += 1
            continue
        if stripped.startswith("# "):
            out.append(f"<h1>{inline(stripped[2:])}</h1>")
            i += 1
            continue

        # tables
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\|[\s:\-|]+\|?$", lines[i + 1].strip()):
            header = [c.strip() for c in stripped.strip("|").split("|")]
            out.append("<table><thead><tr>" +
                       "".join(f"<th>{inline(c)}</th>" for c in header) +
                       "</tr></thead><tbody>")
            i += 2
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
                i += 1
            out.append("</tbody></table>")
            continue

        # unordered list
        if stripped.startswith("- "):
            out.append("<ul>")
            while i < n and lines[i].strip().startswith("- "):
                out.append(f"<li>{inline(lines[i].strip()[2:])}</li>")
                i += 1
            out.append("</ul>")
            continue

        # ordered list
        if re.match(r"^\d+\.\s", stripped):
            out.append("<ol>")
            while i < n and re.match(r"^\d+\.\s", lines[i].strip()):
                item = re.sub(r"^\d+\.\s", "", lines[i].strip())
                out.append(f"<li>{inline(item)}</li>")
                i += 1
            out.append("</ol>")
            continue

        # paragraph (gather consecutive non-blank, non-special lines)
        para = [stripped]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#|-|\d+\.|\||::)", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")

    return "\n".join(out)


def render(tpl, mapping):
    for k, v in mapping.items():
        tpl = tpl.replace("{{" + k + "}}", str(v))
    return tpl


def main():
    cfg = load_config()
    os.makedirs(OUT_ARTICLES, exist_ok=True)
    with open(os.path.join(TPL, "article.html"), encoding="utf-8") as f:
        article_tpl = f.read()
    with open(os.path.join(TPL, "index.html"), encoding="utf-8") as f:
        index_tpl = f.read()

    articles = []
    for path in glob.glob(os.path.join(CONTENT, "*.md")):
        with open(path, encoding="utf-8") as f:
            meta, body = parse_frontmatter(f.read())
        slug = meta.get("slug") or os.path.splitext(os.path.basename(path))[0]
        meta["slug"] = slug
        meta.setdefault("updated", meta.get("date", cfg["year"]))
        meta.setdefault("category", "比較")
        content_html = md_to_html(body)
        page = render(article_tpl, {
            "title": meta.get("title", slug),
            "description": meta.get("description", ""),
            "slug": slug,
            "category": meta.get("category"),
            "date": meta.get("date", ""),
            "updated": meta.get("updated"),
            "content": content_html,
            "site_name": cfg["site_name"],
            "base_url": cfg["base_url"],
            "year": cfg["year"],
        })
        with open(os.path.join(OUT_ARTICLES, slug + ".html"), "w", encoding="utf-8") as f:
            f.write(page)
        articles.append(meta)

    articles.sort(key=lambda m: m.get("date", ""), reverse=True)

    cards = []
    for m in articles:
        cards.append(
            f'<div class="card"><span class="tag">{html.escape(m.get("category",""))}</span>'
            f'<h2><a class="full" href="articles/{m["slug"]}.html">{html.escape(m.get("title",""))}</a></h2>'
            f'<p>{html.escape(m.get("description",""))}</p></div>'
        )

    index_html = render(index_tpl, {
        "site_name": cfg["site_name"],
        "tagline": cfg["tagline"],
        "site_description": cfg["site_description"],
        "base_url": cfg["base_url"],
        "year": cfg["year"],
        "cards": "\n".join(cards) if cards else "<p>記事を準備中です。</p>",
    })
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"Built {len(articles)} article(s) -> {OUT}")


if __name__ == "__main__":
    main()
