set -e
python3 dbgmenu.py $PWD/test_v28.iso >/dev/null
python3 k.py q:circle w:8
python3 setscene.py H24000
python3 k.py q:circle w:20
python3 - <<'PY'
import sys;sys.path.insert(0,'tools')
import session as s,cheat
w=s.attach()
for f in (3,0x0A,0xEA): cheat.setflag(w,f,1)
PY
python3 k.py q:square w:2.5 q:right w:1 q:circle w:1.5 q:circle w:1 q:cross w:1 q:circle w:2.5 q:cross w:1.5 s:fs
