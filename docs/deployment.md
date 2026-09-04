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
affect the running site until a new deployment exists.

### Redeploying to pick up a changed variable

**Retrying a deployment re-promotes that deployment's commit**, so retrying an
older row in the dashboard silently rolls production back to older code. The
deployment list is newest-first and the top row is whatever deployed most
recently, which is not necessarily your newest commit — especially right after
someone has retried something.

The safe move is to push, which always builds the newest commit and puts it on
top. An empty commit is enough when the code has not changed:

```
git commit --allow-empty -m "site: redeploy" && git push
```

Retrying from the dashboard is fine too, as long as you retry the row whose
**Source** column matches the commit you actually want live, rather than
reaching for the top row.

Check what is deployed with:

```
wrangler pages deployment list --project-name spidleweb
```

Every deployment also keeps its own permanent `<id>.spidleweb.pages.dev` URL,
which is the quickest way to test whether a specific build works before
promoting it.

Variables are scoped per environment. A value set only on Production is absent
from preview branch deployments, and vice versa.

Current variables, both required by the client-preview gate:

- `PREVIEW_PASSWORD` — the shared password the client types.
- `PREVIEW_COOKIE_KEY` — signs the unlock cookie. Generate a long random value
  (`openssl rand -hex 32`); do not reuse the password here.

## Client-preview gate

`functions/_middleware.js` puts a password gate in front of the case studies
that are still being cleared with the client. It runs on every request and
returns `next()` untouched for anything not in its `GATED` set, so the rest of
the site is unaffected.

Currently gated:

- `/work/expert-insights` and `/work/campaign-sim` (clean and `.html` forms)
- `assets/expert-insights-02.png` through `-07.png` and
  `assets/campaign-sim-02.png` through `-04.png`
- `assets/og/expert-insights.png` and `assets/og/campaign-sim.png`

Deliberately left public: `assets/expert-insights-01.png` and
`assets/campaign-sim-01.png`, because the homepage index renders them as row
thumbnails. Gating them would break the public index.

### How unlocking works

A gated request without a valid cookie gets a styled page with a single
password field — deliberately **not** HTTP Basic Auth, which would show a
browser dialog containing a username box the client would have to be told to
ignore. Nothing sends a `WWW-Authenticate` header, so no native dialog appears.

Submitting the right password sets `sw_preview`, an `HttpOnly; Secure;
SameSite=Lax` cookie scoped to `/` and good for 30 days, then redirects back
with a 303. The cookie is `<expiry-ms>.<hmac>`, where the HMAC-SHA256 is taken
over the expiry using `PREVIEW_COOKIE_KEY`. The expiry travels in the clear but
is signed, so it cannot be extended without the key, and verification is done
with `crypto.subtle.verify`, which compares in constant time. One unlock covers
every gated path, pages and images alike.

Rotating either secret invalidates outstanding cookies and signs everyone out.

### Operational notes

If either variable is unset, gated paths return **500**, not the content. The
gate fails closed, so a missing secret is a broken page rather than a leak.

Use an ASCII password. It is compared to a value parsed from a form body, so
non-ASCII generally survives, but keeping it ASCII avoids encoding surprises
when the client copies it out of an email.

To change what is gated, edit the `GATED` set. To lift the gate entirely,
delete `functions/_middleware.js` and restore the affected `<url>` entries in
`sitemap.xml` — gated routes are kept out of the sitemap on purpose.

## Local development

Static-only changes need nothing more than opening the files or any static
server. To exercise `functions/`, run the Pages runtime with both bindings:

```
wrangler pages dev . --binding PREVIEW_PASSWORD=localtest PREVIEW_COOKIE_KEY=localkey
```

If that fails with `This Worker requires compatibility date "<today>", but the
newest date supported by this server binary is "<older>"`, the installed
wrangler's bundled `workerd` is behind the date wrangler defaults to. Pin it:

```
wrangler pages dev . --compatibility-date=2026-07-15 --binding PREVIEW_PASSWORD=localtest PREVIEW_COOKIE_KEY=localkey
```

This only affects local dev; deployed Functions run on Cloudflare's edge.
Upgrading wrangler is the real fix.

Note that the gate page returns 401, and Chrome's extension screenshot API
refuses to capture a frame with an error status. To screenshot it, either save
the markup as a static file or use headless Chrome directly
(`--headless --screenshot=out.png <url>`), which captures 401 bodies fine.
