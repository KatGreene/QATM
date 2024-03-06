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
import os
from . import classes as cls
from . import ui
from . import sdf
from . import matControl
from . import translation as trans
from bpy.props import CollectionProperty


bl_info = {
    "name": "QATM",
    "author": "绿毛猫KatGreene",
    "version": (0, 4),
    "blender": (3, 6, 0),
    "location": "View3D > Toolbar",
    "description": "Quick Apply Tagged Material 快速应用含同名材质",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}


classes = (
    cls.QATM_OT_copy_material_of_keyword,

    cls.QATM_OT_SetBrush,
    cls.QATM_OT_AddOutlineButton,  
    cls.QATM_OT_AddDriversButton, 
    cls.QATM_OT_DeleteUnusedMaterialsByName,
    cls.QATM_OT_DeleteGeometryNodesByName,
    cls.QATM_OT_DeleteDriversNodes,

    cls.QATM_MaterialAssociationProperties,
    cls.QATM_OutlineCameraProperties,
    cls.QATM_OutlineMaterialProperties,
    cls.QATM_CustomIntProperties,
    cls.QATM_MaterialSelectionSettings,
    cls.QATM_MaterialLinkSettings,

    cls.QATM_KeywordItem, 
    cls.QATM_UL_uilist, 
    cls.QATM_OT_NewItem, 
    cls.QATM_OT_AddFromCollection,
    cls.QATM_OT_DeleteItem,
    cls.QATM_OT_ClearList, 
    cls.QATM_OT_MoveItem, 

    sdf.QATM_OT_AttachEmptyObject,
    sdf.QATM_OT_DetachEmptyObject,
    sdf.QATM_OT_AddNewSDF,
    sdf.QATM_OT_UnifySunlightRotation,
    sdf.QATM_OT_AddNormalFix,

    cls.QATM_OT_AddResourcesOutline,
    cls.QATM_OT_AddResourcesAll,
    cls.QATM_OT_OpenManualPDF,

    ui.QATM_PT_custom_panel,
    ui.QATM_PT_custom_panel02,
    ui.QATM_PT_custom_subpanel01,
    ui.QATM_PT_custom_subpanel02,
    ui.QATM_PT_custom_subpanel03,
)

properties = [
    ("mat_association_props", bpy.props.PointerProperty(type=cls.QATM_MaterialAssociationProperties)),
    ("outline_camera_props", bpy.props.PointerProperty(type=cls.QATM_OutlineCameraProperties)),
    ("outline_material_props", bpy.props.PointerProperty(type=cls.QATM_OutlineMaterialProperties)),
    ("keyword_list", CollectionProperty(type=cls.QATM_KeywordItem)),
    ("material_selection_settings", bpy.props.PointerProperty(type=cls.QATM_MaterialSelectionSettings)),
    ("material_link_settings", bpy.props.PointerProperty(type=cls.QATM_MaterialLinkSettings)),
    ("sdf_tool", bpy.props.PointerProperty(type=cls.QATM_CustomIntProperties)),
    ("keyword_list_index", bpy.props.IntProperty(name="自定义关键词", default=0, min=0)),
    ("suffix", bpy.props.StringProperty(name="Suffix", default="")),
    ("source_armature", bpy.props.StringProperty(name="选中骨架"))
]

# 构建存放英文翻译文件的文件夹路径
locale_directory = os.path.join(os.path.dirname(__file__), 'locale', 'en', 'LC_MESSAGES')

# 获取插件文件夹路径
addon_path = os.path.dirname(__file__)

# 获取本地化文件夹路径
locales_dir = os.path.join(addon_path, "locale")

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    for prop_name, prop_value in properties:
        setattr(bpy.types.Scene, prop_name, prop_value)

    trans.register()
    matControl.register()
    # bpy.app.translations.register(__name__, translation_dict) # 注册你的翻译字典
    

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for prop_name, _ in properties:
        delattr(bpy.types.Scene, prop_name)

    trans.unregister()
    matControl.unregister()


if __name__ == "__main__":
    register()
    
