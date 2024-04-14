# -*- coding: utf-8 -*-

#    <QATM, Blender addon for quick applying tagged materials.>
#    Copyright (C) <2024> <绿毛猫KatGreene>


import bpy
import os
import subprocess
from . import functions as func
from . import normalEdit as norm
from bpy.app.translations import pgettext
from gettext import gettext
from mathutils import *
from math import *


class QATM_OT_AddResourcesOutline(bpy.types.Operator):
    bl_idname = "qatm.add_resources_outline"
    bl_label = pgettext("追加资源/Append Resources")
    bl_description = gettext("追加描边节点组与描边材质")

    def execute(self, context):

        collection_exists = func.check_scene_for_collection_name("QATM_OutLine")

        # 执行这个功能前的检查
        if not collection_exists:
            func.load_resources(["Collection/QATM_OutLine"])

            def draw(self, context):
                self.layout.label(text=pgettext("成功加载资源"), icon='SEQUENCE_COLOR_03')
                self.layout.label(text="")
            bpy.context.window_manager.popup_menu(draw)
        else:
            def draw(self, context):
                self.layout.label(text=pgettext("未加载资源：该资源已加载过!"), icon='SEQUENCE_COLOR_01')
                self.layout.label(text="")
            bpy.context.window_manager.popup_menu(draw)

        bpy.ops.ed.undo_push(message=pgettext(gettext("QATM: 追加资源")))
        return {'FINISHED'}
    

class QATM_OT_AddResourcesAll(bpy.types.Operator):
    bl_idname = "qatm.add_resources_all"
    bl_label = gettext("手动追加全部资源")
    bl_description = gettext("追加预设工程中的全部节点组/材质/物体")

    def execute(self, context):

        collection_exists = func.check_scene_for_collection_name("QATM_Resources")
        collection_exists_outline = func.check_scene_for_collection_name("QATM_OutLine")

        # 执行这个功能前的检查
        if not collection_exists:
            func.load_resources(["Collection/QATM_Resources"])
            if not collection_exists_outline:
                func.load_resources(["Collection/QATM_OutLine"])

            def draw(self, context):
                self.layout.label(text=pgettext("成功加载资源"), icon='SEQUENCE_COLOR_03')
                self.layout.label(text="")
            bpy.context.window_manager.popup_menu(draw)
        else:
            def draw(self, context):
                self.layout.label(text=pgettext("未加载资源：该资源已加载过!"), icon='SEQUENCE_COLOR_01')
                self.layout.label(text="")
            bpy.context.window_manager.popup_menu(draw)

        bpy.ops.ed.undo_push(message=gettext("QATM: 追加资源"))
        return {'FINISHED'}


class QATM_OT_ConfirmResourceLoad(bpy.types.Operator):
    bl_idname = "qatm.confirm_resource_load"
    bl_label = "确认资源加载"

    def execute(self, context):
        func.load_resources(['Object/000OutLine'])  # 加载资源的逻辑
        func.mark_append_function_as_executed()  # 标记完成
        bpy.ops.ed.undo_push(message="Add resources: resource loaded")
        return {'FINISHED'}


class QATM_OT_SetBrush(bpy.types.Operator):
    bl_idname = "qatm.set_brush_button"
    bl_label = "快捷设置参数"
    bl_description = "设置权重笔刷值为0 并取消仅前面的面"

    def execute(self, context):
        bpy.context.scene.tool_settings.unified_paint_settings.weight = 0
        bpy.data.brushes["Draw"].use_frontface = False
        bpy.ops.ed.undo_push(message="QATM: 设置笔刷")
        return {'FINISHED'}

    
class QATM_OT_AddOutlineButton(bpy.types.Operator):
    bl_idname = "qatm.add_outline_button"
    bl_label = "添加描边"
    bl_description = "给选定的物体添加一个名为‘QATM_OutLine’的几何节点组"

    def execute(self, context):
        func.add_outline_to_selected_objects()
        bpy.ops.ed.undo_push(message="QATM: 添加描边")
        return {'FINISHED'}
    

class QATM_OT_AddDriversButton(bpy.types.Operator):
    bl_idname = "qatm.add_drivers_button"
    bl_label = "添加描边"
    bl_description = "给选定的物体添加一个名为‘QATM_Drivers’的几何节点组"

    def execute(self, context):
        func.add_drivers_to_selected_objects()
        bpy.ops.ed.undo_push(message="QATM: 添加驱动")
        return {'FINISHED'}
    

# 操作类用于删除选中物体中名为"QATM_OutLine"的几何节点修改器
class QATM_OT_DeleteGeometryNodesByName(bpy.types.Operator):
    """删除选定的物体中名为'QATM_OutLine'的几何节点修改器"""
    bl_idname = "qatm.delete_geometry_nodes_by_name"
    bl_label = "删除'QATM_OutLine'修改器"

    def execute(self, context):
        func.delete_geometry_node_modifiers("QATM_OutLine")
        bpy.ops.ed.undo_push(message="QATM: 删除描边")
        return {'FINISHED'}
    

# 操作类用于删除选中物体中名为"QATM_Drivers"的几何节点修改器
class QATM_OT_DeleteDriversNodes(bpy.types.Operator):
    """删除选定的物体中名为'QATM_Drivers'的几何节点修改器"""
    bl_idname = "qatm.delete_drivers_nodes"
    bl_label = "删除'QATM_Drivers'修改器"

    def execute(self, context):
        func.delete_geometry_node_modifiers("QATM_Drivers")
        bpy.ops.ed.undo_push(message="QATM: 删除驱动器")
        return {'FINISHED'}
    

# 运算符，执行删除操作
class QATM_OT_DeleteUnusedMaterialsByName(bpy.types.Operator):
    """删除未使用且名称匹配的材质"""
    bl_idname = "qatm.delete_unused_materials_by_name"
    bl_label = "删除未使用的匹配材质"

    # 当按钮被按下时执行的方法
    def execute(self, context):
        names_to_check = func.collect_keyword_names(bpy.context)
        func.delete_unused_materials_by_name(names_to_check)
        bpy.ops.ed.undo_push(message="QATM: 清理多余材质")
        return {'FINISHED'}


# 打开pdf手册
class QATM_OT_OpenManualPDF(bpy.types.Operator):
    bl_idname = "qatm.open_manual_pdf"
    bl_label = "查看手册"
    bl_description = "打开并查看用户PDF使用手册"

    def execute(self, context):
        # 获取当前文件路径
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # 得到上级目录的路径
        parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
        # 构造到上级目录中的resources文件夹的路径
        file_path = os.path.join(parent_dir_path, 'manual', 'manual_zh-CN.pdf')
        
        # 确保文件存在
        if not os.path.isfile(file_path):
            self.report({'ERROR'}, 'Manual PDF file is missing.')
            return {'CANCELLED'}
        
        # 试图打开PDF文件，这里使用默认的PDF阅读器
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        else:
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.call([opener, file_path])

        return {'FINISHED'}
 

class QATM_OT_SmoothNormalToUV(bpy.types.Operator):
    bl_idname = "qatm.smooth_normal_to_color"
    bl_label = "平滑法线到UV"
    bl_description = "为选中模型执行平滑法线并存入UV"


    def execute(self, context):
        selected_objects = bpy.context.selected_objects

        for obj in selected_objects:
            if obj is None or obj.type != 'MESH':
                continue

            norm.smooth_normal_to_uv(obj)
        
        bpy.ops.ed.undo_push(message="QATM: 平滑法线到UV")
        return {'FINISHED'}


class QATM_OT_CopyNormalToUV(bpy.types.Operator):
    bl_idname = "qatm.copy_normal_to_color"
    bl_label = "复制法线到UV"
    bl_description = "将选中模型法线存入UV"


    def execute(self, context):
        selected_objects = bpy.context.selected_objects

        for obj in selected_objects:
            if obj is None or obj.type != 'MESH':
                continue

            norm.copy_normal_to_uv(obj)

        bpy.ops.ed.undo_push(message="QATM: 复制法线到UV")
        return {'FINISHED'}
    

