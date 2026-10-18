from PIL import Image,ImageDraw
from pathlib import Path
src=Path('/tmp/afus-atlas')
colors={'arm':('Arm_color.dds',{'armor':(368,44),'metal':(128,236),'dark':(236,344),'glow':(116,20)}),
'cor':('cor_color.dds',{'armor':(260,8),'metal':(80,236),'dark':(236,68),'glow':(20,200)}),
'leg':('leg_color.dds',{'armor':(164,488),'metal':(8,20),'dark':(80,32),'glow':(8,368)})}
for f,(name,points) in colors.items():
 im=Image.open(src/name).convert('RGB')
 im.thumbnail((1024,1024));d=ImageDraw.Draw(im)
 for label,(x,y) in points.items():
  fx=x*im.width/512;fy=y*im.height/512
  d.rectangle((fx,fy,fx+24,fy+24),outline='white',width=3)
  d.text((fx,fy),label,fill='yellow',stroke_width=1,stroke_fill='black')
 out=Path('/tmp/naval_afus_atlas_'+f+'.png')
 im.save(out)
 print('ATLAS_SHEET',f,im.size,out.stat().st_size)
