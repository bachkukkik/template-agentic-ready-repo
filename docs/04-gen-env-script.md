# 04 — gen-env Script

## What

`scripts/gen-env.py` regenerates `.env` from `.env.example` line-by-line with the exact comment blocks preserved: `--fresh` writes a byte-identical copy for a new deployment, `--update` writes `.env.new` carrying the existing deployment's values key-by-key into the verbatim template.

## Why

- `.env.example` evolves alongside the codebase; a deployed `.env` drifts behind it and reconciling by hand loses operator-guidance comments.
- The user's usage contract (verbatim): *"gen new one for fresh deployment. Only update the new one, keep existing one to update the existing deployment"* — so the tool never touches a live `.env`.

## How

Stdlib-only Python 3 (`argparse`, `pathlib`), no subprocess, ~130 lines. Modes per `docs/prd/04-gen-env-script.md`:

| Mode | Target | Refuses without `--force` when |
|------|--------|-------------------------------|
| `--fresh` | `.env` | `.env` exists |
| `--update` | `.env.new` | `.env.new` exists |

`--update` reads the existing `.env`, maps `KEY` → value (exact key match, everything after the first `=`, `export ` prefixes ignored), rewrites `.env.example`'s lines with carried values, and prints dropped keys **by name only** — values are never echoed. Exit `0` on success, `1` on usage/environment errors.

## Verification

```bash
# Unit tier (5 hermetic tests, AC-GEN-001..005)
python3 -m pytest tests/unit/test_gen_env.py -v

# Whole tier
python3 -m pytest tests/unit -q          # 9 passed

# CLI smoke (scratch dir)
cd "$(mktemp -d)" && mkdir proj && cd proj
cp <repo>/.env.example .env.example
python3 <repo>/scripts/gen-env.py --fresh          # -> wrote .env
cmp .env .env.example && echo BYTE-IDENTICAL
# drift .env, add LEGACY_VAR=..., then:
python3 <repo>/scripts/gen-env.py --update         # -> wrote .env.new
                                                   #    dropped keys (not in .env.example): LEGACY_VAR
```

## What Works

- `--fresh` output is byte-identical to `.env.example` (`cmp` clean) — every comment block verbatim
- `--update` preserves the template's 13 comment lines, carries drifted values (`APP_NAME=prod-frontend`, `DB_PORT=6543` in the smoke), and drops `LEGACY_VAR` with a name-only stdout report; the dropped key never appears in `.env.new`
- The existing `.env` is untouched by `--update` (md5 identical before/after)
- `--fresh` over an existing `.env` refuses with exit 1 until `--force`
- Values with quotes, spaces, `=#` and unicode carry byte-exact; `export KEY=val` lines in the old `.env` are recognized
- 5/5 unit tests green; module imports side-effect-free (`if __name__ == "__main__"` guard)

## What Fails

- **No diff preview:** `--update` writes `.env.new` whole; an operator who wants a key-by-key diff runs `diff .env .env.new` themselves (chosen over embedding a diff for simplicity).
- **Comment-only drift is silent for values:** if a template line's *default* changed but the key exists in `.env`, the carried value hides the new default — visible only by reading `.env.new`'s comments vs value.
- **Flat key space:** sections are comments, not parsed structure; two `KEY=` lines with the same name in one file would be last-wins (not a real `.env` pattern, unguarded).

## Resolution

- **No diff preview:** documented behavior — `diff .env .env.new` is the review step before swapping.
- **Comment-only drift:** the operator reads `.env.new` before `mv .env.new .env`; the PRD's swap is manual by design.
- **Flat key space:** acceptable for `.env` semantics (duplicate keys are undefined behavior upstream anyway); no guard added.

## Verdict

**works** — Both modes verify end to end against the real `.env.example` (byte-identical fresh output; value-carrying update with name-only drop reports and an untouched source `.env`), guarded by 5 hermetic unit tests in the CI `unit` job.
