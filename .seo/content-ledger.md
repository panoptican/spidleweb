# Jason Spidle — Content Ledger

> The memory of the engine. Read first on every `/seo` run: the **Shipped** table is the dedup record (never re-write a covered topic); the **Performance** table is the scoreboard; the **Candidate backlog** is the scored shortlist so each run starts warm.

---

## Shipped

The six case studies shipped before the ledger existed — backfilled 2026-09-11 from the live site. Date shown is the sitemap `lastmod` (a content-touch date, not the original publish date). Vol/Bucket are blank: no keyword tool connected at backfill.

| Date | Title | Type | Slug / URL | Target keyword | Vol | Bucket | Original data (source · n · as-of) | Refresh due | Primary internal links | Commit / PR |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-04 | Expert Insights | case-study | /work/expert-insights | scout dashboard design, sports data platform | | | first-hand project account | n/a | Homepage index | pre-ledger |
| 2026-09-04 | Campaign Sim | case-study | /work/campaign-sim | campaign planning simulation, sports representation software | | | first-hand project account | n/a | Homepage index | pre-ledger |
| 2026-09-04 | Ever.Ag | case-study | /work/everag | agtech design system, enterprise design system | | | first-hand project account | n/a | Homepage index | pre-ledger |
| 2026-09-03 | Conservis | case-study | /work/conservis | farm management dashboard, agtech dashboard design | | | first-hand project account | n/a | Homepage index | pre-ledger |
| 2026-09-03 | Vidscrip | case-study | /work/vidscrip | clinical workflow design, patient journey timeline | | | first-hand project account | n/a | Homepage index | pre-ledger |
| 2026-09-03 | PLINTH | case-study | /work/plinth | literary journal design, editorial typography | | | first-hand project account | n/a | Homepage index | pre-ledger |

---

## Performance

> Filled by a later run from GSC (`references/gsc.md` §2), seeded as `unmeasured`. GSC is not connected yet — the first GSC-aware run must backfill all rows in one pass before selecting anything.
>
> **Backfilled:** never — waiting on GSC connection (needs-you NY-1).

| Slug / URL | Published | Indexed? (state · checked) | Read @28d | Read @56d | Site-wide same window | Best lever | State | Note / next action |
|---|---|---|---|---|---|---|---|---|
| /work/expert-insights | pre-ledger | unchecked | — | — | — | — | unmeasured | needs GSC |
| /work/campaign-sim | pre-ledger | unchecked | — | — | — | — | unmeasured | needs GSC |
| /work/everag | pre-ledger | unchecked | — | — | — | — | unmeasured | needs GSC |
| /work/conservis | pre-ledger | unchecked | — | — | — | — | unmeasured | needs GSC |
| /work/vidscrip | pre-ledger | unchecked | — | — | — | — | unmeasured | needs GSC |
| /work/plinth | pre-ledger | unchecked | — | — | — | — | unmeasured | needs GSC |

---

## Candidate backlog

> Empty. The first selection run builds the pool; with no GSC or DataForSEO, demand evidence must come from dated community threads (`demand` provenance) until GSC rows exist.

| Rank | Candidate | Proposed type | Target keyword | Vol | Bucket (E/M/H · src) | Intent | Data angle | Score | Notes / angle |
|---|---|---|---|---|---|---|---|---|---|

---

## Coverage map (optional)

| Cluster / theme | Pieces shipped | Gaps still open |
|---|---|---|
| Enterprise dashboards | Expert Insights, Conservis | financial-services dashboard case study (Ascensus work is linked out, not cased) |
| Design systems | Ever.Ag | none major |
| Complex workflows | Campaign Sim, Vidscrip | none major |
| Editorial / personal | PLINTH | none — intentionally small |

---

## Notes

- **Difficulty buckets, not a KD cap:** playable bucket is `easy` (cold start, no GSC yet).
- **This is a portfolio, not a content business:** `create-editorial` candidates must serve the hiring-manager audience (PRODUCT.md) and carry first-hand evidence. Volume-chasing pieces are off-brand per `brand.md` anti-positioning #5.
- **One piece per run.**
- **Refresh beats rewrite.** Case-study refresh = new numbers, new screens, sharper opening — same URL.
- **2026-09-12 repair (branch `seo/phase-0-schema`):** the backfilled dates above were stale sitemap `lastmod` values; re-derived from git history (last commit touching visible copy/imagery, delivery-plumbing commits excluded) and the sitemap corrected to match. Same branch added JSON-LD to all 7 pages and repointed internal links from `.html` hrefs to canonical clean URLs after the first health_diff fingerprint (`health/2026-09-12.json`, 21 violations) traced orphan/redirect violations to that root cause. Post-fix local fingerprint: `health/2026-09-12-post.json`, 0 violations.
