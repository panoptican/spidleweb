// Cloudflare Pages Function — the real visitor counter.
//
// Backed by a Workers KV namespace bound as `HITS` on the Pages project
// (Settings → Functions → KV namespace bindings, variable name HITS).
// See docs/agents/hit-counter.md for the one-time setup.
//
//   GET /api/hits          → { count }  (read only)
//   GET /api/hits?bump=1    → increment, then { count }
//
// The client bumps once per browser per day and otherwise just reads, so the
// number is a genuine shared tally without inflating on every reload.

const KEY = 'total';

// Where the count picks up from, so a freshly-bound namespace doesn't reset
// the site to zero. Matches the number the page showed before it went live.
const BASE = 4721;

export async function onRequestGet({ request, env }) {
  const kv = env.HITS;

  // No binding yet — fail soft so the page keeps its static fallback.
  if (!kv) {
    return json({ count: BASE }, 200);
  }

  const bump = new URL(request.url).searchParams.get('bump') === '1';
  const current = parseInt(await kv.get(KEY), 10);
  let count = Number.isFinite(current) ? current : BASE;

  if (bump) {
    count += 1;
    // KV is eventually consistent; a lost write under heavy concurrency just
    // means an occasional skipped increment, which is fine for a visitor count.
    await kv.put(KEY, String(count));
  }

  return json({ count });
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
    },
  });
}
