import sys,time,subprocess
ISO=sys.argv[1]
# (name, pages to the right, downs, extra key script)
modes=[('save',1,5),('load',1,6),('sumo',1,9),('memory',1,10),('adhoc',2,3),('delfile',2,9),('chkfile',2,10),('inet',2,11),('titletest',1,1),('kuchiki',1,0)]
def keys(seq):
    subprocess.run(['python3','k.py']+seq,check=False,stdout=subprocess.DEVNULL)
for name,pages,downs in modes:
    subprocess.run(['python3','dbgmenu.py',ISO],stdout=subprocess.DEVNULL)
    bg=subprocess.Popen(['python3','audit.py','45',name],stdout=open('audit_m_%s.log'%name,'w'),stderr=subprocess.STDOUT)
    seq=[]
    for p in range(pages): seq+=['q:right','w:0.7']
    for d in range(downs): seq+=['q:down','w:0.4']
    seq+=['q:circle','w:6','s:m_%s_0'%name]
    for k in range(4): seq+=['q:circle','w:3','s:m_%s_%d'%(name,k+1),'q:down','w:1','q:circle','w:3','q:cross','w:2']
    keys(seq); bg.wait()
    print(name,open('audit_m_%s.log'%name).read().strip().replace('\n',' | '),flush=True)
