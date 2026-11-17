# Coverage checklist (built 2026-11-14 from fan guides + automated scans)

Kept spoiler-free on purpose: feature types only, no story details. Sources: lemono.jp (area/event data), gorillawiki and h1g.jp wiki
(search summaries; both returned 403 to direct fetch), retro-game-fan hatenablog chart, GameFAQs Portable Q&A.

## Automated completeness (work/coverage.py, build_patch.py output)
- Story messages: 2288 / 2288 translated, 0 encoding problems.
- UI text blocks in all game files: 459 covered; the 3 "missing" are placeholders (`？？？`, PLAYTIME 00:00:00, a bracket).
- Image files not redrawn (checked by contact sheets): model textures (no text); map pictures MAP01-10 and ITIRAN_BG (no text);
  tilted book-opening frames (Z_A01-05, Z_N01-05, MOP*/TOP* frames 2-6) still show the Japanese cover on the first frame (known gap).
- Movies (25 .pmf, ffmpeg can read them): the opening (m27) and ending (m28) have burned-in staff credits and title card in Japanese;
  omake.pmf is the Sneak Peek trailer. Not changed (credits/logo left as in README).

## Game features listed by the guides vs patch status
| Feature | Status |
|---|---|
| Bug net catch screen (name, Caught m/d, mm) | seen in game, English; its Keep / Let go prompt was vertical -> fixed in v29 (untested) |
| Bug cage / Jumbo Box / specimen page / Species List | seen in game (empty states, prompts, panel); filled specimen page and Jumbo header not seen |
| Fishing: tackle desk page | seen in game |
| Fishing: rod, cast, HIT mark | seen in game (user), English |
| Fishing: fish names after a catch | not seen |
| Kite flying (HUD, pause menu, kite list) | seen in game; crash message not seen |
| Bug sumo (cage screen, notebook cover) | seen in game; matches/moves/W-L not seen (need beetles) |
| Hornet-nest poking, pressed-flower gathering, photo/camera events, fireworks, dinner quiz | story/prompt text only; no separate interface files found; not individually checked on screen |
| Desk menu, items list, radio exercise card, settings, controls help, save/load, Favorites | seen in game |
| Summer Memories menu + previews | seen in game; viewers need a finished-game save |
| 5 endings (oti00-04) | redrawn captions; not seen in game |
| Ad-hoc bug exchange mode | English message seen (no Favorites file) |
| Sneak Peek | trailer/notice left as is |
