# -*- coding: utf-8 -*-

#    <QATM, Blender addon for quick applying tagged materials.>
#    Copyright (C) <2024> <绿毛猫KatGreene>


import bpy

from bpy.types import Panel

###UI界面
class QATM_PT_custom_panel(bpy.types.Panel):
    """创建一个在N键属性栏中的自定义面板"""
    bl_label = "QATM 快速应用含同名材质"
    bl_idname = "QATM_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        mat_assoc_props = scene.mat_association_props

        layout.label(text="指定优先搜索范围")
        layout.prop(mat_assoc_props, "collection")
        row = layout.row()
        row.operator("qatm.add_from_collection", icon='COLLECTION_NEW', text="导入集合内的材质名")
        box = layout.box()
        row = box.row()
        row.prop(scene.material_selection_settings, "select_objects_with_mat", text="",  icon="RESTRICT_SELECT_OFF", toggle=True)
        row.label(text="应用后选中源物体")
        row = box.row()
        row.prop(scene.material_link_settings, "link_objects_with_mat", text="",  icon="PRESET_NEW", toggle=True)
        row.label(text="关联选择同材质物体")
        
            
class QATM_PT_custom_default_subpanel(bpy.types.Panel):
    bl_label = "内置关键词"
    bl_parent_id = "QATM_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.use_property_split = False
        layout.use_property_decorate = False

        box = layout.box()
        row = box.row(align=True)
        row.operator("material.copy_material_01skin", icon="SHADING_SOLID", text="01Skin")
        row.operator("material.copy_material_02hair", icon="MATSPHERE", text="02Hair")  
        row = box.row(align=True) 
        row.operator("material.copy_material_03clos", icon="SHADING_RENDERED")
        row.operator("material.copy_material_04clor", icon="SHADING_TEXTURE")
        row = box.row(align=True) 
        row.operator("material.copy_material_05metl", icon="NODE_MATERIAL")
        row.operator("material.copy_material_06eyes", icon="ANTIALIASED")
        row = box.row(align=True) 
        row.operator("material.copy_material_07stks", icon="PROP_ON")
        

class QATM_PT_keyword_subpanel(Panel):
    bl_label = "自定义关键词"
    bl_parent_id = "QATM_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.template_list("KEYWORDS_UL_uilist", "The_List", scene, "keyword_list", scene, "keyword_list_index")

        col = row.column(align=True)
        col.operator("qatm.new_item", icon='ADD', text="")
        col.operator("qatm.delete_item", icon='REMOVE', text="")
        col.separator()
        col.operator("material.copy_material_of_keyword", icon='CHECKMARK', text="")
        col.separator()
        col.operator("qatm.move_item", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("qatm.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'
        col.separator()
        col.operator("qatm.clear_list", icon="TRASH", text="")
        
        if scene.keyword_list:
            layout.label(text="选中词命名", icon="WORDWRAP_ON")
            item = scene.keyword_list[scene.keyword_list_index]
            col = layout.column(align=False)
            col.prop(item, "name", text="")
            row = col.row(align=True)
            row.operator("material.copy_material_of_keyword", icon='CHECKMARK', text="应用含此关键词的材质")
            row = layout.row()
            row.operator("material.copy_material_of_keyword", icon='ADD', text="加载内置关键词")


class QATM_PT_custom_panel02(bpy.types.Panel):
    """创建一个在N键属性栏中的自定义面板"""
    bl_label = "QATM 附加功能"
    bl_idname = "QATM_PT_custom_panel02"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.label(text="追加预设工程中的全部资源")
        row.operator("tool.add_resources_all", text="", icon="FILE_BLEND")


class QATM_PT_custom_subpanel01(bpy.types.Panel):
    """创建一个在N键属性栏中的自定义面板"""
    bl_label = "删除多余材质"
    bl_parent_id = "QATM_PT_custom_panel02"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="仅删除含关键词的多余材质")
        row = layout.row()
        row.scale_y = 1.5
        button = row.operator("wm.delete_unused_materials_by_name", text="清理多余材质", icon="TRASH")


class QATM_PT_custom_subpanel02(bpy.types.Panel):
    """创建一个在N键属性栏中的自定义面板"""
    bl_label = "描边"
    bl_parent_id = "QATM_PT_custom_panel02"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM' 

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row(align=True)
        row.label(text="几何节点自适应描边")
        row.prop(scene.material_link_settings, "link_objects_with_mat", text="",  icon="PRESET_NEW", toggle=True)
        row.operator("tool.set_brush_button", text="", icon="BRUSHES_ALL")
        row.operator("tool.add_resources_outline", text="", icon="FILE_BLANK")
        outline_cam_props = scene.outline_camera_props
        outline_mat_props = scene.outline_material_props

        box = layout.box()
        box.label(text="指定描边设置", icon='PRESET')
        col = box.column()
        col.prop(outline_mat_props, "outline_material", text="材质")
        col.prop(outline_cam_props, "outline_camera", text="摄像机")
        row = layout.row()
        row.scale_y = 1.5
        button = row.operator("object.add_outline_button", text="添加描边", icon="ADD")
        row.operator("wm.delete_geometry_nodes_by_name", text="删除描边", icon="X")


class QATM_PT_custom_subpanel03(bpy.types.Panel):
    """创建一个自定义面板类"""
    bl_label = "装载SDF空物体"
    bl_parent_id = "QATM_PT_custom_panel02"

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM' 

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        
        sdf_tool = scene.sdf_tool

        # 创建选择框
        box = layout.box()
        col = box.column()
        col.prop_search(context.scene, "source_armature", bpy.data, "objects", text="骨架")
        col.prop(sdf_tool, "sdf_system_id", text="SDF系统ID")
        
        # 创建按钮
        row = layout.row()
        row.scale_y = 1.5
        row.operator("object.attach_empty_object", text="装载空物体", icon="SORT_DESC")
        row.operator("object.detach_empty_object", text="卸载空物体", icon="SORT_ASC")
        row = layout.row(align=True)
        row.operator("object.add_new_sdf", text="添加新的SDF系统", icon="ADD")
        row.operator("qatm.unify_sunlight_rotation", text="", icon="LIGHT_SUN")
        row.operator("qatm.add_normal_fix", text="", icon="MOD_NORMALEDIT")


class QATM_PT_custom_subpanel04(bpy.types.Panel):
    """创建一个自定义面板类"""
    bl_label = "图像处理"
    bl_parent_id = "QATM_PT_custom_panel02"

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM' 

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        
        sdf_tool = scene.sdf_tool

        # 创建选择框
        box = layout.box()
        col = box.column()
        col.prop_search(context.scene, "source_armature", bpy.data, "objects", text="骨架")
        col.prop(sdf_tool, "sdf_system_id", text="SDF系统ID")
        
        # 创建按钮
        row = layout.row()
        row.scale_y = 1.5
        row.operator("object.attach_empty_object", text="装载空物体", icon="SORT_DESC")
        row.operator("object.detach_empty_object", text="卸载空物体", icon="SORT_ASC")
        row = layout.row(align=True)
        row.operator("object.add_new_sdf", text="添加新的SDF系统", icon="ADD")
        row.operator("qatm.unify_sunlight_rotation", text="", icon="LIGHT_SUN")
        row.operator("qatm.add_normal_fix", text="", icon="MOD_NORMALEDIT")
        
        
        