# Paste-ready aesthetics fragment (for projects WITHOUT an imported design system)

Append this to a creation prompt when the project has no design system and you want distinctive output. Source: Anthropic cookbook, "Prompting for frontend aesthetics". Do not use it when a design system is imported; the system governs and this fragment would fight the validator.

```
You tend to converge toward generic, "on distribution" outputs. In frontend design, this creates what users call the "AI slop" aesthetic. Avoid this: make creative, distinctive frontends that surprise and delight. Focus on:

Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics.

Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Draw from IDE themes and cultural aesthetics for inspiration.

Motion: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions.

Backgrounds: Create atmosphere and depth rather than defaulting to solid colors. Layer CSS gradients, use geometric patterns, or add contextual effects that match the overall aesthetic.

Avoid generic AI-generated aesthetics: overused font families, cliched color schemes, predictable layouts, cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context.
```

Dimension shortcuts when you want targeted control rather than the whole block:

- Typography only: name a pairing with high contrast (display + monospace, serif + geometric sans) and extreme weights (200 vs 800), size jumps of 3x or more.
- Palette only: name a source aesthetic (an IDE theme, a cultural reference) and one dominant color plus one sharp accent.
- Motion only: one orchestrated page-load with staggered reveals; skip everything else.
