import bpy, random, math
from mathutils import Euler
from util import *

def make_asteroid_metaball(
    radius=1, 
    element_range=(2,3), 
    element_size_range=(0.5,1.5), 
    negative_chance=0.2):
    
    # Make a new metaball
    ball = bpy.data.metaballs.new("Asteroid_Ball")

    # Configure the resolution of the ball
    ball.resolution = 0.1
    
    # Generate a random number of metaball elements
    for i in range(random.randint(*element_range)):

        # Make a new element
        element = ball.elements.new()

        # Make it a randomly-sized ellipsoid
        element.type = 'ELLIPSOID'
        element.size_x = random.uniform(*element_size_range)
        element.size_y = random.uniform(*element_size_range)
        element.size_z = random.uniform(*element_size_range) 

        # Generate a random rotation and use it
        element.rotation = random_rotation()

        # Place it somewhere in the sphere          
        element.co = point_inside_sphere(radius)    
    
        # Maybe make it a negative shape if it's not the first element
        if i != 0:
            element.use_negative = random.uniform(0,1) < negative_chance
    
    # Make a new object that uses the metaball
    ball_obj = bpy.data.objects.new(ball.name, ball)

    # Add it to the scene
    bpy.context.scene.objects.link(ball_obj)
    
    return ball_obj

def make_mesh_from_metaball(mball_object, name="Asteroid"):  
    # Ensure that the metaballs have generated
    bpy.context.scene.update()
    
    # Convert the metaballs to a mesh
    ball_mesh = mball_object.to_mesh(
        bpy.context.scene, # what scene we're doing this in
        False,  # apply modifiers?
        'PREVIEW') # what settings to use (preview, or render)
        
    # Create a new object that uses this mesh
    ball_mesh_object = bpy.data.objects.new(name, ball_mesh)
    
    # Add it to the scene
    bpy.context.scene.objects.link(ball_mesh_object)

    # Remove the metaball from the scene
    bpy.context.scene.objects.unlink(mball_object)

    return ball_mesh_object

def add_modifiers(obj):
    # Add a subsurface modifier so that we have more faces to work with
    obj.modifiers.new("Subsurf", 'SUBSURF')
    
    # Create a texture that the displacement modifier will use
    texture = bpy.data.textures.new("Asteroid_Displacement", 'VORONOI')
    
    # Set it up with some settings that produce a nice rocky surface
    texture.weight_1 = 2
    texture.weight_2 = 2
    texture.weight_3 = 2
    texture.weight_4 = 2
    texture.noise_scale = 0.5

    # Add a displacement modifier to add this rough surface to the mesh
    displace = obj.modifiers.new("Displace", 'DISPLACE')    
    
    # Set up the displacement modifier
    displace.texture = texture
    displace.strength = 0.5
    
    # Generate a mesh that incorporates these modifiers, and replace our
    # mesh with it
    obj.data = obj.to_mesh(bpy.context.scene, True, 'PREVIEW')

    # Get rid of the modifiers - we don't need them anymore
    obj.modifiers.clear()

# Duplicates the input object, and creates a new one that has a lower
# polycount.
def make_lowpoly_object(hipoly_obj, decimate_ratio=0.025):
    
    # Figure out what to call the low-poly version
    lowpoly_name = hipoly_obj.name + " Lowpoly"

    # Duplicate the high-poly object by creating a new object that uses a
    # copy of its data
    lowpoly_object = bpy.data.objects.new(lowpoly_name, hipoly_obj.data.copy())

    # Add the new low-poly object to the scene
    bpy.context.scene.objects.link(lowpoly_object)
    
    # Create a decimate modifier, which reduces the polycount of the mesh
    decimate = lowpoly_object.modifiers.new("Decimate", 'DECIMATE')
    decimate.ratio = decimate_ratio
    
    # Get the resulting mesh, apply it, and clear the modifiers
    lowpoly_object.data = lowpoly_object.to_mesh(bpy.context.scene, True, 'PREVIEW')
    lowpoly_object.modifiers.clear()
    
    # Return the new object that we created and added
    return lowpoly_object

# Generates a UV map for the object by using the Smart Project operation
def uv_unwrap(obj, island_margin=0.1):

    # Select the object and make it the active one too
    bpy.context.scene.objects.active = obj
    obj.select = True

    # Enter Edit mode, which Smart Project requires
    bpy.ops.object.mode_set(mode='EDIT')

    # Select all faces (we want to unwrap the entire object)
    bpy.ops.mesh.select_all(action='SELECT') 

    # Perform the smart project
    bpy.ops.uv.smart_project(island_margin=island_margin)

    # The object now has a UV map!

    # Return to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')

def create_bake_material(lowpoly_obj):
    # Create a new material 
    bake_material = bpy.data.materials.new("Asteroid")

    # Make it use nodes, and get its node tree
    bake_material.use_nodes = True
    bake_node_tree = bake_material.node_tree
    
    # Create a new texture image node
    node = bake_node_tree.nodes.new("ShaderNodeTexImage")
    node.name = "Bake Destination"

    # Select it and make it active
    node.select = True
    bake_node_tree.nodes.active = node

    # Set the low-poly object's active material to the bake material
    lowpoly_obj.active_material = bake_material
    
    return bake_material

def prepare_for_bake():
    # Set up our renderer
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.bake.use_selected_to_active = True

    # Tell Blender we want to export images as PNGs
    bpy.context.scene.render.image_settings.file_format='PNG'
    

# Bakes the normals from hipoly_obj into an image, using lowpoly_obj's UV
# map.
def bake_normals(hipoly_obj, lowpoly_obj, bake_material, size=(1024,1024), path="//Asteroid_nrm.png"):

    # To bake the normals of an object onto another, you need the following
    # things:
    #
    # - both the objects are selected
    # - the target object must be active
    # - the target object must have a material
    # - the target object must have a UV map
    # - the material must be configured to use nodes
    # - the material must have an Image Texture node
    # - the Image Texture node must be the active node
    # - the Image Texture node is configured to use a texture of the size
    #   you need
    # - the two objects must be in the same position
    # - the scene has been configured to bake the selected objects to the
    #   active object
    #
    # We'll also be using the Cycles render engine, because it gives nice
    # results.

    # Ensure that both objects are selected
    hipoly_obj.select = True
    lowpoly_obj.select = True
    
    # Make the low-poly object active
    bpy.context.scene.objects.active = lowpoly_obj
    
    # Create an image and make the node use it
    bake_image = bpy.data.images.new('Asteroid_Normalfile',*size)
    bake_node = bake_material.node_tree.nodes["Bake Destination"]
    bake_node.image = bake_image
    
    # Perform the bake!
    bpy.ops.object.bake(type='NORMAL', cage_extrusion=0.1)
    
    # Convert the path we got into an absolute path
    output_path = bpy.path.abspath(path)

    # Save the image to disk
    bake_image.save_render(output_path, bpy.context.scene)

# Erase the scene
reset()

# Generate asteroid shapes
asteroid_metaball = make_asteroid_metaball()

# Make a mesh from those shapes
asteroid_highpoly = make_mesh_from_metaball(asteroid_metaball)

# Add modifiers to make the shape look like rock
add_modifiers(asteroid_highpoly)

# Make a low-poly version of the rock mesh
asteroid_lowpoly = make_lowpoly_object(asteroid_highpoly)

# Unwrap the low-poly object so we can create a texture
uv_unwrap(asteroid_lowpoly)

# Create a material for baking textures with
bake_material = create_bake_material(asteroid_lowpoly)

# Prepare Blender for baking by setting the render engine and some other settings
prepare_for_bake()

# Generate a normal map from the high-poly object and save it
bake_normals(asteroid_highpoly, asteroid_lowpoly, bake_material, path='//Procgen/Assets/Asteroid_Nrm.png')