# -*- coding: utf-8 -*-

#    <QATM, Blender addon for quick applying tagged materials.>
#    Copyright (C) <2024> <绿毛猫KatGreene>


import bpy
import os
from bpy.app.translations import pgettext


### 加载描边节点组
def load_resources(nodepaths):

    dir_path = os.path.dirname(os.path.realpath(__file__))
    blend_file_path = os.path.join(dir_path, 'resources', 'resources.blend')

    for nodepath in nodepaths:
        # 提取文件夹和节点名称
        try:
            directory_path, filename = nodepath.rsplit('/', 1)
        except ValueError:  # 没有'/'的情况，表示它可能在根目录
            directory_path = ''
            filename = nodepath
        
        # 创建完整的文件路径和目录路径
        filepath = os.path.join(blend_file_path, nodepath)
        directory = os.path.join(blend_file_path, directory_path)

        bpy.ops.wm.append(
            filepath=filepath,
            directory=directory,
            filename=filename
        )


def check_collection_exists(collection, collection_name):
    # 首先检查当前集合名字是否匹配
    if collection.name == collection_name:
        return True
    # 然后递归遍历子集合
    for child_collection in collection.children:
        if check_collection_exists(child_collection, collection_name):
            return True
    # 如果没有找到匹配的集合，返回 False
    return False

def check_scene_for_collection_name(collection_name):
    # 获取场景的主集合
    master_collection = bpy.context.scene.collection
    # 使用上面定义的函数从主集合开始检查
    return check_collection_exists(master_collection, collection_name)


### 加描边功能
def add_outline_to_selected_objects():
    scene = bpy.context.scene
    
    outline_node_group = bpy.data.node_groups.get("QATM_OutLine")
    # 检查名为"000OutLine"的节点组
    if not outline_node_group:
        load_resources(["Collection/QATM_OutLine"])
        outline_node_group = bpy.data.node_groups.get("QATM_OutLine")
        def draw(self, context):
                self.layout.label(text="已自动加载描边资源", icon='SEQUENCE_COLOR_03')
                self.layout.label(text="")
        bpy.context.window_manager.popup_menu(draw)
    
    # 获取当前选择的所有物体
    selected_objects = bpy.context.selected_objects

    # 设置默认摄像机
    outline_cam_props = scene.outline_camera_props
    camera_object = outline_cam_props.outline_camera
    if camera_object:
        bpy.data.node_groups["QATM_OutLine"].inputs[5].default_value = camera_object

    # 设置默认描边材质
    outline_mat_props = scene.outline_material_props
    outline_mat = outline_mat_props.outline_material
    if outline_mat:
        bpy.data.node_groups["QATM_OutLine"].inputs[3].default_value = outline_mat

    # 获取是否关联选择同材质物体
    link_objects = scene.material_link_settings.link_objects_with_mat
    if link_objects:
        bpy.ops.object.select_linked(type='MATERIAL')
        selected_objects = bpy.context.selected_objects

    # 对所有选中的物体执行操作
    for obj in selected_objects:
        if obj.type == 'MESH':  # 确保只处理网格类型的物体
            # 创建新的几何节点修改器
            geo_node_mod = obj.modifiers.new(type="NODES", name="QATM_OutLine")

            # 设置修改器的节点组为描边节点组
            geo_node_mod.node_group = outline_node_group


### 删除选中物体的所有名为"000OutLine"的几何节点修改器
def delete_geometry_node_modifiers(named):
    scene = bpy.context.scene
    selected_objects = bpy.context.selected_objects

    # 获取是否关联选择同材质物体
    link_objects = scene.material_link_settings.link_objects_with_mat
    if link_objects:
        bpy.ops.object.select_linked(type='MATERIAL')
        selected_objects = bpy.context.selected_objects
    
    for obj in selected_objects:  # 遍历场景中的所有选中物体
        # 确保只对网格类型的物体进行操作
        if obj.type == 'MESH':
            # 遍历物体的修改器
            modifiers_to_remove = [mod for mod in obj.modifiers if mod.type == 'NODES' and named in mod.name]
            for modifier in modifiers_to_remove:
                obj.modifiers.remove(modifier)


### 加材质功能
# 弹出未找到材质的消息
def popup_no_material_found():
    def draw(self, context):
        self.layout.label(text="没有找到目标材质!", icon='SEQUENCE_COLOR_02')
        self.layout.label(text="")
    bpy.context.window_manager.popup_menu(draw)

# 将指定材质复制到所有选中的物体
def copy_material_to_selected_objects(mat_name):
    scene = bpy.context.scene
    collection = scene.mat_association_props.collection
    material_to_copy = None
    object_with_material = None
    selected_objects = bpy.context.selected_objects

    if not selected_objects:
        def draw(self, context):
            self.layout.label(text="没有选中的物体!", icon='SEQUENCE_COLOR_02')
            self.layout.label(text="")
        bpy.context.window_manager.popup_menu(draw)
        return

    # 定义搜索材质的函数
    def find_material(objects):
        nonlocal material_to_copy, object_with_material
        for obj in objects:
            for mat_slot in obj.material_slots:
                if mat_slot.material and mat_name in mat_slot.material.name:
                    material_to_copy = mat_slot.material
                    object_with_material = obj
                    return material_to_copy
        return None

    # 如果选择了集合, 则优先在集合内部查找材质
    if collection:
        material_to_copy = find_material(collection.objects)
  
    # 如果未选择集合或在集合中没有找到材质, 则在所有物体中查找材质
    if not material_to_copy:
        material_to_copy = find_material(bpy.data.objects)

    # 如果没有找到材质, 弹出消息
    if not material_to_copy:
        popup_no_material_found()
        return

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
        self.layout.label(text=pgettext("已清理 ")+f'{remove_count}'+pgettext(" 个材质"), icon='SEQUENCE_COLOR_02')
        self.layout.label(text="")
    bpy.context.window_manager.popup_menu(draw)


def qatm_add_normal_fix():
    scene = bpy.context.scene
    sdf_tool = scene.sdf_tool
    sdf_system_id = sdf_tool.sdf_system_id

    if sdf_system_id != 0:
        face_center_name = f"Face_Center.{sdf_system_id:03d}"
    else:
        face_center_name = "Face_Center"

    bpy.ops.object.modifier_add(type='NORMAL_EDIT')
    obj = bpy.context.object
    obj.modifiers[-1].name = "QATM_HairNormal"
    obj.modifiers["QATM_HairNormal"].target = bpy.data.objects[face_center_name]
    obj.modifiers["QATM_HairNormal"].no_polynors_fix = True
    obj.modifiers["QATM_HairNormal"].mix_factor = 0.7

    def draw(self, context):
                self.layout.label(text="已添加修改器 SDF系统ID:"+f"{sdf_system_id:03d}", icon='SEQUENCE_COLOR_03')
                self.layout.label(text="")
    bpy.context.window_manager.popup_menu(draw)


### 加材质驱动器功能
def add_drivers_to_selected_objects():
    scene = bpy.context.scene
    
    outline_node_group = bpy.data.node_groups.get("QATM_Drivers")
    # 检查名为"QATM_Drivers"的节点组
    if not outline_node_group:
        load_resources(["Collection/QATM_Drivers"])
        outline_node_group = bpy.data.node_groups.get("QATM_Drivers")
        def draw(self, context):
                self.layout.label(text="已自动加载驱动器资源", icon='SEQUENCE_COLOR_03')
                self.layout.label(text="")
        bpy.context.window_manager.popup_menu(draw)
    
    # 获取当前选择的所有物体
    selected_objects = bpy.context.selected_objects

    sdf_tool = scene.sdf_tool
    sdf_system_id = sdf_tool.sdf_system_id

    if sdf_system_id != 0:
        face_forward_name = f"Face_Forward.{sdf_system_id:03d}"
    else:
        face_forward_name = "Face_Forward"

    empty_object_face_forward = bpy.data.objects.get(face_forward_name)

    if empty_object_face_forward is None:
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        # 获取当前活动物体，即刚刚添加的空物体
        empty_object_face_forward = bpy.context.active_object
        # 设置空物体的名字
        empty_object_face_forward.name = face_forward_name

    bpy.data.node_groups["QATM_Drivers"].inputs[1].default_value = empty_object_face_forward

    # 获取是否关联选择同材质物体
    link_objects = scene.material_link_settings.link_objects_with_mat
    if link_objects:
        bpy.ops.object.select_linked(type='MATERIAL')
        selected_objects = bpy.context.selected_objects

    # 对所有选中的物体执行操作
    for obj in selected_objects:
        if obj.type == 'MESH':  # 确保只处理网格类型的物体
            # 创建新的几何节点修改器
            geo_node_mod = obj.modifiers.new(type="NODES", name="QATM_Drivers")

            # 设置修改器的节点组为描边节点组
            geo_node_mod.node_group = outline_node_group


def select_objects_with_same_keyword():
    # 当前选中的关键词列表
    names_to_check = collect_keyword_names(bpy.context)

    def check_materials(obj, keyword):
        if obj.type == 'MESH':
            for mat in obj.data.materials:
                if keyword in mat.name:
                    return True
            return False

    # 首先确保场景中至少有一个物体被选中
    if bpy.context.selected_objects:
        # 获取当前选中的物体
        active_obj = bpy.context.active_object
        # 存储匹配关键字的数组

        # 假设所有选中的物体使用相同的材质作为检查标准
        for mat in active_obj.data.materials:
            names_to_check.append(mat.name)

        # 取消选择所有物体
        bpy.ops.object.select_all(action='DESELECT')

        # 迭代场景中的所有物体，检查它们是否含有所需的材质
        for obj in bpy.context.scene.objects:
            for keyword in names_to_check:
                if check_materials(obj, keyword):
                    obj.select_set(True)
                    # 设置选中物体为激活状态
                    bpy.context.view_layer.objects.active = obj
                    break  # 如果找到匹配的材质，跳出内层循环