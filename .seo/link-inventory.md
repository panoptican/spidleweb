# Jason Spidle — Internal Link Inventory

> Every URL `/seo` can link to, and every URL it has shipped. Each new page picks ≥3 in-body links from here, takes ≥2 inbound links from existing pages (≥1 of them a frequently-crawled hub), and registers itself here on ship so the next page can link to it.

## Existing pages (link targets)

### Homepage + core marketing

| Slug | URL | Title (anchor-text candidate) | Linked by |
|---|---|---|---|
| `/` | https://spidleweb.net/ | Jason Spidle — Principal Product Designer | All case-study panels (← Index) |
| `/#work` | https://spidleweb.net/#work | Selected Work index | — |
| `/#profile` | https://spidleweb.net/#profile | Profile / bio | — |
| `/#contact` | https://spidleweb.net/#contact | Contact | — |

### Case studies (the content library)

| Slug | URL | Title | Linked by |
|---|---|---|---|
| `work/expert-insights` | https://spidleweb.net/work/expert-insights | Expert Insights — Scout dashboards | Homepage index |
| `work/campaign-sim` | https://spidleweb.net/work/campaign-sim | Campaign Sim — Planning simulation | Homepage index |
| `work/everag` | https://spidleweb.net/work/everag | Ever.Ag — Agtech design system | Homepage index |
| `work/vidscrip` | https://spidleweb.net/work/vidscrip | Vidscrip — Clinical workflows | Homepage index |
| `work/conservis` | https://spidleweb.net/work/conservis | Conservis — Agtech dashboards | Homepage index |
| `work/plinth` | https://spidleweb.net/work/plinth | PLINTH — Literary journal | Homepage index |

### Features / tools / blog

None. No blog, no tools, no feature pages yet — the six case studies are the whole library.

---

## Crawl hubs

> Fallback until GSC answers (`gsc.md` §7a): homepage is the only confirmed crawl hub. Re-derive from `batch_url_inspection` once connected.

| URL | Last crawled | Read on |
|---|---|---|
| `/` | unknown — GSC not connected | — |

---

## Programmatic pages

No programmatic surface exists yet. Pattern tables fill here if the programmatic lane ever ships batches — for a portfolio this will likely stay empty.

### `/alternatives/[slug]`

| Slug | Ships in phase | URL | Inbound links from | Outbound links to |
|---|---|---|---|---|

### `/for/[slug]`

| Slug | Ships in phase | URL | Inbound links from | Outbound links to |
|---|---|---|---|---|

### `/compare/[slug]`

| Slug | Ships in phase | URL | Inbound links from | Outbound links to |
|---|---|---|---|---|

### `/playbooks/[slug]`

| Slug | Ships in phase | URL | Inbound links from | Outbound links to |
|---|---|---|---|---|

---

## Editorial pieces shipped

> Appended on every run that ships a piece. The six case studies predate the ledger; they're backfilled in `.seo/content-ledger.md` and count as existing link targets above.

| Slug | URL | Title | Type | Inbound links from | Anchor-text variations |
|---|---|---|---|---|---|

---

## Anchor-text variations (avoid repetition)

When linking to the homepage, rotate:

- "Jason Spidle"
- "Jason Spidle's portfolio"
- "principal product designer Jason Spidle"
- "Spidleweb"
- "Jason Spidle, product designer in Minneapolis"

Case-study links: use the project name plus its kind ("Ever.Ag design system case study", "the Conservis dashboard work"), not bare "case study" or "read more".
