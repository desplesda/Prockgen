import bpy, random, math; from mathutils import Euler

# Selects or deselects all objects in the scene.
def select_all(select=True):
    for o in bpy.context.scene.objects:
            o.select = select
    

# Deletes all objects in the scene.
def reset():    
    # Unlink all objects in the scene
    for obj in bpy.context.scene.objects:
        bpy.context.scene.objects.unlink(obj)
    bpy.context.scene.update()
    

def random_rotation():
    angles = (
            random.uniform(0, 2*math.pi),
            random.uniform(0, 2*math.pi),    
            random.uniform(0, 2*math.pi)
        )
    return Euler(angles, 'XYZ').to_quaternion()
 
# Generates a random point inside a sphere
def point_inside_sphere(radius):
    phi = random.uniform(0,2 * math.pi)
    costheta = random.uniform(-1,1)
    u = random.uniform(0,1)

    theta = math.acos( costheta )
    r = radius * math.pow(u, 1/3.)

    x = r * math.sin( theta) * math.cos( phi )
    y = r * math.sin( theta) * math.sin( phi )
    z = r * math.cos( theta )

    return (x,y,z)