# -*- coding: utf-8 -*-

#    <QATM, Blender addon for quick applying tagged materials.>
#    Copyright (C) <2024> <绿毛猫KatGreene>


from mathutils import *
from math import *
import numpy as np
import bpy
import bmesh


def smooth_normal_to_uv(obj):
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh = obj.data

    # 遍历对象的UV层列表
    uv_layers = mesh.uv_layers
    uv_layer_exists = False
    for uv_layer in uv_layers:
        if uv_layer.name == "UVMap":
            uv_layer_exists = True
            break

    if uv_layer_exists:
        mesh.calc_tangents(uvmap="UVMap")
    else:
        uv_layer = mesh.uv_layers.new(name="UVMap")
        mesh.calc_tangents(uvmap="UVMap")

    geo_dict = {}

    def vec2str(vec):
        return "x=" + str(vec.x) + ",y=" + str(vec.y) + ",z=" + str(vec.z)

    def cross_product(vec1, vec2):
        return Vector(
            (vec1.y * vec2.z - vec2.y * vec1.z, vec1.z * vec2.x - vec2.z * vec1.x, vec1.x * vec2.y - vec2.x * vec1.y))

    def vector_length(vec):
        return sqrt(vec.x * vec.x + vec.y * vec.y + vec.z * vec.z)

    def normallize(vec):
        return vec / (vector_length(vec) + 0.001)

    def dot_product(vec1, vec2):
        return vec1.x * vec2.x + vec1.y * vec2.y + vec1.z * vec2.z

    def included_angle(vec1, vec2):
        a_size = vector_length(vec1)
        b_size = vector_length(vec2)
        degree = np.arccos(dot_product(vec1, vec2) / (a_size * b_size))
        return degree

    def need_outline(vertex):
        # need = False
        for g in vertex.groups:
            if g.group == 446:
                break
        return True

    for v in mesh.vertices:
        co = v.co
        co_str = vec2str(co)
        geo_dict[co_str] = []

    for poly in mesh.polygons:
        l0 = mesh.loops[poly.loop_start]
        l1 = mesh.loops[poly.loop_start + 1]
        l2 = mesh.loops[poly.loop_start + 2]

        v0 = mesh.vertices[l0.vertex_index]
        v1 = mesh.vertices[l1.vertex_index]
        v2 = mesh.vertices[l2.vertex_index]

        n = cross_product(v1.co - v0.co, v2.co - v0.co)
        n = normallize(n)

        co0_str = vec2str(v0.co)
        co1_str = vec2str(v1.co)
        co2_str = vec2str(v2.co)

        if co0_str in geo_dict and need_outline(v0):
            w = included_angle(v2.co - v0.co, v1.co - v0.co)
            geo_dict[co0_str].append({"n": n, "w": w, "l": l0})
        if co1_str in geo_dict and need_outline(v1):
            w = included_angle(v2.co - v1.co, v0.co - v1.co)
            geo_dict[co0_str].append({"n": n, "w": w, "l": l1})
        if co2_str in geo_dict and need_outline(v2):
            w = included_angle(v1.co - v2.co, v0.co - v2.co)
            geo_dict[co0_str].append({"n": n, "w": w, "l": l2})

    uv_layer = mesh.uv_layers.new(name="SmoothNormal")

    for poly in mesh.polygons:
        for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
            vertex_index = mesh.loops[loop_index].vertex_index
            v = mesh.vertices[vertex_index]
            smoothnormal = Vector((0, 0, 0))
            weightsum = 0
            if need_outline(v):
                costr = vec2str(v.co)

                if costr in geo_dict:
                    a = geo_dict[costr]
                    for d in a:
                        n = d['n']
                        w = d['w']
                        smoothnormal += n * w
                        weightsum += w
            if smoothnormal != Vector((0, 0, 0)):
                smoothnormal /= weightsum
                smoothnormal = normallize(smoothnormal)

            normal = mesh.loops[loop_index].normal
            tangent = mesh.loops[loop_index].tangent
            bitangent = mesh.loops[loop_index].bitangent

            normal_tsx = dot_product(tangent, smoothnormal)
            normal_tsy = dot_product(bitangent, smoothnormal)
            normal_tsz = dot_product(normal, smoothnormal)

            normal_ts = Vector((normal_tsx, normal_tsy, normal_tsz))

            # color = [normalTS.x * 0.5 + 0.5, normalTS.y *0.5 + 0.5, normalTS.z *0.5 + 0.5, 1]
            # mesh.vertex_colors.active.data[loop_index].color = color

            uv = (normal_ts.x * 0.5 + 0.5, normal_ts.y * 0.5 + 0.5)
            # uv = (normalTS.x, 1 + normalTS.y)
            uv_layer.data[loop_index].uv = uv

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.unwrap(method='ANGLE_BASED')
    bpy.ops.object.mode_set(mode="OBJECT")


def copy_normal_to_uv(obj):
    bpy.ops.object.mode_set(mode='OBJECT')

    mesh = obj.data

    uv_layer = mesh.uv_layers.new(name="CopiedNormal")
    # 设置新建的UV层为当前活动的UV
    obj.data.uv_layers.active = uv_layer
    mesh.calc_tangents(uvmap="CopiedNormal")

    # uv_layer = mesh.uv_layers.active

    uv_data = uv_layer.data

    mesh.calc_normals()

    bm = bmesh.new()
    bm.from_mesh(mesh)

    uv_layer = bm.loops.layers.uv.active  # 此处修改

    for face in bm.faces:
        for loop in face.loops:
            luv = loop[uv_layer]  # 修改后的正确引用方法
            normal = loop.vert.normal
            # 适当地调整然后重新映射这些坐标
            luv.uv = ((normal.x + 1) / 2, (normal.y + 1) / 2)

    bm.to_mesh(mesh)
    bm.free()
