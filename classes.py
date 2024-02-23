# -*- coding: utf-8 -*-

#    <QATM, Blender addon for quick applying tagged materials.>
#    Copyright (C) <2024> <绿毛猫KatGreene>


import bpy
import os
import subprocess
from . import functions as func
from bpy.props import StringProperty
from bpy.types import Operator, UIList, PropertyGroup
from bpy.app.translations import pgettext
from gettext import gettext


class TOOL_OT_AddResourcesOutline(bpy.types.Operator):
    bl_idname = "tool.add_resources_outline"
    bl_label = gettext("追加资源")
    bl_description = gettext("追加描边节点组与描边材质")

    def execute(self, context):

        collection_exists = func.check_scene_for_collection_name("QATM_OutLine")

        # 执行这个功能前的检查
        if not collection_exists:
            func.load_resources(["Collection/QATM_OutLine"])

            def draw(self, context):
                self.layout.label(text=gettext("成功加载资源"), icon='SEQUENCE_COLOR_03')
                self.layout.label(text="")
            bpy.context.window_manager.popup_menu(draw)
        else:
            def draw(self, context):
                self.layout.label(text=gettext("未加载资源：该资源已加载过!"), icon='SEQUENCE_COLOR_01')
                self.layout.label(text="")
            bpy.context.window_manager.popup_menu(draw)

        bpy.ops.ed.undo_push(message=pgettext(gettext("QATM: 追加资源")))
        return {'FINISHED'}
    

class TOOL_OT_AddResourcesAll(bpy.types.Operator):
    bl_idname = "tool.add_resources_all"
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
                self.layout.label(text=gettext("成功加载资源"), icon='SEQUENCE_COLOR_03')
                self.layout.label(text="")
            bpy.context.window_manager.popup_menu(draw)
        else:
            def draw(self, context):
                self.layout.label(text=gettext("未加载资源：该资源已加载过!"), icon='SEQUENCE_COLOR_01')
                self.layout.label(text="")
            bpy.context.window_manager.popup_menu(draw)

        bpy.ops.ed.undo_push(message=gettext("QATM: 追加资源"))
        return {'FINISHED'}


class TOOL_OT_ConfirmResourceLoad(bpy.types.Operator):
    bl_idname = "tool.confirm_resource_load"
    bl_label = "确认资源加载"

    def execute(self, context):
        func.load_resources(['Object/000OutLine'])  # 加载资源的逻辑
        func.mark_append_function_as_executed()  # 标记完成
        bpy.ops.ed.undo_push(message="Add resources: resource loaded")
        return {'FINISHED'}


class TOOL_OT_SetBrush(bpy.types.Operator):
    bl_idname = "tool.set_brush_button"
    bl_label = "快捷设置参数"
    bl_description = "设置权重笔刷值为0 并取消仅前面的面"

    def execute(self, context):
        bpy.context.scene.tool_settings.unified_paint_settings.weight = 0
        bpy.data.brushes["Draw"].use_frontface = False
        return {'FINISHED'}

    
class OBJECT_OT_AddOutlineButton(bpy.types.Operator):
    bl_idname = "object.add_outline_button"
    bl_label = "添加描边"
    bl_description = "给选定的物体添加一个名为‘000OutLine’的几何节点组"

    def execute(self, context):
        func.add_outline_to_selected_objects()
        return {'FINISHED'}
    

# 操作类用于删除选中物体中名为"000OutLine"的几何节点修改器
class WM_OT_DeleteGeometryNodesByName(bpy.types.Operator):
    """删除选定的物体中名为'000OutLine'的几何节点修改器"""
    bl_idname = "wm.delete_geometry_nodes_by_name"
    bl_label = "删除'000OutLine'修改器"

    def execute(self, context):
        func.delete_geometry_node_modifiers("000OutLine")
        bpy.ops.ed.undo_push(message="QATM: 删除描边")
        return {'FINISHED'}
    

### 添加一个指向集合的属性
class MaterialAssociationProperties(bpy.types.PropertyGroup):
    collection: bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection
    ) # type: ignore


### 添加一个指向摄像机的属性
class OutlineCameraProperties(bpy.types.PropertyGroup):
    outline_camera: bpy.props.PointerProperty(
        name="描边摄像机",
        type=bpy.types.Object,
        # 通过指定 poll 方法，可以确保只有摄像机对象能被赋值给此属性
        poll=lambda self, object: object.type == 'CAMERA'
    ) # type: ignore


### 添加一个指向描边材质的属性
class OutlineMaterialProperties(bpy.types.PropertyGroup):
    outline_material: bpy.props.PointerProperty(
        name="描边材质",
        type=bpy.types.Material,
    ) # type: ignore
    

class CustomIntProperties(bpy.types.PropertyGroup):
    sdf_system_id: bpy.props.IntProperty(
        name="SDF系统",
        description="SDF系统整数ID",
        default=0,
        min=0,
        max=64
    ) # type: ignore


### 添加布尔属性
class MaterialSelectionSettings(bpy.types.PropertyGroup):
    select_objects_with_mat: bpy.props.BoolProperty(
        name="应用后选中源物体",
        description="QATM: 点击切换设置",
        default=False
    ) # type: ignore

class MaterialLinkSettings(bpy.types.PropertyGroup):
    link_objects_with_mat: bpy.props.BoolProperty(
        name="应用前关联选择同材质物体",
        description="QATM: 点击切换设置",
        default=False
    ) # type: ignore


#UI操作类
class BaseCopyMaterialOperator(bpy.types.Operator):
    """基础复制材质操作类"""
    bl_idname = "material.copy_base"
    bl_label = "复制基础材质"
    material_suffix = ""

    def execute(self, context):
        func.copy_material_to_selected_objects(self.material_suffix)
        bpy.ops.ed.undo_push(message="QATM: 匹配材质")
        return {'FINISHED'}

# 应用列表中关键词的材质
class QATM_OT_copy_material_of_keyword(BaseCopyMaterialOperator):
    bl_idname = "material.copy_material_of_keyword"
    bl_label = "应用含此关键词的材质"
    
    @classmethod
    def poll(cls, context):
        return context.scene.keyword_list_index >= 0 and len(context.scene.keyword_list) > 0

    def execute(self, context):
        scene = context.scene
        index = scene.keyword_list_index
        if len(scene.keyword_list) == 1:
            scene.suffix = scene.keyword_list[index-1].name
        else:
            scene.suffix = scene.keyword_list[index].name
        func.copy_material_to_selected_objects(scene.suffix)

        bpy.ops.ed.undo_push(message="QATM: 匹配材质")
        return {'FINISHED'}
    

### UIList部分 定义关键词项属性
class KeywordItem(PropertyGroup):
    name: StringProperty(
           name="Keyword",
           description="A keyword",
           default="Keyword") # type: ignore

# 列表 UI 类
class KEYWORDS_UL_uilist(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'WORDWRAP_ON' if item else 'WORDWRAP_OFF'
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            
            row = layout.row(align=True)
            row.label(text=item.name, icon = 'SEQ_CHROMA_SCOPE')
            
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            
            row = layout.row(align=True)
            row.label(text="", icon = 'SEQ_CHROMA_SCOPE')

# 添加关键词操作
class KEYWORDS_OT_NewItem(Operator):
    bl_idname = "qatm.new_item"
    bl_label = "添加新关键词"
    
    @classmethod
    def poll(cls, context):
        # 这个方法决定了操作是否可以执行
        return context.scene is not None

    def execute(self, context):
        keyword_list = context.scene.keyword_list
        index = context.scene.keyword_list_index
        
        # 假设新关键词的基础名称是"Keyword"
        base_name = "Keyword"
        new_name = base_name
        
        # 查找列表中是否已存在该名称，如果存在则调整名称
        existing_names = [item.name for item in keyword_list]
        counter = 1
        while new_name in existing_names:
            new_name = "{}.{:03d}".format(base_name, counter) # 如果存在重复名称，添加后缀
            counter += 1
            
        # 创建新关键词
        new_item = keyword_list.add()
        new_item.name = new_name  # 设置新关键词的名称，防止重复
        
        # 插入新关键词在当前选中关键词之后
        new_index = index + 1 if keyword_list else 0

        # 将新元素移动到新索引位置
        keyword_list.move(len(keyword_list) - 1, new_index)
        
        # 更新当前选中关键词到新添加的关键词
        context.scene.keyword_list_index = new_index

        # 执行添加操作后，手动推送撤销步骤
        bpy.ops.ed.undo_push(message="QATM: 添加关键词")
        
        return {'FINISHED'}

# 从集合添加关键词操作    
class KEYWORDS_OT_AddFromCollection(Operator):
    bl_idname = "qatm.add_from_collection"
    bl_label = "从集合添加关键词"
    bl_description = "导入集合内的所有材质名到自定义关键词列表"
    
    @classmethod
    def poll(cls, context):
        # 检查是否存在用于添加关键词的集合
        return hasattr(context.scene, "mat_association_props") and hasattr(context.scene.mat_association_props, "collection")
        
    def execute(self, context):
        # 获取集合内的所有物体
        collection = context.scene.mat_association_props.collection
        
        # 确保存在关键词列表属性 (确保可以添加关键字)
        if not hasattr(context.scene, "keyword_list"):
            self.report({'ERROR'}, "Scene 中不存在 keyword_list 属性")
            return {'CANCELLED'}
        
        # 创建一个集合用来存储已有的关键词名
        existing_keywords = {kw.name for kw in context.scene.keyword_list}
        
        # 遍历集合中的每个物体
        if hasattr(collection, "objects"):
            for obj in collection.objects:
                # 遍历对象的每个材质槽
                for slot in obj.material_slots:
                    # 检查材质槽是否有材质
                    if slot.material:
                        material_name = slot.material.name
                        # 若关键词列表中不存在当前材质名，则添加到列表中
                        if material_name not in existing_keywords:
                            keyword_item = context.scene.keyword_list.add()
                            keyword_item.name = material_name
                            # 将新添加的材质名加入到已有关键词集合中
                            existing_keywords.add(material_name)

        bpy.ops.ed.undo_push(message="QATM: 从集合添加关键词")

        return {'FINISHED'}

# 删除关键词操作
class KEYWORDS_OT_DeleteItem(Operator):
    bl_idname = "qatm.delete_item"
    bl_label = "删除此关键词"
    
    @classmethod
    def poll(cls, context):
        return context.scene.keyword_list

    def execute(self, context):
        keyword_list = context.scene.keyword_list
        index = context.scene.keyword_list_index

        keyword_list.remove(index)
        if index < len(keyword_list):  # 当前位置有下一个元素
            context.scene.keyword_list_index = index
        else:  # 删除的是列表中的最后一个元素
            context.scene.keyword_list_index = max(0, len(keyword_list) - 1)
        
        bpy.ops.ed.undo_push(message="QATM: 移除关键词")

        return {'FINISHED'}

# 清除所有关键词
class KEYWORDS_OT_ClearList(Operator):
    bl_idname = "qatm.clear_list"
    bl_label = "清除所有关键词"
    
    @classmethod
    def poll(cls, context):
        # 只有关键词列表存在且不为空时，此操作才有效
        return hasattr(context.scene, "keyword_list") and context.scene.keyword_list
    
    def execute(self, context):
        keyword_list = context.scene.keyword_list
        
        # 从最后一个元素开始删除，直到列表为空
        while keyword_list:
            keyword_list.remove(len(keyword_list) - 1)
        
        # 重置当前选中的列表索引
        context.scene.keyword_list_index = 0

        bpy.ops.ed.undo_push(message="QATM: 清除关键词")

        return {'FINISHED'}


# 移动关键词操作
class KEYWORDS_OT_MoveItem(Operator):
    bl_idname = "qatm.move_item"
    bl_label = "移动此关键词"
    
    direction: bpy.props.EnumProperty(items=(
        ('UP', 'Up', ""),
        ('DOWN', 'Down', ""),
        )) # type: ignore
    
    @classmethod
    def poll(cls, context):
        return context.scene.keyword_list

    def move_index(self):
        """ 移动此关键词并限制范围 """

        index = bpy.context.scene.keyword_list_index
        list_length = len(bpy.context.scene.keyword_list) - 1

        new_index = min(max(0, index + (-1 if self.direction == 'UP' else 1)), list_length)

        bpy.context.scene.keyword_list_index = new_index

    def execute(self, context):
        keyword_list = context.scene.keyword_list
        index = context.scene.keyword_list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        keyword_list.move(neighbor, index)
        self.move_index()

        bpy.ops.ed.undo_push(message="QATM: 移动关键词")

        return {'FINISHED'}
    

# 运算符，执行删除操作
class WM_OT_DeleteUnusedMaterialsByName(bpy.types.Operator):
    """删除未使用且名称匹配的材质"""
    bl_idname = "wm.delete_unused_materials_by_name"
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
        # 获取插件的文件路径（假设本操作文件与 'manual' 文件夹位于同一目录）
        file_path = os.path.join(os.path.dirname(__file__), 'manual', 'manual_zh-CN.pdf')
        
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
    
