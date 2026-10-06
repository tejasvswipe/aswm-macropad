import bpy, math, os
from mathutils import Vector

OUT = os.path.abspath(os.path.dirname(__file__))
# Clear scene
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials: bpy.data.materials.remove(d)

# Materials for the presentation assembly only

def mat(name, color, metallic=0.0, rough=0.35):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metallic; p.inputs['Roughness'].default_value=rough
    return m
case_mat=mat('Graphite polymer',(0.055,0.075,0.12),0.12)
plate_mat=mat('Warm light plate',(0.78,0.82,0.84),0.08)
accent_mat=mat('Hack Club orange accent',(1.0,0.27,0.035),0.15)
pcb_mat=mat('PCB proxy',(0.025,0.32,0.22),0.1)
key_mat=mat('Keycap proxy',(0.9,0.92,0.95),0.0)
metal_mat=mat('Fasteners',(0.5,0.54,0.58),0.75)

# Helpers

def rounded_box(name, dims, loc, radius, material=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    b=o.modifiers.new('Soft radiused edges','BEVEL'); b.width=radius; b.segments=8; b.profile=0.5
    o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=b.name)
    if material: o.data.materials.append(material)
    return o

def cyl(name, r, depth, loc, material=None, vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=r, depth=depth, location=loc); o=bpy.context.object; o.name=name
    if material: o.data.materials.append(material)
    return o

def difference(target, cutter, name):
    bpy.context.view_layer.objects.active=target
    m=target.modifiers.new(name,'BOOLEAN'); m.operation='DIFFERENCE'; m.object=cutter
    bpy.ops.object.modifier_apply(modifier=m.name); bpy.data.objects.remove(cutter, do_unlink=True)

def union(target, other, name):
    bpy.context.view_layer.objects.active=target
    m=target.modifiers.new(name,'BOOLEAN'); m.operation='UNION'; m.object=other
    bpy.ops.object.modifier_apply(modifier=m.name); bpy.data.objects.remove(other, do_unlink=True)

def export_stl(obj, filename):
    # Export a duplicate grounded at Z=0 for easy direct slicing; retain the assembly placement in the .blend.
    dup=obj.copy(); dup.data=obj.data.copy(); bpy.context.collection.objects.link(dup); dup.name='PRINT EXPORT | '+filename
    min_z=min((dup.matrix_world @ Vector(corner)).z for corner in dup.bound_box); dup.location.z-=min_z
    bpy.ops.object.select_all(action='DESELECT'); dup.select_set(True); bpy.context.view_layer.objects.active=dup
    bpy.ops.wm.stl_export(filepath=os.path.join(OUT,filename), export_selected_objects=True)
    bpy.data.objects.remove(dup,do_unlink=True)

# Guide dimensions: 100 mm PCB, 0.2 mm clearance per side, 10 mm case border,
# 3 mm tray floor, 10 mm wall, and 3 mm sandwich top plate.
board=100.0; clearance=0.2; margin=10.0; outer=board+2*margin
floor=3.0; wall=10.0; base_h=floor+wall; plate_z=base_h; plate_t=3.0
holes=[(15,15),(105,35),(18,94),(105,105)]
keys=[(30+19.05*c,41+19.05*r) for r in range(4) for c in range(4)]
encoder=(87,18)
usb_x=35.0

# Tray outer shell and PCB pocket. Build at origin so parts lie flat for printing.
base=rounded_box('01 | Lower tray (120 x 120)',(outer,outer,base_h),(60,60,base_h/2),7,case_mat)
pocket=rounded_box('pocket cutter',(100+2*clearance,100+2*clearance,wall+1),(60,60,floor+(wall+1)/2),3.5)
difference(base,pocket,'PCB pocket | 0.2 mm each side')
# Standoffs match this board's irregular hole pattern; 2.7 mm pilot holes.
for i,(x,y) in enumerate(holes):
    boss=cyl('standoff',(7.4/2),8.0,(x,y,7.0),case_mat)
    union(base,boss,'integrated PCB standoff')
    bore=cyl('pilot',(2.7/2),8.3,(x,y,7.0),None,64); difference(base,bore,'M3 self-tapping pilot')
# XIAO USB-C side opening at front edge.
cut=rounded_box('USB opening cutter',(16,12,8.4),(usb_x,4.5,9.4),1.2); difference(base,cut,'USB-C cable opening')
# Underside 24 mm service opening + four M2 cover screw pilots.
cut=rounded_box('service hatch cutter',(24,24,4),(35,22,1.5),2); difference(base,cut,'underside BOOT RESET access')
for dx in (-15,15):
    for dy in (-15,15):
        difference(base,cyl('hatch pilot cutter',0.9,3.5,(35+dx,22+dy,1.5),None,48),'M2 hatch screw pilot')
base.data.materials.clear(); base.data.materials.append(case_mat)

# Top sandwich plate, printable flat. PCB holes include countersink pockets on top.
plate=rounded_box('02 | Switch plate (120 x 120 x 3)',(outer,outer,plate_t),(60,60,plate_z+plate_t/2),7,plate_mat)
for x,y in keys:
    cut=rounded_box('MX switch opening',(14.4,14.4,plate_t+2),(x,y,plate_z+plate_t/2),0.25)
    difference(plate,cut,'14.4 mm MX opening')
# EC11 shaft, bezel recess and board fasteners.
difference(plate,cyl('encoder cutter',3.7,plate_t+2,(encoder[0],encoder[1],plate_z+plate_t/2),None),'EC11 shaft opening')
ringcut=cyl('ring recess outer',10,0.9,(encoder[0],encoder[1],plate_z+plate_t-0.4),None)
ringinner=cyl('ring recess inner',8.15,1.2,(encoder[0],encoder[1],plate_z+plate_t-0.4),None)
difference(ringcut,ringinner,'ring cutter annulus')
difference(plate,ringcut,'flush accent ring recess')
for x,y in holes:
    difference(plate,cyl('M3 clearance',1.7,plate_t+2,(x,y,plate_z+plate_t/2),None,64),'M3 through hole')
    difference(plate,cyl('head counterbore',3.0,0.9,(x,y,plate_z+plate_t-0.4),None,64),'flush screw counterbore')
# USB notch through front edge.
cut=rounded_box('USB notch cutter',(16,12,plate_t+2),(usb_x,4.5,plate_z+plate_t/2),1.0); difference(plate,cut,'USB-C edge notch')
# Badge inset near rear edge and subtle side-line accent grooves.
badge_recess=rounded_box('badge recess cutter',(44,10,0.9),(60,112,plate_z+plate_t-0.35),1.2); difference(plate,badge_recess,'removable name badge pocket')
# Counterbore and notch edges deburr-safe via small bevels inherent to cut layout.

# Separate hatch: 34 mm cover over 24 mm opening, M2 clearance holes.
hatch=rounded_box('03 | Service hatch',(34,34,1.8),(35,22,0.9),3,case_mat)
for dx in (-15,15):
    for dy in (-15,15):
        difference(hatch,cyl('M2 clearance',1.1,2.4,(35+dx,22+dy,0.9),None,48),'M2 hatch clearance')
# Shallow inset panel line.
panel_outer=rounded_box('panel groove outer',(30,30,0.45),(35,22,1.62),2.5)
panel_inner=rounded_box('panel groove inner',(27,27,0.7),(35,22,1.62),2.0)
difference(panel_outer,panel_inner,'panel groove ring'); difference(hatch,panel_outer,'hatch inset line')

# Encoder opening is 7.4 mm for the nominal 7 mm EC11 bushing (0.2 mm radial print clearance). The wider bezel bore leaves side clearance for a knob that can be pressed.
bezel=cyl('04 | Encoder accent bezel',9.9,0.58,(encoder[0],encoder[1],plate_z+plate_t-0.62+0.29),accent_mat)
difference(bezel,cyl('bezel bore',8.5,1.0,(encoder[0],encoder[1],plate_z+plate_t-0.62+0.29),None),'encoder bezel opening')
# Separate removable badge with raised Hackpad 16 label.
badge=rounded_box('05 | Hackpad 16 badge',(43.6,9.6,0.68),(60,112,plate_z+plate_t-0.72+0.34),1.0,accent_mat)
# Text mesh is separate but overlaps badge base and is joined for single-piece export.
curve=bpy.data.curves.new('Tejas got not chill | Hackpad raised lettering','FONT'); curve.body='Tejas got not chill'+chr(10)+'Hackpad'; curve.size=3.1; curve.extrude=0.18; curve.align_x='CENTER'; curve.align_y='CENTER'
txt=bpy.data.objects.new('Tejas got not chill | Hackpad raised lettering',curve); bpy.context.collection.objects.link(txt); txt.location=(60,112,plate_z+plate_t-0.72+0.68)
bpy.context.view_layer.objects.active=txt; txt.select_set(True); bpy.ops.object.convert(target='MESH'); txt=bpy.context.object
badge.select_set(True); bpy.context.view_layer.objects.active=badge; bpy.ops.object.join(); badge=bpy.context.object; badge.name='05 | Tejas got not chill | Hackpad badge'

# Save production-ready STL pieces (individual, correctly oriented print pieces).
for ob in list(bpy.context.scene.objects): ob.select_set(False)
export_stl(base,'lower_tray.stl'); export_stl(plate,'switch_plate.stl'); export_stl(hatch,'service_hatch.stl'); export_stl(bezel,'encoder_bezel.stl'); export_stl(badge,'hackpad16_badge.stl')

# Rename and collection organize source file. Add clearly marked visualization proxies.
assembly=bpy.data.collections.new('ASSEMBLY | visual proxies (not for printing)'); bpy.context.scene.collection.children.link(assembly)
def move_to(obj, coll):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    coll.objects.link(obj)
# Unhide parts in assembly and place base/plate at their designed z.
# They remain separated as named design parts in the editable blend.

# PCB proxy and key/encoder visual components at final assembled heights.
proxy=rounded_box('PROXY ONLY | 100 mm PCB',(100,100,1.6),(60,60,11.8),0.2,pcb_mat); move_to(proxy,assembly)
for i,(x,y) in enumerate(keys):
    sw=rounded_box('PROXY ONLY | switch %02d'%(i+1),(13.6,13.6,4.4),(x,y,14.8),1,key_mat); move_to(sw,assembly)
    cap=rounded_box('PROXY ONLY | keycap %02d'%(i+1),(14.2,14.2,5.5),(x,y,19.75),1.2,key_mat); move_to(cap,assembly)
knob=cyl('PROXY ONLY | press-to-click encoder knob',7.3,10,(encoder[0],encoder[1],22.5),metal_mat,48); move_to(knob,assembly)
# Assembly scene only; actual print objects retain their origin layouts.

# Aesthetic studio setup
world=bpy.context.scene.world or bpy.data.worlds.new('Studio world'); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(0.16,0.19,0.25,1); world.node_tree.nodes['Background'].inputs[1].default_value=1.2
for name,loc,power,size in [('Key',(20,-70,145),1700,85),('Fill',(130,35,105),1150,70),('Rim',(20,145,115),1400,55)]:
    bpy.ops.object.light_add(type='AREA', location=loc); l=bpy.context.object; l.name='Studio '+name; l.data.energy=power; l.data.shape='DISK'; l.data.size=size; l.rotation_euler=(Vector((60,60,8))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(205,-230,225)); cam=bpy.context.object; cam.name='Presentation camera'; cam.rotation_euler=(Vector((60,60,8))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=205; bpy.context.scene.camera=cam
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.render.resolution_x=1400; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=1.0; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(OUT,'hackpad16_case_preview.png')
# Display assembly: base, plate elevated modestly for edge reveal, proxies in place.
# Hide tray only from render? Show both parts assembled. Base lower at z0; plate existing at z13.
# Rename material and ensure presentation parts read clearly.
bpy.ops.object.select_all(action='DESELECT')
scene.render.film_transparent=False
bpy.ops.render.render(write_still=True)
# Export layout preview top plate too by hiding irrelevant objects is optional, and preserve editable .blend.
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'hackpad16_case.blend'))





