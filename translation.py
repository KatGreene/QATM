# -*- coding: utf-8 -*-

#    <QATM, Blender addon for quick applying tagged materials.>
#    Copyright (C) <2024> <绿毛猫KatGreene>


import bpy


# 定义翻译字典
translations_dict = {
    "en_US": {
        ("*", "指定优先搜索范围"): "Specify Search Priority",
        ("*", "导入集合内的材质名"): "Import Material Names",
        ("*", "应用后选中源物体"): "Select Source Objects",
        ("*", "关联选择同材质物体"): "Select Linked-Material",
        ("*", "自定义关键词"): "Custom Keywords",
        ("*", "选中词命名"): "Rename",
        ("*", "应用含此关键词的材质"): "Apply Selected",

        ("*", "QATM 附加功能"): "QATM Extra Tools",
        ("*", "追加预设工程中的全部资源"): "Append QATM Resources",

        ("*", "删除多余材质"): "Clear Unused",
        ("*", "清理多余材质"): "Clear Material",
        ("*", "仅删除含关键词的多余材质"): "Only Affect Tagged",

        ("*", "描边"): "Add Outline",
        ("*", "几何节点自适应描边"): "GN-Node Based",
        ("*", "指定描边设置"): "Outline Settings",
        ("*", "材质"): "Material",
        ("*", "摄像机"): "Camera",
        ("*", "添加描边"): "Add",
        ("*", "删除描边"): "Delete",

        ("*", "SDF工具"): "SDF Tools",
        ("*", "骨架"): "Armature",
        ("*", "SDF系统ID"): "SDF System ID",
        ("*", "装载空物体"): "Attach",
        ("*", "卸载空物体"): "Detach",
        ("*", "添加新的SDF系统"): "Add New System",

        ("*", "追加资源"): "Append Resources",
    },
}


# 注册翻译函数
def register():
    bpy.app.translations.register(__name__, translations_dict)

def unregister():
    bpy.app.translations.unregister(__name__)

