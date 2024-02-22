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
    },
}


# 注册翻译函数
def register():
    bpy.app.translations.register(__name__, translations_dict)

def unregister():
    bpy.app.translations.unregister(__name__)

