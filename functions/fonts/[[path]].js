const ALLOWED_FONTS = new Set([
  "GT-America-Expanded-Regular.woff",
  "GT-America-Expanded-Regular.woff2",
  "GT-America-Standard-Medium.woff",
  "GT-America-Standard-Medium.woff2",
]);

export async function onRequest({ env, request }) {
  if (request.method !== "GET" && request.method !== "HEAD") {
    return new Response("Method not allowed", {
      status: 405,
      headers: { Allow: "GET, HEAD" },
    });
  }

  const key = new URL(request.url).pathname.slice("/fonts/".length);
  if (!ALLOWED_FONTS.has(key)) {
    return new Response("Not found", { status: 404 });
  }

  const font = await env.FONT_FILES.get(key);
  if (!font) {
    return new Response("Not found", { status: 404 });
  }

  const headers = new Headers();
  font.writeHttpMetadata(headers);
  headers.set("Access-Control-Allow-Origin", "*");
  headers.set("Cache-Control", "public, max-age=31536000, immutable");
  headers.set("ETag", font.httpEtag);
  headers.set("X-Content-Type-Options", "nosniff");

  return new Response(request.method === "HEAD" ? null : font.body, { headers });
}
