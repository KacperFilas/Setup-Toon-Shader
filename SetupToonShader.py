bl_info = {
    "name": "Setup Toon Settings",
    "author": "Kacper Filas",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "3D Viewport > Sidebar > Toon Tab",
    "description": "Adds a panel in Object Mode sidebar for toon setup",
    "category": "3D View",
}

import bpy

asset_file = "E:\Moje projekty\Youtube\BlendFiles\MyAssetLibrary\MyAssetLibrary.blend"
geo_node_name ="ToonOutline"
material_name = "Stylized"





class OBJECT_OT_setup_toon(bpy.types.Operator):
    bl_idname = "object.setup_toon"
    bl_label = "Setup Toon Settings"

    def execute(self, context):


        def append_node_group():
            appended_group = bpy.data.node_groups.get(geo_node_name)    # check if node group is already appended       
            if not appended_group:  # if node group is not appended
                with bpy.data.libraries.load(asset_file, link=False) as (data_from, data_to): # load node group from asset file
                    if geo_node_name in data_from.node_groups:
                        data_to.node_groups = [geo_node_name]
                        for area in bpy.context.screen.areas: # tag all areas for redraw
                            area.tag_redraw()
                        self.report({'INFO'}, f"Appended: {geo_node_name}")
                    else:
                        self.report({'ERROR'}, f"Node group '{geo_node_name}' not found")
                        return False     # return False if node group is not appended

            return True   # return True if node group is appended
        def append_material():
            appended_mat = bpy.data.materials.get(material_name)    
            if not appended_mat:
                with bpy.data.libraries.load(asset_file, link=False) as (data_from, data_to):
                     if material_name in data_from.materials:
                        data_to.materials = [material_name]
                        for area in bpy.context.screen.areas:
                            area.tag_redraw()
                            self.report({'INFO'}, f"Appended: {material_name}")
                     else:
                        self.report({'ERROR'}, f"Material '{material_name}' not found")
                        return False
                return True
  
        append_material()
        append_node_group()



        def assign_to_selected():

            appended_group = bpy.data.node_groups.get(geo_node_name)
            appended_mat = bpy.data.materials.get(material_name)
            if appended_group and appended_mat:
                for obj in context.selected_objects:

                     # Store the image texture from old material   
                    old_mat = obj.data.materials[0] if obj.data.materials else None
                    tex_image = None
                    if old_mat:
                        for node in old_mat.node_tree.nodes:
                            if node.type == 'TEX_IMAGE':
                                tex_image = node.image
                                break
                    print(tex_image)
                    
                    if obj.type == 'MESH':
                        if not any(mod.type == 'NODES' and mod.name == "ToonOutline" and mod.node_group == appended_group
                           for mod in obj.modifiers):
                            mod = obj.modifiers.new(name="ToonOutline", type='NODES')
                            mod.node_group = appended_group
                            
                        # Assign new material
                        if obj.data.materials:
                            new_mat=appended_mat.copy()
                            obj.data.materials[0] = new_mat
                        else:
                            new_mat=appended_mat.copy()
                            obj.data.materials.append(new_mat) 

                        # Apply stored texture to the new material
                        if tex_image and new_mat.node_tree:
                            for node in new_mat.node_tree.nodes:
                                if node.type == 'TEX_IMAGE':
                                    node.image = tex_image
                                    break
                            
                return None  # stop timer 
            return 0.1  # retry in 0.1 seconds if not ready , blender thing to make sure the node group is ready, set timer for bpy.app.timers.register
 
        bpy.app.timers.register(assign_to_selected)   # run assign_to_selected() and return {'FINISHED'} if node group is appended



        return {'FINISHED'}


    
class VIEW3D_PT_toon_panel(bpy.types.Panel):
    bl_label = "Setup Toon Settings"
    bl_idname = "VIEW3D_PT_toon_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Toon'
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.setup_toon", text="Setup Toon Settings")

def register():
    bpy.utils.register_class(OBJECT_OT_setup_toon)
    bpy.utils.register_class(VIEW3D_PT_toon_panel)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_toon_panel)
    bpy.utils.unregister_class(OBJECT_OT_setup_toon)

if __name__ == "__main__":
    register()