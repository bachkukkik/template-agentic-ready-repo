# Knowledge Base — Schema & Conventions

## Purpose

The KB is the authoritative source for project semantics, architecture decisions, data models, and research findings. PRDs and code reference KB entries via `[[wikilinks]]`.

## Directory Structure

```
kb/
├── SCHEMA.md       # This file
├── index.md        # Concept index (auto-maintained)
├── concepts/       # Architecture, decisions, patterns
├── entities/       # External services, vendors, integrations
└── raw/            # Raw research, imported articles
```

## Page Format

Every KB page uses YAML frontmatter + markdown body:

```markdown
---
title: "Concept Name"
tags: [tag1, tag2]
confidence: high  # high | medium | low
sources:
  - https://example.com
---

# Concept Name

[Body content...]
```

## Confidence Ratings

- **high** — Multiple independent sources verified
- **medium** — Single source + reasonable inference
- **low** — Unverified, needs validation

## Wikilinks

Use `[[page-name]]` to cross-reference KB pages. The page name is the filename without `.md`.

## Conventions

- One concept per file
- File names use kebab-case
- Concepts are stable facts; ephemeral state goes in `scratchpads/`
- Raw research is moved to `concepts/` or `entities/` after synthesis
