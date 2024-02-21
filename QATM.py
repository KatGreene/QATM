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
from bpy.props import StringProperty, CollectionProperty
from bpy.types import Panel, Operator, UIList, PropertyGroup


bl_info = {
    "name": "QATM",
    "author": "绿毛猫KatGreene",
    "version": (0, 3),
    "blender": (3, 6, 0),
    "location": "View3D > Toolbar",
    "description": "Quick Apply Tagged Material 快速应用含同名材质",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}


### 加描边功能
def add_outline_to_selected_objects():
    scene = bpy.context.scene
    # 检查并创建一个名为"000OutLine"的节点组（如果尚不存在）
    outline_node_group = bpy.data.node_groups.get("000OutLine")
    
    # 获取当前选择的所有物体
    selected_objects = bpy.context.selected_objects

    # 对所有选中的物体执行操作
    for obj in selected_objects:
        if obj.type == 'MESH':  # 确保只处理网格类型的物体

            # 设置默认摄像机
            outline_cam_props = scene.outline_camera_props
            camera_object = outline_cam_props.outline_camera
            if camera_object:
                bpy.data.node_groups["000OutLine"].inputs[5].default_value = camera_object

            # 设置默认描边材质
            outline_mat_props = scene.outline_material_props
            outline_mat = outline_mat_props.outline_material
            if outline_mat:
                bpy.data.node_groups["000OutLine"].inputs[3].default_value = outline_mat

            # 创建新的几何节点修改器
            geo_node_mod = obj.modifiers.new(type="NODES", name="000OutLine")

            # 设置修改器的节点组为描边节点组
            geo_node_mod.node_group = outline_node_group


# 加描边功能UI操作类
class OBJECT_OT_AddOutlineButton(bpy.types.Operator):
    bl_idname = "object.add_outline_button"
    bl_label = "添加描边"
    bl_description = "给选定的物体添加一个名为‘000OutLine’的几何节点组"

    def execute(self, context):
        add_outline_to_selected_objects()
        bpy.ops.ed.undo_push(message="QATM: 添加描边")
        return {'FINISHED'}
    

# 设置笔刷操作类
class TOOL_OT_SetBrush(bpy.types.Operator):
    bl_idname = "tool.set_brush_button"
    bl_label = "快捷设置参数"
    bl_description = "设置权重笔刷值为0 并取消仅前面的面"

    def execute(self, context):
        bpy.context.scene.tool_settings.unified_paint_settings.weight = 0
        bpy.data.brushes["Draw"].use_frontface = False
        bpy.ops.ed.undo_push(message="QATM: 设置笔刷")
        return {'FINISHED'}


### 删除选中物体的所有名为"000OutLine"的几何节点修改器
def delete_geometry_node_modifiers(named):
    for obj in bpy.context.selected_objects:  # 遍历场景中的所有选中物体
        # 确保只对网格类型的物体进行操作
        if obj.type == 'MESH':
            # 遍历物体的修改器
            modifiers_to_remove = [mod for mod in obj.modifiers if mod.type == 'NODES' and named in mod.name]
            for modifier in modifiers_to_remove:
                obj.modifiers.remove(modifier)

# 操作类用于删除选中物体中名为"000OutLine"的几何节点修改器
class WM_OT_DeleteGeometryNodesByName(bpy.types.Operator):
    """删除选定的物体中名为'000OutLine'的几何节点修改器"""
    bl_idname = "wm.delete_geometry_nodes_by_name"
    bl_label = "删除'000OutLine'修改器"

    def execute(self, context):
        delete_geometry_node_modifiers("000OutLine")
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


### 加材质功能
def copy_material_to_selected_objects(mat_name):

    scene = bpy.context.scene
    
    # 查找是否存在指定名称的材质
    original_image_textures = None
    mat = None

    collection = scene.mat_association_props.collection

    material_to_copy = None
    object_with_material = None # 用于记录拥有目标材质的物体

    # 如果选中了集合，则从该集合内的物体搜索匹配的材质
    if collection:
        for obj in collection.objects:
            for mat_slot in obj.material_slots:
                if mat_slot.material and mat_name in mat_slot.material.name:
                    material_to_copy = mat_slot.material
                    object_with_material = obj
                    break  # 找到匹配的材质，停止搜索
            if material_to_copy:  # 如果已找到材质，不需要进一步搜索
                break
            else:  # 否则，在全局范围内搜索匹配的材质
                for obj in bpy.data.objects:
                    for mat_slot in obj.material_slots:
                        if mat_slot.material and mat_name in mat_slot.material.name:
                            material_to_copy = mat_slot.material
                            object_with_material = obj
                            break
                if material_to_copy:
                    break
                else:
                    def draw(self, context):
                        self.layout.label(text="没有找到目标材质", icon='SEQUENCE_COLOR_02')
                        self.layout.label(text="")
                    bpy.context.window_manager.popup_menu(draw)
                    break

    # 否则，在全局范围内搜索匹配的材质
    else:
        for obj in bpy.data.objects:
            for mat_slot in obj.material_slots:
                if mat_slot.material and mat_name in mat_slot.material.name:
                    material_to_copy = mat_slot.material
                    object_with_material = obj
                    break
            if material_to_copy:
                break
            else:
                def draw(self, context):
                    self.layout.label(text="没有找到目标材质", icon='SEQUENCE_COLOR_02')
                    self.layout.label(text="")
                bpy.context.window_manager.popup_menu(draw)
                break

    selected_objects = bpy.context.selected_objects
    if not selected_objects:
        def draw(self, context):
            self.layout.label(text="没有选中的物体", icon='SEQUENCE_COLOR_02')
            self.layout.label(text="")
        bpy.context.window_manager.popup_menu(draw)
        return  # 如果没有选中的物体，直接返回

    # 如果找到具有目标材质的物体
    if object_with_material:
        # 获取用户是否勾选了双态按钮的属性
        select_objects = scene.material_selection_settings.select_objects_with_mat
        
        if select_objects:
            # 取消所有物体的选中状态
            bpy.ops.object.select_all(action='DESELECT')
            # 选中目标物体
            object_with_material.select_set(True)
            # 设置为活动物体
            bpy.context.view_layer.objects.active = object_with_material
            
            # 将布尔值重置为False，防止重复操作
            scene.material_selection_settings.select_objects_with_mat = False

    # 存储材质名称和材质的映射，避免创建不必要的副本
    material_mapping = {}

    link_objects = scene.material_link_settings.link_objects_with_mat

    if link_objects:
        bpy.ops.object.select_linked(type='MATERIAL')
        selected_objects = bpy.context.selected_objects

    for obj in selected_objects:
        if obj.type == 'MESH':
            # 如果没有材质，则新建材质
            if len(obj.material_slots) == 0:
                new_mat = bpy.data.materials.new(name=obj.name)
                obj.data.materials.append(new_mat)
            
            # 检查所有材质槽
            for material_slot in obj.material_slots:
                # 如果材质槽为空，则创建新材质并赋给这个槽
                if material_slot.material is None:
                    new_mat = bpy.data.materials.new(name=obj.name)
                    material_slot.material = new_mat
            
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
                            names_to_check = collect_keyword_names(bpy.context)

                            processed_original_name = remove_keywords(original_mat_name, names_to_check)
                            new_mat.name = f'{material_to_copy.name}_{processed_original_name}'
                            new_mat.name = process_material_name(new_mat.name)
                            
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

# 声明函数用于处理原名称
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

def process_material_name(original_name):
    # 以"_"作为分隔符将原始名称拆分成单词列表
    words = original_name.split('_')
    # 创建一个新的列表，用于存储不重复的单词
    new_words = []
    # 遍历原始名称中的每个单词
    for word in words:
        # 如果当前单词在新列表中不存在，则将其添加到新列表中
        if word not in new_words:
            new_words.append(word)
    # 将新列表中的单词用"_"连接成新的名称
    new_name = '_'.join(new_words)
    return new_name

#UI操作类
class BaseCopyMaterialOperator(bpy.types.Operator):
    """基础复制材质操作类"""
    bl_idname = "material.copy_base"
    bl_label = "复制基础材质"
    material_suffix = ""

    def execute(self, context):
        copy_material_to_selected_objects(self.material_suffix)
        bpy.ops.ed.undo_push(message="QATM: 匹配材质")
        return {'FINISHED'}

# 应用内置关键词的材质
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

# 应用列表中关键词的材质
class MATERIAL_OT_copy_material_of_keyword(BaseCopyMaterialOperator):
    bl_idname = "material.copy_material_of_keyword"
    bl_label = "应用含此关键词的材质"
    
    @classmethod
    def poll(cls, context):
        return context.scene.keyword_list_index >= 0 and len(context.scene.keyword_list) > 0

    def execute(self, context):
        scene = context.scene
        index = scene.keyword_list_index
        scene.suffix = scene.keyword_list[index].name
        copy_material_to_selected_objects(scene.suffix)

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
    bl_idname = "keywords.new_item"
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
    bl_idname = "keywords.add_from_collection"
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
    bl_idname = "keywords.delete_item"
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
    bl_idname = "keywords.clear_list"
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
    bl_idname = "keywords.move_item"
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


###删除多余对应材质功能
def collect_keyword_names(context):
    if hasattr(context.scene, "keyword_list"):
        names_to_check = [item.name for item in context.scene.keyword_list]
    return names_to_check
# Name数组，包含需要检查的材质名关键词
names_to_check = ["01Skin", "02Hair", "03CloS", "04CloR","05Metl", "06Eyes", "07Stks"]


# 删除未使用且名称匹配的材质
def delete_unused_materials_by_name(names):
    remove_count = 0
    for material in bpy.data.materials:
        # 检查材质是否未被使用
        if material.users == 0:
            # 检查材质的名称是否包含names数组中的任一元素
            if any(name in material.name for name in names):
                # 删除材质
                bpy.data.materials.remove(material)
                remove_count += 1

    def draw(self, context):
        self.layout.label(text="已清理"+f'{remove_count}'+"个材质", icon='SEQUENCE_COLOR_02')
        self.layout.label(text="")
    bpy.context.window_manager.popup_menu(draw)
    

# 运算符，执行删除操作
class WM_OT_DeleteUnusedMaterialsByName(bpy.types.Operator):
    """删除未使用且名称匹配的材质"""
    bl_idname = "wm.delete_unused_materials_by_name"
    bl_label = "删除未使用的匹配材质"

    # 当按钮被按下时执行的方法
    def execute(self, context):
        names_to_check = collect_keyword_names(bpy.context)
        delete_unused_materials_by_name(names_to_check)
        bpy.ops.ed.undo_push(message="QATM: 清理多余材质")
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

        layout.label(text="指定优先搜索范围")
        layout.prop(mat_assoc_props, "collection")
        row = layout.row()
        row.operator("keywords.add_from_collection", icon='COLLECTION_NEW', text="导入集合内的材质名")
        box = layout.box()
        row = box.row()
        row.prop(scene.material_selection_settings, "select_objects_with_mat", text="",  icon="RESTRICT_SELECT_OFF", toggle=True)
        row.label(text="应用后选中源物体")
        row = box.row()
        row.prop(scene.material_link_settings, "link_objects_with_mat", text="",  icon="PRESET_NEW", toggle=True)
        row.label(text="关联选择同材质物体")
        
            
class MATERIAL_PT_custom_default_subpanel(bpy.types.Panel):
    bl_label = "内置关键词"
    bl_parent_id = "MATERIAL_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.use_property_split = False
        layout.use_property_decorate = False

        box = layout.box()
        col = box.column()
        col.operator("material.copy_material_01skin", icon="SHADING_SOLID")
        col.operator("material.copy_material_02hair", icon="MATSPHERE")   
        col.operator("material.copy_material_03clos", icon="SHADING_RENDERED")
        col.operator("material.copy_material_04clor", icon="SHADING_TEXTURE")
        col.operator("material.copy_material_05metl", icon="NODE_MATERIAL")
        col.operator("material.copy_material_06eyes", icon="ANTIALIASED")
        col.operator("material.copy_material_07stks", icon="PROP_ON")
        

class KEYWORDS_PT_keyword_subpanel(Panel):
    bl_label = "自定义关键词"
    bl_parent_id = "MATERIAL_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.template_list("KEYWORDS_UL_uilist", "The_List", scene, "keyword_list", scene, "keyword_list_index")

        col = row.column(align=True)
        col.operator("keywords.new_item", icon='ADD', text="")
        col.operator("keywords.delete_item", icon='REMOVE', text="")
        col.separator()
        col.operator("material.copy_material_of_keyword", icon='CHECKMARK', text="")
        col.separator()
        col.operator("keywords.move_item", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("keywords.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'
        col.separator()
        col.operator("keywords.clear_list", icon="TRASH", text="")
        
        if scene.keyword_list:
            layout.label(text="选中词命名", icon="WORDWRAP_ON")
            item = scene.keyword_list[scene.keyword_list_index]
            col = layout.column(align=False)
            col.prop(item, "name", text="")
            row = col.row(align=True)
            row.operator("material.copy_material_of_keyword", icon='CHECKMARK', text="应用含此关键词的材质")


class MATERIAL_PT_custom_panel02(bpy.types.Panel):
    """创建一个在N键属性栏中的自定义面板"""
    bl_label = "QATM 附加功能"
    bl_idname = "MATERIAL_PT_custom_panel02"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene


class MATERIAL_PT_custom_subpanel01(bpy.types.Panel):
    """创建一个在N键属性栏中的自定义面板"""
    bl_label = "删除多余材质"
    bl_parent_id = "MATERIAL_PT_custom_panel02"
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


class MATERIAL_PT_custom_subpanel02(bpy.types.Panel):
    """创建一个在N键属性栏中的自定义面板"""
    bl_label = "描边"
    bl_parent_id = "MATERIAL_PT_custom_panel02"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM' 

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.label(text="几何节点自适应描边")
        row.operator("tool.set_brush_button", text="", icon="BRUSHES_ALL")
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


classes = (
    MATERIAL_OT_copy_material_01Skin,
    MATERIAL_OT_copy_material_02Hair,
    MATERIAL_OT_copy_material_03CloS,
    MATERIAL_OT_copy_material_04CloR,
    MATERIAL_OT_copy_material_05Metl,
    MATERIAL_OT_copy_material_06Eyes,
    MATERIAL_OT_copy_material_07Stks,
    MATERIAL_OT_copy_material_of_keyword,
    TOOL_OT_SetBrush,
    OBJECT_OT_AddOutlineButton,  
    WM_OT_DeleteUnusedMaterialsByName,
    WM_OT_DeleteGeometryNodesByName,
    MaterialAssociationProperties,
    OutlineCameraProperties,
    OutlineMaterialProperties,
    MaterialSelectionSettings,
    MaterialLinkSettings,
    MATERIAL_PT_custom_panel,
    KEYWORDS_PT_keyword_subpanel,
    MATERIAL_PT_custom_default_subpanel,
    MATERIAL_PT_custom_panel02,
    MATERIAL_PT_custom_subpanel01,
    MATERIAL_PT_custom_subpanel02,
    KeywordItem, KEYWORDS_UL_uilist, 
    KEYWORDS_OT_NewItem, 
    KEYWORDS_OT_AddFromCollection,
    KEYWORDS_OT_DeleteItem,
    KEYWORDS_OT_ClearList, 
    KEYWORDS_OT_MoveItem, 
)

properties = [
    ("mat_association_props", bpy.props.PointerProperty(type=MaterialAssociationProperties)),
    ("keyword_list", CollectionProperty(type=KeywordItem)),
    ("material_selection_settings", bpy.props.PointerProperty(type=MaterialSelectionSettings)),
    ("material_link_settings", bpy.props.PointerProperty(type=MaterialLinkSettings)),
    ("keyword_list_index", bpy.props.IntProperty(name="自定义关键词", default=0, min=0)),
    ("suffix", bpy.props.StringProperty(name="Suffix", default="")),
    ("outline_camera_props", bpy.props.PointerProperty(type=OutlineCameraProperties)),
    ("outline_material_props", bpy.props.PointerProperty(type=OutlineMaterialProperties)),
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    for prop_name, prop_value in properties:
        setattr(bpy.types.Scene, prop_name, prop_value)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for prop_name, _ in properties:
        delattr(bpy.types.Scene, prop_name)

if __name__ == "__main__":
    register()
