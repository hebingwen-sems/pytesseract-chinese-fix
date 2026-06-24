#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytesseract 中文 OCR 修复模块
自动检测并安装 chi_sim 中文语言包，解决中文识别乱码问题
"""

import os
import sys
import subprocess
import urllib.request
import shutil
import platform
from pathlib import Path


def get_tesseract_path():
    """获取 Tesseract 可执行文件路径"""
    system = platform.system()
    
    if system == "Windows":
        # Windows 常见安装路径
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        # 也尝试从环境变量 PATH 中查找
        tesseract_cmd = shutil.which("tesseract")
        if tesseract_cmd:
            possible_paths.insert(0, tesseract_cmd)
            
        for path in possible_paths:
            if os.path.isfile(path):
                return path
        return None
    
    else:  # Linux / macOS
        tesseract_cmd = shutil.which("tesseract")
        return tesseract_cmd


def get_tessdata_dir():
    """获取 tessdata 目录路径"""
    tesseract_path = get_tesseract_path()
    if not tesseract_path:
        return None
    
    # 尝试通过 tesseract --list-langs 获取 tessdata 路径
    try:
        result = subprocess.run(
            [tesseract_path, "--list-langs"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # 第一行通常包含 tessdata 路径信息
        # 例如: List of available languages in "/usr/share/tessdata/"
        for line in result.stderr.split('\n'):
            if 'tessdata' in line:
                # 提取路径
                start = line.find('"') + 1
                end = line.rfind('"')
                if start > 0 and end > start:
                    return line[start:end]
    except Exception:
        pass
    
    # 常见 tessdata 路径
    system = platform.system()
    possible_dirs = []
    
    if system == "Windows":
        tesseract_dir = os.path.dirname(tesseract_path)
        possible_dirs = [
            os.path.join(tesseract_dir, "tessdata"),
            r"C:\Program Files\Tesseract-OCR\tessdata",
            r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
        ]
    elif system == "Darwin":  # macOS
        possible_dirs = [
            "/usr/local/share/tessdata",
            "/opt/homebrew/share/tessdata",
            "/usr/share/tessdata",
        ]
    else:  # Linux
        possible_dirs = [
            "/usr/share/tesseract-ocr/4.00/tessdata",
            "/usr/share/tessdata",
            "/usr/local/share/tessdata",
        ]
    
    for dir_path in possible_dirs:
        if os.path.isdir(dir_path):
            return dir_path
    
    return None


def check_chi_sim_installed():
    """检查 chi_sim 语言包是否已安装"""
    tessdata_dir = get_tessdata_dir()
    if not tessdata_dir:
        return False
    
    chi_sim_path = os.path.join(tessdata_dir, "chi_sim.traineddata")
    chi_sim_best_path = os.path.join(tessdata_dir, "chi_sim_best.traineddata")
    
    return os.path.isfile(chi_sim_path) or os.path.isfile(chi_sim_best_path)


def get_installed_languages():
    """获取已安装的语言列表"""
    tesseract_path = get_tesseract_path()
    if not tesseract_path:
        return []
    
    try:
        result = subprocess.run(
            [tesseract_path, "--list-langs"],
            capture_output=True,
            text=True,
            timeout=10
        )
        languages = []
        for line in result.stdout.split('\n') + result.stderr.split('\n'):
            line = line.strip()
            if line and not line.startswith('List') and not line.startswith('Error'):
                languages.append(line)
        return languages
    except Exception as e:
        print(f"[错误] 获取语言列表失败: {e}")
        return []


def download_chi_sim():
    """
    下载 chi_sim 中文语言包
    使用 Tesseract GitHub 官方仓库的语言包
    """
    tessdata_dir = get_tessdata_dir()
    if not tessdata_dir:
        print("[错误] 无法找到 tessdata 目录")
        return False
    
    # 确保 tessdata 目录存在
    os.makedirs(tessdata_dir, exist_ok=True)
    
    # GitHub 官方语言包下载地址
    download_urls = [
        "https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata",
        "https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/chi_sim.traineddata",
    ]
    
    output_path = os.path.join(tessdata_dir, "chi_sim.traineddata")
    
    print(f"[信息] 开始下载 chi_sim 语言包...")
    print(f"[信息] 目标路径: {output_path}")
    
    for url in download_urls:
        try:
            print(f"[信息] 尝试从 {url} 下载...")
            
            # 创建请求（添加 User-Agent 避免被 GitHub 拒绝）
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            # 下载文件
            with urllib.request.urlopen(req, timeout=120) as response:
                if response.status == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.read())
                    
                    # 验证文件大小（正常应该 > 10MB）
                    file_size = os.path.getsize(output_path)
                    print(f"[成功] 下载完成！文件大小: {file_size / 1024 / 1024:.2f} MB")
                    
                    if file_size < 1024 * 1024:  # 小于 1MB 可能下载失败
                        print("[警告] 文件大小异常，可能下载不完整")
                        os.remove(output_path)
                        continue
                    
                    return True
                else:
                    print(f"[错误] HTTP 状态码: {response.status}")
                    
        except Exception as e:
            print(f"[错误] 从该地址下载失败: {e}")
            continue
    
    print("[失败] 所有下载地址均失败")
    return False


def setup_pytesseract_for_chinese():
    """
    配置 pytesseract 以支持中文识别
    返回配置好的 pytesseract 模块
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        print("[错误] 未安装 pytesseract 或 Pillow")
        print("[提示] 请运行: pip install pytesseract Pillow")
        return None
    
    # 设置 Tesseract 路径（Windows 需要）
    tesseract_path = get_tesseract_path()
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        print(f"[信息] Tesseract 路径: {tesseract_path}")
    
    return pytesseract


def chinese_ocr(image_path, lang='chi_sim+eng', config='--psm 6'):
    """
    中文 OCR 识别函数
    
    参数:
        image_path: 图片路径
        lang: 语言代码，默认 'chi_sim+eng'（中文简体+英文）
              其他选项: 'chi_sim'（仅中文）, 'chi_tra'（繁体中文）
        config: Tesseract 配置，--psm 6 适合单一文本块
    
    返回:
        识别出的文本字符串
    """
    from PIL import Image
    
    pytesseract = setup_pytesseract_for_chinese()
    if not pytesseract:
        return None
    
    # 确保 chi_sim 已安装
    if not check_chi_sim_installed():
        print("[警告] chi_sim 语言包未安装，正在尝试自动安装...")
        if not download_chi_sim():
            print("[失败] 无法自动安装 chi_sim 语言包")
            print("[提示] 请手动下载: https://github.com/tesseract-ocr/tessdata")
            print("       将 chi_sim.traineddata 放入 tessdata 目录")
            return None
    
    try:
        # 打开图片
        image = Image.open(image_path)
        
        # 执行 OCR
        text = pytesseract.image_to_string(
            image,
            lang=lang,
            config=config
        )
        
        return text.strip()
        
    except Exception as e:
        print(f"[错误] OCR 识别失败: {e}")
        return None


def main():
    """主函数：检查环境并安装语言包"""
    print("=" * 60)
    print("Pytesseract 中文 OCR 环境检查与修复工具")
    print("=" * 60)
    
    # 1. 检查 Tesseract 安装
    tesseract_path = get_tesseract_path()
    if not tesseract_path:
        print("\n[错误] 未检测到 Tesseract OCR 引擎！")
        print("[提示] 请先安装 Tesseract:")
        print("  - Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  - macOS: brew install tesseract tesseract-lang")
        print("  - Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim")
        print("  - CentOS/RHEL: sudo yum install tesseract tesseract-langpack-chi_sim")
        return 1
    
    print(f"\n[成功] 检测到 Tesseract: {tesseract_path}")
    
    # 2. 检查 tessdata 目录
    tessdata_dir = get_tessdata_dir()
    if tessdata_dir:
        print(f"[成功] tessdata 目录: {tessdata_dir}")
    else:
        print("[警告] 无法自动定位 tessdata 目录")
    
    # 3. 检查已安装语言包
    languages = get_installed_languages()
    print(f"\n[信息] 已安装的语言包 ({len(languages)} 个):")
    print(", ".join(languages))
    
    # 4. 检查 chi_sim
    if check_chi_sim_installed():
        print("\n[成功] chi_sim (中文简体) 语言包已安装！")
        print("       你现在可以使用 lang='chi_sim' 进行中文 OCR 了")
    else:
        print("\n[警告] chi_sim (中文简体) 语言包未安装！")
        print("[信息] 正在尝试自动安装...")
        
        if download_chi_sim():
            print("\n[成功] chi_sim 语言包安装完成！")
            print("       请重新运行此脚本验证")
        else:
            print("\n[失败] 自动安装失败")
            print("[手动安装指南]")
            print("1. 访问 https://github.com/tesseract-ocr/tessdata")
            print("2. 下载 chi_sim.traineddata 文件")
            if tessdata_dir:
                print(f"3. 将文件放入: {tessdata_dir}")
            else:
                print("3. 将文件放入你的 tessdata 目录")
            print("4. 重新运行此脚本验证")
    
    # 5. 测试导入 pytesseract
    print("\n[检查] 验证 Python 环境...")
    pytesseract = setup_pytesseract_for_chinese()
    if pytesseract:
        print("[成功] pytesseract 模块可正常使用")
        
        # 显示使用示例
        print("\n" + "=" * 60)
        print("使用示例:")
        print("=" * 60)
        print("""
from ocr_chinese_fix import chinese_ocr

# 识别中文图片
text = chinese_ocr('your_image.png')
print(text)

# 或者使用 chi_sim+eng 同时识别中英文
text = chinese_ocr('your_image.png', lang='chi_sim+eng')

# 高级配置
text = chinese_ocr(
    'your_image.png', 
    lang='chi_sim',
    config='--psm 6 -c preserve_interword_spaces=1'
)
""")
    else:
        print("[错误] pytesseract 模块导入失败")
        print("[提示] 请运行: pip install pytesseract Pillow")
        return 1
    
    print("\n" + "=" * 60)
    print("检查完成！")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
