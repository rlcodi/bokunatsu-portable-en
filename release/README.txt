================================================================================
 BOKU NO NATSUYASUMI PORTABLE - ENGLISH TRANSLATION PATCH
 ぼくのなつやすみ ポータブル ムシムシ博士とてっぺん山の秘密!!
 PSP / UCJS10038 / JPN / BUILD 40 / XDELTA3
================================================================================

 RELEASE INFO
 ..............................................................................
   ROM .......... Boku no Natsuyasumi Portable (Japan)
   PLATFORM ..... Sony PlayStation Portable
   ID ........... UCJS10038
   REGION ....... Japan
   BUILD ........ 40
   FORMAT ....... xdelta3 patch - no game data included
   SOURCE ....... https://github.com/rlcodi/bokunatsu-portable-en

 SOURCE IMAGE
 ..............................................................................
   Untouched Japanese ISO only:
     size   397,508,608 bytes
     SHA-1  c7c9549fe565ee2702512a93a97353be208dd2cd

 APPLYING THE PATCH
 ..............................................................................
   Command line:

     xdelta3 -d -s "original.iso" bnn-portable-en.xdelta "patched.iso"

   Browser, no install - RomPatcher.js by Marc Robledo (xdelta supported,
   files are processed locally and never uploaded):

     1. Open https://www.marcrobledo.com/RomPatcher.js/
     2. ROM file:    your untouched Japanese ISO
     3. Patch file:  bnn-portable-en.xdelta
     4. Apply patch, then download the patched ISO

   Expected patched ISO SHA-1:
     3eb71c02b4be79dc5e624221fd38d4cd33afc631

   Any mismatch means the source image is the wrong revision. Re-dump it; do
   not report bugs from a mismatched build.

 AI ASSISTANCE AND APPROACH
 ..............................................................................
   This is an AI-assisted translation. Both the translation and the review
   pass were done by AI, working from a directive to keep the tone and feel of
   the original. It has not been reviewed by a native speaker.

   The goal is authenticity, not paraphrase:
     - each speaker keeps their register and voice instead of being flattened
       into one neutral English;
     - the period and place feel of a rural 1970s summer is kept, without
       modern slang;
     - jokes and wordplay work in English where an equivalent exists, and stay
       visible where it does not;
     - names, honorifics and forms of address follow the Japanese rather than
       being localised away.

   Nothing was invented or padded, and text that could not be translated
   confidently was left alone rather than guessed at. There has been no
   native-speaker pass, so expect rough spots. Corrections are wanted:
   see PROOFREADING.

 WHAT IS TRANSLATED
 ..............................................................................
   - Story: all 2,288 dialogue, narration, hint and choice messages, drawn as
     centred subtitles on a dark band along the bottom of the screen.
   - Menus: all 459 interface text blocks - item names and notes, insect names
     and specimen entries, kite names, fishing notes, bug sumo and cage
     prompts, save/load and Favorites messages, Summer Memories menus,
     settings and controls help.
   - Graphics: title menu and subtitle, settings screen, speech bubbles,
     plaques and buttons, fishing labels, sumo result cards and move names,
     specimen page, radio exercise card, 8 kite book pages, 17 insect guide
     pages (day and night), both book covers, all 98 picture diary pages, kite
     gauges, ending caption.
   - Executable strings: "Caught m/d", "No specimens yet", win/loss marks,
     fortune results, the kite crash box, fish names.
   - Vertical text: English is set horizontally everywhere it was found, with
     boxes resized to fit - specimen names and notes, the bedtime prompt,
     "Let it go?", the species list panel, cage notices, the kite pause menu,
     "Keep / Let go", fortunes, and all 14 layouts of the story choice widget.
   - XMB: game title, icon caption and splash text (Japanese logo kept).
   - Fonts: M PLUS Rounded 1c for dialogue and menus, Patrick Hand for the
     diary pages.

 NOT DONE OR NOT VERIFIED
 ..............................................................................
   Still Japanese:
     - staff credits and title cards burned into the opening/ending videos
     - the Sneak Peek trailer
     - the game logo on the title screen
     - the covers in the tilted frames of the book-opening animation
     - a few crayon captions inside diary pictures
     - posters and a calligraphy scroll painted into the storehouse
       background, and product art on items

   Not yet seen on screen: fish names after a catch, bug sumo matches
   (move names, win/loss marks), the Kites and Favorites viewers, real story
   choice menus, a filled specimen page, the Jumbo Box header.

   Checked in PPSSPP: opening scenes, title and settings, desk menu, item
   list, bug kit and cage, empty specimen page, species list, bedtime and
   diary, save/load and Continue, examine hints, kite flying and its pause
   menu, fishing tackle page, bug catch prompt, sumo cage screen, fortunes,
   ending save prompts, and the Summer Memories menu and viewers.

   Confirmation on a physical PSP is in progress; not every screen has been
   checked on hardware yet. Display issues may still turn up. Corrections and
   bug reports are welcome.

 PROOFREADING
 ..............................................................................
   docs/translation-table.tsv in the repository lists every story message -
   id, speaker, source file, Japanese next to English. Fix a line by editing
   its id in work/tr/<file>.txt and sending a PR or an issue.

 REPORTING
 ..............................................................................
   Bugs, untranslated text, layout errors: open an issue with a screenshot.
   https://github.com/rlcodi/bokunatsu-portable-en/issues

 FONTS
 ..............................................................................
   M PLUS Rounded 1c (c) 2016 The Rounded M+ Project Authors, SIL OFL 1.1.
   Patrick Hand (c) 2010-2012 Patrick Wagesreiter, SIL OFL 1.1
   (see PatrickHand-OFL.txt).

 LEGAL
 ..............................................................................
   Fan translation. Not affiliated with, sponsored by or endorsed by Sony
   Computer Entertainment or the original developers and publishers. The
   game and its art, music and text remain the property of their owners.

   This patch contains no game data that can be used without the original
   disc image. Do not ask for ISOs and do not post them.

================================================================================
