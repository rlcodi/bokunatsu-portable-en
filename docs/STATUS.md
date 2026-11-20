# Translation status

Build 40. Patched SHA-1 `3eb71c02b4be79dc5e624221fd38d4cd33afc631`. Last updated 2026-11-19.

Short version: it's fully translated, I've checked most of the game in an emulator, and a handful of screens
haven't been seen yet. It's not a finished release.

## Done

- **Story:** all 2,288 messages (dialogue, narration, hints, choices). Shown as centered subtitles.
  All of them load and encode with no errors.
- **Interface text:** all 459 text blocks across the game's files. Item names and notes, bug names and entries,
  kite names, fishing notes, sumo and cage prompts, save/load/Favorites messages, settings, controls help.
- **Pictures:** title menu and subtitle, settings screen, the desk and speech bubbles, plaques and buttons,
  fishing labels, sumo cards and move names, the specimen page, the radio exercise card, 8 kite book pages,
  17 insect guide pages (day and night), both book covers, 98 picture diary pages, the kite gauges, the ending
  captions, the Summer Memories previews, the sumo notebook cover.
- **Text inside the executable:** the "Caught" line, win/loss marks, fortune results, the kite crash word, fish names.
- **Vertical text:** the game draws a lot of Japanese vertically. In English it's horizontal everywhere I found it:
  specimen names and notes, the bedtime prompt, the "Let it go?" prompt, the species list panel, the cage notices,
  the kite pause menu, the "Keep / Let go" prompt, the fortune window, the kite crash box, and every layout of the menu widget
  the story choices use. Boxes were resized to fit.
- **XMB:** game title, icon caption and the splash text are English (the Japanese logo is kept, like on the title screen).
- **Subtitles:** drawn on a dark band at the bottom of the screen, every line centred (checked against the opening arrival scene).
- **Review pass (build 40):** every one of the 2,288 messages was re-read against the Japanese in context, including the ~50 short "..." fragments. Fixed nine lines (a garbled "let's eat" fragment, the Baumkuchen mix-up, "drink your mama's milk", the longhorn beetle, the blood-rain joke and a few clunky phrasings). Still an AI translation with no native-speaker review.
- **Fonts:** M PLUS Rounded 1c for dialogue and menus, Patrick Hand for diary pages.

## Seen working in an emulator

Title and settings, desk and items, bug kit and cage, specimen page (empty and filled, full bug names),
species list, bedtime and diary saving, save and load screens, Favorites and ad-hoc messages, kite flying (gauges, pause menu, kite list,
crash), fishing (tackle page, rod, the HIT mark), the bug catch screen and its "Keep / Let go" prompt, the sumo cage screen,
the fortune result, the ending save prompts, and in Summer Memories: the menu, the picture diary, the items and the ending viewer
(using a finished-game save). Story subtitles looked right wherever I looked, but I haven't read every scene in game.

I also forced all 14 layouts of the menu widget with the widest real English text and measured them against their boxes. They fit.
A test build that logs every glyph drawn found no vertical or off-screen text on the screens above.

## Not seen yet

- Fish names after a catch, and the Jumbo Box header (the saves I had held no fish).
- Bug sumo matches: move names, win/loss marks.
- Real story choice menus. The layouts are checked, but I haven't watched one in an actual scene.
- The Kites and Favorites entries in Summer Memories.
- The species list side panel with a real collected bug (checked earlier with edited memory).
- A real PSP. All of this was tested in PPSSPP.

## Still Japanese (on purpose or not done)

- Staff credits and title card burned into the opening and ending **movies**. That's video, not text.
- The Sneak Peek trailer (its title card and voice credit are in the video).
- The game logo on the title screen.
- The covers on the tilted frames of the book-opening animation (insect guide, kite book, the picture diary notebook brand name).
- A few crayon captions drawn inside diary pictures.
- Posters and a calligraphy scroll painted into the storehouse background, and product art on items (the cracker bag, a book cover).

## Known rough spots

- It's a first-pass translation, drafted with AI help. Names and jokes may not match what a human translator would pick. Tell me what reads wrong.
- The 2-option story choices have an empty third row in the layout they use. I haven't checked how the cursor behaves there.
- Some long names are tight in the species list panel.

## How it was checked

`docs/COVERAGE.md` has the checklist I used against fan guides, and `docs/NOTES.md` has the debugging notes.
