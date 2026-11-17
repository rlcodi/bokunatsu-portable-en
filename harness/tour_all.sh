ISO=$PWD/audit_v31.iso
# 1) save/load/adhoc screens
for spec in "save 1 5" "load 1 6" "adhoc 2 3"; do set -- $spec; name=$1; pages=$2; downs=$3
  python3 dbgmenu.py $ISO >/dev/null
  python3 audit.py 40 t_$name > audit_t_$name.log 2>&1 &
  seq=""; for i in $(seq $pages); do seq="$seq q:right w:0.7"; done; for i in $(seq $downs); do seq="$seq q:down w:0.4"; done
  python3 k.py $seq q:circle w:6 q:circle w:3 q:down w:1 q:circle w:3 q:cross w:2 q:circle w:3 q:cross w:2 >/dev/null
  wait; echo "$name: $(tr '\n' ' ' < audit_t_$name.log)"
done
# 2) desk + kit + cage + specimen on the real save
timeout 400 python3 t_go.py $ISO >/dev/null 2>&1
python3 audit.py 150 t_desk > audit_t_desk.log 2>&1 &
python3 k.py q:square w:2.5 q:right w:1.2 q:circle w:2.5 q:circle w:1.5 q:cross w:1.5 q:circle w:2.5 q:square w:2.5 q:left w:1 q:circle w:2.5 q:cross w:1.5 q:circle w:2 q:right w:1 q:circle w:2.5 q:cross w:1.5 q:circle w:2 q:right w:1 q:circle w:2.5 q:cross w:1.5 q:circle w:2 q:right w:1 q:circle w:3 q:circle w:2 q:circle w:2 q:cross w:2 q:cross w:2 q:cross w:2 >/dev/null
python3 k.py q:square w:2.5 q:right w:0.8 q:right w:0.8 q:up w:0.8 q:circle w:2.5 q:left w:1.5 q:circle w:2.5 q:down w:2.5 q:circle w:2.5 q:circle w:2.5 q:cross w:2 q:cross w:2 q:cross w:2 >/dev/null
wait; echo "desk/kit: $(tr '\n' ' ' < audit_t_desk.log)"
