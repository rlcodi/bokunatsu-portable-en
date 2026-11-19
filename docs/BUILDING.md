# Building the patch yourself

You don't need this to just play. Grab the xdelta from the Releases page and follow the README.
This is for rebuilding, tweaking text, or poking around.

You need: your own Japanese ISO (UCJS10038), Python 3, `xdelta3`, `bsdtar` (or any ISO extractor), `swiftc` (macOS) for two small helpers.
Nothing from the game is in this repo. Everything below is made from your ISO.

`S` = an empty scratch folder. Keep game files out of the repo.
Scripts in `tools/` and `harness/` read `S` from the `BNN_S` env var (default: the current folder).

1. Extract from the ISO into `S`:
   - `PSP_GAME/SYSDIR/BOOT.BIN` and `EBOOT.BIN` into `S/bnn-x/` (keep the relative paths)
   - `PSP_GAME/USRDIR/cdimg.idx` into `S/bnn-x/` and `cdimg0.img` into `S/bnn-img/` (same relative paths)
   - `tools/isox.py game.iso` lists the files in an ISO if your extractor won't read it.
2. `python3 tools/dfi_extract.py S/bnn-x/PSP_GAME/USRDIR/cdimg.idx S/bnn-img/PSP_GAME/USRDIR/cdimg0.img S/bnn-files`
3. `python3 tools/gzx_unpack.py S/bnn-files S/bnn-gzx` and `python3 tools/gzc_unpack.py S/bnn-files S/bnn-gzc`
4. Copy into `S`: `work/tr`, `work/trui`, `work/fontdl`, `work/bnn-table.txt`, `work/bnn-table2.txt`, `work/glyphs.txt`, `work/chars.txt`,
   and the whole `tools/` folder (as `S/tools`).
5. Make the Japanese script dump (it's game text, so it's made locally, never committed): `python3 tools/dump3.py S` -> `S/script_v3.json`.
6. `S/font.bin` = entry 5 of the decompressed `01startup/startup.bin` (offset 0x75b80, size 0x40140).
7. Build the two Swift helpers: `swiftc -O tools/rtext.swift -o S/rtext` and `swiftc -O tools/render_glyphs.swift -o S/render_glyphs`.
8. `python3 tools/fontpack.py S` -> `S/font_en.bin`, `S/font_en_map.json`.
9. `python3 tools/build_patch.py S x S/patched.iso` (about half a minute).
10. `xdelta3 -e -9 -s original.iso S/patched.iso bnn-portable-en-wip.xdelta`, then decode it again and compare SHA-1s.

Build 39 gives patched SHA-1 `514eea55b0c464406274d0c5c3d58f093c35235f`. A clean rebuild from build 39's sources should match it.

## Testing in PPSSPP

- Never use your real PPSSPP config or saves. Launch with `HOME=<S>/home` and seed it with `work/ppsspp/ppsspp.ini`
  (software renderer on, fast memory access off) under `home/.config/ppsspp/PSP/SYSTEM/`.
- `--appendconfig=work/ppsspp/ppsspp-dbg.ini` turns on the WebSocket debugger. The test scripts in `harness/` use it.
- `tools/session.py` (launch, press, read memory, screenshot) is the base for those scripts.
- A debug build of the patch (`BNN_AUDIT=1 python3 tools/build_patch.py ...`) logs every glyph draw so `harness/audit.py` can flag vertical or off-screen text. Never ship that build.

## Layout

- `tools/`: the build pipeline (extract, pack, text, font, images, executable patch).
- `work/`: translation text (`tr/` story, `trui/` menus, bugs and diary), character tables, font inputs.
- `harness/`: emulator debugger and test scripts. Rough, but they work. See `docs/NOTES.md`.
- `docs/`: status, notes, coverage.
