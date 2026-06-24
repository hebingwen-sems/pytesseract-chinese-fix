#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chi_sim 中文语言包快速安装脚本
一键检测并安装 Tesseract 中文 OCR 语言包
支持 Tesseract v4/v5 及 Windows/macOS/Linux
"""

import os
import sys
import urllib.request
import shutil
import platform
import subprocess


def find_tessdata_dir():
    """查找 tessdata 目录（支持 v4/v5 多平台）"""
    # 尝试通过 tesseract 命令获取
    tesseract_cmd = shutil.which("tesseract")
    
    if platform.system() == "Windows" and not tesseract_cmd:
        # Windows 常见路径
        for path in [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]:
            if os.path.isfile(path):
                tesseract_cmd = path
                break
    
    if tesseract_cmd:
        try:
            result = subprocess.run(
                [tesseract_cmd, "--list-langs"],
                capture_output=True,
                text=True,
                timeout=10
            )
            for line in (result.stdout + result.stderr).split('\n'):
                if 'tessdata' in line:
                    start = line.find('"') + 1
                    end = line.rfind('"')
                    if start > 0 and end > start:
                        return line[start:end]
        except:
            pass
    
    # 常见路径（覆盖 v4/v5 及多平台）
    paths = {
        "Windows": [
            r"C:\Program Files\Tesseract-OCR\tessdata",
            r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
        ],
        "Darwin": [
            "/usr/local/share/tessdata",
            "/opt/homebrew/share/tessdata",
        ],
        "Linux": [
            "/usr/share/tesseract-ocr/5/tessdata",    # Ubuntu 22.04+ / Tesseract v5
            "/usr/share/tesseract-ocr/4.00/tessdata", # 旧版本
            "/usr/share/tessdata",
            "/usr/local/share/tessdata",
        ]
    }
    
    system = platform.system()
    for path in paths.get(system, []):
        if os.path.isdir(path):
            return path
    
    return None


def install():
    """安装 chi_sim 语言包"""
    print("=" * 50)
    print("Tesseract 中文语言包 (chi_sim) 安装工具")
    print("=" * 50)
    
    # 查找 tessdata 目录
    tessdata_dir = find_tessdata_dir()
    
    if not tessdata_dir:
        print("\n[错误] 找不到 tessdata 目录！")
        print("\n请确认 Tesseract OCR 已正确安装:")
        print("  • Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  • macOS:   brew install tesseract")
        print("  • Ubuntu:  sudo apt install tesseract-ocr")
        return False
    
    print(f"\n[信息] tessdata 目录: {tessdata_dir}")
    
    # 检查是否已安装
    chi_sim_file = os.path.join(tessdata_dir, "chi_sim.traineddata")
    if os.path.isfile(chi_sim_file):
        size_mb = os.path.getsize(chi_sim_file) / 1024 / 1024
        print(f"\n[✓] chi_sim 语言包已存在！({size_mb:.1f} MB)")
        print(f"       路径: {chi_sim_file}")
        return True
    
    # 创建目录（如果不存在）
    os.makedirs(tessdata_dir, exist_ok=True)
    
    # 下载语言包（支持多镜像源）
    download_urls = [
        "https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata",
        "https://ghproxy.com/https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata",
    ]
    
    print(f"\n[下载] 正在下载 chi_sim 语言包...")
    print(f"       文件较大 (~40MB)，请耐心等待...")
    
    for url in download_urls:
        try:
            print(f"\n[信息] 尝试: {url[:60]}...")
            
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            with urllib.request.urlopen(req, timeout=300) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                chunk_size = 512 * 1024  # 512KB chunks
                
                with open(chi_sim_file, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r       进度: {percent:.1f}% ({downloaded/1024/1024:.1f}/{total_size/1024/1024:.1f} MB)", 
                                  end='', flush=True)
            
            print("\n\n[✓] 安装完成！")
            print(f"       文件: {chi_sim_file}")
            print(f"       大小: {os.path.getsize(chi_sim_file) / 1024 / 1024:.1f} MB")
            
            # 验证
            print("\n[验证] 检查安装结果...")
            result = subprocess.run(
                [shutil.which("tesseract") or "tesseract", "--list-langs"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if 'chi_sim' in (result.stdout + result.stderr):
                print("[✓] chi_sim 语言包已可用！")
            else:
                print("[!] 语言包可能未正确加载，请重启终端后重试")
            
            return True
            
        except Exception as e:
            print(f"\n[错误] 下载失败: {str(e)[:80]}")
            if os.path.isfile(chi_sim_file):
                os.remove(chi_sim_file)
            continue
    
    print("\n[✗] 所有下载地址均失败")
    print("\n[手动安装方法]")
    print("1. 浏览器访问: https://github.com/tesseract-ocr/tessdata")
    print("2. 点击 chi_sim.traineddata 文件")
    print("3. 点击右上角的 'Download' 或 'Raw' 按钮下载")
    print(f"4. 将下载的文件移动到: {tessdata_dir}")
    return False


if __name__ == "__main__":
    success = install()
    sys.exit(0 if success else 1)
