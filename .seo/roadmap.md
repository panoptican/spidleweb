# Jason Spidle — Programmatic SEO Roadmap

> **Canonical document** for programmatic-page work. This is a seven-page portfolio: the programmatic lane will rarely fire, and that is correct. The roadmap exists so Phase 0 (technical foundations) is tracked and any future pattern batch starts warm.

---

## Phase Status Tracker

| # | Phase | Pattern | Status | PR |
|---|---|---|---|---|
| 0 | Technical foundations | Setup | in_progress | branch `seo/phase-0-schema` (PR TBD) |

**Conventions:**
- `pending` → `in_progress` → `completed` (in same commit as PR)
- PR column: `branch \`name\` (PR TBD)` then `#NNN` after `gh pr create`

---

## Reference Data (read once per agent)

### 1. Site facts

- **Domain:** https://spidleweb.net
- **GSC property:** not connected (user verifying 2026-09-11 — record exact string in `.seo/config.json` when the client answers)
- **Bing site:** not connected
- **OpenSEO project:** not connected
- **Authority / playable bucket:** unknown → `easy` (as of 2026-09-11, cold start)
- **Stack:** plain HTML, zero build tools, vanilla CSS/JS, Cloudflare Pages (auto-deploy on merge to `main`)
- **Brand accent color:** Archive Red `#fa1900`
- **Hero font / body font:** GT America Expanded / GT America
- **Marketing pages root:** repo root (`index.html`) + `work/`

### 2. Existing programmatic surface (DO NOT DUPLICATE)

None.

### 3. Critical files

| File | What lives there |
|---|---|
| `index.html` | Homepage: hero panel, Selected Work index, Shipped Sites, Profile, Contact |
| `work/*.html` | The six case studies (expert-insights, campaign-sim, everag, vidscrip, conservis, plinth) |
| `sitemap.xml` | Hand-maintained sitemap, 7 URLs, real content `lastmod` dates |
| `robots.txt` | Allows all, references sitemap |
| `_headers` | Cloudflare Pages headers (fonts CORS, openapi/.well-known content types) |
| `assets/og/*.png` | Per-page OG images, 1200×630, one per page |
| `PRODUCT.md` | Audience + product definition |
| `DESIGN.md` | Design tokens and the Documentarian Ledger system |

### 4. Data shapes

Plain HTML pages, no content collections. Case-study facts live in each page's `<dl class="panel__facts">` and `.seo/truth.md`.

### 5. Conventions

**URL slugs:** clean extensionless URLs via Cloudflare Pages (`work/vidscrip.html` → `/work/vidscrip`). Canonical tags must stay extensionless.

**Internal-link minimums per page:** every case study links back to the homepage index (← Index); any future editorial page takes ≥3 in-body links from `.seo/link-inventory.md` and ≥2 inbound links, one from the homepage.

**Schema:** hand-written JSON-LD `@graph` blocks, no build step (added 2026-09-12). Homepage: `Person` (`https://spidleweb.net/#person`) + `WebSite` (`#website`). Case studies: compact `Person` + `Article` + `BreadcrumbList`. New pages must carry the same pattern — see `.agents/skills/seo/references/schema-examples.md`.

**Deployment is merging to `main`.** Never merge from a run.

---

## Keyword Research Appendix

Empty — no keyword tool connected (2026-09-11). First research pass runs when GSC or DataForSEO answers. Until then, create candidates need demand provenance from dated community threads (`references/demand-radar.md`).

---

## Phases

### Phase 0 — Technical foundations

**Why:** the day-0 crawl shapes how Google understands the site for months. Most of Phase 0 is already done on this site; what remains is schema and console submission.

**Scope:**

1. ~~Sitemap.xml~~ — exists, 7 URLs, real lastmod dates.
2. ~~robots.txt~~ — allows all, references sitemap.
3. ~~Unique title + description per page~~ — present on all 7 pages, plus canonical and full OG/Twitter cards with per-page 1200×630 images.
4. ~~Add JSON-LD schema~~ — done 2026-09-12 on branch `seo/phase-0-schema`: `Person` + `WebSite` on the homepage, `Article` + `BreadcrumbList` on the six case studies, dates from git content history. Same pass repaired 5 stale sitemap `lastmod` values and repointed all internal links to canonical clean URLs (health_diff baseline 21 violations → 0 on the post-fix local fingerprint).
5. **Submit sitemap in Google Search Console** (human step, blocked on NY-1) and Bing Webmaster Tools (NY-3).
6. Optional: `llms.txt` at the root — the site is text-dense and already crawlable; low priority.

**Files modified:** `index.html`, `work/*.html` (JSON-LD blocks only).

**Verification:**
- [ ] `python3 .agents/skills/seo/scripts/tech_audit.py --domain https://spidleweb.net` returns 0 critical findings
- [ ] JSON-LD validates (Rich Results Test on `/` and one case study)
- [ ] Sitemap submitted in GSC (manual check, needs-you NY-1)

---

## Off-page checklist

For a portfolio the highest-value off-page surfaces are professional directories and profiles, not SaaS directories. Briefs only — a human does the sending.

- [ ] LinkedIn — exists (linkedin.com/in/jspidle); keep headline aligned with positioning
- [ ] Google Knowledge Panel — will follow from consistent `Person` schema (Phase 0)
- [ ] Designer Hangout / ADPList / similar professional directories — evaluate when a run surfaces them
- [ ] Crunchbase — only if Vault AI / Blueshift profiles warrant a person entry

---

## Glossary

- **Bucket** — Easy / Medium / Hard winnability read. Playable bucket is `easy` until GSC shows otherwise.
- **Striking distance** — pages ranking position 5-20 in GSC, one push from page 1.
