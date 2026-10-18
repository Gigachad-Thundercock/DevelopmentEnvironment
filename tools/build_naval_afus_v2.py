#!/usr/bin/env python3
"""Naval AFUS II: independent faction naval fusion architecture on STOCK naval hulls.

ONLY writes NavalAfus/objects3d/Units/{arm,cor,leg}uwafus.s3o.
Uses real underwater fusion donor hulls/textures from BAR. Never edits unitdefs.
S3O geometry is authored from scratch above the foundation, NOT a scaled land AFUS.
"""
import math,os,sys,copy,random,collections
from pathlib import Path
sys.path.insert(0,"tools")
from build_naval_afus_models import (load,download,clone_tree,transform_tree,bounds,Model,
    Piece as S3Piece,save,recalc_model,walk)
from build_original_naval_afus import Piece as GeoPiece,box,cyl,ring,beam,palette

OUT=Path("NavalAfus/objects3d/Units")
OUT.mkdir(parents=True,exist_ok=True)

DONORS={'arm':'armuwfus.s3o','cor':'coruwfus.s3o','leg':'leganavalfusion.s3o'}
TEX={'arm':('Arm_color.dds','Arm_other.dds'),
     'cor':('cor_color.dds','cor_other.dds'),
     'leg':('leg_color.dds','leg_shader.dds')}
# Keep the footprint and total dimensions of existing naval AFUS as measured;
# this build is constrained by envelope of originals and actual 6x6 unitdefs.
LIMIT_XZ=104.0
HEIGHT_MAX=85.0
def convert(geo):
 p=S3Piece(geo.name,geo.off,list(geo.v),list(geo.idx),0,0,[])
 p.children=[convert(c) for c in geo.children]
 return p
def merge_geopiece(dst,src):
 for v in src.v:dst.v.append(v)
 delta=len(dst.v)-len(src.v)
 dst.idx.extend([i+delta for i in src.idx])
def component(name):
 return GeoPiece(name)
def new_base(f):
 t=palette(f)
 hull_model=load(download(DONORS[f]))
 # Original model authentic underwater-fusion body, with all its UVs intact.
 donor=clone_tree(hull_model.root,"hull_")
 b=bounds(donor)
 dx=b[1]-b[0];dz=b[5]-b[4]
 # Retain original hull profile rather than blind scaling the original fused tower.
 sx=94.0/max(dx,1.0);sz=94.0/max(dz,1.0)
 transform_tree(donor,sx,1.0,sz)
 b=bounds(donor)
 # Keep hull under 40 so advanced reactor can be visibly distinct.
 # If donor is tall, compress height moderately while preserving vertical shape.
 if b[3]-b[2]>43:
  transform_tree(donor,1,43/(b[3]-b[2]),1)
  b=bounds(donor)
 # Grounded at model origin: bottom of hull = 0; original stock appearance preserved.
 donor.offset=(donor.offset[0]-(b[0]+b[1])/2,-b[2]+donor.offset[1],
              donor.offset[2]-(b[4]+b[5])/2)
 b=bounds(donor)
 top=b[3]
 print('HULL',f,'span',round(b[1]-b[0],2),round(b[5]-b[4],2),'height',round(top,2),flush=True)
 root=S3Piece("base",children=[donor],primitive=0)
 # All newly authored visible parts are kept in clearly named pieces for UV/art iteration.
 parts={name:GeoPiece(name) for name in ('structure','armor','mechanism','lights','rotor','core','pulse')}
 # The visual rotor assembly rotates, core and pulse do not.
 return t,root,parts,top

def ringshell(p,r_inner,r_outer,y_bottom,y_top,uv,n=32):
 # Actual annular structural plate with open central aperture; not capped disc.
 for k in range(n):
  a=2*math.pi*k/n;b=2*math.pi*(k+1)/n
  ca,sa=math.cos(a),math.sin(a);cb,sb=math.cos(b),math.sin(b)
  q=lambda rr,yy,c,s:(rr*c,yy,rr*s)
  # Top, underside, inner/outer walls.
  p.quad(q(r_inner,y_top,ca,sa),q(r_inner,y_top,cb,sb),q(r_outer,y_top,cb,sb),q(r_outer,y_top,ca,sa),uv)
  p.quad(q(r_outer,y_bottom,ca,sa),q(r_outer,y_bottom,cb,sb),q(r_inner,y_bottom,cb,sb),q(r_inner,y_bottom,ca,sa),uv)
  p.quad(q(r_outer,y_top,ca,sa),q(r_outer,y_top,cb,sb),q(r_outer,y_bottom,cb,sb),q(r_outer,y_bottom,ca,sa),uv)
  p.quad(q(r_inner,y_bottom,ca,sa),q(r_inner,y_bottom,cb,sb),q(r_inner,y_top,cb,sb),q(r_inner,y_top,ca,sa),uv)

def tapered_column(p,x,z,ylo,yhi,wide,narrow,uv):
 # Closed panelled obelisk, firmly rooted in hull deck and structurally joined to reactor collar.
 for j in range(4):
  ang=j*math.pi/2;an=(j+1)*math.pi/2
  a=(x+wide*math.cos(ang),ylo,z+wide*math.sin(ang))
  b=(x+wide*math.cos(an),ylo,z+wide*math.sin(an))
  c=(x+narrow*math.cos(an),yhi,z+narrow*math.sin(an))
  d=(x+narrow*math.cos(ang),yhi,z+narrow*math.sin(ang))
  p.quad(a,b,c,d,uv)
 box(p,x,ylo,z,wide*.85,1.2,wide*.85,uv)

def hex_cage(p,rlo,rhi,y0,y1,uv,n=6):
 for k in range(n):
  th=2*math.pi*k/n;ph=2*math.pi*(k+1)/n
  # upper/lower longitudinal rails with bridges
  a=(rlo*math.cos(th),y0,rlo*math.sin(th))
  b=(rhi*math.cos(th),y1,rhi*math.sin(th))
  beam(p,a,b,2.9,uv)
  beam(p,b,(rhi*math.cos(ph),y1,rhi*math.sin(ph)),2.1,uv)

def fins(p,rlo,rhi,yl,yh,number,uv):
 for k in range(number):
  ang=2*math.pi*k/number
  c,s=math.cos(ang),math.sin(ang)
  v=(-s,c)
  # slab is radial from supporting wall and has a beveled end in silhouette
  for dx in (-1,1):
   b=(rlo*c+v[0]*dx*2,yl,rlo*s+v[1]*dx*2)
   e=(rhi*c+v[0]*dx*2,yh,rhi*s+v[1]*dx*2)
   beam(p,b,e,1.1,uv)

def build_arm(parts,top,t):
 a=t['armor'];m=t['metal'];d=t['dark'];g=t['glow']
 # Armada - precise symmetric white-blue reactor with modular navy engineering,
 # four slab outriggers, open anti-pressure cage and double toroidal drive.
 ringshell(parts['structure'],17,27,top-2,top+2,m)
 cyl(parts['mechanism'],17,14,top+1,top+26,d,16)
 cyl(parts['core'],11,10,top+3,top+31,g,24)
 ringshell(parts['rotor'],13,17,top+24,top+29,a)
 ringshell(parts['rotor'],19,22,top+17,top+20,m)
 ringshell(parts['lights'],11,12.5,top+28,top+31,g)
 for i in range(4):
  an=math.pi/4+i*math.pi/2;c,s=math.cos(an),math.sin(an)
  x,z=31*c,31*s
  tapered_column(parts['armor'],x,z,top-5,top+22,6.5,3.5,a)
  beam(parts['structure'],(x,top+18,z),(15*c,top+29,15*s),3,m)
  beam(parts['mechanism'],(x,top+3,z),(20*c,top+11,20*s),2,d)
  box(parts['lights'],x,top+17,z,2,1.2,2,g)
 # Four armored module housings with actual recessed dark slots
 for x,z in [(-24,0),(24,0),(0,-24),(0,24)]:
  box(parts['armor'],x,top-1,z,5,5,8,a)
  box(parts['mechanism'],x,top+4,z,3.8,1.6,5.5,d)
 hex_cage(parts['structure'],15,15,top+4,top+27,m,n=8)
 for i in range(8):
  th=i*math.pi/4
  box(parts['lights'],22*math.cos(th),top+19,22*math.sin(th),1,1.1,1,g)
 # linked exposed coil in lower reactor chamber
 for yy in (top+6,top+10,top+14):
  ringshell(parts['pulse'],11.3,12.0,yy,yy+0.7,g,20)

def build_cor(parts,top,t):
 a=t['armor'];m=t['metal'];d=t['dark'];g=t['glow']
 # Cortex - industrial six-sided pressure vessel, angular reactor shields,
 # concentrated crimson energy channels rather than delicate floating rings.
 ringshell(parts['structure'],20,32,top-3,top+2,d,n=12)
 cyl(parts['mechanism'],21,18,top,top+28,a,n=8)
 cyl(parts['core'],13,15,top+4,top+35,g,n=12)
 ringshell(parts['rotor'],19,23,top+27,top+32,d,n=12)
 ringshell(parts['rotor'],15,18,top+32,top+35,m,n=12)
 ringshell(parts['lights'],13,15,top+34,top+37,g,n=12)
 for i in range(6):
  th=i*math.pi/3;c,s=math.cos(th),math.sin(th)
  x,z=29*c,29*s
  tapered_column(parts['armor'],x,z,top-6,top+25,7.0,4.5,a)
  beam(parts['structure'],(x,top+24,z),(17*c,top+32,17*s),4.0,m)
  beam(parts['mechanism'],(x,top+5,z),(23*c,top+16,23*s),2.3,d)
  box(parts['lights'],x,top+21,z,1.4,3.8,1.4,g)
  box(parts['mechanism'],32*c,top+7,32*s,3.5,5.0,3.5,d)
 hex_cage(parts['structure'],22,22,top+2,top+26,a,n=6)
 # Industrial compression-stack stripes, not atlas-filling squares
 for yy in (top+9,top+13,top+17,top+21):
  ringshell(parts['pulse'],13.7,14.8,yy,yy+.6,g,16)
 for zz in (-11,11):
  box(parts['armor'],0,top+4,zz,9,3.2,3.4,a)
  box(parts['mechanism'],0,top+8,zz,7,2.2,2.4,d)

def build_leg(parts,top,t):
 a=t['armor'];m=t['metal'];d=t['dark'];g=t['glow']
 # Legion - heavy bronze-gray forged reactor with six segmented stanchions,
 # hexagonal hub, recessed emerald conduits and divided concentric gimbals.
 ringshell(parts['structure'],20,34,top-2,top+2,a,n=24)
 cyl(parts['mechanism'],20,17,top+1,top+28,d,n=12)
 cyl(parts['core'],11,13,top+5,top+35,g,n=16)
 ringshell(parts['rotor'],18,23,top+28,top+32,a,n=24)
 ringshell(parts['rotor'],14,17,top+34,top+37,m,n=24)
 ringshell(parts['lights'],12,14,top+34,top+37,g,n=24)
 for i in range(6):
  an=i*math.pi/3;c,s=math.cos(an),math.sin(an)
  x,z=29*c,29*s
  tapered_column(parts['armor'],x,z,top-5,top+27,6.7,3.7,a)
  beam(parts['structure'],(x,top+27,z),(17*c,top+33,17*s),3.0,m)
  beam(parts['mechanism'],(x,top+8,z),(19*c,top+21,19*s),2.0,d)
  box(parts['lights'],27*c,top+18,27*s,1.2,4.0,1.2,g)
  box(parts['armor'],x,top+1,z,5.0,2.0,5.0,a)
 hex_cage(parts['structure'],20,20,top+5,top+28,m,n=6)
 # Contrasting machinery/radiator shields at the outer rim
 fins(parts['armor'],27,38,top+3,top+14,12,a)
 for yy in (top+11,top+16,top+21,top+26):
  ringshell(parts['pulse'],12.0,13.0,yy,yy+0.7,g,24)
 for i in range(12):
  th=i*math.pi/6
  box(parts['lights'],33*math.cos(th),top+3,33*math.sin(th),1.5,1.2,1.5,g)

BUILDERS={'arm':build_arm,'cor':build_cor,'leg':build_leg}
def validate_s3o(path):
 m=load(str(path));names={p.name for p in walk(m.root)}
 needed={'base','rotor','core','pulse','emit'}
 if not needed.issubset(names):raise RuntimeError((path,'missing',needed-names))
 b=bounds(m.root)
 span=(b[1]-b[0],b[5]-b[4]);height=b[3]-b[2]
 if span[0]>LIMIT_XZ or span[1]>LIMIT_XZ or height>HEIGHT_MAX:
  raise RuntimeError((path,'model envelope',span,height))
 faces=0
 for p in walk(m.root):
  if p.indices:
   assert len(p.indices)%3==0,(path,p.name)
   assert max(p.indices)<len(p.verts),(path,p.name)
   assert all((-0.02<=v[6]<=1.02 and -0.02<=v[7]<=1.02) if p.name.startswith('hull_') else (0<=v[6]<=1 and 0<=v[7]<=1) for v in p.verts),(path,p.name)
   faces+=len(p.indices)//3
 assert faces>1300,(path,'insufficient geometry',faces)
 print('MODEL_VALID',path,'faces',faces,'span',span,'height',height,'pieces',len(names))
 return m
def build(f):
 textures,root,parts,top=new_base(f)
 BUILDERS[f](parts,top,textures)
 # The actual visual geometry is organized into independently editable pieces.
 # zero-geometry top-level pivots exactly match the new animation script pieces.
 for name in ('structure','armor','mechanism','lights','core','pulse','rotor'):
  root.children.append(convert(parts[name]))
 root.children.append(S3Piece('emit',(0,top+31,0),[],[],primitive=0))
 model=Model(70,78,(0,32,0),*TEX[f],root)
 recalc_model(model)
 dest=OUT/(f+'uwafus.s3o')
 save(model,str(dest))
 validate_s3o(dest)
 print('NAVAL_ADVANCED_FUSION_CREATED',f,dest,dest.stat().st_size)
if __name__=='__main__':
 for faction in ('arm','cor','leg'):build(faction)
