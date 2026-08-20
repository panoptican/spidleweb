# Deployment

## How the site ships

Cloudflare Pages project **`spidleweb`** (account "Spidleweb"), connected to
GitHub **`panoptican/spidleweb`**. Cloudflare builds and deploys on push;
production tracks **`main`**.

**Pushing to `main` is deploying.** There is no separate release step and no CI
in the repo — the absence of `.github/workflows/` does not mean the site is
deployed by hand.

Do not run `wrangler pages deploy`. It would upload a one-off deployment out of
band from git and leave the dashboard's build history disagreeing with `main`.
`wrangler` is still the right tool for secrets and local dev, below.

There is no build step: plain HTML, CSS, and JS are served as-is, and anything
under `functions/` is compiled by Cloudflare into a Pages Function.

## Environment variables and secrets

Set them in the dashboard (Pages → spidleweb → Settings → Variables and secrets)
or from the CLI:

```
wrangler pages secret put NAME --project-name spidleweb
```

Pages binds variables **at deploy time**, so adding or changing one does not
affect the running site until a new deployment exists. After changing a
variable, retry the latest deployment from the dashboard or push again.

Variables are scoped per environment. A value set only on Production is absent
from preview branch deployments, and vice versa.

Current variables:

- `PREVIEW_PASSWORD` — shared password for the client-preview gate, below.

## Client-preview gate

`functions/_middleware.js` puts HTTP Basic Auth in front of the case studies
that are still being cleared with the client. It runs on every request and
returns `next()` untouched for anything not in its `GATED` set, so the rest of
the site is unaffected.

Currently gated:

- `/work/expert-insights` and `/work/campaign-sim` (clean and `.html` forms)
- `assets/{expert-insights,campaign-sim}-02.png` and `-03.png`
- `assets/og/expert-insights.png` and `assets/og/campaign-sim.png`

Deliberately left public: `assets/expert-insights-01.png` and
`assets/campaign-sim-01.png`, because the homepage index renders them as row
thumbnails. Gating them would break the public index.

The password is only ever read from `env.PREVIEW_PASSWORD`; it is never
committed. Use an ASCII password — Basic credentials are latin1-decoded, so
non-ASCII characters will not compare equal.

If `PREVIEW_PASSWORD` is unset, gated paths return **500**, not the content.
The gate fails closed, so a missing secret is a broken page rather than a leak.

To change what is gated, edit the `GATED` set. To lift the gate entirely,
delete `functions/_middleware.js` and restore the affected `<url>` entries in
`sitemap.xml` — gated routes are kept out of the sitemap on purpose.

## Local development

Static-only changes need nothing more than opening the files or any static
server. To exercise `functions/`, run the Pages runtime:

```
wrangler pages dev . --binding PREVIEW_PASSWORD=localtest
```

If that fails with `This Worker requires compatibility date "<today>", but the
newest date supported by this server binary is "<older>"`, the installed
wrangler's bundled `workerd` is behind the date wrangler defaults to. Pin it:

```
wrangler pages dev . --compatibility-date=2026-07-15 --binding PREVIEW_PASSWORD=localtest
```

This only affects local dev; deployed Functions run on Cloudflare's edge.
Upgrading wrangler is the real fix.
