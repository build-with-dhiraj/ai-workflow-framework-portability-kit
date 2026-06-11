#!/usr/bin/env python3
"""
Count rendered characters in LaTeX resume/CV bullets.
Strips LaTeX markup to show what a reader actually sees on the page, then
classifies each bullet into a variant (1L/2L/3L) and flags budget status.

Usage:
  python3 char_count.py "\\textbf{DFT} analysis of \\ce{TiO2} surfaces"
  echo "bullet text" | python3 char_count.py
  python3 char_count.py -f cv output/file.tex     # all \\item lines + total line count
  python3 char_count.py --raw "bullet text"       # just the number (for scripting)

Limits match the 7.5in-textwidth templates shipped with the master-resume skill.
"""

import re
import sys
import argparse


def strip_latex(text):
    """Strip LaTeX markup to get rendered text."""
    text = re.sub(r'\\item\s*(\[\s*\])?\s*', '', text)            # \item[] prefix
    text = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', text)      # \href{url}{text} -> text
    for cmd in ('textbf', 'textit', 'underline', 'emph', 'ce'):   # \cmd{X} -> X
        text = re.sub(r'\\%s\{([^}]*)\}' % cmd, r'\1', text)
    greeks = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
              'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma',
              'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega', 'Alpha', 'Beta',
              'Gamma', 'Delta', 'Theta', 'Lambda', 'Sigma', 'Phi', 'Psi', 'Omega']
    for g in greeks:
        text = text.replace('$\\%s$' % g, 'G').replace('\\%s' % g, 'G')
    text = re.sub(r'\$\^\{?\\circ\}?\$', 'D', text)               # degree
    text = re.sub(r'\$\^\{?\\dagger\}?\$', 'D', text)             # dagger
    text = re.sub(r'\$\^\{([^}]*)\}\$', r'\1', text)              # superscript {..}
    text = re.sub(r'\$\^(.)\$', r'\1', text)                      # superscript single
    text = re.sub(r'\$_\{([^}]*)\}\$', r'\1', text)              # subscript {..}
    text = re.sub(r'\$_(.)\$', r'\1', text)                       # subscript single
    text = text.replace('$\\sim$', '~').replace('\\sim', '~').replace('\\textasciitilde', '~')
    text = re.sub(r'\$([<>])\$', r'\1', text)
    text = text.replace('---', '—').replace('--', '–')  # dashes
    text = text.replace('$', '')                                  # remaining math delims
    text = re.sub(r'\\[a-zA-Z]+\s*', '', text)                    # remaining \commands
    text = text.replace('{', '').replace('}', '')
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def count_bold_chars(text):
    return sum(len(m) for m in re.findall(r'\\textbf\{([^}]*)\}', text))


def count_em_dashes(text):
    return len(re.findall(r'---', text))


def classify_bullet(char_count, bold_chars, fmt):
    if fmt == 'resume':
        base, penalty = 119, 0.5
        tiers = [('1L', 105, 111, 117, None), ('2L', 189, 205, 218, 78)]
    else:
        base, penalty = 91, 0.25
        tiers = [('1L', 88, 93, 101, None), ('2L', 168, 182, 190, 65), ('3L', 250, 268, 280, 65)]
    effective = base - (penalty * bold_chars)
    for variant, lo, hi, hard_max, orphan in tiers:
        if char_count <= hard_max:
            status = 'SHORT' if char_count < lo else ('OK' if char_count <= hi else 'NEAR MAX')
            return variant, status, lo, hi, hard_max, orphan, effective
    return 'OVER', 'OVER LIMIT', 0, 0, 0, None, effective


def format_one(raw, fmt):
    rendered = strip_latex(raw)
    n = len(rendered)
    bold = count_bold_chars(raw)
    em = count_em_dashes(raw)
    variant, status, lo, hi, hard_max, orphan, eff = classify_bullet(n, bold, fmt)
    parts = ["  %3d chars | %s %s | %s (target %d-%d, max %d)" % (n, variant, fmt.upper(), status, lo, hi, hard_max)]
    if bold:
        parts.append("  Bold: %d chars -> effective limit/line: %.0f" % (bold, eff))
    if em:
        parts.append("  Em-dashes: %d (each ~2x wide, budget +%d extra)" % (em, em))
    parts.append("  Rendered: %s" % rendered)
    return '\n'.join(parts), variant


def extract_items(text):
    return [ln.strip() for ln in text.split('\n') if ln.strip().startswith('\\item')]


def main():
    p = argparse.ArgumentParser(description='Count rendered characters in LaTeX resume/CV bullets')
    p.add_argument('input', nargs='?', help='Bullet text or .tex file path')
    p.add_argument('-f', '--format', choices=['resume', 'cv'], default='resume', help='Document format (default: resume)')
    p.add_argument('--raw', action='store_true', help='Output only char count')
    args = p.parse_args()

    if args.input and args.input.endswith('.tex'):
        with open(args.input) as f:
            items = extract_items(f.read())
        if not items:
            print("No \\item lines found.")
            return
        total_lines = 0
        print("Found %d bullets (%s format):\n" % (len(items), args.format))
        for i, item in enumerate(items, 1):
            if args.raw:
                print(len(strip_latex(item)))
            else:
                report, variant = format_one(item, args.format)
                print("Bullet %d:\n%s\n" % (i, report))
                if variant != 'OVER':
                    total_lines += int(variant[0])
        if not args.raw:
            print("Total rendered lines: %d" % total_lines)
    elif args.input:
        print(len(strip_latex(args.input)) if args.raw else format_one(args.input, args.format)[0])
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            if args.raw:
                print(len(strip_latex(line)))
            else:
                print(format_one(line, args.format)[0] + '\n')


if __name__ == '__main__':
    main()
