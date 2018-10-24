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
    
# Erase the scene
reset()

# Generate asteroid shapes
asteroid_metaball = make_asteroid_metaball()

# Make a mesh from those shapes
asteroid_highpoly = make_mesh_from_metaball(asteroid_metaball)
