# -*- coding: utf-8 -*-

#    <QATM, Blender addon for quick applying tagged materials.>
#    Copyright (C) <2024> <绿毛猫KatGreene>


import bpy
from bpy.app.translations import pgettext


# UI界面
class QATM_PT_custom_panel(bpy.types.Panel):
    """QATM主面板"""
    bl_label = "QATM"
    bl_idname = "QATM_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        mat_assoc_props = scene.mat_association_props

        row = layout.row()
        row.label(text=pgettext("指定优先搜索范围"))
        row.operator("qatm.open_manual_pdf", icon='HELP', text="")
        row = layout.row()
        row.prop(mat_assoc_props, "collection")
        row = layout.row()
        row.scale_y = 1.25
        row.operator("qatm.add_from_collection", icon='COLLECTION_NEW', text=pgettext("导入集合内的材质名"))
        box = layout.box()
        row = box.row()
        row.prop(scene.material_selection_settings, "select_objects_with_mat", text="",  icon="RESTRICT_SELECT_OFF", toggle=True)
        row.label(text=pgettext("应用后选中源物体"))
        row = box.row()
        row.prop(scene.material_link_settings, "link_objects_with_mat", text="",  icon="PRESET_NEW", toggle=True)
        row.label(text=pgettext("关联选择同材质物体"))
        
        self.layout.label(text=pgettext("自定义关键词"))

        row = layout.row()
        row.template_list("QATM_UL_uilist", "The_List", scene, "keyword_list", scene, "keyword_list_index")

        col = row.column(align=True)
        col.operator("qatm.new_item", icon='ADD', text="")
        col.operator("qatm.delete_item", icon='REMOVE', text="")
        col.separator()
        col.operator("qatm.copy_material_of_keyword", icon='CHECKMARK', text="")
        col.separator()
        col.operator("qatm.move_item", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("qatm.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'
        col.separator()
        col.operator("qatm.clear_list", icon="TRASH", text="")
        
        if scene.keyword_list:
            layout.label(text=pgettext("选中词命名"), icon="WORDWRAP_ON")
            item = scene.keyword_list[scene.keyword_list_index]
            col = layout.column(align=False)
            col.prop(item, "name", text="")
            row = col.row(align=True)
            row.operator("qatm.copy_material_of_keyword", icon='CHECKMARK', text=pgettext("应用含此关键词的材质"))


class QATM_PT_custom_panel02(bpy.types.Panel):
    """QATM附加功能面板"""
    bl_label = pgettext("QATM 附加功能")
    bl_idname = "QATM_PT_custom_panel02"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        self.update_label()

        row = layout.row()
        row.label(text=pgettext("追加预设工程中的全部资源"))
        row.operator("qatm.add_resources_all", text="", icon="FILE_BLEND")

    def update_label(self):
        if bpy.app.translations.locale in bpy.app.translations.locales:
            locale = bpy.app.translations.locale
            translated_label = pgettext("QATM 附加功能")
            self.bl_label = translated_label


class QATM_PT_custom_subpanel01(bpy.types.Panel):
    """QATM附加功能面板子面板"""
    bl_label = pgettext("删除多余材质")
    bl_parent_id = "QATM_PT_custom_panel02"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        self.update_label()

        layout.label(text=pgettext("仅删除含关键词的多余材质"))
        row = layout.row()
        row.scale_y = 1.25
        button = row.operator("qatm.delete_unused_materials_by_name", text=pgettext("清理多余材质"), icon="TRASH")

    def update_label(self):
        if bpy.app.translations.locale in bpy.app.translations.locales:
            locale = bpy.app.translations.locale
            translated_label = pgettext("删除多余材质")
            self.bl_label = translated_label


class QATM_PT_custom_subpanel02(bpy.types.Panel):
    """QATM附加功能面板子面板"""
    bl_label = pgettext("描边")
    bl_parent_id = "QATM_PT_custom_panel02"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM' 

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        self.update_label()

        row = layout.row(align=True)
        row.label(text=pgettext("几何节点自适应描边"))
        row.prop(scene.material_link_settings, "link_objects_with_mat", text="",  icon="PRESET_NEW", toggle=True)
        row.operator("qatm.set_brush_button", text="", icon="BRUSHES_ALL")
        row.operator("qatm.add_resources_outline", text="", icon="FILE_BLANK")
        outline_cam_props = scene.outline_camera_props
        outline_mat_props = scene.outline_material_props

        box = layout.box()
        box.label(text=pgettext("指定描边设置"), icon='PRESET')
        col = box.column()
        col.prop(outline_mat_props, "outline_material", text=pgettext("材质"))
        col.prop(outline_cam_props, "outline_camera", text=pgettext("摄像机"))
        row = layout.row()
        row.scale_y = 1.25
        button = row.operator("qatm.add_outline_button", text=pgettext("添加描边"), icon="ADD")
        row.operator("qatm.delete_geometry_nodes_by_name", text=pgettext("删除描边"), icon="X")

    def update_label(self):
        if bpy.app.translations.locale in bpy.app.translations.locales:
            locale = bpy.app.translations.locale
            translated_label = pgettext("描边")
            self.bl_label = translated_label


class QATM_PT_custom_subpanel03(bpy.types.Panel):
    """QATM附加功能面板子面板"""
    bl_label = pgettext("SDF工具")
    bl_parent_id = "QATM_PT_custom_panel02"

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM' 

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        
        sdf_tool = scene.sdf_tool

        self.update_label()

        row = layout.row(align=True)  

        box = layout.box()
        col = box.column()
        col.prop_search(context.scene, "source_armature", bpy.data, "objects", text=pgettext("骨架"))
        col.prop(sdf_tool, "sdf_system_id", text=pgettext("SDF系统ID"))
        row = box.row(align=True)
        row.scale_y = 1.25
        row.label(text="空物体:")
        row.operator("qatm.attach_empty_object", text=pgettext("装载"), icon="SORT_DESC")
        row.operator("qatm.detach_empty_object", text=pgettext("卸载"), icon="SORT_ASC")
        row = box.row(align=True)
        row.scale_y = 1.25
        row.label(text="驱动器:")
        row.operator("qatm.add_drivers_button", text=pgettext("添加"), icon="ADD")
        row.operator("qatm.delete_drivers_nodes", text=pgettext("删除"), icon="X")
        
        row = layout.row(align=True)
        row.operator("qatm.add_new_sdf", text=pgettext("添加新的SDF系统"), icon="ADD")
        row.operator("qatm.unify_sunlight_rotation", text="", icon="LIGHT_SUN")
        row.operator("qatm.add_normal_fix", text="", icon="MOD_NORMALEDIT")     

        row = layout.row(align=True)   
        row.operator("qatm.smooth_normal_to_color", text="平滑法线", icon="LIGHT_HEMI")
        row.operator("qatm.copy_normal_to_color", text="复制法线", icon="LIGHT_AREA")  

        row = layout.row()
        row.template_list("QATM_UL_SDFlist", "The_List_02", scene, "sdf_list", scene, "sdf_list_index")

    def update_label(self):
        if bpy.app.translations.locale in bpy.app.translations.locales:
            locale = bpy.app.translations.locale
            translated_label = pgettext("SDF工具")
            self.bl_label = translated_label
        
        