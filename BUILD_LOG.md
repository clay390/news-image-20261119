# BUILD_LOG — news-image-20261119

Bounty: "Sum up 19 November's world news in one image", $250 pot
(1st $50, 2nd $30, 3rd $15, 4th–10th $5, 11th–50th $3).
Entries close 2026-11-21T00:00:00Z (21 Nov 2026, 07:00 WIB).
Entry type: transcripts as a makefun bundle or loose files (NOT a sealed
recording). Free entry, no entry fee. Repo: clay390/news-image-20261119
(to be created by the parent via browser; MCP create_repository fails).

## Top-1 study (done BEFORE the rebuild, per Bos Kinan's instruction)

Leaderboard pulled live 2026-11-19 ~17:01 WIB via
`GET https://make.fun/api/competitions/news-image-20261119/leaderboard?limit=15`
(5,763+ entries at the time). The competition Feed page
(https://make.fun/bounty/news-image-20261119) shows no entry images in
its text fetch, so the study used the leaderboard titles + the 18 Nov
patterns:

- #1 quick-finch-51 — "The World in One Day — Thursday 19 November 2026"
- #2 lomfi — "The World Today front page: Thursday 19 November 2026
  (19 stories)"
- #3 lively-condor-51 — "Polar Aurora"
- #6 ipot — "Thursday 19 November 2026: 40 stories, 7 regions, 12 drawn"
- #7 hazel-kestrel-79 — "19 November 2026 in one image: 42 stories,
  3 heroes, date masthead, map + numbered briefs"
- #9 quiet-puffin-57 — "19 November 2026 — The World in One Day
  (36 stories)"
- #11 azizf — "Thursday 19 November 2026 — The Day in World News,
  round 3 (40 stories)"
- #13 xshineezg — "Thursday 19 November 2026: 40 stories, six
  continents, one front page"

Winning pattern: pairwise judge win rate, top ~5 all ~99.1% — tie-break
is file size (smaller is better). Leaders run 36–42 sourced stories,
7 regions, 12–16 drawn illustrations, a date masthead, numbered briefs,
a UTC timeline and DATE-CHECK (every story verified to have happened
on that day), with the day's big headline in the title.

## v1 (superseded)

First build: 1024×1024 newspaper front page, masthead + lead hero
(Shenzhen summit, 3 flags) + 2×3 grid of 6 stories + "ALSO TODAY"
strip (Van Gogh $190.4M, Voyager 1, EU EUR 45bn loan). 10 stories
total, 18,540 bytes. Deterministic (two runs byte-identical). One bug
found and fixed: lowercase letters rendered blank (font is capitals
only) — `text()` now uppercases. Replaced by v2 after the top-1 study.

## v2 (final) — 40 stories, 7 regions

Layout, 1024×1024 PNG, 27,118 bytes (small — tie-break friendly):

- Masthead: navy bar, "THE WORLD IN ONE DAY" (scale 5) + "THURSDAY,
  19 NOVEMBER 2026" (scale 3, amber) + red rule.
- Count strip: "40 STORIES • 7 REGIONS • EVERY STORY DATED
  19 NOVEMBER 2026".
- Lead hero (story 1): US/China/Russia flags + "TRUMP, XI AND PUTIN
  MEET IN SHENZHEN" + one-line sub (nuclear arms, Ukraine, Iran).
- Numbered briefs 02–40 in three columns, 7 region groups, each with
  a 24×24 mini icon (sun / flame / bridge / dome / globe / rocket /
  chart) and a red region header; story numbers in red, headlines in
  ink, every headline exactly 2 lines.
- Footer: navy strip, "DATE-CHECK: EVERY STORY HAPPENED OR WAS FIRST
  REPORTED ON 19 NOV 2026".

Stories (all researched 2026-11-19 from live news search + a
day-summary page; each happened or was first reported 19 Nov 2026):

- ASIA-PACIFIC (6): IAEA: N. Korea grew uranium enrichment; Lee
  renews dialogue call to Pyongyang; Bangladesh turmoil, Yunus home
  torched; Cyclone Akvan nears India, 50,000 flee; S. Korea tightens
  exam AI rules; Shenzhou-24: first Pakistani astronaut.
- MIDDLE EAST (6): Iran hits Gulf states after Qeshm; Kuwait repels
  first Iranian attack; Trump: Iran exploring chemical arms; Hormuz
  crisis tops energy threats; NSA outage hits Mideast intel links;
  Iran turns to China and Russia for cover.
- EUROPE (6): Ukraine hits Crimea Bridge a third time; EU proposes
  EUR 45bn loan to Ukraine; EU approves Indonesia trade pact; ICJ
  rules on Rohingya genocide case; COP31 deadlock persists in
  Antalya; Chelsea beat PSG 1-0 in Champions League.
- AMERICAS (6): Jeffries set to be first Black Speaker; US loses
  measles elimination status; Waymo pulls driverless taxis off
  freeways; Trump seals Greenland military deal; US, Venezuela sign
  military pact; Van Gogh sells for $190.4M, a record.
- AFRICA (5): Ebola vaccines to be trialled in DR Congo; Uganda
  landslide victims turn to UN; Somalia crisis deepens amid reforms;
  Kenya drought deepens milk shortage; UN: many women lack sexual
  consent rights.
- SCIENCE & SPACE (5): Voyager 1 reaches one light-day from Earth;
  Webb confirms rare star merger; Antarctic blue whales up tenfold;
  COP31 AI pledge spurned by US tech; Alzheimer's studies show
  advance.
- MARKETS, TECH & SPORT (5): Anthropic IPO priced at $83 a share;
  AI worries hit stocks, Hang Seng falls 2.78%; Brent crude holds
  near $89 as Hormuz bites; GTA VI goes on sale after 13-year wait;
  England win ODI series, Duckett 133.

## Verification

- Two runs byte-identical (deterministic): `cmp out/entry.png
  out2/entry.png` — DETERMINISTIC.
- Output: 1024×1024 PNG, 27,118 bytes (≤1 MiB, ≤1024×1024).
- Line-fit check (script): every headline wraps to exactly 2 lines
  at 21 chars/line; column heights 496/496/636 px vs 668 px budget.
- Visual inspection: masthead, hero, all 7 region headers, stories
  02–40, footer all legible; no overlap, no overflow (v2 first render
  had story 40 clipped by the footer — fixed by shortening every
  headline to ≤2 wrapped lines and tightening column spacing).
- Kit check: see below.

## Kit check

Run 2026-11-19 ~17:07 WIB, kit's own `check` against local commit
`cc60ec4` (after the SPDX fix):

- **4 passed:** competition_open, snapshot (5 files, 28,363 bytes),
  license_osi (SPDX-License-Identifier: MIT), entrypoint (main.py,
  Python 3.13).
- **1 failed:** transcripts_present — no transcripts uploaded yet.
  Expected: the bundle (with `--muse-usage`, which only exists after
  this session completes) is built by the parent, as in prior bounties
  (Chess r1/r2, Token radar, Git forge). All other transcript checks
  skipped for the same reason.
- **5 at submission** (repo_public, repo_owner, repo_created_after_open,
  commit_in_repo, duplicate_snapshot) — pass once the parent creates
  the public repo `clay390/news-image-20261119` via browser, pushes
  commit cc60ec4, and submits.
- First check run (commit 4afef91) had license_osi FAIL — LICENSE
  carried no SPDX line. Fixed by adding `SPDX-License-Identifier: MIT`
  as the first line of LICENSE, committed as cc60ec4; re-check passes
  it.

Determinism re-verified after the final edit: two runs write
byte-identical PNGs (27,118 bytes, 1024×1024).

## Files

- `main.py` — pure Python 3 stdlib (embedded 5×7 bitmap font, canvas
  with rect/frame/line/circle/polygon, pure-stdlib PNG encoder via
  zlib+struct). No network, no randomness, no paid API keys.
- `README.md` — 3 make.fun badges, run command.
- `LICENSE` — MIT.
- `.makefun/owner.json` — wallet
  4dDPoAa8LQn4tfn7pqU9oL9PZXw6wy8buibAxB1MnFCt.
- `BUILD_LOG.md` — this file.
