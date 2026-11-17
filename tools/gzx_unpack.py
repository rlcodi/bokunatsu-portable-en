import sys,os,zlib,glob,re
src,dst=sys.argv[1:3]
strict=re.compile(rb'(?:(?:[\x81-\x9f\xe0-\xea][\x40-\x7e\x80-\xfc])|[\x20-\x7e]){8,}')
for f in sorted(glob.glob(src+'/*/*.gzx')):
    d=open(f,'rb').read()
    assert d[4:6]==b'\x1f\x8b',f
    raw=zlib.decompressobj(31).decompress(d[4:])
    out=os.path.join(dst,os.path.relpath(f,src)[:-4]); os.makedirs(os.path.dirname(out),exist_ok=True)
    open(out,'wb').write(raw)
    jp=0
    for m in strict.finditer(raw):
        try: t=m.group().decode('cp932')
        except: continue
        if re.search('[ぁ-んァ-ヶ一-龥]',t) and len(re.findall('[ぁ-んァ-ヶ一-龥]',t))>=4: jp+=1
    print(f'{os.path.relpath(f,src):42s} {len(d):8d} -> {len(raw):8d}  jp_runs={jp}  hdr={d[:4].hex()}')
