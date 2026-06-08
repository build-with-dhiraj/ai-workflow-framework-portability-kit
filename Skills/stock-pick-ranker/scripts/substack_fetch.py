#!/usr/bin/env python3
"""
Substack public-API helper (no API key). Resolve a profile, list a publication's post
archive, and fetch FREE post bodies as plain text. Paid-post bodies are paywalled and
must be pasted by the user.

Usage:
  python3 substack_fetch.py resolve <handle>                 # @handle or handle -> subdomain/id
  python3 substack_fetch.py archive <subdomain>              # all posts (title/slug/date/audience)
  python3 substack_fetch.py body    <subdomain> <slug>       # plain-text body of one free post
  python3 substack_fetch.py dump    <subdomain> [outdir]     # save all free post bodies to outdir/*.txt

Works with /usr/bin/python3 (stdlib only).
"""
import json
import os
import re
import sys
import time
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except Exception:
            if attempt == 4:
                raise
            time.sleep(1.5)


def resolve(handle):
    """@handle or handle -> {name, id, subdomain}."""
    h = handle.lstrip("@").strip()
    d = _get(f"https://substack.com/api/v1/user/{h}/public_profile")
    pub = d.get("primaryPublication") or {}
    return {"name": d.get("name"), "id": d.get("id"), "handle": d.get("handle"),
            "subdomain": pub.get("subdomain"), "publication": pub.get("name")}


def archive(subdomain):
    """All posts for a publication subdomain (paginated)."""
    posts, offset = [], 0
    while True:
        d = _get(f"https://{subdomain}.substack.com/api/v1/archive"
                 f"?sort=new&search=&offset={offset}&limit=50")
        if not isinstance(d, list) or not d:
            break
        for p in d:
            posts.append({"title": p.get("title"), "slug": p.get("slug"),
                          "post_date": (p.get("post_date") or "")[:10],
                          "audience": p.get("audience"),
                          "url": p.get("canonical_url")})
        if len(d) < 50:
            break
        offset += 50
        time.sleep(0.4)
    return posts


def body_text(subdomain, slug):
    """Plain-text body of a FREE post ('' for paywalled/empty)."""
    d = _get(f"https://{subdomain}.substack.com/api/v1/posts/{slug}")
    html = d.get("body_html") or ""
    text = re.sub("<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


def dump(subdomain, outdir):
    os.makedirs(outdir, exist_ok=True)
    posts = archive(subdomain)
    saved, free = [], 0
    for p in posts:
        if p.get("audience") != "everyone":
            continue
        free += 1
        txt = body_text(subdomain, p["slug"])
        path = os.path.join(outdir, f"{p['slug']}.txt")
        with open(path, "w") as f:
            f.write(f"# {p['title']}\n{p['post_date']}\n\n{txt}")
        saved.append(path)
        time.sleep(0.3)
    return {"total": len(posts), "free": free, "saved": saved}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "resolve":
        print(json.dumps(resolve(sys.argv[2]), indent=2, ensure_ascii=False))
    elif cmd == "archive":
        print(json.dumps(archive(sys.argv[2]), indent=2, ensure_ascii=False))
    elif cmd == "body":
        print(body_text(sys.argv[2], sys.argv[3]))
    elif cmd == "dump":
        outdir = sys.argv[3] if len(sys.argv) > 3 else f"/tmp/{sys.argv[2]}"
        print(json.dumps(dump(sys.argv[2], outdir), indent=2))
    else:
        print(__doc__)
        sys.exit(1)
