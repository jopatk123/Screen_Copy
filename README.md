学习 git 用的

一个基于Python的截图识别工具，能够对屏幕截图进行OCR文字识别。

## 功能特点

- 屏幕截图功能
- OCR文字识别
- 支持环境变量配置

## 项目结构

```
.
├── core/
│   └── screenshot.py      # 截图核心功能
├── .env.example          # 环境变量示例文件
├── .env                  # 环境变量配置文件
├── requirements.txt      # 项目依赖
└── test_ocr.py          # OCR测试用例
```

## 安装说明

1. 克隆仓库
```bash
git clone [仓库地址]
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
- 复制 `.env.example` 为 `.env`
- 根据需要修改配置参数

## 使用方法

```bash
python core/screenshot.py
```

## 测试

运行测试用例：
```bash
python test_ocr.py
```

## 环境要求

- Python 3.x
- 查看 `requirements.txt` 获取完整依赖列表

project/
├── main.py
├── build.py
├── requirements.txt
├── resources/
│   ├── icon.ico
│   └── other_resources/
├── dist/
│   └── ScreenOCR.exe  # 打包后的文件
└── build/  # 打包过程的临时文件

