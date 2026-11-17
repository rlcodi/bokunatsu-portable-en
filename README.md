# Boku no Natsuyasumi Portable: English patch

English patch for **ぼくのなつやすみ ポータブル ムシムシ博士とてっぺん山の秘密!!** (PSP, Japan, UCJS10038).

**Status: work in progress. Build 36.** Everything you read in the game is translated, and I've gone through most
screens in an emulator. A few things aren't checked yet and a few things are still Japanese. Details in
[docs/STATUS.md](docs/STATUS.md).

This repo has **no game data**. You need your own copy of the Japanese game. You get the patch from the
[Releases](../../releases) page.

## What you need

- Your own Japanese disc image, untouched:
  - size 397,508,608 bytes
  - SHA-1 `c7c9549fe565ee2702512a93a97353be208dd2cd`
- `xdelta3` (mac: `brew install xdelta`, Linux: your package manager, Windows: any xdelta patcher, like xdelta UI)
- [PPSSPP](https://www.ppsspp.org/) or a PSP with custom firmware

## Patch it

```bash
xdelta3 -d -s "original.iso" bnn-portable-en-wip.xdelta "Boku no Natsuyasumi Portable (English WIP).iso"
shasum "Boku no Natsuyasumi Portable (English WIP).iso"
```

The patched ISO should come out as SHA-1 `182b896a47ca1316af93cdb66a1de325f5c57b17`.
If it doesn't, your original isn't the right one.

## Play it

- **PPSSPP:** just open the ISO.
- **PSP:** you need custom firmware. The patched ISO boots the game's plain, unencrypted executable, so stock firmware won't run it.
  Put the ISO in your `ISO` folder like any other game.
- Same game ID as the Japanese game, so your existing saves load. Back them up first anyway.

## What's translated

All the dialogue, narration and choices (2,288 messages), every menu and prompt, the item and bug text,
the picture diary, the book pages and guides, the speech bubbles, plaques and buttons, and the text hidden in the executable.
Text is shown as centered subtitles, and the English is drawn horizontally even where the original was vertical.

## What's not done or not checked

- Not seen in game yet: fish names after a catch, bug sumo matches, the Kites and Favorites viewers, and the choice menus in real story scenes.
- Still Japanese: the credits burned into the opening and ending movies, the Sneak Peek trailer, the game logo,
  the covers in the tilted book-opening frames, a few crayon captions in diary drawings.
- Not tested on a real PSP yet.

If you find something broken or still in Japanese, open an issue. A screenshot helps a lot.

## Building it yourself

[docs/BUILDING.md](docs/BUILDING.md). Rough dev notes are in [docs/NOTES.md](docs/NOTES.md).

## Credits and legal

- Translation and tools made with help from Claude (Anthropic's AI). Text was reviewed in game, but it's still a first pass, so expect rough spots.
- Fonts: M PLUS Rounded 1c and Patrick Hand, both SIL OFL 1.1 ([licenses/](licenses/)).
- Code and translation text are MIT ([LICENSE](LICENSE)).
- Fan project. Not affiliated with or endorsed by Sony or the original developers. The game and its art, music and text belong to their owners.
  Don't ask for ISOs and don't post them here.
