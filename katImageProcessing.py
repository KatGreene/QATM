import bpy
import bmesh
import math

# 定义要匹配的特定RGB值
target_rgb = (0.862711, 0.843104, 0.898004)
final_rgb = [0.937219, 0.917612, 0.933298]
threshold = 0.05  # 阈值

# def is_within_threshold(rgb1, rgb2, threshold):
#     return all(abs(a - b) <= threshold for a, b in zip(rgb1, rgb2))

# # 获取活动图像
# image = bpy.data.images['头发.png']  # 替换为你的图像名称
# pixels = list(image.pixels)

# # 遍历图像中的所有像素
# for i in range(0, len(pixels), 4):
#     r, g, b, a = pixels[i], pixels[i+1], pixels[i+2], pixels[i+3]
    
#     # 检查当前像素是否在目标RGB值的阈值范围内
#     if is_within_threshold((r, g, b), target_rgb, threshold):
#         # 对RGB各通道乘2，但保持在[0,1]范围内
#         pixels[i] = final_rgb[0]
#         pixels[i+1] = final_rgb[1]
#         pixels[i+2] = final_rgb[2]

# # 更新图像像素
# image.pixels = pixels

# # 更新图像以显示更改
# image.update()

feather_strength = 0.5  # 羽化强度，0到1之间

def calculate_feather_factor(rgb1, rgb2, threshold, feather_strength):
    # 计算两个RGB值之间的差异
    diff = math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))
    # 计算羽化因子
    feather_factor = max(0, 1 - (diff / threshold) * feather_strength)
    return feather_factor

def is_within_threshold(rgb1, rgb2, threshold):
    # 检查RGB是否在阈值范围内
    return all(abs(a - b) <= threshold for a, b in zip(rgb1, rgb2))

def modify_image(image_name, target_rgb, threshold, feather_strength):
    # 获取活动图像
    image = bpy.data.images[image_name]  # 替换为你的图像名称
    pixels = list(image.pixels)

    # 遍历图像中的所有像素
    for i in range(0, len(pixels), 4):
        r, g, b, a = pixels[i], pixels[i+1], pixels[i+2], pixels[i+3]
        current_rgb = (r, g, b)

        # 检查当前像素是否在目标RGB值的阈值范围内
        if is_within_threshold(current_rgb, target_rgb, threshold):
            # 计算羽化因子
            feather_factor = calculate_feather_factor(current_rgb, target_rgb, threshold, feather_strength)
            # 根据羽化因子对RGB各通道进行平滑过渡
            pixels[i] = min(1.0, r + (final_rgb[0] * feather_factor))
            pixels[i+1] = min(1.0, g + (final_rgb[1] * feather_factor))
            pixels[i+2] = min(1.0, b + (final_rgb[2] * feather_factor))

    # 更新图像像素
    image.pixels = pixels

    # 更新图像以显示更改
    image.update()

image_name = '头发.png'
modify_image(image_name, target_rgb, threshold, feather_strength)