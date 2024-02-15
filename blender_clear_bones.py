import bpy

# Select the specific armature you want to remove if there are multiple
armature_name = "NameOfYourArmature"

# Loop through all objects in the scene
for obj in bpy.data.objects:
    # Check if the object is a mesh
    if obj.type == 'MESH':
        # Loop through each modifier in the object
        for modifier in obj.modifiers:
            # If the modifier is an armature and its name matches, remove it
            if modifier.type == 'ARMATURE' and modifier.object.name == armature_name:
                obj.modifiers.remove(modifier)
                # Break the loop if you assume there's only one armature modifier per object
                break
        
        # Remove all vertex groups from the mesh
        obj.vertex_groups.clear()

# Optional: Remove the armature object itself if it's no longer needed
if armature_name in bpy.data.objects:
    armature = bpy.data.objects[armature_name]
    bpy.data.objects.remove(armature, do_unlink=True)
