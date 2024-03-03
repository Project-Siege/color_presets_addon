import bpy
import re

bl_info = {
    "name": "Color Presets Add-on",
    "author": "Nomadic_Jester",
    "version": (1, 10),
    "blender": (4, 0, 0),
    "location": "View3D > Object Context Menu",
    "description": "Add custom color presets to quickly update object materials.",
    "category": "Object",
}

# Custom property group for color presets
class ColorPreset(bpy.types.PropertyGroup):
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),  # Default white color
        min=0.0,
        max=1.0
    )
    name: bpy.props.StringProperty(name="Name")
    index: bpy.props.IntProperty()  # Add index property

# Operator to update material color
class UpdateMaterialColorOperator(bpy.types.Operator):
    bl_idname = "object.update_material_color"
    bl_label = "Update Material Color"
    
    preset_index: bpy.props.IntProperty()
    
    def execute(self, context):
        obj = context.active_object
        preset_color = context.scene.color_presets[self.preset_index].color
        
        if obj.active_material:
            mat = obj.active_material
            mat.use_nodes = True
            node = mat.node_tree.nodes.get('Principled BSDF')
            if node:
                node.inputs['Base Color'].default_value = preset_color
        else:
            mat = bpy.data.materials.new(name="Material")
            mat.use_nodes = True
            node = mat.node_tree.nodes.get('Principled BSDF')
            if node:
                node.inputs['Base Color'].default_value = preset_color
            obj.data.materials.append(mat)
            
        return {'FINISHED'}

# Operator to delete all presets
class DeleteAllPresetsOperator(bpy.types.Operator):
    bl_idname = "object.delete_all_presets"
    bl_label = "Delete All Presets"
    
    def execute(self, context):
        context.scene.color_presets.clear()
        return {'FINISHED'}

# Operator to load presets from a file
class LoadPresetsFromFileOperator(bpy.types.Operator):
    bl_idname = "object.load_presets_from_file"
    bl_label = "Load Presets from File"
    
    def execute(self, context):
        try:
            with open(context.scene.filepath, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    parts = line.strip().split(' ')
                    if len(parts) >= 2:
                        hex_color = parts[0]
                        color_name = ' '.join(parts[1:])
                        
                        # Convert hex color to float vector
                        preset_color = [
                            int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5)
                        ] + [1.0]
                        
                        # Add preset
                        preset = context.scene.color_presets.add()
                        preset.color = preset_color
                        preset.name = color_name
                        preset.index = len(context.scene.color_presets) - 1
                self.report({'INFO'}, "Presets loaded successfully.")
        except Exception as e:
            self.report({'ERROR'}, f"Error loading presets: {e}")
        return {'FINISHED'}

# Context Menu for Color Presets
class OBJECT_MT_color_presets_context_menu(bpy.types.Menu):
    bl_label = "Color Presets"
    bl_idname = "OBJECT_MT_color_presets_context_menu"
    
    def draw(self, context):
        layout = self.layout
        for preset in context.scene.color_presets:
            layout.operator("object.update_material_color", text=preset.name).preset_index = preset.index
            layout.operator("object.delete_preset", text="", icon='X').preset_index = preset.index

# Panel for Color Presets
class OBJECT_PT_color_presets_panel(bpy.types.Panel):
    bl_label = "Color Presets"
    bl_idname = "OBJECT_PT_color_presets_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_category = "Color"
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        
        # Add custom color preset
        col.separator()
        col.label(text="Custom Preset:")
        row = col.row(align=True)
        row.prop(context.scene, "custom_preset_color", text="Color")
        row.prop(context.scene, "custom_preset_name", text="Name")
        col.operator("object.add_custom_preset", text="Add Preset")
        
        # Delete all presets button
        col.operator("object.delete_all_presets", text="Delete All Presets", icon='CANCEL')

        # Load presets from file
        col.separator()
        col.label(text="Load Presets from File:")
        col.prop(context.scene, "filepath", text="")

        col.operator("object.load_presets_from_file", text="Load Presets")

        # List presets
        col.separator()
        col.label(text="Presets:")
        for preset in context.scene.color_presets:
            row = col.row(align=True)
            row.operator("object.update_material_color", text=preset.name).preset_index = preset.index
            row.operator("object.delete_preset", text="", icon='X').preset_index = preset.index

# Operator to add custom color preset
class AddCustomPresetOperator(bpy.types.Operator):
    bl_idname = "object.add_custom_preset"
    bl_label = "Add Custom Preset"
    
    def execute(self, context):
        color = context.scene.custom_preset_color
        name = context.scene.custom_preset_name
        
        if color:
            preset = context.scene.color_presets.add()
            preset.color = color
            preset.name = name
            preset.index = len(context.scene.color_presets) - 1  # Set index
            self.report({'INFO'}, "Custom preset added successfully.")
        else:
            self.report({'ERROR'}, "Please select a color for the custom preset.")
        
        return {'FINISHED'}

# Operator to delete preset
class DeletePresetOperator(bpy.types.Operator):
    bl_idname = "object.delete_preset"
    bl_label = "Delete Preset"
    
    preset_index: bpy.props.IntProperty()
    
    def execute(self, context):
        context.scene.color_presets.remove(self.preset_index)
        # Decrement index of presets after the removed one
        for preset in context.scene.color_presets:
            if preset.index > self.preset_index:
                preset.index -= 1
        return {'FINISHED'}

# Register classes and properties
def register():
    bpy.utils.register_class(ColorPreset)
    bpy.utils.register_class(UpdateMaterialColorOperator)
    bpy.utils.register_class(DeleteAllPresetsOperator)
    bpy.utils.register_class(LoadPresetsFromFileOperator)
    bpy.utils.register_class(OBJECT_MT_color_presets_context_menu)
    bpy.utils.register_class(OBJECT_PT_color_presets_panel)
    bpy.utils.register_class(AddCustomPresetOperator)
    bpy.utils.register_class(DeletePresetOperator)
    
    bpy.types.Scene.color_presets = bpy.props.CollectionProperty(type=ColorPreset)
    bpy.types.Scene.custom_preset_color = bpy.props.FloatVectorProperty(
        name="Custom Preset Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),  # Default white color
        min=0.0,
        max=1.0
    )
    bpy.types.Scene.custom_preset_name = bpy.props.StringProperty(name="Custom Preset Name")
    bpy.types.Scene.filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    bpy.types.VIEW3D_MT_object_context_menu.append(draw_menu)

def unregister():
    bpy.utils.unregister_class(ColorPreset)
    bpy.utils.unregister_class(UpdateMaterialColorOperator)
    bpy.utils.unregister_class(DeleteAllPresetsOperator)
    bpy.utils.unregister_class(LoadPresetsFromFileOperator)
    bpy.utils.unregister_class(OBJECT_MT_color_presets_context_menu)
    bpy.utils.unregister_class(OBJECT_PT_color_presets_panel)
    bpy.utils.unregister_class(AddCustomPresetOperator)
    bpy.utils.unregister_class(DeletePresetOperator)
    
    del bpy.types.Scene.color_presets
    del bpy.types.Scene.custom_preset_color
    del bpy.types.Scene.custom_preset_name
    del bpy.types.Scene.filepath

    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_menu)

def draw_menu(self, context):
    self.layout.separator()
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.menu(OBJECT_MT_color_presets_context_menu.bl_idname)

if __name__ == "__main__":
    register()
