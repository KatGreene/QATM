# -*- coding: utf-8 -*-

#    <QATM, Blender addon for quick applying tagged materials.>
#    Copyright (C) <2024> <绿毛猫KatGreene>


import bpy
from . import functions as func


# 装载SDF空物体
class QATM_OT_AttachEmptyObject(bpy.types.Operator):
    """创建一个自定义操作符类，用来执行父级设置操作"""
    bl_idname = "object.attach_empty_object"
    bl_label = "装载空物体到骨骼"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 获取当前场景和空物体
        scene = context.scene
        armature_name = scene.source_armature
        sdf_tool = scene.sdf_tool
        sdf_system_id = sdf_tool.sdf_system_id

        if sdf_system_id != 0:
            face_forward_name = f"Face_Forward.{sdf_system_id:03d}"
            face_center_name = f"Face_Center.{sdf_system_id:03d}"
        else:
            face_forward_name = "Face_Forward"
            face_center_name = "Face_Center"

        # 确保骨架存在
        if armature_name:
            armature_object = bpy.data.objects[armature_name]

            # 首个空物体设置父级到 'ff' 骨骼
            empty_object_face_forward = bpy.data.objects.get(face_forward_name)
            bone_names_ff = [ "メガネ", "ff", "齒上", "齒下", "両目", "首"]  # 备用骨骼名，确保至少找到一个可用的骨骼

            if empty_object_face_forward is None:
            # 添加一个新的空物体
                bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                # 获取当前活动物体，即刚刚添加的空物体
                empty_object_face_forward = bpy.context.active_object
                # 设置空物体的名字
                empty_object_face_forward.name = face_forward_name
                self.report({'INFO'}, "添加了新的SDF空物体 SDF系统ID:"+f"{sdf_system_id:03d}")

            bone_found_ff = False
            for bone_name in bone_names_ff:
                # 判断提供的骨骼名称是否在骨骼列表中
                if bone_name in armature_object.data.bones:
                    # 如果存在，设置父骨骼
                    empty_object_face_forward.parent = armature_object
                    empty_object_face_forward.parent_type = 'BONE'
                    empty_object_face_forward.parent_bone = bone_name
                    bone_found_ff = True
                    # 设置完毕后跳出循环，因为我们只需要找到一个存在的骨骼即可
                    break
            if not bone_found_ff:
                self.report({'ERROR'}, "无法找到前骨")
                return {'CANCELLED'}
  

            # 第二个空物体设置父级到 'head' 骨骼
            empty_object_face_center = bpy.data.objects.get(face_center_name)
            # 名称数组，其中包含应检查的所有骨骼名称
            bone_names_head = ["頭", "head"]

            if empty_object_face_center is None:
            # 添加一个新的空物体
                bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                # 获取当前活动物体，即刚刚添加的空物体
                empty_object_face_center = bpy.context.active_object
                # 设置空物体的名字
                empty_object_face_center.name = face_center_name
                self.report({'INFO'}, "添加了新的SDF空物体 SDF系统ID:"+f"{sdf_system_id:03d}")   

            bone_found_center = False
            for bone_name in bone_names_head:
                # 判断提供的骨骼名称是否在骨骼列表中
                if bone_name in armature_object.data.bones:
                    # 如果存在，设置父骨骼
                    empty_object_face_center.parent = armature_object
                    empty_object_face_center.parent_type = 'BONE'
                    empty_object_face_center.parent_bone = bone_name
                    bone_found_center = True
                    # 设置完毕后跳出循环，因为我们只需要找到一个存在的骨骼即可
                    break
            if not bone_found_center:
                self.report({'ERROR'}, "无法找到头骨")
                return {'CANCELLED'}

            # 更新场景，确保变化生效
            bpy.context.view_layer.update()

            self.report({'INFO'}, "空物体已成功装载到骨骼")
            bpy.ops.ed.undo_push(message="QATM: 装载空物体")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "无法找到指定的骨架")
            return {'CANCELLED'}
        

# 卸载SDF空物体
class QATM_OT_DetachEmptyObject(bpy.types.Operator):
    """创建一个自定义操作符类，用来执行父级设置操作"""
    bl_idname = "object.detach_empty_object"
    bl_label = "卸载空物体到骨骼"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 获取当前场景和空物体
        scene = context.scene
        sdf_tool = scene.sdf_tool
        sdf_system_id = sdf_tool.sdf_system_id

        if sdf_system_id != 0:
            face_forward_name = f"Face_Forward.{sdf_system_id:03d}"
            face_center_name = f"Face_Center.{sdf_system_id:03d}"
        else:
            face_forward_name = "Face_Forward"
            face_center_name = "Face_Center"

        # 首个空物体设置父级到 'ff' 骨骼
        empty_object_face_forward = bpy.data.objects.get(face_forward_name)

        if empty_object_face_forward:
            empty_object_face_forward.parent = None
        else:
            self.report({'ERROR'}, "无法找到SDF空物体")
            return {'CANCELLED'}
        
        empty_object_face_center = bpy.data.objects.get(face_center_name)

        if empty_object_face_center:
            empty_object_face_center.parent = None
        else:
            self.report({'ERROR'}, "无法找到SDF空物体")
            return {'CANCELLED'}
        
        self.report({'INFO'}, "空物体已成功卸载")
        bpy.context.view_layer.update()
        bpy.ops.ed.undo_push(message="QATM: 卸载空物体")
        
        return {'FINISHED'}
    

# 新的SDF系统
class QATM_OT_AddNewSDF(bpy.types.Operator):
    """创建一个自定义操作符类，用来执行父级设置操作"""
    bl_idname = "object.add_new_sdf"
    bl_label = "添加新的SDF系统"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene
        func.load_resources(["Collection/QATM_SDF_NodeGroups"])
        
        self.report({'INFO'}, "已添加新的SDF系统")
        bpy.context.view_layer.update()
        bpy.ops.ed.undo_push(message="QATM: 添加SDF系统")
        
        return {'FINISHED'}
    

# 统一所有日光的旋转
class QATM_OT_UnifySunlightRotation(bpy.types.Operator):
    """统一所有驱动SDF的日光的旋转"""
    bl_idname = "qatm.unify_sunlight_rotation"
    bl_label = "统一日光旋转"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 找到名称为 'QATM_Sunlight' 的空物体
        sunlight_empty = bpy.data.objects.get("QATM_000Sun_日光总控")
        if sunlight_empty is None:
            # 添加一个新的空物体
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

            # 获取当前活动物体，即刚刚添加的空物体
            sunlight_empty = bpy.context.active_object

            # 设置空物体的名字
            sunlight_empty.name = "QATM_000Sun_日光总控"
        
        # 获取并设置所有相应日光对象的父对象
        for obj in bpy.data.objects:
            if "QATM_DirLight01_日光" in obj.name:
                obj.parent = sunlight_empty

        bpy.ops.ed.undo_push(message="QATM: 统一日光旋转")
        return {'FINISHED'}
    

class QATM_OT_AddNormalFix(bpy.types.Operator):
    """添加法线编辑修改器"""
    bl_idname = "qatm.add_normal_fix"
    bl_label = "添加法线修复"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        func.qatm_add_normal_fix()
        bpy.ops.ed.undo_push(message="QATM: 法线修复")
        return {'FINISHED'}
