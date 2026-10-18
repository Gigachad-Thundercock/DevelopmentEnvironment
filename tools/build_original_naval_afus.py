#!/usr/bin/env python3
"""Original tri-faction naval advanced fusion models. No borrowed donor geometry.
Actual atlas artwork sampled per faction; builds NavalAfus/objects3d/Units/*.s3o.
"""
import math,struct,urllib.request
from pathlib import Path
from PIL import Image,ImageStat
H=struct.Struct("<12sI5f4I");P=struct.Struct("<10I3f");V=struct.Struct("<8f")
OUT=Path("NavalAfus/objects3d/Units");OUT.mkdir(parents=True,exist_ok=True)
TMP=Path("/tmp/afus-atlas");TMP.mkdir(exist_ok=True)
TEXTURES={"arm":"Arm_color.dds","cor":"cor_color.dds","leg":"leg_color.dds"}
class Piece:
 def __init__(self,name,off=(0,0,0)):
  self.name=name;self.off=off;self.v=[];self.idx=[];self.children=[]
 def child(self,name,off=(0,0,0)):
  c=Piece(name,off);self.children.append(c);return c
 def tri(self,pts,uv):
  a,b,c=pts;d=[b[i]-a[i] for i in range(3)];e=[c[i]-a[i] for i in range(3)]
  n=(d[1]*e[2]-d[2]*e[1],d[2]*e[0]-d[0]*e[2],d[0]*e[1]-d[1]*e[0]);l=math.sqrt(sum(x*x for x in n)) or 1
  for p,t in zip(pts,uv):
   self.idx.append(len(self.v));self.v.append((*p,*(x/l for x in n),*t))
 def quad(self,a,b,c,d,uv):
  self.tri((a,b,c),uv[:3]);self.tri((a,c,d),(uv[0],uv[2],uv[3]))
def palette(faction):
 name=TEXTURES[faction];p=TMP/name
 if not p.exists():urllib.request.urlretrieve("https://raw.githubusercontent.com/beyond-all-reason/Beyond-All-Reason/master/unittextures/"+name,p)
 image=Image.open(p).convert("RGB");W,T=image.size
 thumb=image.copy();thumb.thumbnail((512,512));w,h=thumb.size
 data=[]
 for y in range(8,h-20,12):
  for x in range(8,w-20,12):
   st=ImageStat.Stat(thumb.crop((x,y,x+12,y+12)))
   rgb=st.mean;v=sum(st.var)**.5/3;b=sum(rgb)/3
   if 38<b<201 and v<38:data.append((x,y,rgb,v,b))
 assert len(data)>50,(name,len(data))
 goals={'arm':(111,122,148),'cor':(117,99,96),'leg':(123,104,82)}
 def quality(a,k):
  x,y,c,v,b=a;r,g,blue=c
  if k=='armor':return sum((c[i]-goals[faction][i])**2 for i in range(3))**.5+abs(v-14)*.4
  if k=='metal':return abs(b-133)+abs(max(c)-min(c))*0.8
  if k=='dark':return abs(b-57)+abs(v-10)*.4
  if faction=='arm':return max(0,r-blue)*4+max(0,g-blue)*2+abs(b-135)*.4
  if faction=='cor':return max(0,g-r)*4+max(0,blue-r)*3+abs(b-135)*.4
  return max(0,r-g)*3+max(0,blue-g)*3+abs(b-130)*.4
 found={}
 for k in ('armor','metal','dark','glow'):
  ranked=sorted(data,key=lambda a:quality(a,k))
  picked=next((a for a in ranked if all(abs(a[0]-q[0])>24 or abs(a[1]-q[1])>24 for q in found.values())),ranked[0])
  found[k]=picked
 uv={}
 for k,(x,y,_,_,_) in found.items():
  X=x*W/w;Y=y*T/h;sz=12*W/w;side=12*T/h
  uv[k]=(( (X+6)/W,1-(Y+6)/T),((X+sz-6)/W,1-(Y+6)/T),((X+sz-6)/W,1-(Y+side-6)/T),((X+6)/W,1-(Y+side-6)/T))
 print("Atlas selected",faction,{k:(v[0],v[1]) for k,v in found.items()},flush=True)
 return uv
def cyl(p,rlo,rhi,lo,hi,t,n=12):
 for i in range(n):
  a=2*math.pi*i/n;b=2*math.pi*(i+1)/n;u=(math.cos(a),math.sin(a));v=(math.cos(b),math.sin(b))
  p.quad((rlo*u[0],lo,rlo*u[1]),(rlo*v[0],lo,rlo*v[1]),(rhi*v[0],hi,rhi*v[1]),(rhi*u[0],hi,rhi*u[1]),t)
  p.tri(((0,hi,0),(rhi*u[0],hi,rhi*u[1]),(rhi*v[0],hi,rhi*v[1])),t[:3])
def ring(p,r,q,y,t,n=32,m=8):
 for i in range(n):
  a=2*math.pi*i/n;b=2*math.pi*(i+1)/n
  for j in range(m):
   f=2*math.pi*j/m;g=2*math.pi*(j+1)/m
   def at(angle,phi):return ((r+q*math.cos(phi))*math.cos(angle),y+q*math.sin(phi),(r+q*math.cos(phi))*math.sin(angle))
   p.quad(at(a,f),at(b,f),at(b,g),at(a,g),t)
def box(p,x,y,z,dx,dy,dz,t):
 pts=[(x+sx*dx,y+sy*dy,z+sz*dz) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 for a,b,c,d in [(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]:p.quad(pts[a],pts[b],pts[c],pts[d],t)
def beam(p,a,b,r,t):
 v=[b[i]-a[i] for i in range(3)];l=math.sqrt(sum(x*x for x in v)) or 1;v=[x/l for x in v]
 h=(0,1,0) if abs(v[1])<.88 else (1,0,0)
 cross=lambda u,w:(u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0])
 u=cross(v,h);nl=math.sqrt(sum(x*x for x in u));u=[x/nl for x in u];w=cross(v,u)
 def corner(c,j):return tuple(c[i]+r*(u[i]*math.cos(j*math.pi/2)+w[i]*math.sin(j*math.pi/2)) for i in range(3))
 for j in range(4):p.quad(corner(a,j),corner(a,(j+1)%4),corner(b,(j+1)%4),corner(b,j),t)
def build(f):
 t=palette(f);a=t['armor'];d=t['dark'];m=t['metal'];g=t['glow']
 base=Piece("base");rotor=base.child("rotor");core=base.child("core");pulse=base.child("pulse");base.child("emit",(0,44,0))
 if f=='arm':
  cyl(base,43,47,-3,7,d);cyl(base,47,37,7,16,a);cyl(base,26,23,16,43,m)
  cyl(core,17,15,18,59,g,16);ring(rotor,24,2.5,48,m);ring(rotor,24,1.4,51,g)
  for i in range(4):
   th=i*math.pi/2;x=math.cos(th);z=math.sin(th)
   box(base,34*x,15,34*z,9,7,9,a)
   beam(base,(23*x,40,23*z),(40*x,15,40*z),3.7,m)
   beam(pulse,(20*x,49,20*z),(27*x,30,27*z),2,g)
   box(base,35*x,23,35*z,3,3,3,g)
 elif f=='cor':
  cyl(base,46,47,-3,10,d,8);cyl(base,47,37,10,20,a,8);cyl(base,32,27,20,49,m,8)
  cyl(core,17,19,22,61,g,12);ring(rotor,26,3,53,d,16);ring(rotor,26,1.6,57,g,16)
  for i in range(6):
   th=i*math.pi/3;x=math.cos(th);z=math.sin(th)
   beam(base,(39*x,12,39*z),(28*x,48,28*z),4.5,a)
   box(base,37*x,17,37*z,5,7,5,m)
   beam(pulse,(21*x,28,21*z),(21*x,51,21*z),2.3,g)
 else:
  cyl(base,43,47,-3,8,d);cyl(base,47,38,8,19,a);cyl(base,30,21,19,52,m)
  cyl(core,15,17,22,62,g,16);ring(rotor,25,3,55,a);ring(rotor,25,1.3,58,g);ring(rotor,30,1.7,48,m)
  for i in range(6):
   th=i*math.pi/3;x=math.cos(th);z=math.sin(th)
   beam(base,(38*x,13,38*z),(23*x,49,23*z),3.6,a)
   box(base,34*x,16,34*z,4,7,4,d)
  for i in range(8):
   th=i*math.pi/4;box(rotor,26*math.cos(th),55,26*math.sin(th),2,2,2,g)
 return base
def save(f,root):
 path=OUT/(f+'uwafus.s3o');buf=bytearray(b'\0'*H.size)
 def align():
  while len(buf)%4:buf.append(0)
 def string(s):
  off=len(buf);buf.extend(s.encode()+b'\0');return off
 def write(p):
  align();off=len(buf);buf.extend(b'\0'*P.size);nm=string(p.name)
  vo=io=0
  if p.v:
   align();vo=len(buf)
   for v in p.v:buf.extend(V.pack(*v))
  if p.idx:
   align();io=len(buf);buf.extend(struct.pack('<'+'I'*len(p.idx),*p.idx))
  children=[write(c) for c in p.children];ch=0
  if children:
   align();ch=len(buf);buf.extend(struct.pack('<'+'I'*len(children),*children))
  P.pack_into(buf,off,nm,len(children),ch,len(p.v),vo,0,0,len(p.idx),io,0,*p.off)
  return off
 ro=write(root);c1=string(TEXTURES[f]);c2=string({'arm':'Arm_other.dds','cor':'cor_other.dds','leg':'leg_shader.dds'}[f])
 H.pack_into(buf,0,b'Spring unit\0',0,75,85,0,36,0,ro,0,c1,c2)
 path.write_bytes(buf)
 # Verify S3O is playable with closed indices, engine-visible surfaces and all script pieces.
 import math
 names=[];count=0;extent=[]
 def verify(off,origin=(0,0,0)):
  nonlocal count
  v=P.unpack_from(buf,off);nm=buf[v[0]:buf.index(b'\0',v[0])].decode();names.append(nm)
  pos=[origin[i]+v[10+i] for i in range(3)]
  verts=[V.unpack_from(buf,v[4]+i*V.size) for i in range(v[3])]
  idx=struct.unpack_from('<'+'I'*v[7],buf,v[8]) if v[7] else []
  assert v[6]==0 and len(idx)%3==0 and all(i<len(verts) for i in idx)
  assert all(0<=q[6]<=1 and 0<=q[7]<=1 for q in verts)
  count+=len(idx)//3
  extent.extend(tuple(q[i]+pos[i] for i in range(3)) for q in verts)
  if v[1]:
   for ch in struct.unpack_from('<'+'I'*v[1],buf,v[2]):verify(ch,pos)
 verify(ro)
 assert set(names)=={'base','core','rotor','pulse','emit'},names
 assert count>750,count
 assert all(max(q[i] for q in extent)-min(q[i] for q in extent)<=105 for i in (0,2))
 print('Validated',path,'faces',count,'bytes',len(buf),'parts',names,flush=True)
if __name__=='__main__':
 for faction in ('arm','cor','leg'):save(faction,build(faction))
