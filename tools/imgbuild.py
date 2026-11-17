"""All image-text jobs. apply(S, files) -> files with redrawn sprites. files: {relpath: bytes}"""
import sys,os,zlib
sys.path.insert(0,os.path.dirname(__file__)); import pim2
from imgtext import R,Sheet,BOLD,MED,lum
def load(S,files,rel):
    if rel in files: return bytearray(files[rel])
    p=S+'/'+rel
    return bytearray(open(p,'rb').read())
def title(S,r,d):
    sh=Sheet(d,pim2.find(d)[1])
    sh.outlined(r,(396,127,104,17),2,'New Game')
    sh.outlined(r,(396,148,104,17),3,'Continue')
    sh.outlined(r,(396,169,104,17),4,'Summer Memories')
    sh.outlined(r,(378,358,56,17),5,'Settings'); sh.clear(468,2,31,17); sh.set_sprite(5,378,358,56,17)
    sh.outlined(r,(336,252,86,17),25,'Sneak Peek')
    for yy in range(218+3,218+29):       # erase between the capsule's left and right border runs
        a=2
        while sh.get(a,yy)==0: a+=1
        while sh.get(a,yy)!=0: a+=1
        b=2+328
        while sh.get(b,yy)==0: b-=1
        while sh.get(b,yy)!=0: b-=1
        for xx in range(a,b+1): sh.put(xx,yy,0)
    print('  subtitle',sh.alpha(r,(2+12,218+3,305,26),8,'Dr. Bug and the Secret of Mt. Teppen!!',size=17,margin=2))
    sh.save()
LIB=[]   # clean bubbles: (transparency mask, rgba list)
def bubble(sh,r,x,y,p,text,size=11,w=48,h=36):
    from collections import Counter
    from imgtext import nearest
    rect=(x,y,62,62); pal=sh.palette(p)
    paper=Counter(sh.get(x+a,y+b) for b in range(19,35) for a in range(23,39) if pal[sh.get(x+a,y+b)][:3]>(200,200,200)).most_common(1)[0][0]
    sh.erase_islands(rect,paper)
    xs=[a for b in range(20,35) for a in range(62) if sh.get(x+a,y+b)==paper]; cx=(min(xs)+max(xs)+1)//2; cy=27
    mask=bytes(1 if pal[sh.get(x+a,y+b)][3]<8 else 0 for b in range(62) for a in range(62))
    dirty=sum(1 for b in range(62) for a in range(62) if (a-cx)**2+(b-cy)**2<18*18 and sh.get(x+a,y+b)!=paper)
    if dirty:
        best=min(LIB,key=lambda e:sum(i!=j for i,j in zip(e[0],mask))); diff=sum(i!=j for i,j in zip(best[0],mask))
        assert diff<60,('no clean twin',text,diff)
        nn=nearest(pal)
        for b in range(62):
            for a in range(62):
                c=best[1][b*62+a]; sh.put(x+a,y+b,nn((c[0]*c[3]/255.,c[1]*c[3]/255.,c[2]*c[3]/255.,c[3])))
        print('   (twin used for %r, mask diff %d)'%(text,diff))
    else: LIB.append((mask,[pal[sh.get(x+a,y+b)] for b in range(62) for a in range(62)]))
    ink=min((c for c in pal if c[3]>=0xf0),key=lambda c:sum(c[:3]))[:3]
    return sh.inked(r,(x+cx-w//2,y+cy-h//2,w,h),p,text,size=size,lg=-1,margin=1,ink=ink,paper=pal[paper][:3])
def bubbles(sh,r,p,labels):
    for (x,y),t in labels.items(): print('  bubble',t.replace('\n','/'),bubble(sh,r,x,y,p,t))
def desk(S,r,d):
    sh=Sheet(d,pim2.find(d)[0])
    bubbles(sh,r,1,{(186,124):'Items',(190,0):'Fishing\nTackle',(128,0):'Fly\nKite',(190,62):'Nothing',(0,112):'Bug\nNet',(62,112):'Back',(124,124):'Settings',(128,62):'Bug\nKit'})
    sh.save()
def specimen(S,r,d):
    sh=Sheet(d,pim2.find(d)[0])
    bubbles(sh,r,0,{(2,2):'Bug\nCage',(68,2):'Magnifier',(134,2):'Syringe',(200,2):'Delete\nSpecimen',(266,2):'Prev\nPage',(332,2):'Jumbo\nBox',
                    (2,68):'Release\nBug',(68,68):'Medicine',(134,68):'Specimen\nBox',(200,68):'Species\nList',(266,68):'Next\nPage',(332,68):'Edit'})
    sh.save()
    sh=Sheet(d,pim2.find(d)[3]); ink=lambda R,G,B,A:lum(R,G,B)<150     # specimen page: printed month/day marks -> "m / d"
    sh.erase_text([(88,225,18,17)],0,ink,grow=1)
    print('  specimen page slash',sh.relabel(r,(50,225,18,17),0,'/',ink,grow=1,font=MED,size=13,fill=(0x10,0x10,0x10),margin=0))
    sh.save()
def nbcover(S,r,d):                              # picture-diary notebook cover (flat frame): hand-lettered label
    sh=Sheet(d,pim2.find(d)[0])
    print('  notebook label',sh.relabel(r,(139,179,101,23),0,'Picture Diary',lambda R,G,B,A:lum(R,G,B)<150,grow=1,flat=True,size=13,fill=(0x10,0x10,0x10),margin=0))
    sh.save()
def sumo(S,r,d):
    sh=Sheet(d,pim2.find(d)[0]); sumo0(sh,r); sh.save()
    sh=Sheet(d,pim2.find(d)[3])
    print('  stamina',sh.relabel(r,(203,157,46,20),5,'Stamina',lambda R,G,B,A:lum(R,G,B)>140 or lum(R,G,B)<85,grow=1,flat=True,size=10,fill=(0xf0,0xc8,0x80),edge=(0x40,0x28,0x08),stroke=0.8,margin=0))
    print('  swap',sh.relabel(r,(271,157,31,22),9,'Swap',lambda R,G,B,A:lum(R,G,B)<170 and abs(R-B)<40,grow=1,flat=True,size=10,fill=(0x18,0x18,0x18),margin=0))
    bubbles(sh,r,8,{(68,54):'Bug\nCage',(2,54):'Swap\nBug',(250,22):'Release\nBug',(250,88):'Mine',(2,120):'Bug\nRank',(68,120):'Place\nBug',(134,122):'Gong'})
    sh.save()
    sh=Sheet(d,pim2.find(d)[2]); sumo2(sh,r); sh.save()
    sh=Sheet(d,pim2.find(d)[4]); sumo3(sh,r); sh.save()
MOVES={0:'Winning Move',1:'Head Charge',2:'Thrust Barrage',3:'Pivot Throw',4:'Bulldoze',5:'Guts',6:'Overarm Throw',7:'Brainbuster',
       8:'Pull Down',9:'Ankle Sweep',10:'Scoop Throw',11:'Lift Out',12:'Leg Pull',13:'Flip Over',14:'Body Crush',15:'Thrust Out',
       16:'Bear Hug',17:'Slap',18:'Scythe Clamp',19:'Scythe Buster',20:'Horn Drill',21:'Jumping Pivot Throw',22:'Horn Flick',
       23:'Tornado Charge',24:'Stamina Win',25:'Push Out',26:'Draw'}
def sumo0(sh,r):                                  # cage-selection backdrop: red crayon notebook title (bug exchange notebook)
    redp=lambda R,G,B,A:R>G+70 and R>B+70
    red=sh.pick((50,118,106,130),0,lambda R,G,B:R-G-B)
    for rect in ((70,118,66,52),(46,172,114,36),(66,208,88,42)):
        m=sh.mask_rgb(rect,0,redp,grow=2); sh.inpaint_any(rect,m,0)
    for rect,txt,sz in (((66,120,74,48),'Bug',34),((54,172,98,34),'Swap',28),((52,208,102,36),'Notebook',24)):
        print('  sumo notebook',txt,sh.over(r,rect,0,txt,font=HAND,size=sz,stroke=1.4,fill=red,edge=red,margin=0))
def sumo3(sh,r):                                  # winning-move names: vertical brush lettering -> rotated text
    for k,t in MOVES.items():
        sz=sh.vtext(r,k,t,size=13 if k==0 else 17,stroke=1.2 if k==0 else 1.5,top=0 if k==0 else 15)
        if sz<(11 if k==0 else 15): print('  move',k,t,'size',sz)
def sumo2(sh,r):
    dark=lambda R,G,B,A:lum(R,G,B)<178
    for dy in (0,144,274):
        p=5 if dy<272 else 6; ink=dict(fill=(0x20,0x20,0x20),font=MED,margin=0)
        sh.relabel(r,(150,34+dy,60,19),p,'Caught',dark,grow=1,size=12,**ink)
        sh.relabel(r,(108,82+dy,156,16),p,'Saw stag beetle value:',dark,grow=1,size=11,**ink)
        sh.relabel(r,(188,100+dy,60,16),p,'beetles',dark,grow=1,size=11,align='left',**ink)
    for dy in (0,274):
        p=5 if dy<272 else 6
        sh.relabel(r,(242,125+dy,41,14),p,'Close',lambda R,G,B,A:lum(R,G,B)<90,grow=0,flat=True,size=9.5,fill=(0x28,0x18,0x08),margin=0)
    for k,t in enumerate(('STRONG','WEAK')):     # chalk kanji inside the ring
        cx,cy=351,42+96*k; rect=(cx-36,cy-25,72,50)
        m=[q for q in sh.mask_rgb(rect,0,lambda R,G,B,A:lum(R,G,B)>110,grow=1) if ((q[0]-cx)/35.)**2+((q[1]-cy)/24.)**2<1]
        sh.inpaint_any(rect,m,0)
        print('  tile',t,sh.over(r,(cx-33,cy-12,66,24),0,t,size=15,fill=(0xf0,0xf0,0xe6),margin=0))
def jumbo(S,r,d):
    sh=Sheet(d,pim2.find(d)[1],swz=False); bubbles(sh,r,3,{(2,36):'Edit'}); sh.save()
def diaryicon(S,r,d):
    sh=Sheet(d,pim2.find(d)[1]); bubbles(sh,r,0,{(0,0):'Good\nNight'}); sh.save()
def item(S,r,d):
    sh=Sheet(d,pim2.find(d)[5]); bubbles(sh,r,0,{(0,0):'Items'}); sh.save()
    sh=Sheet(d,pim2.find(d)[1]); radiocard(sh,r); sh.save()
def kitebook(S,r,d):
    sh=Sheet(d,pim2.find(d)[0]); bubbles(sh,r,0,{(0,0):'Make\nThis Kite'}); sh.save()
    ink=lambda R,G,B,A:lum(R,G,B)<150 and max(R,G,B)-min(R,G,B)<50
    for k,(name,grade,body) in enumerate(KITES):
        sh=Sheet(d,pim2.find(d)[2+k])
        sh.erase_text([(164,6,150,211),(138,14,24,202)],0,ink)
        sh.textblock(r,(168,12,140,18),0,name,font=BOLD,size=14,lh=16,align='center',wrap=False)
        sh.textblock(r,(168,30,140,14),0,'['+grade+']',font=MED,size=10,lh=12,align='center',wrap=False)
        n=sh.textblock(r,(170,48,138,160),0,body,font=MED,size=10,lh=12)
        print('  kite page',name,n,'lines'); sh.save()
KITES=[('Carp Kite','Advanced',"A 3D kite shaped like a carp streamer swimming happily across the sky. Its frame is made of thin square rods. It's bigger and heavier than the other kites, so it takes real strength to get it up, but once it's flying it stays steady."),
 ('Bird Kite','Advanced',"A 3D kite shaped like a bird with big wings. Its colorful orange body stands out against the blue, and it glides gracefully, as if swimming through the open sky."),
 ('Square Kite','Beginner',"The second cross-spar from the top is strung extra tight, so this type is called a center-bowed square kite. It flies well even in a light breeze. If it wobbles on the way up, stick paper tails on the left and right corners."),
 ('Nina Kite','Intermediate',"A small children's kite made on the island of Iki. Its ribs are very thin, so fly it when the wind is light. Once it's up, you can clearly see its long red-and-white striped tail streaming in the wind. Very pretty."),
 ('Cicada Kite','Intermediate',"It's built with fairly thick ribs, so fly it on a windy day. Bow it a little harder to give it more shape. In summer it looks just like a real cicada flying through the sky. Tie on a thin string 2 to 3 m long as a tail."),
 ('Airplane Kite','Expert',"A small 3D kite that flies very steadily. Be careful not to let it hit the ground hard when it lands. Reel the line in skillfully and you can bring it right back to your hand while it's still flying."),
 ('Kite Train','Expert',"Kites made from light, colorful plastic bags, strung in a row. With anywhere from 5 to 100 of them, it can handle a light breeze or a fairly strong wind. Take care the line doesn't snap and let them get away."),
 ('Portrait Kite','???',"A life-size kite that looks just like a certain someone. It has no ribs below the knees, so once it's up it seems to walk across the sky. Float your double up there and try a little stroll through the air.")]
def kitesel(S,r,d):
    sh=Sheet(d,pim2.find(d)[3]); bubbles(sh,r,0,{(0,0):'Fly\nKite'}); sh.save()
def fishing(S,r,d):
    sh=Sheet(d,pim2.find(d)[3]); bubbles(sh,r,0,{(0,58):'Fishing\nTackle'})
    sh.clear(146,0,108,76,15)                       # tackle names, 19px bands, black on white
    for i,t in enumerate(('Bait (worm)','Bait (worm) + float','Tenkara (small fly)','Tenkara (large fly)')):
        print('  tackle',t,sh.inked(r,(146,19*i+1,108,17),1,t,font=MED,size=10.5,align='left',margin=1))
    sh.clear(0,18,100,40,15); sh.clear(126,0,20,18,15)   # Size / Avg / Max; drop the fish counter word
    sh.inked(r,(1,20,58,17),2,'Size',font=MED,size=12,align='left',margin=0)
    sh.inked(r,(62,20,36,17),2,'Avg',font=MED,size=12,align='left',margin=0)
    sh.inked(r,(62,38,36,17),2,'Max',font=MED,size=12,align='left',margin=0)
    sh.save()
def hud(S,r,d):
    sh=Sheet(d,pim2.find(d)[2],swz=False)
    # "rare" starbursts (3 frames)
    for k in range(3):
        rc=(48*k,16,48,48); m=sh.text_mask(rc,(5,6,10,11),(0,1,2,3,4),grow=4)+sh.text_mask(rc,(7,8,9),(),grow=0)
        sh.inpaint(rc,m,(12,13,14,15))
        sh.over(r,(48*k+6,16+10,34,17),10,'RARE',size=11,stroke=1.2,fill=(0xdb,0x1a,0x17),edge=(0x62,0x0b,0x08),margin=0)
    # Back plaque (stone arrow)
    rc=(144,48,64,32); m=[q for q in sh.text_mask(rc,(7,10,11),(0,1,2,3,5),grow=4) if q[1]>=48+10]+[q for q in sh.text_mask(rc,(7,10,11,12),(0,1,2,3,5),grow=1) if q[1]<48+10]
    sh.inpaint(rc,m,(6,8,9,13,14,15))
    sh.over(r,(144+11,48+3,36,17),9,'Back',size=13,fill=(0x11,0x0d,0x0c),margin=0)
    # butterfly button
    rc=(208,48,48,32); m=sh.text_mask(rc,(4,5,6,7,8),(0,1,2,3),grow=2)
    sh.inpaint(rc,m,(9,10,11,12,13,14,15))
    sh.over(r,(208+4,48+4,40,24),12,'Take\nOut',size=10,lg=-1,fill=(0x19,0x1a,0x0d),margin=0)
    # voice tag: 20x9 black box at (2,2)
    for b in range(2,12):
        for a in range(2,22): sh.put(a,96+b,1)
    sh.pixtext(3,96+3,'VOICE',15)
    sh.save()
def config(S,r,d):
    sh=Sheet(d,pim2.find(d)[1]); white=lambda R,G,B,A:lum(R,G,B)>140 or lum(R,G,B)<42
    kw=dict(fill=(255,255,255),edge=(0x38,0x08,0x14),stroke=1.0,margin=1)
    for rect,t,sz in (((120,186,114,26),'Voice + Subtitles',13),((2,186,114,26),'Voice + Subtitles',11),((162,62,92,26),'Voice Only',13),((162,92,92,26),'Voice Only',11),
                      ((162,2,92,26),'Subtitles Only',13),((162,32,92,26),'Subtitles Only',11)):
        x,y,w,h=rect; print('  cfg',t,sh.relabel(r,(x+2,y+2,w-4,h-4),0,t,white,grow=2,size=sz,**kw))
    print('  plaque',sh.relabel(r,(23,231,58,34),1,'Settings',lambda R,G,B,A:lum(R,G,B)<150,grow=1,size=12,fill=(0x18,0x18,0x18),margin=1))
    sh.save()
def memory(S,r,d):
    sh=Sheet(d,pim2.find(d)[0]); dark=lambda R,G,B,A:lum(R,G,B)<150
    print('  plaque',sh.relabel(r,(21,287,118,34),0,'Summer Memories',dark,grow=1,size=13,fill=(0x18,0x18,0x18),margin=1))
    print('  plaque',sh.relabel(r,(175,287,118,34),0,'Favorites',dark,grow=1,size=13,fill=(0x18,0x18,0x18),margin=1))
    sh.save()
    sh=Sheet(d,pim2.find(d)[1]); memthumbs(sh,r); sh.save()
def memthumbs(sh,r):                              # Summer Memories preview pictures: shrunk screenshots of the viewers with vertical Japanese text
    ink=lambda R,G,B,A:lum(R,G,B)<150
    ink2=lambda R,G,B,A:lum(R,G,B)<165
    def swap(rect,p,txt,font,size,lh,pred=ink,erase=None,grow=1):
        x,y,w,h=rect; er=erase or rect; m=sh.mask_rgb(er,p,pred,grow=grow); sh.inpaint_any(er,m,p)
        n=sh.textblock(r,rect,p,txt,font=font,size=size,lh=lh,wrap=False,fill=(0x28,0x28,0x28)); print('  thumb',txt[:14].replace('\n','/'),n)
    swap((27,93,116,41),0,'Aug. 1: Mom is having a baby, so\nthings are crazy! I am going to\nUncle\'s place. Lots of fun things\nto do there, I bet!',HAND,8,9)
    swap((158,113,53,47),1,'Swallowtail\nButterfly.\nSeen all\nover Japan.',MED,7,8,ink2,erase=(157,112,55,56))
    swap((314,292,53,52),5,'Giant Stag\nBeetle. Big\nand strong,\nand very\nrare.',MED,7,8,ink2)
    # kite book spread: right page vertical column text + title + label
    m=sh.mask_rgb((380,44,11,84),2,ink,grow=1); sh.inpaint_any((380,44,11,84),m,2)     # caption column in the margin
    swap((393,46,54,80),2,'Square Kite\nThe classic\nkite. Steady\nin a gentle\nwind, so it\nis easy to\nfly. Great\nfor first-\ntimers.',MED,6,8,lambda R,G,B,A:lum(R,G,B)<185,erase=(391,40,62,92),grow=2)
def saveload(S,r,d):
    sh=Sheet(d,pim2.find(d)[1])
    for (x,y,w,h,p) in sh.sp:
        if (w,h)!=(75,68) or p==0: continue      # palette 0 = the book (busy) animation, no label
        for yy in range(y+38,y+68):                 # background is a vertical gradient: refill each row from its left edge
            v=sh.get(x+1,yy)
            for xx in range(x+2,x+74): sh.put(xx,yy,v)
        sh.over(r,(x+2,y+41,71,24),p,'Linking',size=13,stroke=1.3,fill=(255,255,255),edge=(0,0,0),margin=1)
    p=sh.pal_at(280,110)
    print('  back',sh.relabel(r,(264,103,42,22),p,'Back',lambda R,G,B,A:lum(R,G,B)<95,grow=1,size=10.5,fill=(0x18,0x12,0x10),margin=0))
    sh.save()
def radiocard(sh,r):
    p=sh.pal_at(200,340); blue=lambda R,G,B,A:B>R+40 and lum(R,G,B)<215
    kw=dict(fill=(0x30,0xa8,0xe8),margin=0)
    print('  card',sh.relabel(r,(166,329,76,34),p,'Radio Exercise\nAttendance',blue,grow=1,flat=True,size=9.5,lg=1,**kw))
    print('  card',sh.relabel(r,(162,484,132,14),p,'Have a healthy summer!',blue,grow=1,flat=True,size=8.5,**kw))
from guide_data import GUIDE,BOOK
def guide_page(sh,r,e,book=False):
    name,fam,sizes,food,body=e
    ink=lambda R,G,B,A:lum(R,G,B)<165 and max(R,G,B)-min(R,G,B)<60
    top=125 if book else 121
    sh.erase_text([(162,17,152,98),(163,121,150,104),(10,121,152,104)],0,ink)
    sh.textblock(r,(164,18,150,15),0,name,font=BOLD,size=12 if len(name)<21 else 11,lh=14,align='center',wrap=False)
    lines=[fam]+sizes+r.wrap(food,MED,9.5,140)
    sh.textblock(r,(164,36,150,80),0,'\n'.join(lines),font=MED,size=9.5,lh=11.5,align='center',wrap=False)
    for size,lh in ((9.5,11.5),(9,11),(8.5,10.5)):
        nl=int((225-top)//lh); nr=int(104//lh); ls=r.wrap(body,MED,size,136)
        if len(ls)<=nl+nr: break
    else: raise ValueError('guide body too long: '+name)
    sh.textblock(r,(16,top+1,140,225-top),0,'\n'.join(ls[:nl]),font=MED,size=size,lh=lh,wrap=False)
    if ls[nl:]: sh.textblock(r,(169,122,142,104),0,'\n'.join(ls[nl:]),font=MED,size=size,lh=lh,wrap=False)
    return size,len(ls)
def guide_file(k):
    def f(S,r,d):
        sh=Sheet(d,pim2.find(d)[0]); print('  guide',GUIDE[k][0],guide_page(sh,r,GUIDE[k])); sh.save()
    return f
def guide_book(S,r,d):
    for i,o in enumerate(pim2.find(d)):
        sh=Sheet(d,o); print('  book',GUIDE[BOOK[i]][0],guide_page(sh,r,GUIDE[BOOK[i]],book=True)); sh.save()
def sat(R,G,B,A=255): return max(R,G,B)-min(R,G,B)
def cover_insect(S,r,d):
    sh=Sheet(d,pim2.find(d)[0]); T=(84,42,142,30)
    black=sh.pick(T,0,lambda R,G,B:-lum(R,G,B)); white=sh.pick(T,0,lambda R,G,B:lum(R,G,B),lambda R,G,B:sat(R,G,B)<40)
    red=sh.pick((116,24,74,20),0,lambda R,G,B:R-G-B); k=lum(*white)
    from collections import Counter
    yel=lambda R,G,B,A=255:R>G-10 and G>B+70 and sat(R,G,B)>90
    top=(84,40,142,17); v=Counter(sh.get(top[0]+a,top[1]+b) for b in range(4) for a in range(142) if yel(*sh.palette(0)[sh.get(top[0]+a,top[1]+b)])).most_common(1)[0][0]
    for q in sh.mask_rgb((78,42,152,16),0,lambda R,G,B,A:not yel(R,G,B) and not (R>G+80 and R>B+80),grow=1): sh.put(q[0],q[1],v)
    # the band where the old title overlapped the photo ring: rebuild from the ring's geometry
    P=sh.palette(0); isred=lambda c:c[0]>c[1]+90 and c[0]>c[2]+90
    pts=[(x,y) for y in range(78,215) for x in range(60,246) if isred(P[sh.get(x,y)])]
    n=len(pts); sx=sum(q[0] for q in pts)/n; sy=sum(q[1] for q in pts)/n
    u=[(q[0]-sx,q[1]-sy) for q in pts]; suu=sum(a*a for a,b in u); svv=sum(b*b for a,b in u); suv=sum(a*b for a,b in u)
    suuu=sum(a**3 for a,b in u); svvv=sum(b**3 for a,b in u); suvv=sum(a*b*b for a,b in u); svuu=sum(b*a*a for a,b in u)
    det=suu*svv-suv*suv; uc=((suuu+suvv)/2*svv-(svvv+svuu)/2*suv)/det; vc=((svvv+svuu)/2*suu-(suuu+suvv)/2*suv)/det
    cx,cy=sx+uc,sy+vc; rad=(uc*uc+vc*vc+(suu+svv)/n)**0.5
    ringv=Counter(sh.get(x,y) for x,y in pts).most_common(1)[0][0]; hole=[]
    for y in range(57,73):
        for x in range(78,230):
            dd=((x-cx)**2+(y-cy)**2)**0.5
            if dd>rad+1.5: sh.put(x,y,v)
            elif dd>rad-2.5: sh.put(x,y,ringv)
            elif sat(*P[sh.get(x,y)])<70 or lum(*P[sh.get(x,y)])<50 or True: hole.append((x,y))
    sh.inpaint_any((78,57,152,24),hole,0)
    O=(122,23,62,22); m=sh.mask_rgb(O,0,lambda R,G,B,A:G>red[1]+50 and not yel(R,G,B),grow=1)
    for q in m: sh.put(q[0],q[1],sh.idx[33*sh.w+118])
    sh.over(r,(122,25,62,19),0,'RARE',size=14,fill=white,margin=0)
    sh.over(r,(82,45,146,26),0,'INSECT GUIDE',size=18,stroke=1.6,fill=black,edge=white,margin=1)
    U=(108,73,90,11); m=sh.mask_rgb(U,0,lambda R,G,B,A:lum(R,G,B)>k-90 and sat(R,G,B)<70,grow=1); sh.inpaint_any(U,m,0)
    sh.over(r,(104,71,98,14),0,'Unusual Bugs',size=9,stroke=0.9,fill=white,edge=black,margin=0)
    sh.save()
def cover_kite(S,r,d):
    sh=Sheet(d,pim2.find(d)[0]); T=(136,24,40,118)
    black=sh.pick(T,0,lambda R,G,B:-lum(R,G,B)); white=sh.pick(T,0,lambda R,G,B:lum(R,G,B),lambda R,G,B:sat(R,G,B)<40)
    red=sh.pick(T,0,lambda R,G,B:R-G-B)
    m=sh.mask_rgb(T,0,lambda R,G,B,A:lum(R,G,B)<lum(*black)+45 or (R>red[0]-60 and R-G>90 and R-B>90),grow=2); sh.inpaint_any(T,m,0)
    sh.over(r,(92,46,126,16),0,'The Fun',size=13,stroke=1.2,fill=red,edge=white,margin=0)
    sh.over(r,(92,61,126,30),0,'KITE',size=27,stroke=1.8,fill=black,edge=white,margin=0)
    sh.over(r,(90,90,130,16),0,'ENCYCLOPEDIA',size=12.5,stroke=1.3,fill=black,edge=white,margin=1)
    sh.save()
JOBS={'bnn-files/sub/MOPA1.pm2':cover_insect,'bnn-files/sub/MOPN1.pm2':cover_insect,'bnn-files/sub/TOPA1.pm2':cover_kite,'bnn-files/sub/TOPN1.pm2':cover_kite,'bnn-files/sub/insect_book_day.bin':guide_book,'bnn-files/sub/insect_book_night.bin':guide_book,'bnn-gzx/system/saveload_normal.bin':saveload,'bnn-gzx/system/saveload_favorite.bin':saveload,'bnn-gzx/title/config.bin':config,'bnn-files/title/memory.bin':memory,'bnn-gzx/sub/0sub.bin':desk,'bnn-gzx/01startup/startup.bin':hud,'bnn-files/title/title.bin':title,
      'bnn-files/sub/specimen2.bin':specimen,'bnn-files/sub/sumo.dat':sumo,'bnn-files/sub/jumbo.bin':jumbo,'bnn-files/diary/icon.bin':diaryicon,'bnn-files/diary/Z_A00.pm2':nbcover,'bnn-files/diary/Z_N00.pm2':nbcover,
      'bnn-gzx/sub/item.bin':item,'bnn-files/sub/kite_book.bin':kitebook,'bnn-gzx/sub/kite_select.bin':kitesel,'bnn-gzx/sub/fishing_tackle.bin':fishing}
HAND='fontdl/PatrickHand-Regular.ttf'
def ending(S,r,d):
    sh=Sheet(d,pim2.find(d)[2]); sh.clear(0,0,288,64,0)
    sh.inked(r,(0,1,288,36),0,'Produced and copyrighted by\nSony Computer Entertainment Inc.',font=MED,size=12,lg=4,ink=(0xe7,0xe7,0xe7),paper=(0,0,0),margin=1)
    for i in range(288*64):                      # keep the background transparent
        if sh.idx[i]==1 or sh.pal[sh.idx[i]][:3]<(0x10,0x10,0x10): sh.idx[i]=0
    sh.save()
def kitehud(S,r,d):
    sh=Sheet(d,pim2.find(d)[0]); pal=sh.palette(0)
    fill=max(pal,key=lambda c:lum(*c[:3])*(c[3]>200))[:3]; edge=min((c for c in pal if c[3]>200),key=lambda c:lum(*c[:3]))[:3]
    for rect,t in (((3,417,36,19),'Dir.'),((41,417,36,19),'Wind'),((79,417,37,19),'Alt.')):
        print('  kite hud',t,sh.outlined(r,rect,0,t,font=HAND,size=15,stroke=1.2,fill=fill,edge=edge,margin=1))
    sh.save()
def diary_page(text):
    def f(S,r,d):
        sh=Sheet(d,pim2.find(d)[0]); R_=(3,141,298,94)
        ink=lambda R,G,B,A:(lum(R,G,B)<150 and sat(R,G,B)<50) or (B>R+6 and lum(R,G,B)<238)     # writing, and the column rules
        sh.erase_text([R_],0,ink,grow=2)
        sh.textblock(r,(277,145,26,16),0,'Aug.',font=HAND,size=12,lh=13,align='center',wrap=False,fill=(0x20,0x20,0x20))
        for size,lh in ((15,16),(14,15),(13,14),(12,13)):
            ls=r.wrap(text,HAND,size,258)
            if len(ls)*lh<=90: break
        else: raise ValueError('diary text too long: '+text[:30])
        sh.textblock(r,(10,147,264,90),0,'\n'.join(ls),font=HAND,size=size,lh=lh,wrap=False,fill=(0x20,0x20,0x20))
        sh.save()
    return f
def _diary(S_):
    for ln in open(S_+'/trui/diary.txt',encoding='utf8'):
        if '|' in ln and not ln.startswith('#'):
            k,t=ln.rstrip('\n').split('|',1); JOBS['bnn-files/diary/NIKKI%s.pm2'%k]=diary_page(t)
for _k in range(5): JOBS['bnn-files/oti/oti%02d.bin'%_k]=ending
for _k in range(2): JOBS['bnn-files/tako/tbg%02d.pm2'%_k]=kitehud
for _k in range(17):
    for _c in 'AN': JOBS['bnn-files/sub/MZ%s%02d.pm2'%(_c,_k+1)]=guide_file(_k)
def apply(S,files,only=None):
    _diary(S)
    r=R(S); out=dict(files)
    for rel,fn in JOBS.items():
        if only and rel not in only: continue
        d=load(S,files,rel); print('img',rel); fn(S,r,d); out[rel]=bytes(d)
    return out
if __name__=='__main__':
    S=sys.argv[1]; want=sys.argv[2:]; _diary(S); out=apply(S,{},only=set(k for k in JOBS if any(os.path.basename(k)==w.split(':')[0] for w in want)) or None)
    for rel,d in out.items():
        for k,o in enumerate(pim2.find(d)):
            tag='%s:%d'%(os.path.basename(rel),k)
            if want and tag not in want: continue
            name=S+'/img/new_%s_%02d.png'%(os.path.basename(rel),k); sw=d[o:o+4]==b'PIM2'
            if pim2.sprites(d,o): pim2.render_sprites(d,o,name,swz=sw)
            else:
                w,h,rgba,_,_,_=pim2.decode(d,o,swz=sw); pim2.to_png(name,w,h,rgba)
