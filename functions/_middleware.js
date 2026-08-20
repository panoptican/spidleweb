/* Client-preview gate.

   Two case studies are still being cleared with the client, so they sit behind a
   shared password until that lands. Everything else on the site stays public,
   including the two `-01` screenshots the homepage index uses as row thumbnails
   (gating those would break the public index).

   The password lives in the PREVIEW_PASSWORD Pages environment variable:
     wrangler pages secret put PREVIEW_PASSWORD --project-name spidleweb
   Use an ASCII password: Basic credentials are latin1-decoded below, so a
   password with non-ASCII characters will not compare equal.

   To lift the gate, delete this file and restore the two <url> entries in
   sitemap.xml. */

const GATED = new Set([
  "/work/expert-insights",
  "/work/campaign-sim",
  "/assets/expert-insights-02.png",
  "/assets/expert-insights-03.png",
  "/assets/campaign-sim-02.png",
  "/assets/campaign-sim-03.png",
  "/assets/og/expert-insights.png",
  "/assets/og/campaign-sim.png",
]);

/* Pages serves a page at both `/work/foo` and `/work/foo.html`, and asset
   matching is not reliably case-sensitive, so compare on one canonical form. */
function canonical(pathname) {
  const trimmed = pathname.replace(/\/+$/, "").toLowerCase() || "/";
  return trimmed.endsWith(".html") ? trimmed.slice(0, -5) : trimmed;
}

function supplied(request) {
  const [scheme, encoded] = (request.headers.get("Authorization") || "").split(" ");
  if (scheme !== "Basic" || !encoded) return null;
  try {
    const decoded = atob(encoded);
    return decoded.slice(decoded.indexOf(":") + 1);
  } catch {
    return null;
  }
}

const CHALLENGE = `<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Client preview &mdash; Spidleweb</title>
<style>
  /* Self-contained: style.css is not linked here, so the two faces the page
     uses are redeclared against the same public /fonts paths. */
  @font-face {
    font-family: "GT America"; src: url("/fonts/Medium.ttf") format("truetype");
    font-weight: 500; font-display: swap;
  }
  @font-face {
    font-family: "GT America Expanded"; src: url("/fonts/Expanded.ttf") format("truetype");
    font-weight: 400; font-display: swap;
  }
  :root { --paper: #f2f2ef; --ink: #0a0a0a; --accent: #fa1900; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--paper); color: var(--ink);
    font: 500 1rem/1.5 "GT America", Helvetica, Arial, sans-serif;
    min-height: 100dvh; display: grid; place-items: center; padding: 24px;
    -webkit-font-smoothing: antialiased;
  }
  main { max-width: 34rem; }
  p.label {
    font: 0.65rem/1 ui-monospace, "SF Mono", Menlo, monospace;
    letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent);
    padding-bottom: 12px; border-bottom: 1px solid var(--ink); margin-bottom: 24px;
  }
  h1 {
    font-family: "GT America Expanded", "Arial Black", Helvetica, sans-serif;
    font-size: clamp(1.35rem, 2.8vw, 2.5rem); font-weight: 400;
    line-height: 1.15; margin-bottom: 12px;
  }
  a { color: inherit; }
</style>
<main>
  <p class="label">401 &mdash; Client preview</p>
  <h1>This case study is under client review.</h1>
  <p>Reload and enter the shared password to continue, or head back to the
  <a href="/">index</a>.</p>
</main>`;

export async function onRequest({ request, next, env }) {
  if (!GATED.has(canonical(new URL(request.url).pathname))) return next();

  if (!env.PREVIEW_PASSWORD) {
    return new Response("PREVIEW_PASSWORD is not set on this deployment.", {
      status: 500,
      headers: { "Cache-Control": "no-store" },
    });
  }

  if (supplied(request) === env.PREVIEW_PASSWORD) {
    /* Copy the upstream response so the gated pages are never cached at the
       edge or in a shared proxy while they are still under review. */
    const upstream = await next();
    const response = new Response(upstream.body, upstream);
    response.headers.set("Cache-Control", "no-store");
    response.headers.set("X-Robots-Tag", "noindex");
    return response;
  }

  return new Response(CHALLENGE, {
    status: 401,
    headers: {
      "WWW-Authenticate": 'Basic realm="Spidleweb client preview", charset="UTF-8"',
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex",
    },
  });
}
