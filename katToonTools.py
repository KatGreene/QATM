import bpy
import bmesh
from mathutils import *
from math import *
import numpy as np

# 获取活动对象
obj = bpy.context.active_object

def dot_product(vec1, vec2):
    return vec1.x * vec2.x + vec1.y * vec2.y + vec1.z * vec2.z

def normallize(vec):
    return vec / (vector_length(vec) + 0.001)

def vector_length(vec):
    return sqrt(vec.x * vec.x + vec.y * vec.y + vec.z * vec.z)

def calc_highlight_uv():
    # 确保该对象是网格
    if obj and obj.type == 'MESH':
        # 获取网格数据
        mesh = obj.data

        # 使用 BMesh 以便更方便地处理顶点数据
        bm = bmesh.new()
        bm.from_mesh(mesh)

        empty_object_base_point = bpy.data.objects.get("A_BasePoint")
        empty_object_target_point = bpy.data.objects.get("B_TargetPoint")

        # 目标点
        # target_point = Vector((0, 0, 24.3382))
        base_point = empty_object_base_point.matrix_world.to_translation()
        target_point = empty_object_target_point.matrix_world.to_translation()

        AB = normallize(base_point - target_point)

        # 确保有一个 UV 图层
        if not bm.loops.layers.uv:
            uv_layer = bm.loops.layers.uv.new()
        else:
            uv_layer = bm.loops.layers.uv.active

        # 存储所有的 projectionLength 值
        projection_lengths = []

        # 计算每个顶点到目标点的距离
        for face in bm.faces:
            for loop in face.loops:
                vert = loop.vert
                if vert.select:
                    worldToA = vert.co - base_point
                    projectionLength = dot_product(worldToA, AB)
                    projection_lengths.append(projectionLength)

        # 找到最大值和最小值
        max_proj_length = max(projection_lengths)
        min_proj_length = min(projection_lengths)

        # 归一化处理并存储在 UV 坐标的 U 分量中
        for face in bm.faces:
            for loop in face.loops:
                vert = loop.vert
                if vert.select:
                    worldToA = vert.co - base_point
                    projectionLength = dot_product(worldToA, AB)
                    normalized_proj_length = (projectionLength - min_proj_length) / (max_proj_length - min_proj_length)
                    uv = loop[uv_layer].uv
                    uv.x = normalized_proj_length # 将归一化后的值存储在 U 分量中
                    highlight_period = 0.2
                    uv.y = 1 - min(1, max(0, 50 * cos(2 * np.pi * (1 / highlight_period) * normalized_proj_length)))
                    uv.x += - float(np.floor(uv.x / highlight_period)) * highlight_period
                    

        # 将 BMesh 写回到网格数据
        bm.to_mesh(mesh)
        bm.free()

        print("已成功将归一化后的距离存储到 UV 坐标的 U 分量中")
    else:
        print("请选择一个网格对象")


def setup_highlight_empty():

    empty_object_base_point = bpy.data.objects.get("A_BasePoint")
    empty_object_target_point = bpy.data.objects.get("B_TargetPoint")

    if empty_object_base_point is None:
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        empty_object_base_point = bpy.context.active_object
        empty_object_base_point.name = "A_BasePoint"

    if empty_object_target_point is None:
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        empty_object_target_point = bpy.context.active_object
        empty_object_target_point.name = "B_TargetPoint"


setup_highlight_empty()
#calc_highlight_uv()