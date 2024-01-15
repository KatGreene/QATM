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
    "version": (0, 1),
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
    for obj in bpy.context.selected_objects:  # 遍历场景中的所有物体
        # 确保我们只对网格类型的物体进行操作
        if obj.type == 'MESH':
            # 遍历物体的修改器
            modifiers_to_remove = [mod for mod in obj.modifiers if mod.type == 'NODES' and mod.name == named]
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

    # 应用材质
    for obj in selected_objects:
        # 如果没有材质，则新建材质
        if len(obj.material_slots) == 0:
            new_mat = bpy.data.materials.new(name="00Midl")
            obj.data.materials.append(new_mat)
            bpy.data.materials.remove(new_mat)
            
        if obj.type == 'MESH' and len(obj.material_slots) > 0:
            # 获取原材质中图像纹理所关联的图像
            original_image_textures = {}
            for mat_slot in obj.material_slots:
                if mat_slot.material and mat_slot.material.use_nodes:
                    for node in mat_slot.material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            original_image_textures[node.location.y] = node.image
    
            #复制和更新图像
            if material_to_copy: #and original_image_textures
                new_mat = material_to_copy.copy()
                new_mat.name += "_" + obj.name
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

#UI操作类
class MATERIAL_OT_copy_material_01Skin(bpy.types.Operator):
    """复制包含'01Skin'的材质"""
    bl_idname = "material.copy_material_01skin"
    bl_label = "01Skin 皮肤"
    def execute(self, context):
        copy_material_to_selected_objects("01Skin")
        return {'FINISHED'}

class MATERIAL_OT_copy_material_02Hair(bpy.types.Operator):
    """复制包含'02Hair'的材质"""
    bl_idname = "material.copy_material_02hair"
    bl_label = "02Hair 头发"
    def execute(self, context):
        copy_material_to_selected_objects("02Hair")
        return {'FINISHED'}
    
class MATERIAL_OT_copy_material_03CloS(bpy.types.Operator):
    """复制包含'03CloS'的材质"""
    bl_idname = "material.copy_material_03clos"
    bl_label = "03CloS 光滑衣物"
    def execute(self, context):
        copy_material_to_selected_objects("03CloS")
        return {'FINISHED'}

class MATERIAL_OT_copy_material_04CloR(bpy.types.Operator):
    """复制包含'04CloR'的材质"""
    bl_idname = "material.copy_material_04clor"
    bl_label = "04CloR 粗糙衣物"
    def execute(self, context):
        copy_material_to_selected_objects("04CloR")
        return {'FINISHED'}
    
class MATERIAL_OT_copy_material_05Metl(bpy.types.Operator):
    """复制包含'05Metl'的材质"""
    bl_idname = "material.copy_material_05metl"
    bl_label = "05Metl 金属"
    def execute(self, context):
        copy_material_to_selected_objects("05Metl")
        return {'FINISHED'}
    
class MATERIAL_OT_copy_material_06Eyes(bpy.types.Operator):
    """复制包含'06Eyes'的材质"""
    bl_idname = "material.copy_material_06eyes"
    bl_label = "06Eyes 眼睛"
    def execute(self, context):
        copy_material_to_selected_objects("06Eyes")
        return {'FINISHED'}
    
class MATERIAL_OT_copy_material_07Stks(bpy.types.Operator):
    """复制包含'07Stks'的材质"""
    bl_idname = "material.copy_material_07stks"
    bl_label = "07Stks 丝袜"
    def execute(self, context):
        copy_material_to_selected_objects("07Stks")
        return {'FINISHED'}
    
class MATERIAL_OT_copy_material_08Cstm(bpy.types.Operator):
    """复制包含'08Cstm'的材质"""
    bl_idname = "material.copy_material_08cstm"
    bl_label = "08Cstm 自定义"
    def execute(self, context):
        copy_material_to_selected_objects("08Cstm")
        return {'FINISHED'}




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
        
        # 绘制集合选择框
        row = layout.row()
        layout.label(text="指定优先搜索范围")
        layout.prop(mat_assoc_props, "collection")

        layout.label(text="匹配名称含同样 xxXXXX 的材质")
        row = layout.row()
        row.operator("material.copy_material_01skin", icon="SHADING_SOLID")
        row = layout.row()
        row.operator("material.copy_material_02hair", icon="MATSPHERE")
        row = layout.row()
        row = layout.row(align=True)
        row.operator("material.copy_material_03clos", icon="SHADING_RENDERED")
        row = layout.row()
        row.operator("material.copy_material_04clor", icon="SHADING_TEXTURE")
        row = layout.row()
        row = layout.row(align=True)
        row.operator("material.copy_material_05metl", icon="NODE_MATERIAL")
        row = layout.row()
        row.operator("material.copy_material_06eyes", icon="ANTIALIASED")
        row = layout.row()
        row.operator("material.copy_material_07stks", icon="PROP_ON")
        row = layout.row(align=True)
        row = layout.row()
        row.operator("material.copy_material_08cstm", icon="SEQ_CHROMA_SCOPE")
        row = layout.row()
        layout.label(text="删除名称含 xxXXXX 的多余材质")
        row = layout.row()
        row.scale_y = 1.5
        button = row.operator("wm.delete_unused_materials_by_name", text="删除多余对应材质", icon="TRASH")
        row = layout.row()
        row = layout.row()
        layout.label(text="几何节点自适应描边")
        row = layout.row()
        row.scale_y = 1.5
        button = row.operator("object.add_outline_button", text="添加描边", icon="ADD")
        row.operator("wm.delete_geometry_nodes_by_name", text="删除描边", icon="X")
        row = layout.row()
        

def register():
    bpy.utils.register_class(MATERIAL_OT_copy_material_01Skin)
    bpy.utils.register_class(MATERIAL_OT_copy_material_02Hair)
    bpy.utils.register_class(MATERIAL_OT_copy_material_03CloS)
    bpy.utils.register_class(MATERIAL_OT_copy_material_04CloR)
    bpy.utils.register_class(MATERIAL_OT_copy_material_05Metl)
    bpy.utils.register_class(MATERIAL_OT_copy_material_06Eyes)
    bpy.utils.register_class(MATERIAL_OT_copy_material_07Stks)
    bpy.utils.register_class(MATERIAL_OT_copy_material_08Cstm)
    bpy.utils.register_class(OBJECT_OT_AddOutlineButton)
    bpy.utils.register_class(WM_OT_DeleteUnusedMaterialsByName)
    bpy.utils.register_class(WM_OT_DeleteGeometryNodesByName)

    bpy.utils.register_class(MaterialAssociationProperties)
    
    bpy.types.Scene.mat_association_props = bpy.props.PointerProperty(type=MaterialAssociationProperties)

    bpy.utils.register_class(MATERIAL_PT_custom_panel)

def unregister():
    bpy.utils.unregister_class(MATERIAL_OT_copy_material_01Skin)
    bpy.utils.unregister_class(MATERIAL_OT_copy_material_02Hair)
    bpy.utils.unregister_class(MATERIAL_OT_copy_material_03CloS)
    bpy.utils.unregister_class(MATERIAL_OT_copy_material_04CloR)
    bpy.utils.unregister_class(MATERIAL_OT_copy_material_05Metl)
    bpy.utils.unregister_class(MATERIAL_OT_copy_material_06Eyes)
    bpy.utils.unregister_class(MATERIAL_OT_copy_material_07Stks)
    bpy.utils.unregister_class(MATERIAL_OT_copy_material_08Cstm)
    bpy.utils.unregister_class(OBJECT_OT_AddOutlineButton)
    bpy.utils.unregister_class(WM_OT_DeleteUnusedMaterialsByName)
    bpy.utils.unregister_class(WM_OT_DeleteGeometryNodesByName)
    bpy.utils.unregister_class(MATERIAL_PT_custom_panel)

    bpy.utils.unregister_class(MaterialAssociationProperties)
    
    del bpy.types.Scene.mat_association_props

if __name__ == "__main__":
    register()