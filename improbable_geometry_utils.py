bl_info = {
    "name": "Improbable Geometry Processor",
    "author": "Felipe Pesantez",
    "version": (0,0,1),
    "blender": (3,5,0),
    "location": "3D Viewport > Sidebar > Improbable geometry process",
    "description": "Metaverse Avatar geometry process",
    "category": "Development",
}

import bpy
import mathutils

def createUECube():
    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 1), scale=(0.89, 0.89, 0.89))
    bpy.context.active_object.location.z -= 0.1


def removeArmature(armature_name):
    # Get all mesh objects in the scene
    all_objects = [obj for obj in bpy.context.scene.objects]

    # Select all mesh objects
    for obj in all_objects:
        obj.select_set(True)

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

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
        
    

def merge_and_delete_transform_groups(obj):
    # Select the object and enter edit mode
    bpy.context.view_layer.objects.active = obj

    # Clear parent and keep transformation
    obj.matrix_world = obj.matrix_world @ obj.matrix_parent_inverse
    obj.matrix_basis.identity()
    obj.parent = None
    obj.matrix_world.identity()

def scale_object_to_fit():
    # Get the selected objects
    selected_objects = bpy.context.selected_objects

    # Check if there are at least two selected objects
    if len(selected_objects) < 2:
        print("Select at least two objects.")
        return

    # Get the dimensions of the last two selected objects
    
    object_a = selected_objects[-2]
    object_b = selected_objects[-1]

    # Get the dimensions of objectB
    bounding_box = object_b.bound_box
    max_dimensions = [max(bounding_box[i][j] for i in range(8)) for j in range(3)]

    # Find the maximum dimension of objectB
    max_scale = max(max_dimensions)

    # Calculate the scaling factor
    scale_factor = max_scale / max(object_a.dimensions)
    scale_factor *= 2

    # Apply the scaling to objectA
    object_a.scale = (scale_factor, scale_factor, scale_factor)

def cleanup_geo():
    # Get all mesh objects in the scene
    all_objects = [obj for obj in bpy.context.scene.objects]

    # Select all mesh objects
    for obj in all_objects:
        obj.select_set(True)

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    # Clear existing selection
    bpy.ops.object.select_all(action='DESELECT')

    # Get all mesh objects in the scene
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

    # Select all mesh objects
    for obj in mesh_objects:
        obj.select_set(True)

    # Print the names of selected mesh objects (optional)
    selected_mesh_names = [obj.name for obj in bpy.context.selected_objects]
    print("Selected Mesh Objects:", selected_mesh_names)

    for object in mesh_objects:

        object_name = object.name

        # Get the object by name
        obj = bpy.data.objects.get(object_name)

        if obj:
            # Check if the object has any parent
            if obj.parent:
                # Apply the parent inverse to clear transformations
                obj.matrix_world = obj.matrix_world @ obj.matrix_parent_inverse
                obj.parent = None
            try:
                # Delete transform groups
                for group in obj.users_group:
                    bpy.data.groups.remove(group)
            except:
                pass

            # Merge and delete transform groups
            merge_and_delete_transform_groups(obj)
        else:
            print(f"Object with name '{object_name}' not found.")
        

    other_objects = [obj for obj in bpy.context.scene.objects if obj.type != 'MESH']

    for obj in other_objects:
        bpy.data.objects.remove(obj, do_unlink=True)
        
    bpy.ops.object.join()
    
class MESH_OT_ue_cube(bpy.types.Operator):
    """Creates a cube with the UE skeleton unit scale for reference"""
    bl_idname = "cube.cube_id"
    bl_label = "Cube with UE skeleton scale"
    bl_options = {"REGISTER", "UNDO"}
    
    
    def execute(self, context):
        createUECube()

        return {"FINISHED"}

class MESH_OT_clean_armature(bpy.types.Operator):
    """Removes the skeleton armature and clears all vertex groups"""
    bl_idname = "armature.armature_id"
    bl_label = "Skeleton Rig cleanup"
    bl_options = {"REGISTER", "UNDO"}
    
    
    skeleton_name: bpy.props.StringProperty(
        name="Armature Name",
        default="Armature",
        description="Name of the armature in the scene"
    )
    
    
    def execute(self, context):
        removeArmature(self.skeleton_name)

        return {"FINISHED"}

class MESH_OT_clean_geom_transforms(bpy.types.Operator):
    """Clears all transform groups and places the meshes at the root hierarchy level"""
    bl_idname = "mesh.mesh_id"
    bl_label = "Geometry transform cleanup"
    bl_options = {"REGISTER", "UNDO"}
    
    """
    user_name: bpy.props.StringProperty(
        name="User Name",
        default="Felipe",
        description="Name of the user"
    )
    """
    
    def execute(self, context):
        cleanup_geo()

        return {"FINISHED"}
    
class MESH_OT_match_transforms(bpy.types.Operator):
    """Match the bound scale from B to A"""
    bl_idname = "scale.scale_id"
    bl_label = "Geometry bound match transform"
    bl_options = {"REGISTER", "UNDO"}
    
    
    def execute(self, context):
        scale_object_to_fit()

        return {"FINISHED"}
        
class VIEW3D_PT_geometry_process_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    bl_category = "Improbable geometry process"
    bl_label = "Geometry Process Panel"

    def draw(self, context):
        row = self.layout.row()
        row.operator("cube.cube_id", text="Add UE Cube")
        
        self.layout.separator()
        
        row = self.layout.row()
        row.operator("armature.armature_id", text="Remove Armature")
        row = self.layout.row()
        row.operator("mesh.mesh_id", text="Remove Transform Groups")
        row = self.layout.row()
        row.operator("scale.scale_id", text="Match Scale")

def register():
    bpy.utils.register_class(VIEW3D_PT_geometry_process_panel)
    bpy.utils.register_class(MESH_OT_ue_cube)
    bpy.utils.register_class(MESH_OT_clean_armature)
    bpy.utils.register_class(MESH_OT_clean_geom_transforms)
    bpy.utils.register_class(MESH_OT_match_transforms)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_geometry_process_panel)
    bpy.utils.unregister_class(MESH_OT_ue_cube)
    bpy.utils.unregister_class(MESH_OT_clean_armature)
    bpy.utils.unregister_class(MESH_OT_clean_geom_transforms)
    bpy.utils.unregister_class(MESH_OT_match_transforms)
    

if __name__ == "__main__":
    register()
