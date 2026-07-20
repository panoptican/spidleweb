# Visitor hit counter

The footer counter on the homepage is a real, shared tally — not a per-browser
fake. It's served by a Cloudflare Pages Function backed by a Workers KV
namespace.

## Pieces

- `functions/api/hits.js` — the Pages Function. `GET /api/hits` reads the count;
  `GET /api/hits?bump=1` increments it. Reads/writes a single KV key (`total`).
- `jp.js` — the homepage script fetches `/api/hits`, bumping at most once per
  browser per day (tracked in `localStorage`), and otherwise just reads. If the
  request fails, the static number in the markup stays put.

## One-time Cloudflare setup

Pages Functions deploy automatically from the `functions/` directory on every
GitHub push — no build step. The only manual step is creating the KV namespace
and binding it, once:

1. Cloudflare dashboard → **Workers & Pages → KV → Create namespace**
   (e.g. name it `spidleweb-hits`).
2. Open the Pages project → **Settings → Functions → KV namespace bindings →
   Add binding**.
   - Variable name: `HITS` (must match the `env.HITS` used in the function)
   - KV namespace: the one created in step 1
   - Add it for **Production** (and Preview, if you want the counter live on
     preview deploys too).
3. Redeploy (or push any commit) so the binding takes effect.

Until the binding exists, `/api/hits` returns the base number (4721) and never
errors, so the page looks correct throughout.

## Notes

- The count seeds from `BASE = 4721` in `functions/api/hits.js` — the number the
  site displayed before the counter went live — so a fresh namespace doesn't
  reset the site to zero.
- KV is eventually consistent; under heavy concurrent load an occasional
  increment can be lost. That's an acceptable trade for a visitor counter.
- To set the count manually (e.g. seed a specific starting value), edit the
  `total` key in the KV namespace from the dashboard or with
  `npx wrangler kv key put --namespace-id=<id> total <value>`.
