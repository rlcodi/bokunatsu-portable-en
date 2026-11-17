Boku no Natsuyasumi Portable (PSP, UCJS10038) - English patch, WORK IN PROGRESS
Build: 2026-11-16 (test_v36)

Apply to an untouched Japanese ISO:
  size   397,508,608 bytes
  SHA-1  c7c9549fe565ee2702512a93a97353be208dd2cd

  xdelta3 -d -s "original.iso" bnn-portable-en-wip.xdelta "patched.iso"

Patched ISO SHA-1: 182b896a47ca1316af93cdb66a1de325f5c57b17

What is translated
- All scene dialogue, narration, hints and choice text (2,288 unique messages), shown as centred subtitles.
- Menu text: item names and notes, insect names and specimen entries, kite names, fishing notes, bug sumo and
  bug cage prompts, save/load and Favorites messages, Summer Memories menus, settings options, controls help.
- Picture text: title menu and subtitle, settings screen, desk-menu and other speech bubbles, plaques and buttons,
  fishing labels, sumo result cards and winning-move names, the specimen page, radio exercise card, the 8 kite book pages, the 17 insect field guide pages
  (day and night), both book covers, all 98 picture diary pages, the kite-flying gauges and the ending caption.
- Text stored in the executable: the "Caught m/d" line and "No specimens yet" in the bug cage, win/loss marks,
  fortune results (the shrine fortune window, seen on screen; the bug name on a filled specimen page, now a full horizontal line, seen on screen), the kite crash message (now a horizontal "Crash!" box, seen on screen) and fish names. Specimen page notes and the bedtime
  "Write your diary and go to bed?" prompt are now drawn horizontally (answers read No / Yes, matching the
  left/right keys). The specimen "Let it go?" prompt, the Species List side panel (name and note) and the
  bug cage's "cage and Jumbo Box are both full" notice are drawn horizontally too. The picture-diary notebook
  cover label is translated. Every pop-up menu built by the game's vertical menu widget (the kite pause menu, the bug-catch "Keep / Let go"
  prompt, and the story's choice menus) is now laid out as horizontal English rows in a resized box; the sumo bug-cage screen's "Bug Swap Notebook" cover and the four preview pictures in the Summer
  Memories menu (diary, specimens, kite book) are redrawn in English.

Not done yet
- Crayon captions drawn inside some diary pictures, the two tilted frames of each book-opening animation,
  small publisher/credit lines on the book covers, the notebook brand title, wall posters and a calligraphy
  scroll painted into the storehouse background, the Sneak Peek
  trailer's notice text and the Japanese game logo are left as they are.
- Checked on screen in PPSSPP: opening scenes, title menu, Summer Memories flow, settings, controls help, desk menu,
  item list, bug kit boxes, bug cage header, empty specimen page, dinner and bedtime scenes, bedtime prompt,
  picture diary pages for Aug. 1 and 2, saving, Continue and the load screen, examine hints, the Items screen,
  the empty Jumbo Box, specimen tool bubbles, the "Let it go?" prompt, the Species List panel and the cage-full
  notice (the last three were brought up by editing memory, not by playing to them).
  Also seen in game (reached through the game's own hidden debug menu): the kite-flying screen and its HUD, the kite
  pause menu, the Change-kite list, the sumo bug-cage screen and the Summer Memories menu with its previews.
  Not yet seen in game: fishing play screens, bug sumo matches, the translated notebook cover, a filled specimen
  page, the Jumbo Box header, sumo move names, win/loss marks, fortunes, fish names, the
  Summer Memories viewers (they need a finished save) (these
  executable strings were rendered offline with the built font and compose correctly, but their on-screen
  placement is unchecked). The Fishing Tackle screen has been seen in game. Not tested on a real PSP.
- The executable in the patched ISO is the game's own unencrypted copy with small changes; a real PSP needs
  custom firmware that accepts it.

Fonts
- M PLUS Rounded 1c (c) 2016 The Rounded M+ Project Authors, SIL Open Font License 1.1.
- Patrick Hand (c) 2010-2012 Patrick Wagesreiter, SIL Open Font License 1.1 (see PatrickHand-OFL.txt).

This patch contains no game data that can be used without the original disc image.
