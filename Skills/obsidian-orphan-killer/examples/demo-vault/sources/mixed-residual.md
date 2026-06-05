---
title: Resolver residual demo
entities:
  - python3
  - SomeUnknownLibrary
topics:
  - PKM
  - SomethingThatDoesNotResolve
---

# Resolver residual demo

This note mixes resolvable (`python3` -> `[[python]]`, `PKM` ->
`[[knowledge-management]]`) and unresolvable (`SomeUnknownLibrary`,
`SomethingThatDoesNotResolve`) plain-string entities. The resolver should
rewrite the resolvable ones to wikilinks and leave the unresolvable ones as
plain strings (never minting a dangling link). The unresolvable surface
forms appear in the `top_residuals` report so the user can decide whether
to mint a hub for them later.
