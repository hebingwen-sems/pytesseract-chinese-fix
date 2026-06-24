#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytesseract 中文 OCR 使用示例
展示如何正确配置和使用中文识别
"""

from PIL import Image
import pytesseract


def basic_chinese_ocr(image_path):
    """基础中文 OCR 识别"""
    image = Image.open(image_path)
    
    # 仅使用中文识别
    text = pytesseract.image_to_string(
        image,
        lang='chi_sim'  # 指定中文简体语言包
    )
    return text


def mixed_language_ocr(image_path):
    """中英文混合识别"""
    image = Image.open(image_path)
    
    # 使用 + 连接多种语言
    text = pytesseract.image_to_string(
        image,
        lang='chi_sim+eng'  # 中文简体 + 英文
    )
    return text


def advanced_ocr_with_config(image_path):
    """带高级配置的中文 OCR"""
    image = Image.open(image_path)
    
    # 配置说明：
    # --psm 3: 自动分页（默认）
    # --psm 4: 单列文本
    # --psm 6: 单一文本块（适合截图）
    # --psm 7: 单行文本
    # --psm 8: 单个单词
    # --psm 11: 稀疏文本（适合不规则排版）
    # --oem 1: 使用 LSTM 神经网络引擎（更准确）
    # -c preserve_interword_spaces=1: 保留单词间距
    
    text = pytesseract.image_to_string(
        image,
        lang='chi_sim+eng',
        config='--psm 6 --oem 1 -c preserve_interword_spaces=1'
    )
    return text


def ocr_with_preprocessing(image_path):
    """带图像预处理的中文 OCR（提高识别率）"""
    from PIL import ImageEnhance, ImageFilter
    
    # 打开图片
    image = Image.open(image_path)
    
    # 预处理步骤
    # 1. 转换为灰度
    image = image.convert('L')
    
    # 2. 增强对比度
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    # 3. 轻微锐化
    image = image.filter(ImageFilter.SHARPEN)
    
    # 4. 二值化（阈值可根据实际情况调整）
    threshold = 128
    image = image.point(lambda x: 0 if x < threshold else 255, '1')
    
    # OCR 识别
    text = pytesseract.image_to_string(
        image,
        lang='chi_sim+eng',
        config='--psm 6'
    )
    return text


def get_bounding_boxes(image_path):
    """获取文字位置信息"""
    image = Image.open(image_path)
    
    # 获取每个文字的边界框
    data = pytesseract.image_to_data(
        image,
        lang='chi_sim',
        output_type=pytesseract.Output.DICT
    )
    
    boxes = []
    n_boxes = len(data['text'])
    for i in range(n_boxes):
        if int(data['conf'][i]) > 60:  # 过滤低置信度结果
            boxes.append({
                'text': data['text'][i],
                'x': data['left'][i],
                'y': data['top'][i],
                'width': data['width'][i],
                'height': data['height'][i],
                'confidence': data['conf'][i]
            })
    
    return boxes


if __name__ == "__main__":
    print("=" * 50)
    print("pytesseract 中文 OCR 使用示例")
    print("=" * 50)
    
    # 测试图片路径（请替换为你的图片路径）
    test_image = "test_chinese.png"
    
    print("\n可用的 PSM 模式:")
    print("  0 - 仅方向和脚本检测")
    print("  1 - 使用 OSD 自动分页")
    print("  2 - 自动分页，但没有 OSD 或 OCR")
    print("  3 - 完全自动分页，但没有 OSD (默认)")
    print("  4 - 假设一列可变大小的文本")
    print("  5 - 假设一个垂直对齐文本的单一块")
    print("  6 - 假设一个单一的文本块")
    print("  7 - 将图像视为单行文本")
    print("  8 - 将图像视为单个单词")
    print("  9 - 将图像视为圆圈中的单个单词")
    print("  10 - 将图像视为单个字符")
    print("  11 - 找到尽可能多的稀疏文本")
    print("  12 - 带有 OSD 的稀疏文本")
    print("  13 - 原始行，不处理任何内容")
    
    print("\n使用示例:")
    print("-" * 50)
    
    print("""
from example_usage import basic_chinese_ocr, mixed_language_ocr

# 基础中文识别
text = basic_chinese_ocr('screenshot.png')
print(text)

# 中英文混合识别
text = mixed_language_ocr('document.png')
print(text)

# 带预处理的识别（提高准确率）
text = ocr_with_preprocessing('blurry_image.png')
print(text)
""")
