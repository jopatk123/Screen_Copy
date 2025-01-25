import PyInstaller.__main__
import os
import sys

def create_exe():
    # 确定图标路径
    icon_path = os.path.join('resources', 'icon.ico')
    
    # PyInstaller参数
    args = [
        'main.py',  # 主程序入口
        '--name=ScreenOCR',  # 生成的exe名称
        '--noconsole',  # 不显示控制台窗口
        f'--icon={icon_path}' if os.path.exists(icon_path) else '',  # 应用图标
        '--add-data=resources;resources',  # 添加资源文件
        '--onefile',  # 打包成单个exe文件
        '--clean',  # 清理临时文件
        '--windowed',  # Windows下不显示命令行
        # 添加所需的隐式导入
        '--hidden-import=pynput.keyboard._win32',
        '--hidden-import=pynput.mouse._win32',
    ]
    
    # 执行打包
    PyInstaller.__main__.run(args)

if __name__ == '__main__':
    create_exe() 