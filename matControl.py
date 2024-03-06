# -*- coding: utf-8 -*-

#    <QATM, Blender addon for quick applying tagged materials.>
#    Copyright (C) <2024> <绿毛猫KatGreene>


import bpy
from bpy.app.translations import pgettext


# 假设的标签数组
qatm_labels = ["01", "02", "0304", "05"]

# 更新数值的函数
def update_qatm(self, context, label):
    mat = bpy.data.materials.get("QATM_MatControl")
    if mat is not None:
        # 检查是否存在节点群组实例，并且群组的名字是 "NodeGroup"（或其他你组的名字）
        for node in mat.node_tree.nodes:
            if node.type == 'GROUP' and node.node_tree.name == "QATM_全局PBR混合调节":
                group_outputs = node.outputs
                # 遍历当前节点群组实例的节点
                for inp in node.node_tree.nodes:
                    # 检查标签而不是节点的名字
                    if inp.label == label:
                        # 更新输入插槽的值
                        inp.outputs[0].default_value = getattr(context.scene, "qatm_value_" + label)
                        break

# 为每个标签创建自己的更新函数
for label in qatm_labels:
    exec(
        f"def update_{label}(self, context): update_qatm(self, context, '{label}')"
    )

# UI面板绘制
class QATM_PT_MatControlPanel(bpy.types.Panel):
    bl_label = pgettext("QATM 材质控制")
    bl_idname = "QATM_PT_mat_control_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QATM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        self.update_label()

        box = layout.box()
        box.label(text=pgettext("QATM材质PBR混合"), icon='PRESET')
        for label in qatm_labels:
            box.prop(scene, f"qatm_value_{label}", slider=True, text=pgettext("材质号 ")+f"{label}")

    def update_label(self):
        if bpy.app.translations.locale in bpy.app.translations.locales:
            locale = bpy.app.translations.locale
            translated_label = pgettext("QATM 材质控制")
            self.bl_label = translated_label


# 注册
def register():
    for label in qatm_labels:
        setattr(
            bpy.types.Scene,
            f"qatm_value_{label}",
            bpy.props.FloatProperty(
                name="Set Value "+f"{label}",
                description=f"Set value for {label} node label",
                default=0.0,
                min=0.0,
                max=1.0,
                update=globals()[f"update_{label}"]
            )
        )
    bpy.utils.register_class(QATM_PT_MatControlPanel)

# 注销
def unregister():
    bpy.utils.unregister_class(QATM_PT_MatControlPanel)
    for label in qatm_labels:
        delattr(bpy.types.Scene, f"qatm_value_{label}")

if __name__ == "__main__":
    register()

