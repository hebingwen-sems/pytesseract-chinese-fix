# pytesseract 中文 OCR 修复工具

自动检测并安装 Tesseract 中文语言包 (`chi_sim`)，解决中文识别乱码问题。

## 问题描述

在使用 pytesseract 进行中文 OCR 时，如果环境中缺少 `chi_sim` 语言包，中文内容会被识别为乱码或空字符串。

```python
import pytesseract
from PIL import Image

# 错误：未指定语言，默认使用英文
text = pytesseract.image_to_string(image)  # 中文输出乱码！

# 错误：chi_sim 语言包未安装
text = pytesseract.image_to_string(image, lang='chi_sim')  # 报错！
```

## 解决方案

### 快速开始

1. **运行自动修复脚本**：

```bash
python ocr_chinese_fix.py
```

2. **仅安装中文语言包**：

```bash
python install_chi_sim.py
```

3. **在代码中使用**：

```python
from ocr_chinese_fix import chinese_ocr

# 自动处理语言包，直接识别中文
text = chinese_ocr('your_image.png')
print(text)
```

## 安装说明

### 1. 安装 Tesseract OCR

**Windows**：
- 下载安装程序：https://github.com/UB-Mannheim/tesseract/wiki
- 安装时勾选 "Chinese (Simplified)" 语言包
- 或将安装路径添加到系统 PATH

**macOS**：
```bash
brew install tesseract tesseract-lang
```

**Ubuntu/Debian**：
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
```

**CentOS/RHEL**：
```bash
sudo yum install tesseract tesseract-langpack-chi_sim
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 验证安装

```bash
python ocr_chinese_fix.py
```

## 使用示例

### 基础中文识别

```python
from ocr_chinese_fix import chinese_ocr

# 识别中文图片
text = chinese_ocr('screenshot.png')
print(text)
```

### 中英文混合识别

```python
# 同时识别中英文
text = chinese_ocr('document.png', lang='chi_sim+eng')
```

### 繁体中文识别

```python
# 需要先安装 chi_tra 语言包
text = chinese_ocr('traditional.png', lang='chi_tra')
```

### 使用原生 pytesseract（已配置好环境）

```python
import pytesseract
from PIL import Image

image = Image.open('test.png')

# 中文识别
text = pytesseract.image_to_string(image, lang='chi_sim')

# 中英文混合
text = pytesseract.image_to_string(image, lang='chi_sim+eng')

# 高级配置
text = pytesseract.image_to_string(
    image,
    lang='chi_sim',
    config='--psm 6 --oem 1'
)
```

## PSM 模式说明

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| 3 | 完全自动分页（默认） | 一般文档 |
| 4 | 单列文本 | 单列排版 |
| 6 | 单一文本块 | 截图、对话框 |
| 7 | 单行文本 | 验证码 |
| 11 | 稀疏文本 | 不规则排版 |

## 提高识别准确率

1. **图像预处理**：提高分辨率、对比度
2. **选择合适的 PSM 模式**
3. **使用 LSTM 引擎**：`--oem 1`
4. **语言包选择**：混合内容使用 `chi_sim+eng`

## 文件说明

| 文件 | 说明 |
|------|------|
| `ocr_chinese_fix.py` | 主修复模块，含自动检测和安装功能 |
| `install_chi_sim.py` | 仅安装 chi_sim 语言包的快速脚本 |
| `example_usage.py` | 使用示例和高级配置 |
| `requirements.txt` | Python 依赖 |

## 手动下载语言包

如果自动下载失败，可以手动安装：

1. 访问 https://github.com/tesseract-ocr/tessdata
2. 下载 `chi_sim.traineddata`（约 40MB）
3. 放入 Tesseract 的 `tessdata` 目录：
   - Windows: `C:\Program Files\Tesseract-OCR\tessdata`
   - macOS: `/usr/local/share/tessdata` 或 `/opt/homebrew/share/tessdata`
   - Linux: `/usr/share/tessdata`

## 更多语言包

| 语言代码 | 说明 |
|----------|------|
| `chi_sim` | 中文简体 |
| `chi_tra` | 中文繁体 |
| `eng` | 英文 |
| `jpn` | 日文 |
| `kor` | 韩文 |

完整列表：https://github.com/tesseract-ocr/tessdata

## 许可证

MIT License
