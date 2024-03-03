import bpy
import re

bl_info = {
    "name": "Color Presets Add-on",
    "author": "Nomadic_Jester",
    "version": (1, 1),
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

# Context Menu for Color Presets
class OBJECT_MT_color_presets_context_menu(bpy.types.Menu):
    bl_label = "Color Presets"
    bl_idname = "OBJECT_MT_color_presets_context_menu"
    
    def draw(self, context):
        layout = self.layout
        for preset in context.scene.color_presets:
            layout.operator("object.update_material_color", text=preset.name).preset_index = preset.index

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
        
        # Load presets from file
        col.separator()
        col.label(text="Load Presets from File:")
        row = col.row(align=True)
        row.operator("object.select_file_to_load_presets", text="Select File")
        row.operator("object.load_presets_from_file", text="Load Presets")

        # List presets
        col.separator()
        col.label(text="Presets:")
        for preset in context.scene.color_presets:
            row = col.row(align=True)
            row.operator("object.update_material_color", text=preset.name).preset_index = preset.index

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

# Operator to open file browser for selecting file
class SelectFileToLoadPresetsOperator(bpy.types.Operator):
    bl_idname = "object.select_file_to_load_presets"
    bl_label = "Select File to Load Presets"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        # Set the file path from the operator's property
        context.scene.filepath = self.filepath
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # Open file browser
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "filepath", text="File Path")

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

# Define the draw_menu function
def draw_menu(self, context):
    self.layout.separator()
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.menu(OBJECT_MT_color_presets_context_menu.bl_idname)

def register():
    bpy.utils.register_class(ColorPreset)
    bpy.utils.register_class(UpdateMaterialColorOperator)
    bpy.utils.register_class(OBJECT_MT_color_presets_context_menu)
    bpy.utils.register_class(OBJECT_PT_color_presets_panel)
    bpy.utils.register_class(AddCustomPresetOperator)
    bpy.utils.register_class(SelectFileToLoadPresetsOperator)
    bpy.utils.register_class(LoadPresetsFromFileOperator)
    
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
    bpy.utils.unregister_class(OBJECT_MT_color_presets_context_menu)
    bpy.utils.unregister_class(OBJECT_PT_color_presets_panel)
    bpy.utils.unregister_class(AddCustomPresetOperator)
    bpy.utils.unregister_class(SelectFileToLoadPresetsOperator)
    bpy.utils.unregister_class(LoadPresetsFromFileOperator)
    
    del bpy.types.Scene.color_presets
    del bpy.types.Scene.custom_preset_color
    del bpy.types.Scene.custom_preset_name
    del bpy.types.Scene.filepath

    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_menu)

if __name__ == "__main__":
    register()
