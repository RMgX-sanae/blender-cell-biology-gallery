"""Model a generic vertical clean bench. Run with Blender 5 in background mode."""

import argparse
import json
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SKILL = Path(os.environ.get("CELL_BIOLOGY_SKILL", Path.home() / ".codex/skills/blender-cell-biology"))
sys.path.insert(0, str(SKILL / "scripts"))
from detail_scene import linear, material


PARTS = {
    "Frame": ("机架与工作腔", [0, 0, 0]),
    "Worktop": ("工作面", [-0.32, 0.035, 1.25]),
    "Sash": ("透明前窗", [2.02, 0.12, 0.64]),
    "Filter": ("主过滤盒", [0.02, 0.46, 0.04]),
    "Blower": ("送风机组", [0.04, 0.97, -0.03]),
    "Prefilter": ("进风预滤网", [0.04, 1.50, -0.09]),
    "Hood": ("顶罩与控制面板", [-2.22, 0.57, 0.30]),
}
ORIGIN = (0, 0, 0)
roots = {}
parts = {}
materials = {}


def finish(obj, group, mat, edge=0):
    parts[group].objects.link(obj)
    obj.parent = roots[group]
    if mat:
        obj.data.materials.append(materials[mat])
    if edge:
        bevel = obj.modifiers.new("Fold and finish edges", "BEVEL")
        bevel.width = edge
        bevel.segments = 3
        bevel.harden_normals = True
        obj.modifiers.new("Planar face normals", "WEIGHTED_NORMAL")
    return obj


def mesh(group, name, vertices, faces, mat, edge=0):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    return finish(bpy.data.objects.new(name, data), group, mat, edge)


def box(group, name, loc, dims, mat, edge=0.008):
    x, y, z = (d / 2 for d in dims)
    vertices = [(a*x, b*y, c*z) for c in (-1,1) for b in (-1,1) for a in (-1,1)]
    faces = [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    obj = mesh(group, name, vertices, faces, mat, edge)
    obj.location = loc
    return obj


def beam(group, name, start, end, width, depth, mat, edge=0.005):
    start, end = Vector(start), Vector(end)
    obj = box(group, name, (start+end)/2, (width,depth,(end-start).length), mat, edge)
    obj.rotation_euler = (end-start).to_track_quat("Z","Y").to_euler()
    return obj


def cylinder(group, name, center, radius, height, mat, axis=(0,0,1), n=40, edge=0.002):
    points = [(radius*math.cos(i*math.tau/n),radius*math.sin(i*math.tau/n),z)
              for z in (-height/2,height/2) for i in range(n)]
    faces = [tuple(reversed(range(n))), tuple(range(n,2*n))]
    faces.extend((i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n))
    obj = mesh(group,name,points,faces,mat,edge)
    for poly in list(obj.data.polygons)[2:]:
        poly.use_smooth = True
    obj.location = center
    obj.rotation_euler = Vector(axis).to_track_quat("Z","Y").to_euler()
    return obj


def rounded(width, depth, radius, steps=5):
    pts = []
    for cx,cy,start in [(width/2-radius,depth/2-radius,0),(-width/2+radius,depth/2-radius,90),
                        (-width/2+radius,-depth/2+radius,180),(width/2-radius,-depth/2+radius,270)]:
        for i in range(steps+1):
            t = math.radians(start+90*i/steps)
            pts.append((cx+radius*math.cos(t),cy+radius*math.sin(t)))
    return pts


def rim(group, name, center, outer, inner, height, radii, mat, edge=0.004):
    outside = rounded(*outer,radii[0])
    inside = rounded(*inner,radii[1])
    loops = [(outside,-height/2),(outside,height/2),(inside,height/2),(inside,-height/2)]
    vertices = [(x,y,z) for loop,z in loops for x,y in loop]
    n = len(outside)
    faces = []
    for k in range(4):
        a, b = k*n, (k+1)%4*n
        faces.extend((a+i,a+(i+1)%n,b+(i+1)%n,b+i) for i in range(n))
    obj = mesh(group,name,vertices,faces,mat,edge)
    obj.location = center
    return obj


def annulus(group,name,loc,r_outer,r_inner,height,mat,axis=(0,0,1),n=60):
    vertices = [(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z)
                for r,z in [(r_outer,-height/2),(r_outer,height/2),(r_inner,height/2),(r_inner,-height/2)]
                for i in range(n)]
    faces = []
    for k in range(4):
        a,b=k*n,(k+1)%4*n
        faces.extend((a+i,a+(i+1)%n,b+(i+1)%n,b+i) for i in range(n))
    obj = mesh(group,name,vertices,faces,mat,0.0015)
    for p in obj.data.polygons:
        p.use_smooth = p.index < n or 2*n <= p.index < 3*n
    obj.location = loc
    obj.rotation_euler = Vector(axis).to_track_quat("Z","Y").to_euler()
    return obj


def side_panel(group, name, x, thickness, yz, mat, edge=0.008):
    # Polygon is counterclockwise when looking in the -X direction.
    if sum(y*z2-y2*z for (y,z),(y2,z2) in zip(yz, yz[1:]+yz[:1])) < 0:
        yz = list(reversed(yz))
    n = len(yz)
    vertices = [(x+dx,y,z) for dx in (-thickness/2,thickness/2) for y,z in yz]
    faces = [tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces.extend((i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n))
    return mesh(group,name,vertices,faces,mat,edge)


def lettering(group,name,words,loc,size,mat):
    curve = bpy.data.curves.new(name,"FONT")
    curve.body, curve.size, curve.space_character = words,size,1.12
    curve.resolution_u = 3
    curve.extrude = 0.00025
    obj = finish(bpy.data.objects.new(name,curve),group,mat)
    obj.rotation_euler.x = math.pi/2
    obj.location = loc
    return obj


def make_materials():
    palette = [
        ("shell","Cool white enamel","D6DFE5",.32,.15,.22),
        ("front","Porcelain white fascia","E8ECF0",.32,.13,.22),
        ("cobalt","Cobalt blue powder coat","2141A6",.33,.35,.14),
        ("navy","Deep navy trim","182D54",.30,.38,.12),
        ("boot","Gaskets","242C39",.49,.03,0),
        ("steel","Brushed stainless","B9C6CD",.31,.72,.08),
        ("alloy","Machined alloy","D7DDE1",.24,.72,.12),
        ("back","Work chamber enamel","D7E1E8",.38,.13,.13),
        ("paper","Pleated main medium","E0D7C0",.65,.03,0),
        ("coarse","Prefilter fleece","889CAC",.76,.02,0),
        ("glass","Low iron glazing","ADD1E4",.11,.06,.42),
        ("edge","Tinted glass edge","7199BD",.15,.18,.36),
        ("marker","Knob marker","BCD2EF",.34,.22,.15),
        ("dial","Gauge ground","E3E6E8",.48,.01,.04),
        ("light","Work light diffuser","F5F7F9",.28,.01,.12),
    ]
    for key,name,color,rough,metal,coat in palette:
        m = material(name,color,settings={"roughness":rough,"bump":0,"subsurface_weight":0})
        p = m.node_tree.nodes.get("Principled BSDF")
        p.inputs["Metallic"].default_value = metal
        p.inputs["Coat Weight"].default_value = coat
        if key == "glass":
            p.inputs["Alpha"].default_value = .135
            m.diffuse_color = (*linear(color),.135)
            m.surface_render_method = "BLENDED"
        elif key == "steel":
            p.inputs["Anisotropic"].default_value = .42
        elif key == "light":
            p.inputs["Emission Color"].default_value = (*linear(color),1)
            p.inputs["Emission Strength"].default_value = 1.3
        materials[key] = m


def build_frame():
    g = "Frame"
    for x in (-1.027,1.027):
        for y in (-.432,.439):
            cylinder(g,"Leveling pad",(x,y,.029),.089,.052,"boot")
            cylinder(g,"Foot adjuster",(x,y,.078),.035,.072,"alloy",n=16)
            cylinder(g,"Foot locknut",(x,y,.088),.052,.026,"alloy",n=6)
            box(g,"Leg",(x,y,.533),(.106,.103,.867),"cobalt",.017)
            box(g,"Leg socket",(x,y,.14),(.113,.11,.075),"navy",.008)
        box(g,"Stand side beam",(x,.006,.306),(.087,.879,.074),"cobalt",.013)
        box(g,"Stand side head",(x,.004,.915),(.11,1.04,.115),"navy",.012)
    box(g,"Rear foot rail",(0,.439,.297),(2.04,.085,.079),"cobalt",.013)
    box(g,"Rear stand beam",(0,.444,.91),(2.11,.12,.135),"navy",.012)
    box(g,"Front stand beam",(0,-.434,.926),(2.14,.11,.115),"navy",.014)
    rim(g,"Deck bearer",(0,-.012,.996),(2.41,1.179),(2.22,.995),.108,(.065,.036),"shell",.013)
    rim(g,"Apron isolation seal",(0,-.012,1.042),(2.342,1.122),(2.21,.98),.025,(.045,.03),"boot",.005)
    for x in (-.58,.58):
        box(g,"Table bearing rail",(x,-.01,1.002),(.055,1.08,.055),"steel",.007)
    box(g,"Cabinet back",(0,.511,1.671),(2.30,.070,1.176),"shell",.025)
    box(g,"Rear liner",(0,.466,1.643),(2.167,.036,1.086),"back",.025)
    # Two short grilles are separate stamped strips with a dark gap behind each bank.
    for xc in (-.723,.723):
        box(g,"Rear vent inset",(xc,.444,1.204),(.504,.019,.11),"navy",.013)
        for row in range(4):
            box(g,"Return louver",(xc,.427,1.163+.027*row),(.484,.026,.013),"steel",.005)
    for s in (-1,1):
        x = s*1.126
        # Broad rear return, sloped front rail and a glazed viewing aperture.
        side_panel(g,"Side return",x,.083,[(.365,1.04),(.554,1.04),(.554,2.258),(.38,2.258),(.318,2.17),(.345,1.17)],"cobalt",.014)
        side_panel(g,"Lower side sill",x,.085,[(-.543,1.055),(.491,1.055),(.493,1.19),(-.402,1.172),(-.535,1.139)],"shell",.012)
        side_panel(g,"Window head",x,.086,[(-.424,2.13),(.442,2.13),(.448,2.259),(-.439,2.259)],"cobalt",.013)
        side_panel(g,"Front guide",x,.084,[(-.539,1.079),(-.459,1.092),(-.351,2.24),(-.429,2.24)],"navy",.012)
        side_panel(g,"Glazed cheek",x,.018,[(-.489,1.15),(.379,1.16),(.375,2.166),(-.388,2.17)],"glass",.004)
        for y,z in [( .427,1.143),(.433,2.19),(-.475,1.146),(-.391,2.174)]:
            cylinder(g,"Glazing cap",(x+s*.047,y,z),.021,.014,"alloy",(s,0,0),n=20)
            cylinder(g,"Recess",(x+s*.054,y,z),.0068,.0015,"boot",(s,0,0),n=6,edge=0)
    box(g,"Ceiling frame back",(0,.438,2.208),(2.28,.147,.093),"navy",.013)


def build_worktop_and_sash():
    g = "Worktop"
    box(g,"Rolled stainless deck",(0,-.007,1.087),(2.347,1.158,.073),"steel",.029)
    box(g,"Turned front lip",(0,-.59,1.078),(2.262,.026,.035),"alloy",.012)
    box(g,"Rear upstand",(0,.521,1.137),(2.16,.048,.091),"steel",.014)
    for x in (-1.10,1.10):
        box(g,"Raised side rim",(x,-.003,1.125),(.043,1.027,.037),"steel",.014)
    g = "Sash"
    slope = .095
    midz = 1.986
    midy = -.459
    h = .478
    pane = box(g,"Sliding front glazing",(0,midy,midz),(2.17,.018,h),"glass",.005)
    pane.rotation_euler.x = -slope
    for sign in (-1,1):
        y = midy + sign*math.sin(slope)*h/2
        z = midz + sign*math.cos(slope)*h/2
        box(g,"Lower lift rail" if sign<0 else "Upper glazing channel",(0,y,z),
            (2.184,.047,.039 if sign<0 else .035),"navy",.009)
    for x in (-1.071,1.071):
        strip = box(g,"Polished glass edge",(x,midy,midz),(.007,.021,h-.029),"edge",.002)
        strip.rotation_euler.x = -slope
    box(g,"Lift rail finger grip",(0,-.509,1.736),(.53,.044,.034),"cobalt",.013)


def build_filter():
    g = "Filter"
    rim(g,"Main filter frame",(0,0,2.244),(2.167,1.035),(2.032,.924),.124,(.035,.018),"alloy")
    rim(g,"Seal upper",(0,0,2.308),(2.169,1.037),(2.093,.965),.018,(.033,.026),"boot")
    rim(g,"Seal lower",(0,0,2.179),(2.16,1.028),(2.072,.944),.013,(.032,.019),"cobalt")
    pleats(g,"Filter folds",2.03,.919,2.246,.077,64,"paper")
    for yy in (-.319,0,.319):
        box(g,"Face strip",(0,yy,2.284),(2.049,.010,.014),"alloy",.002)
        box(g,"Lower face strip",(0,yy,2.202),(2.049,.010,.013),"alloy",.002)
    for xx in (-.66,.66):
        for yy in (-.529,.529):
            box(g,"Cassette clip",(xx,yy,2.252),(.105,.022,.078),"cobalt",.009)


def pleats(group,name,width,depth,z,amplitude,cycles,mat):
    vertices = []
    faces = []
    for i in range(cycles*2+1):
        x = -width/2+width*i/(2*cycles)
        zz = z + (-.5 if i%2==0 else .5)*amplitude
        vertices.extend(((x,-depth/2,zz),(x,depth/2,zz)))
        if i:
            k=2*i
            faces.append((k-2,k,k+1,k-1))
    return mesh(group,name,vertices,faces,mat)


def build_blower():
    g = "Blower"
    for x in (-.53,.53):
        box(g,"Mounting bridge",(x,0,2.363),(.104,.85,.038),"cobalt",.009)
        for y in (-.343,.343):
            cylinder(g,"Isolation mount",(x,y,2.332),.044,.042,"boot",n=24)
    cylinder(g,"Impeller backplate",(0,.01,2.392),.436,.037,"steel",n=72)
    annulus(g,"Curved inlet lip",(0,.01,2.582),.431,.292,.037,"alloy",n=72)
    cylinder(g,"Motor",(0,.01,2.478),.145,.173,"navy",n=60,edge=.012)
    cylinder(g,"Motor cap",(0,.01,2.569),.117,.024,"steel",n=48,edge=.009)
    cylinder(g,"Axle cap",(0,.01,2.586),.041,.015,"navy",n=36)
    vertices, faces = [],[]
    for i in range(24):
        angle=i*math.tau/24
        start=len(vertices)
        for j in range(8):
            t=j/7
            r=.283+.131*t
            ang=angle + .31*(t**1.2)
            for da,z in [(-.013,2.404),(.013,2.404),(.013,2.568),(-.013,2.568)]:
                vertices.append((r*math.cos(ang+da),.01+r*math.sin(ang+da),z))
            if j:
                k=len(vertices)-8
                for side in range(4):
                    a,b=k+side,k+(side+1)%4
                    faces.append((a,b,b+4,a+4))
        faces.extend(((start+3,start+2,start+1,start),tuple(range(start+28,start+32))))
    mesh(g,"Backward-curved wheel blades",vertices,faces,"cobalt",.0015)
    for a in range(3):
        t=math.tau*a/3 + .32
        beam(g,"Motor cradle",(.113*math.cos(t),.01+.113*math.sin(t),2.54),
             (.304*math.cos(t),.01+.304*math.sin(t),2.535),.028,.013,"steel",.002)


def build_prefilter():
    g = "Prefilter"
    rim(g,"Intake cassette",(0,.009,2.713),(1.59,.818),(1.494,.726),.061,(.048,.027),"cobalt")
    pleats(g,"Intake medium",1.493,.724,2.716,.026,38,"coarse")
    for y in (-.261,-.087,.087,.261):
        box(g,"Intake protector",(0,.009+y,2.745),(1.508,.015,.013),"alloy",.004)
    for x in (-.51,.51):
        box(g,"Intake keeper",(x,.009,2.752),(.013,.737,.014),"cobalt",.004)
    for x in (-.733,.733):
        for y in (-.362,.38):
            cylinder(g,"Retainer",(x,y,2.747),.012,.009,"alloy",n=18,edge=.001)


def build_hood():
    g="Hood"
    rim(g,"Powder coated plenum shell",(0,0,2.48),(2.46,1.25),(2.335,1.087),.498,(.102,.057),"shell",.014)
    rim(g,"Dark lower trim",(0,0,2.221),(2.441,1.229),(2.152,1.028),.044,(.092,.041),"navy",.009)
    rim(g,"Intake surround",(0,0,2.717),(2.441,1.227),(1.51,.744),.051,(.103,.03),"front",.008)
    # The detachable front panel leaves its physical shadow gap in the top box.
    box(g,"Front service door seal",(0,-.624,2.474),(2.194,.012,.344),"navy",.05)
    box(g,"Control fascia",(0,-.633,2.475),(2.183,.028,.331),"front",.045)
    x0=.604
    box(g,"Control recess",(x0,-.654,2.476),(.731,.022,.204),"navy",.031)
    box(g,"Switch insert",(x0,-.670,2.476),(.702,.014,.177),"cobalt",.025)
    for x in (.387,.523):
        box(g,"Button gasket",(x,-.678,2.473),(.104,.019,.117),"boot",.014)
        box(g,"Rocker",(x,-.692,2.472),(.082,.026,.095),"navy",.012)
        box(g,"Switch index",(x,-.706,2.494),(.024,.0025,.006),"marker",.001)
    gauge_center=(.789,-.687,2.477)
    cylinder(g,"Pressure gauge rim",gauge_center,.079,.044,"alloy",(0,-1,0),n=56,edge=.004)
    cylinder(g,"Dial",(.789,-.712,2.477),.068,.008,"dial",(0,-1,0),n=56,edge=.002)
    for i in range(13):
        angle=math.radians(222-i*22)
        length=.012 if i%3==0 else .007
        x=.789+(.052-length/2)*math.cos(angle)
        z=2.477+(.052-length/2)*math.sin(angle)
        mark=box(g,"Gauge index",(x,-.717,z),(length,.0018,.0019),"navy",0)
        mark.rotation_euler.y = -angle
    start=(.784,-.719,2.474)
    end=(.757,-.719,2.503)
    beam(g,"Gauge pointer",start,end,.0038,.0021,"navy",0)
    cylinder(g,"Gauge pivot",(.789,-.720,2.477),.006,.003,"marker",(0,-1,0),n=16,edge=0)
    for x in (-1.035,1.035):
        for z in (2.352,2.595):
            cylinder(g,"Panel captive screw",(x,-.6515,z),.010,.005,"alloy",(0,-1,0),n=16,edge=.0007)
    lettering(g,"Fascia marking","VERTICAL FLOW",(-.904,-.65,2.477),.072,"navy")
    lettering(g,"Secondary marking","CLEAN BENCH",(-.901,-.65,2.405),.034,"cobalt")
    box(g,"Lamp housing",(0,-.505,2.192),(1.845,.083,.034),"navy",.014)
    box(g,"Lamp diffuser",(0,-.513,2.171),(1.771,.048,.015),"light",.006)
    for s in (-1,1):
        # Flush side access panel and two quarter-turn fasteners.
        box(g,"Side service seam",(s*1.229,.031,2.491),(.009,.89,.316),"cobalt",.035)
        box(g,"Side access panel",(s*1.236,.031,2.491),(.016,.878,.305),"shell",.032)
        for y in (-.338,.401):
            cylinder(g,"Side fastener",(s*1.249,y,2.488),.013,.009,"alloy",(s,0,0),n=20,edge=.001)


def aim(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()


def camera(studio,name,location,target,span):
    data = bpy.data.cameras.new(name)
    data.type, data.ortho_scale = "ORTHO",span
    obj=bpy.data.objects.new(name,data)
    studio.objects.link(obj)
    obj.location=location
    aim(obj,target)
    return obj


def add_area(studio,name,loc,target,power,size,size_y,color):
    data=bpy.data.lights.new(name,"AREA")
    data.energy, data.shape, data.size, data.size_y=power,"RECTANGLE",size,size_y
    data.color=linear(color)
    obj=bpy.data.objects.new(name,data)
    studio.objects.link(obj)
    obj.location=loc
    aim(obj,target)


def setup_studio(scene,studio,width,samples):
    scene.render.engine="CYCLES"
    scene.cycles.samples=samples
    scene.cycles.use_denoising=True
    scene.cycles.use_adaptive_sampling=True
    scene.cycles.adaptive_threshold=.035
    scene.cycles.max_bounces=6
    scene.cycles.transparent_max_bounces=9
    try:
        prefs=bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type="METAL"
        prefs.refresh_devices()
        if any(d.type=="METAL" for d in prefs.devices):
            for d in prefs.devices:
                d.use=d.type=="METAL"
            scene.cycles.device="GPU"
    except (RuntimeError,TypeError):
        pass
    scene.render.resolution_x=width
    scene.render.resolution_y=round(width*2/3)
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.image_settings.color_mode="RGBA"
    scene.render.image_settings.color_depth="8"
    scene.view_settings.view_transform="AgX"
    world=bpy.data.worlds.new("Broad daylight")
    scene.world=world
    world.use_nodes=True
    bg=world.node_tree.nodes["Background"]
    bg.inputs[0].default_value=(*linear("E3EAF1"),1)
    bg.inputs[1].default_value=.52
    add_area(studio,"Large softbox",(-3.6,-4.2,5.65),(0,0,1.52),384,3.8,3.4,"FFFAF0")
    add_area(studio,"Long reflection",(3.5,-1.6,4.5),(0,0,1.87),243,1.45,4.8,"E2ECF6")
    add_area(studio,"Back strip",(-.8,3,4.8),(0,0,1.8),426,3.05,2.35,"E0EAF5")
    add_area(studio,"Chamber fill",(-.4,-2.6,1.55),(0,0,1.5),24,2.4,1.25,"E7EFF6")
    add_area(studio,"Upper sweep",(0,1,6.0),(0,0,2),138,3.6,2.3,"F6F0E6")
    # The strip light is attached to the hood so the assembly view remains coherent.
    lamp=bpy.data.lights.new("Cabinet work light","AREA")
    lamp.shape,lamp.size,lamp.size_y,lamp.energy="RECTANGLE",1.55,.096,15
    lamp.color=linear("F7F7F2")
    led=bpy.data.objects.new("Cabinet light pool",lamp)
    studio.objects.link(led)
    led.parent=roots["Hood"]
    led.location=(0,-.442,2.161)
    aim(led,(0,.04,1.11))
    cam_a=camera(studio,"Assembled three quarter",(3.35,-6.45,3.37),(0,0,1.38),5.31)
    cam_b=camera(studio,"Exploded three quarter",(3.72,-7.10,4.85),(-.30,-.12,2.12),7.85)
    scene.camera=cam_a
    m1=scene.timeline_markers.new("Assembled",frame=1)
    m2=scene.timeline_markers.new("Exploded",frame=101)
    m1.camera,m2.camera=cam_a,cam_b
    # Keep the enclosed studio world out of alpha in the primary still.
    data=bpy.data.meshes.new("Studio floor")
    data.from_pydata([(-100,-100,-.001),(100,-100,-.001),(100,100,-.001),(-100,100,-.001)],[],[(0,1,2,3)])
    data.update()
    floor=bpy.data.objects.new("Blue-grey studio floor",data)
    studio.objects.link(floor)
    ground=material("Mist blue cyclorama","D3E0F0",settings={"roughness":.74,"bump":0,"subsurface_weight":0})
    shader=ground.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Emission Color"].default_value=(*linear("C6DCF7"),1)
    rays=ground.node_tree.nodes.new("ShaderNodeLightPath")
    lift=ground.node_tree.nodes.new("ShaderNodeMath")
    lift.operation="MULTIPLY"
    lift.inputs[1].default_value=1.95
    ground.node_tree.links.new(rays.outputs["Is Camera Ray"],lift.inputs[0])
    ground.node_tree.links.new(lift.outputs[0],shader.inputs["Emission Strength"])
    floor.data.materials.append(ground)
    floor.hide_render=True
    floor.keyframe_insert(data_path="hide_render",frame=1)
    floor.hide_render=False
    floor.keyframe_insert(data_path="hide_render",frame=101)
    scene.render.film_transparent=True
    scene.render.keyframe_insert(data_path="film_transparent",frame=1)
    scene.render.film_transparent=False
    scene.render.keyframe_insert(data_path="film_transparent",frame=101)


def export_web(scene,path):
    # Bake each original component as one mesh for selection and fewer browser draw calls.
    output = bpy.data.collections.new("Web meshes")
    scene.collection.children.link(output)
    originals = []
    duplicates = []
    bpy.ops.object.select_all(action="DESELECT")
    scene.frame_set(1)
    depsgraph=bpy.context.evaluated_depsgraph_get()
    for part_name,root in roots.items():
        group_objs=[]
        for editable in list(parts[part_name].objects):
            if editable.type not in {"MESH","FONT"}:
                continue
            evaluated=editable.evaluated_get(depsgraph)
            data=bpy.data.meshes.new_from_object(evaluated,depsgraph=depsgraph)
            ob=bpy.data.objects.new("Export surface",data)
            output.objects.link(ob)
            ob.matrix_world=editable.matrix_world
            group_objs.append(ob)
        bpy.ops.object.select_all(action="DESELECT")
        for obj in group_objs:
            obj.select_set(True)
        joined=group_objs[0]
        bpy.context.view_layer.objects.active=joined
        bpy.ops.object.join()
        # Parent at identity to leave the seven root objects available to the viewer.
        original_name = root.name
        root.name="Editable "+part_name
        originals.append((root,original_name))
        export_root=bpy.data.objects.new(part_name,None)
        output.objects.link(export_root)
        export_root["display_name"]=PARTS[part_name][0]
        export_root["explode"]=PARTS[part_name][1]
        joined.name=part_name+" surface"
        joined.parent=export_root
        duplicates.extend((export_root,joined))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in duplicates:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",use_selection=True,
                              export_animations=False,export_yup=True,export_extras=True,
                              export_materials="EXPORT",export_cameras=False,export_lights=False,
                              export_texcoords=False,export_tangents=False)
    for obj in duplicates:
        bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.collections.remove(output)
    for obj,name in originals:
        obj.name=name


def build(args):
    out=args.out.resolve()
    out.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene
    scene.name="Clean bench"
    scene.frame_start,scene.frame_end=1,101
    studio=bpy.data.collections.new("Studio and cameras")
    scene.collection.children.link(studio)
    for name,(label,delta) in PARTS.items():
        col=bpy.data.collections.new(label)
        scene.collection.children.link(col)
        obj=bpy.data.objects.new(name,None)
        col.objects.link(obj)
        obj.empty_display_size=.08
        roots[name]=obj
        parts[name]=col
        obj["display_name"]=label
        obj["exploded_delta_gltf"]=delta
        obj["evidence"]="schematic"
        obj.keyframe_insert(data_path="location",frame=1)
        obj.location=(delta[0],-delta[2],delta[1])
        obj.keyframe_insert(data_path="location",frame=101)
        obj.location=ORIGIN
    make_materials()
    build_frame()
    build_worktop_and_sash()
    build_filter()
    build_blower()
    build_prefilter()
    build_hood()
    setup_studio(scene,studio,args.width,args.samples)
    scene.frame_set(1)
    scene.render.filepath="//assembled.png"
    scene["teaching_scope"]="Generic vertical clean bench. Part locations and explosion travel are schematic."
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=="VIEW_3D":
                area.spaces.active.overlay.show_overlays=False
                area.spaces.active.region_3d.view_perspective="CAMERA"
    if not args.preview:
        export_web(scene,out/"clean-bench.glb")
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active=None
        bpy.data.orphans_purge(do_recursive=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(out/"clean-bench.blend"),compress=True)
        (out/"parts.json").write_text(json.dumps({
            "model":"垂直流超净工作台","axes":"glTF +Y up, +Z front",
            "assembled_camera":{"position":[3.35,3.37,6.45],"target":[0,1.38,0]},
            "exploded_camera":{"position":[3.72,4.85,7.10],"target":[-.30,2.12,.12]},
            "parts":[{"node":n,"label":v[0],"explode":v[1]} for n,v in PARTS.items()]
        },ensure_ascii=False,indent=2)+"\n")
    for frame,stem in [(1,"assembled"),(101,"exploded")]:
        scene.frame_set(frame)
        scene.render.filepath=str(out/(stem+".png"))
        bpy.ops.render.render(write_still=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--width",type=int,default=1920)
    parser.add_argument("--samples",type=int,default=48)
    parser.add_argument("--preview",action="store_true")
    build(parser.parse_args(sys.argv[sys.argv.index("--")+1:]))
