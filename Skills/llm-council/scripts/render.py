#!/usr/bin/env python3
"""Render a council session into an HTML report + a markdown transcript.

Usage: render.py session.json [outdir]

session.json:
{
  "question": "the user's raw question",
  "framed":   "the framed question all advisors received",
  "advisors": [{"name": "The Contrarian", "letter": "C", "response": "..."}, ...],
  "reviews":  [{"reviewer": "The Contrarian", "text": "..."}, ...],
  "positions":[{"advisor": "The Contrarian", "stance": "against", "one_line": "..."}, ...],
  "verdict":  "## Where the Council Agrees\n..."   # chairman markdown
}
`letter` is that advisor's anonymized label from the peer-review round.
`positions` is optional; omit it to skip the stance grid.
"""
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

STANCE = {"for": ("#1a7f5a", "#e7f5ef"), "against": ("#b3402f", "#fbecea"),
          "reframe": ("#8a6d1f", "#fbf4e2")}


def md(text):
    """Minimal markdown -> HTML: ## headings, - lists, **bold**, *italic*, paragraphs."""
    out, buf = [], []

    def flush():
        if buf:
            out.append("<p>" + "<br>".join(buf) + "</p>")
            buf.clear()

    lines, i = text.split("\n"), 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("## "):
            flush()
            out.append(f"<h3>{inline(line[3:])}</h3>")
        elif line.lstrip().startswith(("- ", "* ")) or re.match(r"\s*\d+\. ", line):
            flush()
            items = []
            while i < len(lines) and (lines[i].lstrip().startswith(("- ", "* "))
                                      or re.match(r"\s*\d+\. ", lines[i])):
                items.append(f"<li>{inline(re.sub(r'^\s*(?:[-*]|\d+\.)\s+', '', lines[i]))}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif not line:
            flush()
        else:
            buf.append(inline(line))
        i += 1
    flush()
    return "\n".join(out)


def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", s)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)


def grid(positions):
    if not positions:
        return ""
    cells = []
    for p in positions:
        fg, bg = STANCE.get(p.get("stance", "").lower(), ("#4a4a4a", "#f0f0f0"))
        cells.append(
            f'<div class="pos" style="border-left:3px solid {fg};background:{bg}">'
            f'<div class="pos-a">{html.escape(p["advisor"])}</div>'
            f'<div class="pos-s" style="color:{fg}">{html.escape(p.get("stance", "")).upper()}</div>'
            f'<div class="pos-l">{inline(p.get("one_line", ""))}</div></div>')
    return '<h2>Where they landed</h2><div class="grid">' + "".join(cells) + "</div>"


CSS = """
*{box-sizing:border-box}
body{margin:0;padding:48px 24px;background:#fafaf9;color:#1c1c1a;
 font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
main{max-width:760px;margin:0 auto}
h1{font-size:15px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#8a8a80;margin:0 0 20px}
h2{font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
 color:#8a8a80;margin:44px 0 14px;padding-bottom:8px;border-bottom:1px solid #e6e4df}
h3{font-size:17px;font-weight:600;margin:26px 0 8px}
.q{font-size:20px;line-height:1.45;font-weight:500;margin:0 0 8px}
.framed{background:#fff;border:1px solid #e6e4df;border-radius:8px;padding:16px 20px;
 font-size:14px;color:#55554e;white-space:pre-wrap;margin-top:16px}
.verdict{background:#fff;border:1px solid #e6e4df;border-radius:10px;padding:8px 28px 24px}
.verdict h3:first-child{margin-top:18px}
.grid{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.pos{border-radius:6px;padding:12px 14px}
.pos-a{font-weight:600;font-size:14px}
.pos-s{font-size:11px;font-weight:700;letter-spacing:.08em;margin:2px 0 6px}
.pos-l{font-size:13px;color:#44443e}
details{background:#fff;border:1px solid #e6e4df;border-radius:8px;margin-bottom:8px}
summary{cursor:pointer;padding:13px 18px;font-weight:600;font-size:14px;list-style:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"+ ";color:#a8a89e;font-weight:400}
details[open] summary::before{content:"\\2212 "}
details>div{padding:0 18px 16px;border-top:1px solid #f0eeea;font-size:14px;color:#333330}
.tag{font-weight:400;color:#a8a89e;font-size:12px;margin-left:6px}
footer{margin-top:52px;padding-top:16px;border-top:1px solid #e6e4df;font-size:12px;color:#a0a098}
code{background:#f2f1ec;padding:1px 5px;border-radius:3px;font-size:.9em}
"""


def main():
    src = Path(sys.argv[1])
    outdir = Path(sys.argv[2] if len(sys.argv) > 2 else ".")
    s = json.loads(src.read_text())
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    stamp = datetime.now().strftime("%d %b %Y, %H:%M")

    advisors = "".join(
        f'<details><summary>{html.escape(a["name"])}'
        f'<span class="tag">reviewed as Response {html.escape(a.get("letter", "?"))}</span>'
        f'</summary><div>{md(a["response"])}</div></details>'
        for a in s["advisors"])
    reviews = "".join(
        f'<details><summary>{html.escape(r["reviewer"])} reviewing the room</summary>'
        f'<div>{md(r["text"])}</div></details>' for r in s.get("reviews", []))

    html_doc = f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Council verdict</title><style>{CSS}</style></head><body><main>
<h1>Council verdict</h1>
<p class="q">{inline(s["question"])}</p>
<div class="framed">{html.escape(s["framed"])}</div>
<h2>The verdict</h2>
<div class="verdict">{md(s["verdict"])}</div>
{grid(s.get("positions"))}
<h2>Advisors in full</h2>{advisors}
<h2>Peer review</h2>{reviews}
<footer>5 advisors &middot; blind peer review &middot; chairman synthesis &middot; {stamp}</footer>
</main></body></html>"""

    tr = [f"# Council transcript\n\n_{stamp}_\n",
          f"## The question\n\n{s['question']}\n",
          f"## Framed for the council\n\n{s['framed']}\n",
          "## Advisor responses\n"]
    tr += [f"### {a['name']}  _(anonymized as Response {a.get('letter','?')})_\n\n{a['response']}\n"
           for a in s["advisors"]]
    tr.append("## Peer reviews\n")
    tr += [f"### {r['reviewer']}\n\n{r['text']}\n" for r in s.get("reviews", [])]
    tr.append(f"## Chairman synthesis\n\n{s['verdict']}\n")

    hp = outdir / f"council-report-{ts}.html"
    mp = outdir / f"council-transcript-{ts}.md"
    hp.write_text(html_doc)
    mp.write_text("\n".join(tr))
    print(hp)
    print(mp)


if __name__ == "__main__":
    main()
