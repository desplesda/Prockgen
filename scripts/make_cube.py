# Import the Blender modules
import bpy
import bmesh

# Get the current scene
scene = bpy.context.scene

# Create an empty mesh
mesh = bpy.data.meshes.new("My Cube")

# Create the cube object
cube = bpy.data.objects.new("My Cube", mesh)

# Add the object into the scene.
scene.objects.link(cube)

# Build a cube mesh using bmesh, Blender's mesh editing system
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=3.0)

# Store the bmesh inside inside the mesh
bm.to_mesh(mesh)
