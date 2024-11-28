import bpy

class ListBones(bpy.types.Operator):
    bl_idname = "wm.mimic_list_bones"
    bl_label = "List Bones"
    bl_description = "Prints bone names to console."
    bl_options = {'REGISTER'}
    
    def print_bone_hierarchy(self, bone, indent_level=0):
        # Print current bone with indentation
        indent = " " * indent_level  # 4 spaces per level
        print(f"{indent}- {bone.name}")
        
        # Recursively print children with increased indentation
        for child in bone.children:
            self.print_bone_hierarchy(child, indent_level + 1)
    
    def execute(self, context):
        # Get the active object
        active_obj = context.active_object
        
        if (active_obj and active_obj.type == 'ARMATURE' and 
            context.mode == 'POSE'):
            
            # Get the selected pose bone
            selected_bone = context.active_pose_bone
            if selected_bone:
                # Get the corresponding bone from armature data
                bone = active_obj.data.bones[selected_bone.name]
                print(f"\nSelected bone and its children:")
                self.print_bone_hierarchy(bone)
            else:
                print("Please select a bone in pose mode")
        else:
            print("Please select an armature and enter pose mode")
            
        return {'FINISHED'}

class AddShapeKeys(bpy.types.Operator):
    bl_idname = "wm.mimic_add_face_shapes"
    bl_label = "Add Face Shapes"
    bl_description = "Adds default ARKit shape keys to selected object."
    bl_options = {'REGISTER'}
    
    def print_bone_hierarchy(self, bone, indent_level=0):
        # Print current bone with indentation
        indent = " " * indent_level  # 4 spaces per level
        print(f"{indent}- {bone.name}")
        
        # Recursively print children with increased indentation
        for child in bone.children:
            self.print_bone_hierarchy(child, indent_level + 1)
    
    def execute(self, context):
        # Get the active object
        active_obj = context.active_object
        
        if (active_obj and active_obj.type == 'ARMATURE' and 
            context.mode == 'POSE'):
            
            # Get the selected pose bone
            selected_bone = context.active_pose_bone
            if selected_bone:
                # Get the corresponding bone from armature data
                bone = active_obj.data.bones[selected_bone.name]
                print(f"\nSelected bone and its children:")
                self.print_bone_hierarchy(bone)
            else:
                print("Please select a bone in pose mode")
        else:
            print("Please select an armature and enter pose mode")
            
        return {'FINISHED'}
