# -*- coding: utf-8 -*-

#    <QATM, Blender addon for quick applying tagged materials.>
#    Copyright (C) <2024> <绿毛猫KatGreene>
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
bl_info = {
    "name": "QATM",
    "author": "绿毛猫KatGreene",
    "version": (0, 2),
    "blender": (3, 6, 0),
    "location": "View3D > Toolbar",
    "description": "Quick Apply Tagged Material 快速应用含同名材质",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"  # 插件在哪个类别下显示
}




### 加描边功能
def add_outline_to_selected_objects():
    # 检查并创建一个名为"000OutLine"的节点组（如果尚不存在）
    outline_node_group = bpy.data.node_groups.get("000OutLine")
    
    # 获取当前选择的所有物体
    selected_objects = bpy.context.selected_objects

    # 对所有选中的物体执行操作
    for obj in selected_objects:
        if obj.type == 'MESH':  # 确保只处理网格类型的物体

            # 创建新的几何节点修改器
            geo_node_mod = obj.modifiers.new(type="NODES", name="000OutLine")

            # 设置修改器的节点组为描边节点组
            geo_node_mod.node_group = outline_node_group

# UI操作类
class OBJECT_OT_AddOutlineButton(bpy.types.Operator):
    bl_idname = "object.add_outline_button"
    bl_label = "添加描边"
    bl_description = "给选定的物体添加一个名为‘000OutLine’的几何节点组"

    def execute(self, context):
        add_outline_to_selected_objects()
        return {'FINISHED'}




### 删除选中物体的所有名为"000OutLine"的几何节点修改器
def delete_geometry_node_modifiers(named):
    for obj in bpy.context.selected_objects:  # 遍历场景中的所有选中物体
        # 确保我们只对网格类型的物体进行操作
        if obj.type == 'MESH':
            # 遍历物体的修改器
            modifiers_to_remove = [mod for mod in obj.modifiers if mod.type == 'NODES' and named in mod.name]
            for modifier in modifiers_to_remove:
                obj.modifiers.remove(modifier)

# 操作类用于删除选中物体中名为"000OutLine"的几何节点修改器
class WM_OT_DeleteGeometryNodesByName(bpy.types.Operator):
    """删除场景中物体名为'000OutLine'的几何节点修改器"""
    bl_idname = "wm.delete_geometry_nodes_by_name"
    bl_label = "删除'000OutLine'修改器"

    def execute(self, context):
        delete_geometry_node_modifiers("000OutLine")
        return {'FINISHED'}




### 添加一个指向集合的属性
class MaterialAssociationProperties(bpy.types.PropertyGroup):
    collection: bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection
    )




### 加材质功能
def copy_material_to_selected_objects(mat_name):
    scene = bpy.context.scene

    selected_objects = bpy.context.selected_objects
    if not selected_objects:
        return  # 如果没有选中的物体，直接返回
    
    # 查找是否存在指定名称的材质
    original_image_textures = None
    mat = None

    collection = scene.mat_association_props.collection

    material_to_copy = None
    # 如果选中了集合，则从该集合内的物体搜索匹配的材质
    if collection:
        for obj in collection.objects:
            for mat_slot in obj.material_slots:
                if mat_slot.material and mat_name in mat_slot.material.name:
                    material_to_copy = mat_slot.material
                    break  # 找到匹配的材质，停止搜索
            if material_to_copy:  # 如果已找到材质，不需要进一步搜索
                break
    
    # 否则，在全局范围内搜索匹配的材质
    else:
        for mat in bpy.data.materials:
            if mat_name in mat.name:
                material_to_copy = mat
                break

    # 存储材质名称和材质的映射，避免创建不必要的副本
    material_mapping = {}

    for obj in selected_objects:
        if obj.type == 'MESH':
            # 如果没有材质，则新建材质
            if len(obj.material_slots) == 0:
                new_mat = bpy.data.materials.new(name=obj.name)
                obj.data.materials.append(new_mat)
            
            if obj.type == 'MESH' and len(obj.material_slots) > 0:
                # 获取原材质中图像纹理所关联的图像
                original_image_textures = {}
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material.use_nodes:
                        for node in mat_slot.material.node_tree.nodes:
                            if node.type == 'TEX_IMAGE':
                                original_image_textures[node.location.y] = node.image
        
                # 仅当有要复制的材料时进行复制
                if material_to_copy:
                # 为每个唯一的材质数据块创建一个材料映射关系
                    for mat_slot in obj.material_slots:
                        if mat_slot.material:
                            original_mat_name = mat_slot.material.name
                            # 检查映射中是否已经存在这个材质data的副本
                            if original_mat_name in material_mapping:
                                # 使用已经创建的副本
                                new_mat = material_mapping[original_mat_name]
                            else:
                                # 创建新的副本，并更新映射
                                new_mat = material_to_copy.copy()

                            # 处理原有材料名称
                            processed_original_name = remove_keywords(original_mat_name, names_to_check)
                            new_mat.name = f'{material_to_copy.name}_{processed_original_name}'

                            material_mapping[original_mat_name] = new_mat

                    obj.data.materials[0] = new_mat

                    # 按照节点树Y方向位置顺序排序
                    sorted_images = [image for key, image in sorted(original_image_textures.items(), reverse=True)]
                    if sorted_images:  # 防止除数为0
                        # 用原图像替换新图像
                        i = 0
                        for node in new_mat.node_tree.nodes:
                            if node.type == 'TEX_IMAGE':
                                index = i % len(sorted_images)
                                node.image = sorted_images[index]
                                i += 1

# 声明一个函数用于处理原名称
def remove_keywords(original_name, keywords):
    new_name = original_name
    for keyword in keywords:
        # 如果关键词存在于原材料名称
        if keyword in new_name:
            # 找到关键词后面的部分（包括关键词本身）
            key_and_trailing = f'{keyword}_'
            # 用替换方法移除关键词和它后面的下划线
            new_name = new_name.replace(key_and_trailing, '')
    return new_name

#UI操作类
class BaseCopyMaterialOperator(bpy.types.Operator):
    """基础复制材质操作类"""
    bl_idname = "material.copy_base"
    bl_label = "复制基础材质"
    material_suffix = ""

    def execute(self, context):
        copy_material_to_selected_objects(self.material_suffix)
        return {'FINISHED'}

class MATERIAL_OT_copy_material_01Skin(BaseCopyMaterialOperator):
    bl_idname = "material.copy_material_01skin"
    bl_label = "01Skin 皮肤"
    material_suffix = "01Skin"

class MATERIAL_OT_copy_material_02Hair(BaseCopyMaterialOperator):
    bl_idname = "material.copy_material_02hair"
    bl_label = "02Hair 头发"
    material_suffix = "02Hair"

class MATERIAL_OT_copy_material_03CloS(BaseCopyMaterialOperator):
    bl_idname = "material.copy_material_03clos"
    bl_label = "03CloS 光滑衣物"
    material_suffix = "03CloS"

class MATERIAL_OT_copy_material_04CloR(BaseCopyMaterialOperator):
    bl_idname = "material.copy_material_04clor"
    bl_label = "04CloR 粗糙衣物"
    material_suffix = "04CloR"

class MATERIAL_OT_copy_material_05Metl(BaseCopyMaterialOperator):
    bl_idname = "material.copy_material_05metl"
    bl_label = "05Metl 金属"
    material_suffix = "05Metl"

class MATERIAL_OT_copy_material_06Eyes(BaseCopyMaterialOperator):
    bl_idname = "material.copy_material_06eyes"
    bl_label = "06Eyes 眼睛"
    material_suffix = "06Eyes"

class MATERIAL_OT_copy_material_07Stks(BaseCopyMaterialOperator):
    bl_idname = "material.copy_material_07stks"
    bl_label = "07Stks 丝袜"
    material_suffix = "07Stks"

class MATERIAL_OT_copy_material_08Cstm(BaseCopyMaterialOperator):
    bl_idname = "material.copy_material_08cstm"
    bl_label = "08Cstm 自定义"
    material_suffix = "08Cstm"




###删除多余对应材质功能
# Name数组，包含需要检查的材质名关键词
names_to_check = ["01Skin", "02Hair", "03CloS", "04CloR","05Metl", "06Eyes", "07Stks", "08Cstm" ]

# 删除未使用且名称匹配的材质
def delete_unused_materials_by_name(names):
    for material in bpy.data.materials:
        # 检查材质是否未被使用
        if material.users == 0:
            # 检查材质的名称是否包含names数组中的任一元素
            if any(name in material.name for name in names):
                # 删除材质
                bpy.data.materials.remove(material)
    

# 运算符，执行删除操作
class WM_OT_DeleteUnusedMaterialsByName(bpy.types.Operator):
    """删除未使用且名称匹配的材质"""
    bl_idname = "wm.delete_unused_materials_by_name"
    bl_label = "删除未使用的匹配材质"

    # 当按钮被按下时执行的方法
    def execute(self, context):
        delete_unused_materials_by_name(names_to_check)
        return {'FINISHED'}




###UI界面
class MATERIAL_PT_custom_panel(bpy.types.Panel):
    """创建一个在N键属性栏中的自定义面板"""
    bl_label = "QATM 快速应用含同名材质"
    bl_idname = "MATERIAL_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mat_assoc_props = scene.mat_association_props
        
        layout.use_property_split = False
        layout.use_property_decorate = False
        
        # 绘制集合选择框
        layout.label(text="指定优先搜索范围")
        layout.prop(mat_assoc_props, "collection")

        layout.label(text="匹配名称含同样 xxXXXX 的材质")

        box = layout.box()
        #box.label(text="基础", icon='LIGHT_DATA')
        col = box.column()
        col.operator("material.copy_material_01skin", icon="SHADING_SOLID")
        col.operator("material.copy_material_02hair", icon="MATSPHERE")
        
        
        box = layout.box()
        #box.label(text="衣物", icon='LIGHT_DATA')
        col = box.column()
        col.operator("material.copy_material_03clos", icon="SHADING_RENDERED")
        col.operator("material.copy_material_04clor", icon="SHADING_TEXTURE")
        
        box = layout.box()
        #box.label(text="其它", icon='LIGHT_DATA')
        col = box.column()
        col.operator("material.copy_material_05metl", icon="NODE_MATERIAL")
        col.operator("material.copy_material_06eyes", icon="ANTIALIASED")
        col.operator("material.copy_material_07stks", icon="PROP_ON")
        
        box = layout.box()
        row = box.row()
        row.operator("material.copy_material_08cstm", icon="SEQ_CHROMA_SCOPE")
        
class MATERIAL_PT_custom_subpanel01(bpy.types.Panel):
    """创建一个在N键属性栏中的自定义面板"""
    bl_label = "删除多余材质"
    bl_parent_id = "MATERIAL_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="删除名称含 xxXXXX 的多余材质")
        row = layout.row()
        row.scale_y = 1.5
        button = row.operator("wm.delete_unused_materials_by_name", text="删除多余对应材质", icon="TRASH")

class MATERIAL_PT_custom_subpanel02(bpy.types.Panel):
    """创建一个在N键属性栏中的自定义面板"""
    bl_label = "描边"
    bl_parent_id = "MATERIAL_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM' 

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="几何节点自适应描边")
        row = layout.row()
        row.scale_y = 1.5
        button = row.operator("object.add_outline_button", text="添加描边", icon="ADD")
        row.operator("wm.delete_geometry_nodes_by_name", text="删除描边", icon="X")
        

classes = (
    MATERIAL_OT_copy_material_01Skin,
    MATERIAL_OT_copy_material_02Hair,
    MATERIAL_OT_copy_material_03CloS,
    MATERIAL_OT_copy_material_04CloR,
    MATERIAL_OT_copy_material_05Metl,
    MATERIAL_OT_copy_material_06Eyes,
    MATERIAL_OT_copy_material_07Stks,
    MATERIAL_OT_copy_material_08Cstm,
    OBJECT_OT_AddOutlineButton,
    WM_OT_DeleteUnusedMaterialsByName,
    WM_OT_DeleteGeometryNodesByName,
    MaterialAssociationProperties,
    MATERIAL_PT_custom_panel,
    MATERIAL_PT_custom_subpanel01,
    MATERIAL_PT_custom_subpanel02,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.mat_association_props = bpy.props.PointerProperty(type=MaterialAssociationProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.mat_association_props

if __name__ == "__main__":
    register()