import json,sys
S=sys.argv[1]; a,b=int(sys.argv[2]),int(sys.argv[3])
for r in json.load(open(S+'/script_v3.json',encoding='utf8'))[a:b]:
    sc=r['first'].split(':')[0][2:]
    if r['kind']=='choice': print('%d C %s x%d | %s'%(r['id'],sc,r['count'],' / '.join(r['jp'][0].strip('\n').split('\n'))))
    else: print('%d %s %s | %s'%(r['id'],sc,r['spk'],' ‖ '.join(r['jp'])))
