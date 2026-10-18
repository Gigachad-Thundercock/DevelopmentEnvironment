import bpy,sys,os,math,importlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,'/tmp/python_addons')
kit=importlib.import_module('s3o_kit');kit.register()
bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.device='CPU';bpy.context.scene.cycles.samples=12
bpy.context.scene.render.resolution_x=840;bpy.context.scene.render.resolution_y=840
bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.render.image_settings.file_format='PNG'
scene=bpy.context.scene;scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.3,.3,.3,1);bg.inputs['Strength'].default_value=0.85
for f in ['arm','cor','leg']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 src=Path('NavalAfus/objects3d/Units')/(f+'uwafus.s3o')
 assert src.is_file(),src
 result=bpy.ops.s3o_tools.import_s3o(filepath=str(src.resolve()),unit_textures_folder='/tmp/afus-atlas',merge_vertices=False)
 assert 'FINISHED' in result,result
 mesh=[o for o in bpy.data.objects if o.type=='MESH']
 assert len(mesh)>=3,[(o.name,o.type) for o in bpy.data.objects]
 for im in bpy.data.images:
  if im.name.lower().startswith((f+'_','arm_')) and im.name.lower().endswith('.dds'):
   match=Path('/tmp/afus-atlas')/im.name
   if match.is_file():
    im.filepath=str(match);im.reload();im.pack()
 # camera
 camd=bpy.data.cameras.new('Preview');cam=bpy.data.objects.new('Preview',camd);scene.collection.objects.link(cam)
 camd.type='ORTHO';camd.ortho_scale=138;cam.location=(118,106,146)
 target=Vector((0,24,0));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
 for i,loc in enumerate(((70,125,85),(-70,85,-35),(35,150,-60))):
  ld=bpy.data.lights.new('Softbox','AREA');lo=bpy.data.objects.new('Softbox',ld);scene.collection.objects.link(lo)
  lo.location=loc;ld.energy=24000;ld.size=95;lo.rotation_euler=(target-lo.location).to_track_quat('-Z','Y').to_euler()
 out=Path('/tmp/naval_afus_preview_'+f+'.png');scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
 print('RENDERED_NAVAL_AFUS',f,out.stat().st_size,flush=True)
