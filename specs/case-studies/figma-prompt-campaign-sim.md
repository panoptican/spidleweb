# Figma edit prompts — Campaign Sim screens

One prompt per screen in `qa/precision-screens/`. Each is self-contained: select
the matching frame in Figma and paste the whole prompt. The shell edits (logo,
team name) and the left-panel edits repeat across prompts on purpose — the
screens may be edited in any order, and if those are shared components that
have already been changed, the agent simply finds nothing left to do there.

Export names after editing: `campaign-sim-01` → `campaign-sim-01`,
`-02` → `-02`, `-03` (Channel Insights, new) → `-03`, `-04` (Review Campaign)
→ `-04`. The site currently uses `-01` to `-03` with Review Campaign as `-03`;
`work/campaign-sim.html` will need its third figure repointed to `-04` and a
fourth figure added for Channel Insights.

Names carried over from the current screens, all invented: Sofia Clarino, Eric
Robertson, Martin Johnson, Frank Smith, Julie Abraham, Victor Gregorio. The
only new name is the team, Northline.

The sport is football (soccer) throughout, matching the Expert Insights
screens — but no real club, league, competition, or person is ever named.

---

## campaign-sim-01 — Select Channels

```
This screen is the Select Channels step of a campaign-planning simulation used
to train sports representation agencies. Teams plan how to reach talent scouts
across a set of outreach channels against a budget. Update the text so the
screen reads as that product. Change only what is listed below. Keep the
layout, type styles, colors, icons, figures, buttons, and spacing exactly as
they are. Text layers may reflow to fit new strings; do not change type sizes
to compensate.

Shell:
- Top-left logo: replace the pink starburst mark with a simple geometric mark
  in the same pink — a filled circle with a smaller white circle offset toward
  its upper right is fine. Nothing that reads as a starburst, asterisk, or
  flower.
- Top bar: "Team Skywalker" → "Team Northline". Keep "2nd place", "Round 2",
  "80%" / "Capacity used", and "¢ 235,340" / "Remaining budget".

Header:
- Title "Planning Tool – Select Channels" stays.
- Subtitle "Select the channels you'll use to reach Dr. Julie Abraham." →
  "Select the channels you'll use to reach Julie Abraham."

Left panel:
- "Dr. Sofia Clarino" → "Sofia Clarino"; "Key Opinion Leader" → "Talent Scout".
- Description → "Paid offline channel, sponsorship of scouts. Maximum of 25
  delegates per showcase."
- Segment Details: label "Patient potential" → "Prospect potential" and its
  value "SP 1" → "T1"; the "Accessible per year" value "2 per company" →
  "2 per club". "Group Size" / "40" stays.
- Heading "Customer Preferences" → "Scout Preferences". Its three rows stay.
- Plan Totals: "Expected MCQ" → "Expected Exposure". Every other label and
  value stays, as do the "By type" and "By content" bars.

Channel cards (keep every icon, icon color, duplicate button, and Add Content
button — including the bordered one on Advertisement):
- "International congress" → "International Showcase"; body → "Paid offline
  channel, sponsorship of scouts. Maximum of 25 delegates per showcase."
- "Local Scientific Meeting" → "Regional Trial Day"; body → "owned event such
  as face-to-face for a group of scouts"
- "Medical Scientific Liaison" → "Player Liaison Officer"; body →
  "club-facing role performing face-to-face interactions with scouts"
- "Rep visit" → "Scout Visit"; body → "face-to-face conversation with (or
  without) a printed profile sheet or tablet dossier that contains player
  information"
- "eMail Rep" → "Agent Email"; body → "eMail with pre-approved content sent by
  agents. Also called agent triggered eMail (ATE)"
- "Advertisement" stays; body "advertisement in offline media" stays.
- "Smartphone app" stays; body → "application for professional purposes
  delivered by a representation agency (club service)"
- "Teledetailing" → "Remote Film Session"; body → "conducting an interactive,
  online, real-time meeting with a talent scout. Also referred to as 'remote
  review' or 'web calls'"
- "eMSL" → "Remote Liaison"; body → "online player liaison officer"

The bottom bar ("Copy segment from…" and "Continue to next segment") stays.
```

---

## campaign-sim-02 — Select Content

```
This screen is the Select Content step of a campaign-planning simulation used
to train sports representation agencies. Teams plan how to reach talent scouts
across a set of outreach channels against a budget; this step sets the content
mix inside the Advertisement channel. Update the text so the screen reads as
that product. Change only what is listed below. Keep the layout, type styles,
colors, icons, figures, buttons, steppers, and spacing exactly as they are.
Text layers may reflow to fit new strings; do not change type sizes to
compensate.

Shell:
- Top-left logo: replace the pink starburst mark with a simple geometric mark
  in the same pink — a filled circle with a smaller white circle offset toward
  its upper right is fine. Nothing that reads as a starburst, asterisk, or
  flower.
- Top bar: "Team Skywalker" → "Team Northline". Keep "2nd place", "Round 2",
  "80%" / "Capacity used", and "¢ 235,340" / "Remaining budget".

Header:
- Title "Planning Tool – Select Content" stays.
- Subtitle "Select the advertisement content you'll use to reach Dr. Julie
  Abraham." → "Select the advertisement content you'll use to reach Julie
  Abraham."

Left panel:
- "Dr. Sofia Clarino" → "Sofia Clarino"; "Key Opinion Leader" → "Talent Scout".
- Description → "Paid offline channel, sponsorship of scouts. Maximum of 25
  delegates per showcase."
- Segment Details: label "Patient potential" → "Prospect potential" and its
  value "SP 1" → "T1"; the "Accessible per year" value "2 per company" →
  "2 per club". "Group Size" / "40" stays.
- Heading "Customer Preferences" → "Scout Preferences". Its three rows stay.
- Plan Totals: "Expected MCQ" → "Expected Exposure". Every other label and
  value stays, as do the "By type" and "By content" bars.

Advertisement card:
- Title "Advertisement", the subtitle "Choose a mix of content types and set
  the frequency of engagement to maximize effectiveness.", the pink megaphone
  button, the "Content" and "Frequency" headers, every "Clear" link, every
  stepper and its value, the "Total" / "18" row, and the Cancel and Apply
  buttons all stay.
- Content rows, top to bottom (keep each row's icon and icon color):
  - "Product news" → "Player news"; description → "Promotional information
    about your player"
  - "Disease Awareness" → "League Awareness"; description → "General league
    information, without linking to a player"
  - "Reimbursement" → "Contract Terms"; description → "Specific contract
    information on your player or position"
  - "Clinical Trials" → "Performance Data"; description → "Information about
    match results and statistics for your player"
  - "Treatment Guidelines" → "Development Guidelines"; description →
    "Information about guidelines issued by governing bodies"
  - "Event Information" stays; description "Information about logistics,
    agenda, services" stays.

The "Copy segment from…" button stays.
```

---

## campaign-sim-03 — Channel Insights

```
This screen is the Channel Insights reference view of a campaign-planning
simulation used to train sports representation agencies. It lists every
outreach channel with its expected exposure, reach, impact, and costs so teams
can compare channels before planning. Update the text so the screen reads as
that product. Change only what is listed below. Keep the layout, type styles,
colors, icons, figures, and spacing exactly as they are. Text layers may reflow
to fit new strings; do not change type sizes to compensate.

Shell:
- Top-left logo: replace the pink starburst mark with a simple geometric mark
  in the same pink — a filled circle with a smaller white circle offset toward
  its upper right is fine. Nothing that reads as a starburst, asterisk, or
  flower.
- Top bar: "Team Skywalker" → "Team Northline". Keep "2nd place", "Round 2",
  "80%" / "Capacity used", and "¢ 235,340" / "Remaining budget".

Header:
- Title "Channel Insights" stays.
- The placeholder subtitle (Latin text beginning "Ex laborum labore nulla ad
  reprehenderit…") → "Compare expected exposure, reach, impact, and cost for
  every channel before you commit budget."
- The Table / Chart toggle stays, Table selected.
- Legend: "Owned Medical" → "Owned Scouting". "Owned Promotional" and "Paid"
  stay, with their dots.

Video card, top-right:
- "Welcome to Omnitopia!" → "Welcome to Campaign Sim!"
- The "Part 1" chip, play button, scrubber, "0:00", and "8:24" stay.

Table:
- Column header "Exp. MCQ" → "Exp. Exposure"; keep its info icon. "Name",
  "Exp. Reach", "Impact", "Variable Cost", and "Fixed Cost" stay.
- Group headers "Deep engagement channels" and "Enablement channels" stay.
- Every figure in every row stays.
- Rows, top to bottom (keep each row's icon and icon color):
  - "International congress" → "International Showcase"; description → "Paid
    offline channel, sponsorship of scouts. Maximum of 25 delegates per
    showcase."
  - "Local Scientific Meeting" → "Regional Trial Day"; description → "owned
    event such as face-to-face for a group of scouts"
  - "Medical Scientific Liaison" → "Player Liaison Officer"; description →
    "club-facing role performing face-to-face interactions with scouts"
  - "Rep visit" → "Scout Visit"; description → "face-to-face conversation with
    (or without) a printed profile sheet or tablet dossier that contains player
    information"
  - "eMail Rep" → "Agent Email"; description → "eMail with pre-approved content
    sent by agents. Also called agent triggered eMail (ATE)"
  - "eMSL" → "Remote Liaison"; description → "online player liaison officer"
  - "Smartphone app" stays; description → "application for professional
    purposes delivered by a representation agency (club service)". This row is
    clipped by the bottom of the frame — edit it anyway.
- If further rows exist below the frame edge, apply the same renames:
  "Teledetailing" → "Remote Film Session" with description "conducting an
  interactive, online, real-time meeting with a talent scout. Also referred to
  as 'remote review' or 'web calls'"; "Advertisement" and its description stay.
```

---

## campaign-sim-04 — Review Campaign

```
This screen is the Review Campaign step of a campaign-planning simulation used
to train sports representation agencies. It lays out the whole plan — per-scout
investment and expected outcomes with deltas against the previous round —
before the team submits. Update the text so the screen reads as that product.
Change only what is listed below. Keep the layout, type styles, colors, icons,
figures, deltas, bars, and spacing exactly as they are. Text layers may reflow
to fit new strings; do not change type sizes to compensate.

Shell:
- Top-left logo: replace the pink starburst mark with a simple geometric mark
  in the same pink — a filled circle with a smaller white circle offset toward
  its upper right is fine. Nothing that reads as a starburst, asterisk, or
  flower.
- Top bar: "Team Skywalker" → "Team Northline". Keep "2nd place", "Round 2",
  "80%" / "Capacity used", and "¢ 235,340" / "Remaining budget".

Header:
- Title "Review Campaign" and the subtitle "Review your campaign plan, compare
  it with previous rounds, and verify your selected resources before
  submitting." stay.

Main table:
- Names, top to bottom, drop the "Dr." prefix: "Dr. Sofia Clarino" → "Sofia
  Clarino"; "Dr. Eric Robertson" → "Eric Robertson"; "Dr. Martin Johnson" →
  "Martin Johnson"; "Dr. Frank Smith" → "Frank Smith"; "Dr. Julie Abraham" →
  "Julie Abraham"; "Dr. Victor Gregorio" → "Victor Gregorio".
- The role line under every name, "Key Opinion Leader" → "Talent Scout".
- Column header "Expected MCQ" → "Expected Exposure". "Name", "Channels", and
  "Planned Investment" stay.
- Every figure, every green and red "vs Round 1" delta, every Edit link, the
  chevrons, and the Total row stay.

Right rail:
- The Resources card and all its values stay.
- By Type legend: "Owned Medical" → "Owned Scouting". "Owned Promotional" and
  "Paid" stay. The bar stays.
- By Content legend, top to bottom: "Product news" → "Player news";
  "Disease Awareness" → "League Awareness"; "Reimbursement" → "Contract Terms";
  "Clinical Trials" → "Performance Data". If "Treatment Guidelines" and "Event
  Information" rows exist below the frame edge, "Treatment Guidelines" →
  "Development Guidelines" and "Event Information" stays. Percentages, dots,
  and the bar stay.

The bottom bar ("Edit Plan" and "Submit Plan") stays.
```
