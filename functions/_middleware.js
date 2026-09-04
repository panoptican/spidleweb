/* Client-preview gate.

   Two case studies are still being cleared with the client, so they sit behind a
   shared password until that lands. Everything else on the site stays public,
   including the two `-01` screenshots the homepage index uses as row thumbnails
   (gating those would break the public index).

   Unlocking is a form on a styled page rather than HTTP Basic Auth, so the
   client sees one password field instead of a browser dialog with a username
   box they would have to be told to ignore. A correct password sets a signed,
   HttpOnly cookie good for COOKIE_DAYS days.

   Two Pages environment variables are required:
     wrangler pages secret put PREVIEW_PASSWORD   --project-name spidleweb
     wrangler pages secret put PREVIEW_COOKIE_KEY --project-name spidleweb
   PREVIEW_PASSWORD is what the client types. PREVIEW_COOKIE_KEY signs the
   cookie and should be a long random string, not a memorable one:
     openssl rand -hex 32
   Pages binds variables at deploy time, so setting them does not affect the
   live site until a new deployment exists — retry the deployment afterwards.

   If either variable is unset, gated paths return 500 rather than the content:
   the gate fails closed, so a missing secret breaks the page instead of
   leaking it. Rotating either one signs everyone out.

   To lift the gate, delete this file and restore the two <url> entries in
   sitemap.xml. See docs/deployment.md. */

const GATED = new Set([
  "/work/expert-insights",
  "/work/campaign-sim",
  "/assets/expert-insights-02.png",
  "/assets/expert-insights-03.png",
  "/assets/expert-insights-04.png",
  "/assets/expert-insights-05.png",
  "/assets/expert-insights-06.png",
  "/assets/expert-insights-07.png",
  "/assets/campaign-sim-02.png",
  "/assets/campaign-sim-03.png",
  "/assets/campaign-sim-04.png",
  "/assets/og/expert-insights.png",
  "/assets/og/campaign-sim.png",
]);

const COOKIE = "sw_preview";
const COOKIE_DAYS = 30;

/* Pages serves a page at both `/work/foo` and `/work/foo.html`, and asset
   matching is not reliably case-sensitive, so compare on one canonical form. */
function canonical(pathname) {
  const trimmed = pathname.replace(/\/+$/, "").toLowerCase() || "/";
  return trimmed.endsWith(".html") ? trimmed.slice(0, -5) : trimmed;
}

const bytes = (s) => new TextEncoder().encode(s);

function signingKey(secret) {
  return crypto.subtle.importKey(
    "raw",
    bytes(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"],
  );
}

/* Cookie value is `<expiry-ms>.<hex hmac of expiry>`. The expiry is carried in
   the clear and signed, so it cannot be extended without the key, and the
   cookie stays valid only until the timestamp it commits to. */
async function issue(env) {
  const expiry = Date.now() + COOKIE_DAYS * 86400_000;
  const signature = await crypto.subtle.sign(
    "HMAC",
    await signingKey(env.PREVIEW_COOKIE_KEY),
    bytes(String(expiry)),
  );
  const hex = [...new Uint8Array(signature)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  return `${COOKIE}=${expiry}.${hex}; Path=/; Max-Age=${COOKIE_DAYS * 86400}; HttpOnly; Secure; SameSite=Lax`;
}

async function unlocked(request, env) {
  const match = (request.headers.get("Cookie") || "").match(
    new RegExp(`(?:^|;\\s*)${COOKIE}=([^;]+)`),
  );
  if (!match) return false;

  const [expiry, hex] = decodeURIComponent(match[1]).split(".");
  if (!/^\d+$/.test(expiry || "") || !/^[0-9a-f]+$/.test(hex || "")) return false;
  if (Number(expiry) < Date.now()) return false;

  const signature = Uint8Array.from(
    hex.match(/../g).map((pair) => parseInt(pair, 16)),
  );
  /* subtle.verify compares in constant time. */
  return crypto.subtle.verify(
    "HMAC",
    await signingKey(env.PREVIEW_COOKIE_KEY),
    signature,
    bytes(String(Number(expiry))),
  );
}

const escapeAttr = (s) => s.replace(/[&<>"]/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

function gatePage(action, error) {
  return `<!doctype html>
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
  main { width: 100%; max-width: 34rem; }
  .label {
    font: 0.65rem/1 ui-monospace, "SF Mono", Menlo, monospace;
    letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent);
    padding-bottom: 12px; border-bottom: 1px solid var(--ink); margin-bottom: 24px;
  }
  h1 {
    font-family: "GT America Expanded", "Arial Black", Helvetica, sans-serif;
    font-size: clamp(1.35rem, 2.8vw, 2.5rem); font-weight: 400;
    line-height: 1.15; margin-bottom: 12px;
  }
  p.lede { margin-bottom: 32px; }
  label {
    display: block; margin-bottom: 8px;
    font: 0.65rem/1 ui-monospace, "SF Mono", Menlo, monospace;
    letter-spacing: 0.08em; text-transform: uppercase;
  }
  .row { display: flex; gap: 12px; flex-wrap: wrap; }
  input {
    flex: 1 1 16rem; min-width: 0;
    font-family: inherit; font-size: 1rem; font-weight: 500;
    padding: 12px; color: var(--ink);
    background: transparent; border: 1px solid var(--ink); border-radius: 0;
  }
  input:focus-visible, button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  button {
    font: 500 1rem/1 "GT America", Helvetica, Arial, sans-serif;
    padding: 12px 24px; cursor: pointer; border: 1px solid var(--ink);
    background: var(--ink); color: var(--paper); border-radius: 0;
    transition: background 120ms steps(2), color 120ms steps(2);
  }
  button:hover { background: var(--paper); color: var(--ink); }
  .error {
    margin-top: 16px; color: var(--accent);
    font: 0.8rem/1.4 ui-monospace, "SF Mono", Menlo, monospace;
  }
  .back { margin-top: 32px; font-size: 0.8rem; }
  a { color: inherit; }
  @media (prefers-reduced-motion: reduce) { button { transition: none; } }
</style>
<main>
  <p class="label">Client preview</p>
  <h1>This case study is under client review.</h1>
  <p class="lede">Enter the shared password to read it.</p>
  <form method="POST" action="${escapeAttr(action)}">
    <label for="password">Password</label>
    <div class="row">
      <input id="password" name="password" type="password" autocomplete="current-password"
             autofocus required spellcheck="false" aria-describedby="${error ? "error" : ""}">
      <button type="submit">Unlock</button>
    </div>
    ${error ? `<p class="error" id="error" role="alert">${escapeAttr(error)}</p>` : ""}
  </form>
  <p class="back">Or head back to the <a href="/">index</a>.</p>
</main>`;
}

const gateResponse = (action, error) =>
  new Response(gatePage(action, error), {
    status: 401,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex",
    },
  });

export async function onRequest({ request, next, env }) {
  const url = new URL(request.url);
  if (!GATED.has(canonical(url.pathname))) return next();

  if (!env.PREVIEW_PASSWORD || !env.PREVIEW_COOKIE_KEY) {
    return new Response(
      "PREVIEW_PASSWORD and PREVIEW_COOKIE_KEY must both be set on this deployment.",
      { status: 500, headers: { "Cache-Control": "no-store" } },
    );
  }

  if (request.method === "POST") {
    const submitted = (await request.formData()).get("password");
    if (submitted !== env.PREVIEW_PASSWORD) {
      return gateResponse(url.pathname, "That password is not right. Try again.");
    }
    /* 303 so the browser re-requests the page as a GET and a refresh does not
       resubmit the form. */
    return new Response(null, {
      status: 303,
      headers: {
        Location: url.pathname,
        "Set-Cookie": await issue(env),
        "Cache-Control": "no-store",
      },
    });
  }

  if (!(await unlocked(request, env))) return gateResponse(url.pathname);

  /* Copy the upstream response so the gated pages are never cached at the
     edge or in a shared proxy while they are still under review. */
  const upstream = await next();
  const response = new Response(upstream.body, upstream);
  response.headers.set("Cache-Control", "no-store");
  response.headers.set("X-Robots-Tag", "noindex");
  return response;
}
