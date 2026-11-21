# Dev notes

Reverse-engineering and testing notes, oldest first inside each batch. Rough, written while working.
For where the translation stands, see [STATUS.md](STATUS.md).

Addresses are PSP memory addresses in the game's main module (loaded at 0x08804000). `harness/` holds the scripts mentioned here.
`private/` is a local folder with your own game files and saves. It is git-ignored. Never commit or share anything from it.

Quick map of the big findings:
- The game still has its developer **debug menu**. `harness/dbgmenu.py <iso> [entry]` starts it, or jumps straight into any mode (ending, kite, memories, ...).
- `harness/setscene.py` starts any map scene by name, so you can reach places without playing.
- The vertical text menus are one widget with 14 layouts. All of them are patched to horizontal rows. `harness/forcer.py` draws each one, `harness/fitcheck.py` measures them.
- The audit build (`BNN_AUDIT=1`) plus `harness/audit.py` finds vertical or off-screen text.

## Session note 11/14/26 (later): scene warp + fixes

- **Scene warp works.** Boot into the debug menu (`harness/dbgmenu.py`), page 0 item 0 = `mode_map` (CIRCLE). It shows an invisible map-select UI.
  `harness/setscene.py H20000` then writes the scene name into that UI (letter, area, time 0-2, variant are 4 ints on the UI thread's stack,
  found by a breakpoint at 0x8835034); press CIRCLE to start. Scene names: tools list them via `ls S/bnn-gzc/<container>`; areas G*=house, H*=outdoors,
  A*=opening chapters. Starting some scenes lets their scripts move you on (H14000 -> H13000, H20000 -> H27000).
  Then set flags 3/0x0A/0xEA (cheat.setflag) and pick tackle at the desk (square, right, circle, circle, cross, circle) as before.
- **Fishing is still unverified.** H27000 is a riverbank (a bridge scene follows); the fishing spot/trigger was not found. CFishing's vtable is 0x890ff78 (object code
  around 0x8878b94..0x887ac78); the entry point that creates it was not found. Do not fake-call the constructor blindly.
- **Fixed in v26-v28** (tools/eboot_patch.py `kite_menu` + KITE_CODE, tools/imgbuild.py `sumo0`, `memthumbs`):
  kite pause menu (box table 0x8919e34 row 1, position table 0x8919bdc row 1, string in the appended blob, call at 0x08848e3c, glyph advance cave `kite_h`
  at the end of the widget's glyph loop 0x08827808; selection also accepts D-pad up/down); sumo cage backdrop notebook ("Bug / Swap / Notebook"); four Summer Memories preview pictures.
- Other users of the vertical widget 0x08827720 (position rows 0,2-11, box rows 0-7): only the kite pause menu (row 1) was changed. Rows used by other prompts
  (e.g. the call at 0x0884f11c, 0x0886e50c, 0x0881faa0, 0x08820bc0) were not looked at; check them if a vertical Japanese-style menu shows up.
- `mode_adhoc` shows "No Favorites file was found." (English). The Summer Memories Diary viewer stays black with no save loaded.
- Still open: fishing play screens, sumo matches (need caught beetles), fortunes, filled specimen page, Jumbo header, kite "Crash!" placement, viewers needing a finished save,
  real-PSP test, optional polish list at the top.

## Session note 11/16/26 (Summer Memories viewers verified with the finished save)

- **Reliable route to the viewers:** `dbgmenu.py <iso> 891e854` (mode_load_memory) -> wait ~9 s -> circle (slot) -> left (Yes) -> circle -> wait ~16 s -> menu with real data. No title screen, so the attract demo cannot interfere.
- Menu cursor resets to the top after leaving a viewer; `cross` moves it to Back. From the specimen page: circle on Back -> boxes -> `cross` -> menu (then `left` puts the cursor back on the list).
- **Items viewer:** all 8 items (Radio Exercise Card ... Photo) English; descriptions fit; item art left as is. **Ending viewer:** plays the ending sequences; no text issues seen. **Picture Diary:** fine.
  **Kites entry:** circle did nothing (probably locked in this save). **Favorites:** not opened (needs a Favorites file; "No Favorites file" message already seen in English).
- Open still: fish names / Jumbo header (this save has no fish), sumo matches, real script choice menus, Species List side panel hover, tilted book frames, movie credits.

## Session note 11/16/26 (finished-game save, specimen names, v36)

- **Finished-game save obtained** (user downloaded it from GameFAQs save #13574, 246 KB zip, folder UCJS10038S001N, DATA.BIN 8,564 bytes, PARAM.SFO title "1)ボクの思い出 8月31日", playtime 06:51:13).
  Copy kept at `private/save_complete/` (never distribute). Install: copy the folder over `S/home/.config/ppsspp/PSP/SAVEDATA/UCJS10038S001N` (the test save is backed up at `S/save_testbackup` and in `private/save/`).
- **Route to the Summer Memories viewers:** title (3 STARTs show the menu; do NOT press a 4th START, it picks New Game) -> down (Summer Memories) -> circle -> wait ~10 s -> "Load which file?" ->
  circle -> "Is this file okay?" -> left (Yes) -> circle -> wait ~16 s -> menu with real data. Scripts: `harness/to_specimens.py <iso>` (ends on the specimen page), `harness/memviewers.py` (lost sync after Kites, needs more waits).
- **Picture Diary viewer** works with real data (English pages, Patrick Hand). **Specimens + Bug Cage** shows the boxes; with the cursor on Jumbo Box, `down` opens the specimen page. This save holds one specimen (No. 1, Miyama Stag Beetle).
- **Found and fixed on the filled specimen page (v35/v36):** (1) the bug name was a vertical column at x 160 (label call 0x088659c0, x pitch 0 / y pitch 16) -> horizontal line under "NO. n" (x 22, y+17, cave `spec_name`);
  (2) names were cut to 11 characters because the page object's copy routine 0x08869c1c copies only 12 glyphs into a 17-glyph slot -> replaced by cave `spec_copy` that copies up to 47 glyphs into a private 128-byte buffer
  in the appended blob (calls 0x08869c8c through jalr; needs 'jalr' in tools/mips.py). Verified: "Miyama Stag Beetle ♀" on one line, stray "2" gone. Longest species name is 169 px, the page text area about 173 px.
- Species List grid shows the collected bugs; hovering a collected species to check the side panel was not completed (cursor moves in cell units).
- Not yet seen: Kites/Items/Ending/Favorites viewers (sequence desync), sumo matches, fish names, real script choice menus.

## Session note 11/16/26: fortune window fixed (v34), verified by the user in the live game

- The fortune-telling Jizo shrine is scene A11000: step up to the offering plate (net away), face the statues, press X. fortunewatch2.py (breakpoint 0x08827a38) captured the first run.
- v32 problem: the window box was in the middle but the word ("Luckier!") was drawn at the bottom-left, because the dialogue-subtitle patch (cave at 0x0881bf14, window +0x7c == 0) pins every window's text to x16,y200.
  Fix in tools/eboot_patch.py `kite_menu`: the mode-2 branch of the text-window setter (j at 0x0881bc34 -> cave `fort7c`) sets window +0x7c = 1 so the window keeps its own position;
  box 180,78 size 120x50 (calls at 0x08827b24..3c); text x 216 y 79 (0x08827b14/1c). User confirmed v34 is centered. All four result words are 3 cells (48 px) wide.
- Note for scripts: macOS has no `setsid`; start background watchers with `(nohup python3 x.py ... &)`. Under zsh an unmatched `rm -f glob` aborts the line (use `setopt nonomatch`).

## Session note 11/15/26 (community saves: none found)

- Searched for a complete/late-game save (user approved using community saves). save-editor.com board threads for this game exist (savedata num=2121, PPSSPP state num=2122) but contain only the admin
  placeholder posts, no uploads. uu.getuploader.com/psp_savedata is blocked (403/Cloudflare 1005) for scripted access; the ameblo "700+ saves" blog is a generic 2009 promo with no verifiable file. Nothing downloaded.
- Ideas left for the Summer Memories viewers: find what the "finished game" check reads (message index 4 of saveload_normal t3, shown for mode byte +0xA1 == 2 in the save/load mode object, common loader 0x08845104)
  and set that state before saving from mode_oti, or decrypt/edit DATA.BIN (needs the savedata key from the sceUtilitySavedata param).

## Session note 11/15/26 (Jizo / fortune, real catch prompt)

- **Real catch prompt verified in v32:** a net swing at the shrine scene (A11000) opened the real catch screen; "Keep / Let go" showed as two horizontal rows in the small lower-right box.
- **Fortune = the fortune-telling Jizo shrine** (script lines mention it in A11000 and H09000). Warp with `harness/setscene.py A11000`; the shrine (three statues, offering plate) is the first view.
  Net must be put away first (`rtrigger` in scripts, W on the keyboard), Boku faces the statues. Blind walking from the harness did not trigger the prayer (maybe needs a certain day/item, or exact position);
  `harness/fortunewatch2.py <secs>` arms a breakpoint on the fortune routine 0x08827a38 and saves 20 screenshots (fwx_NN.png) when it fires. Try by hand with the watcher running.
- The fortune window text goes through the message-window label path, where the "always horizontal" patch (0x0881bf6c) applies, so it is probably already horizontal; unverified.

## Session note 11/15/26 (kite crash fixed, v32)

- **Kite "Crash!"**: drawn by the kite status thread at 0x8849514 when the kite state struct (`*(thread obj+0xA4)`, found with a breakpoint at 0x8849564 -> s0) has byte +4 == 2 and halfword +0x4E in 0x5D..0xFD.
  Writing those two values (repeatedly) in kite mode shows it. It was three 16-px word slices stacked vertically in a tall box; v32 patches the label call at 0x8849690 (x pitch 16, y pitch 0),
  box 200,66-280,114, text x 216 y 82. Verified on screen.
- Diary viewer (mode_nikki 891e76c) is black with no loaded data; mode_omake (891e988) is the Sneak Peek trailer with a burned-in Japanese title card and voice credit (left as is, as in the README).
- **Fortune results** ("Unlucky!/Lucky!/Luckier!/Jackpot!", words at 0x8919e74..0x8919e8c): drawn by the text-window object update at 0x08827a38 (created from script op handler via 0x08822b68;
  text set with 0x881bb68(a2=2), window rect via 0x881bac8/bd34/bd74 with x=227,y=55, 187,29 etc.). Likely the same vertical-slice problem as the crash box; NOT yet triggered or fixed.

## Session note 11/15/26 (jump to any mode)

- `harness/dbgmenu.py <iso> <entry-hex>` now takes the mode entry to start (default 0x891e1bc = debug menu). Entries are (func,name) pairs; full list from the dump:
  mode_map 891e574, mode_movie 891e75c, mode_newgame 891e764, mode_nikki 891e76c (picture diary), **mode_oti 891e7c4 (ending)**, mode_save 891e844, mode_load 891e84c,
  mode_load_memory 891e854, mode_load/delete/start/save_favorite 891e85c-874, mode_delete_file 891e87c, mode_check_file 891e884, mode_adhoc 891e8b4, mode_kite 891e8dc, mode_sumo 891e934,
  mode_loupe 891e93c, mode_demo* 891e958-978, mode_msg 891e980, mode_omake 891e988, title 891e9e0, config 891e9ec, mode_memory 891ea30, sub 891ea5c, item 891ea64, kite_select 891ea6c,
  fishing_tackle 891ea74, diary 891ea7c, kite_book 891ea84, insect_book 891ea8c, specimen 891eaa8, insect_list 891eab0, insect_cage 891eb00, jumbo 891eb74.
- **mode_oti (endings) runs end to end** and ends with the English end-of-game flow, all checked in v31: "Record everything up to today on the Memory Stick? Yes/No", the save-slot list
  ("Save to which file?", "Okay to overwrite?", "Save complete.") and "Continue playing?". All horizontal English. Caution: saving there overwrites the sandbox save (restore from private/save).
- The record saved from mode_oti is NOT accepted as a finished game ("No file from a finished game was found."), so the Summer Memories viewers stay locked; mode_load_memory
  shows the same message. A real finished-game file needs the real ending flags (not found).
- title_viewers.py: the title route to Summer Memories is flaky because of the attract demo; the attempt landed in the intro movie.

## Session note 11/15/26 (fit check): prompts measured against their boxes

- `harness/fitcheck.py` (needs the audit build, kite mode via goto_kite): forces the widest REAL strings through every widget layout with a matching item count (choices from tr/*.txt with the
  outline font map, cage.bms prompts and kite menu with the plain map), reads the audit log for where glyphs were drawn, and compares with the box rectangle read from the game tables
  (px = tbl*1.5+4 / *1.1333 / *1.3333). Result in v31: every layout passes except long choice text in layouts 0 and 10 (the two small custom boxes); an original-capacity check
  (JP chars per column vs the original box) shows no real choice can use those layouts and overflow, so they are left small. Cage#0 Keep/Let go, cage#1 full prompt, cage#3 Let it go?,
  kite pause all fit.
- Choices can have 2, 3, 4 or 5 options (two 4/5-option flavor lists exist); the script operand (opcodes 33 and 70) picks the layout, so all types must stay generic and horizontal.
- audit.py now also flags glyphs drawn off-screen. save/load/ad-hoc screens: none. Desk/kit tour: one hidden grid below the bottom edge on the bug-box screen (ra 0x881b264, y 270-375),
  not visible and not translation related.
- Not yet seen live: real script choice, real catch prompt (see above), sumo matches, fortunes, kite crash, fish catch/Jumbo header.

## Session note 11/15/26 (later): vertical-text audit build

- **Audit build:** `BNN_AUDIT=1 python3 tools/build_patch.py S x S/audit.iso` hooks all 11 `jal 0x088388c4` (glyph blit) call sites to a logger (cave `audit_log`) that
  stores (caller ra, x=a1, y=a2) of every glyph blit in a 2048-entry ring buffer at module offset printed by the build (0x12f2e0 in v31, abs 0x08933 2e0 = 0x8804000+0x12f2e0).
  `harness/audit.py <secs> <tag>` polls it and flags vertical runs (same caller, x fixed, y stepping 10-40 px, 3+ glyphs), taking a screenshot for each new signature.
  Positive control: undoing the horizontal switch in memory (`write 0x0a209dfa at 0x8827808`) is flagged immediately. The normal build is unaffected (hash re-verified).
- **Results with the audit running (v31, zero vertical runs in all):** all 14 widget layouts via harness/forcer.py (20,836 glyph blits); save screen (141k), load screen (51k), ad-hoc mode (47k);
  desk, items, bug kit, cage/boxes and specimen page on the day-2 save (33k). Modes that logged 0 blits (sumo, Summer Memories, file check/delete, inet) draw text from pre-made images (checked visually).
- **Still not exercised with the audit:** real script choice menus and the real "Keep / Let go" catch prompt (could not get a bug into the net on demand; forced layouts verified),
  sumo matches, fortunes, kite crash, fish catch/Jumbo header, cage-full notice and specimen "Let it go?" (verified earlier in v25 by memory edits, label-routine paths unchanged).
  `harness/modes_audit.py <audit.iso>` runs the debug-menu mode tour; `titletest`/`kuchiki` entries failed to attach.

## Session note 11/15/26: all vertical pop-up menus fixed (v31)

- **Menu widget audit:** every prompt drawn by the vertical menu widget (ctor 0x088272c0, glyph loop 0x08827768) has 14 layouts ("types", 8 box rows; tables 0x8919bdc positions,
  0x8919e34 boxes, 0x8919e0c first-type-per-row, 0x8919e14 item counts). The script's choice menus (54 of them, opcode handlers 33 and 70 in the table at 0x8919768; one handler
  path 0x08825664 -> 0x08820a90 always uses row 7 / type 12 = three options) and the bug-catch "Keep / Let go" prompt (row 5 / type 10) were vertical in English and overflowed.
- **Fix (tools/eboot_patch.py `kite_menu`):** all 14 layouts are generated as horizontal rows (generic box 300 px wide, 38 px row pitch, hand cursor above the text), the glyph-advance cave
  `kite_h` switches to x-advance for the whole position table, the kite pause menu moved to layout 0 (patched `li a2,1` at 0x08848e38), Keep/Let go has a small box at the lower right.
- **Forcer (harness/forcer.py):** in kite mode it hijacks the widget ctor on each triangle press and draws every (row, type) with English text; harness/forcer2.py does the two choice layouts
  with real choice strings. All 14 layouts were checked on screen in v31. NOT yet seen: a real in-game script choice menu and a real "Keep / Let go" catch (forced layouts only).
- Cursor limit for 2-option choices (third row is empty) is unchecked.
- `mode_msg` in the debug menu needs voice_test files that are not on the disc (black screen); not usable.

## Session note 11/14/26 (fishing reached)

- **Fishing area found:** CFishing (object size 0x2B40, created for every map at 0x881df9c, stored at mapobj+0x50) is active when the map name is in the table at 0x890fcf8
  ("H24", "A01", "B15", "D03"). `harness/setscene.py H24000` starts the waterfall pool scene (the scripts may move you to H23000/H22000 afterwards; at the first view
  the fishing object reports pond table 0x890fbf8 at +0x7270, so it is live). Per-frame update 0x887a0b4(obj, dt); the three flag bytes at obj+0x9D11..13 only drive splash effects.
- **Procedure:** debug menu -> mode_map -> setscene H24000 -> circle; flags 3/0x0A/0xEA (cheat.setflag); desk: square, right, circle, circle (Bait), cross, circle, cross;
  walk to the water, press R twice (Boku switches from the net to the rod), CIRCLE casts (rod swing animation plays, line points up-left toward the waterfall).
- **Not seen yet:** a bite and the fishing HUD/fish names. About 4 minutes of casting (hour 5 and 6, day 5 flags) gave no bite and no visible lure. Ideas: read the fish
  objects at obj+0x10 + k*0xE30 and the lure position, try other fishing areas (A01, B15, D03 scenes), wait for morning/evening hours, or force the hit state.
- The kite `Crash!`, fortunes etc. remain unseen.

- Fishing follow-up: the fish object (obj+0x10, stride 0xE30, count at obj+0xC = 1) is live: model, position floats at +0x50 (x,y,z, w) moving by hundreds of units every 3 s (pond coordinates,
  not screen). The lure/hit logic was not located. The fishing play screen has no translated-image job (imgbuild `fishing` is only the desk tackle page); fish names show up
  in the Jumbo Box / specimen lists (ui.txt 62-64: Char, Rainbow Trout, Yamame Trout), so a real catch or a fake Jumbo record is needed to see them.

## Session note 11/14/26 (last): more checks, roadblocks

- Title menu is 2 rows (New Game / Continue; Summer Memories / Settings / Sneak Peek): `down` from New Game reaches Summer Memories. Opening it shows English
  "Checking the Memory Stick..." and, with only a day-2 save, "No file from a finished game was found." (both verified). The viewers need a finished-game file;
  DATA.BIN is encrypted so the test save cannot be edited. Viewer pages reuse assets already verified (diary pages, specimen page, kite book, ending captions).
- The title idles into an attract demo after about 8 s, so every title script must press quickly (t_bed.py/t_go.py cursor detection is flaky: rerun if "no Continue").
  t_bed.py gave a false "ok" this session (landed in the attract demo); the v28 desk, dialogue and load flows were checked by hand instead.
- `harness/wlog.py` logs every call to the vertical widget ctor (0x088272c0) while you press keys; plain walking in the kitchen/yard never calls it.
- Fishing trigger: no script text identifies it (no "bite/caught" messages in script_v3.json), so it is an engine action spot. Next idea: find the caller of the
  CFishing creation (vtable 0x890ff78; code 0x8878b94..0x887ac78) with a breakpoint on its vtable store, then walk to a river bank until it fires.

## Session note 11/14/26: DEBUG MENU WARP FOUND (use this instead of walking)

The retail executable still contains the developer debug menu (mode table at 0x891e1bc, entries are (func, name) pairs, 8 bytes each).
Its font file is not on the disc, so it draws NOTHING (screen stays black) but it takes input.

How to get in: `harness/dbgmenu.py <iso>` (run from the scratch dir; needs `tools/` copied there and `T=` set in tools/session.py).
It boots, presses START until the game queues `mode_start_favor` (0x891e86c) via setter 0x882cc6c, and swaps a0 for the debug menu 0x891e1bc.
Mode manager object = *(0x8924744) (0x89217bc): +0x50 next entry, +0x54 current entry; a queued mode only starts when the current one ends.
Game chain: title -> mode_start_favor -> mode_newgame -> mode_movie -> mode_map (0x891e574 = gameplay).

Blind navigation (cursor starts page 0, item 0; last cursor kept at 0x8925390 page / 0x8925394 item): D-pad down moves, RIGHT = next page, CIRCLE = run.
- page 0: mode_map, game_init, mode_newgame, new_model, musi_model, sumo_model, musi_s_model, bumper, fish_model, char_model, mode_msg
- page 1: kuchiki_test, title_test, insect_man_test, person_test, movie_test, mode_save, mode_load, Tim2Viewer, **mode_kite (8)**, **mode_sumo (9)**, **mode_memory (10)**
- page 2: bgm, voice_debug, se_test, mode_adhoc, debug_waku, mode_demo_play/rec/save/load, mode_delete_file, mode_check_file, inet_image_view
Verify with the mode manager's +0x54. Recipe: right, down x8, circle = kite (works with no save, no story progress).

Also: PPSSPP's own log (--log) records every `sceIoOpen(disc0:/sce_lbn0x..._size0x...)`; `tools/lbnmap.py <iso> <log>` maps them to DFI files.
Area containers are gz/G0a.. (house) and gz/H0a.. (outdoors), loaded on door transitions (see memory note for the dead-end loader hooks).

### Findings from the debug menu (not yet fixed)
1. **Kite pause menu (triangle in kite mode) is untranslated and vertical**: strings at 0x891e8e4 ("凧上げをやめる"/"凧を取り替える", only 16 words, no room),
   pointer to it stored at 0x8921960; drawn by the generic vertical text widget 0x8827768 (per column: position table at 0x8919bdc stride 8,
   glyph call 0x881AFD8, y += 0x10). Background box is a dark rectangle (about x184..290, y45..185). Needs: horizontal drawing + English strings in a cave + box resize.
2. **Bug cage / sumo selection screen**: the left notebook cover is untranslated crayon "虫 こうかん ノート" (image in sumo data). Bubble "Bug Cage" and "Back" are English.
3. **Summer Memories** menu itself is English, but its preview thumbnail (a diary page) shows Japanese text. The Diary viewer showed only black with no save loaded (needs a loaded save / ending flags; try mode_load first).
4. Kite HUD (Dir./Wind/Alt.) verified in English. Wind unit reads "m/h" in the original number art; check whether that is the original "m/s".
5. Sumo needs caught beetles (empty cage); fishing has no direct mode here (try mode_map via menu, scene name field `A01000` in the map-select param struct +0xC).
