# -*- coding: utf-8 -*-

#    <QATM, Blender addon for quick applying tagged materials.>
#    Copyright (C) <2024> <绿毛猫KatGreene>


from mathutils import *
from math import *
import numpy as np
import bpy
import bmesh


def smooth_normal_to_uv():
    bpy.ops.object.mode_set(mode='OBJECT')
    obj = bpy.context.active_object
    if obj is None or obj.type != 'MESH':
        raise ValueError("Active object is not a mesh")

    me = obj.data
                
    uv_layer = me.uv_layers.new(name = "SmoothNormal")
    obj.data.uv_layers.active = uv_layer
    me.calc_tangents(uvmap = uv_layer.name)

    dict = {}

    def vec2str(vec):
        return "x=" + str(vec.x) + ",y=" + str(vec.y) + ",z=" + str(vec.z)

    def cross_product(v1, v2):
        return Vector((v1.y * v2.z - v2.y * v1.z, v1.z * v2.x - v2.z * v1.x, v1.x * v2.y - v2.x * v1.y))

    def vector_length(v):
        return sqrt(v.x * v.x + v.y * v.y + v.z * v.z)

    def normallize(v):
        return v / (vector_length(v) + 0.001)

    def dot_product(v1, v2):
        return v1.x*v2.x + v1.y*v2.y + v1.z*v2.z

    def included_angle(v1, v2):
        return np.arccos(dot_product(v1, v2)/(vector_length(v1)*vector_length(v2)+0.001))

    def need_outline(vertex):
        need = False
        for g in vertex.groups:
            if g.group == 446:
                need = True
                break
        return True

    for v in me.vertices:
        co = v.co
        co_str = vec2str(co)
        dict[co_str] = []

    for poly in me.polygons:
        l0 = me.loops[poly.loop_start]
        l1 = me.loops[poly.loop_start + 1]
        l2 = me.loops[poly.loop_start + 2]

        v0 = me.vertices[l0.vertex_index]
        v1 = me.vertices[l1.vertex_index]
        v2 = me.vertices[l2.vertex_index]

        n = cross_product(v1.co - v0.co , v2.co - v0.co)
        n = normallize(n)

        co0_str = vec2str(v0.co)
        co1_str = vec2str(v1.co)
        co2_str = vec2str(v2.co)

        if co0_str in dict and need_outline(v0):
            w = included_angle(v2.co - v0.co, v1.co - v0.co)
            dict[co0_str].append({"n":n, "w":w, "l":l0})
        if co1_str in dict and need_outline(v1):
            w = included_angle(v0.co - v1.co, v2.co - v1.co)
            dict[co0_str].append({"n":n, "w":w, "l":l1})
        if co2_str in dict and need_outline(v2):
            w = included_angle(v1.co - v2.co, v0.co - v2.co)
            dict[co0_str].append({"n":n, "w":w, "l":l2})

    for poly in me.polygons:
        for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
            vertex_index = me.loops[loop_index].vertex_index
            v = me.vertices[vertex_index]
            smoothnormal = Vector((0,0,0))
            weightsum = 0
            if need_outline(v):
                costr = vec2str(v.co)
                
                if costr in dict:
                    a = dict[costr]
                    for d in a:
                        n = d['n']
                        w = d['w']
                        smoothnormal += n * w
                        weightsum += w
            if smoothnormal != Vector((0,0,0)):
                smoothnormal /= weightsum
                smoothnormal = normallize(smoothnormal)

            normal = me.loops[loop_index].normal
            tangent = me.loops[loop_index].tangent
            bitangent = me.loops[loop_index].bitangent

            normalTSX = dot_product(tangent, smoothnormal)
            normalTSY = dot_product(bitangent, smoothnormal)
            normalTSZ = dot_product(normal, smoothnormal)

            normalTS = Vector((normalTSX, normalTSY, normalTSZ))

            # color = [normalTS.x * 0.5 + 0.5, normalTS.y *0.5 + 0.5, normalTS.z *0.5 + 0.5, 1]
            # me.vertex_colors.active.data[loop_index].color = color

            uv = (normalTS.x, 1 + normalTS.y)
            uv_layer.data[loop_index].uv = uv

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.unwrap(method='ANGLE_BASED')
    bpy.ops.object.mode_set(mode="OBJECT")


def copy_normal_to_uv():
    bpy.ops.object.mode_set(mode='OBJECT')
    
    obj = bpy.context.active_object
    if obj is None or obj.type != 'MESH':
        raise ValueError("Active object is not a mesh")

    me = obj.data
    
    uv_layer = me.uv_layers.new(name = "CopiedNormal")
    # 设置新建的UV层为当前活动的UV
    obj.data.uv_layers.active = uv_layer
    me.calc_tangents(uvmap = uv_layer.name)
    
    # uv_layer = me.uv_layers.active
    
    uv_data = uv_layer.data
    
    me.calc_normals()
    
    bm = bmesh.new()
    bm.from_mesh(me)
    
    uv_layer = bm.loops.layers.uv.active  # 此处修改
    
    for f in bm.faces:
        for l in f.loops:
            luv = l[uv_layer]  # 修改后的正确引用方法
            normal = l.vert.normal
            # 适当地调整然后重新映射这些坐标
            luv.uv = ((normal.x + 1) / 2, (normal.y + 1) / 2)
    
    bm.to_mesh(me)
    bm.free()
