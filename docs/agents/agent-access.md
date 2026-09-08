# Agent access

Spidleweb is a public, static portfolio. The homepage and case studies are
available as ordinary HTML documents and do not require JavaScript to expose
their content. The machine-readable entry points are:

- `/openapi.json` describes the public GET document resources.
- `/.well-known/oauth-protected-resource` publishes the `site:read` scope in
  the RFC 9728 protected-resource metadata format.
- `/robots.txt` allows all crawlers and links to `/sitemap.xml`.

The site currently has no OAuth authorization server and does not require a
bearer token. `site:read` is the least-privilege read scope declared for an
integration if delegated access is introduced later; the current documents
remain public.

## Cloudflare bot access

The site source cannot change zone-level Bot Management or WAF behavior. In
Cloudflare, add an ordered custom rule ahead of the challenge rule for
read-only public paths. Use the expression below as a starting point, then
select the Skip action for the bot-protection phases that are challenging the
requests in Security Events:

```text
(http.host eq "spidleweb.net"
  and http.request.method in {"GET" "HEAD"}
  and (http.request.uri.path eq "/"
    or starts_with(http.request.uri.path, "/work/")
    or http.request.uri.path in {"/openapi.json" "/robots.txt" "/sitemap.xml" "/.well-known/oauth-protected-resource"})
  and (http.user_agent contains "ChatGPT-User"
    or http.user_agent contains "ClaudeBot"
    or http.user_agent contains "Google-Extended"
    or http.user_agent contains "DeepSeekBot"
    or http.user_agent contains "ora-agent"
    or http.user_agent contains "GPTBot"
    or http.user_agent contains "PerplexityBot"
    or http.user_agent contains "Applebot-Extended"))
```

Keep the exception limited to public read paths and GET/HEAD requests because
User-Agent values can be spoofed. If the zone uses a built-in AI crawler block
or Bot Fight Mode that cannot be skipped, narrow or disable that setting for
these public reads and verify the result in Security Events. Do not use a
challenge or allow rule for write, login, or administrative paths.
