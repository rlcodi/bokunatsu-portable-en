import sys,time,struct,subprocess
iso=sys.argv[1]
subprocess.run(['python3','dbgmenu.py',iso],check=True)
subprocess.run(['python3','k.py','q:right','w:0.7']+['q:down','w:0.4']*8+['q:circle','w:5'],check=True)
