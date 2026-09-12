# Needs you

Decisions, logins, reviews, and keys only a human can provide. The skill writes the `question` column. You write the `answer` column. The next run acts on any row with an answer and no `closed` date, then stamps it.

Keep answers to one line where you can. If the answer is "never" or "not now," say that; the row closes and the blocked candidate is dropped or deferred.

| id | opened | blocks | question | answer | closed |
|---|---|---|---|---|---|
| NY-1 | 2026-09-11 | GSC panels, census verdicts, outcomes, Performance backfill | Verify spidleweb.net in Google Search Console (a domain property is best: Settings → Ownership). Then give the host a Search Console MCP client authenticated with a Google account that has Full user access. What is the exact property string (e.g. `sc-domain:spidleweb.net` or `https://spidleweb.net/`)? | in progress — user verifying 2026-09-11 | |
| NY-2 | 2026-09-11 | competitor delta panel, battlecard, comparison research | Who do you actually get compared against? Name 3–7 designers or studios a hiring manager would weigh against you (or "skip" and the panel stays off). | skip — panel stays off until names are provided | 2026-09-11 |
| NY-3 | 2026-09-11 | Bing panel (Copilot grounding) | Optional, free: verify the site at bing.com/webmasters, create an API key in settings, export it as an env var, and tell me the variable's name (it goes in config.bing.api_key_env — the key itself is never stored). Connect now or skip? | | |
| NY-4 | 2026-09-11 | outcome measurement via Umami | Only when a run needs it: is there an Umami API key or shared dashboard link the skill can read for aggregate traffic? (Never per-visitor data.) | | |
| NY-5 | 2026-09-11 | radar accuracy | The radar seeds in .seo/radar.md and the positioning in .seo/brand.md are marked inferred. Confirm or correct: eight seeds from "senior product designer portfolio" to "hiring a principal product designer". | confirmed — positioning and all eight seeds kept as drafted | 2026-09-11 |
| NY-6 | 2026-09-11 | repo-changes panel sharpness | This repo has no changelog. Optional: keep one (even CHANGELOG.md with one line per deploy) so the product-change panel reads it instead of inferring from git log. Yes or no? | | |
