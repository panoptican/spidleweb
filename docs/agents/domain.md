# Domain Docs

Where this repo's documentation lives and how to consume it. Spidleweb is a
static portfolio: plain HTML, CSS, and JS with no build step, no framework, and
no application domain model. There is no `CONTEXT.md` and no `docs/adr/`, and
none is wanted — the documents below are the sources of truth.

## Before changing anything, read the relevant one

Read only what the task touches. None of these are required reading for a
one-line copy fix.

- **`PRODUCT.md`** — who the site is for and the brand register it has to hold
  (editorial, precise, brutalist) plus the anti-references. Read it before
  writing visitor-facing copy or proposing a visual direction.
- **`DESIGN.md`** — the design system, "The Documentarian Ledger." Colors,
  type ramp, and spacing live in its frontmatter. Read it before touching
  `style.css` or adding a page. Values here and in `style.css` must agree; if
  they disagree, `style.css` is what ships and `DESIGN.md` is the bug.
- **`specs/portfolio.md`** — the living spec for the site as built: every
  section, every case study, where each asset came from, and the decisions
  behind them. This is the first place to look for "why is it like this," and
  the place to record a decision that outlives the change.
- **`specs/verification.md`** — what has actually been checked and how. There
  are no automated tests for the site itself; this file is the record.
- **`docs/deployment.md`** — how the site ships. Read it before anything that
  touches deployment, secrets, or a redeploy.
- **`docs/agents/agent-access.md`** — the machine-readable surface
  (`/openapi.json`, `/.well-known/`, `robots.txt`, `sitemap.xml`) and the
  Cloudflare bot rules. Read it when changing routes, adding pages, or editing
  those files.

## Supporting material, not sources of truth

- **`specs/case-studies/`** — client source material the case studies were
  written from (PDFs, Figma prompts). Reference, not spec.
- **`specs/research/`** — background research. Informative; may be stale.
- **`specs/archive/`** — superseded specs, kept for history. Never cite as
  current.
- **`plans/`** — numbered, self-contained animation plans, all marked DONE.
  Historical record of shipped motion work.
- **`tests/`** — `test_agent_readiness.py` checks agent readability only:
  that the homepage carries meaningful raw HTML with sequential headings, and
  that `openapi.json`, the protected-resource metadata, and `_headers` agree
  with `agent-access.md`. It does not exercise appearance or behavior.

## Rules

**Use the vocabulary these documents already use.** `PRODUCT.md` and
`DESIGN.md` name things deliberately. When your output names a concept — an
issue title, a commit message, a CSS class, a spec heading — use the term
already in use rather than a synonym.

**Record decisions in `specs/portfolio.md`,** not in a new file. A decision
worth keeping goes in the relevant section there. Add a new document only when
a topic genuinely has no home; prefer growing the living spec.

**Surface contradictions instead of silently overriding.** If a change would
contradict what `PRODUCT.md`, `DESIGN.md`, or `specs/portfolio.md` says, say so
and name the document, rather than changing code and leaving the doc stale:

> _`specs/portfolio.md` says the Conservis 100% metric is unsourceable and
> banned — but you've asked for a metric there, so which source should it
> cite?_

**Update the doc in the same change as the code.** A change that makes one of
these documents wrong is not finished.
