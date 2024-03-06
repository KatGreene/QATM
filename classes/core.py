# -*- coding: utf-8 -*-

#    <QATM, Blender addon for quick applying tagged materials.>
#    Copyright (C) <2024> <绿毛猫KatGreene>


import bpy
from . import functions as func
from bpy.props import StringProperty
from bpy.types import Operator, UIList, PropertyGroup


#UI操作类
class QATM_BaseCopyMaterialOperator(bpy.types.Operator):
    """基础复制材质操作类"""
    bl_idname = "qatm.copy_base"
    bl_label = "复制基础材质"
    material_suffix = ""

    def execute(self, context):
        func.copy_material_to_selected_objects(self.material_suffix)
        bpy.ops.ed.undo_push(message="QATM: 匹配材质")
        return {'FINISHED'}


# 应用列表中关键词的材质
class QATM_OT_copy_material_of_keyword(QATM_BaseCopyMaterialOperator):
    bl_idname = "qatm.copy_material_of_keyword"
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
class QATM_KeywordItem(PropertyGroup):
    name: StringProperty(
           name="Keyword",
           description="A keyword",
           default="Keyword") # type: ignore


# 列表 UI 类
class QATM_UL_uilist(UIList):

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
class QATM_OT_NewItem(Operator):
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
class QATM_OT_AddFromCollection(Operator):
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
class QATM_OT_DeleteItem(Operator):
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
class QATM_OT_ClearList(Operator):
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
class QATM_OT_MoveItem(Operator):
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
    
