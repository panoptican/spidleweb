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
`wrangler` is still the right tool for inspecting deployments and managing
project secrets, below.

There is no build step and there are no Pages Functions: plain HTML, CSS, and
JS are served as-is. (A `functions/_middleware.js` client-preview gate existed
from 2026-08-20 to 2026-09-04; see below.)

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

**No variables are currently required.** `PREVIEW_PASSWORD` and
`PREVIEW_COOKIE_KEY` served the client-preview gate and are unused now that it
is gone. If they are still set on the project they are harmless, but they can
be deleted:

```
wrangler pages secret delete PREVIEW_PASSWORD --project-name spidleweb
wrangler pages secret delete PREVIEW_COOKIE_KEY --project-name spidleweb
```

## The client-preview gate, removed 2026-09-04

While the Expert Insights and Campaign Sim case studies were being cleared with
the client, `functions/_middleware.js` put a shared-password gate in front of
those two pages, their non-thumbnail screenshots, and their OG images, and the
two routes were kept out of `sitemap.xml`. The client approved both case
studies without changes for display without password protection on
2026-09-04, and the Function, its secrets' purpose, and the sitemap omissions
were removed the same day. The implementation (a styled 401 form setting a
signed, HttpOnly cookie, failing closed if either secret was unset) is in git
history at `functions/_middleware.js` should a gate be needed again.

## Local development

Static-only: open the files directly or run any static server.
`.claude/launch.json` defines `spidleweb-static`, a Python `http.server` on
port 8765, which is what the verification captures in `specs/verification.md`
run against. With no Functions there is nothing for `wrangler pages dev` to
exercise.
