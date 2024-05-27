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


### 添加一个指向集合的属性
class QATM_MaterialAssociationProperties(bpy.types.PropertyGroup):
    collection: bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection
    ) # type: ignore


### 添加一个指向摄像机的属性
class QATM_OutlineCameraProperties(bpy.types.PropertyGroup):
    outline_camera: bpy.props.PointerProperty(
        name="描边摄像机",
        type=bpy.types.Object,
        # 通过指定 poll 方法，可以确保只有摄像机对象能被赋值给此属性
        poll=lambda self, object: object.type == 'CAMERA'
    ) # type: ignore


### 添加一个指向描边材质的属性
class QATM_OutlineMaterialProperties(bpy.types.PropertyGroup):
    outline_material: bpy.props.PointerProperty(
        name="描边材质",
        type=bpy.types.Material,
    ) # type: ignore
    

class QATM_CustomIntProperties(bpy.types.PropertyGroup):
    sdf_system_id: bpy.props.IntProperty(
        name="SDF系统",
        description="SDF系统整数ID",
        default=0,
        min=0,
        max=64
    ) # type: ignore


### 添加布尔属性
class QATM_CustomBoolProperties(bpy.types.PropertyGroup):
    select_objects_with_mat: bpy.props.BoolProperty(
        name="应用后选中源物体",
        description="QATM: 点击切换设置",
        default=False
    ) # type: ignore

    link_objects_with_mat: bpy.props.BoolProperty(
        name="应用前关联选择同材质物体",
        description="QATM: 点击切换设置",
        default=False
    ) # type: ignore

    auto_set_sdf_id: bpy.props.BoolProperty(
        name="自动设置SDF系统ID",
        description="QATM: 点击切换设置",
        default=True
    ) # type: ignore


# class QATM_CustomDictProperties(bpy.types.PropertyGroup):
#     sdf_id_dict: bpy.props.CollectionProperty(
#         name="SDF系统ID字典",
#         description="SDF系统ID字典",
#         type=bpy.types.PropertyGroup,
#     ) # type: ignore