# Figma edit prompts — Expert Insights screens

One prompt per screen in `qa/precision-screens/`. Each is self-contained: select
the matching frame in Figma and paste the whole prompt. The shell edits
(wordmark, nav, disclaimer) repeat in every prompt on purpose — the screens may
be edited in any order, and if the shell is a shared component that has already
been changed, the agent simply finds nothing left to do there.

Export names after editing: `navigator-01` → `expert-insights-01`, and so on
through `-07`. The site currently uses `-01` to `-03`; `-04` to `-07` are new.

Names introduced by these prompts, all invented: Toma Vasquez, Elias Braun,
Ruben Achterberg, Dembe Osei, Rafael Eikeland, Dana Whitfield, Marcus Feld,
Idris Falk, Mateus Oyelaran, Kestrel Sports Group. Names carried over from the
current screens: Sophie Greenfield, Liam Hargrove, Emma Sinclair, Ethan Kim,
Oliver Chen, Mia Turner, Emma Zhang, Sarah Chen, Michael Ross, Lisa Park.

The sport is football (soccer) throughout — transfer fees, release clauses,
academies, loan spells, first-team minutes — but no real club, league,
competition, or person is ever named.

---

## navigator-01 — Dashboard

```
This screen is the Dashboard of a scout-intelligence platform used by a sports
representation agency. It tracks what talent scouts are saying about the
agency's own players and rival agencies' players. Update the text so the screen
reads as that product. Change only what is listed below. Keep the layout, type
styles, colors, icons, figures, chips, and spacing exactly as they are. Text
layers may reflow to fit new strings; do not change type sizes to compensate.

Shell:
- Wordmark, top-left: replace "Navigator365™ Matrix" with "Expert Insights".
  Replace the pink molecule icon beside it with a simple geometric mark in the
  same pink — a filled circle with three short white horizontal bars of
  increasing length is fine. Nothing that reads as a molecule, atom, or network.
- Left nav: "Experts" → "Scouts"; "Conferences" → "Showcases";
  "Therapeutic Areas" → "Leagues". Keep Dashboard, Analysis, Social Explorer,
  Search, Logout, and every icon.
- Disclaimer under What's Moving: change "regulatory, clinical, or strategic
  advice" to "scouting, contractual, or strategic advice". Leave the rest of the
  paragraph as is.

Stat cards:
- "active experts" → "active scouts". Keep "total discussions" and all four
  figures and deltas.

What's Moving (keep the title and the Auto-generated badge):
- Competitive Shift body → "Kestrel Sports Group's #NextWave campaign gained 23%
  share of voice, primarily through amplification of tracking data."
- Sentiment Driver body → "Negative sentiment spike (-12%) linked to
  release-clause discussions around Toma Vasquez"
- Emerging Theme body → "Load-management discussions up 340% following league
  guidance update on under-21 minutes"

Sentiment table:
- Title "Brand Sentiment" → "Roster Sentiment".
- Column header "Top Expert" → "Top Scout". Keep Discussions, Positive, Neutral,
  Negative, and the colored rule under the headers.
- Group label "My Brands" → "My Players"; "Competitor Brands" → "Rival Players".
- Row names, top to bottom: "Palbociclib" → "Toma Vasquez";
  "Ribociclib" → "Elias Braun"; "Abemaciclib" → "Ruben Achterberg";
  "Talazoparib" → "Dembe Osei"; "Trastuzumab" → "Rafael Eikeland".
- Every figure, percentage, leading dot, avatar, chevron, and scout name in the
  Top Scout column stays.
- The view toggle, download and settings icons, date-range button, and the
  floating pink AI button stay.
```

---

## navigator-02 — Search

```
This screen is the Search view of a scout-intelligence platform used by a sports
representation agency. It tracks what talent scouts are saying about the
agency's players. Update the text so the screen reads as that product. Change
only what is listed below. Keep the layout, type styles, colors, icons, figures,
chips, and spacing exactly as they are. Text layers may reflow to fit new
strings; do not change type sizes to compensate.

Shell:
- Wordmark, top-left: replace "Navigator365™ Matrix" with "Expert Insights".
  Replace the pink molecule icon beside it with a simple geometric mark in the
  same pink — a filled circle with three short white horizontal bars of
  increasing length is fine. Nothing that reads as a molecule, atom, or network.
- Left nav: "Experts" → "Scouts"; "Conferences" → "Showcases";
  "Therapeutic Areas" → "Leagues". Keep Dashboard, Analysis, Social Explorer,
  Search, Logout, and every icon. Search stays the active item.
- Disclaimer inside the Insights card: change "regulatory, clinical, or
  strategic advice" to "scouting, contractual, or strategic advice". Leave the
  rest of the paragraph as is.

Search row:
- Field value "#BreastCancerResearch" → "#AcademyWatch". Keep the Search button,
  the Filters button, and the date-range button.

Insights card (keep the title and the Auto-generated badge):
- Body → "Recent discussions reveal a dual landscape of rapid analytical
  progress and persistent access challenges in academy scouting. Tracking data
  is accelerating individualized development plans. While there is a growing
  focus on player welfare and long-term progression, the most critical hurdle
  is persistent disparity in scout coverage, particularly in rural catchments."
- The Sentiment heading, the bar, and its three labels stay.

Channel tabs:
- "Blogs" → "Scout Reports". Every other tab label and every count stays.
  X/Twitter stays the active tab.

Posts, top to bottom:
- Post 1: name "Maryam Lustberg" → "Dana Whitfield"; handle "@maryamlustberg"
  → "@danawhitfield"; body → "Breaking down the movement patterns that separate
  elite academy wingers. Our latest report identifies markers that could change
  how clubs recruit."
- Post 2: name "Dr. John Smith" → "Marcus Feld"; handle "@drjohnsmith" →
  "@marcusfeld"; body → "Scouts are digging deeper into academy data,
  uncovering insights that could change recruitment protocols. Stay tuned for
  updates."
- Post 3: keep "Emma Zhang" and "@emmazhang"; body → "Leading scouts in youth
  football are emphasizing the need for individualized development plans.
  Accessibility and tailored coaching are" — this post runs off the bottom of
  the frame mid-sentence today; keep it that way.
- Timestamps, sentiment chips, avatars, engagement counts, and the floating
  pink AI button stay.
```

---

## navigator-03 — Social Explorer

```
This screen is the Social Explorer view of a scout-intelligence platform used by
a sports representation agency. It compares scout conversation about up to
three players side by side. Update the text so the screen reads as that
product. Change only what is listed below. Keep the layout, type styles,
colors, icons, figures, chips, and spacing exactly as they are. Text layers may
reflow to fit new strings; do not change type sizes to compensate.

Shell:
- Wordmark, top-left: replace "Navigator365™ Matrix" with "Expert Insights".
  Replace the pink molecule icon beside it with a simple geometric mark in the
  same pink — a filled circle with three short white horizontal bars of
  increasing length is fine. Nothing that reads as a molecule, atom, or network.
- Left nav: "Experts" → "Scouts"; "Conferences" → "Showcases";
  "Therapeutic Areas" → "Leagues". Keep Dashboard, Analysis, Social Explorer,
  Search, Logout, and every icon. Social Explorer stays the active item.
- Disclaimer inside the Combined Analysis card: change "regulatory, clinical,
  or strategic advice" to "scouting, contractual, or strategic advice". Leave
  the rest of the paragraph as is.

Keyword row (keep the three labels, the Add buttons, Saved Reports, Filters,
and the date-range button):
- Keyword 1 value "Deruxtecan" → "Toma Vasquez"
- Keyword 2 value "Pertuzmab, Emtansine" → "Elias Braun"
- Keyword 3 value "Talazoparib" → "Dembe Osei"

Combined Analysis (keep the title and the Auto-generated badge):
- Body → "Comparative Analysis: Elias Braun leads in overall conversation
  volume with 332 active scouts, suggesting broader network reach. However,
  Toma Vasquez shows the strongest positive sentiment (50%), driven largely by
  academy coaches. While Elias Braun has visibility, qualitative analysis
  suggests Toma Vasquez is winning on scout perception."

Comparison columns, left to right:
- Column titles: "Deruxtecan" → "Toma Vasquez"; "Pertuzmab, Emtansine" →
  "Elias Braun"; "Talazoparib" → "Dembe Osei".
- "Top Experts" → "Top Scouts" in all three columns.
- The Discussions figures, sentiment bars and labels, "View full list" links,
  the four scout rows per column with their chips and post counts, and the
  floating pink AI button stay.
```

---

## navigator-04 — Dashboard with the Ask panel open

```
This screen is the Dashboard of a scout-intelligence platform used by a sports
representation agency, with its AI "Ask anything" panel open over the sentiment
table. Update the text so the screen reads as that product. Change only what is
listed below. Keep the layout, type styles, colors, icons, figures, chips, and
spacing exactly as they are. Text layers may reflow to fit new strings; let the
suggestion chips widen or narrow to their new text without wrapping; do not
change type sizes to compensate.

Shell:
- Wordmark, top-left: replace "Navigator365™ Matrix" with "Expert Insights".
  Replace the pink molecule icon beside it with a simple geometric mark in the
  same pink — a filled circle with three short white horizontal bars of
  increasing length is fine. Nothing that reads as a molecule, atom, or network.
- Left nav: "Experts" → "Scouts"; "Conferences" → "Showcases";
  "Therapeutic Areas" → "Leagues". Keep Dashboard, Analysis, Social Explorer,
  Search, Logout, and every icon.
- Disclaimer under What's Moving: change "regulatory, clinical, or strategic
  advice" to "scouting, contractual, or strategic advice". Leave the rest of the
  paragraph as is.

Dashboard content (identical to the plain Dashboard screen):
- Stat card "active experts" → "active scouts". Keep "total discussions" and
  all four figures and deltas.
- Competitive Shift body → "Kestrel Sports Group's #NextWave campaign gained 23%
  share of voice, primarily through amplification of tracking data."
- Sentiment Driver body → "Negative sentiment spike (-12%) linked to
  release-clause discussions around Toma Vasquez"
- Emerging Theme body → "Load-management discussions up 340% following league
  guidance update on under-21 minutes"
- Table title "Brand Sentiment" → "Roster Sentiment"; column header
  "Top Expert" → "Top Scout"; group label "My Brands" → "My Players";
  "Competitor Brands" → "Rival Players".
- Row names, top to bottom: "Palbociclib" → "Toma Vasquez"; "Ribociclib" →
  "Elias Braun"; "Abemaciclib" → "Ruben Achterberg"; "Talazoparib" → "Dembe Osei";
  "Trastuzumab" → "Rafael Eikeland". Every figure and scout name stays.

Ask panel (bottom-right):
- Keep the placeholder "Ask anything..." and the help icon.
- Suggestion chips, in order:
  - "What's driving Keytruda's positive sentiment?" → "What's driving Elias
    Braun's positive sentiment?"
  - "Compare Opdivo vs Tecentriq this quarter" → "Compare Idris Falk vs Mateus
    Oyelaran this quarter"
  - "Which DOLs are most active on combination therapy?" → "Which scouts are
    most active on under-21 prospects?"
  - "Summarize sentiment trends for my brands" → "Summarize sentiment trends
    for my players"
- The floating pink AI button stays.
```

---

## navigator-05 — Dashboard with an answer open: sentiment driver

```
This screen is the Dashboard of a scout-intelligence platform used by a sports
representation agency, with an AI answer panel open over the sentiment table.
Update the text so the screen reads as that product. Change only what is listed
below. Keep the layout, type styles, colors, icons, figures, chips, and spacing
exactly as they are. Text layers may reflow to fit new strings; do not change
type sizes to compensate.

Shell:
- Wordmark, top-left: replace "Navigator365™ Matrix" with "Expert Insights".
  Replace the pink molecule icon beside it with a simple geometric mark in the
  same pink — a filled circle with three short white horizontal bars of
  increasing length is fine. Nothing that reads as a molecule, atom, or network.
- Left nav: "Experts" → "Scouts"; "Conferences" → "Showcases";
  "Therapeutic Areas" → "Leagues". Keep Dashboard, Analysis, Social Explorer,
  Search, Logout, and every icon.
- Disclaimer under What's Moving (partly hidden behind the panel — edit it
  anyway): change "regulatory, clinical, or strategic advice" to "scouting,
  contractual, or strategic advice".

Dashboard content behind the panel (identical to the plain Dashboard screen;
edit the layers even where the panel covers them):
- Stat card "active experts" → "active scouts". Keep all figures and deltas.
- Competitive Shift body → "Kestrel Sports Group's #NextWave campaign gained 23%
  share of voice, primarily through amplification of tracking data."
- Sentiment Driver body → "Negative sentiment spike (-12%) linked to
  release-clause discussions around Toma Vasquez"
- Emerging Theme body → "Load-management discussions up 340% following league
  guidance update on under-21 minutes"
- Table title "Brand Sentiment" → "Roster Sentiment"; column header
  "Top Expert" → "Top Scout"; group label "My Brands" → "My Players";
  "Competitor Brands" → "Rival Players".
- Row names, top to bottom: "Palbociclib" → "Toma Vasquez"; "Ribociclib" →
  "Elias Braun"; "Abemaciclib" → "Ruben Achterberg"; "Talazoparib" → "Dembe Osei";
  "Trastuzumab" → "Rafael Eikeland". Every figure and scout name stays.

Answer panel:
- Title "What's driving Keytruda's positive sentiment?" → "What's driving Elias
  Braun's positive sentiment?"
- Insights body (keep the heading and the Auto-generated badge) → "Elias
  Braun's positive sentiment increased 18% this quarter, primarily driven by
  strong tracking data from the autumn fixtures and an expanded first-team
  role. Scout discussions emphasize his passing range under pressure."
- Under "What's driving sentiment": row "DESTINY trial data" → "Autumn tracking
  data"; row "HER2-low expansion" → "First-team role". Both chips stay Positive.
- "Top experts discussing" → "Top scouts discussing". The avatar row, "+5", and
  "View full list" stay.
- The follow-up input, Send button, thumbs, "Based on 847 discussions • Nov 3 -
  Dec 3, 2025", download icon, close icon, and the floating pink AI button
  stay.
```

---

## navigator-06 — Dashboard with an answer open: most active scouts

```
This screen is the Dashboard of a scout-intelligence platform used by a sports
representation agency, with an AI answer panel open over the sentiment table.
Update the text so the screen reads as that product. Change only what is listed
below. Keep the layout, type styles, colors, icons, figures, chips, and spacing
exactly as they are. Text layers may reflow to fit new strings; do not change
type sizes to compensate.

Shell:
- Wordmark, top-left: replace "Navigator365™ Matrix" with "Expert Insights".
  Replace the pink molecule icon beside it with a simple geometric mark in the
  same pink — a filled circle with three short white horizontal bars of
  increasing length is fine. Nothing that reads as a molecule, atom, or network.
- Left nav: "Experts" → "Scouts"; "Conferences" → "Showcases";
  "Therapeutic Areas" → "Leagues". Keep Dashboard, Analysis, Social Explorer,
  Search, Logout, and every icon.
- Disclaimer under What's Moving (partly hidden behind the panel — edit it
  anyway): change "regulatory, clinical, or strategic advice" to "scouting,
  contractual, or strategic advice".

Dashboard content behind the panel (identical to the plain Dashboard screen;
edit the layers even where the panel covers them):
- Stat card "active experts" → "active scouts". Keep all figures and deltas.
- Competitive Shift body → "Kestrel Sports Group's #NextWave campaign gained 23%
  share of voice, primarily through amplification of tracking data."
- Sentiment Driver body → "Negative sentiment spike (-12%) linked to
  release-clause discussions around Toma Vasquez"
- Emerging Theme body → "Load-management discussions up 340% following league
  guidance update on under-21 minutes"
- Table title "Brand Sentiment" → "Roster Sentiment"; column header
  "Top Expert" → "Top Scout"; group label "My Brands" → "My Players";
  "Competitor Brands" → "Rival Players".
- Row names, top to bottom: "Palbociclib" → "Toma Vasquez"; "Ribociclib" →
  "Elias Braun"; "Abemaciclib" → "Ruben Achterberg"; "Talazoparib" → "Dembe Osei";
  "Trastuzumab" → "Rafael Eikeland". Every figure and scout name stays.

Answer panel:
- Title "Which DOLs are most active on combination therapy?" → "Which scouts
  are most active on under-21 prospects?"
- Insights body (keep the heading and the Auto-generated badge) → "Sarah Chen
  leads under-21 prospect discussions with 47 posts this quarter, followed by
  Michael Ross (38 posts) and Lisa Park (31 posts). Focus areas: academy
  graduates and loan-spell performance."
- List heading "Experts" → "Scouts". The five rows, their sentiment chips, and
  post counts stay.
- The follow-up input, Send button, thumbs, "Based on 847 discussions • Nov 3 -
  Dec 3, 2025", download icon, close icon, and the floating pink AI button
  stay.
```

---

## navigator-07 — Dashboard with an answer open: two-player comparison

```
This screen is the Dashboard of a scout-intelligence platform used by a sports
representation agency, with an AI answer panel open over the sentiment table
comparing two players. Update the text so the screen reads as that product.
Change only what is listed below. Keep the layout, type styles, colors, icons,
figures, chips, bar lengths, and spacing exactly as they are. Text layers may
reflow to fit new strings; do not change type sizes to compensate.

Shell:
- Wordmark, top-left: replace "Navigator365™ Matrix" with "Expert Insights".
  Replace the pink molecule icon beside it with a simple geometric mark in the
  same pink — a filled circle with three short white horizontal bars of
  increasing length is fine. Nothing that reads as a molecule, atom, or network.
- Left nav: "Experts" → "Scouts"; "Conferences" → "Showcases";
  "Therapeutic Areas" → "Leagues". Keep Dashboard, Analysis, Social Explorer,
  Search, Logout, and every icon.
- Disclaimer under What's Moving (partly hidden behind the panel — edit it
  anyway): change "regulatory, clinical, or strategic advice" to "scouting,
  contractual, or strategic advice".

Dashboard content behind the panel (identical to the plain Dashboard screen;
edit the layers even where the panel covers them):
- Stat card "active experts" → "active scouts". Keep all figures and deltas.
- Competitive Shift body → "Kestrel Sports Group's #NextWave campaign gained 23%
  share of voice, primarily through amplification of tracking data."
- Sentiment Driver body → "Negative sentiment spike (-12%) linked to
  release-clause discussions around Toma Vasquez"
- Emerging Theme body → "Load-management discussions up 340% following league
  guidance update on under-21 minutes"
- Table title "Brand Sentiment" → "Roster Sentiment"; column header
  "Top Expert" → "Top Scout"; group label "My Brands" → "My Players";
  "Competitor Brands" → "Rival Players".
- Row names, top to bottom: "Palbociclib" → "Toma Vasquez"; "Ribociclib" →
  "Elias Braun"; "Abemaciclib" → "Ruben Achterberg"; "Talazoparib" → "Dembe Osei";
  "Trastuzumab" → "Rafael Eikeland". Every figure and scout name stays.

Answer panel:
- Title "Compare Opdivo vs Tecentriq this quarter" → "Compare Idris Falk vs
  Mateus Oyelaran this quarter"
- Insights body (keep the heading and the Auto-generated badge) → "Idris Falk
  leads on sentiment with a 58% positive rate vs Mateus Oyelaran's 35%.
  However, Mateus Oyelaran shows stronger momentum, with sentiment improving
  +8% vs Idris Falk's +2% this quarter."
- Legend: "Opdivo" → "Idris Falk"; "Tecentriq" → "Mateus Oyelaran". Keep the
  blue and orange dots and their colors.
- Bar label "Experts discussing" → "Scouts discussing". "Discussion volume",
  "Positive sentiment", and "Negative sentiment" stay. All four bars and the
  eight figures beneath them stay exactly as they are.
- The follow-up input, Send button, thumbs, "Based on 847 discussions • Nov 3 -
  Dec 3, 2025", download icon, close icon, and the floating pink AI button
  stay.
```
